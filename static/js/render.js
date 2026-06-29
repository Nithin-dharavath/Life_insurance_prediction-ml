/* Render the results panel — editorial layout: huge category + sentence + bar chart */
(function () {
  const reduceMotion = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const COPY = {
    Low:    "You sit in a low premium bracket — a favorable risk profile.",
    Medium: "You sit in a moderate premium bracket — a balanced risk profile.",
    High:   "You sit in a high premium bracket — an elevated risk profile."
  };

  function el(tag, props = {}, children = []) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(props)) {
      if (k === "class") node.className = v;
      else if (k === "text") node.textContent = v;
      else node[k] = v;
    }
    for (const c of [].concat(children)) {
      if (c == null) continue;
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    }
    return node;
  }

  function categoryClass(cat) {
    const c = String(cat || "").toLowerCase();
    if (c === "low")    return "is-low";
    if (c === "medium") return "is-med";
    if (c === "high")   return "is-high";
    return "";
  }

  function categoryColor(cat) {
    return {
      Low:    "var(--cat-low)",
      Medium: "var(--cat-med)",
      High:   "var(--cat-high)"
    }[cat] || "var(--accent)";
  }

  function fmtPct(p) {
    return (Math.round(p * 1000) / 10).toFixed(1) + "%";
  }

  function lead(result) {
    const wrap = el("div", { class: "result " + categoryClass(result.predicted_category) });
    wrap.style.setProperty("--cat-color", categoryColor(result.predicted_category));

    wrap.appendChild(el("p", { class: "result__eyebrow stagger", text: "You're estimated at" }));

    const lead = el("div", { class: "result__lead stagger" });
    lead.appendChild(el("span", { class: "bracket", text: "—" }));
    lead.appendChild(el("span", { class: "word",    text: result.predicted_category }));
    lead.appendChild(el("span", { class: "bracket", text: "—" }));
    wrap.appendChild(lead);

    wrap.appendChild(el("p", {
      class: "result__copy stagger",
      text: COPY[result.predicted_category] || "Prediction complete."
    }));
    return wrap;
  }

  function confidenceBlock(result) {
    const block = el("div", { class: "stagger" });
    block.appendChild(el("div", { class: "rule" }));
    const meta = el("div", { class: "meta" });
    meta.appendChild(el("span", { class: "meta__label", text: "Confidence" }));
    const val = el("span", { class: "meta__value" });
    val.appendChild(el("span", { class: "pct-count", text: "0" }));
    val.appendChild(el("span", { class: "pct", text: "%" }));
    meta.appendChild(val);
    block.appendChild(meta);
    return { block, countEl: val.querySelector(".pct-count") };
  }

  function probabilityChart(result) {
    const wrap = el("div", { class: "stagger" });
    wrap.appendChild(el("p", { class: "probs__title", text: "Probability breakdown" }));

    const winner = result.predicted_category;
    const entries = Object.entries(result.class_probabilities || {})
      .map(([label, value]) => ({ label, value }))
      .sort((a, b) => b.value - a.value);

    const rowRefs = [];
    for (const e of entries) {
      const isWinner = e.label === winner;
      const row = el("div", { class: "prob" + (isWinner ? " is-winner" : "") });
      row.style.setProperty("--cat-color", categoryColor(e.label));
      row.appendChild(el("span", { class: "prob__label", text: e.label }));

      const track = el("div", { class: "prob__track" });
      const fill  = el("div", { class: "prob__fill" });
      track.appendChild(fill);
      row.appendChild(track);

      row.appendChild(el("span", {
        class: "prob__pct" + (isWinner ? "" : " muted"),
        text: fmtPct(e.value)
      }));

      wrap.appendChild(row);
      rowRefs.push({ row, fill, target: e.value });
    }
    return { wrap, rowRefs };
  }

  function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }

  function countUp(el, to, duration) {
    if (reduceMotion) { el.textContent = String(Math.round(to)); return Promise.resolve(); }
    const start = performance.now();
    return new Promise((resolve) => {
      function frame(now) {
        const t = Math.min(1, (now - start) / duration);
        el.textContent = String(Math.round(to * easeOutCubic(t)));
        if (t < 1) requestAnimationFrame(frame);
        else resolve();
      }
      requestAnimationFrame(frame);
    });
  }

  function delay(ms) { return new Promise((r) => setTimeout(r, ms)); }

  // Sequential reveal — robust against transitionend flakiness.
  async function renderResults(container, responseData /* , clientFeatures — unused in editorial layout */) {
    container.replaceChildren();
    container.hidden = true;

    // Build structure
    const cardHead = el("div", { class: "card__body" });
    const leadEl = lead(responseData);
    const { block: confBlock, countEl } = confidenceBlock(responseData);
    const { wrap: probs, rowRefs } = probabilityChart(responseData);

    cardHead.appendChild(leadEl);
    cardHead.appendChild(confBlock);
    cardHead.appendChild(probs);
    container.appendChild(cardHead);

    // Reveal — make the card visible instantly, no dependency on transition events
    container.hidden = false;

    // Stagger entrance of children
    const stages = [
      leadEl.querySelector(".result__eyebrow"),
      leadEl.querySelector(".result__lead"),
      leadEl.querySelector(".result__copy"),
      confBlock,
      probs
    ].filter(Boolean);

    for (const s of stages) {
      s.classList.add("is-in");
      await delay(reduceMotion ? 0 : 60);
    }

    // Animate confidence count-up
    await countUp(countEl, responseData.confidence * 100, reduceMotion ? 0 : 600);

    // Animate probability bar widths + stagger rows
    const sortedRows = rowRefs.slice().sort((a, b) => b.target - a.target);
    for (const r of sortedRows) {
      r.row.classList.add("is-in");
      // Force next frame so the transition kicks in
      requestAnimationFrame(() => {
        r.fill.style.width = (Math.max(0, Math.min(1, r.target)) * 100) + "%";
      });
      await delay(reduceMotion ? 0 : 70);
    }
  }

  function clearResults(container) {
    container.classList.remove("is-revealed");
    container.replaceChildren();
    container.hidden = true;
  }

  window.App = window.App || {};
  window.App.render = { renderResults, clearResults };
})();
