"""Replace lettering inside native containers; never redraw button artwork."""
from pathlib import Path
from PIL import Image
import cv2
import numpy as np
import build_menu_top_atlas as codec
from ui_font import sprite

FILE_BUTTONS=[('Erase',(276,8,44,18)),('Copy',(160,30,48,20)),('Yes',(116,70,48,23)),('No',(123,117,35,23)),('Start',(52,211,61,26)),('Options',(178,207,62,19)),('Erase',(421,11,63,24)),('Cancel',(416,59,74,25)),('Overwrite',(404,108,98,24)),('Back',(5,130,43,16))]
NAME_BUTTONS=[('Back',(430,57,43,15)),('Yes',(396,183,51,23)),('No',(404,238,36,24)),('OK',(451,344,28,17)),('Cancel',(435,375,66,19))]

def button(atlas,text,rect):
    x,y,w,h=rect
    original=np.array(atlas)
    rgb=original[:,:,:3].copy()
    mask=np.zeros(rgb.shape[:2],np.uint8)
    region=rgb[y:y+h,x:x+w]
    selected=((region.min(axis=2)>=170)|(region.max(axis=2)<=85)).astype(np.uint8)*255
    selected=cv2.dilate(selected,np.ones((3,3),np.uint8),iterations=1)
    mask[y:y+h,x:x+w]=selected
    restored=cv2.inpaint(rgb,mask,3,cv2.INPAINT_TELEA)
    original[mask!=0,:3]=restored[mask!=0]
    result=Image.fromarray(original)
    result.alpha_composite(sprite(text,w,h),(x,y))
    atlas.paste(result.crop((x,y,x+w,y+h)),(x,y))

def build(retail,output,previews):
    for family in ('menu_file_select','name_entry00'):
        for variant in ('00','01'):
            name=f'{family}_parts{variant}.ctxb'
            base=(retail/name).read_bytes()
            codec.HEIGHT=512 if family=='name_entry00' else 256
            atlas=codec.decode_ctxb(base)
            for text,rect in FILE_BUTTONS if family=='menu_file_select' else NAME_BUTTONS:button(atlas,text,rect)
            # Preserve native keyboard keys until each text-only region is
            # recovered; the former guessed grid overwrote container artwork.
            target=output/name;target.parent.mkdir(parents=True,exist_ok=True)
            data=codec.encode_ctxb(base[:codec.HEADER_SIZE],atlas);target.write_bytes(data)
            if codec.encode_ctxb(base[:codec.HEADER_SIZE],codec.decode_ctxb(data))!=data:raise ValueError('Frontend CTXB roundtrip')
            previews.mkdir(parents=True,exist_ok=True);atlas.save(previews/(name+'.png'))
    codec.HEIGHT=256
