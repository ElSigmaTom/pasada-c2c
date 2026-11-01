#!/usr/bin/env python3
"""Convert an existing OSM export to a SUMO network. Does not create measured demand."""
import argparse
from pathlib import Path
import subprocess

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--osm',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--netconvert',default='netconvert')
    a=p.parse_args()
    if not a.osm.is_file():p.error('Provide an existing .osm or .osm.xml export.')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    try:subprocess.run([a.netconvert,'--osm-files',str(a.osm),'--output-file',str(a.output)],check=True)
    except (FileNotFoundError,subprocess.CalledProcessError) as e:p.exit(2,f'Conversion failed: {e}\nInstall SUMO locally and inspect its geometry in netedit.\n')
    print('Network converted. Verify road directions, lane permissions, crossings and TLS identities. Demand/calibration are separate inputs.')

if __name__=='__main__':main()
