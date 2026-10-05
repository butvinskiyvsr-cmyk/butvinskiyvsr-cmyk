"""Generate the profile's own typography and vector artwork (Python + Pillow)."""
from pathlib import Path
from html import escape
from PIL import Image, ImageDraw, ImageFont
import os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
BG, PANEL, LINE = '#0D1117', '#161D27', '#2B3645'
WHITE, MUTED, BLUE, TEAL = '#F0F6FC', '#9DAFC2', '#58A6FF', '#39D0C8'

def font(size, bold=False, mono=False):
    name = ('DejaVuSansMono' if mono else 'DejaVuSans') + ('-Bold' if bold else '') + '.ttf'
    choices = [Path(os.environ.get('PROFILE_FONT_DIR', '/usr/share/fonts/truetype/dejavu')) / name,
               Path('/Library/Fonts') / name, Path('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf')]
    for p in choices:
        if p.is_file():
            return ImageFont.truetype(str(p), size)
    raise RuntimeError('Set PROFILE_FONT_DIR to a folder containing DejaVuSans TTF fonts.')

class Canvas:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.im = Image.new('RGB', (width, height), BG)
        self.d = ImageDraw.Draw(self.im)
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                    f'<rect width="{width}" height="{height}" fill="{BG}"/>']

    def rect(self, box, fill, radius=0, stroke=None):
        self.d.rounded_rectangle(box, radius=radius, fill=fill, outline=stroke, width=1)
        x,y,r,b=box
        self.svg.append(f'<rect x="{x}" y="{y}" width="{r-x}" height="{b-y}" rx="{radius}" fill="{fill}" stroke="{stroke or "none"}"/>')

    def line(self, points, color=LINE, width=2):
        self.d.line(points, fill=color, width=width)
        pts=' '.join(f'{x},{y}' for x,y in points)
        self.svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}"/>')

    def circle(self, x,y,r,fill,stroke=None):
        self.d.ellipse((x-r,y-r,x+r,y+r), fill=fill, outline=stroke, width=2)
        self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="2"/>')

    def text(self,x,y,value,size=24,color=WHITE,bold=False,mono=False):
        f=font(size,bold,mono)
        # Anchor text at its true top for consistent PNG and editable SVG.
        self.d.text((x,y),value,font=f,fill=color,anchor='lt')
        family='DejaVu Sans Mono' if mono else 'DejaVu Sans'
        self.svg.append(f'<text x="{x}" y="{y}" dominant-baseline="text-before-edge" font-family="{family},sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(value)}</text>')
        if x + self.d.textlength(value,font=f) > self.width-24:
            raise ValueError(f'Text overflows canvas: {value}')

    def save(self,name):
        self.im.save(OUT / f'{name}.png',optimize=True)
        (OUT / f'{name}.svg').write_text('\n'.join(self.svg+['</svg>']),encoding='utf-8')

def header():
    c=Canvas(1280,400)
    c.rect((1,1,1278,398),BG,20,LINE)
    c.rect((36,40,40,356),BLUE,2)
    c.text(68,46,'VLADISLAV / BUTVINSKY',20,TEAL,mono=True)
    c.text(66,100,'Владислав',52,bold=True)
    c.text(66,162,'Бутвинский',52,bold=True)
    c.text(68,242,'Ведущий разработчик 1С',28,WHITE)
    c.text(68,286,'Developer Tools / Desktop Applications',22,MUTED)
    c.text(68,342,'1C / BSL     Git / Gitea     .NET     Electron',18,BLUE,mono=True)
    # Abstract metadata / Git motif, rather than a made-up application screenshot.
    c.rect((865,42,1238,358),PANEL,16,LINE)
    c.text(895,70,'FROM PROCESS TO PRODUCT',16,MUTED,mono=True)
    c.line([(921,137),(921,302)],BLUE,3)
    for y,num,title,sub,col in [(137,'01','Enterprise','1C / Integrations',BLUE),
                              (216,'02','Developer tools','Git / Metadata',TEAL),
                              (295,'03','Desktop products','Interface / Delivery',BLUE)]:
        c.circle(921,y,9,PANEL,col)
        c.line([(932,y),(955,y)],col,2)
        c.text(971,y-16,title,22,WHITE,bold=True)
        c.text(971,y+14,sub,15,MUTED)
    c.save('header')

def icon(c,kind,col):
    x,y=1080,106
    if kind=='tree':
        c.line([(x,y-28),(x,y+48)],col,3)
        for yy,xx in [(y-24,x+53),(y+13,x+74),(y+48,x+45)]:
            c.line([(x,yy),(xx,yy)],col,3)
            c.rect((xx-9,yy-9,xx+9,yy+9),PANEL,3,col)
        c.circle(x,y-44,9,col)
    elif kind=='plan':
        for i,l in enumerate([77,45,66]):
            yy=y-27+i*38
            c.rect((x-3,yy,x+13,yy+16),PANEL,4,col)
            c.line([(x+27,yy+8),(x+27+l,yy+8)],col,4)
    elif kind=='branch':
        c.line([(x,y-38),(x,y+57)],col,3)
        c.line([(x,y+12),(x+60,y+12),(x+60,y-24)],col,3)
        for xx,yy in [(x,y-38),(x,y+57),(x+60,y-24)]:
            c.circle(xx,yy,9,PANEL,col)
    else:
        c.rect((x-6,y-36,x+51,y+49),PANEL,8,col)
        c.rect((x+12,y-25,x+69,y+60),PANEL,8,col)
        c.circle(x+40,y+11,12,PANEL,col)
        c.line([(x+23,y+43),(x+56,y+43)],col,2)

def card(name,index,title,category,subtitle,stack,kind,col=BLUE):
    c=Canvas(1280,240)
    c.rect((1,1,1278,238),PANEL,18,LINE)
    c.rect((36,32,40,208),col,2)
    c.text(64,30,f'{index} / {category}',16,col,mono=True)
    c.text(62,65,title,42,bold=True)
    c.text(64,122,subtitle,24,MUTED)
    c.line([(64,163),(994,163)],LINE,1)
    c.text(64,185,stack,18,WHITE,mono=True)
    c.line([(1030,40),(1030,200)],LINE,1)
    icon(c,kind,col)
    c.save(name)

if __name__ == '__main__':
    header()
    card('configscope','01','ConfigScope','DEVELOPER TOOL','История изменений 1С через объекты метаданных','C# / .NET 8 / WPF / Git / BSL','tree')
    card('ritm','02','RITM','PRODUCT / USER TESTING','Задачи, проекты и планирование','Electron / JavaScript / Node.js / PostgreSQL','plan',TEAL)
    card('hrangor','03','HranGor','DEVELOPER TOOL','История узлов метаданных и сверка выгрузки 1С','TypeScript / Electron / Git / Gitea / XML','branch')
    card('arkanov','04','Книга Арканов','DESKTOP PRODUCT','Персональная база знаний по 78 картам','Flutter / Dart / Windows','book',TEAL)
    print('Generated 5 PNGs and 5 editable SVGs.')
