"""Run one authorized fixed experiment, sequential backbones, with durable exits."""
import argparse,subprocess,json,os,time
from common import ROOT,PYTHON,environment,dump,now
p=argparse.ArgumentParser();p.add_argument('experiment',choices=['e4b','e5']);a=p.parse_args()
out=ROOT/a.experiment/'supervisor';out.mkdir(exist_ok=True)
dump(out/'launch.json',dict(time=now(),pid=os.getpid(),experiment=a.experiment,gpu=3))
for m in ['M4','M5']:
 terminal=ROOT/a.experiment/'runs'/m.lower()/'terminal.json'
 if terminal.exists() and json.load(terminal.open()).get('status')=='complete':continue
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.free','--format=csv,noheader,nounits'],text=True)
 cards={int(line.split(',')[0]):int(line.split(',')[1]) for line in raw.splitlines()}
 if cards[3]<60*1024:
  dump(out/'resource_block.json',dict(time=now(),method=m,free_mib=cards[3],required_mib=60*1024));raise SystemExit(75)
 with (out/f'{m.lower()}.log').open('a') as log:
  job=subprocess.Popen([str(PYTHON),str(ROOT/f'run_{a.experiment}.py'),'--method',m],cwd=ROOT,env=environment('3'),stdout=log,stderr=subprocess.STDOUT)
  dump(out/f'{m.lower()}_launch.json',dict(time=now(),pid=job.pid,gpu=3))
  code=job.wait()
 dump(out/f'{m.lower()}_exit.json',dict(time=now(),exit_code=code))
 if code:raise SystemExit(code)
dump(out/'terminal.json',dict(time=now(),status='complete'))
