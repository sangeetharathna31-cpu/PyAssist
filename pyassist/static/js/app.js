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
    loadingText: "PyAssist is thinking…"
  },
  generate: {
    name: "Generate Code",
    icon: "⚡",
    placeholder: "Describe the Python code you need (e.g. Write an LRU Cache with O(1) ops)...",
    loadingText: "PyAssist is working on your code…"
  },
  debug: {
    name: "Debug Code",
    icon: "🐞",
    placeholder: "Paste buggy code or error traceback (e.g. IndexError: list index out of range in line 4)...",
    loadingText: "PyAssist is tracing the issue…"
  },
  explain: {
    name: "Explain Code",
    icon: "📖",
    placeholder: "Paste Python code or algorithm to explain step-by-step with complexity analysis...",
    loadingText: "PyAssist is explaining the code…"
  },
  review: {
    name: "Code Review",
    icon: "🔍",
    placeholder: "Paste Python code for review (PEP 8, performance, security, edge cases)...",
    loadingText: "PyAssist is reviewing your code…"
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
      const data = await PyAssistErrors.fetchJson("/api/auth/csrf");
      token = data && data.csrf_token;
    } catch (e) {
      console.warn("CSRF token request failed.");
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

const PYTHON_KEYWORDS = new Set([
  "and", "as", "assert", "async", "await", "break", "class", "continue",
  "def", "del", "elif", "else", "except", "False", "finally", "for", "from",
  "global", "if", "import", "in", "is", "lambda", "nonlocal", "not", "or",
  "pass", "raise", "return", "True", "try", "while", "with", "yield", "None"
]);
const PYTHON_BUILTINS = new Set([
  "abs", "all", "any", "bool", "dict", "enumerate", "filter", "float", "int",
  "len", "list", "map", "max", "min", "print", "range", "reversed", "round",
  "set", "sorted", "str", "sum", "tuple", "type", "zip"
]);

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function highlightCode(code, language) {
  if (!["python", "py"].includes(String(language || "python").toLowerCase())) {
    return escapeHtml(code);
  }

  const tokenPattern = /(#.*$|"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b\d+(?:\.\d+)?\b|\b[A-Za-z_]\w*\b)/gm;
  let html = "";
  let lastIndex = 0;

  for (const match of code.matchAll(tokenPattern)) {
    html += escapeHtml(code.slice(lastIndex, match.index));
    const token = match[0];
    let tokenClass = "";

    if (token.startsWith("#")) {
      tokenClass = "comment";
    } else if (/^(?:["'])/.test(token)) {
      tokenClass = "string";
    } else if (/^\d/.test(token)) {
      tokenClass = "number";
    } else if (PYTHON_KEYWORDS.has(token)) {
      tokenClass = "keyword";
    } else if (PYTHON_BUILTINS.has(token)) {
      tokenClass = "builtin";
    }

    html += tokenClass
      ? `<span class="syntax-${tokenClass}">${escapeHtml(token)}</span>`
      : escapeHtml(token);
    lastIndex = match.index + token.length;
  }

  return html + escapeHtml(code.slice(lastIndex));
}

function createCodeBlock(code, language = "python") {
  const codeBox = document.createElement("div");
  codeBox.className = "code-container";

  const codeHeader = document.createElement("div");
  codeHeader.className = "code-header";

  const languageLabel = document.createElement("span");
  languageLabel.className = "code-header-left";
  languageLabel.textContent = ["python", "py"].includes(String(language).toLowerCase())
    ? "Python"
    : (language || "Code");

  const copyButton = document.createElement("button");
  copyButton.type = "button";
  copyButton.className = "btn-copy";
  copyButton.textContent = "Copy code";
  copyButton.setAttribute("aria-label", "Copy code");
  copyButton.onclick = async () => {
    try {
      await navigator.clipboard.writeText(code);
      copyButton.textContent = "Copied";
      window.setTimeout(() => { copyButton.textContent = "Copy code"; }, 1800);
    } catch {
      copyButton.textContent = "Copy unavailable";
      window.setTimeout(() => { copyButton.textContent = "Copy code"; }, 1800);
    }
  };

  codeHeader.append(languageLabel, copyButton);

  const codePre = document.createElement("pre");
  codePre.className = "code-content";
  const codeElement = document.createElement("code");
  codeElement.innerHTML = highlightCode(code, language);
  codePre.appendChild(codeElement);

  codeBox.append(codeHeader, codePre);
  return codeBox;
}

// Render a small, safe subset of Markdown used by assistant responses.
function renderFormattedContent(text) {
  const container = document.createElement("div");
  container.className = "message-text";
  const lines = String(text || "").split("\n");
  let currentList = null;
  let currentListType = "";
  let currentParagraph = [];
  let inCodeBlock = false;
  let codeLanguage = "python";
  let codeLines = [];
  let hasCodeBlocks = false;

  function flushParagraph() {
    if (!currentParagraph.length) return;
    const paragraph = document.createElement("p");
    paragraph.innerHTML = formatInlineMarkdown(currentParagraph.join(" "));
    container.appendChild(paragraph);
    currentParagraph = [];
  }

  function flushList() {
    if (!currentList) return;
    container.appendChild(currentList);
    currentList = null;
    currentListType = "";
  }

  function appendListItem(type, textContent) {
    flushParagraph();
    if (currentList && currentListType !== type) flushList();
    if (!currentList) {
      currentList = document.createElement(type);
      currentListType = type;
    }
    const item = document.createElement("li");
    item.innerHTML = formatInlineMarkdown(textContent);
    currentList.appendChild(item);
  }

  for (const line of lines) {
    const trimmed = line.trim();

    if (inCodeBlock) {
      if (trimmed.startsWith("```")) {
        container.appendChild(createCodeBlock(codeLines.join("\n"), codeLanguage));
        codeLines = [];
        inCodeBlock = false;
      } else {
        codeLines.push(line);
      }
      continue;
    }

    const fence = trimmed.match(/^```([a-zA-Z0-9_+-]*)\s*$/);
    if (fence) {
      flushParagraph();
      flushList();
      inCodeBlock = true;
      codeLanguage = fence[1] || "python";
      hasCodeBlocks = true;
      continue;
    }

    if (!trimmed) {
      flushParagraph();
      flushList();
      continue;
    }

    const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const title = document.createElement(`h${heading[1].length}`);
      title.textContent = heading[2];
      container.appendChild(title);
      continue;
    }

    const bullet = trimmed.match(/^(?:[-*•])\s+(.+)$/);
    if (bullet) {
      appendListItem("ul", bullet[1]);
      continue;
    }

    const numbered = trimmed.match(/^\d+[.)]\s+(.+)$/);
    if (numbered) {
      appendListItem("ol", numbered[1]);
      continue;
    }

    flushList();
    currentParagraph.push(trimmed);
  }

  if (inCodeBlock) {
    container.appendChild(createCodeBlock(codeLines.join("\n"), codeLanguage));
  }
  flushParagraph();
  flushList();
  container.dataset.hasCodeBlocks = String(hasCodeBlocks);
  return container;
}

function formatInlineMarkdown(text) {
  return String(text)
    .split(/(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g)
    .map((part) => {
      if (part.startsWith("`") && part.endsWith("`")) {
        return `<code>${escapeHtml(part.slice(1, -1))}</code>`;
      }
      if (part.startsWith("**") && part.endsWith("**")) {
        return `<strong>${escapeHtml(part.slice(2, -2))}</strong>`;
      }
      if (part.startsWith("*") && part.endsWith("*")) {
        return `<em>${escapeHtml(part.slice(1, -1))}</em>`;
      }
      return escapeHtml(part);
    })
    .join("");
}

function assistantDisplayText(message) {
  const content = String(message.content || "");
  if (
    !message.is_supported &&
    /^(?:Gemini is unavailable|This mode requires Gemini)/i.test(content.trim())
  ) {
    return "PyAssist couldn't complete that response. Please try again in a moment.";
  }
  return content;
}

// Check Authentication
async function checkAuth() {
  try {
    currentUser = await PyAssistErrors.fetchJson("/api/auth/me");
    setupUserProfile();
    return true;
  } catch (err) {
    console.warn("Authentication check failed.");
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
    conversations = await PyAssistErrors.fetchJson("/api/history");
    renderConversationList();
  } catch (err) {
    console.warn("Could not load conversation history.");
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
    const data = await PyAssistErrors.fetchJson(`/api/history/${conversationId}`);
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
    console.warn("Could not load conversation details.");
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
  const isUser = msg.role === "user";
  const row = document.createElement("div");
  row.className = `message-row ${isUser ? "user" : "bot"}`;

  const avatar = document.createElement("div");
  avatar.className = `message-avatar ${isUser ? "user" : "bot"}`;
  avatar.textContent = isUser ? ((currentUser && currentUser.username[0]) || "U").toUpperCase() : "P";

  const contentCol = document.createElement("div");
  contentCol.className = "message-content";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  const meta = document.createElement("div");
  meta.className = `message-meta ${isUser ? "user-meta" : "assistant-meta"}`;

  const author = document.createElement("span");
  author.className = isUser ? "message-author user-author" : "message-author assistant-author";
  author.textContent = isUser ? "You" : "PyAssist";
  meta.appendChild(author);

  const modeKey = msg.mode ||
    (msg.topic_id && msg.topic_id.startsWith("gemini_")
      ? msg.topic_id.slice(7)
      : (msg.topic_id && msg.topic_id.startsWith("mode:")
        ? msg.topic_id.slice(5)
        : "ask"));
  const modeConfig = MODE_CONFIG[modeKey];
  if (modeConfig && modeKey !== "ask") {
    const modeBadge = document.createElement("span");
    modeBadge.className = `mode-badge ${modeKey}`;
    modeBadge.textContent = modeConfig.name;
    meta.appendChild(modeBadge);
  }

  const time = document.createElement("span");
  time.className = "message-time";
  time.textContent = formatDate(msg.created_at);
  meta.appendChild(time);
  bubble.appendChild(meta);

  if (isUser) {
    const userText = document.createElement("div");
    userText.className = "user-message-text";
    userText.textContent = msg.content;
    bubble.appendChild(userText);
  } else {
    const displayText = assistantDisplayText(msg);
    const formattedContent = renderFormattedContent(displayText);
    bubble.appendChild(formattedContent);

    // Use the structured code field only when the answer has no fenced code block.
    if (msg.code_example && formattedContent.dataset.hasCodeBlocks !== "true") {
      bubble.appendChild(createCodeBlock(msg.code_example, "python"));
    }

    if (msg.expected_output) {
      const outBox = document.createElement("div");
      outBox.className = "output-container";

      const outHeader = document.createElement("div");
      outHeader.className = "output-header";
      outHeader.textContent = "Expected output";

      const outPre = document.createElement("pre");
      outPre.className = "output-content";
      outPre.textContent = msg.expected_output;

      outBox.append(outHeader, outPre);
      bubble.appendChild(outBox);
    }
  }

  contentCol.appendChild(bubble);

  // Bot actions
  if (!isUser) {
    const actions = document.createElement("div");
    actions.className = "message-actions";

    const copyAnsBtn = document.createElement("button");
    copyAnsBtn.className = "action-btn";
    copyAnsBtn.type = "button";
    copyAnsBtn.textContent = "Copy response";
    copyAnsBtn.onclick = async () => {
      const fullText = `${assistantDisplayText(msg)}\n\n${msg.code_example ? '```python\n' + msg.code_example + '\n```\n' : ''}${msg.expected_output ? 'Output:\n' + msg.expected_output : ''}`;
      try {
        await navigator.clipboard.writeText(fullText);
        copyAnsBtn.textContent = "Copied";
        window.setTimeout(() => { copyAnsBtn.textContent = "Copy response"; }, 1800);
      } catch {
        copyAnsBtn.textContent = "Copy unavailable";
        window.setTimeout(() => { copyAnsBtn.textContent = "Copy response"; }, 1800);
      }
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
    const data = await PyAssistErrors.fetchJson("/api/chat/ask", {
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
    }, { fallback: "Something went wrong while processing your question." });
    loading.style.display = "none";

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
    if (err && err.status === 401) {
      window.location.href = "/login.html";
      return;
    }
    const errorBanner = document.getElementById("chat-error-banner");
    const errorMsg = document.getElementById("chat-error-message");
    errorMsg.textContent = PyAssistErrors.formatApiError(err, {
      fallback: "Something went wrong while processing your question."
    });
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
    await PyAssistErrors.fetchJson(`/api/history/${idToDelete}`, {
      method: "DELETE",
      headers: {
        ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {})
      }
    });

    if (currentConversationId === idToDelete) {
      startNewChat();
    }
    loadConversations();
  } catch (err) {
    console.warn("Could not delete conversation.");
  }
}

// Topics Explorer Modal Logic
async function openTopicsModal() {
  const modal = document.getElementById("topics-modal");
  const listEl = document.getElementById("topics-modal-list");
  listEl.textContent = "Loading topics...";
  modal.classList.add("active");

  try {
    const topics = await PyAssistErrors.fetchJson("/api/chat/topics");
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
    listEl.textContent = "Failed to load topics. Please try again.";
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
    await PyAssistErrors.fetchJson("/api/auth/logout", {
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
      const mode = chip.getAttribute("data-mode") || "ask";
      setMode(mode);
      if (q) submitQuestion(q, mode);
    });
  });

  // Assistant mode selectors
  document.querySelectorAll(".mode-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const mode = tab.getAttribute("data-mode");
      if (mode) setMode(mode);
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
