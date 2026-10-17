/* Код счастливой жизни — логика сайта: цены/даты из config.js, UTM, кнопки «Купить» → окно записи → Telegram Марины, фильтры каталога. */
(function(){
  var C = window.SITE_CONFIG || {};
  var P = C.prices || {}, D = C.dates || {}, K = C.contacts || {};
  function val(map, code, group){ return (code && map[code]) || (group && map[group]) || ""; }
  function price(code, group){ return val(P, code, group) || C.defaultPrice || "Цена уточняется"; }
  function date(code, group){ return val(D, code, group) || C.defaultDate || "Дата уточняется"; }

  /* --- UTM: запоминаем, из какого ролика пришёл человек --- */
  var qs = new URLSearchParams(location.search), utm = {};
  ["utm_source","utm_medium","utm_campaign","utm_content","utm_term"].forEach(function(k){ if(qs.get(k)) utm[k]=qs.get(k); });
  try{
    if(Object.keys(utm).length){
      localStorage.setItem("ku_last_utm", JSON.stringify(utm));
      if(!localStorage.getItem("ku_first_utm")) localStorage.setItem("ku_first_utm", JSON.stringify(utm));
    } else { utm = JSON.parse(localStorage.getItem("ku_last_utm")||"{}"); }
  }catch(e){}
  function sourceTag(){
    var s = [utm.utm_source, utm.utm_campaign, utm.utm_content].filter(Boolean).join(" / ");
    return s ? " (источник: " + s + ")" : "";
  }

  /* --- Подстановка цен, дат, длительности --- */
  document.querySelectorAll("[data-price]").forEach(function(el){ el.textContent = price(el.dataset.price, el.dataset.group); });
  document.querySelectorAll("[data-date]").forEach(function(el){ el.textContent = date(el.dataset.date, el.dataset.group); });
  document.querySelectorAll("[data-duration]").forEach(function(el){ if(C.defaultTrainingDuration) el.textContent = C.defaultTrainingDuration; });
  document.querySelectorAll("[data-upgrade]").forEach(function(el){ if(C.upgradeNote) el.textContent = C.upgradeNote; });
  document.querySelectorAll("[data-link]").forEach(function(el){
    var u = K[el.dataset.link]; if(u){ el.href = u; el.classList.remove("hidden"); } else if(el.dataset.hideEmpty!==undefined){ el.classList.add("hidden"); }
  });
  ["marina","anna"].forEach(function(h){
    var ph = (C.photos||{})[h], bio = (C.bios||{})[h];
    document.querySelectorAll('[data-photo="'+h+'"]').forEach(function(el){
      if(ph){ var root = el.dataset.root||""; el.innerHTML = '<img src="'+root+ph+'" alt="" loading="lazy">'; }
    });
    document.querySelectorAll('[data-bio="'+h+'"]').forEach(function(el){ if(bio){ el.textContent = bio; el.classList.remove("hidden"); } });
  });
  if(C.showPsyTrainingWaitlist === false) document.querySelectorAll("[data-psy-waitlist]").forEach(function(el){ el.classList.add("hidden"); });

  /* --- Меню --- */
  var b = document.querySelector(".burger"), n = document.querySelector(".nav");
  if(b && n) b.addEventListener("click", function(){ n.classList.toggle("open"); b.setAttribute("aria-expanded", n.classList.contains("open")); });

  /* --- Кнопки «Купить»: сразу в Telegram Марины с готовым текстом --- */
  var TG = K.marinaTelegram || "https://t.me/MarinaNew";
  function realPrice(code, group){ return val(P, code, group); }
  function buildMsg(el){
    var head = el.dataset.head || "", tail = el.dataset.tail || "", pr = "";
    if(el.dataset.noprice === undefined){ var v = realPrice(el.dataset.cta, el.dataset.group); if(v) pr = " Цена на сайте: " + v + "."; }
    var src = [utm.utm_source, utm.utm_campaign, utm.utm_content].filter(Boolean).join(" / ");
    return (head + pr + (tail ? " " + tail : "")) + (src ? "\n(источник: " + src + ")" : "");
  }
  document.querySelectorAll("[data-cta]").forEach(function(el){
    el.href = TG + "?text=" + encodeURIComponent(buildMsg(el));
    el.target = "_blank"; el.rel = "noopener";
  });
  document.querySelectorAll("[data-pay]").forEach(function(el){
    var u = (C.paymentLinks||{})[el.dataset.pay]; if(u){ el.href = u; el.classList.remove("hidden"); }
  });
  var toast = document.getElementById("toast"), tt;
  function showToast(t){ if(!toast) return; toast.textContent = t; toast.classList.add("show"); clearTimeout(tt); tt = setTimeout(function(){ toast.classList.remove("show"); }, 6000); }
  function copyText(t, okEl){
    try{ if(navigator.clipboard) navigator.clipboard.writeText(t).then(function(){
      if(okEl) okEl.textContent = "Текст скопирован. Если в Telegram он не подставился — просто вставьте его в чат.";
      else showToast("Текст сообщения скопирован — если он не подставился, вставьте его в чат.");
    }, function(){}); }catch(err){}
  }

  /* --- Окно записи (модальное) --- */
  var modal = document.getElementById("cta-modal");
  function titleOf(el){ return el.dataset.title || (document.querySelector("h1")||{}).textContent || document.title; }
  function openModal(el){
    var code = el.dataset.cta, group = el.dataset.group, msg = buildMsg(el), url = TG + "?text=" + encodeURIComponent(msg);
    var head = el.dataset.head || "", m = head.match(/«[^»]+»(?:[^«.]*«[^»]+»)?/);
    modal.querySelector("[data-m-title]").textContent = el.dataset.title || (m ? m[0] : titleOf(el));
    modal.querySelector("[data-m-price]").textContent = price(code, group);
    modal.querySelector("[data-m-date]").textContent = date(code, group);
    modal.querySelector("[data-m-msg]").textContent = msg;
    var tg = modal.querySelector("[data-m-tg]"); tg.href = url;
    var pay = modal.querySelector("[data-m-pay]"), pl = (C.paymentLinks||{})[code];
    if(pl){ pay.href = pl; pay.classList.remove("hidden"); } else pay.classList.add("hidden");
    modal.querySelector("[data-m-paynote]").textContent = pl ? "Можно оплатить онлайн или написать Марине." : "Напишите нам — пришлём детали для оплаты.";
    modal.querySelector(".ok").textContent = "";
    modal.dataset.msg = msg;
    modal.classList.add("open");
    tg.focus();
    try{ if(window.ym && C.yandexMetrikaId) ym(+C.yandexMetrikaId, "reachGoal", "cta_click", {product: code}); }catch(err){}
  }
  function closeModal(){ if(modal) modal.classList.remove("open"); }
  document.addEventListener("click", function(e){
    var el = e.target.closest("[data-cta]");
    if(el){
      if(modal){ e.preventDefault(); openModal(el); }
      else { el.href = TG + "?text=" + encodeURIComponent(buildMsg(el)); copyText(buildMsg(el)); }
      return;
    }
    if(!modal) return;
    if(e.target === modal || e.target.closest(".mclose")){ closeModal(); return; }
    if(e.target.closest("[data-m-tg]")){
      copyText(modal.dataset.msg, modal.querySelector(".ok"));
      try{ if(window.ym && C.yandexMetrikaId) ym(+C.yandexMetrikaId, "reachGoal", "tg_click"); }catch(err){}
    }
    if(e.target.closest("[data-m-copy]")) copyText(modal.dataset.msg, modal.querySelector(".ok"));
  });
  document.addEventListener("keydown", function(e){ if(e.key === "Escape") closeModal(); });

  /* --- Фильтры каталога --- */
  var cat = document.getElementById("catalog");
  if(cat){
    var state = {topic: qs.get("tema") || "all", format: qs.get("format") || "all"};
    function apply(){
      var shown = 0;
      cat.querySelectorAll("[data-topics]").forEach(function(c){
        var okT = state.topic==="all" || c.dataset.topics.split(" ").indexOf(state.topic)>-1;
        var okF = state.format==="all" || c.dataset.format===state.format;
        c.classList.toggle("hidden", !(okT&&okF)); if(okT&&okF) shown++;
      });
      document.querySelectorAll("[data-filter]").forEach(function(btn){
        btn.classList.toggle("on", state[btn.dataset.filter]===btn.dataset.value);
      });
      var e = document.getElementById("empty"); if(e) e.classList.toggle("hidden", shown>0);
    }
    document.querySelectorAll("[data-filter]").forEach(function(btn){
      btn.addEventListener("click", function(){
        state[btn.dataset.filter] = btn.dataset.value; apply();
        var u = new URL(location.href);
        u.searchParams.set("tema", state.topic); u.searchParams.set("format", state.format);
        history.replaceState(null, "", u);
      });
    });
    apply();
  }

  /* --- Яндекс.Метрика (если указан номер) --- */
  if(C.yandexMetrikaId){
    (function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};m[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");
    ym(+C.yandexMetrikaId, "init", {clickmap:true, trackLinks:true, accurateTrackBounce:true, webvisor:true});
  }
})();
