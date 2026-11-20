/* Hudson, Jones, Jaywork & Fisher: small, dependency-free interactions. */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.add("js");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* Mobile menu */
  var toggle = $(".menu-toggle");
  var panel = $("#menu-panel");
  if (toggle && panel) {
    var setMenu = function (open) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      panel.hidden = !open;
      $(".menu-toggle-label", toggle).textContent = open ? "Close" : "Menu";
      document.body.style.overflow = open ? "hidden" : "";
    };
    toggle.addEventListener("click", function () {
      setMenu(toggle.getAttribute("aria-expanded") !== "true");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !panel.hidden) { setMenu(false); toggle.focus(); }
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 1060 && !panel.hidden) setMenu(false);
    });
  }

  /* Reveal on scroll */
  var revs = $$(".reveal");
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    revs.forEach(function (el) { io.observe(el); });
  } else {
    revs.forEach(function (el) { el.classList.add("in"); });
  }

  /* Home: table of contents preview */
  var preview = $(".toc-preview");
  if (preview) {
    var pNum = $(".toc-preview-num", preview);
    var pText = $(".toc-preview-text", preview);
    $$(".toc a").forEach(function (a) {
      var show = function () { pNum.textContent = a.dataset.num; pText.textContent = a.dataset.summary; };
      a.addEventListener("mouseenter", show);
      a.addEventListener("focus", show);
    });
  }

  /* Size inline selects to the chosen option instead of the longest one */
  var sizer = document.createElement("span");
  sizer.setAttribute("aria-hidden", "true");
  sizer.style.cssText = "position:absolute;visibility:hidden;white-space:nowrap;left:-9999px;top:0";
  document.body.appendChild(sizer);
  var autosize = function (sel) {
    var cs = getComputedStyle(sel);
    sizer.style.fontFamily = cs.fontFamily;
    sizer.style.fontSize = cs.fontSize;
    sizer.style.fontStyle = cs.fontStyle;
    sizer.style.fontWeight = cs.fontWeight;
    sizer.style.letterSpacing = cs.letterSpacing;
    sizer.textContent = sel.options[sel.selectedIndex] ? sel.options[sel.selectedIndex].text : "";
    var pad = parseFloat(cs.paddingRight) || 0;
    var max = sel.parentNode.parentNode.clientWidth;
    sel.style.width = Math.min(max, Math.ceil(sizer.getBoundingClientRect().width + pad + 6)) + "px";
  };
  var autoSelects = $$(".finder select");
  var sizeAll = function () { autoSelects.forEach(autosize); };
  autoSelects.forEach(function (s) { s.addEventListener("change", function () { autosize(s); }); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(sizeAll);
  sizeAll();
  window.addEventListener("resize", sizeAll);

  /* Home: "What brings you here?" sentence */
  var role = $("#finder-role");
  var need = $("#finder-need");
  if (role && need) {
    var finder = JSON.parse($("#finder-data").textContent);
    var practices = JSON.parse($("#practice-data").textContent);
    var answer = $(".finder-answer");
    var esc = function (s) {
      return String(s).replace(/[&<>"]/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
      });
    };
    var render = function () {
      var p = practices[need.value];
      if (!p) return;
      answer.classList.add("is-swapping");
      setTimeout(function () {
        var link = $(".finder-practice", answer);
        link.textContent = p.name;
        link.href = p.url;
        $(".finder-summary", answer).textContent = p.summary;
        $(".finder-attorneys", answer).innerHTML = p.attorneys.length
          ? p.attorneys.map(function (a) { return '<a href="' + a.url + '">' + esc(a.name) + "</a>"; }).join(", ")
          : "Call either office and we will connect you with the right attorney.";
        answer.classList.remove("is-swapping");
      }, reduce ? 0 : 180);
    };
    var fillNeeds = function () {
      var f = finder[role.value];
      need.innerHTML = f.needs.map(function (n) {
        return '<option value="' + n.slug + '">' + esc(n.label) + "</option>";
      }).join("");
      autosize(need);
      render();
    };
    role.addEventListener("change", fillNeeds);
    need.addEventListener("change", render);
  }

  /* Home: portrait that follows the cursor over the roll call */
  var floatBox = $(".roll-float");
  if (floatBox && window.matchMedia("(hover: hover)").matches) {
    var fImg = $("img", floatBox);
    var fCap = $("span", floatBox);
    var x = 0, y = 0, raf = null;
    var move = function () {
      floatBox.style.left = x + "px";
      floatBox.style.top = y + "px";
      raf = null;
    };
    $$(".roll a").forEach(function (a) {
      a.addEventListener("mouseenter", function () {
        fImg.src = a.dataset.portrait;
        fCap.textContent = a.dataset.meta;
        floatBox.classList.add("on");
      });
      a.addEventListener("mouseleave", function () { floatBox.classList.remove("on"); });
      a.addEventListener("mousemove", function (e) {
        x = e.clientX; y = e.clientY;
        if (!raf) raf = requestAnimationFrame(move);
      });
    });
  }

  /* Home: letters from clients */
  var letters = $$(".letter");
  if (letters.length) {
    var cur = 0;
    var count = $(".letters-count .cur");
    var show = function (i) {
      letters[cur].hidden = true;
      letters[cur].classList.remove("is-active");
      cur = (i + letters.length) % letters.length;
      letters[cur].hidden = false;
      letters[cur].classList.add("is-active");
      count.textContent = (cur + 1 < 10 ? "0" : "") + (cur + 1);
    };
    $(".letters-prev").addEventListener("click", function () { show(cur - 1); });
    $(".letters-next").addEventListener("click", function () { show(cur + 1); });
  }

  /* Attorneys: filters and portrait frame */
  var rows = $$(".rows .row");
  if (rows.length) {
    var officeBtns = $$(".filter-office button");
    var practiceSel = $("#practice-filter");
    var countEl = $(".filter-count span");
    var none = $(".directory .no-match");
    var office = "";
    var apply = function () {
      var pr = practiceSel.value, n = 0;
      rows.forEach(function (r) {
        var ok = (!office || r.dataset.office.split(" ").indexOf(office) > -1) &&
          (!pr || r.dataset.practices.split(" ").indexOf(pr) > -1);
        r.hidden = !ok;
        if (ok) n++;
      });
      countEl.textContent = n;
      none.hidden = n !== 0;
    };
    officeBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        office = b.dataset.office;
        officeBtns.forEach(function (o) { o.setAttribute("aria-checked", o === b ? "true" : "false"); });
        apply();
      });
    });
    practiceSel.addEventListener("change", apply);
    var frame = $(".directory-frame img");
    if (frame) {
      rows.forEach(function (r) {
        var a = $("a", r);
        var swap = function () {
          if (frame.getAttribute("src") === a.dataset.portrait) return;
          frame.style.opacity = 0;
          setTimeout(function () { frame.src = a.dataset.portrait; frame.style.opacity = 1; }, reduce ? 0 : 120);
        };
        a.addEventListener("mouseenter", swap);
        a.addEventListener("focus", swap);
      });
    }
  }

  /* Practice pages: highlight current section in the side contents */
  var tocLinks = $$(".pa-toc a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          tocLinks.forEach(function (a) { a.classList.remove("is-current"); });
          var l = map[en.target.id];
          if (l) l.classList.add("is-current");
        }
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    $$(".pa-section").forEach(function (s) { so.observe(s); });
  }

  /* About: load the video only when asked */
  var video = $(".video");
  if (video) {
    $(".video-btn", video).addEventListener("click", function () {
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + video.dataset.video + "?start=" + video.dataset.start + "&autoplay=1";
      f.title = "Hudson, Jones, Jaywork & Fisher video";
      f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
      f.allowFullscreen = true;
      video.innerHTML = "";
      video.appendChild(f);
    });
  }

  /* Resources: filter links */
  var resInput = $("#res-filter");
  if (resInput) {
    var groups = $$(".res-group");
    var resNone = $(".res-sec .no-match");
    resInput.addEventListener("input", function () {
      var q = resInput.value.trim().toLowerCase(), total = 0;
      groups.forEach(function (g) {
        var title = $("h3", g).textContent.toLowerCase();
        var n = 0;
        $$("li", g).forEach(function (li) {
          var ok = !q || li.textContent.toLowerCase().indexOf(q) > -1 || title.indexOf(q) > -1;
          li.hidden = !ok;
          if (ok) n++;
        });
        g.hidden = n === 0;
        total += n;
      });
      resNone.hidden = total !== 0;
    });
  }
})();
