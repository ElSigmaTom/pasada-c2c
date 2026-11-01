"""Create captioned MP4 walkthroughs from actual browser captures and a downloaded profile.
No USB dialog, physical flashing, or device readback is invented.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import argparse,json,subprocess,textwrap
p=argparse.ArgumentParser();p.add_argument('--frames',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--profile',type=Path,required=True);p.add_argument('--only',choices=['V07','V08','all'],default='all');a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=True)
fonts='/usr/share/fonts/truetype/dejavu/'
F=lambda n,b=False:ImageFont.truetype(fonts+('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf'),n)
navy='#153750';gold='#f5cd62';gray='#b8cbd7'
frames=json.loads(a.frames.read_text());profile=json.loads(a.profile.read_text())
assert profile['device_id']=='PUCK-C-SORIANO_SE-IN-L1-U05'
def base(clip,title,subtitle):
 im=Image.new('RGB',(1920,1080),navy);d=ImageDraw.Draw(im);d.rectangle((0,0,1920,7),fill=gold);d.text((55,26),f'PASADA / T.E.A.M.     {clip}',font=F(23,True),fill=gold);d.text((55,66),title,font=F(33,True),fill='white');d.text((55,112),subtitle,font=F(19),fill=gray);return im,d

def screenshot_slide(clip,title,f):
 im,d=base(clip,title,'Actual browser UI stills · captioned walkthrough · simulation workspace')
 image=Image.open(a.frames.parent/Path(f['path']).name).convert('RGB');image.thumbnail((1750,780),Image.Resampling.LANCZOS);x=(1920-image.width)//2;y=156+(780-image.height)//2;im.paste(image,(x,y));d.rectangle((x-1,y-1,x+image.width,y+image.height),outline=gray,width=1)
 for i,line in enumerate(textwrap.wrap(f['caption'],115)):d.text((60,956+i*31),line,font=F(23),fill='white')
 return im

def card(clip,title,lines):
 im,d=base(clip,title,'Browser workflow evidence · physical hardware acceptance remains separate')
 y=220
 for line in lines:
  for ln in textwrap.wrap(line,99):d.text((95,y),ln,font=F(27),fill='white');y+=43
  y+=25
 return im

def encode(clip,title,slides):
 folder=a.output/(clip+'_slides');folder.mkdir(exist_ok=True);lst=[]
 for i,(im,duration)in enumerate(slides):
  f=folder/f'{i:02d}.png';im.save(f);lst.append(f"file '{f}'\nduration {duration}\n")
 lst.append(f"file '{folder/f'{len(slides)-1:02d}.png'}'\n")
 c=folder/'concat.txt';c.write_text(''.join(lst));out=a.output/f'{clip}_{title}.mp4'
 subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(c),'-vf','fps=15,format=yuv420p','-c:v','libx264','-threads','2','-preset','veryfast','-crf','19','-movflags','+faststart',str(out)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_name,width,height','-show_entries','format=duration,size','-of','json',str(out)]));assert probe['streams'][0]['codec_name']=='h264' and probe['streams'][0]['width']==1920
 print(json.dumps({'id':clip,'path':str(out),'probe':probe}),flush=True)
if a.only in ['V08','all']:
 selected=[f for f in frames if f['name'] in ['pasada-ui-v08-02-https','pasada-ui-v08-03-no-device']]
 assert len(selected)==2
 loc=profile['location'];sensor=profile['sensor']
 slides=[(card('V08','Individual device setup', ['Select an intersection and one planned component.','Request a USB connection and download its device profile.','This clip uses actual browser UI stills and the file downloaded during the recorded interaction.']),5)]
 slides.extend((screenshot_slide('V08','A. Soriano / selected planning component',f),10)for f in selected)
 slides.append((card('V08','The downloaded device profile', [f"Planning ID: {profile['device_id']}",f"Site: {profile['intersection_id']}  /  role: {profile['role']}  /  coordinator: {profile['controller_id']}",f"Lane: {sensor['lane_id']}  /  upstream offset: {sensor['offset_m']} m",f"WGS84: {loc['latitude']:.7f}, {loc['longitude']:.7f}",f"Profile mode: {profile['security_mode']}  /  output: {profile['output_mode']}",'The native chooser was requested; no board was selected. Its native dialog is not captured in these page screenshots.']),13))
 slides.append((card('V08','Evidence boundary', ['Profile export does not write firmware.','Physical connection, flashing, authenticated enrollment, readback, and reboot retention require separate hardware evidence.','No compatible physical device was connected in this recording.']),6))
 encode('V08','Device_Connection_Profile_Export',slides)
if a.only in ['V07','all']:
 selected=[f for f in frames if 'v07-' in f['name']]
 assert len(selected)>=6
 slides=[(card('V07','C2C browser walkthrough', ['Actual UI stills from the running PASADA browser app.','Installation planning, emergency registry, synthetic diagnostics, and recorded-study replay have separate evidence scopes.']),5)]
 slides.extend((screenshot_slide('V07','Installation to operations',f),7)for f in selected)
 slides.append((card('V07','Evidence boundary',['The planning workspace uses proposed, editable device positions.','Recorded SUMO runs use frozen native lane and signal IDs; they do not certify the editable installation plan.','Real hardware, radio and cabinet connections remain unverified.']),6))
 encode('V07','C2C_Browser_Walkthrough',slides)
