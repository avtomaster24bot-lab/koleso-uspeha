# -*- coding: utf-8 -*-
"""Генератор статического сайта «Код счастливой жизни». Запуск из корня репозитория: python3 _src/gen.py"""
import os, html, json
from data import TOPICS, FORMATS, MODULES, T, MINIS
from reviews import R, HOME

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # корень сайта (папка над _src)
SITE = "https://avtomaster24bot-lab.github.io/koleso-uspeha/"
BRAND = "Код счастливой жизни"
MARINA_TG = "https://t.me/MarinaNew"
HOSTS = "Марина Степанова"
e = html.escape
TOPIC = dict(TOPICS); FORMAT = dict(FORMATS)
MOD = {m["n"]: m for m in MODULES}
MINI = {m["slug"]: m for m in MINIS}
PAIR_MINI = {m["pair"]: m for m in MINIS}
PAGES = []

def murl(m): return "modul/%s/" % m["slug"]
def turl(slug): return "trening/%s/" % slug
def miniurl(slug): return "mini/%s/" % slug

def nav(root, active):
    items = [("", "Главная", "home"), ("katalog/", "Все тренинги", "cat"), ("koleso-uspeha/", "Программа", "prog"),
             ("dlya-psihologov/", "Психологам", "psy"), ("vedushchie/", "Ведущая", "hosts"), ("otzyvy/", "Отзывы", "rev"), ("faq/", "Вопросы", "faq")]
    return "".join('<a href="%s%s"%s>%s</a>' % (root, u, ' class="on"' if k == active else "", t) for u, t, k in items)

from urllib.parse import quote as _q
PROG_VARIANT = {"koleso-full": "полная программа (6 месяцев, 24 тренинга)",
                "koleso-part1": "Часть 1 «Внутренняя опора» (модули 1–3, 3 месяца)",
                "koleso-part2": "Часть 2 «Проявленность и масштаб» (модули 4–6, 3 месяца)"}
TAIL = "Подскажите, как оплатить и ближайшую дату."
def msg_for(code, title):
    """(head, tail, with_price) — текст сообщения Марине под конкретный продукт."""
    hi = "Здравствуйте, Марина! "
    if code in PROG_VARIANT:
        return hi + "Хочу купить программу «Колесо успеха» — вариант: %s." % PROG_VARIANT[code], TAIL, True
    if code.startswith("modul-"):
        m = MOD[int(code.split("-")[1])]
        return hi + "Хочу купить модуль %d «%s» программы «Колесо успеха» (1 месяц, 4 тренинга)." % (m["n"], m["title"]), TAIL, True
    if code.startswith("trening-"):
        t = T[code[8:]]
        mod = (" (модуль «%s»)" % MOD[t["module"]]["title"]) if t["module"] else ""
        return hi + "Хочу купить тренинг «%s»%s." % (t["title"], mod), TAIL, True
    if code.startswith("mini-"):
        return hi + "Хочу купить мини-тренинг «%s» (1–1,5 часа, онлайн)." % MINI[code[5:]]["title"], TAIL, True
    if code == "marafon-samoprinyatie":
        return hi + "Хочу участвовать в марафоне «Самопринятие» (5 недель).", TAIL + "", True
    if code == "marafon-dvizhenie":
        return hi + "ХОЧУ В ДВИЖЕНИЕ — участвовать в марафоне «Движение к цели» (14 дней).", "Подскажите, как оплатить и когда старт.", True
    if code == "igra-lila":
        return hi + "Хочу записаться на игру «Лила» (4 часа, онлайн).", TAIL, True
    if code == "arhitektor-produkta":
        return hi + "Хочу обсудить наставничество «Архитектор продукта» для своего проекта.", "Расскажите, пожалуйста, как проходит работа и как оплатить.", True
    if code == "psy-obuchenie":
        return hi + "Хочу встать в лист ожидания на обучение ведению Т-игр и групп с МАК.", "Сообщите, пожалуйста, когда откроется набор.", False
    if code == "klub":
        return hi + "Хочу вступить в клуб «ЗАДОЛБАЛО!».", "Пришлите, пожалуйста, ссылку для входа.", False
    if code == "podbor":
        return hi + "Хочу подобрать тренинг под свой запрос.", "Подскажите, с чего лучше начать и ближайшие даты.", False
    if code == "vopros":
        return hi + "У меня вопрос о тренингах.", "", False
    return hi + "Хочу купить: «%s»." % title, TAIL, True

def tg_link(text): return MARINA_TG + "?text=" + _q(text, safe="")

def cta(code, group, title, label="Купить", cls="btn"):
    head, tail, wp = msg_for(code, title)
    static = (head + " " + tail).strip()
    return ('<a href="%s" class="%s" target="_blank" rel="noopener" data-cta="%s" data-group="%s" data-title="%s" data-head="%s" data-tail="%s"%s>%s</a>'
            % (e(tg_link(static), quote=True), cls, code, group, e(title, quote=True), e(head, quote=True), e(tail, quote=True), "" if wp else " data-noprice", label))

def price_span(code, group): return '<span data-price="%s" data-group="%s">Цена уточняется</span>' % (code, group)
def date_span(code, group): return '<span data-date="%s" data-group="%s">Дата уточняется</span>' % (code, group)

def ticks(items, q=False):
    return '<ul class="ticks%s">%s</ul>' % (" q" if q else "", "".join("<li>%s</li>" % e(i) for i in items))

def rev_html(key, label=None, limit=None):
    out = []
    for txt, sig in R.get(key, [])[:limit]:
        out.append('<blockquote class="rev"><p>%s</p><cite>%s</cite></blockquote>' % (e(txt), e(sig or label or "Участница")))
    return "".join(out)

MODAL = '''<div class="toast" id="toast" role="status" aria-live="polite"></div>
<div class="modal" id="cta-modal" role="dialog" aria-modal="true" aria-labelledby="m-t"><div class="mbox">
<button class="mclose" type="button" aria-label="Закрыть">×</button>
<span class="kicker">Запись</span><h3 id="m-t" data-m-title></h3>
<p class="small muted" style="margin:0">Стоимость: <b data-m-price></b> · Ближайшая дата: <b data-m-date></b></p>
<p class="small" style="margin-top:14px" data-m-paynote>Напишите нам — пришлём детали для оплаты.</p>
<p class="small muted" style="margin:0">Текст сообщения Марине (подставится в Telegram и скопируется):</p>
<div class="codebox" data-m-msg></div>
<a class="btn" data-m-tg href="https://t.me/MarinaNew" target="_blank" rel="noopener">Купить — написать Марине в Telegram</a>
<a class="btn ghost hidden" data-m-pay target="_blank" rel="noopener">Оплатить онлайн</a>
<button class="btn ghost" data-m-copy type="button">Скопировать текст</button>
<p class="ok"></p>
<p class="small muted">Все тренинги проходят онлайн и только вживую — в группе с ведущей.</p>
</div></div>'''

def layout(path, title, desc, body, active="", mcta=None, ogtitle=None, jsonld=None):
    depth = path.count("/")
    root = "../" * depth
    url = SITE + path
    full_title = title if BRAND in title else "%s — %s" % (title, BRAND)
    ld = ('<script type="application/ld+json">%s</script>' % json.dumps(jsonld, ensure_ascii=False)) if jsonld else ""
    m = ('<div class="mcta">%s</div>' % mcta) if mcta else ""
    doc = f'''<!doctype html>
<html lang="ru"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc, quote=True)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{e(ogtitle or title, quote=True)}"><meta property="og:description" content="{e(desc, quote=True)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}assets/og.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#fbf6ef">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Manrope:wght@400;600;700;800&display=swap&subset=cyrillic" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/style.css?v=4">{ld}
</head><body>
<header class="top"><div class="wrap">
<a class="logo" href="{root}"><span class="logo-mark" aria-hidden="true"></span>{BRAND}</a>
<button class="burger" aria-label="Меню" aria-expanded="false">☰</button>
<nav class="nav">{nav(root, active)}</nav>
</div></header>
<main>{body}</main>
<footer class="foot"><div class="wrap"><div class="cols">
<div><h4>{BRAND}</h4><p>Трансформационные тренинги, мини-тренинги и Т-игры. Онлайн, в живой группе.<br>Ведущая: {HOSTS}.</p></div>
<div><h4>Тренинги</h4><ul><li><a href="{root}katalog/">Все тренинги</a></li><li><a href="{root}koleso-uspeha/">Программа «Колесо успеха»</a></li><li><a href="{root}katalog/?format=mini">Мини-тренинги</a></li><li><a href="{root}igra/lila/">Игра «Лила»</a></li></ul></div>
<div><h4>Ещё</h4><ul><li><a href="{root}dlya-psihologov/">Для психологов и коучей</a></li><li><a href="{root}klub/">Клуб «ЗАДОЛБАЛО!»</a></li><li><a href="{root}otzyvy/">Отзывы</a></li><li><a href="{root}faq/">Вопросы и ответы</a></li></ul></div>
<div><h4>Связаться</h4><ul><li><a href="https://t.me/MarinaNew" data-link="marinaTelegram" target="_blank" rel="noopener">Марина Степанова — Telegram @MarinaNew</a></li><li><a class="hidden" data-link="whatsapp" data-hide-empty target="_blank" rel="noopener">WhatsApp</a></li><li><a class="hidden" data-link="channelUrl" data-hide-empty target="_blank" rel="noopener">Telegram-канал</a></li><li><a class="hidden" data-link="vkUrl" data-hide-empty target="_blank" rel="noopener">ВКонтакте</a></li><li><a class="hidden" data-link="youtubeUrl" data-hide-empty target="_blank" rel="noopener">YouTube</a></li></ul></div>
</div><p class="small" style="margin-top:28px;opacity:.7">Тренинги — это групповая трансформационная работа и не заменяют медицинскую или психиатрическую помощь.</p></div></footer>
{m}
{MODAL}
<script src="{root}assets/config.js?v=4"></script><script src="{root}assets/app.js?v=4"></script>
</body></html>'''
    fp = os.path.join(OUT, path, "index.html") if not path.endswith(".html") else os.path.join(OUT, path)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(doc)
    PAGES.append((path, title))

