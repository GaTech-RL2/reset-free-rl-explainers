import concurrent.futures,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def verify(ep):
    path=ROOT/'media'/f'{ep["id"]}.mp4'
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(path)]))
    streams={s['codec_type']:s for s in probe['streams']}
    assert abs(float(probe['format']['duration'])-840)<.03
    assert streams['video']['width']==1600 and streams['video']['height']==900
    assert streams['video']['codec_name']=='h264' and streams['audio']['codec_name']=='aac'
    assert streams['subtitle']['codec_name']=='mov_text'
    assert len(probe['chapters'])==12
    for c in ep['chapters']:
        assert c['start']<=c['beat_starts'][0]<c['beat_starts'][1]<c['beat_starts'][2]<c['end']
    assert all(0<=s['start']<s['end']<=840 for s in ep['subtitles'])
    decoded=subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(path),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True)
    assert decoded.returncode==0 and not decoded.stderr,decoded.stderr
    volume=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-map','0:a:0','-af','volumedetect','-f','null','-'],capture_output=True,text=True)
    mean=float(re.search(r'mean_volume: ([-\d.]+)',volume.stderr)[1]);peak=float(re.search(r'max_volume: ([-\d.]+)',volume.stderr)[1])
    assert -40<mean<-5 and peak<=0,(mean,peak)
    # A representative decoded frame checks the encoded result, not just source PIL frames.
    subprocess.run(['ffmpeg','-y','-v','error','-ss','437','-i',str(path),'-frames:v','1',str(ROOT/'qa'/f'{ep["id"]}-encoded.jpg')],check=True)
    return dict(id=ep['id'],duration=float(probe['format']['duration']),width=1600,height=900,fps=streams['video']['r_frame_rate'],chapters=12,subtitles=len(ep['subtitles']),mean_audio_db=mean,peak_audio_db=peak,full_decode_passed=True,bytes=path.stat().st_size)

if __name__=='__main__':
    eps=json.loads((ROOT/'content.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(verify,eps))
    (ROOT/'qa/media-verification.json').write_text(json.dumps(results,indent=2))
    print('Six complete video/audio decodes passed; timings, chapters, subtitles, and narration levels verified.')
