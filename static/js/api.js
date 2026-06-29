/* API wrapper — POSTs to /predict and normalizes errors */
(function () {
  const TIMEOUT_MS = 15000;

  async function predict(apiUrl, payload) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
    let res;
    try {
      res = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal
      });
    } catch (err) {
      clearTimeout(timer);
      if (err && err.name === "AbortError") {
        return {
          kind: "timeout",
          message: "Request timed out. The server may be overloaded — please try again."
        };
      }
      return {
        kind: "network",
        message: "Could not connect to the API server. Make sure it's running."
      };
    }
    clearTimeout(timer);

    let body = null;
    try {
      body = await res.json();
    } catch {
      // Non-JSON response
    }

    if (res.ok) {
      // Expected: { Response: { predicted_category, confidence, class_probabilities } }
      if (body && body.Response) return { kind: "ok", data: body.Response };
      return { kind: "http", status: res.status, message: "Unexpected response shape." };
    }

    if (res.status === 422) {
      // FastAPI / Pydantic v2 detail[]
      const items = [];
      if (Array.isArray(body && body.detail)) {
        for (const d of body.detail) {
          const field = Array.isArray(d.loc) ? d.loc.slice(-1)[0] : null;
          const message = String(d.msg || "Invalid value").replace(/^Value error,\s*/i, "");
          items.push({ field, message });
        }
      }
      return { kind: "validation", items };
    }

    if (res.status >= 500) {
      return { kind: "server", message: (body && body.error) || "Internal server error." };
    }

    return {
      kind: "http",
      status: res.status,
      message: (body && body.error) || `Request failed (${res.status}).`
    };
  }

  window.App = window.App || {};
  window.App.api = { predict };
})();