def crumbs(root, items):
    parts = ['<a href="%s">Главная</a>' % root] + [('<a href="%s%s">%s</a>' % (root, u, e(t)) if u else e(t)) for u, t in items]
    return '<div class="crumbs">%s</div>' % " / ".join(parts)

HOW = ticks([
 "Онлайн-встреча в живой группе с ведущей — Мариной Степановой.",
 "Работа с метафорическими ассоциативными картами (МАК), точными вопросами и практиками.",
 "Можно отвечать голосом или писать в чат — как вам комфортнее.",
 "В конце — конкретные шаги на ближайшие 24 часа и на неделю."])

def card(href, tag, tagcls, title, text, topics, fmt, code, group, root, extra=""):
    return ('<a class="card" href="%s%s" data-topics="%s" data-format="%s"><span class="tag %s">%s</span><h3>%s</h3><p class="muted">%s</p>%s'
            '<div class="price">%s</div><span class="more">Подробнее →</span></a>') % (
        root, href, " ".join(topics), fmt, tagcls, e(tag), e(title), e(text), extra, price_span(code, group))

def all_cards(root):
    out = []
    out.append(card("koleso-uspeha/", "Флагманская программа", "prog", "Колесо успеха: 6 месяцев", "6 модулей × 1 месяц, 24 трансформационных тренинга. Полностью, частями по 3 месяца или по модулям.", [t for t, _ in TOPICS], "programma", "koleso-full", "", root))
    for m in MINIS:
        out.append(card(miniurl(m["slug"]), "Мини-тренинг · 1–1,5 ч", "mini", m["title"], m["hook"], m["topics"], "mini", "mini-" + m["slug"], "mini", root))
    for m in MODULES:
        out.append(card(murl(m), "Модуль %d · 1 месяц" % m["n"], "mod", m["title"], "Цель: %s. 4 тренинга." % m["goal"], m["topics"], "modul", "modul-%d" % m["n"], "module", root))
    for m in MODULES:
        for s in m["trainings"]:
            t = T[s]
            out.append(card(turl(s), "Тренинг · модуль %d" % m["n"], "tt", t["title"], t["short"], t["topics"], "trening", "trening-" + s, "training", root))
    out.append(card(turl("samotsennost"), "Тренинг · 3–3,5 ч", "tt", T["samotsennost"]["title"], "Баланс между помощью другим и ценностью себя.", ["samoocenka"], "trening", "trening-samotsennost", "training", root))
    out.append(card("marafon/samoprinyatie/", "Марафон · 5 недель", "mar", "Марафон «Самопринятие»", "5 недель мягкой трансформации в поддерживающем кругу.", ["samoocenka"], "marafon", "marafon-samoprinyatie", "", root))
    out.append(card("marafon/dvizhenie-k-celi/", "Марафон · 14 дней", "mar", "Марафон «Движение к цели»", "8 шагов и 14 дней, чтобы двинуться с мёртвой точки.", ["celi"], "marafon", "marafon-dvizhenie", "", root))
    out.append(card("igra/lila/", "Т-игра · 4 часа", "game", "Игра «Лила» — авторская версия", "Найти самую важную точку развития и скрытые сценарии.", ["celi", "strahi", "dengi"], "igra", "igra-lila", "", root))
    return "".join(out)

def buybox(code, group, title, rows, label="Купить — написать Марине"):
    dl = "".join("<dt>%s</dt><dd>%s</dd>" % (k, v) for k, v in rows)
    return ('<aside class="buy"><div class="small muted">Стоимость</div><div class="p">%s</div><dl><dt>Старт</dt><dd>%s</dd>%s</dl>%s'
            '<p class="small muted" style="margin:12px 0 0">Нажмите — откроется окно записи с готовым сообщением Марине.</p></aside>') % (
        price_span(code, group), date_span(code, group), dl, cta(code, group, title, label) + '<a class="btn ghost hidden" style="width:100%%;margin-top:10px" data-pay="%s" target="_blank" rel="noopener">Оплатить онлайн</a>' % code)

