/*! ai-widget.js — помощник «Код счастливой жизни». Ключей внутри нет. Сборка: scripts/build.mjs */
(function(){
"use strict";
// Сценарный «Навигатор»: работает без ИИ и без сети. Общий для сервера (Deno) и виджета (браузер).
// В браузерную сборку попадает без слов `export` (см. scripts/build.mjs) — не используйте здесь import/Deno/DOM.

function normalize(s) {
  return (" " + String(s || "").toLowerCase().replace(/ё/g, "е").replace(/[^a-zа-я0-9]+/gi, " ").replace(/\s+/g, " ").trim() + " ");
}

function hasKw(normText, kw) {
  const k = normalize(kw).trim();
  if (!k) return false;
  // короткие слова (до 3 букв) — только целым словом, остальные — по началу слова (основе)
  if (k.length <= 3 && k.indexOf(" ") < 0) return normText.indexOf(" " + k + " ") >= 0;
  return normText.indexOf(" " + k) >= 0;
}

function detectCrisis(text, sc) {
  const t = normalize(text);
  return ((sc.crisis && sc.crisis.keywords) || []).some((k) => hasKw(t, k));
}

function containsBanned(text, sc) {
  const t = normalize(text);
  return (sc.banned || []).some((k) => hasKw(t, k));
}

function matchIntent(text, sc) {
  const t = normalize(text);
  let best = null, bestScore = 0;
  for (const it of sc.intents || []) {
    let score = 0;
    for (const kw of it.keywords || []) if (hasKw(t, kw)) score += normalize(kw).trim().split(" ").length;
    if (score > bestScore) { best = it; bestScore = score; }
  }
  return best ? { intent: best, score: bestScore } : null;
}

function tgLink(sc, text) {
  return (sc.marina_tg || "https://t.me/MarinaNew") + (text ? "?text=" + encodeURIComponent(text) : "");
}

function resolveButton(b, sc) {
  if (!b) return null;
  if (b.path !== undefined) return { label: b.label, url: (sc.site_base || "") + ((sc.path_map && sc.path_map[b.path]) || b.path) };
  if (b.tg !== undefined) return { label: b.label, url: tgLink(sc, b.tg) };
  if (b.url) return { label: b.label, url: b.url };
  if (b.cmd) return { label: b.label, cmd: b.cmd };
  return null;
}

function resolveButtons(list, sc) {
  return (list || []).map((b) => resolveButton(b, sc)).filter(Boolean);
}

function intentById(id, sc) {
  if (id === "menu") return { id: "menu", reply: sc.menu.reply, buttons: sc.menu.buttons };
  return (sc.intents || []).find((i) => i.id === id) || null;
}

function crisisReply(sc) {
  return { reply: sc.crisis.reply, suggestions: resolveButtons(sc.crisis.buttons, sc), intent: "crisis", crisis: true };
}

/** Главная функция сценария: текст → ответ. Никогда не бросает исключений. */
/** Сценарий для другого сайта (v2 и т. п.): та же логика, свои адреса страниц. */
function scenarioForSite(sc, site) {
  const s = sc.sites && sc.sites[site];
  return s ? Object.assign({}, sc, { site_base: s.site_base, path_map: s.path_map || {} }) : sc;
}

function scriptedReply(text, sc) {
  try {
    const raw = String(text || "");
    if (detectCrisis(raw, sc)) return crisisReply(sc);
    const cmd = raw.trim().match(/^intent:([a-z_]+)$/);
    const it = cmd ? intentById(cmd[1], sc) : (matchIntent(raw, sc) || {}).intent;
    if (it) return { reply: it.reply, suggestions: resolveButtons(it.buttons, sc), intent: it.id, crisis: false };
    return { reply: sc.default.reply, suggestions: resolveButtons(sc.default.buttons, sc), intent: "other", crisis: false };
  } catch (_e) {
    return { reply: "Напишите, пожалуйста, Марине в Telegram @MarinaNew — она ответит лично.", suggestions: [{ label: "Написать Марине", url: "https://t.me/MarinaNew" }], intent: "other", crisis: false };
  }
}

/** Тест: answers — строка из индексов ответов, напр. "02141". Возвращает id темы с наибольшим числом ответов. */
function testTopic(answers, sc) {
  const counts = {};
  const qs = sc.test.questions;
  String(answers).split("").forEach((ch, qi) => {
    const q = qs[qi]; const o = q && q.options[+ch];
    if (o) counts[o[1]] = (counts[o[1]] || 0) + 1;
  });
  let best = "celi", n = -1;
  for (const opt of qs[0].options) { const k = opt[1]; if ((counts[k] || 0) > n) { best = k; n = counts[k] || 0; } }
  return best;
}

/** Карта дня: стабильна для человека в течение суток (seed — id пользователя или случайное число). */
function cardOfDay(sc, seed, date) {
  const d = date || new Date();
  const day = Math.floor((d.getTime() + 3 * 3600e3) / 864e5); // сутки по МСК
  let h = 2166136261;
  const s = String(seed) + ":" + day;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
  return sc.cards[h % sc.cards.length];
}

/** Предохранитель: после N сбоев подряд ИИ пропускается на cooldownMs и сразу отвечает сценарий. */
class Breaker {
  constructor(threshold = 3, cooldownMs = 5 * 60e3, state) {
    this.threshold = threshold; this.cooldownMs = cooldownMs;
    this.fails = (state && state.fails) || 0; this.until = (state && state.until) || 0;
  }
  isOpen(now = Date.now()) { return this.until > now; }
  success() { this.fails = 0; this.until = 0; }
  failure(now = Date.now()) {
    this.fails += 1;
    if (this.fails >= this.threshold) { this.until = now + this.cooldownMs; this.fails = 0; }
  }
  state() { return { fails: this.fails, until: this.until }; }
}

/** Извлечь JSON из ответа модели (как в content_engine.py: снимаем ```json и берём от первой { до последней }). */
function extractJson(text) {
  let t = String(text || "").trim();
  t = t.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
  const a = t.indexOf("{"), b = t.lastIndexOf("}");
  if (a >= 0 && b > a) t = t.slice(a, b + 1);
  return JSON.parse(t);
}

/** Разрешена ли ссылка: страницы из каталога (без query/hash) и Telegram Марины/канала. */
function isAllowedUrl(url, allowedPages) {
  try {
    const u = new URL(url);
    if (u.protocol !== "https:") return false;
    if (u.host === "t.me") return /^\/(MarinaNew|koleso_uspeha)\/?$/i.test(u.pathname);
    const clean = u.origin + u.pathname.replace(/\/?$/, "/");
    return allowedPages.has(clean);
  } catch (_e) { return false; }
}

/* ---- Виджет. Настройка (любой из вариантов):
   window.KZ_AI = { aiEndpoint: "https://<ref>.supabase.co/functions/v1/kod-zhizni-ai", site: "v1", scenarioUrl: "...", title: "..." }
   или для сайта v1: window.SITE_CONFIG.ai = { enabled: true, aiEndpoint: "" }
   Пустой aiEndpoint = работает только сценарный «Навигатор» (без сервера и без ИИ). */
var SC0 = window.SITE_CONFIG || {};
var CFG = Object.assign({ enabled: true, aiEndpoint: "", site: "v1", title: "Помощник по программам", subtitle: "Подберу формат за минуту", timeoutMs: 15000 }, SC0.ai || {}, window.KZ_AI || {});
if (!CFG.enabled || window.__kzAiLoaded) return;
window.__kzAiLoaded = true;
var me = document.currentScript && document.currentScript.src;
var scenarioUrl = CFG.scenarioUrl || (me ? me.replace(/ai-widget\.js(\?.*)?$/, "ai-scenario.json" + (me.match(/\?.*$/) || [""])[0]) : "ai-scenario.json");
var LABEL = { ai: "ИИ-помощник", script: "Навигатор" };
var SC = null, scPromise = null;
var MINI_SC = { site_base: "", marina_tg: "https://t.me/MarinaNew", crisis: { keywords: ["суицид", "не хочу жить", "покончить с собой", "убить себя"], reply: "Пожалуйста, не оставайтесь с этим одни: 112 — при угрозе жизни; +7 (495) 989-50-50 — экстренная психологическая помощь МЧС (круглосуточно); 8-800-2000-122 — для детей, подростков и родителей.", buttons: [] },
  intents: [], menu: { reply: "Напишите Марине — она ответит лично.", buttons: [] }, default: { reply: "Напишите, пожалуйста, Марине в Telegram — она ответит лично и подскажет, с чего начать.", buttons: [{ label: "Написать Марине", url: "https://t.me/MarinaNew" }] } };
function loadScenario() {
  if (SC) return Promise.resolve(SC);
  if (!scPromise) scPromise = fetch(scenarioUrl, { cache: "force-cache" }).then(function (r) { if (!r.ok) throw 0; return r.json(); })
    .then(function (j) { SC = j; if (CFG.siteBase) SC.site_base = CFG.siteBase; return SC; })
    .catch(function () { SC = MINI_SC; return SC; });
  return scPromise;
}
/* предохранитель в localStorage: 3 сбоя сервера подряд → 5 минут сразу сценарий */
var BK = "kz_ai_breaker";
function brk() { var st = null; try { st = JSON.parse(localStorage.getItem(BK) || "null"); } catch (e) {} return new Breaker(3, 5 * 60e3, st); }
function brkSave(b) { try { localStorage.setItem(BK, JSON.stringify(b.state())); } catch (e) {} }
function goal(name, params) { try { var id = (SC0 || {}).yandexMetrikaId; if (window.ym && id) ym(+id, "reachGoal", name, params || {}); } catch (e) {} }
function utmNote() { try { var u = JSON.parse(localStorage.getItem("ku_last_utm") || "{}"); var s = [u.utm_source, u.utm_campaign, u.utm_content].filter(Boolean).join(" / "); return "\n(источник: помощник сайта" + (s ? " / " + s : "") + ")"; } catch (e) { return ""; } }

var history = [];
try { history = JSON.parse(sessionStorage.getItem("kz_ai_hist") || "[]"); } catch (e) {}
function saveHist() { try { sessionStorage.setItem("kz_ai_hist", JSON.stringify(history.slice(-20))); } catch (e) {} }

/* ---------- ответ: сервер (ИИ → сценарий на сервере) → при сбое локальный сценарий ---------- */
function localAnswer(text, reason) {
  return loadScenario().then(function (sc) { var r = scriptedReply(text, sc); r.source = "script"; r.reason = reason; return r; });
}
function ask(text) {
  var b = brk();
  if (!CFG.aiEndpoint) return localAnswer(text, "no_endpoint");
  if (/^intent:/.test(text)) return localAnswer(text, "menu_button");
  if (b.isOpen()) return localAnswer(text, "client_breaker_open");
  var ctrl = window.AbortController ? new AbortController() : null;
  var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, CFG.timeoutMs);
  var msgs = history.filter(function (m) { return !/^intent:/.test(m.content); }).slice(-9).concat([{ role: "user", content: text }]);
  return fetch(CFG.aiEndpoint.replace(/\/+$/, "") + "/chat", {
    method: "POST", headers: { "Content-Type": "application/json" }, signal: ctrl ? ctrl.signal : undefined,
    body: JSON.stringify({ messages: msgs, page: location.pathname, mode: "auto", site: CFG.site })
  }).then(function (r) { if (!r.ok) throw new Error("http_" + r.status); return r.json(); })
    .then(function (j) {
      clearTimeout(timer);
      if (!j || typeof j.reply !== "string" || !j.reply.trim()) throw new Error("empty");
      b.success(); brkSave(b);
      return j;
    })
    .catch(function (e) { clearTimeout(timer); b.failure(); brkSave(b); return localAnswer(text, "server_" + ((e && e.message) || "error")); });
}

/* ---------- UI ---------- */
var css = ".kzai-btn{position:fixed;right:18px;bottom:18px;z-index:90;display:flex;align-items:center;gap:8px;border:0;border-radius:999px;padding:12px 16px 12px 14px;background:var(--accent,#c8553d);color:#fff;font:600 15px/1.2 var(--sans,system-ui,sans-serif);box-shadow:0 8px 24px rgba(0,0,0,.18);cursor:pointer}" +
".kzai-btn:hover{background:var(--accent-d,#a8412c)}.kzai-btn i{font-style:normal;font-size:20px;line-height:1}" +
".kzai-btn.kzai-up{bottom:84px}" +
"@media(max-width:600px){.kzai-btn span{display:none}.kzai-btn{padding:14px;right:14px}}" +
".kzai-panel{position:fixed;right:18px;bottom:18px;z-index:95;width:380px;max-width:calc(100vw - 24px);height:560px;max-height:calc(100vh - 36px);display:none;flex-direction:column;background:var(--card,#fff);color:var(--ink,#2b2420);border:1px solid var(--line,#e8dccd);border-radius:18px;box-shadow:0 18px 50px rgba(0,0,0,.22);overflow:hidden;font:15px/1.5 var(--sans,system-ui,sans-serif)}" +
".kzai-panel.open{display:flex}@media(max-width:600px){.kzai-panel{right:6px;left:6px;bottom:6px;width:auto;max-width:none;height:82vh}}" +
".kzai-h{display:flex;align-items:center;gap:10px;padding:12px 14px;background:var(--bg2,#f4ebdf);border-bottom:1px solid var(--line,#e8dccd)}" +
".kzai-h b{display:block;font-size:15px}.kzai-h small{color:var(--muted,#6d625a);font-size:12px}.kzai-x{margin-left:auto;border:0;background:none;font-size:22px;cursor:pointer;color:inherit;line-height:1}" +
".kzai-log{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px;background:var(--bg,#fbf6ef)}" +
".kzai-m{max-width:88%;padding:9px 12px;border-radius:14px;white-space:pre-wrap;word-wrap:break-word}" +
".kzai-u{align-self:flex-end;background:var(--accent,#c8553d);color:#fff;border-bottom-right-radius:4px}" +
".kzai-b{align-self:flex-start;background:var(--card,#fff);border:1px solid var(--line,#e8dccd);border-bottom-left-radius:4px}" +
".kzai-src{display:block;font-size:11px;color:var(--muted,#6d625a);margin-top:4px}" +
".kzai-sg{display:flex;flex-wrap:wrap;gap:6px;align-self:flex-start;max-width:95%}" +
".kzai-sg a,.kzai-sg button{display:inline-block;border:1px solid var(--accent,#c8553d);color:var(--accent-d,#a8412c);background:var(--card,#fff);border-radius:999px;padding:6px 11px;font:600 13px/1.3 inherit;text-decoration:none;cursor:pointer}" +
".kzai-sg a:hover,.kzai-sg button:hover{background:var(--accent-l,#f6c9b8)}" +
".kzai-f{display:flex;gap:6px;padding:10px;border-top:1px solid var(--line,#e8dccd);background:var(--card,#fff)}" +
".kzai-f textarea{flex:1;resize:none;height:42px;line-height:1.35;overflow-y:auto;border:1px solid var(--line,#e8dccd);border-radius:12px;padding:10px;font:inherit;color:inherit;background:var(--bg,#fbf6ef)}" +
".kzai-f button{border:0;border-radius:12px;padding:0 14px;background:var(--accent,#c8553d);color:#fff;font-weight:700;cursor:pointer}" +
".kzai-d{font-size:11px;color:var(--muted,#6d625a);padding:0 12px 8px;background:var(--card,#fff)}" +
".kzai-typing{opacity:.6;font-style:italic}";
var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);

