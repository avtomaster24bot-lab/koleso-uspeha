# -*- coding: utf-8 -*-
"""Продающие аудио-истории «Послушать» для сайта «Код счастливой жизни».

Тексты: _src/audio_texts.json (по программам) + _src/audio_entry.txt (вступление «С чего начать»).
Маршрут прослушивания (PATHS) и «Дальше послушать» (next) — только по аудио этого сайта.
Цены в аудио не называются; никаких гарантий результата. Голос — диктор, не Марина.
Озвучка: python3 _src/audio_build.py
"""
import json, os, re
_HERE = os.path.dirname(os.path.abspath(__file__))
TEXTS = json.load(open(os.path.join(_HERE, "audio_texts.json"), encoding="utf-8"))
START = "start"
PATHS = {
 "samozvanec": ("Самозванец и самоценность", ["mini-samozvanets", "trening-samozvanets-strah-razoblacheniya", "trening-samoocenka", "trening-samotsennost",
   "trening-perfekcionizm", "trening-koroli-prokrastinacii", "trening-proyavlyajsya-legko", "trening-moj-produkt-krutoj", "trening-stoimost-uslugi",
   "trening-kak-ozvuchivat-cenu", "modul-4", "modul-5", "koleso-uspeha"]),
 "dengi": ("Деньги", ["mini-finansovyj-strah", "trening-ya-vizhu-dengi", "trening-dengi-iz-detstva", "trening-finansovyj-potolok", "trening-moya-bogataya-zhizn",
   "trening-finansovyj-strah-osvobozhdenie", "modul-1", "koleso-uspeha"]),
 "strahi": ("Страхи и тормоза", ["mini-strah-uspeha", "mini-bazovyj-strah", "trening-strah-uspeha", "trening-bazovyj-strah", "modul-2", "koleso-uspeha"]),
 "otnosheniya": ("Отношения, контроль, конфликты", ["mini-kontrol", "mini-bez-menya", "mini-istoki-konfliktov", "mini-svyaz-v-konfliktah", "diagnostika",
   "trening-vsyo-pod-kontrolem", "trening-lider-a-ne-nyanka", "trening-ne-daj-soboj-manipulirovat", "trening-konflikty-v-rost", "trening-dejstvuj-kak",
   "modul-3", "individualno"]),
 "prednaznachenie": ("Цели и ресурс", ["marafon-samoprinyatie", "marafon-dvizhenie-k-celi", "trening-vsyo-nachinaetsya-s-mechty", "trening-istinnost-celi",
   "trening-fundament-starta", "trening-konkretnye-shagi", "modul-6", "klub", "koleso-uspeha"]),
 "lila": ("Игра «Лила»", ["lila", "individualno"]),
 "psy": ("Психологам и коучам", ["trening-stoimost-uslugi", "trening-kak-ozvuchivat-cenu", "psihologam"]),
}
ORDER = ["samozvanec", "dengi", "strahi", "otnosheniya", "prednaznachenie", "lila", "psy"]
PRIMARY = {"koleso-uspeha": "samozvanec", "individualno": "otnosheniya", "trening-stoimost-uslugi": "samozvanec", "trening-kak-ozvuchivat-cenu": "samozvanec"}
SIDE = {
 "mini-samozvanets": "trening-samozvanets-strah-razoblacheniya", "mini-strah-uspeha": "trening-strah-uspeha", "mini-finansovyj-strah": "trening-finansovyj-strah-osvobozhdenie",
 "mini-bazovyj-strah": "trening-bazovyj-strah", "mini-kontrol": "trening-vsyo-pod-kontrolem", "mini-bez-menya": "trening-lider-a-ne-nyanka",
 "mini-istoki-konfliktov": "trening-ne-daj-soboj-manipulirovat", "mini-svyaz-v-konfliktah": "trening-konflikty-v-rost",
 "modul-1": "modul-2", "modul-2": "modul-3", "modul-3": "modul-4", "modul-4": "modul-5", "modul-5": "modul-6", "modul-6": "koleso-uspeha",
 "koleso-uspeha": "diagnostika", "lila": "klub", "klub": "lila", "individualno": "diagnostika", "diagnostika": "individualno",
 "marafon-samoprinyatie": "klub", "marafon-dvizhenie-k-celi": "trening-istinnost-celi", "psihologam": "lila",
}
TITLE = {i: v["title"] for i, v in TEXTS.items()}
TITLE[START] = "С чего начать: что такое «Код счастливой жизни»"
DISCLAIMER = "Озвучено голосом диктора — а вживую с вами работает сама Марина."

