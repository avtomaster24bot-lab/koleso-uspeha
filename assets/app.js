/* Колесо успеха — логика сайта: цены/даты из config.js, UTM, окно записи, фильтры каталога. */
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

  /* --- Окно записи --- */
  var modal = document.getElementById("cta-modal");
  function openCta(code, group, title){
    if(!modal) return;
    var msg = "Здравствуйте! Хочу записаться: «" + title + "»." + sourceTag();
    modal.querySelector("[data-m-title]").textContent = title;
    modal.querySelector("[data-m-price]").textContent = price(code, group);
    modal.querySelector("[data-m-date]").textContent = date(code, group);
    modal.querySelector("[data-m-msg]").textContent = msg;
    var pay = modal.querySelector("[data-m-pay]"), pl = (C.paymentLinks||{})[code];
    if(pl){ pay.href = pl; pay.classList.remove("hidden"); } else pay.classList.add("hidden");
    modal.querySelector("[data-m-paynote]").textContent = pl ? "" : (C.paymentNote||"");
    var links = {marinaTelegram:"[data-m-marina]", annaTelegram:"[data-m-anna]", whatsapp:"[data-m-wa]", formUrl:"[data-m-form]"};
    Object.keys(links).forEach(function(k){
      var el = modal.querySelector(links[k]); if(!el) return;
      var u = K[k];
      if(u){
        if(k==="whatsapp") u += (u.indexOf("?")>-1?"&":"?") + "text=" + encodeURIComponent(msg);
        el.href = u; el.classList.remove("hidden");
      } else el.classList.add("hidden");
    });
    var em = modal.querySelector("[data-m-email]");
    if(K.email){ em.href = "mailto:"+K.email+"?subject="+encodeURIComponent("Запись: "+title)+"&body="+encodeURIComponent(msg); em.classList.remove("hidden"); } else em.classList.add("hidden");
    modal.querySelector(".ok").textContent = "";
    modal.classList.add("open"); modal.dataset.msg = msg;
    try{ if(window.ym && C.yandexMetrikaId) ym(+C.yandexMetrikaId, "reachGoal", "cta_click", {product: code}); }catch(e){}
  }
  function copyMsg(){
    var t = modal.dataset.msg || "";
    var done = function(){ modal.querySelector(".ok").textContent = "Текст скопирован — вставьте его в сообщение."; };
    if(navigator.clipboard) navigator.clipboard.writeText(t).then(done, function(){});
  }
  document.addEventListener("click", function(e){
    var t = e.target.closest("[data-cta]");
    if(t){ e.preventDefault(); openCta(t.dataset.cta, t.dataset.group, t.dataset.title || document.title); return; }
    if(modal && (e.target === modal || e.target.closest(".mclose"))) modal.classList.remove("open");
    if(e.target.closest("[data-m-copy]")) copyMsg();
    if(e.target.closest("[data-m-marina],[data-m-anna]")) copyMsg();
  });
  document.addEventListener("keydown", function(e){ if(e.key==="Escape" && modal) modal.classList.remove("open"); });

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