var btn = document.createElement("button");
btn.className = "kzai-btn"; btn.type = "button"; btn.setAttribute("aria-label", "Открыть помощника");
btn.innerHTML = "<i aria-hidden=\"true\">💬</i><span>Подобрать программу</span>";
var panel = document.createElement("div");
panel.className = "kzai-panel"; panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", CFG.title);
panel.innerHTML = "<div class=\"kzai-h\"><div><b></b><small></small></div><button class=\"kzai-x\" type=\"button\" aria-label=\"Закрыть\">×</button></div>" +
  "<div class=\"kzai-log\" aria-live=\"polite\"></div><form class=\"kzai-f\"><textarea placeholder=\"Напишите, что вас беспокоит…\" aria-label=\"Сообщение\"></textarea><button type=\"submit\">➤</button></form><div class=\"kzai-d\"></div>";
panel.querySelector("b").textContent = CFG.title;
panel.querySelector("small").textContent = CFG.subtitle;
document.body.appendChild(btn); document.body.appendChild(panel);
var log_ = panel.querySelector(".kzai-log"), ta = panel.querySelector("textarea"), form = panel.querySelector("form");
function placeBtn() { var m = document.querySelector(".mcta"); btn.classList.toggle("kzai-up", !!(m && getComputedStyle(m).display !== "none")); }
placeBtn(); window.addEventListener("resize", placeBtn);

