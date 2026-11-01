"""Show a fresh fixed/PASADA run without overwriting the measured comparison."""
import argparse,pathlib,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'learning'))
from environment import Environment
p=argparse.ArgumentParser()
p.add_argument('--case',default='J3_AM',choices=[s+'_'+t for s in ['J1','J2','J3','CORRIDOR'] for t in ['AM','PM']])
p.add_argument('--mode',default='rule',choices=['fixed','rule'])
p.add_argument('--seed',type=int,default=7100)
a=p.parse_args()
folder=ROOT/'results'/'viewings'/str(time.time_ns())/a.case/a.mode
env=Environment(a.case,folder,a.mode,a.seed,horizon=4200,gui=True)
try:
 while env.now<4200:
  actions={s:env.observer.rule(s,c,env.now) if a.mode=='rule' else 0 for s,c in env.controllers.items()}
  _,_,terminal,truncated=env.step(actions)
  if terminal or truncated:break
finally:
 print(env.close())
