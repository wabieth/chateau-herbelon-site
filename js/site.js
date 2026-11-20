/* Château d'Herbelon — navigation entre les vues, langue, calendrier, estimateur, formulaire */
(function () {
  "use strict";

  var VIEWS = ["accueil", "seminaires", "ete", "restaurant", "mariages", "proches", "retraites", "chateau", "contact", "mentions", "confidentialite"];
  var views = Array.prototype.slice.call(document.querySelectorAll(".view"));
  var navLinks = Array.prototype.slice.call(document.querySelectorAll("[data-nav]"));
  var nav = document.getElementById("nav");
  var burger = document.getElementById("burger");
  var navTop = document.querySelector(".nav-top");
  var lang = document.documentElement.lang === "en" ? "en" : "fr";
  var pendingTopic = null;
  var firstLoad = true;

  /* ---------- Vues ---------- */
  /* Chaque vue a sa propre page (/seminaires/, /mariages/…) : la page dit laquelle elle affiche.
     Les anciens liens en « #seminaires » renvoient vers la bonne adresse. */
  var SLUGS = { accueil: "", seminaires: "seminaires", ete: "ete", restaurant: "restaurant", mariages: "mariages", proches: "entre-proches", retraites: "retraites", chateau: "le-chateau", contact: "contact", mentions: "mentions-legales", confidentialite: "confidentialite" };
  var ROOT = document.documentElement.getAttribute("data-root") || "./";
  var legacy = (location.hash || "").replace("#", "");
  if (VIEWS.indexOf(legacy) >= 0 && document.documentElement.getAttribute("data-page") && document.documentElement.lang !== "en") {
    location.replace(ROOT + (SLUGS[legacy] ? SLUGS[legacy] + "/" : ""));
    return;
  }
  function currentView() {
    var p = document.documentElement.getAttribute("data-page");
    if (p) return p;
    var h = (location.hash || "").replace("#", "");
    return VIEWS.indexOf(h) >= 0 ? h : "accueil";
  }
  try {
    var sujet = new URLSearchParams(location.search).get("sujet");
    if (sujet) pendingTopic = sujet;
  } catch (e) {}

  function show() {
    var name = currentView();
    views.forEach(function (v) { v.hidden = v.getAttribute("data-view") !== name; });
    navLinks.forEach(function (a) {
      if (a.getAttribute("data-nav") === name) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
    nav.classList.remove("open");
    burger.setAttribute("aria-expanded", "false");
    if (navTop) {
      navTop.setAttribute("aria-expanded", "false");
      navTop.classList.toggle("is-current", ["seminaires", "mariages", "proches", "retraites"].indexOf(name) >= 0);
    }
    if (name === "contact" && pendingTopic && document.getElementById("f-topic")) {
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
  window.addEventListener("hashchange", function () {
    /* une ancre interne (#reserver…) ne change pas de vue */
    var h = (location.hash || "").replace("#", "");
    if (h && VIEWS.indexOf(h) < 0) return;
    show();
  });

  /* Menu « Privatiser » : s’ouvre au survol, au clic et au clavier ; se ferme avec Échap ou en cliquant ailleurs */
  if (navTop) {
    navTop.addEventListener("click", function () {
      if (window.matchMedia("(max-width: 1020px)").matches) return;
      navTop.setAttribute("aria-expanded", navTop.getAttribute("aria-expanded") === "true" ? "false" : "true");
    });
    document.addEventListener("click", function (e) {
      if (!e.target.closest || !e.target.closest(".nav-group")) navTop.setAttribute("aria-expanded", "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && navTop.getAttribute("aria-expanded") === "true") { navTop.setAttribute("aria-expanded", "false"); navTop.focus(); }
    });
  }

  burger.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    burger.setAttribute("aria-expanded", open ? "true" : "false");
  });

  /* ---------- Langue ----------
     Chaque langue a ses propres pages (/ et /en/) : la page dit sa langue. */
  lang = document.documentElement.lang === "en" ? "en" : "fr";

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
    if (!ePeople || !eDays) return;
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
    document.getElementById("e-sum").innerHTML = fr ? money(total) + "\u00a0€\u00a0HT" : "€" + money(total) + '<span class="estim-tax"> excl. VAT</span>';
    document.getElementById("e-detail").textContent = fr
      ? people + " personnes × " + lengthLabel + " × " + unit + "\u00a0€\u00a0HT"
      : people + " people × " + lengthLabel + " × €" + unit + " excl. VAT";
  }
  var estimForm = document.getElementById("estim");
  if (estimForm) {
    estimForm.addEventListener("input", estimate);
    document.getElementById("e-format-day").addEventListener("change", function () { eDays.value = 1; estimate(); });
    estimForm.addEventListener("submit", function (e) { e.preventDefault(); });
  }

  /* ---------- Formulaire de contact ----------
     Envoi par Web3Forms (https://web3forms.com) vers la boîte du château.
     Tant que la clé n'est pas renseignée, le formulaire affiche un message de maquette. */
  var FORM_KEY = "e7947d3a-2034-48ed-9929-26dc29805e78";
  var form = document.getElementById("contact-form");
  var formState = "idle";
  var MSG = {
    proto: ["Maquette\u00a0: ce formulaire n’envoie encore rien. Écrivez-nous à contact@chateaudherbelon.com ou appelez le 04\u00a058\u00a000\u00a088\u00a095.", "Prototype: this form doesn’t send anything yet. Email contact@chateaudherbelon.com or call +33 4 58 00 88 95."],
    missing: ["Indiquez votre nom et une adresse e-mail valide pour que nous puissions vous répondre.", "Please give your name and a valid email address so we can reply."],
    sending: ["Envoi en cours…", "Sending…"],
    ok: ["Merci, votre demande est bien partie. Nous vous répondons sous 48\u00a0heures.", "Thank you, your request has been sent. We’ll reply within 48 hours."],
    error: ["L’envoi n’a pas abouti. Réessayez, ou écrivez-nous à contact@chateaudherbelon.com.", "Your request couldn’t be sent. Please try again, or email contact@chateaudherbelon.com."]
  };
  function statusText() { return (MSG[formState] || MSG.proto)[lang === "en" ? 1 : 0]; }
  function setStatus(st) {
    formState = st;
    var status = document.getElementById("form-status");
    status.textContent = statusText();
    status.hidden = false;
    status.classList.toggle("is-error", st === "missing" || st === "error");
  }
  if (form) form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!FORM_KEY) { setStatus("proto"); return; }
    var name = form.elements.name.value.trim(), email = form.elements.email.value.trim();
    if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { setStatus("missing"); return; }
    if (form.elements.botcheck.checked) return;
    var topic = form.elements.topic.options[form.elements.topic.selectedIndex].text;
    var data = {
      access_key: FORM_KEY,
      subject: "Site : demande « " + topic + " » de " + name,
      from_name: "Site du Château d’Herbelon",
      replyto: email,
      "Vous venez pour": topic,
      "Dates envisagées": form.elements.dates.value,
      "Nombre de personnes": form.elements.people.value,
      "Nom": name,
      "E-mail": email,
      "Téléphone": form.elements.phone.value,
      "Message": form.elements.message.value,
      "Langue": lang
    };
    var btn = form.querySelector("button[type=submit]");
    btn.disabled = true; setStatus("sending");
    fetch("https://api.web3forms.com/submit", { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(data) })
      .then(function (r) { return r.json(); })
      .then(function (j) { if (j && j.success) { form.reset(); setStatus("ok"); } else { setStatus("error"); } })
      .catch(function () { setStatus("error"); })
      .then(function () { btn.disabled = false; });
  });



  /* ---------- Saison : ce que l'accueil met en avant ----------
     De septembre à juin : devis et événementiel. En juillet-août : réservation de chambre et l'été en premier. */
  var seasonButtons = Array.prototype.slice.call(document.querySelectorAll("[data-season-btn]"));
  var seasonal = Array.prototype.slice.call(document.querySelectorAll("[data-season]"));
  /* Septembre à mai : événementiel. Juin : l'été passe en avant pour qu'on réserve (le restaurant ouvre le 1er juillet).
     Juillet-août : l'été, restaurant ouvert. */
  function setSeason(s) {
    var summer = s === "summer" || s === "june";
    document.documentElement.classList.toggle("is-summer", summer);
    document.documentElement.classList.toggle("is-june", s === "june");
    seasonal.forEach(function (el) { el.hidden = el.getAttribute("data-season") !== (summer ? "summer" : "off"); });
    seasonButtons.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-season-btn") === s ? "true" : "false"); });
  }
  seasonButtons.forEach(function (b) { b.addEventListener("click", function () { setSeason(b.getAttribute("data-season-btn")); }); });
  var m = new Date().getMonth();
  setSeason(m === 5 ? "june" : (m === 6 || m === 7) ? "summer" : "off");

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

  /* Vidéos en boucle (restaurant, retraites…) : lecture quand elles sont à l’écran, pause ailleurs, bouton pause */
  var calmL = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var saveL = navigator.connection && navigator.connection.saveData;
  var loopIO = (!calmL && !saveL && "IntersectionObserver" in window) ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var v = e.target;
      if (e.isIntersecting && e.intersectionRatio >= 0.25) { if (!v._userPaused) v._play(); }
      else if (!v.paused) { v.pause(); }
    });
  }, { threshold: [0, 0.25, 0.5] }) : null;
  Array.prototype.forEach.call(document.querySelectorAll(".loop-video"), function (v) {
    var btn = v.parentNode.querySelector(".loop-pause");
    var loaded = false;
    var setPaused = function (p) { if (btn) { btn.hidden = false; btn.setAttribute("aria-pressed", p ? "true" : "false"); } };
    v._userPaused = false;
    v._play = function () {
      if (!loaded) {
        loaded = true;
        var mob = v.getAttribute("data-src-mobile");
        v.src = (mob && window.innerWidth < 760) ? mob : v.getAttribute("data-src");
        v.muted = true;
      }
      var pr = v.play();
      if (pr && pr.catch) pr.catch(function () { v._userPaused = true; setPaused(true); });
    };
    v.addEventListener("playing", function () { setPaused(false); });
    if (btn) btn.addEventListener("click", function () {
      if (v.paused) { v._userPaused = false; v._play(); }
      else { v._userPaused = true; v.pause(); setPaused(true); }
    });
    if (loopIO) loopIO.observe(v);
    else { v._userPaused = true; setPaused(true); }
  });
  /* Réservation des chambres : widget Sirvoy, chargé seulement sur la page L’été, dans la langue choisie */
  var sirvoyBox = document.getElementById("sirvoy-box");
  var sirvoyLang = null;
  function loadSirvoy() {
    if (!sirvoyBox || currentView() !== "ete") return;
    sirvoyLang = lang;
    Array.prototype.forEach.call(sirvoyBox.querySelectorAll("div, script"), function (n) { n.parentNode.removeChild(n); });
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://secured.sirvoy.com/widget/sirvoy.js";
    s.setAttribute("data-form-id", sirvoyBox.getAttribute("data-form-id"));
    s.setAttribute("data-lang", lang);
    sirvoyBox.appendChild(s);
  }
  show();
  estimate();
  loadSirvoy();
})();
