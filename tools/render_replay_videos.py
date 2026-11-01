#!/usr/bin/env python3
"""Render source-backed 1080p SUMO replay evidence with Pillow and FFmpeg.

Ordinary traffic motion is an observer-only deterministic reproduction and must
match both archived sensor traces and exact supervisor transitions before any
video is emitted. Emergency motion is the original archived 1 Hz probe trace.
No ordinary vehicles, occupancy values or painted queue estimates are invented.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
NAVY = "#17384f"
GOLD = "#d9ad46"
BG = "#edf2f6"
INK = "#183449"
MUTED = "#64778a"
ROAD = "#697a8c"
EDGE = "#506477"
PALETTE = {"MOTORCYCLE": "#f1bf58", "PUV": "#50bdd0", "PUJ": "#ed9c60", "PUB": "#c8d76c",
           "PRIVATE_CAR": "#bcd3f4", "CAR": "#bcd3f4", "CONTAINER_VAN": "#e8c58b", "WING_VAN": "#bdaddd"}
CASE_NAMES = {"J1": "A.C. Cortes / D.M. Cortes", "J2": "D.M. Cortes / C. Ouano–F. Mendoza",
              "J3": "A. Soriano / Ouano / S.B. Cabahug", "CORRIDOR": "Connected three-intersection corridor"}
SIGNAL = {"r": "#ed626a", "y": "#fac958", "g": "#49d18a", "G": "#49d18a", "s": "#ed626a", "o": "#a7b4c1", "O": "#a7b4c1"}
FONT_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FONT_BOLD = FONT_PATH.with_name("DejaVuSans-Bold.ttf")
FONTS = {}


def font(size, bold=False):
    key = size, bold
    if key not in FONTS:
        FONTS[key] = ImageFont.truetype(str(FONT_BOLD if bold else FONT_PATH), size)
    return FONTS[key]


def text(draw, xy, value, size=24, fill=INK, bold=False, anchor=None):
    draw.text(xy, str(value), font=font(size, bold), fill=fill, anchor=anchor)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def clock(t):
    return f"{int(t)//3600:02d}:{int(t)%3600//60:02d}:{int(t)%60:02d}"


def scalar(value):
    if value in ("True", "False"):
        return value == "True"
    try:
        return float(value)
    except ValueError:
        return value


def validate_capture(folder, archived):
    with (folder / "sensor_trace.csv").open(newline="") as stream:
        rows = [{k: scalar(v) for k, v in row.items()} for row in csv.DictReader(stream)]
    assert rows == archived["sensor_trace"], f"Captured sensor trace differs from original: {folder}"
    assert load_json(folder / "supervisor_events.json") == archived["supervisor_events"], f"Supervisor event mismatch: {folder}"
    metric = load_json(folder / "metrics.json")
    for key in ("scheduled_due", "inserted", "arrived", "unfinished", "uninserted_due", "collision_events", "teleports"):
        assert metric[key] == archived["metrics"][key], (folder, key, metric[key], archived["metrics"][key])
    motion = load_json(folder / "motion.json.gz")
    assert motion["capture_window_s"] == [1200, 2400] and motion["sample_s"] == 1
    assert len(motion["frames"]) == 1201
    return motion, {"sensor_trace_semantic_equal": True, "supervisor_events_equal": True, "core_metrics_equal": True,
                    "motion_sha256": sha(folder / "motion.json.gz"), "position_reference": motion["position_reference"]}


class View:
    def __init__(self, geometry, box, bounds):
        self.geometry = geometry
        self.x0, self.y0, self.w, self.h = box
        xmin, ymin, xmax, ymax = bounds
        scale = min(self.w / (xmax-xmin), self.h / (ymax-ymin))
        cx, cy = (xmin+xmax)/2, (ymin+ymax)/2
        self.scale = scale
        self.xmin, self.xmax = cx-self.w/2/scale, cx+self.w/2/scale
        self.ymin, self.ymax = cy-self.h/2/scale, cy+self.h/2/scale
        self.lanes = {x["id"]: x for x in geometry["lanes"]}
        self.background = self.make_background()

    def point(self, p):
        return (p[0]-self.xmin)*self.scale, self.h-(p[1]-self.ymin)*self.scale

    def visible(self, p, margin=20):
        return self.xmin-margin <= p[0] <= self.xmax+margin and self.ymin-margin <= p[1] <= self.ymax+margin

    def make_background(self):
        image = Image.new("RGB", (self.w, self.h), "#eaf0f4")
        draw = ImageDraw.Draw(image)
        visible = []
        for lane in self.geometry["lanes"]:
            points = lane["shape"]
            if not points:
                continue
            xs, ys = [p[0] for p in points], [p[1] for p in points]
            if max(xs)<self.xmin-30 or min(xs)>self.xmax+30 or max(ys)<self.ymin-30 or min(ys)>self.ymax+30:
                continue
            visible.append(lane)
        # Draw curbs first and native lane surfaces second, preserving all context.
        for extra, color in ((2, EDGE), (0, ROAD)):
            for lane in visible:
                pts = [self.point(p) for p in lane["shape"]]
                width = max(1, round(lane["width"] * self.scale))
                pedestrian = lane.get("allow") == "pedestrian"
                draw.line(pts, fill=("#bac7d2" if pedestrian else color), width=width+extra, joint="curve")
        for junction in self.geometry["junctions"]:
            pts = junction["shape"]
            if len(pts)>=3 and any(self.visible(p) for p in pts):
                draw.polygon([self.point(p) for p in pts], fill=ROAD)
        # Thin lateral lane borders, never a centerline beneath a puck.
        for lane in visible:
            pts = lane["shape"]
            if lane["internal"] or len(pts)<2:
                continue
            for side in (-1, 1):
                border = []
                for index, p in enumerate(pts):
                    a, b = pts[max(0,index-1)], pts[min(len(pts)-1,index+1)]
                    dx, dy = b[0]-a[0], b[1]-a[1]
                    length = math.hypot(dx,dy) or 1
                    border.append(self.point((p[0]-side*dy/length*lane["width"]/2, p[1]+side*dx/length*lane["width"]/2)))
                draw.line(border, fill="#aebbc7", width=1)
        for detector in self.geometry["detectors"]:
            if self.visible((detector["x"],detector["y"])):
                x,y=self.point((detector["x"],detector["y"]))
                radius=max(2,2.0*self.scale)
                draw.ellipse((x-radius,y-radius,x+radius,y+radius), fill="#f6fafc", outline=NAVY, width=1)
        # A measured scale bar and north arrow remain visible in every pane.
        metres = 100 if self.geometry["layout"] == "CORRIDOR" else 50
        x,y=22,self.h-32
        draw.line((x,y,x+metres*self.scale,y),fill=NAVY,width=3)
        draw.line((x,y-5,x,y+5),fill=NAVY,width=2)
        draw.line((x+metres*self.scale,y-5,x+metres*self.scale,y+5),fill=NAVY,width=2)
        text(draw,(x,y-27),f"{metres} m",17,bold=True)
        text(draw,(self.w-24,18),"N ↑",19,bold=True,anchor="ra")
        return image

    def draw_signals(self, image, run, t, period="AM"):
        draw = ImageDraw.Draw(image)
        for signal in self.geometry["signals"]:
            events=run["supervisor_events"].get(signal["site"],[])
            index=bisect.bisect_right([e["time"] for e in events],t)-1
            state=events[index] if index>=0 else {"stage":0,"aspect":"green"}
            code=signal["stages"][period][state["stage"]][state["aspect"]]
            groups={}
            for link in signal["links"]:
                groups.setdefault(link["from_lane"],[]).append(link)
            for lane_id,links in groups.items():
                lane=self.lanes[lane_id];points=lane["shape"]
                if len(points)<2 or not self.visible(points[-1]):
                    continue
                a,b=points[-2],points[-1];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy) or 1
                normal=(-dy/length,dx/length)
                links=sorted(links,key=lambda x:x["link_index"])
                for index,link in enumerate(links):
                    start=-lane["width"]/2+lane["width"]*index/len(links)
                    end=-lane["width"]/2+lane["width"]*(index+1)/len(links)
                    u=self.point((b[0]+normal[0]*start,b[1]+normal[1]*start))
                    v=self.point((b[0]+normal[0]*end,b[1]+normal[1]*end))
                    char=code[link["link_index"]]
                    draw.line((*u,*v),fill="#ffffff",width=max(5,round(4*self.scale)))
                    draw.line((*u,*v),fill=SIGNAL.get(char,"#a7b4c1"),width=max(3,round(2.5*self.scale)))
            x,y=self.point((signal["x"],signal["y"]))
            label=f"{signal['site']} · S{state['stage']+1} · {state['aspect'].replace('_',' ')}"
            length=draw.textlength(label,font=font(17,True))
            yy=y+20
            draw.rounded_rectangle((x-length/2-8,yy,x+length/2+8,yy+30),radius=5,fill=NAVY)
            text(draw,(x,yy+5),label,17,fill="white",bold=True,anchor="ma")

    def rectangle(self, draw, x, y, angle, length, width, fill, halo=False):
        if not self.visible((x,y)):
            return
        rad=math.radians(angle);forward=(math.sin(rad),math.cos(rad));normal=(-forward[1],forward[0])
        points=[]
        for along,side in ((0,-.5),(0,.5),(-length,.5),(-length,-.5)):
            points.append(self.point((x+forward[0]*along+normal[0]*side*width,y+forward[1]*along+normal[1]*side*width)))
        if halo:
            cx,cy=self.point((x-forward[0]*length/2,y-forward[1]*length/2))
            draw.ellipse((cx-10,cy-10,cx+10,cy+10),outline="#e85363",width=3)
        draw.polygon(points,fill=fill,outline="#203e55")

    def motion_image(self, run, motion, t):
        image=self.background.copy();draw=ImageDraw.Draw(image)
        # The supplied 1 Hz actual samples are displayed with zero-order hold;
        # vehicle paths are never invented between missing IDs.
        index=max(0,min(len(motion["frames"])-1,bisect.bisect_right([f[0] for f in motion["frames"]],t)-1))
        for vid,x,y,angle in motion["frames"][index][1]:
            length,width,kind=motion["vehicles"][str(vid)]
            self.rectangle(draw,x,y,angle,length,width,PALETTE.get(kind,"#bcd3f4"))
        self.draw_signals(image,run,t)
        return image

    def probe_image(self, run, t):
        image=self.background.copy();draw=ImageDraw.Draw(image);points=run["probe_positions"]
        # Only the archived probe is rendered; ordinary-vehicle trajectories
        # were not preserved and are not fabricated for this recording.
        if points:
            past=[self.point((p["x"],p["y"])) for p in points if p["time_s"]<=t]
            if len(past)>1:
                draw.line(past,fill="#d7ab46",width=3)
            index=bisect.bisect_right([p["time_s"] for p in points],t)-1
            if 0<=index<len(points) and t<run["metrics"]["probe"]["arrival_s"]:
                p=points[index]
                prev=index-1
                while prev>=0 and math.dist((p["x"],p["y"]),(points[prev]["x"],points[prev]["y"]))<.05:
                    prev-=1
                if prev>=0:
                    q=points[prev];angle=math.degrees(math.atan2(p["x"]-q["x"],p["y"]-q["y"]))
                else:
                    nxt=points[min(index+1,len(points)-1)];angle=math.degrees(math.atan2(nxt["x"]-p["x"],nxt["y"]-p["y"]))
                self.rectangle(draw,p["x"],p["y"],angle,5,2,"#76cde7",halo=True)
        self.draw_signals(image,run,t)
        return image


def frame_base(title, subtitle, time_s, label):
    image=Image.new("RGB",(W,H),BG);draw=ImageDraw.Draw(image)
    draw.rectangle((0,0,W,143),fill=NAVY)
    draw.rectangle((0,0,W,6),fill=GOLD)
    text(draw,(32,24),"PASADA  /  SIMULATION EVIDENCE",22,fill=GOLD,bold=True)
    text(draw,(32,61),title,34,fill="white",bold=True)
    text(draw,(32,108),subtitle,19,fill="#d5e2ec")
    text(draw,(W-32,31),"T.E.A.M. · MANDAUE",21,fill="white",bold=True,anchor="ra")
    text(draw,(W-32,70),f"SIM {clock(time_s)}  ·  t={time_s:06.1f} s",22,fill=GOLD,bold=True,anchor="ra")
    text(draw,(W-32,109),label,18,fill="#d5e2ec",anchor="ra")
    return image


def trace_at(run, t):
    sites={}
    for row in run["sensor_trace"]:
        if row["time_s"]>t:
            break
        sites[row["site"]]=row
    return sites


def rounded_panel(draw, box):
    draw.rounded_rectangle(box,radius=12,fill="white",outline="#d6e0e8",width=1)


def render_ordinary_frame(layout, runs, motions, views, t, end=False):
    image=frame_base(f"{layout} · {CASE_NAMES[layout]}","AM demand ×1.00 · seed 7100 · matched inputs, simulated clock and playback speed",t,"30× playback · 1 Hz vehicle samples")
    draw=ImageDraw.Draw(image)
    for index,(arm,label) in enumerate((("fixed","FIXED BASELINE"),("rule","PASADA LOCAL CONTROL"))):
        x=32+index*944;run=runs[arm]
        rounded_panel(draw,(x,163,x+912,931))
        text(draw,(x+20,180),label,24,bold=True)
        image.paste(views[arm].motion_image(run,motions[arm],t),(x+12,221))
        traces=trace_at(run,t)
        yy=841
        if layout=="CORRIDOR":
            for j,site in enumerate(("J1","J2","J3")):
                r=traces.get(site,{})
                text(draw,(x+18,yy+j*25),f"{site}: stock {r.get('stock_raw','—')}   entries {r.get('boundary_entries','—')}   exits {r.get('boundary_exits','—')}",17,bold=j==0)
            halt=next(iter(traces.values()),{}).get("halting_network","—")
            text(draw,(x+650,yy),f"Network halted: {halt}",16,bold=True)
        else:
            r=traces.get(layout,{})
            for j,(key,lab) in enumerate((("stock_raw","STOCK"),("boundary_entries","ENTRIES"),("boundary_exits","EXITS"),("halting_network","NETWORK HALTED"))):
                text(draw,(x+20+j*220,yy),lab,14,fill=MUTED,bold=True)
                text(draw,(x+20+j*220,yy+23),r.get(key,"—"),27,bold=True)
        metric=run["metrics"]
        summary=f"At 4,200 s cutoff: cohort completed {metric['study_cohort_completed']:,}  ·  active {metric['study_cohort_active']:,}  ·  uninserted {metric['study_cohort_uninserted']:,}"
        text(draw,(x+18,909),summary,14,fill=MUTED)
    text(draw,(32,954),"MOTION: observer-only deterministic reproduction; original sensor traces and exact signal transitions match.",23,bold=True)
    text(draw,(32,991),"Neutral dots = catalogued lane detectors; individual occupancy was not archived. No painted queue vehicles.",20,fill=MUTED)
    text(draw,(32,1028),"Native SUMO geometry © OpenStreetMap contributors  ·  Reconstructed full-count demand  ·  Motor-only model; no field validation",18,fill=MUTED)
    if end:
        draw.rounded_rectangle((590,765,1330,813),radius=8,fill=NAVY)
        text(draw,(960,776),"Full results retain unfinished and uninserted demand.",20,fill="white",bold=True,anchor="ma")
    return image


def emergency_times(run):
    m=run["metrics"];enc=m["encounters"]["J3"];truth=m["ground_truth_encounters"]["J3"]
    yellow=next((e["time"] for e in run["supervisor_events"]["J3"] if e["time"]>=enc["request_s"] and e["aspect"]=="yellow"),None)
    red=next((e["time"] for e in run["supervisor_events"]["J3"] if e["time"]>=enc["request_s"] and e["aspect"]=="all_red"),None)
    return [("Qualified fix",enc["request_s"]),("Yellow",yellow),("All-red",red),("Compatible green",enc.get("first_compatible_green_s")),
            ("20 s cap ends",enc["release_s"]),("Actual passage",truth["stopline_pass_s"])]


def render_emergency_frame(runs,views,t,end=False):
    image=frame_base("J3 · Emergency journey comparison","AM demand ×1.00 · seed 7300 · same ordinary driver proxy, route and dispatch · three arms at identical clock",t,"30× playback · original 1 Hz probe")
    draw=ImageDraw.Draw(image)
    for index,(arm,label) in enumerate((("fixed","FIXED BASELINE"),("local","LOCAL CONTROL"),("priority20","LOCAL + BEACON (20 s)"))):
        x=24+index*632;run=runs[arm];m=run["metrics"];p=m["probe"]
        rounded_panel(draw,(x,163,x+608,921))
        text(draw,(x+16,179),label,22,bold=True)
        text(draw,(x+16,211),"Priority applied" if arm=="priority20" else "Beacon observations only; no priority",15,fill=MUTED)
        image.paste(views[arm].probe_image(run,t),(x+8,242))
        status="Awaiting scheduled dispatch" if t<1800 else "Waiting to enter network" if t<p["depart_s"] else "ARRIVED" if t>=p["arrival_s"] else "Probe moving / queued"
        text(draw,(x+16,670),status,19,bold=True)
        text(draw,(x+16,703),f"Insertion delay {p['departDelay']:.1f} s  ·  On-road {p['duration']:.1f} s",17)
        text(draw,(x+16,731),f"Dispatch → arrival {p['dispatch_to_arrival_s']:.1f} s",19,bold=True)
        for i,(name,when) in enumerate(emergency_times(run)):
            col=i%2;row=i//2;xx=x+16+col*295;yy=774+row*41
            fill=INK if when is not None and t>=when else MUTED
            text(draw,(xx,yy),name,14,fill=fill,bold=when is not None and t>=when)
            text(draw,(xx,yy+18),"unreported" if when is None else f"{when:.1f} s",16,fill=fill)
    text(draw,(24,945),"This seed: beacon-priority on-road time 538 s versus local 515 s — 23 s slower. The unfavorable result is retained.",23,bold=True)
    text(draw,(24,983),"The 20 s request expires before passage; early compatible green does not imply an ambulance has passed.",22,fill=MUTED)
    text(draw,(24,1021),"Original archived probe only; ordinary vehicle positions unavailable. Red locator halo enlarged. Ideal GNSS; no physical radio/field validation.",18,fill=MUTED)
    text(draw,(24,1050),"Native SUMO geometry © OpenStreetMap contributors · Gold trail = previously recorded probe positions; all arms use the same simulated clock.",16,fill=MUTED)
    return image


def render_fallback_frame(replay,t,end=False):
    frames=replay["frames"]
    index=max(0,min(len(frames)-1,bisect.bisect_right([f["t"] for f in frames],t)-1))
    frame=frames[index];site=next(s for s in frame["intersections"] if s["id"]=="J-A")
    image=frame_base("J-A · Fault, fixed fallback and recovery","Browser synthetic resilience scenario · seed 42 · exported engine frames and timestamped events",t,"4× playback · 1 Hz browser frames")
    draw=ImageDraw.Draw(image)
    rounded_panel(draw,(32,164,865,931));rounded_panel(draw,(889,164,1888,931))
    text(draw,(58,187),"WHOLE-INTERSECTION STATE",25,bold=True)
    text(draw,(58,231),site["mode"].replace("_"," "),31,bold=True)
    text(draw,(58,278),f"Actual engine phase: {site['phase']}",20,fill=MUTED)
    text(draw,(58,312),f"Phase elapsed: {site['phase_elapsed_s']} s",20,fill=MUTED)
    phase=site["phase"]
    aspects={"NS":"red","EW":"red"}
    if phase.startswith("NS_"):
        aspects["NS"]="green" if phase.endswith("GREEN") else "yellow" if phase.endswith("YELLOW") else "red"
    elif phase.startswith("EW_"):
        aspects["EW"]="green" if phase.endswith("GREEN") else "yellow" if phase.endswith("YELLOW") else "red"
    for i,axis in enumerate(("NS","EW")):
        x=70+i*390
        text(draw,(x,366),"NORTH / SOUTH" if axis=="NS" else "EAST / WEST",21,bold=True)
        draw.rounded_rectangle((x,407,x+334,514),radius=17,fill=NAVY)
        for j,(color,fill) in enumerate((("red","#ec626a"),("yellow","#f4c653"),("green","#50d293"))):
            cx=x+60+j*107;cy=460
            draw.ellipse((cx-30,cy-30,cx+30,cy+30),fill=fill if aspects[axis]==color else "#345068",outline="#e0e8ee" if aspects[axis]==color else "#345068",width=2)
        text(draw,(x,536),aspects[axis].upper(),22,bold=True)
    health=site["device_health"];offline=[k for k,v in health.items() if v!="online"]
    text(draw,(58,590),f"Device heartbeat health: {len(health)-len(offline)} / {len(health)} online",23,bold=True)
    text(draw,(58,630),f"Health state: {site['health']}  ·  Pending mode: {site.get('pending_mode') or 'none'}",20)
    if offline:
        text(draw,(58,671),"Missing heartbeat: "+offline[0],17,fill="#b74452",bold=True)
    else:
        text(draw,(58,671),"No missing heartbeat in this exported frame.",18,fill=MUTED)
    start=next((e["t"] for e in replay["events"] if e["kind"]=="RECOVERY_STARTED"),None)
    ready=next((e["t"] for e in replay["events"] if e["kind"]=="RECOVERY_READY"),None)
    elapsed=min(ready-start,max(0,t-start)) if start is not None and ready is not None else None
    timer="Not started" if elapsed is None or t<start else f"{elapsed:.0f} / {ready-start:.0f} s"
    text(draw,(58,721),"Continuous healthy recovery",20,bold=True)
    text(draw,(58,756),timer,31,bold=True)
    draw.rounded_rectangle((58,807,824,830),radius=7,fill="#e1e8ee")
    if elapsed is not None and elapsed>0:
        draw.rounded_rectangle((58,807,58+766*elapsed/(ready-start),830),radius=7,fill=GOLD)
    text(draw,(58,858),f"Synthetic arrivals: {site['arrived']}   ·   Synthetic departures: {site['departed']}",20,bold=True)
    text(draw,(914,187),"RECORDED ENGINE EVENT LOG",25,bold=True)
    events=[e for e in replay["events"] if e["t"]<=t][-8:]
    y=235
    for event in events:
        color="#b74452" if event["severity"]=="error" else "#9d7527" if event["severity"]=="warning" else INK
        text(draw,(914,y),f"{event['t']:03d} s  ·  {event['kind'].replace('_',' ')}",19,fill=color,bold=True)
        lines=textwrap.wrap(event["message"],width=84)
        for j,line in enumerate(lines):
            text(draw,(914,y+27+j*23),line,17,fill=MUTED)
        y+=35+23*len(lines)
    text(draw,(32,954),"EVIDENCE TYPE: browser synthetic fault logic — separate from SUMO and physical cabinet or radio acceptance.",23,bold=True)
    text(draw,(32,992),"Two-axis browser profile: 3 s yellow / 2 s all-red. Original SUMO study uses four stages and 4 s / 4 s clearance.",21,fill=MUTED)
    text(draw,(32,1031),"The missing puck, fallback mode, 60 s recovery interval and safe return are read directly from the exported replay JSON.",19,fill=MUTED)
    return image


def encode(path, frame_function, duration, fps, intro, t0, t1, speed):
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-vcodec","rawvideo","-pix_fmt","rgb24",
         "-s",f"{W}x{H}","-r",str(fps),"-i","-","-an","-c:v","libx264","-preset","fast","-crf","21",
         "-pix_fmt","yuv420p","-threads","2","-movflags","+faststart",str(path)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for n in range(round(duration*fps)):
            elapsed=n/fps
            t=max(t0,min(t1,t0+max(0,elapsed-intro)*speed))
            frame=frame_function(t,elapsed>=intro+(t1-t0)/speed)
            proc.stdin.write(frame.tobytes())
            if n%(fps*10)==0:
                print(f"{path.name}: {elapsed:.0f}/{duration}s",flush=True)
    finally:
        proc.stdin.close()
        rc=proc.wait()
    if rc:
        raise RuntimeError(f"FFmpeg failed ({rc}): {path}")
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)]))
    stream=probe["streams"][0]
    assert stream["codec_name"]=="h264" and stream["width"]==1920 and stream["height"]==1080
    assert abs(float(probe["format"]["duration"])-duration)<.1
    return {"codec":stream["codec_name"],"width":stream["width"],"height":stream["height"],"duration_s":float(probe["format"]["duration"]),
            "fps":fps,"bytes":path.stat().st_size,"sha256":sha(path)}


def contacts(output, video_id, frame_function, times):
    contact=Image.new("RGB",(1920,1080),BG)
    for i,t in enumerate(times):
        frame=frame_function(t,False)
        if i==1:
            frame.save(output/f"{video_id}_still.png")
        contact.paste(frame.resize((960,540),Image.Resampling.LANCZOS),((i%2)*960,(i//2)*540))
    contact.save(output/f"{video_id}_contact.png")


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--replays",type=Path,default=Path(__file__).resolve().parents[1]/"dist/replays")
    p.add_argument("--captures",type=Path,default=Path("/workspace/scratch/cf04383f0d55/motion-captures"))
    p.add_argument("--output",type=Path,default=Path("/workspace/scratch/cf04383f0d55/pasada-video-evidence"))
    p.add_argument("--only",choices=["all","V01","V02","V03","V04","V05","V06"],default="all")
    p.add_argument("--fps",type=int,default=20)
    a=p.parse_args(argv);a.output.mkdir(parents=True,exist_ok=True)
    manifest=load_json(a.replays/"manifest.json");index={r["id"]:r for r in manifest["runs"]}
    release_path=a.output/"render_manifest.json"
    release=load_json(release_path) if release_path.exists() else {"schema":"pasada.video-evidence/1","videos":{},"sources":manifest["sources"]}
    for num,layout in enumerate(("J1","J2","J3","CORRIDOR"),start=1):
        video_id=f"V{num:02d}"
        if a.only not in ("all",video_id):
            continue
        if video_id in release["videos"] and Path(release["videos"][video_id]["file"]).is_file():
            print(f"Preserving completed {video_id}",flush=True)
            continue
        g=load_json(a.replays/manifest["geometry"][layout]);signals=g["signals"]
        if layout=="CORRIDOR":
            bounds=(min(x["x"] for x in signals)-150,min(x["y"] for x in signals)-150,max(x["x"] for x in signals)+150,max(x["y"] for x in signals)+150)
        else:
            center=signals[0];bounds=(center["x"]-220,center["y"]-220,center["x"]+220,center["y"]+220)
        runs={};motions={};verification={};views={}
        for arm in ("fixed","rule"):
            meta=index[f"ordinary-{layout}_AM-{arm}-7100"]
            runs[arm]=load_json(a.replays/meta["file"])
            motions[arm],verification[arm]=validate_capture(a.captures/f"{layout}_AM"/arm,runs[arm])
            views[arm]=View(g,(0,0,888,610),bounds)
        function=lambda t,end=False:render_ordinary_frame(layout,runs,motions,views,t,end)
        path=a.output/f"{video_id}_{layout}_AM_Seed7100_Fixed_vs_PASADA.mp4"
        contacts(a.output,video_id,function,[1200,1600,2000,2400])
        result=encode(path,function,45,a.fps,3,1200,2400,30)
        release["videos"][video_id]={"file":str(path),"title":CASE_NAMES[layout],"type":"Observer-only deterministic reproduction; exact original controller/sensor traces match",
                                     "case":f"{layout}_AM","seed":7100,"arms":["fixed","rule"],"clock_s":[1200,2400],"playback_speed":30,
                                     "capture_verification":verification,"video":result}
        release_path.write_text(json.dumps(release,indent=2))
    if a.only in ("all","V06") and not ("V06" in release["videos"] and Path(release["videos"]["V06"]["file"]).is_file()):
        runs={arm:load_json(a.replays/index[f"emergency-main-J3_AM-{arm}-7300"]["file"]) for arm in ("fixed","local","priority20")}
        g=load_json(a.replays/manifest["geometry"]["J3"])
        positions=[p for r in runs.values() for p in r["probe_positions"]]
        bounds=(min(p["x"] for p in positions)-40,min(p["y"] for p in positions)-100,max(p["x"] for p in positions)+40,max(p["y"] for p in positions)+100)
        views={arm:View(g,(0,0,592,410),bounds) for arm in runs}
        function=lambda t,end=False:render_emergency_frame(runs,views,t,end)
        path=a.output/"V06_J3_AM_Seed7300_Emergency_Three_Arms.mp4"
        contacts(a.output,"V06",function,[1800,2255,2603,3415])
        result=encode(path,function,60,a.fps,2,1750,3430,30)
        release["videos"]["V06"]={"file":str(path),"title":"J3 matched emergency journey comparison","type":"Original archived 1 Hz probe and exact controller event playback",
                                    "case":"J3_AM","seed":7300,"arms":["fixed","local","priority20"],"clock_s":[1750,3430],"playback_speed":30,
                                    "probe_metrics":{arm:r["metrics"]["probe"] for arm,r in runs.items()},"video":result}
        release_path.write_text(json.dumps(release,indent=2))
    if a.only in ("all","V05") and not ("V05" in release["videos"] and Path(release["videos"]["V05"]["file"]).is_file()):
        source=a.output/"browser-fallback-replay.json";replay=load_json(source)
        assert replay["provenance"]["source"]=="synthetic" and len(replay["frames"])==180
        function=lambda t,end=False:render_fallback_frame(replay,t,end)
        path=a.output/"V05_Browser_Synthetic_Fault_Fallback_Recovery.mp4"
        contacts(a.output,"V05",function,[44,56,120,155])
        result=encode(path,function,49,a.fps,2,1,180,4)
        release["videos"]["V05"]={"file":str(path),"title":"Browser synthetic fault, fixed fallback and recovery",
                                    "type":"Original browser synthetic engine frame/event playback; not SUMO or hardware evidence",
                                    "seed":42,"clock_s":[1,180],"playback_speed":4,"source_file":str(source),"source_sha256":sha(source),
                                    "provenance":replay["provenance"],"video":result}
        release_path.write_text(json.dumps(release,indent=2))
    print(json.dumps({"output":str(a.output),"completed":list(release["videos"])}),flush=True)


if __name__=="__main__":
    main()
