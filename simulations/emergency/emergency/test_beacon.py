import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'learning'));sys.path.insert(0,str(ROOT/'emergency'))
from beacon import Receiver,EmergencySupervisor

def geometry():
 return {'J':{'junction_polygon':[[-10,-10],[10,-10],[10,10],[-10,10]],'approaches':[[[200,0],[0,0]],[[0,200],[0,0]],[[-200,0],[0,0]],[[0,-200],[0,0]]]}}
def packet(t,x,**changes):
 return {'beacon':'REGISTERED_PROBE','vehicle':'EV_PROBE','authorized':True,'emergency_active':True,'session':1,'sequence':int(t)+1,'time':t,'x':x,'y':0.,'hacc':.5,**changes}
def receiver():
 r=Receiver(geometry())
 for t,x in [(0,140),(1,135),(2,130)]:r.receive(packet(t,x),t+.5)
 return r

def controller():
 return EmergencySupervisor([{'green':''.join('G' if i==j else 'r' for j in range(4)),'yellow':''.join('y' if i==j else 'r' for j in range(4)),'all_red':'rrrr','duration':30.} for i in range(4)],'rule')

class BeaconTests(unittest.TestCase):
 def test_three_fixes_and_heading(self):
  r=Receiver(geometry());r.receive(packet(0,140),.5);r.receive(packet(1,135),1.5);self.assertFalse(r.encounters)
  r.receive(packet(2,130),2.5);self.assertEqual(r.active('J',2.5)['stage'],0)
 def test_stationary_jitter_cannot_create_approach(self):
  r=Receiver(geometry())
  for t,x in [(0,140),(1,140.1),(2,139.9)]:r.receive(packet(t,x),t+.5)
  self.assertFalse(r.encounters)
 def test_registration_binding(self):
  for change in [{'beacon':'UNKNOWN'},{'vehicle':'OTHER'},{'authorized':False},{'emergency_active':False}]:
   r=Receiver(geometry())
   for t in range(3):r.receive(packet(t,140-5*t,**change),t+.5)
   self.assertFalse(r.encounters)
 def test_stale_future_and_duplicate_packets(self):
  r=Receiver(geometry());r.receive(packet(0,140),4);r.receive(packet(5,140),1);self.assertEqual(len(r.fixes),0)
  r.receive(packet(0,140),.5);r.receive(packet(0,135),1.5);self.assertEqual(len(r.fixes),1)
 def test_beacon_staleness_releases(self):
  r=receiver();self.assertIsNone(r.active('J',6));self.assertEqual(r.encounters['J']['release_reason'],'stale_beacon')
 def test_cap_is_not_renewed(self):
  r=receiver()
  for t in range(3,25):
   r.receive(packet(t,130),t+.5);r.active('J',t+.5)
  self.assertEqual(len(r.encounters),1);self.assertEqual(r.encounters['J']['release_s'],22.5);self.assertIsNone(r.active('J',25))
 def test_ambiguous_geometry_rejected(self):
  g=geometry();g['J']['approaches'][1]=[[200,1],[0,1]];r=Receiver(g)
  for t in range(3):r.receive(packet(t,140-5*t),t+.5)
  self.assertFalse(r.encounters)
 def test_clearances_and_minimum_green(self):
  c=controller();timeline=[]
  for i in range(81):
   t=i*.5;c.set_request({'stage':1} if t<20 else None,t);c.tick(t,True);timeline.append((t,c.stage,c.aspect))
  self.assertEqual(next(t for t,s,a in timeline if s==1 and a=='green'),18)
  self.assertEqual(next(t for t,s,a in timeline if s==2 and a=='green'),36)
  self.assertTrue(all(a=='green' for t,s,a in timeline if t<10))
  self.assertTrue(all(a=='yellow' for t,s,a in timeline if 10<=t<14))
  self.assertTrue(all(a=='all_red' for t,s,a in timeline if 14<=t<18))
 def test_release_during_yellow_does_not_skip_allred(self):
  c=controller();timeline=[]
  for i in range(45):
   t=i*.5;c.set_request({'stage':3} if t<12 else None,t);c.tick(t,True);timeline.append((t,c.stage,c.aspect))
  self.assertTrue(all(a=='yellow' for t,s,a in timeline if 10<=t<14));self.assertTrue(all(a=='all_red' for t,s,a in timeline if 14<=t<18))
  self.assertFalse(any(s==3 and a=='green' for t,s,a in timeline))
 def test_priority_still_works_in_puck_fallback(self):
  c=controller()
  for i in range(37):
   t=i*.5;c.set_request({'stage':2},t);c.tick(t,False)
  self.assertTrue(c.fallback);self.assertEqual((c.stage,c.aspect),(2,'green'))

if __name__=='__main__':unittest.main()

