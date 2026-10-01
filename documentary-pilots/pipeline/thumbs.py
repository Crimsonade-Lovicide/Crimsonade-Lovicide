import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pilots import PILOTS
T = {'p1_pink_slime': ('FAKE LOCAL NEWS', 'NOW OUTNUMBERS REAL'),
     'p2_the_count': ('38%', 'OF ELECTION OFFICIALS', 'HARASSED OR THREATENED'),
     'p3_server_nation': ('THE DISCORD', 'PRIME MINISTER'),
     'p4_long_arm': ('54 GOVERNMENTS', 'HAVE TARGETED CRITICS ABROAD'),
     'p5_brokered': ('YOUR LOCATION', 'IS FOR SALE')}
W, H = 1280, 720
for pid, tx in T.items():
    a, b = tx[0], tx[1]; b2 = tx[2] if len(tx) > 2 else None
    p = PILOTS[pid]; acc = tuple(p['accent'])
    im = Image.open(f'hf/A{p["keyart"]}.png').convert('RGB')
    s = max(W / im.width, H / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    arr = np.asarray(im).astype(np.float32)
    grad = np.clip(np.linspace(1.0, -0.2, W), 0, 1)[None, :, None]
    arr = arr * (1 - 0.8 * grad) ; im = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(im)
    big = ImageFont.truetype('fonts/BebasNeue.ttf', 150 if len(a) <= 10 else 118)
    sub = ImageFont.truetype('fonts/BebasNeue.ttf', 66)
    tag = ImageFont.truetype('fonts/PlexMonoSemi.ttf', 26)
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for dd, img in ((sd, None), (d, None)):
        pass
    y = 200
    sd.text((64, y + 6), a, font=big, fill=(0, 0, 0, 230)); sd.text((68, y + 160), b, font=sub, fill=(0, 0, 0, 230))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(8))); d = ImageDraw.Draw(im)
    d.rectangle((48, y + 18, 58, y + (290 if b2 else 228)), fill=(*acc, 255))
    d.text((70, y), a, font=big, fill=(245, 245, 240))
    d.text((72, y + 156), b, font=sub, fill=(*acc, 255))
    if b2: d.text((72, y + 222), b2, font=sub, fill=(*acc, 255))
    d.text((72, 92), p['series'], font=tag, fill=(235, 235, 230))
    im.convert('RGB').save(f'out/thumb_{pid}.jpg', quality=92)
c = Image.new('RGB', (1280, 720 * 5 // 2 + 0))
c = Image.new('RGB', (640 * 2, 360 * 3), (0, 0, 0))
for i, pid in enumerate(T): c.paste(Image.open(f'out/thumb_{pid}.jpg').resize((640, 360)), ((i % 2) * 640, (i // 2) * 360))
c.save('out/thumbs_contact.jpg', quality=85)
