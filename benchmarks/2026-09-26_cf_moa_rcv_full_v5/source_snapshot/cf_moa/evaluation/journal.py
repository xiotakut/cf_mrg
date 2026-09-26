"""Durable per-request recovery. A missing response is never silently resampled."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import time

from cf_moa.contracts import ModelResult, digest


class JournalConflict(RuntimeError):
    pass


class UnresolvedCall(RuntimeError):
    pass


class PreservedFailure(RuntimeError):
    pass


class StoppedOnError(PreservedFailure):
    pass


def error_category(error):
    return getattr(error, 'category', 'infrastructure')


def serialized(value):
    return json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))


class RunJournal:
    def __init__(self,path,plan,*,resume=False):
        path=Path(path)
        if path.exists()!=resume:
            raise JournalConflict('New runs require a new journal; resuming requires an existing journal')
        self.db=sqlite3.connect(path)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS calls (
                request_id TEXT NOT NULL, ordinal INTEGER NOT NULL, request TEXT NOT NULL,
                reserved_tokens INTEGER NOT NULL, phase TEXT NOT NULL, status TEXT NOT NULL,
                result TEXT, physical TEXT, error TEXT, started REAL NOT NULL, finished REAL,
                PRIMARY KEY (request_id, ordinal));
            CREATE TABLE IF NOT EXISTS outputs (request_id TEXT PRIMARY KEY, record TEXT NOT NULL);
        ''')
        old=self.db.execute("SELECT value FROM meta WHERE key='plan'").fetchone()
        if resume:
            if not old or digest(json.loads(old[0]))!=digest(plan):
                self.db.close()
                raise JournalConflict('Input, budget, code, configuration or candidate identity changed')
        else:
            with self.db:self.db.execute('INSERT INTO meta VALUES (?,?)',('plan',serialized(plan)))

    def lookup(self,request_id,ordinal):
        cursor=self.db.execute('SELECT * FROM calls WHERE request_id=? AND ordinal=?',(request_id,ordinal))
        row=cursor.fetchone()
        return dict(zip([d[0] for d in cursor.description],row)) if row else None

    def count(self,request_id):
        return self.db.execute('SELECT COUNT(*) FROM calls WHERE request_id=?',(request_id,)).fetchone()[0]

    def output(self,request_id):
        row=self.db.execute('SELECT record FROM outputs WHERE request_id=?',(request_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def save_output(self,request_id,value):
        with self.db:self.db.execute('INSERT INTO outputs VALUES (?,?)',(request_id,serialized(value)))

    def first_error(self):
        row=self.db.execute("SELECT value FROM meta WHERE key='first_error'").fetchone()
        return json.loads(row[0]) if row else None

    def request_counts(self):
        submitted=completed=in_flight=unknown=0
        records=list(self.db.execute('SELECT status,phase,physical FROM calls'))
        for status,phase,physical in records:
            entries=json.loads(physical) if physical is not None else []
            if entries:
                for entry in entries:
                    state=entry.get('submission_state')
                    done='event' in entry
                    sent=done or state in ('accepted','attempted_unknown') or (
                        state is None and phase=='submitted')
                    submitted+=int(sent);completed+=int(done)
                    in_flight+=int(sent and not done)
                    unknown+=int(sent and not done and state!='not_submitted')
            elif phase=='submitted':
                submitted+=1;in_flight+=1;unknown+=1
        return dict(attempted=len(records),submitted=submitted,completed=completed,
            in_flight=in_flight,in_flight_state_unknown=unknown,
            definition='submitted includes uncertain transport submissions; in_flight means no durable completion, not a claim that GPU execution is still active')

    def stop(self,request_id,error,ordinal=None):
        first=dict(request_id=request_id,ordinal=ordinal,error_type=type(error).__name__,
            error_category=error_category(error),message=str(error),at=time.time(),
            source=getattr(error,'source','runtime'),
            counts=self.request_counts())
        with self.db:self.db.execute('INSERT OR IGNORE INTO meta VALUES (?,?)',('first_error',serialized(first)))
        return self.first_error()

    def ensure_running(self):
        first=self.first_error()
        if first:
            raise StoppedOnError('Run stopped at '+first['request_id']+': '+first['message'])

    def cost(self,request_id=None):
        sql='SELECT status,phase,physical FROM calls'
        cursor=self.db.execute(sql+' WHERE request_id=?',(request_id,)) if request_id is not None else self.db.execute(sql)
        records=list(cursor);events=[];physical_count=unknown=0
        for status,phase,physical in records:
            if physical is not None:
                entries=json.loads(physical)
                physical_count+=len(entries)
                events.extend(e['event'] for e in entries if 'event' in e)
                unknown+=sum('event' not in e and e.get('submission_state')!='not_submitted' for e in entries)
            elif phase=='submitted':
                unknown+=1
        live=[e for e in events if e['mode']=='live']
        times=self.db.execute('SELECT started,finished FROM calls'+
            (' WHERE request_id=?' if request_id is not None else ''),
            (request_id,) if request_id is not None else ()).fetchall()
        return dict(physical_model_requests=physical_count,new_model_requests=len(live),
            live_input_tokens=sum(e['input_tokens'] for e in live),
            live_output_tokens=sum(e['output_tokens'] for e in live),
            live_model_seconds=sum(e['elapsed_seconds'] for e in live),
            recorded_call_wall_seconds=sum(max(0,end-start) for start,end in times if end is not None),
            unfinished_call_wall_unknown=sum(end is None for start,end in times),
            unresolved_model_usage=unknown,model_usage_complete=unknown==0,
            submission_attempts=len(records),failed_attempts=sum(r[0]=='failed' for r in records),
            cost_basis='unique durable physical records across attempts; unresolved usage excluded, not zero')

    def export(self,root):
        root=Path(root)
        values=[json.loads(r[0]) for r in self.db.execute('SELECT record FROM outputs ORDER BY rowid')]
        calls=[]
        for request_id,ordinal,request,status,phase,result,physical,error in self.db.execute(
                'SELECT request_id,ordinal,request,status,phase,result,physical,error FROM calls ORDER BY rowid'):
            calls.append(dict(request_id=request_id,ordinal=ordinal,request=json.loads(request),status=status,
                phase=phase,result=json.loads(result) if result else None,
                physical=json.loads(physical) if physical else None,error=json.loads(error) if error else None))
        for name,records in [('proposals.jsonl',values),('model_calls.jsonl',calls)]:
            temp=root/(name+'.tmp')
            with temp.open('w') as stream:
                for value in records:stream.write(serialized(value)+'\n')
            temp.replace(root/name)  # SQLite is the authoritative fsynced journal.
        first=self.first_error()
        if first:
            (root/'first_error.json').write_text(json.dumps(first,ensure_ascii=False,indent=2)+'\n')


class JournalBackend:
    def __init__(self,journal,backend_factory):
        self.journal=journal
        self.factory=backend_factory
        self.backend=None
        self.request_id=None
        self.ordinal=0
        self.reused=0
        self.unresolved=None

    def begin_item(self,request_id):
        self.request_id=request_id;self.ordinal=0;self.reused=0;self.unresolved=None

    def cached(self,request):
        row=self.journal.lookup(self.request_id,self.ordinal)
        if row and digest(json.loads(row['request']))!=digest(request):
            raise JournalConflict('Resumed model request differs at '+self.request_id+':'+str(self.ordinal))
        return row

    def count_tokens(self,request):
        self.journal.ensure_running()
        row=self.cached(request)
        if row:return row['reserved_tokens']
        try:
            if self.backend is None:self.backend=self.factory()
            return self.backend.count_tokens(request)
        except Exception as error:
            self.journal.stop(self.request_id,error,self.ordinal)
            raise

    def __call__(self,request):
        self.journal.ensure_running()
        started=time.monotonic();row=self.cached(request)
        if row:
            if row['status']=='started':
                self.unresolved=UnresolvedCall('A previous call has no durable result; automatic resampling is disabled: '+self.request_id)
                self.journal.stop(self.request_id,self.unresolved,self.ordinal)
                raise self.unresolved
            if row['status']=='failed':
                error=PreservedFailure('Previously failed call retained: '+row['error'])
                self.journal.stop(self.request_id,error,self.ordinal)
                raise error
            saved=json.loads(row['result'])
            events=deepcopy(saved['events'])
            for event in events:
                event.update(mode='replay',original_event=deepcopy(event),
                    elapsed_seconds=time.monotonic()-started,recovery='same_run_durable_response')
            self.ordinal+=1;self.reused+=1
            return ModelResult(saved['value'],events)
        tokens=self.count_tokens(request)
        with self.journal.db:
            self.journal.db.execute('INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                (self.request_id,self.ordinal,serialized(request),tokens,'validating','started',None,None,None,time.time(),None))
        physical_start=len(self.backend.physical_calls)
        try:
            self.backend.preflight(request)
            with self.journal.db:
                self.journal.db.execute("UPDATE calls SET phase='initializing' WHERE request_id=? AND ordinal=?",(self.request_id,self.ordinal))
            if self.backend.llm is None:self.backend.start()
            with self.journal.db:
                self.journal.db.execute("UPDATE calls SET phase='submitted' WHERE request_id=? AND ordinal=?",(self.request_id,self.ordinal))
            result=self.backend(request)
            if not isinstance(result,ModelResult) or len(result.events)!=1:
                raise ValueError('One physical result is required for durable replay')
            physical=self.backend.physical_calls[physical_start:]
            with self.journal.db:
                self.journal.db.execute("UPDATE calls SET status='complete',result=?,physical=?,finished=? WHERE request_id=? AND ordinal=?",
                    (serialized(dict(value=result.value,events=result.events)),serialized(physical),time.time(),self.request_id,self.ordinal))
            self.ordinal+=1
            return result
        except Exception as error:
            physical=self.backend.physical_calls[physical_start:]
            phase=self.journal.lookup(self.request_id,self.ordinal)['phase']
            with self.journal.db:
                self.journal.db.execute("UPDATE calls SET status='failed',physical=?,error=?,finished=? WHERE request_id=? AND ordinal=?",
                    (serialized(physical) if physical or phase in ('initializing','validating') else None,
                     serialized(dict(type=type(error).__name__,category=error_category(error),message=str(error))),time.time(),self.request_id,self.ordinal))
            self.journal.stop(self.request_id,error,self.ordinal)
            self.ordinal+=1
            raise

    def finish_item(self):
        self.journal.ensure_running()
        if self.ordinal!=self.journal.count(self.request_id):
            raise JournalConflict('The resumed execution ended before consuming its saved model responses')