# ------------------------------------------------------------------ HOME
def home():
    root = ""
    road = "".join('<a class="m%d" href="%s"><span class="n">Модуль %d</span><b>%s</b><span>Цель: %s</span></a>' % (m["n"], murl(m), m["n"], e(m["title"].split(":")[0]), e(m["goal"])) for m in MODULES)
    pains = [("Деньги не растут, хотя стараюсь", miniurl("finansovyj-strah")), ("Боюсь, что «раскроют», что я не так хорош", miniurl("samozvanets")),
             ("Почти дохожу до цели — и срываюсь", miniurl("strah-uspeha")), ("Фоновая тревога", miniurl("bazovyj-strah")),
             ("Всё контролирую сам(а)", miniurl("kontrol")), ("Тащу всё на себе", miniurl("bez-menya")),
             ("Одни и те же конфликты", miniurl("istoki-konfliktov")), ("Меня не слышат", miniurl("svyaz-v-konfliktah")),
             ("Стесняюсь назвать цену", turl("kak-ozvuchivat-cenu")), ("Откладываю важное", turl("koroli-prokrastinacii")),
             ("Перфекционизм тормозит", turl("perfekcionizm")), ("Не знаю, моя ли это цель", turl("istinnost-celi"))]
    pains_html = "".join('<a href="%s">%s</a>' % (u, e(t)) for t, u in pains)
    revs = "".join('<blockquote class="rev"><p>%s</p><cite>%s</cite></blockquote>' % (e(R[k][i][0]), e(R[k][i][1] or "Участница тренинга")) for k, i in HOME)
    minis = "".join(card(miniurl(m["slug"]), "Мини-тренинг · 1–1,5 ч", "mini", m["title"], m["hook"], m["topics"], "mini", "mini-" + m["slug"], "mini", root) for m in MINIS[:4])
    body = f'''
<section class="hero"><div class="wrap">
<span class="kicker">Онлайн · живые группы · авторские тренинги</span>
<h1>Код счастливой жизни: убери внутренние тормоза — и деньги, цели и отношения сдвинутся</h1>
<p class="lead">Трансформационные тренинги, мини-тренинги и Т-игры для предпринимателей, экспертов, руководителей и всех, кто хочет большего. Ведущие — {HOSTS}.</p>
<div class="btns"><a class="btn" href="katalog/">Подобрать тренинг</a><a class="btn ghost" href="koleso-uspeha/">Программа на 6 месяцев</a></div>
<div class="meta"><span class="chip c1">Деньги</span><span class="chip c2">Страхи</span><span class="chip c3">Контроль и лидерство</span><span class="chip c1">Конфликты</span><span class="chip c2">Проявленность</span><span class="chip c4">Цели</span></div>
</div></section>

<section class="section"><div class="wrap">
<div class="grid g2">
<div class="card aud a1"><span class="kicker">Для себя и своего дела</span><h2>Хочу изменений в своей жизни и бизнесе</h2>
<ul><li>Деньги и финансовый потолок</li><li>Страх успеха, синдром самозванца, тревога</li><li>Контроль, делегирование, лидерство</li><li>Конфликты, манипуляции, отношения</li><li>Проявленность, цена, продажи</li><li>Мечты, цели и конкретные шаги</li></ul>
<div class="btns"><a class="btn" href="katalog/">Смотреть тренинги</a><a class="btn ghost" href="#pain">Что у меня болит?</a></div></div>
<div class="card aud a2"><span class="kicker">Для психологов и коучей</span><h2>Я специалист и хочу расти в профессии</h2>
<ul><li>Наставничество «Архитектор продукта»: создать свою трансформационную игру или программу</li><li>Личная проработка: самозванец, цена своей услуги, «спасательство»</li><li>Увидеть формат Т-игры и групповой работы с МАК изнутри</li></ul>
<div class="btns"><a class="btn" href="dlya-psihologov/">Раздел для специалистов</a></div></div>
</div></div></section>

<section class="section alt" id="pain"><div class="wrap center">
<span class="kicker">Быстрый выбор</span><h2>Что откликается прямо сейчас?</h2>
<p class="lead">Нажмите на то, что про вас, — откроется тренинг именно на эту тему.</p>
<div class="pains" style="margin-top:22px">{pains_html}</div>
</div></section>

<section class="section"><div class="wrap">
<span class="kicker">Как выстроен путь</span><h2>Начните с малого — идите так глубоко, как готовы</h2>
<div class="ladder" style="margin-top:22px">
<div class="step"><span class="s">1</span><h3>Мини-тренинг</h3><p class="muted">1–1,5 часа онлайн. Диагностика: увидеть, что именно тормозит.</p><a href="katalog/?format=mini">Мини-тренинги →</a></div>
<div class="step"><span class="s">2</span><h3>Трансформационный тренинг</h3><p class="muted">Глубокая работа с одной темой и план действий на 24 часа и неделю.</p><a href="katalog/?format=trening">Тренинги →</a></div>
<div class="step"><span class="s">3</span><h3>Модуль на месяц</h3><p class="muted">4 тренинга по одной сфере: деньги, страхи, лидерство, проявленность, ритм, цели.</p><a href="katalog/?format=modul">Модули →</a></div>
<div class="step"><span class="s">4</span><h3>Программа «Колесо успеха»</h3><p class="muted">6 модулей за 6 месяцев — или две части по 3 месяца.</p><a href="koleso-uspeha/">Программа →</a></div>
</div></div></section>

<section class="section alt"><div class="wrap">
<span class="kicker">Флагманская программа</span><h2>6 модулей «Колеса успеха»</h2>
<p class="lead">Каждый модуль — месяц и 4 трансформационных тренинга. Можно пройти один модуль или всё колесо целиком.</p>
<div class="road" style="margin-top:22px">{road}</div>
<div class="btns"><a class="btn" href="koleso-uspeha/">Подробнее о программе и форматах участия</a></div>
</div></section>

<section class="section"><div class="wrap">
<span class="kicker">Попробовать формат</span><h2>Мини-тренинги: 1–1,5 часа онлайн</h2>
<div class="grid g4" style="margin-top:22px">{minis}</div>
<div class="btns"><a class="btn ghost" href="katalog/?format=mini">Все мини-тренинги</a></div>
</div></section>

<section class="section alt"><div class="wrap two">
<div><span class="kicker">Как проходит тренинг</span><h2>Живая работа, а не лекция в записи</h2>{HOW}</div>
<div><span class="kicker">Ведущая</span><h2>Марина Степанова</h2>
<div class="host" style="margin:16px 0"><div class="ph" data-photo="marina">МС</div><div><h3>Марина Степанова</h3><p>Автор и ведущая Т-игр и тренингов, предприниматель с опытом 9 лет.</p></div></div>
<div class="btns"><a class="btn ghost" href="vedushchie/">О ведущей</a></div></div>
</div></section>

<section class="section"><div class="wrap">
<span class="kicker">Отзывы участников</span><h2>Что меняется после тренингов</h2>
<div class="revs" style="margin-top:22px">{revs}</div>
<div class="btns"><a class="btn ghost" href="otzyvy/">Все отзывы</a></div>
</div></section>

<section class="section"><div class="wrap"><div class="band">
<h2>Не знаете, с чего начать?</h2><p>Напишите нам — подскажем тренинг под ваш запрос и ближайшую дату.</p>
<div class="btns" style="justify-content:center">{cta("podbor","","Подбор тренинга","Подобрать тренинг","btn light")}<a class="btn ghost" style="color:#fff;box-shadow:inset 0 0 0 2px #fff" href="faq/">Частые вопросы</a></div>
</div></div></section>'''
    layout("", "Код счастливой жизни — трансформационные тренинги Марины Степановой",
           "Онлайн-тренинги, мини-тренинги и Т-игры: деньги, страхи, контроль, конфликты, проявленность и цели. Программа «Колесо успеха» — 6 модулей. Живые группы.",
           body, "home", mcta=cta("podbor", "", "Подбор тренинга", "Подобрать тренинг"))

# ------------------------------------------------------------------ CATALOG
def catalog():
    root = "../"
    tb = '<button data-filter="topic" data-value="all">Все темы</button>' + "".join('<button data-filter="topic" data-value="%s">%s</button>' % (k, v) for k, v in TOPICS)
    fb = '<button data-filter="format" data-value="all">Все форматы</button>' + "".join('<button data-filter="format" data-value="%s">%s</button>' % (k, v) for k, v in FORMATS)
    body = f'''<section class="hero"><div class="wrap">{crumbs(root, [(None, "Все тренинги")])}
<span class="kicker">Каталог</span><h1>Все тренинги, игры и программы</h1>
<p class="lead">Выберите тему и формат. Всё проходит онлайн, вживую, в группе с ведущей.</p></div></section>
<section class="section" style="padding-top:0"><div class="wrap">
<div class="flabel">Тема</div><div class="filters">{tb}</div>
<div class="flabel">Формат</div><div class="filters">{fb}</div>
<div class="grid g3" id="catalog" style="margin-top:22px">{all_cards(root)}</div>
<p id="empty" class="hidden muted">По этому сочетанию пока ничего нет — выберите другую тему или формат.</p>
</div></section>'''
    layout("katalog/", "Каталог тренингов", "Все тренинги Марины Степановой: мини-тренинги, трансформационные тренинги, модули, марафоны, Т-игры. Фильтр по темам.", body, "cat",
           mcta=cta("podbor", "", "Подбор тренинга", "Помогите выбрать"))

# ------------------------------------------------------------------ MINI
def mini_page(m):
    root = "../../"
    pair = T[m["pair"]]
    mod = MOD[pair["module"]]
    code = "mini-" + m["slug"]
    revs = rev_html(code, "Участница мини-тренинга «%s»" % m["title"])
    rev_label = "Отзывы участников"
    if not revs:
        revs = rev_html(m["pair"], "Участница тренинга «%s»" % pair["title"], 3)
        rev_label = "Отзывы о полном тренинге «%s»" % pair["title"]
    body = f'''<section class="hero"><div class="wrap">{crumbs(root, [("katalog/?format=mini", "Мини-тренинги"), (None, m["title"])])}
<span class="kicker">Мини-тренинг · 1–1,5 часа · онлайн</span><h1>{e(m["title"])}</h1>
<p class="lead">{e(m["hook"])}</p><p class="muted">{e(m["aud"])}.</p>
<div class="btns">{cta(code, "mini", m["title"])}<a class="btn ghost" href="#detail">Подробнее</a></div></div></section>
<section class="section" id="detail" style="padding-top:10px"><div class="wrap layout"><div>
<div class="panel"><h2>Это для тебя, если:</h2>{ticks(m["foryou"], True)}</div>
<div class="panel" style="margin-top:20px"><h2>На мини-тренинге ты:</h2>{ticks(m["res"])}</div>
<div class="panel" style="margin-top:20px"><h2>Как проходит</h2>{HOW}</div>
</div>{buybox(code, "mini", m["title"], [("Формат", "онлайн, живая группа"), ("Длительность", "1–1,5 часа")])}</div></section>
<section class="section alt"><div class="wrap"><h2>{e(rev_label)}</h2><div class="revs" style="margin-top:18px">{revs}</div></div></section>
<section class="section"><div class="wrap"><span class="kicker">Следующий шаг</span><h2>Хотите не только увидеть, но и изменить?</h2>
<p class="lead">Мини-тренинг — это диагностика. Глубокая трансформация этой темы — в полном тренинге и модуле.</p>
<div class="grid g3" style="margin-top:20px">
{card(turl(m["pair"]), "Трансформационный тренинг", "tt", pair["title"], pair["short"], pair["topics"], "trening", "trening-" + m["pair"], "training", root)}
{card(murl(mod), "Модуль %d · 1 месяц" % mod["n"], "mod", mod["title"], "4 тренинга. Цель: %s." % mod["goal"], mod["topics"], "modul", "modul-%d" % mod["n"], "module", root)}
{card("koleso-uspeha/", "Программа", "prog", "Колесо успеха", "6 модулей, 24 тренинга — полностью или частями.", [], "programma", "koleso-full", "", root)}
</div></div></section>'''
    layout(miniurl(m["slug"]), m["title"] + " — мини-тренинг", "%s Мини-тренинг 1–1,5 часа онлайн. Ведущая — %s." % (m["hook"], HOSTS), body, "cat",
           mcta=cta(code, "mini", m["title"]))

