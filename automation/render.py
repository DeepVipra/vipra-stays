"""Render Vipra Stays creatives from a calendar JSON. Usage: python3 render.py calendar.json outdir"""
import json, sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

LIB = "/home/claude/vs/lib"
F = "/home/claude/vs/fonts"
SERIF = f"{F}/pf-latin-600-normal.ttf"
SERIF_I = f"{F}/pf-latin-500-italic.ttf"
SANS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
SANS_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
GREEN = (30, 59, 42); CREAM = (245, 239, 227); GOLD = (214, 172, 84); TERRA = (180, 71, 47)
WA = "WhatsApp +91 85869 29882"

def font(p, s): return ImageFont.truetype(p, s)

def cover(im, w, h, ax=0.5, ay=0.5):
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = round((im.width - w) * ax); y = round((im.height - h) * ay)
    return im.crop((x, y, x + w, y + h))

def photo(name): return Image.open(f"{LIB}/{name}.jpg").convert("RGB")

def spaced(d, xy, text, f, fill, spacing=4):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + spacing
    return x

def spaced_w(d, text, f, spacing=4): return sum(d.textlength(c, font=f) + spacing for c in text) - spacing

def gradient(w, h, top_alpha, bot_alpha, color=GREEN):
    g = Image.new("L", (1, h))
    for y in range(h): g.putpixel((0, y), round(top_alpha + (bot_alpha - top_alpha) * (y / (h - 1)) ** 1.15))
    a = g.resize((w, h)); layer = Image.new("RGBA", (w, h), color + (0,)); layer.putalpha(a); return layer

def wordmark(d, x, y, scale=1.0, fill=CREAM):
    spaced(d, (x, y), "VIPRA STAYS", font(SANS, round(22 * scale)), fill, round(5 * scale))
    d.text((x, y + round(30 * scale)), "Greenwood Farm", font=font(SERIF_I, round(24 * scale)), fill=fill)

def fit_title(d, text, maxw, start):
    s = start
    while s > 40:
        f = font(SERIF, s)
        if all(d.textlength(l, font=f) <= maxw for l in text.split("\n")): return f
        s -= 4
    return font(SERIF, s)

def cover_slide(p, w=1080, h=1350, img_name=None):
    im = cover(photo(img_name or p["photos"][0]), w, h).convert("RGBA")
    gh = round(h * 0.62); im.alpha_composite(gradient(w, gh, 0, 245), (0, h - gh))
    im.alpha_composite(gradient(w, 220, 150, 0), (0, 0))
    d = ImageDraw.Draw(im)
    wordmark(d, 64, 56)
    title = p["title"]; tf = fit_title(d, title, w - 128, 96)
    lines = title.split("\n"); lh = round(tf.size * 1.16)
    y = h - 150 - lh * len(lines)
    spaced(d, (64, y - 56), p["eyebrow"], font(SANS, 24), GOLD, 4)
    for i, l in enumerate(lines): d.text((64, y + i * lh), l, font=tf, fill=CREAM)
    d.line((64, h - 104, w - 64, h - 104), fill=CREAM + (90,), width=1)
    d.text((64, h - 84), WA, font=font(SANS_M, 24), fill=CREAM)
    t = "45 mins from Gurgaon"; f2 = font(SANS_M, 24)
    d.text((w - 64 - d.textlength(t, font=f2), h - 84), t, font=f2, fill=CREAM)
    return im.convert("RGB")

def photo_slide(name, label, idx, total, w=1080, h=1350):
    im = Image.new("RGB", (w, h), CREAM)
    ph = cover(photo(name), w, 900); im.paste(ph, (0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 900, w, 908), fill=TERRA)
    lf = fit_title(d, label, w - 128, 64)
    d.text((64, 980), label, font=lf, fill=GREEN)
    spaced(d, (64, 1240), f"{idx:02d} / {total:02d}", font(SANS, 22), GREEN, 4)
    spaced(d, (w - 64 - spaced_w(d, "VIPRA STAYS", font(SANS, 22)), 1240), "VIPRA STAYS", font(SANS, 22), GREEN, 4)
    return im

def cta_slide(w=1080, h=1350, headline="Book your dates."):
    im = Image.new("RGB", (w, h), GREEN); d = ImageDraw.Draw(im)
    wordmark(d, 64, 72)
    d.text((64, 430), headline, font=font(SERIF, 92), fill=CREAM)
    rows = ["Stays for up to 10 guests", "Parties & events for up to 100", "45 mins from Gurgaon · Taoru Road"]
    for i, r in enumerate(rows):
        d.ellipse((66, 618 + i * 64, 80, 632 + i * 64), fill=GOLD)
        d.text((104, 606 + i * 64), r, font=font(SANS_M, 34), fill=CREAM)
    d.rounded_rectangle((64, 1010, w - 64, 1130), 60, fill=GOLD)
    t = WA; f = font(SANS, 40)
    d.text(((w - d.textlength(t, font=f)) / 2, 1046), t, font=f, fill=GREEN)
    t = "or tap the link in bio"; f = font(SANS_M, 28)
    d.text(((w - d.textlength(t, font=f)) / 2, 1170), t, font=f, fill=CREAM)
    return im

