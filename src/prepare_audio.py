"""Synthesize original scripts and align chapter/derivation beats to fourteen-minute lessons."""
import asyncio, json, subprocess, re, wave
from pathlib import Path
import edge_tts
from content import EPISODES, ROOT

RAW=ROOT/'media'/'narration'
RAW.mkdir(exist_ok=True)

def run(args):
    subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)

def duration(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)]))

def spoken(s):
    for a,b in [('MoReFree','More Free'),('RISC','risk'),('MEDAL','medal'),('EARL','Earl'),('RL','R L'),('MDP','M D P'),('CMDP','C M D P'),('UCB','U C B')]:
        s=s.replace(a,b)
    return s

async def synth(ep,i,ch,sem):
    base=RAW/f'{ep["id"]}-{i:02}'
    mp3=base.with_suffix('.mp3'); meta=base.with_suffix('.json')
    if mp3.exists() and meta.exists(): return
    async with sem:
        for attempt in range(3):
            try:
                words=[]
                communicate=edge_tts.Communicate(spoken(ch['narration']),'en-US-AndrewNeural',rate='-8%',boundary='WordBoundary')
                with mp3.open('wb') as out:
                    async for event in communicate.stream():
                        if event['type']=='audio': out.write(event['data'])
                        elif event['type']=='WordBoundary':
                            words.append(dict(start=event['offset']/1e7,end=(event['offset']+event['duration'])/1e7,text=event['text']))
                meta.write_text(json.dumps(words))
                print('voiced',ep['id'],i,round(duration(mp3),1),flush=True)
                return
            except Exception as e:
                if attempt==2: raise
                print('retry',ep['id'],i,type(e).__name__,flush=True)
                await asyncio.sleep(1)

def timestamp(t,comma=False):
    ms=round(t*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02}{"," if comma else "."}{ms:03}'

async def main():
    sem=asyncio.Semaphore(3)
    await asyncio.gather(*(synth(ep,i,ch,sem) for ep in EPISODES for i,ch in enumerate(ep['chapters'])))
    for ep in EPISODES:
        rawdur=[duration(RAW/f'{ep["id"]}-{i:02}.mp3') for i in range(len(ep['chapters']))]
        target=ep['target_duration']
        scale=(target-1.5*len(rawdur))/sum(rawdur); cursor=0; subtitles=[]; chapterfiles=[]
        for i,(ch,dur) in enumerate(zip(ep['chapters'],rawdur)):
            base=RAW/f'{ep["id"]}-{i:02}'
            length=dur*scale+1.5
            ch.update(start=cursor,duration=length,end=cursor+length)
            wav=base.with_suffix('.wav')
            run(['ffmpeg','-y','-v','error','-i',str(base.with_suffix('.mp3')),'-af',f'atempo={1/scale:.9f},adelay=500:all=1,apad','-t',f'{length:.9f}','-ar','24000','-ac','1',str(wav)])
            chapterfiles.append(wav)
            words=json.loads(base.with_suffix('.json').read_text()); group=[]
            # Match normalized paragraph text into the aligned word stream. Paragraph
            # punctuation differs from TTS tokens, so match character positions.
            norm=lambda s: ''.join(re.findall(r'[a-z0-9]+',s.lower()))
            prefix=0; char_ends=[]
            for word in words:
                prefix+=len(norm(word['text'])); char_ends.append(prefix)
            import bisect
            starts=[]; prefix=0
            for para in ch['paragraphs']:
                wi=min(len(words)-1,bisect.bisect_right(char_ends,prefix))
                starts.append(cursor+.5+words[wi]['start']*scale)
                prefix+=len(norm(spoken(para)))
            ch['beat_starts']=starts
            for j,word in enumerate(words):
                group.append(word)
                if len(' '.join(w['text'] for w in group))>=67 or j==len(words)-1 or (word['text'].endswith(('.', '?','!')) and len(group)>=5):
                    subtitles.append(dict(start=cursor+.5+group[0]['start']*scale,end=min(cursor+.5+group[-1]['end']*scale,cursor+length-.5),text=' '.join(w['text'] for w in group)))
                    group=[]
            cursor+=length
        # Concatenate PCM without repeatedly re-encoding narration.
        with wave.open(str(ROOT/'media'/f'{ep["id"]}.wav'),'wb') as out:
            out.setparams((1,2,24000,0,'NONE','not compressed'))
            for p in chapterfiles:
                with wave.open(str(p),'rb') as inp: out.writeframes(inp.readframes(inp.getnframes()))
        ep['duration']=target
        ep['subtitles']=subtitles
        ep['voice']='en-US-AndrewNeural · synthetic narration'
        (ROOT/'captions'/f'{ep["id"]}.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{timestamp(s["start"])} --> {timestamp(s["end"])}\n{s["text"]}' for s in subtitles)+'\n')
        (ROOT/'captions'/f'{ep["id"]}.srt').write_text('\n\n'.join(f'{j+1}\n{timestamp(s["start"],True)} --> {timestamp(s["end"],True)}\n{s["text"]}' for j,s in enumerate(subtitles))+'\n')
        transcript=f'{ep["paper"]}\n{ep["authors"]}\n{ep["url"]}\nOriginal educational narration. Toy examples are not benchmark replications.\n\n'
        for ch in ep['chapters']:
            transcript+=f'{timestamp(ch["start"])} — {ch["title"]}\n{ch["narration"]}\nSource / scope: {ch["source"]}\n\n'
        (ROOT/'transcripts'/f'{ep["id"]}.txt').write_text(transcript)
        (ROOT/'media'/f'{ep["id"]}-chapters.ffmeta').write_text(';FFMETADATA1\n'+''.join(f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(ch["start"]*1000)}\nEND={round(ch["end"]*1000)}\ntitle={ch["title"]}\n' for ch in ep['chapters']))
        print('timeline',ep['id'],target,'seconds, voice scale',round(scale,3),flush=True)
    (ROOT/'content.json').write_text(json.dumps(EPISODES,ensure_ascii=False,indent=2))
    (ROOT/'content.js').write_text('window.EPISODES = '+json.dumps(EPISODES,ensure_ascii=False)+';\n')

if __name__=='__main__': asyncio.run(main())