# ------------------------------------------------------------------ TRAINING
def training_page(s):
    root = "../../"
    t = T[s]; code = "trening-" + s
    if t["module"]:
        mod = MOD[t["module"]]
        kick = "Трансформационный тренинг · модуль %d «%s»" % (mod["n"], mod["title"].split(":")[0])
        cr = [("koleso-uspeha/", "Программа"), (murl(mod), "Модуль %d" % mod["n"]), (None, t["title"])]
    else:
        mod = None; kick = "Трансформационный тренинг · 3–3,5 часа · продолжение марафона «Самопринятие»"
        cr = [("katalog/?format=trening", "Тренинги"), (None, t["title"])]
    stats = ""
    if t["stats"]:
        stats = '<div class="panel"><h2>Почему это важно</h2><div class="stats">%s</div></div><div style="height:20px"></div>' % "".join('<div class="stat">%s</div>' % e(x) for x in t["stats"])
    fy = ""
    if t["foryou"]:
        fy = '<div class="panel"><h2>%s</h2>%s</div><div style="height:20px"></div>' % (e(t["sub"] or "Этот тренинг для вас, если:"), ticks(t["foryou"], True))
    note = '<div class="note">%s</div>' % e(t["note"]) if t["note"] else ""
    revs = rev_html(s, "Участница тренинга «%s»" % t["title"])
    if not revs and mod and mod["n"] == 6: revs = rev_html("modul-6")
    if not revs:
        mm = PAIR_MINI.get(s)
        if mm: revs = rev_html("mini-" + mm["slug"], "Участница мини-тренинга «%s»" % mm["title"])
    revsec = '<section class="section alt"><div class="wrap"><h2>Отзывы участников</h2><div class="revs" style="margin-top:18px">%s</div></div></section>' % revs if revs else ""
    dur = "3–3,5 часа" if s == "samotsennost" else '<span data-duration>уточняется</span>'
    nxt = ""
    if mod:
        sib = "".join(card(turl(x), "Тренинг", "tt", T[x]["title"], T[x]["short"], T[x]["topics"], "trening", "trening-" + x, "training", root) for x in mod["trainings"] if x != s)
        mm = PAIR_MINI.get(s)
        start = ('<p class="muted">Хотите сначала попробовать формат? Начните с мини-тренинга <a href="%s%s">«%s»</a> (1–1,5 часа).</p>' % (root, miniurl(mm["slug"]), e(mm["title"]))) if mm else ""
        nxt = f'''<section class="section"><div class="wrap"><span class="kicker">Выгоднее и глубже</span><h2>Тренинг входит в модуль «{e(mod["title"])}»</h2>
<p class="lead">Пройдите все 4 тренинга модуля за месяц — тема прорабатывается комплексно.</p>{start}
<div class="btns">{cta("modul-%d" % mod["n"], "module", "Модуль %d «%s»" % (mod["n"], mod["title"]), "Купить весь модуль")}<a class="btn ghost" href="{root}{murl(mod)}">О модуле</a><a class="btn ghost" href="{root}koleso-uspeha/">Вся программа</a></div>
<h3 style="margin-top:30px">Другие тренинги модуля</h3><div class="grid g3">{sib}</div></div></section>'''
    else:
        nxt = f'''<section class="section"><div class="wrap"><h2>Начните с марафона</h2><p class="lead">Тренинг «Самоценность» — продолжение марафона «Самопринятие».</p><div class="btns"><a class="btn ghost" href="{root}marafon/samoprinyatie/">Марафон «Самопринятие»</a></div></div></section>'''
    body = f'''<section class="hero"><div class="wrap">{crumbs(root, cr)}
<span class="kicker">{e(kick)}</span><h1>{e(t["title"])}</h1><p class="lead">{e(t["lead"])}</p>
<div class="btns">{cta(code, "training", t["title"])}<a class="btn ghost" href="#detail">Подробнее</a></div></div></section>
<section class="section" id="detail" style="padding-top:10px"><div class="wrap layout"><div>
{stats}{fy}<div class="panel"><h2>{"На тренинге вы получите" if s in ("ya-vizhu-dengi","dengi-iz-detstva","finansovyj-potolok","moya-bogataya-zhizn","konkretnye-shagi") else "В результате ты:"}</h2>{ticks(t["results"])}{note}</div>
<div class="panel" style="margin-top:20px"><h2>Как проходит</h2>{HOW}</div>
</div>{buybox(code, "training", t["title"], [("Формат", "онлайн, живая группа"), ("Длительность", dur)])}</div></section>
{revsec}{nxt}'''
    layout(turl(s), t["title"] + " — тренинг", "%s Трансформационный тренинг онлайн. Ведущая — %s." % (t["lead"][:150], HOSTS), body, "cat",
           mcta=cta(code, "training", t["title"]))

# ------------------------------------------------------------------ MODULE
def module_page(m):
    root = "../../"; code = "modul-%d" % m["n"]
    items = ""
    for i, s in enumerate(m["trainings"], 1):
        t = T[s]
        items += '<div class="card"><span class="tag tt">Тренинг %d</span><h3>%s</h3><p class="muted">%s</p>%s<a class="more" href="%s%s">Подробнее о тренинге →</a></div>' % (
            i, e(t["title"]), e(t["lead"]), ticks(t["results"][:3]), root, turl(s))
    revs = ""
    for s in m["trainings"]:
        revs += rev_html(s, "Участница тренинга «%s»" % T[s]["title"], 1)
    if m["n"] == 6: revs = rev_html("modul-6")
    prev = MOD.get(m["n"] - 1); nx = MOD.get(m["n"] + 1)
    pn = ""
    if prev: pn += '<a class="btn ghost sm" href="%s%s">← Модуль %d</a>' % (root, murl(prev), prev["n"])
    if nx: pn += '<a class="btn ghost sm" href="%s%s">Модуль %d →</a>' % (root, murl(nx), nx["n"])
    part = "koleso-part1" if m["n"] <= 3 else "koleso-part2"
    partname = "Часть 1 «Внутренняя опора» (модули 1–3)" if m["n"] <= 3 else "Часть 2 «Проявленность и масштаб» (модули 4–6)"
    body = f'''<section class="hero"><div class="wrap">{crumbs(root, [("koleso-uspeha/", "Программа «Колесо успеха»"), (None, "Модуль %d" % m["n"])])}
<span class="kicker">Модуль {m["n"]} из 6 · 1 месяц · 4 трансформационных тренинга · онлайн</span>
<h1>{e(m["title"])}</h1><p class="lead">{e(m["intro"])}</p>
<div class="meta"><span class="chip c{(m["n"]-1)%4+1}">Цель модуля: {e(m["goal"])}</span></div>
<div class="btns">{cta(code, "module", "Модуль %d «%s»" % (m["n"], m["title"]), "Купить модуль")}<a class="btn ghost" href="#program">Программа модуля</a></div></div></section>
<section class="section" id="program" style="padding-top:10px"><div class="wrap layout"><div>
<h2>4 тренинга модуля</h2><div class="grid" style="margin-top:16px">{items}</div>
</div>{buybox(code, "module", "Модуль %d «%s»" % (m["n"], m["title"]), [("Формат", "онлайн, живая группа"), ("Длительность", "1 месяц"), ("Тренингов", "4")], "Купить модуль")}</div></section>
<section class="section alt"><div class="wrap"><h2>Отзывы участников</h2><div class="revs" style="margin-top:18px">{revs}</div></div></section>
<section class="section"><div class="wrap"><span class="kicker">Варианты участия</span><h2>Как можно пройти эту тему</h2>
<div class="tiers" style="margin-top:20px">
<div class="tier"><h3>Один тренинг</h3><p class="muted">Выберите тренинг выше и запишитесь на него отдельно.</p><div class="p">{price_span("training","training")}</div><a class="btn ghost" href="#program">Выбрать тренинг</a></div>
<div class="tier"><h3>Весь модуль</h3><p class="muted">4 тренинга за месяц — комплексная проработка темы.</p><div class="p">{price_span(code,"module")}</div><p class="save" data-save="module" data-code="{code}"></p>{cta(code, "module", "Модуль %d «%s»" % (m["n"], m["title"]))}</div>
<div class="tier best"><h3>{e(partname)}</h3><p class="muted">3 месяца, 12 тренингов. Этот модуль — внутри.</p><div class="p">{price_span(part,"")}</div><p class="save" data-save="part" data-code="{part}"></p>{cta(part, "", partname)}</div>
</div><div class="btns">{pn}<a class="btn ghost sm" href="{root}koleso-uspeha/">Вся программа</a></div></div></section>'''
    layout(murl(m), "Модуль %d «%s»" % (m["n"], m["title"]), "%s Модуль программы «Колесо успеха»: 1 месяц, 4 тренинга онлайн." % m["intro"][:140], body, "prog",
           mcta=cta(code, "module", "Модуль %d «%s»" % (m["n"], m["title"]), "Купить модуль"))