def render_reel(p, out):
    W, H, FPS, SEG, XF = 1080, 1920, 30, 3.0, 0.4
    names = p["photos"]; caps = p.get("captions_on_video") or [""] * len(names)
    plates = []
    for n in names:
        im = photo(n); r = H / im.height
        im = im.resize((round(im.width * r * 1.06), round(H * 1.06)), Image.LANCZOS); plates.append(im)
    ov_cache = {}
    def overlay(i, first):
        key = (i, first)
        if key in ov_cache: return ov_cache[key]
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        o.alpha_composite(gradient(W, 260, 150, 0), (0, 0))
        o.alpha_composite(gradient(W, 1250, 0, 250), (0, H - 1250))
        d = ImageDraw.Draw(o); wordmark(d, 64, 96, 1.2)
        if first:
            lines = p["title"].split("\n"); tf = fit_title(d, p["title"], W - 128, 110); lh = round(tf.size * 1.15)
            y = H - 520 - lh * len(lines)
            spaced(d, (64, y - 64), p["eyebrow"], font(SANS, 28), GOLD, 5)
            for k, l in enumerate(lines): d.text((64, y + k * lh), l, font=tf, fill=CREAM)
        cf = fit_title(d, caps[i], W - 128, 64) if caps[i] else None
        if cf: d.text((64, H - 420), caps[i], font=cf, fill=CREAM)
        d.text((64, H - 300), WA, font=font(SANS_M, 32), fill=CREAM)
        ov_cache[key] = o; return o
    def frame(i, t):  # t in [0,1]
        pl = plates[i]; maxx = pl.width - W; maxy = pl.height - H
        span = min(maxx, 700); x0 = (maxx - span) / 2
        x = round(x0 + span * t) if i % 2 == 0 else round(x0 + span * (1 - t))
        fr = pl.crop((x, maxy // 2, x + W, maxy // 2 + H)).convert("RGBA")
        fr.alpha_composite(overlay(i, i == 0 and t < 0.999)); return fr.convert("RGB")
    n_seg = round(SEG * FPS); nx = round(XF * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(len(plates)):
        for k in range(n_seg):
            t = k / (n_seg - 1); fr = frame(i, t)
            if i + 1 < len(plates) and k >= n_seg - nx:
                a = (k - (n_seg - nx) + 1) / (nx + 1); fr = Image.blend(fr, frame(i + 1, 0), a)
            pr.stdin.write(fr.tobytes())
    # end card 2s
    end = cta_slide(W, H, "Book your dates.")
    for _ in range(FPS * 2): pr.stdin.write(end.tobytes())
    pr.stdin.close(); pr.wait()
    cover_slide(p, W, H).save(out.replace(".mp4", "-cover.jpg"), quality=90)

def render(p, outdir):
    os.makedirs(outdir, exist_ok=True); base = f"{outdir}/{p['date']}"
    files = []
    if p["fmt"] == "single":
        cover_slide(p).save(f"{base}.jpg", quality=90); files = [f"{base}.jpg"]
    elif p["fmt"] == "carousel":
        n = len(p["photos"]) + 1
        cover_slide(p).save(f"{base}-1.jpg", quality=90); files.append(f"{base}-1.jpg")
        for i, (ph, lab) in enumerate(zip(p["photos"][1:], p["slide_labels"][1:]), start=2):
            photo_slide(ph, lab, i, n).save(f"{base}-{i}.jpg", quality=90); files.append(f"{base}-{i}.jpg")
        cta_slide().save(f"{base}-{n}.jpg", quality=90); files.append(f"{base}-{n}.jpg")
    elif p["fmt"] == "reel":
        render_reel(p, f"{base}.mp4"); files = [f"{base}.mp4", f"{base}-cover.jpg"]
    return [os.path.basename(f) for f in files]

if __name__ == "__main__":
    cal = json.load(open(sys.argv[1])); outdir = sys.argv[2]
    only = sys.argv[3] if len(sys.argv) > 3 else None
    for p in cal:
        if only and p["date"] != only: continue
        p["files"] = render(p, outdir); print(p["date"], p["fmt"], p["files"])
    if not only: json.dump(cal, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
