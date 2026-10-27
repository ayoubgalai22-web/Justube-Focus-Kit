#!/usr/bin/env python3
"""
Justube — مونتاج فيديو "سر اختفاء العملات الورقية في المستقبل"

يركّب: صور مولّدة + تعليق صوتي + حركة Ken Burns + عناوين/أرقام ASS (RTL)
+ موسيقى خلفية مولّدة + ضربات انتقال.
المتطلبات: ffmpeg (عبر imageio-ffmpeg) + Python القياسي فقط.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.dirname(ROOT)
AUDIO = os.path.join(VIDEO, "audio")
ASSETS = os.path.join(VIDEO, "assets")
BUILD = os.path.join(VIDEO, "build")
WORK = os.path.join(VIDEO, "render", "work")
OUT = os.path.join(VIDEO, "render")
FONT_DIR = os.path.join(BUILD, "fonts")

FF = subprocess.check_output(
    ["python3", "-c", "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"],
    text=True,
).strip()

FPS = 30
W, H = 1920, 1080
GAP = 0.45          # صمت بين الفصول

NAVY = "0x0B1220"
MINT = "&H00A0E500"     # ASS = BGR
WHITE = "&H00FFFFFF"
CREAM = "&H00D5E8F2"
GREY = "&H00C0B0A7"

SEGMENTS = [
    {
        "id": "S1_hook", "audio": "vo_01_hook.mp3", "chapter": None,
        "shots": [
            {"img": "img_01_hook.jpg", "dur": 18.0, "motion": "in", "ov": [
                (0.6, 6.5, "Big", "ما نقبل كاش"),
                (7.0, 12.5, "Cap", "قانون: يوليو 2026 — بقالات وصيدليات"),
            ]},
            {"img": "img_05_india.jpg", "dur": 16.1, "motion": "out", "ov": [
                (0.8, 6.5, "Cap", "الهند: رقم قياسي نقدي + أكبر شبكة مدفوعات فورية"),
                (7.2, 15.5, "Big", "مين؟ ليش؟ 2030؟"),
            ]},
        ],
    },
    {
        "id": "S2_cost", "audio": "vo_03_costs.mp3", "chapter": "الفصل 1 — لماذا يختفي؟",
        "shots": [
            {"img": "img_03_cost.jpg", "dur": 58.34, "motion": "in", "ov": [
                (1.0, 6.5, "Title", "ثلاث قوى — بلا مؤامرة"),
                (9.5, 15.5, "Big", "الكلفة"),
                (22.0, 29.0, "Cap", "طبع، نقل، حراسة، عدّ، فكة، صرافات"),
                (34.0, 42.0, "Cap", "12 من كل 100 شركة لا تقبل الكاش — منطقة اليورو"),
                (45.0, 54.0, "Cap", "القبول يقل ← الاستخدام يقل ← القبول يقل أكثر"),
            ]},
        ],
    },
    {
        "id": "S3_trade_data", "audio": "vo_04_data.mp3", "chapter": None,
        "shots": [
            {"img": "img_08_data.jpg", "dur": 69.17, "motion": "panlr", "ov": [
                (1.0, 6.5, "Big", "التجارة تغيّرت"),
                (13.0, 21.0, "Cap", "1 من كل 5 مدفوعات صار أونلاين (اليورو 2024)"),
                (30.0, 36.0, "Big", "البيانات"),
                (40.0, 49.0, "Cap", "مين، متى، وين، على وش، وبكم"),
                (53.0, 63.0, "Cap", "الكاش: آخر مكان في حياتك لا يُقاس"),
            ]},
        ],
    },
    {
        "id": "S4_who_pays", "audio": "vo_05_who_pays.mp3", "chapter": "الفصل 2 — من يدفع الثمن؟",
        "shots": [
            {"img": "img_04_people.jpg", "dur": 60.0, "motion": "in", "ov": [
                (1.0, 7.0, "Title", "من يدفع الثمن؟"),
                (18.0, 27.0, "Big", "1.3 مليار"),
                (27.0, 34.0, "Cap", "بالغ بلا حساب بنكي — و900 مليون منهم عندهم جوال"),
                (38.0, 46.0, "Cap", "الكاش: 52 من كل 100 عملية شراء في اليورو (2024)"),
            ]},
            {"img": "img_05_india.jpg", "dur": 46.25, "motion": "out", "ov": [
                (2.0, 10.0, "Cap", "التاجر الصغير: كلفة + وقت تسوية + خطر انقطاع"),
                (13.0, 20.0, "Cap", "الخصوصية: بالتصميم، لا بالسياسة"),
                (24.0, 32.0, "Cap", "المرونة: السويد، أستراليا، نيويورك — قوانين قبول الكاش"),
                (35.0, 45.0, "Cap", "الكاش: لا يحتاج إذنًا، ولا شبكة، ولا شاحن"),
            ]},
        ],
    },
    {
        "id": "S5_statement", "audio": None, "dur": 14.0, "chapter": "المفارقة",
        "shots": [
            {"img": "img_09_bank.jpg", "dur": 14.0, "motion": "in", "dark": 0.5, "ov": [
                (0.4, 4.6, "Title", "241 مليار عملية رقمية"),
                (4.7, 9.0, "Title", "176 مليار ورقة نقدية"),
                (9.2, 13.8, "Big", "الكاش لا يختفي… يغيّر وظيفته"),
            ]},
        ],
    },
    {
        "id": "S6_future", "audio": "vo_07_future.mp3", "chapter": "الفصل 3 — 2030",
        "shots": [
            {"img": "img_06_future.jpg", "dur": 45.0, "motion": "in", "ov": [
                (1.0, 7.0, "Title", "2030 — 3 سيناريوهات"),
                (10.0, 18.0, "Cap", "يورو رقمي: 2029 محتمل ومشروط — تجربة 2027"),
                (22.0, 31.0, "Cap", "بدون فوائد + سقف حيازة دُرِس بين 500 و3,000"),
                (34.0, 43.0, "Big", "ثلاث طبقات"),
            ]},
            {"img": "img_09_bank.jpg", "dur": 46.46, "motion": "out", "dark": 0.18, "ov": [
                (2.0, 10.0, "Cap", "عملات مستقرة ≈ 305 مليار دولار — 99% بالدولار"),
                (11.0, 19.0, "Cap", "مدفوعاتها في 9 أشهر من 2026: 482 مليار دولار"),
                (24.0, 33.0, "Cap", "النقد كخط دفاع: كهرباء، اتصالات، سيبراني"),
                (36.0, 45.0, "Title", "رقمي دايم… وكاش لما يطفي النور"),
            ]},
        ],
    },
    {
        "id": "S7_outro", "audio": "vo_08_outro.mp3", "chapter": None,
        "shots": [
            {"img": "img_07_safe.jpg", "dur": 38.0, "motion": "in", "ov": [
                (1.0, 7.0, "Title", "3 خطوات"),
                (9.0, 17.0, "Cap", "مبلغ صغير كاش — قدّ ما يكفيك أسبوع"),
                (19.0, 28.0, "Cap", "لا تعتمد على وسيلة دفع وحدة"),
                (30.0, 37.0, "Cap", "الكاش يختفي من يومك… ويكبر في الخزنة"),
            ]},
            {"img": None, "dur": 31.98, "motion": "none", "ov": [
                (1.2, 9.0, "Big", "لو انقطع النت 72 ساعة…"),
                (9.3, 17.0, "Big", "كم كاش في بيتك؟"),
                (18.0, 25.0, "Cap", "اكتب: بلدك + آخر مرة دفعت كاش + المبلغ"),
                (25.6, 31.5, "Cap", "اشترك وفعّل الجرس — الفيديو الجاي: مين يقرر كم تسوى فلوسك؟"),
            ]},
        ],
    },
]

ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Big,Tajawal,124,{MINT},{MINT},&H00120B00,&H00000000,0,0,0,0,100,100,0,0,1,5,4,5,120,120,90,1
Style: Title,Tajawal,88,{WHITE},{WHITE},&H00120B00,&H00000000,0,0,0,0,100,100,0,0,1,4,3,5,120,120,110,1
Style: Cap,Tajawal,52,{CREAM},{CREAM},&H00120B00,&H66000000,0,0,0,0,100,100,0,0,4,2,0,2,120,120,104,1
Style: Badge,Tajawal,36,{MINT},{MINT},&H00120B00,&H00000000,0,0,0,0,100,100,0,0,1,3,2,9,80,80,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ts(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def write_ass(path, overlays, dur, chapter=None):
    lines = [ASS_HEADER]
    if chapter:
        lines.append(f"Dialogue: 1,{ts(0.0)},{ts(dur)},Badge,,0,0,0,,{chapter}")
    for (a, b, style, text) in overlays:
        b = min(b, dur)
        if b > a:
            lines.append(f"Dialogue: 2,{ts(a)},{ts(b)},{style},,0,0,0,,{text}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def probe(path):
    err = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    if not m:
        raise SystemExit(f"cannot probe {path}")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write("FFMPEG FAILED:\n" + " ".join(cmd)[:1500] + "\n" + p.stderr[-3000:])
        raise SystemExit(1)
    return p


def resolve_timeline():
    """يضبط مدة اللقطة الأخيرة في كل مقطع لتساوي مدة الصوت بالضبط."""
    t = 0.0
    for seg in SEGMENTS:
        if seg.get("audio"):
            d = probe(os.path.join(AUDIO, seg["audio"]))
            seg["dur"] = d
            diff = d - sum(s["dur"] for s in seg["shots"][:-1])
            seg["shots"][-1]["dur"] = round(diff, 3)
        # الفاصل الزمني بين الفصول يُضاف لآخر لقطة حتى تتزامن الصورة مع الصوت
        seg["shots"][-1]["dur"] = round(seg["shots"][-1]["dur"] + GAP, 3)
        seg["start"] = round(t, 3)
        t += seg["dur"]
    return round(t, 3)


def render_shot(shot, index, chapter_is_first, chapter, out_path, dur_override=None):
    dur = dur_override or shot["dur"]
    frames = max(1, int(round(dur * FPS)))
    ass_path = os.path.join(WORK, f"shot_{index:02d}.ass")
    write_ass(ass_path, shot["ov"], dur, chapter if chapter_is_first else None)

    if shot["img"]:
        n = max(1, frames - 1)
        if shot["motion"] == "in":
            z, x, y = f"1+0.11*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
        elif shot["motion"] == "out":
            z, x, y = f"1.12-0.12*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
        else:
            z, x, y = "1.16", f"(iw-iw/zoom)*on/{n}", "ih/2-(ih/zoom/2)"
        chain = (
            f"scale=2496:-2:flags=lanczos,"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},"
            f"eq=contrast=1.06:saturation=1.05:gamma=0.99,vignette=PI/5"
        )
        if shot.get("dark"):
            chain += f",drawbox=x=0:y=0:w=iw:h=ih:color=black@{shot['dark']}:t=fill"
        chain += f",ass={ass_path}:fontsdir={FONT_DIR}"
        inputs = ["-loop", "1", "-t", f"{dur:.3f}", "-i", os.path.join(ASSETS, shot["img"])]
        vf = ["-vf", chain]
    else:
        inputs = ["-f", "lavfi", "-i", f"color=c={NAVY}:s={W}x{H}:d={dur:.3f}:r={FPS}"]
        vf = ["-vf", f"ass={ass_path}:fontsdir={FONT_DIR}"]

    run([FF, "-hide_banner", "-loglevel", "error", "-y"] + inputs + vf + [
        "-t", f"{dur:.3f}", "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-g", "60", "-an", out_path,
    ])


def main():
    for d in (WORK, OUT, FONT_DIR):
        os.makedirs(d, exist_ok=True)

    total = resolve_timeline()
    print(f"TOTAL VIDEO: {total:.2f}s = {int(total//60)}:{int(total%60):02d}")

    # 1) لقطات
    idx, clips = 0, []
    for seg in SEGMENTS:
        for j, shot in enumerate(seg["shots"]):
            out = os.path.join(WORK, f"clip_{idx:02d}.mp4")
            render_shot(shot, idx, j == 0, seg.get("chapter"), out)
            clips.append(out)
            print(f"  ✔ shot {idx:02d} ({shot['dur']:.2f}s) {shot['img'] or 'card'}")
            idx += 1

    # 2) دمج
    lst = os.path.join(WORK, "clips.txt")
    with open(lst, "w") as f:
        f.write("".join(f"file '{c}'\n" for c in clips))
    video_only = os.path.join(WORK, "video_only.mp4")
    run([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", video_only])

    # 3) الصوت: قاعدة صامتة + كل VO في موضعه + بيد + ضربات
    total_s = total
    inputs, filt, vo_labels = [], [], []
    filt.append(f"anullsrc=r=44100:cl=stereo,atrim=0:{total_s:.2f}[base]")
    n = 0
    for seg in SEGMENTS:
        if not seg.get("audio"):
            continue
        inputs += ["-i", os.path.join(AUDIO, seg["audio"])]
        ms = int(round(seg["start"] * 1000))
        filt.append(
            f"[{n}:a]aresample=44100,aformat=channel_layouts=stereo,"
            f"adelay={ms}|{ms},apad,atrim=0:{total_s:.2f}[v{n}]"
        )
        vo_labels.append(f"[v{n}]")
        n += 1
    filt.append(f"[base]{''.join(vo_labels)}amix=inputs={n+1}:normalize=0[vo]")

    filt.append(
        "aevalsrc='0.032*sin(2*PI*55*t)+0.017*sin(2*PI*82.41*t)*(0.6+0.4*sin(2*PI*0.07*t))"
        "+0.009*sin(2*PI*164.81*t)':s=44100[bedraw]"
    )
    filt.append(f"[bedraw]aformat=channel_layouts=stereo,lowpass=f=520,volume=0.9,atrim=0:{total_s:.2f}[bed]")

    boom_parts = []
    for seg in SEGMENTS:
        if seg.get("chapter"):
            bt = seg["start"]
            boom_parts.append(
                f"0.45*sin(2*PI*(75*exp(-9*max(0,t-{bt:.2f}))+40)*(t-{bt:.2f}))*exp(-7*max(0,t-{bt:.2f}))*gte(t,{bt:.2f})"
            )
    if boom_parts:
        filt.append(f"aevalsrc='{'+'.join(boom_parts)}':s=44100:d={total_s:.2f}[braw]")
        filt.append("[braw]aformat=channel_layouts=stereo,lowpass=f=220,volume=0.8[booms]")
        filt.append("[vo][bed][booms]amix=inputs=3:weights=1 0.5 0.9:normalize=0,"
                    "loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.96[aout]")
    else:
        filt.append("[vo][bed]amix=inputs=2:weights=1 0.5:normalize=0,"
                    "loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.96[aout]")

    mix = os.path.join(WORK, "mix.m4a")
    run([FF, "-hide_banner", "-loglevel", "error", "-y"] + inputs + [
        "-filter_complex", ";".join(filt), "-map", "[aout]",
        "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2", mix])

    # 4) النهائي
    final = os.path.join(OUT, "cashless-future.mp4")
    run([FF, "-hide_banner", "-loglevel", "error", "-y",
         "-i", video_only, "-i", mix, "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
         "-shortest", "-movflags", "+faststart", final])
    print(f"FINAL: {final}  {os.path.getsize(final)/1e6:.1f} MB  {total_s:.0f}s")


if __name__ == "__main__":
    main()
