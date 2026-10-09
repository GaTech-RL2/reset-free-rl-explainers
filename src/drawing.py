"""Small deterministic drawing toolkit; fonts come from Matplotlib for portability."""
import math
from functools import lru_cache
from pathlib import Path
import matplotlib
from PIL import Image,ImageDraw,ImageFont
W,H=1600,900
BG='#0b1220'; PANEL='#121e30'; INK='#edf2fa'; MUTED='#9faec3'; LINE='#30425d'
CYAN='#67d9ef'; GREEN='#83e0b2'; PURPLE='#bea8ff'; GOLD='#f4cc78'; RED='#ffab91'; BLUE='#86c5ff'

def clamp(x,a=0,b=1):return max(a,min(b,x))
def lerp(a,b,p):return a+(b-a)*clamp(p)
def ease(p):p=clamp(p);return p*p*(3-2*p)
def pos(a,b,p):return lerp(a[0],b[0],p),lerp(a[1],b[1],p)
def blend(a,b,p):
    aa=tuple(int(a[i:i+2],16) for i in (1,3,5));bb=tuple(int(b[i:i+2],16) for i in (1,3,5))
    return tuple(round(lerp(x,y,p)) for x,y in zip(aa,bb))

@lru_cache(None)
def font(n,bold=False,mono=False):
    name='DejaVuSansMono' if mono else 'DejaVuSans'
    return ImageFont.truetype(str(Path(matplotlib.get_data_path())/'fonts/ttf'/f'{name}{"-Bold" if bold else ""}.ttf'),n)

class Canvas:
    def __init__(self,im):self.im=im;self.d=ImageDraw.Draw(im)
    def text(self,x,y,s,size=24,color=INK,bold=False,anchor=None,mono=False):
        self.d.text((round(x),round(y)),str(s),font=font(size,bold,mono),fill=color,anchor=anchor)
    def wrap(self,x,y,s,width,size=24,color=INK,bold=False,leading=1.35):
        lines=[];cur=''
        for word in str(s).split():
            test=(cur+' '+word).strip()
            if cur and self.d.textlength(test,font=font(size,bold))>width:lines.append(cur);cur=word
            else:cur=test
        if cur:lines.append(cur)
        for i,l in enumerate(lines):self.text(x,y+size*leading*i,l,size,color,bold)
        return len(lines)*size*leading
    def line(self,points,color=LINE,width=3,dash=False):
        if not dash:self.d.line(points,fill=color,width=width,joint='curve');return
        for a,b in zip(points,points[1:]):
            length=math.dist(a,b)
            for j in range(0,int(length),18):self.d.line([pos(a,b,j/max(length,1)),pos(a,b,min(1,(j+10)/max(length,1)))],fill=color,width=width)
    def arrow(self,a,b,color=CYAN,width=3):
        self.line([a,b],color,width);ang=math.atan2(b[1]-a[1],b[0]-a[0]);r=15
        self.d.polygon([b,(b[0]-r*math.cos(ang-.4),b[1]-r*math.sin(ang-.4)),(b[0]-r*math.cos(ang+.4),b[1]-r*math.sin(ang+.4))],fill=color)
    def box(self,x,y,w,h,label='',color=LINE,fill=PANEL,size=23):
        self.d.rounded_rectangle((x,y,x+w,y+h),radius=13,fill=fill,outline=color,width=2)
        if label:self.text(x+w/2,y+h/2,label,size,INK,anchor='mm')
    def circle(self,x,y,r,color=CYAN,fill=None,width=3):self.d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=color,width=width)
    def node(self,x,y,label,color=CYAN,r=35):
        self.circle(x,y,r,color,blend(BG,color,.12));self.text(x,y,label,22,color,True,'mm')
    def path(self,pts,p,color=CYAN,width=4):
        lengths=[math.dist(a,b) for a,b in zip(pts,pts[1:])];remain=sum(lengths)*clamp(p);end=pts[0]
        for i,d in enumerate(lengths):
            f=min(1,remain/max(1,d));end=pos(pts[i],pts[i+1],f);self.line([pts[i],end],color,width);remain-=d
            if remain<=0:break
        return end
    def axes(self,x=120,y=535,w=700,h=310,xlabel='',ylabel=''):
        for k in range(1,5):self.line([(x,y-k*h/4),(x+w,y-k*h/4)],'#1e2d44',1)
        self.arrow((x,y),(x+w+12,y),MUTED,2);self.arrow((x,y),(x,y-h-12),MUTED,2)
        self.text(x+w,y+23,xlabel,20,MUTED,anchor='ra');self.text(x,y-h-43,ylabel,20,MUTED)
    def curve(self,fn,x0=0,x1=1,ymax=1,color=CYAN,x=120,y=535,w=700,h=310,p=1):
        pts=[(x+w*i/200,y-h*clamp(fn(x0+(x1-x0)*i/200)/ymax,-.05,1.08)) for i in range(int(200*clamp(p))+1)]
        if len(pts)>1:self.line(pts,color,4)
        return pts[-1]

BASE=Image.new('RGB',(W,H),BG)
bd=ImageDraw.Draw(BASE)
for y in range(H):bd.line([(0,y),(W,y)],fill=blend('#111e30',BG,y/H))
for x in range(0,W,50):bd.line([(x,135),(x,635)],fill='#142136',width=1)
for y in range(135,635,50):bd.line([(45,y),(980,y)],fill='#142136',width=1)
