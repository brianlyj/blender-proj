"""Combine rendered samples for motion and shoulder review."""
from pathlib import Path
from PIL import Image, ImageDraw
project=Path(__file__).resolve().parents[2]
for kind,frames in [('fluid-dance',[0,24,48,66,78,90,102,114,144,174,210,239]),('fluid-paws',[0,12,24,36,48,60,72,84,96,108,120,143])]:
    if not (project/'renders'/kind/('frame_%03d.png'%frames[-1])).exists():continue
    sheet=Image.new('RGB',(4*270,3*382),(22,27,35));draw=ImageDraw.Draw(sheet)
    for index,frame in enumerate(frames):
        im=Image.open(project/'renders'/kind/('frame_%03d.png'%frame)).convert('RGB').resize((270,360))
        x=(index%4)*270;y=(index//4)*382
        sheet.paste(im,(x,y));draw.text((x+8,y+363),'%.2f seconds'%(frame/24),fill='white')
    sheet.save(project/'deliverables/previews'/(kind+'-contact.jpg'),quality=90)
