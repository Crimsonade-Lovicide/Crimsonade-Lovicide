import sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageChops
from rembg import remove, new_session
W,H=1280,720
sess=new_session("u2net_human_seg")

def cutout(path, warm=1.0):
    im=Image.open(path).convert("RGB")
    cut=remove(im,session=sess)  # RGBA
    bbox=cut.getbbox(); cut=cut.crop(bbox)
    if warm!=1.0:
        r,g,b,a=cut.split()
        r=r.point(lambda v:min(255,int(v*warm))); b=b.point(lambda v:int(v/warm))
        cut=Image.merge("RGBA",(r,g,b,a))
        cut=Image.merge("RGBA",(*ImageEnhance.Brightness(cut.convert("RGB")).enhance(1.12).split(),cut.split()[3]))
    return cut

def background(path, crop):
    bg=Image.open(path).convert("RGB")
    w,h=bg.size; x0,y0,x1,y1=[int(v) for v in (crop[0]*w,crop[1]*h,crop[2]*w,crop[3]*h)]
    bg=bg.crop((x0,y0,x1,y1)).resize((W,H),Image.LANCZOS)
    bg=ImageEnhance.Contrast(bg).enhance(1.18); bg=ImageEnhance.Color(bg).enhance(1.25)
    # darken toward the right (Hugo) and the top-left (text) a touch, plus a vignette
    shade=Image.new("L",(W,H),0); d=ImageDraw.Draw(shade)
    for x in range(W):
        v=int(max(0,(x-W*0.55)/(W*0.45))*110)
        d.line([(x,0),(x,H)],fill=v)
    vig=Image.new("L",(W,H),0); ImageDraw.Draw(vig).ellipse((-W*0.25,-H*0.35,W*1.25,H*1.35),fill=255)
    vig=vig.filter(ImageFilter.GaussianBlur(120))
    bg=Image.composite(bg,Image.new("RGB",(W,H),(0,0,0)),vig.point(lambda v:int(90+v*165/255)))
    bg=Image.composite(Image.new("RGB",(W,H),(0,0,0)),bg,shade)
    return bg

def text(img, lines, x, y, size, font="Anton-Regular.ttf"):
    d=ImageDraw.Draw(img); f=ImageFont.truetype(font,size)
    for txt,col in lines:
        # soft shadow, then hard stroke
        sh=Image.new("RGBA",img.size,(0,0,0,0)); ImageDraw.Draw(sh).text((x+6,y+8),txt,font=f,fill=(0,0,0,170))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
        d.text((x,y),txt,font=f,fill=col,stroke_width=7,stroke_fill=(0,0,0))
        y+=int(size*1.02)
    return img

def build(bgpath, crop, hugo, warm, lines, out, hugo_h=760, hugo_x=None, size=128):
    img=background(bgpath,crop).convert("RGBA")
    cut=cutout(hugo,warm)
    s=hugo_h/cut.height; cut=cut.resize((int(cut.width*s),hugo_h),Image.LANCZOS)
    x=hugo_x if hugo_x is not None else W-cut.width+int(cut.width*0.08)
    y=H-cut.height+int(hugo_h*0.06)
    glow=Image.new("RGBA",img.size,(0,0,0,0)); a=cut.split()[3].filter(ImageFilter.GaussianBlur(18))
    glow.paste(Image.new("RGBA",cut.size,(0,0,0,200)),(x-10,y+6),a); img.alpha_composite(glow)
    img.alpha_composite(cut,(x,y))
    img=text(img,lines,46,34,size)
    f=ImageFont.truetype("BebasNeue-Regular.ttf",40); d=ImageDraw.Draw(img)
    d.text((48,H-64),"UNBUILT",font=f,fill=(255,255,255),stroke_width=2,stroke_fill=(0,0,0))
    img.convert("RGB").save(out,quality=92)

hugoA="hugo_O2_4.7.png"
build("../ed/img/CO5.png",(0.02,0.0,0.84,1.0),hugoA,1.12,[("THEY ALMOST",(255,255,255)),("BUILT THIS",(255,212,0))],"thumb_A_dome.jpg")
build("../ed/img/A4.png",(0.0,0.0,0.9,1.0),hugoA,1.10,[("THEY TRIED TO",(255,255,255)),("DRAIN THE SEA",(255,212,0))],"thumb_B_sea.jpg",size=118)
print("done")
