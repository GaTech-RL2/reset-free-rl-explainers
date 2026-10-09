"""Narrated mathematical films with paragraph-aligned visual derivation steps."""
import argparse,bisect,json,math,subprocess
from functools import lru_cache
from pathlib import Path
from PIL import Image
from drawing import *
from scenes import scene
from prepare_math import key
ROOT=Path(__file__).resolve().parents[1]

@lru_cache(256)
def equation(math,color):
    im=Image.open(ROOT/'assets/math'/f'{key(math,color)}.png').convert('RGBA')
    # math_to_image uses a white canvas. Derive alpha from coverage so colored
    # antialiasing remains crisp on the dark film and HTML backgrounds.
    import numpy as np
    a=np.array(im).astype(float)
    target=np.array([int(color[i:i+2],16) for i in (1,3,5)])
    channel=int(np.argmax(255-target));coverage=(255-a[:,:,channel])/max(1,255-target[channel])
    a[:,:,:3]=target;a[:,:,3]=np.clip(coverage,0,1)*255
    im=Image.fromarray(a.astype('uint8'),'RGBA')
    bbox=im.getbbox()
    if bbox:im=im.crop(bbox)
    scale=min(1,1470/im.width,79/im.height)
    if scale<1:im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
    return im

def frame(ep,t,subtitles=True):
    ci=max(0,min(len(ep['chapters'])-1,bisect.bisect_right([c['start'] for c in ep['chapters']],t)-1))
    ch=ep['chapters'][ci];local=t-ch['start'];p=clamp(local/ch['duration'])
    beats=ch.get('beat_starts',[ch['start']+ch['duration']*k/3 for k in range(3)])
    b=max(0,min(2,bisect.bisect_right(beats,t)-1))
    im=BASE.copy();c=Canvas(im);color=ep['color']
    c.text(55,26,f'{ep["number"]}  /  {ep["short"].upper()}',20,color,True)
    c.text(1543,26,f'LEARNING WITHOUT A RESET     {ci+1:02} / 12',18,MUTED,anchor='ra')
    size=42
    while c.d.textlength(ch['title'],font=font(size,True))>1490:size-=1
    c.text(55,72,ch['title'],size,INK,True)
    c.line([(53,134),(1546,134)],LINE,1)
    scene(c,ch['visual'],p,b,ep)
    c.d.rounded_rectangle((1004,159,1548,641),radius=18,fill=PANEL,outline=LINE,width=1)
    c.text(1030,178,'BUILD THE ARGUMENT',17,MUTED,True)
    for j,step in enumerate(ch['steps']):
        y=222+j*132;active=j==b;done=j<b
        co=color if active else MUTED if done else '#60738f'
        c.circle(1036,y+17,12,co,co if active else None,2)
        c.text(1036,y+17,str(j+1),15,BG if active else co,True,'mm')
        height=c.wrap(1060,y,step['title'],452,22,INK if active else co,active,1.24)
        c.wrap(1060,y+height+9,step['explain'],447,19,MUTED if j<=b else '#596b84',leading=1.27)
    c.line([(55,665),(1545,665)],LINE,1)
    eq=equation(ch['steps'][b]['math'],color);im.paste(eq,((W-eq.width)//2,694+(79-eq.height)//2),eq)
    c.text(800,797,f'{ep["short"]} · {ep["year"]}    /    Primary sources and full derivations in the companion',17,MUTED,anchor='mm')
    if subtitles:
        subs=ep.get('subtitles',[]);si=bisect.bisect_right([x['start'] for x in subs],t)-1
        if si>=0 and t<subs[si]['end']+.12:
            s=subs[si]['text'];width=c.d.textlength(s,font=font(24))
            if width<=1470:c.text(800,843,s,24,INK,anchor='mm')
            else:
                words=s.split();mid=len(words)//2
                c.text(800,831,' '.join(words[:mid]),22,INK,anchor='mm');c.text(800,860,' '.join(words[mid:]),22,INK,anchor='mm')
    c.d.rectangle((0,892,W,H),fill=LINE);c.d.rectangle((0,892,W*t/ep['duration'],H),fill=color)
    for chapter in ep['chapters']:
        x=W*chapter['start']/ep['duration'];c.line([(x,892),(x,900)],BG,2)
    if local<.22:im=Image.blend(BASE,im,ease(local/.22))
    return im

def render(ep,fps=20):
    out=ROOT/'media'/f'{ep["id"]}.mp4';duration=ep['duration']
    args=['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(fps),'-i','-',
          '-i',str(ROOT/'media'/f'{ep["id"]}.wav'),'-i',str(ROOT/'captions'/f'{ep["id"]}.srt'),'-i',str(ROOT/'media'/f'{ep["id"]}-chapters.ffmeta'),
          '-map','0:v','-map','1:a','-map','2:s','-map_metadata','3','-map_chapters','3','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-threads','3',
          '-c:a','aac','-b:a','112k','-c:s','mov_text','-metadata:s:s:0','language=eng','-metadata','title='+ep['short']+' — '+ep['title'],
          '-metadata','comment=Original educational animation and synthetic narration. All toy experiments are labeled; paper sources in companion HTML.',
          '-t',str(duration),'-movflags','+faststart',str(out)]
    with (ROOT/'qa'/f'{ep["id"]}-ffmpeg.log').open('w') as log:
        proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=log)
        try:
            for i in range(round(duration*fps)):
                proc.stdin.write(frame(ep,i/fps).tobytes())
                if i%(60*fps)==0:print(ep['id'],f'{i/fps:.0f}/{duration}s',flush=True)
        finally:proc.stdin.close()
        if proc.wait():raise RuntimeError(f'Render failed: {ep["id"]}')
    print('COMPLETE',ep['id'],round(out.stat().st_size/1e6,1),'MB',flush=True)

def previews(eps):
    for ep in eps:
        thumbs=[]
        for i,ch in enumerate(ep['chapters']):
            for b in range(3):
                starts=ch['beat_starts'];end=starts[b+1] if b<2 else ch['end']
                im=frame(ep,starts[b]+(end-starts[b])*.55,False)
                if b==1:im.save(ROOT/'previews'/f'{ep["id"]}-{i+1:02}.png')
                thumbs.append(im.resize((400,225)))
            if i==0:frame(ep,ch['start']+ch['duration']*.28,False).save(ROOT/'previews'/f'{ep["id"]}.jpg',quality=92)
        sheet=Image.new('RGB',(1600,225*9),BG)
        for i,im in enumerate(thumbs):sheet.paste(im,((i%4)*400,(i//4)*225))
        sheet.save(ROOT/'qa'/f'{ep["id"]}-storyboard.jpg',quality=90)
    print('Prepared full-resolution chapter previews and 216-beat storyboards.')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--episode');ap.add_argument('--previews',action='store_true');ap.add_argument('--fps',type=int,default=20);a=ap.parse_args()
    eps=json.loads((ROOT/'content.json').read_text())
    if a.episode:eps=[e for e in eps if e['id']==a.episode]
    if a.previews:previews(eps)
    else:
        for e in eps:render(e,a.fps)
