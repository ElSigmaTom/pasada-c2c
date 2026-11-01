"""Assemble V00 from the verified evidence clips, retaining their source labels."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import argparse,subprocess,json,textwrap
p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True);a=p.parse_args();work=a.folder/'V00_segments';work.mkdir(exist_ok=True)
F=lambda n,b=False:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold'if b else '')+'.ttf',n)
def card(name,title,lines):
 im=Image.new('RGB',(1920,1080),'#153750');d=ImageDraw.Draw(im);d.rectangle((0,0,1920,7),fill='#f5cd62');d.text((70,70),'PASADA / T.E.A.M. / VIDEO V00',font=F(27,True),fill='#f5cd62');d.text((70,150),title,font=F(46,True),fill='white');y=280
 for line in lines:
  for ln in textwrap.wrap(line,91):d.text((80,y),ln,font=F(30),fill='#d8e5ed');y+=49
  y+=35
 out=work/(name+'.png');im.save(out);return out
intro=card('intro','Simulation evidence overview',['A. Soriano Avenue study corridor · Mandaue City','Three isolated junctions and their connected network.','Matched ordinary comparisons, an emergency counterexample, and synthetic fault recovery.','Short excerpts below retain each source clip’s evidence label and simulated clock.'])
end=card('limits','Read each result within its evidence scope',['Ordinary motion: reproduced from frozen inputs; all archived signal and sensor traces match.','Emergency probe: original saved positions and controller events.','Fault logic: separate synthetic browser engine; hardware remains unverified.','All126 original traces replay in C2C. Full V01–V08 clips are indexed in the AI Scratchpad.'])
segments=[]
def encode(src,start,duration,still=False):
 out=work/(f'{len(segments):02d}.mp4');cmd=['ffmpeg','-y','-hide_banner','-loglevel','error']
 if still:cmd+=['-loop','1','-i',str(src)]
 else:cmd+=['-ss',str(start),'-i',str(src)]
 cmd+=['-t',str(duration),'-an','-vf','fps=20,format=yuv420p','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-movflags','+faststart',str(out)]
 subprocess.run(cmd,check=True);segments.append(out)
encode(intro,0,5,True)
for prefix,start,dur in [('V04_',5,12),('V03_',5,12),('V05_',10,15),('V05_',38,7),('V06_',20,12),('V07_',47,7)]:
 src=next(a.folder.glob(prefix+'*.mp4'));encode(src,start,dur)
encode(end,0,8,True)
lst=work/'concat.txt';lst.write_text(''.join(f"file '{s.resolve()}'\n"for s in segments));out=a.folder/'V00_PASADA_Simulation_Evidence_Overview.mp4'
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(lst),'-c','copy','-movflags','+faststart',str(out)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_name,width,height','-show_entries','format=duration,size','-of','json',str(out)]));assert 60<=float(probe['format']['duration'])<=90
print(json.dumps({'path':str(out),'probe':probe}),flush=True)
