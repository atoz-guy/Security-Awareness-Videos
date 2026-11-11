"""Render a 5-second PHP2Shell PSA clip for Facebook (4:5) and LinkedIn (1:1).

Usage: python make_snip.py
"""
import math
import random
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FPS = 30
DURATION = 5.0
FONTS = "C:/Windows/Fonts/"
IMPACT = FONTS + "impact.ttf"
BOLD = FONTS + "segoeuib.ttf"

BG = (10, 12, 18)
RED = (255, 45, 60)
WHITE = (245, 247, 250)
GREY = (150, 158, 172)
YELLOW = (255, 210, 40)

# (start, end) seconds for each scene
SCENES = [(0.0, 2.4), (2.4, 5.0)]


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def ease_out_back(t):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_out(t):
    return 1 - (1 - t) ** 3


def font_fit(path, text, max_w, start):
    size = start
    while size > 10:
        f = ImageFont.truetype(path, size)
        if f.getbbox(text)[2] <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(path, size)


def text_layer(size, text, font, fill, scale=1.0, alpha=1.0):
    """Render text centred on its own transparent layer, optionally scaled."""
    l, t, r, b = font.getbbox(text)
    w, h = r - l + 40, b - t + 40
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((20 - l, 20 - t), text, font=font, fill=fill + (int(255 * alpha),))
    if scale != 1.0:
        layer = layer.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    return layer


def paste_center(canvas, layer, cx, cy):
    canvas.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))


def glitch_text(canvas, text, font, cx, cy, intensity, scale=1.0, fill=WHITE):
    """RGB-split glitch: red/cyan offset copies under the main text."""
    off = int(intensity * 18)
    if off:
        paste_center(canvas, text_layer(canvas.size, text, font, (255, 0, 60), scale, 0.85), cx - off, cy)
        paste_center(canvas, text_layer(canvas.size, text, font, (0, 230, 255), scale, 0.85), cx + off, cy)
    paste_center(canvas, text_layer(canvas.size, text, font, fill, scale), cx, cy)


def warning_icon(draw, cx, cy, size, color):
    h = size * math.sqrt(3) / 2
    pts = [(cx, cy - h * 0.6), (cx - size / 2, cy + h * 0.4), (cx + size / 2, cy + h * 0.4)]
    draw.polygon(pts, fill=color)
    bar_w = size * 0.09
    draw.rounded_rectangle([cx - bar_w / 2, cy - h * 0.28, cx + bar_w / 2, cy + h * 0.12], radius=bar_w / 2, fill=BG)
    draw.ellipse([cx - bar_w * 0.6, cy + h * 0.19, cx + bar_w * 0.6, cy + h * 0.31], fill=BG)


def shield_icon(draw, cx, cy, size, color):
    w, h = size * 0.8, size
    pts = [(cx, cy - h / 2), (cx + w / 2, cy - h / 3), (cx + w / 2, cy), (cx, cy + h / 2),
           (cx - w / 2, cy), (cx - w / 2, cy - h / 3)]
    draw.polygon(pts, fill=color)
    s = size * 0.2
    draw.line([(cx - s, cy), (cx - s * 0.2, cy + s * 0.8), (cx + s * 1.1, cy - s * 0.7)], fill=BG, width=int(size * 0.1))


def background(W, H, t):
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    # drifting cyber grid
    step = 60
    shift = int(t * 40) % step
    for x in range(-step, W + step, step):
        d.line([(x + shift, 0), (x + shift, H)], fill=(22, 28, 40), width=1)
    for y in range(-step, H + step, step):
        d.line([(0, y + shift), (W, y + shift)], fill=(22, 28, 40), width=1)
    # red vignette glow that pulses
    pulse = 0.5 + 0.5 * math.sin(t * math.pi * 4)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-W * 0.3, H * 0.55, W * 1.3, H * 1.6], fill=(160, 0, 20, int(70 + 50 * pulse)))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    return img


def scene_local(t, idx):
    s, e = SCENES[idx]
    return (t - s) / (e - s), t - s


