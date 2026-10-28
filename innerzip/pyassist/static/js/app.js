/**
 * PyAssist - Main Chat Application Logic
 */

let currentUser = null;
let currentConversationId = null;
let conversations = [];
let isRequestPending = false;
let lastQuestionAttempt = "";
let currentMode = "ask";

const MODE_CONFIG = {
  ask: {
    name: "Ask Python",
    icon: "💡",
    placeholder: "Ask a Python question (e.g. What is the difference between is and ==?)...",
    loadingText: "Gemini is analyzing your Python question..."
  },
  generate: {
    name: "Generate Code",
    icon: "⚡",
    placeholder: "Describe the Python code you need (e.g. Write an LRU Cache with O(1) ops)...",
    loadingText: "Gemini is synthesizing clean Python code..."
  },
  debug: {
    name: "Debug Code",
    icon: "🐞",
    placeholder: "Paste buggy code or error traceback (e.g. IndexError: list index out of range in line 4)...",
    loadingText: "Gemini is diagnosing bug and traceback..."
  },
  explain: {
    name: "Explain Code",
    icon: "📖",
    placeholder: "Paste Python code or algorithm to explain step-by-step with complexity analysis...",
    loadingText: "Gemini is breaking down algorithm logic..."
  },
  review: {
    name: "Code Review",
    icon: "🔍",
    placeholder: "Paste Python code for review (PEP 8, performance, security, edge cases)...",
    loadingText: "Gemini is performing senior code review..."
  }
};

// Helper to get cookie value
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

// Fetch or ensure CSRF token
async function getCsrfToken() {
  let token = getCookie("pyassist_csrf");
  if (!token) {
    try {
      const res = await fetch("/api/auth/csrf");
      if (res.ok) {
        const data = await res.json();
        token = data.csrf_token;
      }
    } catch (e) {
      console.warn("CSRF fetch failed:", e);
    }
  }
  return token || "";
}

// Format date helper
function formatDate(dateStr) {
  try {
    const d = new Date(dateStr);
    const now = new Date();
    const isToday = d.toDateString() === now.toDateString();
    if (isToday) {
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  } catch {
    return "";
  }
}

// Sanitize & render formatted markdown-like text safely
function renderFormattedContent(text) {
  const container = document.createElement("div");
  container.className = "message-text";

  const lines = text.split("\n");
  let currentList = null;
  let currentParagraph = [];

  function flushParagraph() {
    if (currentParagraph.length > 0) {
      const p = document.createElement("p");
      p.innerHTML = formatInlineMarkdown(currentParagraph.join(" "));
      container.appendChild(p);
      currentParagraph = [];
    }
  }

  function flushList() {
    if (currentList) {
      container.appendChild(currentList);
      currentList = null;
    }
  }

  for (let line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      flushParagraph();
      flushList();
      continue;
    }

    if (trimmed.startsWith("### ")) {
      flushParagraph();
      flushList();
      const h3 = document.createElement("h3");
      h3.textContent = trimmed.substring(4);
      container.appendChild(h3);
    } else if (trimmed.startsWith("• ") || trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      flushParagraph();
      if (!currentList) {
        currentList = document.createElement("ul");
      }
      const li = document.createElement("li");
      li.innerHTML = formatInlineMarkdown(trimmed.substring(2));
      currentList.appendChild(li);
    } else if (/^\d+\.\s/.test(trimmed)) {
      flushParagraph();
      if (!currentList) {
        currentList = document.createElement("ol");
      }
      const li = document.createElement("li");
      li.innerHTML = formatInlineMarkdown(trimmed.replace(/^\d+\.\s/, ""));
      currentList.appendChild(li);
    } else {
      flushList();
      currentParagraph.push(trimmed);
    }
  }

  flushParagraph();
  flushList();

  return container;
}

