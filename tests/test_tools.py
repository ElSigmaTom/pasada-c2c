import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from provision import simulate,validate_config
from sumo_adapter import validate_mapping,observe

def project():return json.loads((ROOT/'examples/project.json').read_text())
def mapping():return {'intersections':[{'project_intersection_id':j['id'],'sumo_tls_id':'tls-'+j['id'],'approach_lanes':{d:[j['id']+'-'+d] for d in 'NESW'},'exit_lanes':{'N':[j['id']+'-exit']}} for j in project()['intersections']]}
def config():return {'schema':'pasada.device/0.1.0','device_id':'PUCK-TEST','role':'sensor','output_mode':'serial-only','security_mode':'simulation','esp_now_channel':6}

class FakeTraci:
    def __init__(self):self.t=0;self.simulation=self;self.trafficlight=self;self.lane=FakeLanes(self)
    def simulationStep(self):self.t+=1
    def getTime(self):return self.t
    def getIDList(self):return ['tls-'+j['id'] for j in project()['intersections']]
    def getPhase(self,tls):return 0 if self.t<3 else 1
    def getRedYellowGreenState(self,tls):return 'GGrr' if self.t<3 else 'yyrr'
class FakeLanes:
    def __init__(self,t):self.t=t
    def getIDList(self):return [j['id']+'-'+d for j in project()['intersections'] for d in ['N','E','S','W','exit']]
    def getLastStepHaltingNumber(self,lane):return 2
    def getLastStepVehicleNumber(self,lane):return 3
    def getLastStepVehicleIDs(self,lane):return [lane+'-'+str(self.t.t)]

class ToolTests(unittest.TestCase):
    def test_simulator_persists_and_reopens(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=Path(tmp)/'devices.json';c=config();r=simulate(c,store)
            self.assertTrue(r['readback_verified']);self.assertEqual(r['transport'],'simulated')
            self.assertFalse(r['physical_outputs_enabled']);c['esp_now_channel']=7
            simulate(c,store);self.assertEqual(json.loads(store.read_text())['PUCK-TEST']['esp_now_channel'],7)
    def test_physical_output_config_is_rejected(self):
        c=config();c['output_mode']='gpio-actuation'
        with self.assertRaises(ValueError):validate_config(c)
    def test_unlocated_controller_is_rejected_before_provisioning(self):
        c=json.loads((ROOT/'examples/controller-pending-location.json').read_text())
        with self.assertRaises(ValueError):validate_config(c)
        c['location']={'latitude':10.3307,'longitude':123.9475}
        c['installation_ready']=True
        with tempfile.TemporaryDirectory() as tmp:
            r=simulate(c,Path(tmp)/'devices.json')
            self.assertTrue(r['readback_verified'])
            self.assertFalse(r['radio_verified'])
    def test_complete_mapping_required(self):
        m=mapping();validate_mapping(project(),m);m['intersections'].pop()
        with self.assertRaises(ValueError):validate_mapping(project(),m)
    def test_tls_placeholder_rejected(self):
        m=mapping();m['intersections'][0]['sumo_tls_id']='REPLACE_ME'
        with self.assertRaises(ValueError):validate_mapping(project(),m)
    def test_observer_preserves_unknown_health_and_pedestrian_measurements(self):
        r=observe(FakeTraci(),project(),mapping(),4)
        self.assertEqual(r['provenance']['source'],'sumo');self.assertFalse(r['provenance']['calibrated'])
        self.assertEqual([f['t'] for f in r['frames']],[1,2,3,4])
        j=r['frames'][-1]['intersections'][0]
        self.assertEqual(j['queues'],dict.fromkeys('NESW',2));self.assertEqual(j['device_health'],{})
        self.assertIsNone(j['ped_wait_s']);self.assertIsNone(j['arrived']);self.assertEqual(j['departed'],3)
        self.assertEqual(j['mode'],'SUMO_OBSERVED')
    def test_unknown_real_tls_rejected_before_simulation(self):
        m=mapping();m['intersections'][0]['sumo_tls_id']='wrong'
        t=FakeTraci()
        with self.assertRaises(ValueError):observe(t,project(),m,5)
        self.assertEqual(t.t,0)

if __name__=='__main__':unittest.main()
