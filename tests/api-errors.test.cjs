const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const browserGlobal = {};
browserGlobal.globalThis = browserGlobal;
browserGlobal.fetch = global.fetch;
vm.runInNewContext(
  fs.readFileSync(path.join(__dirname, "../pyassist/static/js/api-errors.js"), "utf8"),
  browserGlobal,
  { filename: "api-errors.js" }
);
const errors = browserGlobal.PyAssistErrors;

test("formats string and Error.message values", () => {
  assert.equal(errors.formatApiError("Please try again."), "Please try again.");
  assert.equal(errors.formatApiError(new Error("A readable error.")), "A readable error.");
  assert.notEqual(errors.formatApiError({}), "[object Object]");
});

test("formats FastAPI detail objects and maps authentication/conflict statuses", async () => {
  const response = new Response(JSON.stringify({ detail: "Account is unavailable." }), {
    status: 400,
    headers: { "content-type": "application/json" }
  });
  await assert.rejects(errors.readResponse(response), /Account is unavailable/);
  assert.equal(errors.formatApiError({ detail: "bad credentials" }, { status: 401 }),
    "Invalid username/email or password.");
  assert.equal(errors.formatApiError({ detail: "csrf" }, { status: 403 }),
    "This request could not be verified. Refresh the page and try again.");
  assert.equal(errors.formatApiError({ detail: "missing" }, { status: 404 }),
    "The requested item could not be found.");
  assert.equal(errors.formatApiError({ detail: "duplicate" }, { status: 409 }),
    "This username or email is already registered. Try logging in.");
  assert.equal(errors.formatApiError({ detail: "slow down" }, { status: 429 }),
    "slow down");
  assert.equal(errors.formatApiError({ detail: "internal stack" }, { status: 500 }),
    "Something went wrong. Please try again.");
});

test("extracts field-specific FastAPI validation messages", async () => {
  const response = new Response(JSON.stringify({
    detail: [
      { loc: ["body", "username"], msg: "Username must use letters, numbers, or underscores." },
      { loc: ["body", "email"], msg: "Invalid email address format." }
    ]
  }), { status: 422 });
  await assert.rejects(
    errors.readResponse(response),
    /Username: Username must use letters, numbers, or underscores\. Email: Invalid email address format\./
  );
});

test("handles malformed, empty, and non-JSON responses without exposing HTML", async () => {
  await assert.rejects(
    errors.readResponse(new Response("<html><h1>Proxy error</h1></html>", { status: 502 })),
    /Unable to connect to the server/
  );
  await assert.rejects(
    errors.readResponse(new Response("<html>internal page</html>", { status: 200 })),
    /invalid response/i
  );
  assert.equal(await errors.readResponse(new Response(null, { status: 204 })), null);
  await assert.rejects(
    errors.readResponse(new Response(null, { status: 500 })),
    /Something went wrong/
  );
});

test("maps rejected fetches and hides server diagnostics", async () => {
  browserGlobal.fetch = async () => { throw new TypeError("Failed to fetch"); };
  await assert.rejects(
    errors.fetchJson("/api/auth/register"),
    /Unable to connect to the server/
  );
  assert.equal(
    errors.formatApiError(
      { detail: "Traceback: API_KEY=AIza123456789012345678901234567890123" },
      { status: 400 }
    ),
    "Something went wrong. Please try again."
  );
});
