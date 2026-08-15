/* ARON Assistant — RAG-powered chatbot connected to FastAPI backend
   Features: Auto language detection, multilingual greetings, hybrid knowledge */

(function () {

  // ── Multilingual Greetings (auto-detected on load) ──────────────────────────
  var GREETINGS = {
    "en": "Welcome to ARON! 👋<br>I can help with consultancy, ARON membership, ARON Insight, live demonstrations, energy support, food safety and EHO prep  or connect you with our trusted partners.<br>What are you working on?",
    "ur": "ARON میں خوش آمدید! 👋<br>میں آپ کی مشاورت، ARON رکنیت، لائیو ڈیمونسٹریشن، توانائی، فوڈ سیفٹی اور EHO تیاری میں مدد کر سکتا ہوں۔<br>آپ کس چیز پر کام کر رہے ہیں؟",
    "hi": "ARON में आपका स्वागत है! 👋<br>मैं परामर्श, ARON सदस्यता, लाइव डेमो, ऊर्जा, खाद्य सुरक्षा और EHO तैयारी में मदद कर सकता हूँ।<br>आप किस पर काम कर रहे हैं?",
    "bn": "ARON-এ স্বাগতম! 👋<br>আমি পরামর্শ, ARON সদস্যপদ, লাইভ ডেমো, শক্তি সহায়তা, খাদ্য নিরাপত্তা এবং EHO প্রস্তুতিতে সাহায্য করতে পারি।<br>আপনি কীসে কাজ করছেন?",
    "ar": "مرحباً بك في ARON! 👋<br>يمكنني المساعدة في الاستشارات وعضوية ARON والعروض التوضيحية المباشرة ودعم الطاقة وسلامة الغذاء.<br>بماذا تعمل؟",
    "fr": "Bienvenue chez ARON! 👋<br>Je peux vous aider avec les conseils, l'adhésion ARON, les démonstrations en direct, l'énergie et la sécurité alimentaire.<br>Sur quoi travaillez-vous?",
    "de": "Willkommen bei ARON! 👋<br>Ich kann bei Beratung, ARON-Mitgliedschaft, Live-Demos, Energie und Lebensmittelsicherheit helfen.<br>Woran arbeiten Sie?",
    "es": "¡Bienvenido a ARON! 👋<br>Puedo ayudarte con consultoría, membresía ARON, demostraciones en vivo, energía y seguridad alimentaria.<br>¿En qué estás trabajando?"
  };

  // ── Chat History (kept for conversation context) ──────────────────────────────
  var chatHistory = [];

  // ── Detect User Language from Browser ────────────────────────────────────────
  function detectLanguage() {
    var lang = (navigator.language || navigator.userLanguage || "en").toLowerCase();
    if (lang.startsWith("ur")) return "ur";
    if (lang.startsWith("hi")) return "hi";
    if (lang.startsWith("bn")) return "bn";
    if (lang.startsWith("ar")) return "ar";
    if (lang.startsWith("fr")) return "fr";
    if (lang.startsWith("de")) return "de";
    if (lang.startsWith("es")) return "es";
    return "en"; // Default to English
  }

  // ── Build Chatbot HTML Markup ─────────────────────────────────────────────────
  function markup() {
    return (
      // ── Floating Action Button ──
      '<button class="chat-fab" id="chatFab" aria-label="Open the ARON assistant">' +
      '<span class="pulse"></span>' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">' +
      '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>' +
      '</button>' +

      // ── Chat Panel ──
      '<div class="chat-panel" id="chatPanel" role="dialog" aria-label="ARON assistant">' +

      // Header
      '<div class="chat-head">' +
      '<div class="chat-avatar">A</div>' +
      '<div><strong>ARON Assistant</strong><small>Hospitality, systems &amp; profit</small></div>' +
      '<button class="chat-close" id="chatClose" aria-label="Close chat">✕</button>' +
      '</div>' +

      // Messages body
      '<div class="chat-body" id="chatBody"></div>' +

      // Language support banner — below chips, above input
      '<div class="chat-lang-banner">' +
      '🌐  English | اردو | हिंदी | বাংলা | العربية | Français | Deutsch | Español' +
      '</div>' +

      // Input form
      '<form class="chat-form" id="chatForm">' +
      '<input id="chatInput" placeholder="Ask about your business…" autocomplete="off" />' +
      '<button type="submit" aria-label="Send">→</button>' +
      '</form>' +

      '</div>'
    );
  }

  // ── Inject CSS for language note ─────────────────────────────────────────────
  function injectStyles() {
    var style = document.createElement("style");
    style.textContent = [
      // Language support banner styles
      ".chat-lang-banner {",
      "  background: #f9f6f0;",
      "  border-top: 1px solid #ece8e0;",
      "  border-bottom: 1px solid #ece8e0;",
      "  padding: 7px 14px;",
      "  text-align: center;",
      "  font-size: 11px;",
      "  color: #888;",
      "  line-height: 1.4;",
      "  white-space: nowrap;",
      "  overflow: hidden;",
      "  text-overflow: ellipsis;",
      "}",
      // Language note styles
      ".chat-lang-note {",
      "  font-size: 11px;",
      "  color: #888;",
      "  text-align: center;",
      "  padding: 6px 12px 4px;",
      "  line-height: 1.4;",
      "  border-top: 1px solid #f0f0f0;",
      "  background: #fafafa;",
      "}"
    ].join("\n");
    document.head.appendChild(style);
  }

  // ── Initialise Chatbot on DOM Ready ──────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", function () {

    // Inject language note styles
    injectStyles();

    // Insert chatbot markup into page
    var host = document.createElement("div");
    host.innerHTML = markup();
    document.body.appendChild(host);

    // Cache DOM references
    var fab    = document.getElementById("chatFab");
    var panel  = document.getElementById("chatPanel");
    var body   = document.getElementById("chatBody");
    var form   = document.getElementById("chatForm");
    var input  = document.getElementById("chatInput");

    // ── Format bot response (markdown bold, links, line breaks) ────────────────
    function formatBotResponse(text) {
      if (!text) return "";
      var formatted = text;
      // Convert markdown bold **text** to <strong>text</strong>
      formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      // Convert markdown italic *text* to <em>text</em>
      formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
      // Convert markdown links [title](url) to <a href="url" target="_blank" rel="noopener">title</a>
      formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
      // Convert plain URLs (not already inside href) to clickable links
      formatted = formatted.replace(/(^|[^"'>])(https?:\/\/[^\s<]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>');
      // Convert single newlines to <br>
      formatted = formatted.replace(/\n/g, '<br>');
      return formatted;
    }

    // ── Add message bubble to chat ──────────────────────────────────────────
    function add(role, html) {
      var el = document.createElement("div");
      el.className = "msg " + role;
      el.innerHTML = role === "bot"
        ? '<div class="bubble">' + formatBotResponse(html) + "</div>"
        : '<div class="bubble">' + escapeHtml(html) + "</div>";
      body.appendChild(el);
      body.scrollTop = body.scrollHeight;
      return el;
    }

    // ── Escape HTML for user messages (security) ────────────────────────────
    function escapeHtml(text) {
      return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\n/g, "<br>");
    }

    // ── Show typing indicator ───────────────────────────────────────────────
    function showTyping() {
      var typing = document.createElement("div");
      typing.className = "msg bot";
      typing.id = "typing-indicator";
      typing.innerHTML = '<div class="bubble"><div class="typing"><i></i><i></i><i></i></div></div>';
      body.appendChild(typing);
      body.scrollTop = body.scrollHeight;
    }

    // ── Remove typing indicator ─────────────────────────────────────────────
    function removeTyping() {
      var t = document.getElementById("typing-indicator");
      if (t) t.remove();
    }

    // ── Send message to RAG backend and display reply ───────────────────────
    async function respond(text) {
      showTyping();
      try {
        const res = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text, history: chatHistory })
        });
        const data = await res.json();
        removeTyping();
        const reply = data.reply || "Sorry, I couldn't get a response. Please try again.";
        add("bot", reply);

        // Update conversation history
        chatHistory.push({ role: "user", content: text });
        chatHistory.push({ role: "assistant", content: reply });

        // Keep last 20 messages (10 exchanges) to manage context window
        if (chatHistory.length > 20) {
          chatHistory = chatHistory.slice(-20);
        }
      } catch (err) {
        removeTyping();
        add("bot", "Sorry, something went wrong. Please try again or <a href='contact.html'>contact us directly</a>.");
        console.error("Chat error:", err);
      }
    }

    // ── Show greeting in detected language ──────────────────────────────────
    var detectedLang = detectLanguage();
    var greeting = GREETINGS[detectedLang] || GREETINGS["en"];
    add("bot", greeting);

    // ── Toggle chat panel open/closed ───────────────────────────────────────
    function toggle(open) {
      panel.classList.toggle("open", open);
      if (open) setTimeout(function () { input.focus(); }, 260);
    }

    fab.addEventListener("click", function () {
      toggle(!panel.classList.contains("open"));
    });

    document.getElementById("chatClose").addEventListener("click", function () {
      toggle(false);
    });

    // ── Handle form submission ──────────────────────────────────────────────
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var v = input.value.trim();
      if (!v) return;
      add("user", v);
      input.value = "";
      respond(v);
    });

  });

})();