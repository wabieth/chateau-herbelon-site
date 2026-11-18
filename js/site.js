/* Château d'Herbelon — navigation entre les vues, langue, calendrier, estimateur, formulaire */
(function () {
  "use strict";

  var VIEWS = ["accueil", "seminaires", "ete", "restaurant", "mariages", "proches", "retraites", "chateau", "contact"];
  var views = Array.prototype.slice.call(document.querySelectorAll(".view"));
  var navLinks = Array.prototype.slice.call(document.querySelectorAll("[data-nav]"));
  var nav = document.getElementById("nav");
  var burger = document.getElementById("burger");
  var lang = "fr";
  var pendingTopic = null;
  var firstLoad = true;

  /* ---------- Vues ---------- */
  function currentView() {
    var h = (location.hash || "").replace("#", "");
    return VIEWS.indexOf(h) >= 0 ? h : "accueil";
  }

  function show() {
    var name = currentView();
    views.forEach(function (v) { v.hidden = v.getAttribute("data-view") !== name; });
    navLinks.forEach(function (a) {
      if (a.getAttribute("data-nav") === name) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
    nav.classList.remove("open");
    burger.setAttribute("aria-expanded", "false");
    if (name === "contact" && pendingTopic) {
      document.getElementById("f-topic").value = pendingTopic;
      pendingTopic = null;
    }
    if (!firstLoad) {
      window.scrollTo(0, 0);
      var h1 = document.querySelector('.view[data-view="' + name + '"] h1');
      if (h1) { try { h1.focus({ preventScroll: true }); } catch (e) {} }
    }
    firstLoad = false;
  }

  document.addEventListener("click", function (e) {
    var a = e.target.closest ? e.target.closest("a[data-topic]") : null;
    if (a) pendingTopic = a.getAttribute("data-topic");
  });
  window.addEventListener("hashchange", show);

  burger.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    burger.setAttribute("aria-expanded", open ? "true" : "false");
  });

  /* ---------- Langue ---------- */
  var i18n = Array.prototype.slice.call(document.querySelectorAll("[data-en]"));
  i18n.forEach(function (el) { el.setAttribute("data-fr", el.innerHTML); });
  var langButtons = Array.prototype.slice.call(document.querySelectorAll("[data-lang]"));

  function setLang(l) {
    lang = l === "en" ? "en" : "fr";
    i18n.forEach(function (el) { el.innerHTML = el.getAttribute(lang === "en" ? "data-en" : "data-fr"); });
    document.documentElement.lang = lang;
    langButtons.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-lang") === lang ? "true" : "false"); });
    try { localStorage.setItem("herbelon-lang", lang); } catch (e) {}
    estimate();
    var status = document.getElementById("form-status");
    if (!status.hidden) status.textContent = statusText();
  }
  langButtons.forEach(function (b) { b.addEventListener("click", function () { setLang(b.getAttribute("data-lang")); }); });

  /* ---------- Calendrier : mois en cours ---------- */
  var months = document.querySelectorAll("#year .m");
  var idx = (new Date().getMonth() + 4) % 12; /* l'année du château commence en septembre */
  if (months[idx]) months[idx].classList.add("now");

  /* ---------- Estimateur séminaire ---------- */
  var PRICE = { day: 85, res: 210 }; /* prix « à partir de », HT par personne (grille tarifaire du 18 nov. 2026) */
  var ePeople = document.getElementById("e-people");
  var eDays = document.getElementById("e-days");

  function money(n) {
    return n.toLocaleString(lang === "en" ? "en-GB" : "fr-FR");
  }

  function estimate() {
    var people = parseInt(ePeople.value, 10);
    var n = parseInt(eDays.value, 10);
    var res = document.getElementById("e-format-res").checked;
    var unit = res ? PRICE.res : PRICE.day;
    var total = people * n * unit;
    var fr = lang !== "en";
    var lengthLabel = res
      ? (fr ? n + (n > 1 ? " nuits" : " nuit") : n + (n > 1 ? " nights" : " night"))
      : (fr ? n + (n > 1 ? " jours" : " jour") : n + (n > 1 ? " days" : " day"));
    document.getElementById("e-people-out").textContent = people;
    document.getElementById("e-days-out").textContent = lengthLabel;
    document.getElementById("e-sum").textContent = fr ? money(total) + "\u00a0€\u00a0HT" : "€" + money(total) + " excl. VAT";
    document.getElementById("e-detail").textContent = fr
      ? people + " personnes × " + lengthLabel + " × " + unit + "\u00a0€\u00a0HT"
      : people + " people × " + lengthLabel + " × €" + unit + " excl. VAT";
  }
  document.getElementById("estim").addEventListener("input", estimate);
  document.getElementById("estim").addEventListener("submit", function (e) { e.preventDefault(); });

  /* ---------- Formulaire (maquette : rien n'est envoyé) ---------- */
  function statusText() {
    return lang === "en"
      ? "Prototype: this form doesn’t send anything yet. Once live, your request will reach contact@chateaudherbelon.com. Until then, email or call us directly."
      : "Maquette\u00a0: ce formulaire n’envoie encore rien. Une fois en ligne, votre demande arrivera à contact@chateaudherbelon.com. D’ici là, écrivez-nous ou appelez-nous directement.";
  }
  document.getElementById("contact-form").addEventListener("submit", function (e) {
    e.preventDefault();
    var status = document.getElementById("form-status");
    status.textContent = statusText();
    status.hidden = false;
  });



  /* ---------- Saison : ce que l'accueil met en avant ----------
     De septembre à juin : devis et événementiel. En juillet-août : réservation de chambre et l'été en premier.
     Le bandeau de maquette permet de prévisualiser les deux. */
  var seasonButtons = Array.prototype.slice.call(document.querySelectorAll("[data-season-btn]"));
  var seasonal = Array.prototype.slice.call(document.querySelectorAll("[data-season]"));
  function setSeason(s) {
    var summer = s === "summer";
    document.documentElement.classList.toggle("is-summer", summer);
    seasonal.forEach(function (el) { el.hidden = el.getAttribute("data-season") !== (summer ? "summer" : "off"); });
    seasonButtons.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-season-btn") === s ? "true" : "false"); });
  }
  seasonButtons.forEach(function (b) { b.addEventListener("click", function () { setSeason(b.getAttribute("data-season-btn")); }); });
  var m = new Date().getMonth();
  setSeason(m === 6 || m === 7 ? "summer" : "off");

  /* ---------- Démarrage ---------- */

  /* Vidéo d’accueil : poster d’abord ; pas de vidéo si l’on a demandé moins d’animations ou d’économiser les données */
  var vid = document.querySelector(".hero-video");
  if (vid) {
    var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var saveData = navigator.connection && navigator.connection.saveData;
    if (!calm && !saveData) {
      vid.src = window.innerWidth < 760 ? vid.getAttribute("data-src-mobile") : vid.getAttribute("data-src");
      vid.muted = true;
      var pauseBtn = document.querySelector(".hero-pause");
      var p = vid.play();
      if (p && p.catch) p.catch(function () {});
      vid.addEventListener("playing", function () { pauseBtn.hidden = false; }, { once: true });
      pauseBtn.addEventListener("click", function () {
        var paused = pauseBtn.getAttribute("aria-pressed") === "true";
        if (paused) { vid.play(); } else { vid.pause(); }
        pauseBtn.setAttribute("aria-pressed", paused ? "false" : "true");
      });
    }
  }

  /* Restaurant : la vidéo de la salle à la terrasse se lance une fois, quand on arrive dessus, et s’arrête sur le lac */
  var walk = document.querySelector(".walk-video");
  if (walk) {
    var calmW = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var saveW = navigator.connection && navigator.connection.saveData;
    if (calmW || saveW || !("IntersectionObserver" in window)) {
      walk.poster = walk.getAttribute("data-poster-end");
    } else {
      walk.src = window.innerWidth < 760 ? walk.getAttribute("data-src-mobile") : walk.getAttribute("data-src");
      walk.muted = true;
      new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (e) {
          if (e.isIntersecting && e.intersectionRatio > 0.5) {
            var pr = walk.play(); if (pr && pr.catch) pr.catch(function () { walk.poster = walk.getAttribute("data-poster-end"); });
            obs.disconnect();
          }
        });
      }, { threshold: [0, 0.5, 1] }).observe(walk);
    }
  }
  var saved = null;
  try { saved = localStorage.getItem("herbelon-lang"); } catch (e) {}
  show();
  if (saved === "en") setLang("en"); else estimate();
})();