# ------------------------------------------------------------------ FLAGSHIP
def flagship():
    root = "../"
    road = "".join('<a class="m%d" href="%s%s"><span class="n">Модуль %d · месяц %d</span><b>%s</b><span>Цель: %s</span></a>' % (m["n"], root, murl(m), m["n"], m["n"], e(m["title"]), e(m["goal"])) for m in MODULES)
    road += '<div class="m7" style="border-radius:18px;padding:18px;min-height:150px"><span class="n" style="font:700 13px var(--sans);letter-spacing:.08em;text-transform:uppercase;opacity:.7">Модуль 7 · в разработке</span><b style="display:block;font-family:var(--serif);font-size:19px;margin:6px 0">Системное мышление</b><span style="font-size:14px">Семья, общество, государство — и «Моя система: я дирижёр».</span></div>'
    allrev = rev_html("ya-vizhu-dengi", "Участница тренинга «Я вижу деньги»", 1) + rev_html("strah-uspeha", "Участница тренинга «Страх успеха»", 1) + rev_html("ne-daj-soboj-manipulirovat", None, 1) + rev_html("moj-produkt-krutoj", "Участница тренинга «Мой продукт крутой!»", 1) + rev_html("koroli-prokrastinacii", "Участница тренинга «Короли прокрастинации»", 1) + rev_html("modul-6", None, 1)
    rows = [("Длительность", "1 занятие", "1 месяц", "3 месяца", "6 месяцев"),
            ("Трансформационных тренингов", "1", "4", "12", "24"),
            ("Модулей", "—", "1", "3", "6"),
            ("Формат", "онлайн, вживую", "онлайн, вживую", "онлайн, вживую", "онлайн, вживую"),
            ("Комплексная работа со всеми сферами", "—", "одна сфера", "внутренняя опора: деньги, страхи, ограничения", "всё колесо: от денег до масштаба"),
            ("Стоимость", price_span("training", "training"), price_span("module", "module"), price_span("koleso-part1", "") + " / часть", price_span("koleso-full", "")),
            ("Выгода", "—", '<span data-save="module" data-code="module" data-short></span>', '<span data-save="part" data-code="koleso-part1" data-short></span>', '<span data-save="full" data-code="koleso-full" data-short></span>')]
    thead = '<tr><th></th><th>Тренинг</th><th>Модуль</th><th>Часть (3 мес.)</th><th class="best">Полная программа</th></tr>'
    tbody = "".join("<tr><th>%s</th><td>%s</td><td>%s</td><td>%s</td><td class=\"best\">%s</td></tr>" % r for r in rows)
    faq = faq_items([
     ("Обязательно проходить все 6 месяцев?", "Нет. Можно пройти полную программу, одну из частей по 3 месяца, отдельный модуль или даже один тренинг. Начать можно с мини-тренинга."),
     ("Можно начать с Части 1, а потом продолжить?", "Да, Часть 2 логично продолжает Часть 1. Условия перехода уточняйте у Марины."),
     ("Есть записи занятий?", "Тренинги проводятся только вживую: эффект возникает в живой групповой работе с ведущей."),
     ("Я не «большой бизнес». Мне подойдёт?", "Масштаб у каждого свой: переход на новый уровень в своём деле или даже смена работы на лучшие условия — это тоже масштабирование. Программа для предпринимателей, экспертов, фрилансеров, руководителей и тех, кто работает в найме."),
    ])
    body = f'''<section class="hero"><div class="wrap">{crumbs(root, [(None, "Программа «Колесо успеха»")])}
<span class="kicker">Флагманская программа · 6 модулей · 24 тренинга · онлайн</span>
<h1>Колесо успеха</h1>
<p class="lead">6 модулей по 1 месяцу. Каждый — 4 трансформационных тренинга, которые ведут из точки А в точку Б: от осознания денежных ограничений и освобождения от страхов — к проявленности, системности и масштабу.</p>
<div class="btns">{cta("koleso-full", "", "Программа «Колесо успеха» — 6 месяцев", "Купить программу")}<a class="btn ghost" href="#tiers">Сравнить форматы участия</a></div>
<div class="meta"><span class="chip">Ведущая: {HOSTS}</span><span class="chip">Старт: {date_span("koleso-full","")}</span></div></div></section>

<section class="section alt"><div class="wrap"><span class="kicker">Путь по колесу</span><h2>6 модулей = 6 сфер</h2>
<div class="road" style="margin-top:22px">{road}</div></div></section>

<section class="section" id="tiers"><div class="wrap"><span class="kicker">Форматы участия</span><h2>Выберите свою глубину</h2>
<div class="tiers" style="margin-top:22px">
<div class="tier"><span class="tag mod">3 месяца</span><h3>Часть 1 «Внутренняя опора»</h3><p class="muted">Модули 1–3: деньги, страхи, выход из замкнутого круга. 12 тренингов.</p><ul><li>Танго с деньгами</li><li>Сквозь страхи и сомнения</li><li>Выход из замкнутого круга</li></ul><div class="p">{price_span("koleso-part1","")}</div><p class="save" data-save="part" data-code="koleso-part1"></p>{cta("koleso-part1","","Колесо успеха — Часть 1 «Внутренняя опора»")}</div>
<div class="tier best"><span class="tag prog">6 месяцев</span><h3>Полная программа</h3><p class="muted">Все 6 модулей, 24 тренинга. Полный путь от осознания ограничений до масштабирования.</p><ul><li>Все модули 1–6</li><li>Комплексная работа со всеми сферами</li><li>Последовательный путь по всем 6 целям колеса</li></ul><div class="p">{price_span("koleso-full","")}</div><p class="save" data-save="full" data-code="koleso-full"></p>{cta("koleso-full","","Программа «Колесо успеха» — 6 месяцев")}</div>
<div class="tier"><span class="tag mod">3 месяца</span><h3>Часть 2 «Проявленность и масштаб»</h3><p class="muted">Модули 4–6: продукт и цена, ритм без стресса, от мечты к цели. 12 тренингов.</p><ul><li>Мой продукт — моя гордость</li><li>В ритме успеха</li><li>Квантовый скачок</li></ul><div class="p">{price_span("koleso-part2","")}</div><p class="save" data-save="part" data-code="koleso-part2"></p>{cta("koleso-part2","","Колесо успеха — Часть 2 «Проявленность и масштаб»")}</div>
</div>
<p class="note" data-upgrade>Можно начать с Части 1 и продолжить Частью 2. Условия перехода уточняйте у Марины.</p>
<h3 style="margin-top:34px">Сравнение всех вариантов</h3>
<div class="tblwrap"><table class="tbl"><thead>{thead}</thead><tbody>{tbody}</tbody></table></div>
<p class="muted small" style="margin-top:10px">Хотите сначала попробовать? <a href="{root}katalog/?format=mini">Мини-тренинги на 1–1,5 часа</a> — лучший способ познакомиться с форматом.</p>
</div></section>

<section class="section alt"><div class="wrap two"><div><span class="kicker">Как это устроено</span><h2>4 живых тренинга в каждом месяце</h2>{HOW}</div>
<div><span class="kicker">Для кого</span><h2>Программа для вас, если</h2>{ticks(["Вы предприниматель, эксперт, фрилансер или руководитель — или работаете в найме и хотите большего.", "Доход стоит на месте, несмотря на усилия.", "Страхи и сомнения мешают принимать смелые решения.", "Вы всё тащите на себе и устали от контроля и конфликтов.", "Сложно заявлять о себе и называть цену.", "Хочется двигаться к мечте системно, без выгорания."], True)}</div></div></section>

<section class="section"><div class="wrap"><h2>Отзывы участников модулей</h2><div class="revs" style="margin-top:18px">{allrev}</div><div class="btns"><a class="btn ghost" href="{root}otzyvy/">Все отзывы</a></div></div></section>
<section class="section alt"><div class="wrap"><h2>Вопросы о программе</h2>{faq}</div></section>
<section class="section"><div class="wrap"><div class="band"><h2>Готовы прокрутить своё колесо?</h2><p>Напишите — расскажем о ближайшем потоке и поможем выбрать формат.</p><div class="btns" style="justify-content:center">{cta("koleso-full","","Программа «Колесо успеха»","Купить программу","btn light")}</div></div></div></section>'''
    layout("koleso-uspeha/", "Программа «Колесо успеха» — 6 модулей, 24 тренинга",
           "Флагманская программа: 6 модулей по месяцу — деньги, страхи, ограничения, проявленность, ритм, цели. Полностью, частями по 3 месяца или по модулям. Онлайн, вживую.",
           body, "prog", mcta=cta("koleso-full", "", "Программа «Колесо успеха»", "Купить программу"))

