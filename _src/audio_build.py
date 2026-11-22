# -*- coding: utf-8 -*-
"""Озвучка аудио-объяснений: python3 _src/audio_build.py [--force] [--only id1,id2]

Голос: edge-tts ru-RU-SvetlanaNeural (бесплатный нейроголос, женский). Это голос диктора,
не голос Марины. Чтобы заменить на запись Марины — положите assets/audio/<id>.mp3 и
добавьте id в assets/audio/own_voice.txt: такие файлы скрипт не перезаписывает.
Пересобираются только файлы, у которых изменился текст (хеш в manifest.json).
"""
import asyncio, hashlib, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_scripts import SCRIPTS

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")
VOICE = os.getenv("TTS_VOICE", "ru-RU-SvetlanaNeural")
RATE = os.getenv("TTS_RATE", "+6%")
PITCH = os.getenv("TTS_PITCH", "+4Hz")
MAN = os.path.join(OUT, "manifest.json")

def dur(fp):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", fp]).strip())

def chunks(text, n=700):
    import re
    parts, cur = [], ""
    for snt in re.split(r"(?<=[.!?»…])\s+", text):
        if cur and len(cur) + len(snt) > n: parts.append(cur); cur = snt
        else: cur = (cur + " " + snt).strip()
    if cur: parts.append(cur)
    return parts

PAUSE = float(os.getenv("TTS_PAUSE", "0.55"))     # пауза между абзацами, сек
MUSIC = os.getenv("AUDIO_MUSIC", "1") != "0"      # тихий собственный эмбиент под голосом

async def tts_piece(c, f):
    import edge_tts
    for k in range(8):   # сервис периодически отвечает «No audio received» — повторяем кусок
        try:
            await asyncio.wait_for(edge_tts.Communicate(c, VOICE, rate=RATE, pitch=PITCH).save(f), timeout=float(os.getenv("TTS_TIMEOUT", "30")))
            if os.path.getsize(f) < 1500: raise RuntimeError("empty chunk")
            return
        except Exception as ex:
            print("  chunk retry", k, type(ex).__name__, flush=True)
            if k == 7: raise
            await asyncio.sleep(2 + 2 * k)

def pad_wav(seconds, out, seed):
    import random
    rnd = random.Random(seed)
    ch = rnd.choice([[220.0, 261.63, 329.63, 392.0], [196.0, 246.94, 293.66, 369.99], [174.61, 220.0, 261.63, 329.63], [207.65, 261.63, 311.13, 392.0]])
    expr = "+".join("0.22*sin(2*PI*%.2f*t)*(0.6+0.4*sin(2*PI*%.3f*t))" % (f, 0.05 + 0.03 * i) for i, f in enumerate(ch))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "aevalsrc='%s':s=24000:d=%.2f" % (expr, seconds + 1),
                    "-af", "lowpass=f=1200,aecho=0.8:0.7:120|260:0.3|0.2,afade=t=in:d=3,afade=t=out:st=%.2f:d=4" % max(0, seconds - 4), "-ac", "1", out], check=True)

async def synth(text, out, seed="x"):
    """Абзацы → отдельные куски речи + паузы между абзацами → (опц.) тихий фон → mp3 моно 48 кбит/с."""
    import re, tempfile, wave
    d = tempfile.mkdtemp(); wavs = []
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    k = 0
    for pi, para in enumerate(paras):
        for c in chunks(para):
            f = os.path.join(d, "%03d.mp3" % k); k += 1
            await tts_piece(c, f)
            w = f[:-4] + ".wav"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f, "-af", "apad=pad_dur=%.2f" % (PAUSE if pi < len(paras) - 1 else 0.8), "-ar", "24000", "-ac", "1", w], check=True)
            wavs.append(w)
    voice = os.path.join(d, "voice.wav")
    with wave.open(voice, "wb") as o:
        for i, w in enumerate(wavs):
            with wave.open(w) as r:
                if i == 0: o.setparams(r.getparams())
                o.writeframes(r.readframes(r.getnframes()))
    if MUSIC:
        pad = os.path.join(d, "pad.wav"); pad_wav(dur(voice), pad, seed)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", voice, "-i", pad, "-filter_complex",
                        "[1:a]volume=0.07[m];[0:a][m]amix=inputs=2:duration=first:normalize=0", "-ac", "1", "-ar", "24000", "-c:a", "libmp3lame", "-b:a", "48k", out], check=True)
    else:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", voice, "-ac", "1", "-ar", "24000", "-c:a", "libmp3lame", "-b:a", "48k", out], check=True)

async def one(x, sem, man, force):
    import edge_tts
    fp = os.path.join(OUT, x["id"] + ".mp3")
    h = hashlib.sha1(("v2" + VOICE + RATE + PITCH + str(MUSIC) + str(PAUSE) + x["text"]).encode()).hexdigest()[:12]
    if not force and os.path.exists(fp) and man.get(x["id"], {}).get("hash") == h: return
    async with sem:
        for attempt in range(6):
            try:
                tmp = fp + ".tmp.mp3"
                await synth(x["text"], tmp, x["id"])
                # моно 24 кГц ~48 кбит/с — родной формат edge-tts; добавляем теги без перекодирования
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-c", "copy", "-metadata", "title=" + x["title"],
                                "-metadata", "artist=Код счастливой жизни · Марина Степанова (голос диктора)", "-metadata", "album=Код счастливой жизни: послушать", fp], check=True)
                os.remove(tmp)
                man[x["id"]] = dict(hash=h, duration=round(dur(fp), 1), bytes=os.path.getsize(fp), voice=VOICE)
                json.dump(man, open(MAN, "w"), ensure_ascii=False, indent=1)  # сохраняем по ходу
                print("ok", x["id"], man[x["id"]]["duration"], flush=True); return
            except Exception as ex:
                print("retry", x["id"], ex, flush=True); await asyncio.sleep(3 * (attempt + 1))
        raise RuntimeError("TTS failed: " + x["id"])

async def main():
    os.makedirs(OUT, exist_ok=True)
    force = "--force" in sys.argv
    only = None
    if "--only" in sys.argv: only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    man = json.load(open(MAN)) if os.path.exists(MAN) else {}
    own = set()
    ov = os.path.join(OUT, "own_voice.txt")
    if os.path.exists(ov): own = {l.strip() for l in open(ov) if l.strip() and not l.startswith("#")}
    sem = asyncio.Semaphore(int(os.getenv("TTS_PAR", "3")))
    todo = [x for x in SCRIPTS if x["id"] not in own and (only is None or x["id"] in only) and ("--new-only" not in sys.argv or x.get("new"))]
    await asyncio.gather(*(one(x, sem, man, force) for x in todo))
    for i in own:
        fp = os.path.join(OUT, i + ".mp3")
        if os.path.exists(fp): man[i] = dict(hash="own", duration=round(dur(fp), 1), bytes=os.path.getsize(fp), voice="own")
    ids = {x["id"] for x in SCRIPTS}
    man = {k: v for k, v in sorted(man.items()) if k in ids}
    json.dump(man, open(MAN, "w"), ensure_ascii=False, indent=1)
    print(len(man), "files,", round(sum(v["bytes"] for v in man.values()) / 1e6, 1), "MB,", round(sum(v["duration"] for v in man.values()) / 60, 1), "min")

asyncio.run(main())
