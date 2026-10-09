"""Optional local preview server with HTTP Range support for chapter seeking."""
import argparse,functools,re
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer

class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.byte_range=None
        path=Path(self.translate_path(self.path))
        request=self.headers.get('Range')
        if not request or not path.is_file():return super().send_head()
        size=path.stat().st_size
        match=re.fullmatch(r'bytes=(\d*)-(\d*)',request.strip())
        if not match or not any(match.groups()):
            self.send_error(416,'Invalid range');return None
        a,b=match.groups()
        if a:
            start=int(a);end=min(int(b),size-1) if b else size-1
        else:
            start=max(0,size-int(b));end=size-1
        if start>end or start>=size:
            self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.send_header('Content-Length','0');self.end_headers();return None
        f=path.open('rb');f.seek(start);self.byte_range=(start,end)
        self.send_response(206)
        self.send_header('Content-Type',self.guess_type(str(path)))
        self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length',str(end-start+1))
        self.end_headers();return f
    def end_headers(self):
        self.send_header('Accept-Ranges','bytes')
        super().end_headers()
    def copyfile(self,source,outputfile):
        try:
            if self.byte_range:
                remaining=self.byte_range[1]-self.byte_range[0]+1
                while remaining:
                    block=source.read(min(256*1024,remaining))
                    if not block:break
                    outputfile.write(block);remaining-=len(block)
            else:super().copyfile(source,outputfile)
        except (BrokenPipeError,ConnectionResetError):pass

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8768);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),functools.partial(RangeHandler,directory=str(Path(__file__).parent)))
    print(f'Open http://127.0.0.1:{args.port}',flush=True)
    server.serve_forever()