def faq_items(items):
    return "".join("<details><summary>%s</summary><div>%s</div></details>" % (e(q), a) for q, a in items)

# ------------------------------------------------------------------ PSY
def psy():
    root = "../"
    personal = "".join(card(turl(s), "Тренинг", "tt", T[s]["title"], why, T[s]["topics"], "trening", "trening-" + s, "training", root) for s, why in [
        ("samozvanets-strah-razoblacheniya", "Право заявлять о своей компетенции — без страха «разоблачения»."),
        ("stoimost-uslugi", "Определить комфортную стоимость своей консультации или программы."),
        ("kak-ozvuchivat-cenu", "Называть цену клиенту без оправданий и уступок."),
        ("samotsennost", "Для помогающих профессий: помощь другим без потери себя."),
        ("proyavlyajsya-legko", "Личный бренд, соцсети, выступления — легко."),
        ("moj-produkt-krutoj", "Сначала «продать» свой продукт себе.")])
    body = f'''<section class="hero"><div class="wrap">{crumbs(root, [(None, "Для психологов и коучей")])}
<span class="kicker">Для начинающих и практикующих специалистов</span>
<h1>Для психологов, коучей и экспертов помогающих профессий</h1>
<p class="lead">Этот раздел — отдельно от клиентских тренингов. Здесь — то, что полезно вам как специалисту: создание своего глубокого продукта, личная проработка профессиональных «тормозов» и возможность увидеть формат Т-игр и групповой работы с МАК-картами изнутри.</p>
<div class="btns">{cta("arhitektor-produkta","","Наставничество «Архитектор продукта»","Обсудить с Мариной")}<a class="btn ghost" href="#personal">Личная проработка</a></div></div></section>

<section class="section" style="padding-top:10px"><div class="wrap layout"><div>
<div class="panel"><span class="kicker">Премиум · индивидуально</span><h2>«Архитектор продукта»: наставничество по созданию трансформационных игр и программ</h2>
<p>Для психологов, коучей и экспертов, которые хотят создать свой глубокий продукт, но не знают, как выстроить методологию и механику.</p>
<h3>Что входит</h3>{ticks(["Диагностика вашего текущего продукта или идеи.", "Помощь в создании структуры: от запроса — до механики.", "Присутствие на тестовом проведении с обратной связью.", "Рекомендации по упаковке и воронке: как продавать этот продукт."])}
<p style="margin-top:14px"><b>Формат:</b> индивидуальное сопровождение в течение 1–2 месяцев.</p></div>
</div>{buybox("arhitektor-produkta","","Наставничество «Архитектор продукта»",[("Формат","индивидуально, онлайн"),("Срок","1–2 месяца")],"Обсудить проект с Мариной")}</div></section>

<section class="section alt" id="personal"><div class="wrap"><span class="kicker">Личная работа специалиста</span><h2>Тренинги, которые особенно откликаются специалистам</h2>
<p class="lead">Самозванец, цена своей услуги, «спасательство» — частые профессиональные тормоза помогающих специалистов. Вы проходите тренинг как участник, для себя.</p>
<div class="grid g3" style="margin-top:20px">{personal}</div></div></section>

<section class="section"><div class="wrap two">
<div><span class="kicker">Формат изнутри</span><h2>Посмотреть, как работает Т-игра</h2>
<p>Авторская версия игры «Лила», переработанная Мариной Степановой для бизнеса и общих ситуаций: 4 часа, 4 участника, онлайн. Вы проходите игру со своим запросом — и видите, как ведущая работает с группой, как задаются вопросы и как используются МАК-карты.</p>
<div class="btns"><a class="btn ghost" href="{root}igra/lila/">Об игре «Лила»</a></div></div>
<div>{rev_html("samozvanets-strah-razoblacheniya", None, 1)}{rev_html("igra-lila", "Участница игры «Лила»", 1)}</div></div></section>

<section class="section alt" data-psy-waitlist><div class="wrap"><div class="panel">
<span class="kicker">Направление в разработке · лист ожидания</span>
<h2>Обучение ведению Т-игр и групповых практик с МАК</h2>
<p>Мы готовим отдельный формат для специалистов, которые хотят вести групповые трансформационные практики. Оставьте заявку в лист ожидания — сообщим первыми, когда откроется набор, и учтём ваши пожелания к программе.</p>
<div class="btns">{cta("psy-obuchenie","","Лист ожидания: обучение ведению Т-игр и групп с МАК","Встать в лист ожидания")}</div>
<p class="small muted">Это не курс повышения квалификации и не программа с выдачей диплома.</p></div></div></section>
<section class="section"><div class="wrap"><h2>Вопросы специалистов</h2>{faq_items([
("Я начинающий психолог. Это для меня?", "Да: личная проработка (самозванец, цена услуги, проявленность) особенно полезна в начале практики. «Архитектор продукта» подойдёт, когда появится идея своего продукта."),
("Я практикую давно. Чем это может быть полезно?", "Созданием собственной трансформационной игры или программы с понятной механикой, упаковкой и воронкой — в индивидуальном сопровождении."),
("Можно ли использовать ваши игры в своей практике?", "Авторские игры и тренинги принадлежат авторам. Если вы хотите создать свой продукт — для этого и существует «Архитектор продукта»."),
])}</div></section>'''
    layout("dlya-psihologov/", "Для психологов и коучей", "Наставничество «Архитектор продукта» для психологов, коучей и экспертов: создание своей трансформационной игры или программы. Личная проработка специалиста.", body, "psy",
           mcta=cta("arhitektor-produkta", "", "Наставничество «Архитектор продукта»", "Обсудить с Мариной"))

# ------------------------------------------------------------------ OTHER
def hosts():
    root = "../"
    body = f'''<section class="hero"><div class="wrap">{crumbs(root, [(None, "Ведущая")])}<span class="kicker">Автор и ведущая</span><h1>Марина Степанова</h1>
<p class="lead">Автор программы «Колесо успеха», трансформационных тренингов и авторской версии игры «Лила». Автор и ведущая Т-игр и тренингов, предприниматель с опытом 9 лет.</p></div></section>
<section class="section" style="padding-top:10px"><div class="wrap">
<div class="panel"><div class="host"><div class="ph" data-photo="marina" data-root="{root}">МС</div><div><h2>Марина Степанова</h2><p>Автор и ведущая Т-игр и тренингов, предприниматель с опытом 9 лет.</p><p class="hidden" data-bio="marina"></p>{cta("vopros","","Вопрос Марине","Написать Марине в Telegram","btn sm")}</div></div></div>
</div></section>
<section class="section alt"><div class="wrap"><h2>Как участники говорят о работе Марины</h2><div class="revs" style="margin-top:18px">
<blockquote class="rev"><p>{e(R["bazovyj-strah"][2][0])}</p><cite>Участница тренинга «Базовый страх»</cite></blockquote>
<blockquote class="rev"><p>{e(R["igra-lila"][0][0])}</p><cite>Участница игры «Лила»</cite></blockquote>
<blockquote class="rev"><p>{e(R["samozvanets-strah-razoblacheniya"][2][0])}</p><cite>Участница тренинга «Самозванец! Страх разоблачения»</cite></blockquote>
<blockquote class="rev"><p>{e(R["dejstvuj-kak"][0][0])}</p><cite>Участница тренинга «Действуй как…»</cite></blockquote>
</div></div></section>
<section class="section"><div class="wrap center"><h2>Познакомиться с Мариной вживую</h2><p class="lead">Самый простой способ — мини-тренинг на 1–1,5 часа.</p><div class="btns"><a class="btn" href="{root}katalog/?format=mini">Выбрать мини-тренинг</a></div></div></section>'''
    layout("vedushchie/", "Ведущая: Марина Степанова", "Марина Степанова — автор и ведущая Т-игр и тренингов, предприниматель с опытом 9 лет. Автор программы «Колесо успеха».", body, "hosts")