function addUser(t) { var d = document.createElement("div"); d.className = "kzai-m kzai-u"; d.textContent = t; log_.appendChild(d); log_.scrollTop = 1e6; }
function addBot(r) {
  var d = document.createElement("div"); d.className = "kzai-m kzai-b"; d.textContent = r.reply;
  var s = document.createElement("span"); s.className = "kzai-src"; s.textContent = LABEL[r.source] || LABEL.script; d.appendChild(s);
  log_.appendChild(d);
  var sg = (r.suggestions || []).filter(function (x) { return x && x.label; });
  if (sg.length) {
    var w = document.createElement("div"); w.className = "kzai-sg";
    sg.forEach(function (x) {
      var el;
      if (x.url) {
        el = document.createElement("a"); var u = x.url;
        if (/^https:\/\/t\.me\/MarinaNew\?text=/.test(u)) u += encodeURIComponent(utmNote());
        el.href = u;
        if (!u.startsWith(location.origin)) { el.target = "_blank"; el.rel = "noopener"; }
        el.addEventListener("click", function () { goal(/t\.me/.test(u) ? "ai_tg_click" : "ai_link", { url: x.url }); });
      } else if (x.cmd) {
        el = document.createElement("button"); el.type = "button";
        el.addEventListener("click", function () { send(x.cmd, x.label); });
      } else return;
      el.textContent = x.label; w.appendChild(el);
    });
    log_.appendChild(w);
  }
  log_.scrollTop = 1e6;
}
var busy = false;
function send(text, shown) {
  text = String(text || "").trim(); if (!text || busy) return;
  busy = true; addUser(shown || text);
  var t = document.createElement("div"); t.className = "kzai-m kzai-b kzai-typing"; t.textContent = "Печатает…"; log_.appendChild(t); log_.scrollTop = 1e6;
  ask(text).then(function (r) {
    t.remove(); addBot(r);
    history.push({ role: "user", content: text, shown: shown || "" }); history.push({ role: "assistant", content: r.reply, source: r.source, suggestions: r.suggestions || [] }); saveHist();
    goal("ai_message", { source: r.source });
    try { console.info("[ai-widget]", r.source, r.reason || ""); } catch (e) {}
  }).then(function () { busy = false; }, function () { busy = false; t.remove(); });
}
var opened = false;
function open() {
  panel.classList.add("open"); btn.style.display = "none"; setTimeout(function () { ta.focus(); }, 50);
  if (opened) return; opened = true; goal("ai_open");
  loadScenario().then(function (sc) {
    panel.querySelector(".kzai-d").textContent = sc.disclaimer || "Помощник — не психолог и не врач. Если очень тяжело: 112; МЧС +7 (495) 989-50-50; детям и подросткам — 8-800-2000-122.";
    if (history.length) {
      history.forEach(function (m) { if (m.role === "user") addUser(m.shown || m.content); else addBot({ reply: m.content, source: m.source, suggestions: m.suggestions }); });
    } else {
      addBot({ reply: sc.menu.reply, source: "script", suggestions: resolveButtons(sc.menu.buttons, sc) });
    }
  });
}
btn.addEventListener("click", open);
panel.querySelector(".kzai-x").addEventListener("click", function () { panel.classList.remove("open"); btn.style.display = ""; });
form.addEventListener("submit", function (e) { e.preventDefault(); var v = ta.value; ta.value = ""; send(v); });
ta.addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event("submit")); } });
document.addEventListener("keydown", function (e) { if (e.key === "Escape" && panel.classList.contains("open")) panel.querySelector(".kzai-x").click(); });
if (/[?&]ai=open\b/.test(location.search)) open();
window.KZAI = { open: open, ask: ask };

})();