def render_frame(W, H, t):
    img = background(W, H, t)
    d = ImageDraw.Draw(img)
    cx = W / 2
    maxw = W * 0.86
    rnd = random.Random(int(t * FPS))

    # top alert bar (always on, blinks)
    bar_h = int(H * 0.075)
    blink = (int(t * 4) % 2 == 0) or t > 1.0
    d.rectangle([0, 0, W, bar_h], fill=RED if blink else (120, 10, 20))
    bf = ImageFont.truetype(BOLD, int(bar_h * 0.48))
    label = "SECURITY ALERT  •  QUICK CYBER UPDATE"
    bf = font_fit(BOLD, label, W * 0.9, int(bar_h * 0.48))
    lw = bf.getbbox(label)[2]
    d.text((cx - lw / 2, bar_h * 0.22), label, font=bf, fill=WHITE)

    if t < SCENES[0][1]:
        p, lt = scene_local(t, 0)
        warning_icon(d, cx, H * 0.24, W * 0.18 * ease_out_back(clamp(lt / 0.35)), YELLOW)
        f = font_fit(IMPACT, "PHP2SHELL", maxw, int(W * 0.24))
        sc = 2.2 - 1.2 * ease_out(clamp(lt / 0.25))
        jitter = 1.0 if lt < 0.4 else (0.6 if rnd.random() < 0.15 else 0)
        glitch_text(img, "PHP2SHELL", f, cx + rnd.randint(-6, 6) * jitter, H * 0.43, jitter, sc)
        sub = font_fit(BOLD, "Hackers can break into websites", maxw, int(W * 0.07))
        paste_center(img, text_layer(img.size, "Hackers can break into websites", sub, WHITE, 1, clamp((lt - 0.45) / 0.25)), cx, H * 0.58)
        # stamped red box
        sp = clamp((lt - 0.9) / 0.25)
        if sp > 0:
            fb = font_fit(IMPACT, "NO PASSWORD NEEDED", maxw * 0.9, int(W * 0.1))
            sc = 1.8 - 0.8 * ease_out_back(sp)
            lay = text_layer(img.size, "NO PASSWORD NEEDED", fb, WHITE, sc)
            box = Image.new("RGBA", (lay.width + 50, lay.height + 20), RED + (255,))
            box.alpha_composite(lay, (25, 10))
            box = box.rotate(-4, expand=True, resample=Image.BICUBIC)
            shake = rnd.randint(-8, 8) if sp < 1 else 0
            paste_center(img, box, cx + shake, H * 0.74 + shake)

    else:
        p, lt = scene_local(t, 1)
        a = clamp(lt / 0.25)
        shield_icon(d, cx, H * 0.27, W * 0.17 * ease_out_back(a), (40, 200, 120))
        f1 = font_fit(BOLD, "Ask your hosting provider:", maxw, int(W * 0.068))
        paste_center(img, text_layer(img.size, "Ask your hosting provider:", f1, GREY, 1, a), cx, H * 0.45)
        b = clamp((lt - 0.3) / 0.3)
        f2 = font_fit(IMPACT, "\u201cIS MY PHP PATCHED?\u201d", maxw, int(W * 0.12))
        paste_center(img, text_layer(img.size, "\u201cIS MY PHP PATCHED?\u201d", f2, WHITE, 1.3 - 0.3 * ease_out(b), b), cx, H * 0.58)
        c = clamp((lt - 0.9) / 0.3)
        f4 = font_fit(BOLD, "Read the full post below", maxw, int(W * 0.06))
        paste_center(img, text_layer(img.size, "Read the full post below \u2193", f4, YELLOW, 1, c), cx, H * 0.76)

    # short white flash at each scene cut
    for s, _ in SCENES[1:]:
        if 0 <= t - s < 0.08:
            flash = Image.new("RGBA", (W, H), (255, 255, 255, int(160 * (1 - (t - s) / 0.08))))
            img.alpha_composite(flash)

    # scanlines
    scan = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    for y in range(0, H, 4):
        sd.line([(0, y), (W, y)], fill=(0, 0, 0, 40))
    img.alpha_composite(scan)

    # progress bar
    d = ImageDraw.Draw(img)
    d.rectangle([0, H - 8, W * (t / DURATION), H], fill=RED)
    return img.convert("RGB")


def render(W, H, out):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
           "-c:a", "aac", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(FPS * DURATION)):
        frame = render_frame(W, H, i / FPS)
        proc.stdin.write(frame.tobytes())
        if i in (60, 145):
            frame.save(out.replace(".mp4", f"_preview_{i}.png"))
    proc.stdin.close()
    proc.wait()
    print("wrote", out)


if __name__ == "__main__":
    render(1080, 1350, "php2shell_facebook_4x5.mp4")
    render(1080, 1080, "php2shell_linkedin_1x1.mp4")
