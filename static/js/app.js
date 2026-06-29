/* App entry — form submit, validation, errors, loading state */
(function () {
  const App = window.App;

  document.addEventListener("DOMContentLoaded", () => {
    const apiUrl = window.API_URL || document.body.dataset.apiUrl || "/predict";

    const form         = document.getElementById("predict-form");
    const cta          = document.getElementById("cta");
    const resultsPanel = document.getElementById("results");
    const toastRegion  = document.getElementById("toast-region");
    const formFields   = Array.from(form.querySelectorAll(".field"));

    function readForm() {
      const fd = new FormData(form);
      return {
        age:        Number(fd.get("age")),
        weight:     Number(fd.get("weight")),
        height:     Number(fd.get("height")),
        income_lpa: Number(fd.get("income_lpa")),
        occupation: String(fd.get("occupation") || ""),
        smoker:     fd.get("smoker") === "true",
        city:       String(fd.get("city") || "").trim()
      };
    }

    function setFieldError(name, message) {
      const field = form.querySelector(`.field[data-field="${name}"]`);
      if (!field) return;
      const err = field.querySelector(".field__error");
      if (message) {
        field.classList.add("is-invalid");
        if (err) err.textContent = message;
      } else {
        field.classList.remove("is-invalid");
        if (err) err.textContent = "";
      }
    }

    function clearAllErrors() {
      for (const f of formFields) {
        f.classList.remove("is-invalid");
        const err = f.querySelector(".field__error");
        if (err) err.textContent = "";
      }
    }

    function setLoading(loading) {
      cta.classList.toggle("is-loading", loading);
      cta.disabled = loading;
      form.setAttribute("aria-busy", loading ? "true" : "false");
      for (const f of formFields) {
        const ctl = f.querySelector("input, select");
        if (ctl) ctl.disabled = loading;
      }
    }

    function escape(s) {
      return String(s)
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
    }

    function showToast({ title = "", message = "", kind = "info", duration = 4200 }) {
      const t = document.createElement("div");
      t.className = `toast toast--${kind}`;
      t.innerHTML = `
        <span class="toast__icon" aria-hidden="true"></span>
        <div class="toast__body">
          ${title ? `<p class="toast__title">${escape(title)}</p>` : ""}
          <p class="toast__msg">${escape(message)}</p>
        </div>
        <button class="toast__close" aria-label="Dismiss notification">&times;</button>
      `;
      toastRegion.appendChild(t);
      requestAnimationFrame(() => t.classList.add("is-in"));
      const close = () => {
        t.classList.remove("is-in");
        t.classList.add("is-leaving");
        setTimeout(() => t.remove(), 320);
      };
      t.querySelector(".toast__close").addEventListener("click", close);
      setTimeout(close, duration);
    }

    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      clearAllErrors();

      const data = readForm();
      const { valid, errors } = App.validate(data);
      if (!valid) {
        const firstKey = Object.keys(errors)[0];
        for (const [k, msg] of Object.entries(errors)) setFieldError(k, msg);
        const firstField = form.querySelector(`.field[data-field="${firstKey}"]`);
        if (firstField) {
          const ctl = firstField.querySelector("input, select");
          if (ctl) ctl.focus();
        }
        return;
      }

      setLoading(true);
      try {
        const result = await App.api.predict(apiUrl, data);
        if (result.kind === "ok") {
          // Scroll into view once it exists in the DOM
          requestAnimationFrame(async () => {
            await App.render.renderResults(resultsPanel, result.data);
            resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
          });
        } else {
          handleError(result);
        }
      } catch (e) {
        showToast({ kind: "error", title: "Unexpected error", message: String(e.message || e) });
      } finally {
        setLoading(false);
      }
    });

    function handleError(result) {
      clearAllErrors();
      if (result.kind === "validation") {
        let handled = 0;
        for (const item of result.items) {
          if (item.field && form.querySelector(`.field[data-field="${item.field}"]`)) {
            setFieldError(item.field, item.message);
            handled++;
          }
        }
        if (handled > 0) {
          showToast({
            kind: "error",
            title: "Please review your input",
            message: handled === 1 ? "One field needs attention." : `${handled} fields need attention.`
          });
        } else {
          showToast({ kind: "error", title: "Invalid input",
                      message: result.items[0]?.message || "Please check the form." });
        }
        return;
      }
      if (result.kind === "network")   return showToast({ kind: "error", title: "Can't reach the server", message: result.message });
      if (result.kind === "timeout")   return showToast({ kind: "error", title: "Request timed out",     message: result.message });
      if (result.kind === "server")    return showToast({ kind: "error", title: "Server error",          message: result.message });
      showToast({ kind: "error", title: "Something went wrong", message: result.message || "Please try again." });
    }

    // Clear field errors as the user edits
    for (const f of formFields) {
      const ctl = f.querySelector("input, select");
      if (!ctl) continue;
      const evt = ctl.tagName === "SELECT" ? "change" : "input";
      ctl.addEventListener(evt, () => {
        f.classList.remove("is-invalid");
        const err = f.querySelector(".field__error");
        if (err) err.textContent = "";
      });
    }

    // Sanity: cities list length
    if (window.console && App.cities && App.cities.ALL && App.cities.ALL.length !== 56) {
      console.warn(
        "[Insurance UI] city list length is " + App.cities.ALL.length +
        " — expected 56. Update cities.js to match city/city_tier.py."
      );
    }
  });
})();
