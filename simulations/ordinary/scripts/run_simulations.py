"""Run prepared SUMO cases; Python is optional for watching them in SUMO GUI."""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
BASE_CASES = ["J1_AM","J1_PM","J2_AM","J2_PM","J3_AM","J3_PM","CORRIDOR_AM","CORRIDOR_PM"]
CASES = BASE_CASES + ["ST50_"+case for case in BASE_CASES]


def find_binary(gui=False):
    name = "sumo-gui" if gui else "sumo"
    if os.environ.get("SUMO_HOME"):
        binary = Path(os.environ["SUMO_HOME"])/"bin"/(name+(".exe" if os.name=="nt" else ""))
        if binary.exists():return str(binary)
    found = shutil.which(name)
    if found:return found
    try:
        import sumo
        binary = Path(sumo.__file__).parent/"bin"/(name+(".exe" if os.name=="nt" else ""))
        if binary.exists():return str(binary)
    except ImportError:pass
    raise RuntimeError("SUMO not found. Install SUMO 1.28.0 and set SUMO_HOME or put its bin folder on PATH.")


def run_case(case, gui=False):
    if not gui:
        from run_baseline_checks import run
        return run((case,"reference",42,None))["exit_code"]
    scale="0.5" if case.startswith("ST50_") else "1.0"
    cmd=[find_binary(True),"-c",str(ROOT/f"scenarios/{case}.sumocfg"),
         "--scale",scale,"--seed","42","--start","--delay","50"]
    return subprocess.run(cmd,cwd=ROOT).returncode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case",choices=CASES,default="J1_AM")
    parser.add_argument("--all",action="store_true")
    parser.add_argument("--gui",action="store_true")
    parser.add_argument("--jobs",type=int,default=2)
    args = parser.parse_args()
    if args.gui and args.all:parser.error("Choose one GUI case at a time.")
    selected = BASE_CASES if args.all else [args.case]
    if len(selected)==1:
        codes=[run_case(selected[0],args.gui)]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,args.jobs)) as pool:
            codes=list(pool.map(lambda c:run_case(c,False),selected))
    if any(codes):raise SystemExit(1)


if __name__ == "__main__":main()
