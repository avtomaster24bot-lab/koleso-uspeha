/* Код счастливой жизни — плеер «Послушать»: перемотка, скорость, «Дальше послушать», автопродолжение. */
(function(){
  var boxes = [].slice.call(document.querySelectorAll("[data-audio]")); if(!boxes.length) return;
  var C = window.SITE_CONFIG || {}, cur = null, auto = false;
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  function $(s, r){ return (r||document).querySelector(s); }
  function $$(s, r){ return [].slice.call((r||document).querySelectorAll(s)); }
  function goal(g, p){ try{ if(window.ym && C.yandexMetrikaId) ym(+C.yandexMetrikaId, "reachGoal", g, p); }catch(e){} }
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){ return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); }
  var toastEl = document.getElementById("toast"), tt;
  function toast(t){ if(!toastEl) return; toastEl.textContent = t; toastEl.classList.add("show"); clearTimeout(tt); tt = setTimeout(function(){ toastEl.classList.remove("show"); }, 4000); }
  function fmt(s){ s = Math.floor(s||0); return Math.floor(s/60) + ":" + ("0" + s%60).slice(-2); }
  boxes.forEach(function(box, idx){
    var a = $("audio", box), bar = $(".aud-bar", box), fill = $(".aud-bar i", box), t = $("[data-cur]", box), rb = $("[data-rate]", box);
    var rates = [1, 1.25, 1.5, 0.85], ri = 0, curId = box.dataset.audio;
    var nb = $("[data-next]", box), queue = [], pos = 0;
    try { if(nb) queue = JSON.parse(nb.dataset.next); } catch(e){}
    var autoBox = $("[data-autonext]", box);
    box.classList.add("js"); a.removeAttribute("controls");
    function play(){ if(cur && cur !== a) cur.pause(); cur = a; a.playbackRate = rates[ri]; var p = a.play(); if(p && p.catch) p.catch(function(){}); }
    function load(item){
      curId = item.id; a.src = item.src; fill.style.width = "0%"; t.textContent = "0:00";
      $(".aud-t", box).innerHTML = '<a href="' + esc(item.u) + '">' + esc(item.t) + '</a>';
      $$("[data-dur]", box).forEach(function(d){ d.textContent = item.d; });
      $(".aud-dl", box).href = item.src; play(); goal("audio_next", {id: item.id});
    }
    $(".aud-play", box).addEventListener("click", function(){ if(a.paused){ play(); } else { a.pause(); auto = false; } });
    a.addEventListener("play", function(){ box.classList.add("playing"); goal("audio_play", {id: curId}); });
    a.addEventListener("pause", function(){ box.classList.remove("playing"); });
    a.addEventListener("timeupdate", function(){
      var p = a.duration ? a.currentTime / a.duration * 100 : 0; fill.style.width = p + "%"; bar.setAttribute("aria-valuenow", Math.round(p)); t.textContent = fmt(a.currentTime);
    });
    a.addEventListener("ended", function(){
      box.classList.remove("playing");
      if(auto && boxes[idx+1]){ var n = boxes[idx+1]; n.scrollIntoView({behavior: reduce ? "auto" : "smooth", block: "center"}); $(".aud-play", n).click(); return; }
      if(queue[pos] && autoBox && autoBox.checked){ toast("Дальше: " + queue[pos].t); var it = queue[pos++]; setTimeout(function(){ load(it); }, 1500); }
    });
    $$("[data-nextplay]", box).forEach(function(b){ b.addEventListener("click", function(){ var k = +b.dataset.nextplay; pos = k + 1; load(queue[k]); }); });
    function seek(x){ var r = bar.getBoundingClientRect(); var go = function(){ a.currentTime = Math.max(0, Math.min(1, (x - r.left) / r.width)) * a.duration; }; if(a.duration) go(); else { a.addEventListener("loadedmetadata", go, {once:true}); a.load(); } }
    bar.addEventListener("click", function(ev){ seek(ev.clientX); });
    bar.addEventListener("keydown", function(ev){ if(ev.key === "ArrowRight") a.currentTime += 10; if(ev.key === "ArrowLeft") a.currentTime -= 10; });
    rb.addEventListener("click", function(){ ri = (ri + 1) % rates.length; a.playbackRate = rates[ri]; rb.textContent = rates[ri] + "×"; });
  });
  $$("[data-playall]").forEach(function(b){ b.addEventListener("click", function(ev){ ev.preventDefault(); auto = true; $(".aud-play", boxes[0]).click(); }); });
})();