def reviews_page():
    root = "../"
    secs = ""
    order = []
    for m in MODULES:
        for s in m["trainings"]:
            if s in R: order.append((s, "Тренинг «%s»" % T[s]["title"], turl(s)))
        if m["n"] == 6: order.append(("modul-6", "Модуль «Квантовый скачок от мечты к цели»", murl(m)))
    order.append(("samotsennost", "Тренинг «Самоценность»", turl("samotsennost")))
    for mm in MINIS:
        k = "mini-" + mm["slug"]
        if k in R: order.append((k, "Мини-тренинг «%s»" % mm["title"], miniurl(mm["slug"])))
    order.append(("igra-lila", "Игра «Лила»", "igra/lila/"))
    nav_ = " · ".join('<a href="#%s">%s</a>' % (k, e(t.split("«")[-1].rstrip("»"))) for k, t, u in order)
    for k, t, u in order:
        secs += '<h2 id="%s" style="margin-top:40px;font-size:26px">%s</h2><div class="revs">%s</div><p><a href="%s%s">Перейти к описанию →</a></p>' % (k, e(t), rev_html(k, "Участница"), root, u)
    body = f'''<section class="hero"><div class="wrap">{crumbs(root, [(None, "Отзывы")])}<span class="kicker">Отзывы</span><h1>Отзывы участников</h1>
<p class="lead">Настоящие отзывы участников тренингов и игр — слегка сокращены, без изменения смысла.</p><p class="small">{nav_}</p></div></section>
<section class="section" style="padding-top:0"><div class="wrap">{secs}</div></section>'''
    layout("otzyvy/", "Отзывы участников", "Отзывы участников тренингов Марины Степановой: деньги, страхи, контроль, конфликты, проявленность, цели.", body, "rev")

FAQ_MAIN = [
 ("Как проходят тренинги?", "Онлайн, вживую, в живой группе с ведущей. Используются метафорические ассоциативные карты (МАК), вопросы и практики. В конце вы формулируете конкретные шаги на ближайшие 24 часа и на неделю."),
 ("Есть ли записи?", "Мини-тренинги, трансформационные тренинги и игры проводятся только вживую — эффект возникает в живой групповой работе. В марафоне «Самопринятие» эфиры остаются в записи."),
 ("Обязательно говорить вслух при группе?", "Нет. Можно отвечать голосом или писать в чат — многие участники отмечают, что формат с чатом для них очень комфортный."),
 ("С чего лучше начать?", "С мини-тренинга на 1–1,5 часа по теме, которая откликается сильнее всего. Он показывает, что именно тормозит. Глубокая трансформация — в полном тренинге, модуле или программе."),
 ("Можно купить один тренинг или один модуль?", "Да. Каждый тренинг и каждый модуль можно пройти отдельно. Программу «Колесо успеха» можно пройти целиком (6 месяцев) или частями по 3 месяца."),
 ("Я не предприниматель. Мне подойдёт?", "Да. Тренинги для предпринимателей, экспертов, фрилансеров, руководителей и тех, кто работает в найме. Масштаб у каждого свой — и переход на новый уровень в работе тоже рост."),
 ("Как записаться и оплатить?", "Нажмите «Купить» на странице тренинга — откроется Telegram Марины (@MarinaNew) с готовым сообщением. Марина пришлёт ближайшую дату и детали для оплаты."),
 ("Это психотерапия?", "Нет. Это групповая трансформационная работа: тренинги и игры. Она не заменяет медицинскую или психиатрическую помощь. Если вы в остром состоянии — пожалуйста, обратитесь к врачу."),
 ("Я психолог. Есть что-то для специалистов?", 'Да, смотрите <a href="../dlya-psihologov/">раздел для психологов и коучей</a>.'),
]
def faq_page():
    root = "../"
    body = f'''<section class="hero"><div class="wrap">{crumbs(root, [(None, "Вопросы и ответы")])}<span class="kicker">FAQ</span><h1>Вопросы и ответы</h1></div></section>
<section class="section" style="padding-top:0"><div class="wrap">{faq_items(FAQ_MAIN)}
<div class="band" style="margin-top:30px"><h2>Остался вопрос?</h2><p>Напишите Марине — ответим лично.</p><div class="btns" style="justify-content:center">{cta("vopros","","Вопрос Марине","Задать вопрос","btn light")}</div></div></div></section>'''
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ_MAIN]}
    layout("faq/", "Вопросы и ответы", "Как проходят тренинги, есть ли записи, с чего начать, как записаться и оплатить.", body, "faq", jsonld=ld)

def marathon_samoprinyatie():
    root = "../../"; code = "marafon-samoprinyatie"; title = "Марафон «Самопринятие»"
    body = f'''<section class="hero"><div class="wrap">{crumbs(root, [("katalog/?format=marafon", "Марафоны"), (None, title)])}
<span class="kicker">Марафон · 5 недель · онлайн</span><h1>{title}</h1><p class="lead">5 недель мягкой трансформации в поддерживающем кругу. Это не про «стать лучше». Это про — стать собой.</p>
<div class="btns">{cta(code,"",title)}</div></div></section>
<section class="section" style="padding-top:10px"><div class="wrap layout"><div>
<div class="panel"><h2>Для кого</h2><p>Ты живёшь «на внешнюю оценку»? Уже многое сделано, но в глубине — напряжение, усталость, недовольство собой?</p>{ticks(["«Что-то внутри не отпускает. Как будто я сам себе — не союзник».", "«Сколько бы ни достиг(ла), внутри пусто или колко».", "«Я хочу не ещё одной задачи, а пространства, где можно быть собой. Без масок»."], True)}
<p style="margin-top:12px">Марафон — для тех, кто не хочет ломать себя, а хочет научиться быть с собой в теплоте и в правде.</p></div>
<div class="panel" style="margin-top:20px"><h2>Что ты получишь</h2>{ticks(["Умение останавливаться и слышать себя: где я? чего я сейчас хочу?", "Навык быть поддержкой себе — без зависимости от чужого мнения.", "Спокойствие: не спасать всех, не додумывать за других.", "Внутреннюю свободу — разрешить себе ошибку, уязвимость, проявленность.", "Контакт с телом и желаниями: почувствовать, когда пора отдохнуть или отказать.", "Принятие своей неидеальности как силы, а не слабости."])}</div>
<div class="panel" style="margin-top:20px"><h2>Формат</h2>{ticks(["5 недель.", "6 живых эфиров (в записи — остаются с тобой): мягкое ведение, ответы на вопросы, мини-практики для тела и проживания чувств.", "Сообщество с чатом поддержки.", "Еженедельные задания и вопросы на саморефлексию — ответы ты пишешь для себя.", "Удобная навигация: можно идти в своём ритме."])}
<div class="note">Мы не давим, не исправляем, не сравниваем. Мы создаём пространство, в котором ты вспоминаешь себя настоящего. Стоимость сделана такой, чтобы этот опыт был доступен каждому, кто готов услышать себя.</div></div>
</div>{buybox(code,"",title,[("Формат","онлайн, эфиры + чат"),("Длительность","5 недель")])}</div></section>
<section class="section alt"><div class="wrap"><span class="kicker">Продолжение</span><h2>Трансформационный тренинг «Самоценность»</h2><p class="lead">После марафона — тренинг на 3–3,5 часа: баланс между ценностью помогать другим и самоценностью.</p><div class="btns"><a class="btn ghost" href="{root}{turl("samotsennost")}">О тренинге «Самоценность»</a></div></div></section>'''
    layout("marafon/samoprinyatie/", title + " — 5 недель", "5 недель мягкой трансформации: 6 живых эфиров, чат поддержки, задания на саморефлексию. Стать собой, а не «лучше».", body, "cat", mcta=cta(code, "", title))

