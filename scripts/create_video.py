"""Render the promo from English scene narration (Pillow + imageio-ffmpeg).

Place voice-0.mp3 through voice-5.mp3 in media/. No model or account data is read.
"""
import json
import math
import subprocess
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'media'
WORK = ROOT / 'work/video'
WORK.mkdir(parents=True, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
SCENES = json.loads((MEDIA/'scenes.json').read_text(encoding='utf-8'))
SCALE = 1.5
W,H,FPS = 1920,1080,24
BG='#0B1220'; FG='#F5F2E9'; MUTED='#9AABC1'; GREEN='#8EF0C0'; AMBER='#FFCD7A'
def font(n,bold=False):
    candidates = [Path('C:/Windows/Fonts') / ('segoeuib.ttf' if bold else 'segoeui.ttf'),
                  Path('/usr/share/fonts/truetype/dejavu') / ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')]
    return ImageFont.truetype(str(next(p for p in candidates if p.exists())),int(n*SCALE))
FONTS={}
def f(n,bold=False):
    key=(n,bold)
    if key not in FONTS: FONTS[key]=font(*key)
    return FONTS[key]
def text(d,xy,s,n=24,c=FG,b=False):
    d.text(tuple(int(v*SCALE) for v in xy),s,font=f(n,b),fill=c)
def rect(d,box,fill,r=18,outline=None):
    d.rounded_rectangle(tuple(int(v*SCALE) for v in box),radius=int(r*SCALE),fill=fill,outline=outline,width=2)
def line(d,box,c,width=1):
    d.line(tuple(int(v*SCALE) for v in box),fill=c,width=int(width*SCALE))
def wrap(d,s,n,width):
    lines=[]; current=''
    for word in s.split():
        candidate=(current+' '+word).strip()
        if d.textlength(candidate,font=f(n)) > width*SCALE and current:
            lines.append(current); current=word
        else: current=candidate
    if current: lines.append(current)
    return lines

def base(i):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    for x in range(0,1280,80): line(d,(x,0,x,720),'#101C2B')
    for y in range(0,720,80): line(d,(0,y,1280,y),'#101C2B')
    rect(d,(54,40,88,74),GREEN,9)
    text(d,(63,41),'Q',23,BG,True)
    text(d,(102,43),'QUOTAGUARD',18,FG,True)
    text(d,(1000,48),'BUILT FOR PLUS',14,GREEN,True)
    text(d,(60,106),f'0{i+1} / 06',13,MUTED,True)
    text(d,(60,137),SCENES[i][0],46,FG,True)
    if i==0:
        text(d,(63,216),'A time-aware skill for Work + Codex',25,MUTED)
        rect(d,(65,295,1215,548),'#142335',24)
        text(d,(98,324),'REMAINING QUOTA',15,MUTED,True)
        text(d,(98,355),'10%',84,FG,True)
        text(d,(425,324),'TIME UNTIL RESET',15,MUTED,True)
        text(d,(425,366),'15 min',65,FG,True)
        text(d,(850,324),'NEXT MOVE',15,MUTED,True)
        text(d,(850,373),'Think in',32,GREEN,True)
        text(d,(850,415),'small stages.',32,GREEN,True)
        text(d,(65,570),'The percentage tells only half the story.',21,MUTED)
    elif i==1:
        for x,clock,rate,label,color in [(65,'2 hours','5','TIGHT',AMBER),(665,'15 minutes','40','ABUNDANT',GREEN)]:
            rect(d,(x,240,x+550,566),'#142335',22)
            text(d,(x+30,267),'10% LEFT',28,FG,True)
            text(d,(x+30,314),f'Reset in {clock}',25,MUTED)
            text(d,(x+30,363),rate,78,color,True)
            text(d,(x+168,411),'points / hour',22,MUTED)
            rect(d,(x+30,491,x+500,537),'#203245',9)
            text(d,(x+46,500),label,20,color,True)
    elif i==2:
        text(d,(65,232),'Turn a countdown into a planning budget.',23,MUTED)
        rect(d,(65,300,1215,468),'#142335',22)
        text(d,(102,345),'10%',65,FG,True)
        text(d,(290,353),'/',50,MUTED)
        text(d,(365,345),'0.25 h',65,FG,True)
        text(d,(650,353),'=',50,MUTED)
        text(d,(750,345),'40',65,GREEN,True)
        text(d,(900,379),'points / hour',25,GREEN)
        text(d,(75,499),'Still only 10% available before reset.',26,AMBER,True)
        text(d,(75,542),'A planning budget. Not measured consumption.',21,MUTED)
    elif i==3:
        text(d,(65,228),'Personal reference: 12 percentage points per hour',24,MUTED)
        labels=[('TIGHT','< 6',AMBER),('CONSERVATIVE','6 to < 12','#E9DCA8'),('COMFORTABLE','12 to < 18','#A5E3D8'),('ABUNDANT','18+',GREEN)]
        for k,(label,band,c) in enumerate(labels):
            x=65+k*294
            rect(d,(x,302,x+268,530),'#142335',16)
            rect(d,(x+20,323,x+248,330),c,2)
            text(d,(x+22,361),band,37,c,True)
            text(d,(x+22,438),label,15,FG,True)
            text(d,(x+22,473),'points / hour',16,MUTED)
        text(d,(65,562),'A workflow preference, not an OpenAI rate limit.',21,MUTED)
    elif i==4:
        cards=[('01','Weekly quota','Check the longer window.'),('02','Essential checks','Protect correctness.'),('03','Resume notes','Leave one concrete next step.')]
        for k,(num,title,desc) in enumerate(cards):
            y=240+k*108
            rect(d,(65,y,1215,y+90),'#142335',14)
            text(d,(90,y+23),num,27,GREEN,True)
            text(d,(180,y+18),title,27,FG,True)
            text(d,(650,y+27),desc,21,MUTED)
        text(d,(65,585),'No extra quota. No guaranteed savings.',22,AMBER)
    else:
        text(d,(65,228),'Install once. Invoke when it matters.',24,MUTED)
        rect(d,(65,290,1215,454),'#142335',20)
        text(d,(95,318),'python install.py',26,GREEN)
        text(d,(95,375),'$quotaguard Check my quota and plan this task.',25,FG)
        text(d,(65,493),'github.com/liuguangyu272/quotaguard-skill',28,GREEN,True)
        text(d,(65,547),'Python 3.11+  /  Local Codex sign-in  /  MIT licensed',18,MUTED)
    text(d,(65,684),'ILLUSTRATIVE DEMO · SIMULATED QUOTA',11,MUTED)
    text(d,(890,684),'Independent project · Not affiliated with OpenAI',11,MUTED)
    return im

def stamp(t):
    ms=round(t*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def main():
    durations=[]; chunks=[]; subs=[]; cursor=0
    for i,(_,narration) in enumerate(SCENES):
        wav=WORK/f'{i}.wav'
        subprocess.run([FF,'-y','-loglevel','error','-i',str(MEDIA/f'voice-{i}.mp3'),'-ac','1','-ar','48000',str(wav)],check=True)
        with wave.open(str(wav),'rb') as w: data=w.readframes(w.getnframes())
        duration=len(data)/96000
        total=math.ceil((duration+0.65)*FPS)/FPS
        durations.append(total)
        chunks.append(data+b'\0'*int((total-duration)*96000))
        sentences=[x.strip()+'.' for x in narration.split('.') if x.strip()]
        weights=[len(x.split()) for x in sentences]; start=cursor
        for sentence,weight in zip(sentences,weights):
            end=start+duration*weight/sum(weights)
            subs.append((start,end,sentence)); start=end
        cursor+=total
    with wave.open(str(WORK/'voice.wav'),'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes(b''.join(chunks))
    (MEDIA/'quotaguard-promo.en.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{s}' for i,(a,b,s) in enumerate(subs))+'\n',encoding='utf-8')
    cmd=[FF,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-', '-i',str(WORK/'voice.wav'),'-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-shortest',str(MEDIA/'quotaguard-promo.mp4')]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    global_frame=0; cursor=0; contacts=[]
    for i,duration in enumerate(durations):
        scene=base(i)
        if i==0: scene.save(MEDIA/'poster.png')
        for frame in range(round(duration*FPS)):
            im=scene.copy(); d=ImageDraw.Draw(im); t=cursor+frame/FPS
            fraction=(frame+1)/(duration*FPS)
            rect(d,(65,657,1215,661),'#203245',1)
            rect(d,(65,657,65+1150*fraction,661),GREEN,1)
            active=next((s for a,b,s in subs if a<=t<b),None)
            if active:
                lines=wrap(d,active,20,1120)
                for j,ln in enumerate(lines):
                    width=d.textlength(ln,font=f(20))/SCALE
                    text(d,((1280-width)/2,607+j*24),ln,20,FG)
            if frame==round(duration*FPS/2):
                im.save(WORK/f'scene-{i}.png'); contacts.append(im.resize((640,360)))
            proc.stdin.write(im.tobytes()); global_frame+=1
        cursor+=duration
        print(f'Rendered scene {i+1}/6',flush=True)
    proc.stdin.close()
    if proc.wait()!=0: raise RuntimeError('Video encode failed')
    contact=Image.new('RGB',(1280,1080))
    for i,im in enumerate(contacts): contact.paste(im,((i%2)*640,(i//2)*360))
    contact.save(WORK/'contact-sheet.jpg')
    (MEDIA/'video-info.json').write_text(json.dumps({'duration_seconds':sum(durations),'width':W,'height':H,'fps':FPS,'voice':'en-US-GuyNeural (synthetic)','captions':'English, burned in and SRT','quota_values':'simulated'},indent=2),encoding='utf-8')
    print(f'Complete: {sum(durations):.2f} seconds',flush=True)

if __name__=='__main__': main()
