(function (root) {
  const NETWORK_MESSAGE =
    "Unable to connect to the server. Check that the application is running and try again.";
  const SERVER_MESSAGE = "Something went wrong. Please try again.";
  const INVALID_RESPONSE_MESSAGE =
    "The server returned an invalid response. Please try again.";
  const DUPLICATE_MESSAGE =
    "This username or email is already registered. Try logging in.";

  const STATUS_MESSAGES = {
    401: "Invalid username/email or password.",
    403: "This request could not be verified. Refresh the page and try again.",
    404: "The requested item could not be found.",
    409: DUPLICATE_MESSAGE,
    502: NETWORK_MESSAGE,
    503: NETWORK_MESSAGE,
    504: NETWORK_MESSAGE
  };

  const FIELD_NAMES = {
    username: "Username",
    email: "Email",
    password: "Password",
    username_or_email: "Username or email",
    question: "Question",
    mode: "Mode"
  };

  function safeText(value) {
    if (typeof value !== "string") return "";
    const message = value.trim();
    if (
      !message ||
      message === "[object Object]" ||
      message.length > 240 ||
      /<(?:!doctype|html|head|body|script|pre)\b/i.test(message) ||
      /\b(?:traceback|stack trace|authorization:\s*bearer|api[_ -]?key\s*[:=]|AIza[0-9A-Za-z_-]{20,})/i.test(message)
    ) {
      return "";
    }
    return message;
  }

  function validationMessage(errors) {
    if (!Array.isArray(errors)) return "";
    const messages = errors
      .map((item) => {
        if (!item || typeof item !== "object") return "";
        const msg = safeText(item.msg || item.message);
        if (!msg) return "";
        const location = Array.isArray(item.loc) ? item.loc : [];
        const field = [...location].reverse().find((part) => typeof part === "string");
        const label = FIELD_NAMES[field];
        return label ? `${label}: ${msg}` : msg;
      })
      .filter(Boolean);

    return [...new Set(messages)].join(" ");
  }

  function detailMessage(detail) {
    if (typeof detail === "string") return safeText(detail);
    if (Array.isArray(detail)) return validationMessage(detail);
    if (detail && typeof detail === "object") {
      return safeText(detail.message || detail.msg);
    }
    return "";
  }

  function apiError(message, status) {
    const error = new Error(message);
    if (status) error.status = status;
    return error;
  }

  function formatApiError(error, options) {
    const settings = options || {};
    const status = Number(
      settings.status || (error && (error.status || (error.response && error.response.status)))
    );

    if (status === 429) {
      const detail = detailMessage(error && (error.detail || (error.response && error.response.data?.detail)));
      return detail || "Too many attempts. Please wait a moment and try again.";
    }
    if (STATUS_MESSAGES[status]) return STATUS_MESSAGES[status];
    if (status >= 500) return SERVER_MESSAGE;
    if (status === 422) {
      const payload = error && (error.response?.data || error.data || error);
      const detail = detailMessage(payload && payload.detail);
      return detail || "Please check the highlighted information and try again.";
    }

    const responseData = error && error.response && error.response.data;
    const payload = responseData || (error && error.data) || error;
    const detail = payload && typeof payload === "object"
      ? detailMessage(payload.detail)
      : "";
    if (detail) return detail;

    const message = typeof error === "string"
      ? safeText(error)
      : safeText(error && error.message);
    if (
      (error && error.name === "TypeError") ||
      /failed to fetch|network error|load failed|fetch failed/i.test(message)
    ) {
      return NETWORK_MESSAGE;
    }
    if (/unexpected token|unexpected end of json|not valid json/i.test(message)) {
      return INVALID_RESPONSE_MESSAGE;
    }
    return message || settings.fallback || SERVER_MESSAGE;
  }

  async function readResponse(response, options) {
    let text;
    try {
      text = await response.text();
    } catch (error) {
      throw apiError(formatApiError(error, options), response.status);
    }

    let payload = null;
    if (typeof text === "string" && text.trim()) {
      try {
        payload = JSON.parse(text);
      } catch {
        if (response.ok) throw apiError(INVALID_RESPONSE_MESSAGE, response.status);
      }
    }

    if (!response.ok) {
      throw apiError(formatApiError(payload, {
        ...(options || {}),
        status: response.status
      }), response.status);
    }
    return payload;
  }

  async function fetchJson(url, init, options) {
    let response;
    try {
      response = await root.fetch(url, init);
    } catch (error) {
      throw new Error(formatApiError(error, options));
    }
    return readResponse(response, options);
  }

  root.PyAssistErrors = Object.freeze({
    fetchJson,
    formatApiError,
    readResponse
  });
})(typeof window !== "undefined" ? window : globalThis);
