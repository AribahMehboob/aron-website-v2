/* ARON — shared site behaviour: intro animation, nav drawer, scroll reveals, forms */
(function () {
  // ---- Intro logo animation (only once per session) ----
  function initIntro() {
    var intro = document.getElementById("intro");
    if (!intro) return;
    if (sessionStorage.getItem("aronIntroSeen") === "1") {
      intro.remove();
      return;
    }
    sessionStorage.setItem("aronIntroSeen", "1");
    document.body.style.overflow = "hidden";
    setTimeout(function () {
      intro.classList.add("done");
      document.body.style.overflow = "";
      setTimeout(function () {
        intro.remove();
      }, 600);
    }, 1700);
  }

  // ---- Mobile drawer ----
  function initNav() {
    var burger = document.getElementById("burger");
    var drawer = document.getElementById("drawer");
    var overlay = document.getElementById("drawerOverlay");
    var close = document.getElementById("drawerClose");
    if (!burger || !drawer) return;
    function toggle(open) {
      drawer.classList.toggle("open", open);
      overlay.classList.toggle("open", open);
      burger.classList.toggle("open", open);
    }
    burger.addEventListener("click", function () {
      toggle(!drawer.classList.contains("open"));
    });
    overlay.addEventListener("click", function () {
      toggle(false);
    });
    if (close) close.addEventListener("click", function () { toggle(false); });
  }

  // ---- Scroll reveal ----
  function initReveal() {
    var items = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("in"); });
      return;
    }
    var obs = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            obs.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
    );
    items.forEach(function (el) { obs.observe(el); });
  }

  // ---- Simple front-end form handling ----
  function initForms() {
    document.querySelectorAll("form[data-local-form]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var note = form.querySelector(".form-success");
        form.reset();
        if (note) {
          note.classList.add("show");
          note.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initIntro();
    initNav();
    initReveal();
    initForms();
  });
})();
