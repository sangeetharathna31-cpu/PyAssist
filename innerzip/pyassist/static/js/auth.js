/**
 * PyAssist - Authentication Script
 * Handles Login, Registration, Theme toggling, and CSRF token extraction.
 */

// Helper to get cookie value by name
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

// Fetch CSRF token from endpoint or cookie
async function ensureCsrfToken() {
  let token = getCookie("pyassist_csrf");
  if (!token) {
    try {
      const res = await fetch("/api/auth/csrf");
      if (res.ok) {
        const data = await res.json();
        token = data.csrf_token;
      }
    } catch (e) {
      console.warn("Could not fetch CSRF token:", e);
    }
  }
  return token;
}

// Initialize Theme
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
  if (btn) {
    btn.innerHTML = theme === "dark" ? "☀️" : "🌙";
    btn.setAttribute("title", `Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`);
  }
}

// Registration Form Handler
function setupRegisterForm() {
  const form = document.getElementById("register-form");
  const errorBanner = document.getElementById("auth-error");
  const submitBtn = document.getElementById("btn-submit");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorBanner.style.display = "none";
    errorBanner.textContent = "";

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    if (password !== confirmPassword) {
      errorBanner.textContent = "Passwords do not match.";
      errorBanner.style.display = "block";
      return;
    }

    if (password.length < 8) {
      errorBanner.textContent = "Password must be at least 8 characters long.";
      errorBanner.style.display = "block";
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Creating account...";

    try {
      const csrfToken = await ensureCsrfToken();
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {})
        },
        body: JSON.stringify({ username, email, password })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Registration failed. Please check your details.");
      }

      // Success -> Redirect to chat
      window.location.href = "/";
    } catch (err) {
      errorBanner.textContent = err.message;
      errorBanner.style.display = "block";
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Create Account";
    }
  });
}

// Login Form Handler
function setupLoginForm() {
  const form = document.getElementById("login-form");
  const errorBanner = document.getElementById("auth-error");
  const submitBtn = document.getElementById("btn-submit");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorBanner.style.display = "none";
    errorBanner.textContent = "";

    const username_or_email = document.getElementById("username-or-email").value.trim();
    const password = document.getElementById("password").value;

    submitBtn.disabled = true;
    submitBtn.textContent = "Signing in...";

    try {
      const csrfToken = await ensureCsrfToken();
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {})
        },
        body: JSON.stringify({ username_or_email, password })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Invalid credentials.");
      }

      // Success -> Redirect to chat
      window.location.href = "/";
    } catch (err) {
      errorBanner.textContent = err.message;
      errorBanner.style.display = "block";
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Sign In";
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  setupRegisterForm();
  setupLoginForm();

  const themeBtn = document.getElementById("btn-theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", toggleTheme);
  }

  const demoBtn = document.getElementById("btn-fill-demo");
  if (demoBtn) {
    demoBtn.addEventListener("click", () => {
      const usernameInput = document.getElementById("username-or-email");
      const passwordInput = document.getElementById("password");
      if (usernameInput) usernameInput.value = "demo_user";
      if (passwordInput) passwordInput.value = "Password123";
    });
  }
});
