"""Draw the original editorial share card. Run with py; requires Pillow."""
from pathlib import Path
from math import sqrt
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[1]
S = 2
im = Image.new('RGB', (1200*S,630*S), '#f4f1e8')
d = ImageDraw.Draw(im)
def text(x,y,value,name,size,color='#243b2b'):
    font=ImageFont.truetype('C:/Windows/Fonts/'+name+'.ttf', size*S)
    d.text((x*S,y*S),value,font=font,fill=color)
def line(points,color,width=1):
    d.line([(int(x*S),int(y*S)) for x,y in points],fill=color,width=width*S)
text(52,30,'✳', 'seguisym', 36, '#bd562c')
text(99,34,'abundance.', 'segoeuib', 29)
line([(52,94),(1148,94)],'#d5d8c9')
text(56,125,'AN OPEN INQUIRY INTO A WORLD OF ENOUGH','consola',13,'#626859')
text(51,169,'We have','georgia',80)
text(51,255,'more than','georgia',80)
text(51,345,'enough.','georgiai',91,'#bd562c')
text(56,482,'Resources. People. The distance between them.','segoeui',19,'#626859')
cx,cy,r=900,321,172
d.ellipse(((cx-r-34)*S,(cy-r-34)*S,(cx+r+34)*S,(cy+r+34)*S),outline='#d5d8c9',width=S)
for y in range(-r*S,r*S+1):
    dx=int(sqrt(max(0,(r*S)**2-y*y)))
    t=(y+r*S)/(2*r*S)
    col=tuple(round(a+(b-a)*t) for a,b in zip((242,174,93),(181,80,42)))
    d.line((cx*S-dx,cy*S+y,cx*S+dx,cy*S+y),fill=col,width=1)
for y in range(-r+2,r,5):
    dx=sqrt(r*r-y*y)
    line([(cx-dx,cy+y),(cx+dx,cy+y)],'#b97440')
d.ellipse(((cx-235)*S,(cy-61)*S,(cx+235)*S,(cy+61)*S),outline='#53634c',width=2*S)
d.ellipse(((cx-221)*S,(cy+25)*S,(cx-207)*S,(cy+39)*S),fill='#243b2b')
text(805,535,'ONE PLANET. ALL OF US.','consola',14,'#626859')
line([(52,580),(1148,580)],'#d5d8c9')
text(56,595,'OPEN DATA  /  LINKED SOURCES  /  PUBLIC DOMAIN','consola',12,'#626859')
im=im.resize((1200,630),Image.Resampling.LANCZOS)
out=ROOT/'og-editorial.png'
im.save(out,optimize=True)
print(f'Wrote {out.name}: {out.stat().st_size} bytes')
