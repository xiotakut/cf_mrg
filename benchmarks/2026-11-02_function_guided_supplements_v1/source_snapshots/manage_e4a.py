import subprocess,sys,json,time
from common import ROOT,WORK,PYTHON,environment,dump,now
OUT=ROOT/'e4a'

def main():
    phase=sys.argv[1];assert phase in ['preflight','live']
    folder=OUT/('supervisor_'+phase);folder.mkdir(exist_ok=True)
    for method in ['M4','M5']:
        terminal=folder/(method.lower()+'_exit.json')
        if terminal.exists():
            assert json.loads(terminal.read_text())['exit_code']==0;continue
        if phase=='live':
            state=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True)
            gpu=next([int(v.strip()) for v in l.split(',')] for l in state.splitlines() if l.split(',')[0].strip()=='3')
            dump(folder/(method.lower()+'_gpu_check.json'),dict(time=now(),gpu=gpu))
            if gpu[1]<38000:raise RuntimeError('GPU3 free memory below fixed 38GB guard; no process interrupted')
        cmd=[str(PYTHON),str(ROOT/'run_e4a.py'),'--method',method]+(['--preflight'] if phase=='preflight' else [])
        with (folder/(method.lower()+'.log')).open('a') as log:
            p=subprocess.Popen(cmd,env=environment(),cwd=WORK,stdout=log,stderr=subprocess.STDOUT)
            dump(folder/(method.lower()+'_launch.json'),dict(time=now(),pid=p.pid,command=cmd))
            code=p.wait()
        dump(terminal,dict(time=now(),exit_code=code))
        if code:raise RuntimeError(method+' '+phase+' failed; see preserved log')
    dump(folder/'terminal.json',dict(time=now(),status='complete',phase=phase))

if __name__=='__main__':main()
