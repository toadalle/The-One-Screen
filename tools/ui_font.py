"""One Cascadia Code raster policy for custom UI; never mutates shared NPC fonts."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
FONT=Path(__file__).resolve().parents[1]/'assets/fonts/CascadiaCode-Regular.ttf'
def sprite(text,width,height):
    for size in range(height,3,-1):
        font=ImageFont.truetype(str(FONT),size)
        box=font.getbbox(text,stroke_width=1)
        if box[2]-box[0]<=width and box[3]-box[1]<=height:break
    else:raise ValueError('Text cannot fit without clipping: '+text)
    result=Image.new('RGBA',(width,height))
    ImageDraw.Draw(result).text(((width-(box[2]-box[0]))//2-box[0],(height-(box[3]-box[1]))//2-box[1]),text,font=font,fill=(255,255,255,255),stroke_width=1,stroke_fill=(0,0,0,255))
    return result