function formatInlineMarkdown(text) {
  // Safe inline escaping
  let escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Bold **word**
  escaped = escaped.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  // Inline code `code`
  escaped = escaped.replace(/`([^`]+)`/g, "<code style='background: var(--bg-tertiary); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); font-size: 0.9em; color: #a78bfa;'>$1</code>");
  return escaped;
}

// Check Authentication
async function checkAuth() {
  try {
    const res = await fetch("/api/auth/me");
    if (!res.ok) {
      window.location.href = "/login.html";
      return false;
    }
    currentUser = await res.json();
    setupUserProfile();
    return true;
  } catch (err) {
    console.error("Auth check failed:", err);
    window.location.href = "/login.html";
    return false;
  }
}

function setupUserProfile() {
  if (!currentUser) return;
  const avatar = document.getElementById("user-avatar");
  const nameEl = document.getElementById("user-display-name");
  const emailEl = document.getElementById("user-display-email");

  if (avatar) avatar.textContent = (currentUser.username[0] || "U").toUpperCase();
  if (nameEl) nameEl.textContent = currentUser.username;
  if (emailEl) emailEl.textContent = currentUser.email;
}

// Conversation Management
async function loadConversations() {
  try {
    const res = await fetch("/api/history");
    if (!res.ok) return;
    conversations = await res.json();
    renderConversationList();
  } catch (err) {
    console.error("Failed to load history:", err);
  }
}

function renderConversationList(filterQuery = "") {
  const listEl = document.getElementById("conversation-list");
  if (!listEl) return;
  listEl.innerHTML = "";

  const filtered = conversations.filter(c => 
    !filterQuery || c.title.toLowerCase().includes(filterQuery.toLowerCase())
  );

  if (filtered.length === 0) {
    const empty = document.createElement("div");
    empty.className = "history-empty";
    empty.textContent = filterQuery ? "No matching conversations" : "No conversation history yet. Start asking Python questions!";
    listEl.appendChild(empty);
    return;
  }

  filtered.forEach(c => {
    const item = document.createElement("div");
    item.className = `conversation-item ${c.id === currentConversationId ? "active" : ""}`;
    item.setAttribute("data-id", c.id);

    const info = document.createElement("div");
    info.className = "conv-info";

    const title = document.createElement("div");
    title.className = "conv-title";
    title.textContent = c.title;

    const meta = document.createElement("div");
    meta.className = "conv-meta";
    meta.textContent = `${c.message_count} messages • ${formatDate(c.updated_at)}`;

    info.appendChild(title);
    info.appendChild(meta);

    const delBtn = document.createElement("button");
    delBtn.className = "conv-delete-btn";
    delBtn.title = "Delete conversation";
    delBtn.innerHTML = "✕";
    delBtn.onclick = (e) => {
      e.stopPropagation();
      openDeleteModal(c.id);
    };

    item.appendChild(info);
    item.appendChild(delBtn);

    item.addEventListener("click", () => {
      loadConversationDetail(c.id);
      // Close mobile sidebar if open
      closeMobileSidebar();
    });

    listEl.appendChild(item);
  });
}

// Load detail for a selected conversation
async function loadConversationDetail(conversationId) {
  try {
    const res = await fetch(`/api/history/${conversationId}`);
    if (!res.ok) {
      console.error("Conversation not found");
      return;
    }
    const data = await res.json();
    currentConversationId = data.id;

    document.getElementById("current-chat-title").textContent = data.title;
    renderConversationList(); // updates active highlight

    // Hide welcome, show messages
    document.getElementById("welcome-screen").style.display = "none";
    const feed = document.getElementById("messages-feed");
    feed.innerHTML = "";

    data.messages.forEach(msg => {
      renderMessage(msg);
    });

    scrollToBottom();
  } catch (err) {
    console.error("Failed to load conversation details:", err);
  }
}

// Start New Chat
function startNewChat() {
  currentConversationId = null;
  document.getElementById("current-chat-title").textContent = "New Conversation";
  document.getElementById("messages-feed").innerHTML = "";
  document.getElementById("welcome-screen").style.display = "block";
  document.getElementById("chat-error-banner").style.display = "none";
  renderConversationList();
  closeMobileSidebar();
  document.getElementById("message-input").focus();
}

// Render a single message in the feed
function renderMessage(msg) {
  const feed = document.getElementById("messages-feed");
  const row = document.createElement("div");
  row.className = `message-row ${msg.role === "user" ? "user" : "bot"}`;

  const avatar = document.createElement("div");
  avatar.className = `message-avatar ${msg.role === "user" ? "user" : "bot"}`;
  avatar.textContent = msg.role === "user" ? ((currentUser && currentUser.username[0]) || "U").toUpperCase() : "🐍";

  const contentCol = document.createElement("div");
  contentCol.className = "message-content";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  if (msg.role === "user") {
    bubble.textContent = msg.content;
  } else {
    // Bot message
    if (msg.topic_id || !msg.is_supported) {
      const meta = document.createElement("div");
      meta.className = "message-meta";

      if (msg.topic_id) {
        const badge = document.createElement("span");
        badge.className = "topic-badge";
        badge.textContent = "Verified Knowledge Base";
        meta.appendChild(badge);
      } else if (!msg.is_supported) {
        const badge = document.createElement("span");
        badge.className = "topic-badge";
        badge.style.borderColor = "var(--status-warning)";
        badge.style.color = "var(--status-warning)";
        badge.textContent = "Topic Not Found";
        meta.appendChild(badge);
      }

      const time = document.createElement("span");
      time.className = "message-time";
      time.textContent = formatDate(msg.created_at);
      meta.appendChild(time);

      bubble.appendChild(meta);
    }

    // Explanation formatted
    const textNode = renderFormattedContent(msg.content);
    bubble.appendChild(textNode);

    // Code block if present
    if (msg.code_example) {
      const codeBox = document.createElement("div");
      codeBox.className = "code-container";

      const codeHeader = document.createElement("div");
      codeHeader.className = "code-header";

      const left = document.createElement("div");
      left.className = "code-header-left";
      left.innerHTML = `<span class="code-header-dots"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span></span> Python`;

      const copyBtn = document.createElement("button");
      copyBtn.className = "btn-copy";
      copyBtn.innerHTML = `<span>📋</span> Copy Code`;
      copyBtn.onclick = () => {
        navigator.clipboard.writeText(msg.code_example);
        copyBtn.innerHTML = `<span>✓</span> Copied!`;
        setTimeout(() => { copyBtn.innerHTML = `<span>📋</span> Copy Code`; }, 2000);
      };

      codeHeader.appendChild(left);
      codeHeader.appendChild(copyBtn);

      const codePre = document.createElement("pre");
      codePre.className = "code-content";
      codePre.textContent = msg.code_example;

      codeBox.appendChild(codeHeader);
      codeBox.appendChild(codePre);
      bubble.appendChild(codeBox);
    }

    // Expected output block if present
    if (msg.expected_output) {
      const outBox = document.createElement("div");
      outBox.className = "output-container";

      const outHeader = document.createElement("div");
      outHeader.className = "output-header";
      outHeader.innerHTML = `<span>▶</span> Expected Output`;

      const outPre = document.createElement("pre");
      outPre.className = "output-content";
      outPre.textContent = msg.expected_output;

      outBox.appendChild(outHeader);
      outBox.appendChild(outPre);
      bubble.appendChild(outBox);
    }
  }

  contentCol.appendChild(bubble);

  // Bot actions
  if (msg.role === "assistant") {
    const actions = document.createElement("div");
    actions.className = "message-actions";

    const copyAnsBtn = document.createElement("button");
    copyAnsBtn.className = "action-btn";
    copyAnsBtn.innerHTML = `<span>📋</span> Copy Answer`;
    copyAnsBtn.onclick = () => {
      const fullText = `${msg.content}\n\n${msg.code_example ? '```python\n' + msg.code_example + '\n```\n' : ''}${msg.expected_output ? 'Output:\n' + msg.expected_output : ''}`;
      navigator.clipboard.writeText(fullText);
      copyAnsBtn.innerHTML = `<span>✓</span> Copied!`;
      setTimeout(() => { copyAnsBtn.innerHTML = `<span>📋</span> Copy Answer`; }, 2000);
    };

    actions.appendChild(copyAnsBtn);
    contentCol.appendChild(actions);
  }

  row.appendChild(avatar);
  row.appendChild(contentCol);
  feed.appendChild(row);
}

// Render Related Topics chips for a bot response
function renderRelatedTopics(topics) {
  if (!topics || topics.length === 0) return;
  const feed = document.getElementById("messages-feed");
  const lastRow = feed.lastElementChild;
  if (!lastRow) return;

  const contentCol = lastRow.querySelector(".message-content");
  if (!contentCol) return;

  const relContainer = document.createElement("div");
  relContainer.className = "related-topics-container";

  const label = document.createElement("div");
  label.className = "related-label";
  label.textContent = "Related Questions & Topics:";

  const chips = document.createElement("div");
  chips.className = "related-chips";

  topics.forEach(t => {
    const chip = document.createElement("button");
    chip.className = "related-chip";
    chip.textContent = t;
    chip.onclick = () => {
      submitQuestion(t);
    };
    chips.appendChild(chip);
  });

  relContainer.appendChild(label);
  relContainer.appendChild(chips);
  contentCol.appendChild(relContainer);
}

// Submit Question
async function submitQuestion(questionText, overrideMode) {
  if (isRequestPending) return;
  const q = (questionText || document.getElementById("message-input").value).trim();
  if (!q) return;

  const modeToUse = overrideMode || currentMode || "ask";
  lastQuestionAttempt = q;
  isRequestPending = true;

  // Clear input
  const inputEl = document.getElementById("message-input");
  inputEl.value = "";
  updateCharCounter();
  autoResizeTextarea(inputEl);
  document.getElementById("btn-send").disabled = true;

  // Hide welcome screen
  document.getElementById("welcome-screen").style.display = "none";
  document.getElementById("chat-error-banner").style.display = "none";

  // Render temporary user message in feed with mode
  renderMessage({
    role: "user",
    content: q,
    mode: modeToUse,
    created_at: new Date().toISOString()
  });

  // Show loading indicator with mode-specific text
  const loading = document.getElementById("loading-indicator");
  const loadingTextEl = document.getElementById("loading-text");
  if (loadingTextEl) {
    loadingTextEl.textContent = (MODE_CONFIG[modeToUse] || MODE_CONFIG.ask).loadingText;
  }
  loading.style.display = "flex";
  scrollToBottom();

  try {
    const csrfToken = await getCsrfToken();
    const res = await fetch("/api/chat/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {})
      },
      body: JSON.stringify({
        question: q,
        conversation_id: currentConversationId,
        mode: modeToUse
      })
    });

    const data = await res.json();
    loading.style.display = "none";

    if (!res.ok) {
      if (res.status === 401) {
        window.location.href = "/login.html";
        return;
      }
      throw new Error(data.detail || "Server error while processing question.");
    }

    // Update conversation state
    currentConversationId = data.conversation_id;
    document.getElementById("current-chat-title").textContent = data.conversation_title;

    // Render chatbot answer
    renderMessage(data.bot_message);

    // Render related topics if present
    if (data.related_topics && data.related_topics.length > 0) {
      renderRelatedTopics(data.related_topics);
    }

    scrollToBottom();
    loadConversations(); // refresh sidebar list
  } catch (err) {
    loading.style.display = "none";
    const errorBanner = document.getElementById("chat-error-banner");
    const errorMsg = document.getElementById("chat-error-message");
    errorMsg.textContent = err.message || "Unable to reach PyAssist. Please check your connection.";
    errorBanner.style.display = "flex";
    scrollToBottom();
  } finally {
    isRequestPending = false;
    document.getElementById("btn-send").disabled = false;
  }
}

function scrollToBottom() {
  const container = document.getElementById("messages-container");
  setTimeout(() => {
    container.scrollTop = container.scrollHeight;
  }, 50);
}

// Input Helpers
function setMode(mode) {
  if (!MODE_CONFIG[mode]) return;
  currentMode = mode;
  document.querySelectorAll(".mode-tab").forEach(tab => {
    tab.classList.toggle("active", tab.getAttribute("data-mode") === mode);
  });
  const input = document.getElementById("message-input");
  if (input) {
    input.placeholder = MODE_CONFIG[mode].placeholder;
  }
}

function updateCharCounter() {
  const input = document.getElementById("message-input");
  const counter = document.getElementById("char-counter");
  const btn = document.getElementById("btn-send");
  const len = input.value.trim().length;

  counter.textContent = `${len}/4000`;
  btn.disabled = len === 0 || isRequestPending;
}

function autoResizeTextarea(el) {
  el.style.height = "auto";
  el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
}

// Delete Modal Logic
let pendingDeleteId = null;

function openDeleteModal(convId) {
  pendingDeleteId = convId;
  document.getElementById("delete-modal").classList.add("active");
}

function closeDeleteModal() {
  pendingDeleteId = null;
  document.getElementById("delete-modal").classList.remove("active");
}

async function confirmDeleteConversation() {
  if (!pendingDeleteId) return;
  const idToDelete = pendingDeleteId;
  closeDeleteModal();

  try {
    const csrfToken = await getCsrfToken();
    const res = await fetch(`/api/history/${idToDelete}`, {
      method: "DELETE",
      headers: {
        ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {})
      }
    });

    if (res.ok) {
      if (currentConversationId === idToDelete) {
        startNewChat();
      }
      loadConversations();
    }
  } catch (err) {
    console.error("Delete failed:", err);
  }
}

// Topics Explorer Modal Logic
async function openTopicsModal() {
  const modal = document.getElementById("topics-modal");
  const listEl = document.getElementById("topics-modal-list");
  listEl.innerHTML = "<div>Loading topics...</div>";
  modal.classList.add("active");

  try {
    const res = await fetch("/api/chat/topics");
    if (!res.ok) throw new Error();
    const topics = await res.json();
    listEl.innerHTML = "";

    topics.forEach(t => {
      const card = document.createElement("div");
      card.style.cssText = "background: var(--bg-tertiary); border: 1px solid var(--border-subtle); padding: 12px; border-radius: var(--radius-md); cursor: pointer; transition: var(--transition);";
      card.innerHTML = `
        <div style="font-weight: 600; font-size: 13.5px; color: var(--accent-primary); margin-bottom: 4px;">${t.title}</div>
        <div style="font-size: 12px; color: var(--text-muted); line-height: 1.4;">${t.summary}</div>
      `;
      card.onmouseenter = () => { card.style.borderColor = "var(--accent-border)"; card.style.background = "var(--bg-hover)"; };
      card.onmouseleave = () => { card.style.borderColor = "var(--border-subtle)"; card.style.background = "var(--bg-tertiary)"; };
      card.onclick = () => {
        closeTopicsModal();
        submitQuestion(t.title);
      };
      listEl.appendChild(card);
    });
  } catch {
    listEl.innerHTML = "<div>Failed to load topics.</div>";
  }
}

function closeTopicsModal() {
  document.getElementById("topics-modal").classList.remove("active");
}

// Mobile sidebar controls
function openMobileSidebar() {
  document.getElementById("sidebar").classList.add("open");
  document.getElementById("sidebar-backdrop").classList.add("active");
}

function closeMobileSidebar() {
  document.getElementById("sidebar").classList.remove("open");
  document.getElementById("sidebar-backdrop").classList.remove("active");
}

// Logout
async function handleLogout() {
  try {
    const csrfToken = await getCsrfToken();
    await fetch("/api/auth/logout", {
      method: "POST",
      headers: {
        ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {})
      }
    });
  } finally {
    window.location.href = "/login.html";
  }
}

// Theme handling
function initTheme() {
  const saved = localStorage.getItem("pyassist_theme");
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = saved || (prefersDark ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", theme);
  updateThemeIcon(theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("pyassist_theme", next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  const btn = document.getElementById("btn-theme-toggle");
  if (btn) btn.innerHTML = theme === "dark" ? "☀️" : "🌙";
}

// Initial Setup
document.addEventListener("DOMContentLoaded", async () => {
  initTheme();
  const authed = await checkAuth();
  if (!authed) return;

  loadConversations();

  // Chat Form & Key listeners
  const form = document.getElementById("chat-form");
  const input = document.getElementById("message-input");

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    submitQuestion();
  });

  input.addEventListener("input", () => {
    updateCharCounter();
    autoResizeTextarea(input);
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submitQuestion();
    }
  });

  // Buttons
  document.getElementById("btn-new-chat").addEventListener("click", startNewChat);
  document.getElementById("btn-theme-toggle").addEventListener("click", toggleTheme);
  document.getElementById("btn-logout").addEventListener("click", handleLogout);
  document.getElementById("btn-mobile-menu").addEventListener("click", openMobileSidebar);
  document.getElementById("sidebar-backdrop").addEventListener("click", closeMobileSidebar);

  // Retry button
  document.getElementById("btn-error-retry").addEventListener("click", () => {
    if (lastQuestionAttempt) submitQuestion(lastQuestionAttempt);
  });

  // Welcome screen chips
  document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-question");
      if (q) submitQuestion(q);
    });
  });

  // History search input
  document.getElementById("history-search").addEventListener("input", (e) => {
    renderConversationList(e.target.value);
  });

  // Delete modal
  document.getElementById("btn-cancel-delete").addEventListener("click", closeDeleteModal);
  document.getElementById("btn-close-delete-modal").addEventListener("click", closeDeleteModal);
  document.getElementById("btn-confirm-delete").addEventListener("click", confirmDeleteConversation);

  // Topics modal
  document.getElementById("btn-open-topics").addEventListener("click", openTopicsModal);
  document.getElementById("btn-close-topics-modal").addEventListener("click", closeTopicsModal);
  document.getElementById("btn-done-topics").addEventListener("click", closeTopicsModal);
});