def marathon_dvizhenie():
    root = "../../"; code = "marafon-dvizhenie"; title = "Марафон «Движение к цели»"
    body = f'''<section class="hero"><div class="wrap">{crumbs(root, [("katalog/?format=marafon", "Марафоны"), (None, title)])}
<span class="kicker">Марафон · 14 дней · Telegram + 3 живых эфира</span><h1>{title}</h1><p class="lead">Не про волшебные пендели, а про реальное движение. 8 шагов — чтобы идти к своему, не сливаясь. 14 дней — чтобы встроить навык, который останется с тобой.</p>
<div class="btns">{cta(code,"",title)}</div></div></section>
<section class="section" style="padding-top:10px"><div class="wrap layout"><div>
<div class="panel"><h2>Если тебе знакомо</h2>{ticks(["Есть желания и цели, но ты снова их откладываешь.", "Всё вроде бы ясно, но каждый день — «не сейчас».", "Устал(а) от мотивационных всплесков, которые быстро сдуваются.", "Или наоборот — всё контролируешь, но в душе пусто и будто не туда."], True)}</div>
<div class="panel" style="margin-top:20px"><h2>Вместе мы</h2>{ticks(["Найдём настоящую цель — не навязанную, а живую, от которой мурашки.", "Разложим её на понятные и реальные шаги.", "Отследим, что мешает — внутренне и внешне.", "Создадим устойчивый фокус и лёгкий темп — без перегруза и самоедства."])}
<div class="note">С тобой будут опытный коуч — Марина, обратная связь и пространство, где никто не давит — но всё работает.</div></div>
<div class="panel" style="margin-top:20px"><h2>Подходит, если</h2>{ticks(["Хочешь двинуться с мёртвой точки.", "Давно «в подготовке», но не в реализации.", "Теряешь себя в суете и хочешь фокус.", "Хочешь выдохнуть, понять себя и почувствовать реальное движение."], True)}
<p style="margin-top:12px">Чтобы записаться, напиши Марине в Telegram <b>@MarinaNew</b>: «ХОЧУ В ДВИЖЕНИЕ» — и мы пришлём детали для оплаты. Кнопка «Купить» подставит этот текст сама.</p></div>
</div>{buybox(code,"",title,[("Формат","Telegram + 3 живых эфира"),("Длительность","14 дней, 8 шагов")])}</div></section>
<section class="section alt"><div class="wrap"><h2>Хотите глубже?</h2><p class="lead">Модуль «Квантовый скачок от мечты к цели» — 4 трансформационных тренинга за месяц.</p><div class="btns"><a class="btn ghost" href="{root}{murl(MOD[6])}">О модуле 6</a></div></div></section>'''
    layout("marafon/dvizhenie-k-celi/", title + " — 14 дней", "14 дней, 8 шагов, 3 живых эфира и поддержка коуча: найти живую цель, разложить на шаги и двинуться с мёртвой точки.", body, "cat", mcta=cta(code, "", title))

def lila():
    root = "../../"; code = "igra-lila"; title = "Игра «Лила» — авторская версия"
    body = f'''<section class="hero"><div class="wrap">{crumbs(root, [("katalog/?format=igra", "Игры"), (None, "Лила")])}
<span class="kicker">Трансформационная игра · 4 часа · 4 участника · онлайн</span><h1>Игра «Лила»</h1>
<p class="lead">Авторская версия Марины Степановой, переработанная для бизнеса и общих ситуаций (на основе версии Хариша Джохари «Джняна Чаупада»). Ваш бизнес, отношения или карьера развиваются не так, как хотелось бы? Возможно, мешают невидимые ограничения в мышлении и стратегиях.</p>
<div class="btns">{cta(code,"",title,"Записаться и оплатить")}</div></div></section>
<section class="section" style="padding-top:10px"><div class="wrap layout"><div>
<div class="panel"><h2>Эта игра для вас, если</h2>{ticks(["Бизнес застрял на одном уровне, и вы не понимаете, в чём причина.", "Вы упускаете возможности для роста, но боитесь рисковать.", "Сложно масштабироваться, делегировать или привлекать новые ресурсы.", "Бизнес приносит стресс, а не удовольствие.", "Внутренние страхи и сомнения мешают принимать смелые решения."], True)}</div>
<div class="panel" style="margin-top:20px"><h2>В процессе игры вы</h2>{ticks(["Найдёте самую важную точку развития.", "Увидите скрытые сценарии, которые управляют вашей жизнью.", "Поймёте, какие стратегии ведут к успеху, а какие тормозят рост.", "Найдёте внутренние ресурсы и новые решения.", "Получите практические инсайты, которые сможете применить сразу."])}
<div class="note">«Лила» — не просто игра, а глубокий инструмент осознания. Она покажет, где ваши сильные и слабые стороны, какие решения ведут к процветанию, а какие — в тупик.</div></div>
</div>{buybox(code,"",title,[("Формат","онлайн"),("Длительность","4 часа"),("Участников","4")],"Записаться и оплатить")}</div></section>
<section class="section alt"><div class="wrap"><h2>Отзывы игроков</h2><div class="revs" style="margin-top:18px">{rev_html("igra-lila","Участница игры «Лила»")}</div></div></section>'''
    layout("igra/lila/", "Игра «Лила» — авторская трансформационная игра", "Авторская версия «Лилы» для бизнеса и жизненных ситуаций: 4 часа, 4 участника, онлайн. Найти точку развития и скрытые сценарии.", body, "cat", mcta=cta(code, "", title, "Записаться и оплатить"))

def klub():
    root = "../"
    body = f'''<section class="hero"><div class="wrap">{crumbs(root, [(None, "Клуб «ЗАДОЛБАЛО!»")])}<span class="kicker">Бесплатно · Telegram</span>
<h1>Клуб живых предпринимателей «ЗАДОЛБАЛО!»</h1>
<p class="lead">Здесь ты без масок! Расскажи, что бесит в бизнесе, поделись, что накипело, — и получи рекомендацию, как с этим разобраться, от проекта психологической поддержки предпринимателей. Выдохнул — и пошёл чинить.</p>
<div class="btns">{cta("klub","","Клуб «ЗАДОЛБАЛО!»","Вступить в клуб")}<a class="btn ghost hidden" data-link="clubUrl" data-hide-empty target="_blank" rel="noopener">Открыть чат клуба</a><a class="btn ghost hidden" data-link="channelUrl" data-hide-empty target="_blank" rel="noopener">Канал «Колесо успеха»</a></div></div></section>
<section class="section" style="padding-top:10px"><div class="wrap two">
<div class="panel"><h2>Здесь можно</h2>{ticks(["Высказывать всё, что накипело в работе: сотрудники и подрядчики, налоги, операционка, рабочие ситуации.", "Обсуждать сложности и «затыки» среди равных и понимающих.", "Получить поддерживающую обратную связь на свой вопрос (в области психологии и коучинга).", "Участвовать в эфирах и мероприятиях клуба."])}</div>
<div class="panel"><h2>Здесь нельзя</h2>{ticks(["Проявлять неуважение к организаторам и участникам.", "Осуждать за слабость и насмехаться над сложностями других.", "Оставлять ссылки."], True)}<p class="small muted" style="margin-top:12px">Мы сохраняем поддерживающую атмосферу.</p></div>
</div></section>'''
    layout("klub/", "Клуб предпринимателей «ЗАДОЛБАЛО!»", "Бесплатный Telegram-клуб для предпринимателей: выговориться без масок и получить поддержку и рекомендации от Марины Степановой, автора проекта «Колесо успеха».", body, "")

def notfound():
    body = '''<section class="hero"><div class="wrap center"><h1>Страница не найдена</h1><p class="lead">Возможно, ссылка устарела. Начните с главной или каталога.</p><div class="btns"><a class="btn" href="/koleso-uspeha/">На главную</a><a class="btn ghost" href="/koleso-uspeha/katalog/">Все тренинги</a></div></div></section>'''
    layout("404.html", "Страница не найдена", "Страница не найдена.", body)

if __name__ == "__main__":
    home(); catalog(); flagship(); psy(); hosts(); reviews_page(); faq_page(); klub()
    marathon_samoprinyatie(); marathon_dvizhenie(); lila()
    for m in MODULES: module_page(m)
    for s in T: training_page(s)
    for m in MINIS: mini_page(m)
    notfound()
    # sitemap
    urls = "".join("<url><loc>%s%s</loc></url>" % (SITE, p) for p, _ in PAGES if not p.endswith(".html"))
    open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>' % urls)
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n" % SITE)
    pass
    print(len(PAGES), "pages")