def path_of(i):
    if i in PRIMARY: return PRIMARY[i]
    for k in ORDER:
        if i in PATHS[k][1]: return k

def next_of(i):
    if i == START: return [PATHS[k][1][0] for k in ORDER[:6]]
    lst = PATHS[path_of(i)][1]; k = lst.index(i)
    nx = [lst[k + 1]] if k + 1 < len(lst) else []
    s = SIDE.get(i)
    if s and s not in nx and s != i: nx.append(s)
    return (nx or ["diagnostika", "klub"])[:2]

def spoken(i):
    t = TITLE[i]; return "аудио: " + t[0].lower() + t[1:]

BTN = {"diagnostika": "«Записаться на диагностику»", "lila": "«Записаться и оплатить»", "psihologam": "«Обсудить с Мариной»", "individualno": "«Купить сессию»"}
def cta_line(i):
    b = BTN.get(i, "«Купить»")
    if i.startswith("mini-") or i == "diagnostika":
        return "Записаться можно кнопкой %s на этой странице: откроется сообщение Марине в Телеграме, и любые вопросы можно задать до оплаты." % b
    if i == "klub": return "Вступить в клуб можно кнопкой на этой странице — Марина пришлёт детали лично."
    if i == "psihologam": return "Чтобы обсудить свой проект, нажмите %s на этой странице — откроется сообщение Марине в Телеграме." % b
    return "Не уверены, что это ваш формат? Начните с личной диагностики — тридцать минут один на один с Мариной. Или сразу нажмите %s на этой странице и напишите Марине." % b

def tts(s):
    rep = [("1–1,5 часа", "час-полтора"), ("2–3 часа", "два-три часа"), ("1–2 часа", "один-два часа"), ("1 на 1", "один на один"),
           ("Т-игр", "трансформационных игр"), ("МАК-карт", "метафорических карт"), ("МАК", "метафорические карты"),
           ("т.д.", "так далее"), ("т.п.", "тому подобное"), ("—", " — "), ("…", "..."), ("+", " плюс ")]
    for a, b in rep: s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()

def compose(i):
    if i == START: return open(os.path.join(_HERE, "audio_entry.txt"), encoding="utf-8").read().strip()
    d = TEXTS[i]; nx = next_of(i)
    out = d["text"].strip() + "\n\n" + d.get("teaser", "").strip()
    out += "\n\nЕсли вы узнали себя — следующим послушайте %s." % spoken(nx[0])
    if len(nx) > 1: out += " А если хочется зайти с другой стороны — %s." % spoken(nx[1])
    return out + "\n\n" + cta_line(i) + "\n\n" + DISCLAIMER

def journey_order():
    seen, out = set(), [START]
    for k in ORDER:
        for i in PATHS[k][1]:
            if i not in seen: seen.add(i); out.append(i)
    return out

SCRIPTS = []
for i in journey_order():
    t = compose(i)
    SCRIPTS.append(dict(id=i, url="slushat/" if i == START else TEXTS[i]["url"], title=TITLE[i], kind="Старт" if i == START else TEXTS[i]["kind"],
                        path=path_of(i) or "start", next=next_of(i), text="\n\n".join(tts(p) for p in re.split(r"\n\s*\n", t) if p.strip())))
BY_ID = {x["id"]: x for x in SCRIPTS}
BY_URL = {x["url"]: x for x in SCRIPTS if x["id"] != START}
EXTRA_PAGES = {"": START, "slushat/": START}

if __name__ == "__main__":
    for x in SCRIPTS: print("%-42s %-45s %4d слов -> %s" % (x["id"], x["url"], len(x["text"].split()), ",".join(x["next"])))
    print(len(SCRIPTS))
