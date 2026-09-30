
const $ = (selector) => document.querySelector(selector);

let current = null;

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function fmt(value) {
  if (value === null || value === undefined || value === "") return "—";
  if (Array.isArray(value)) return value.length ? value.join(", ") : "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function shortHash(value) {
  return value ? `${value.slice(0, 12)}…${value.slice(-8)}` : "—";
}

function statusBadge(status) {
  const s = status || "UNKNOWN";
  return `<span class="status-badge" data-status="${escapeHtml(s)}">${escapeHtml(s)}</span>`;
}

function toast(message) {
  const node = $("#toast");
  node.textContent = message;
  node.classList.add("show");
  window.setTimeout(() => node.classList.remove("show"), 2600);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || payload.error || `HTTP ${response.status}`);
  }
  return payload;
}

function renderConnection(data) {
  const node = $("#connection");
  const status = data?.connection?.status || "UNKNOWN";
  node.textContent = status.replaceAll("_", " ");
  node.className = `connection-badge ${status.includes("READY") ? "ok" : "bad"}`;
}

function renderChangeHeader(data) {
  const s = data.state;
  $("#changeHeader").innerHTML = `
    <div class="change-topline">
      <div>
        <div class="eyebrow">CANONICAL CHANGE</div>
        <div class="change-id">${escapeHtml(s.change_id)}</div>
      </div>
      <div class="header-meta">
        <span class="truth-badge">${escapeHtml(data.truth_label)}</span>
        ${statusBadge(s.status)}
      </div>
    </div>
    <div class="change-metrics">
      <div class="metric">
        <div class="metric-label">REVISION</div>
        <div class="metric-value">${escapeHtml(s.revision)}</div>
      </div>
      <div class="metric">
        <div class="metric-label">CANONICAL STATE HASH</div>
        <div class="metric-value hash-value">${escapeHtml(s.state_hash)}</div>
      </div>
      <div class="metric">
        <div class="metric-label">PENDING MUTATIONS</div>
        <div class="metric-value">${escapeHtml(s.pending_call_ids.length)}</div>
      </div>
    </div>
  `;
}

function renderLatestTransaction(data) {
  const tx = data.latest_transaction || {};
  const ops = tx.parsed_operations || [];
  const diff = tx.diff || [];
  const rows = diff.map((d) => `
    <tr>
      <td>${escapeHtml(d.field)}</td>
      <td class="before">${escapeHtml(fmt(d.before))}</td>
      <td class="after">${escapeHtml(fmt(d.after))}</td>
    </tr>`).join("");

  $("#latestTransaction").innerHTML = `
    <div class="panel-heading">
      <div>
        <div class="eyebrow">LATEST TRANSACTION</div>
        <h2>${statusBadge(tx.status || "EMPTY")}</h2>
      </div>
      <div class="eyebrow">REV ${escapeHtml(tx.before_revision ?? "—")} → ${escapeHtml(tx.revision ?? data.state.revision)}</div>
    </div>
    ${tx.text ? `<div class="transcript-quote">“${escapeHtml(tx.text)}”</div>` : `<div class="empty-note">No operator amendment yet.</div>`}
    ${ops.length ? `<div class="ops-row">${ops.map((op) => `<span class="op-chip">${escapeHtml(op)}</span>`).join("")}</div>` : ""}
    ${tx.reason ? `<div class="reason-box">${escapeHtml(tx.reason)}</div>` : ""}
    ${rows ? `
      <table class="diff-table">
        <thead><tr><th>FIELD</th><th>BEFORE</th><th>AFTER</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>` : ""}
  `;
}

function directionLabel(value) {
  if (value === 1 || value === "1") return "West / direction_id 1";
  if (value === 0 || value === "0") return "East / direction_id 0";
  return fmt(value);
}

function renderState(data) {
  const s = data.state;
  const skips = s.skip_stops?.length
    ? s.skip_stops.map((x) => `${x.stop_name} (${x.stop_id})`).join(", ")
    : "None";
  const fields = [
    ["ROUTE", s.route],
    ["DIRECTION", directionLabel(s.direction)],
    ["SERVICE DATE", s.service_date],
    ["START", s.start_time],
    ["END", s.end_time],
    ["SKIPPED STOPS", skips],
    ["REASON", s.reason],
    ["UNRESOLVED", s.unresolved_items?.length ? JSON.stringify(s.unresolved_items) : "None"],
    ["COMMITTED HASH", s.committed_hash ? shortHash(s.committed_hash) : "Not committed"],
  ];

  const validationRows = (data.validation || []).map((v) => `
    <tr>
      <td>${escapeHtml(v.validator)}</td>
      <td class="${v.status === "PASS" ? "pass" : "warn"}"><strong>${escapeHtml(v.status)}</strong></td>
      <td>${escapeHtml(v.detail)}</td>
    </tr>`).join("");

  $("#statePanel").innerHTML = `
    <div class="panel-heading">
      <div>
        <div class="eyebrow">CURRENT TRUTH</div>
        <h2>Materialized service change</h2>
      </div>
      <button class="secondary small" id="copyHash">Copy current hash</button>
    </div>
    <div class="state-grid">
      ${fields.map(([label, value]) => `
        <div class="state-field">
          <div class="state-label">${escapeHtml(label)}</div>
          <div class="state-value ${label.includes("HASH") ? "mono" : ""}">${escapeHtml(fmt(value))}</div>
        </div>`).join("")}
    </div>
    <table class="validation-table">
      <thead><tr><th>BLOCKING VALIDATOR</th><th>STATUS</th><th>DETAIL</th></tr></thead>
      <tbody>${validationRows}</tbody>
    </table>
  `;

  $("#copyHash")?.addEventListener("click", async () => {
    await navigator.clipboard.writeText(s.state_hash);
    toast("Current hash copied.");
  });
}

function renderTimeline(data) {
  const history = [...(data.history || [])].reverse();
  $("#timeline").innerHTML = `
    <div class="panel-heading">
      <div>
        <div class="eyebrow">REVISION TRAIL</div>
        <h2>Amendments and protected actions</h2>
      </div>
      <div class="eyebrow">${history.length} EVENT${history.length === 1 ? "" : "S"}</div>
    </div>
    ${history.length ? `<div class="timeline-list">${
      history.map((item) => `
        <div class="timeline-item">
          <div class="timeline-rev">R${escapeHtml(item.revision ?? data.state.revision)}</div>
          <div>${statusBadge(item.status)}</div>
          <div class="timeline-body">
            <div class="timeline-text">${escapeHtml(item.text || item.reason || item.source || "Protected action")}</div>
            ${(item.parsed_operations || []).length
              ? `<div class="ops-row">${item.parsed_operations.map((op) => `<span class="op-chip">${escapeHtml(op)}</span>`).join("")}</div>`
              : ""}
            <div class="timeline-hash">${escapeHtml(item.before_hash || "—")} → ${escapeHtml(item.state_hash || "—")}</div>
          </div>
        </div>`).join("")
    }</div>` : `<div class="empty-note">The seeded context is revision 1. Applied amendments appear here.</div>`}
  `;
}

function renderCommit(data) {
  const s = data.state;
  const previousApplied = [...(data.history || [])]
    .reverse()
    .find((item) => item.status === "APPLIED" && item.before_hash && item.before_hash !== s.state_hash);

  $("#commitPanel").innerHTML = `
    <div class="eyebrow">PROTECTED HUMAN ACTION</div>
    <h2>Commit reviewed state</h2>
    <p>The backend will commit only if this reviewed hash still matches the canonical state and blocking validators pass.</p>
    <div class="commit-box">
      <label for="reviewHash">Reviewed state hash</label>
      <input id="reviewHash" class="commit-hash" value="${escapeHtml(s.state_hash)}" autocomplete="off" />
      ${previousApplied ? `<button class="secondary small" id="useStaleHash">Load prior hash to test refusal</button>` : ""}
      <label class="confirm-row">
        <input type="checkbox" id="confirmReview">
        <span>I reviewed revision <strong>${escapeHtml(s.revision)}</strong> and intend to commit the hash shown above.</span>
      </label>
      <button class="primary" id="commitState" ${s.status === "COMMITTED" ? "disabled" : ""}>
        ${s.status === "COMMITTED" ? "Already committed" : "Commit reviewed state"}
      </button>
    </div>
  `;

  $("#useStaleHash")?.addEventListener("click", () => {
    $("#reviewHash").value = previousApplied.before_hash;
    $("#confirmReview").checked = false;
    toast("Prior hash loaded. Commit should be refused as stale.");
  });

  $("#commitState")?.addEventListener("click", async () => {
    try {
      const reviewedHash = $("#reviewHash").value.trim();
      const confirmed = $("#confirmReview").checked;
      const payload = await api("/api/commit", {
        method: "POST",
        body: JSON.stringify({ reviewed_hash: reviewedHash, confirmed }),
      });
      current = payload;
      renderAll(payload);
      toast(payload.latest_transaction.status === "COMMITTED"
        ? "Commit accepted by current-hash guard."
        : `Commit not applied: ${payload.latest_transaction.status}`);
    } catch (error) {
      toast(error.message);
    }
  });
}

function renderImpact(data) {
  const impact = data.impact;
  const artifact = data.artifact || {};
  $("#impactPanel").innerHTML = `
    <div class="eyebrow">CONSEQUENCE</div>
    <h2>Current derived impact</h2>
    ${impact ? `
      <div class="impact-grid">
        <div class="impact-cell">
          <div class="state-label">AFFECTED TRIPS</div>
          <div class="impact-number">${escapeHtml(impact.affected_trip_count)}</div>
        </div>
        <div class="impact-cell">
          <div class="state-label">SKIPPED STOP-TIMES</div>
          <div class="impact-number">${escapeHtml(impact.skipped_stop_time_count)}</div>
        </div>
      </div>
      <div class="evidence-row"><span>Trips</span><strong>${escapeHtml(impact.affected_trip_ids.join(", "))}</strong></div>
      <div class="evidence-row"><span>Window</span><strong>${escapeHtml(impact.effective_window.join(" → "))}</strong></div>
      <div class="evidence-row"><span>Local artifact</span><strong>${escapeHtml(artifact.status)}</strong></div>
      <div class="evidence-row"><span>Artifact SHA</span><strong class="hash-value">${escapeHtml(shortHash(artifact.sha256))}</strong></div>
    ` : `<div class="empty-note">Impact becomes available after route, direction and end time are resolved.</div>`}
  `;
}

function renderEvidence(data) {
  const evidence = data.external_evidence || {};
  const validator = evidence.validator || {};
  const consumer = evidence.official_bindings_consumer || {};
  const warnings = validator.warnings || [];

  $("#evidencePanel").innerHTML = `
    <div class="eyebrow">EXTERNAL ACCEPTANCE RECEIPT</div>
    <h2>Independent proof</h2>
    <p>This evidence belongs to the bounded synthetic fixture reference artifact. It is not a production-agency claim.</p>
    <div class="evidence-row"><span>Official bindings consumer</span><strong class="${consumer.pass ? "pass" : "warn"}">${consumer.pass ? "PASS" : "NOT PROVEN"}</strong></div>
    <div class="evidence-row"><span>Canonical validator errors</span><strong class="${validator.blocking_error_group_count === 0 ? "pass" : "warn"}">${escapeHtml(validator.blocking_error_group_count ?? "—")}</strong></div>
    <div class="evidence-row"><span>Validator commit</span><strong class="hash-value">${escapeHtml(shortHash(validator.commit))}</strong></div>
    <div class="evidence-row"><span>Workflow run</span><strong>${escapeHtml(evidence.workflow_run_id ?? "—")}</strong></div>
    ${warnings.length ? `
      <ul class="warning-list">
        ${warnings.map((warning) => `<li>${escapeHtml(warning)}</li>`).join("")}
      </ul>` : ""}
  `;
}

function renderAll(data) {
  current = data;
  renderConnection(data);
  renderChangeHeader(data);
  renderLatestTransaction(data);
  renderState(data);
  renderTimeline(data);
  renderCommit(data);
  renderImpact(data);
  renderEvidence(data);
}

async function refresh() {
  try {
    renderAll(await api("/api/change"));
  } catch (error) {
    $("#connection").textContent = "CORE UNAVAILABLE";
    $("#connection").className = "connection-badge bad";
    toast(error.message);
  }
}

$("#amendForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = $("#amendText").value.trim();
  if (!text) {
    toast("Enter an operational instruction first.");
    return;
  }
  try {
    const payload = await api("/api/amend/direct", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    renderAll(payload);
    toast(`Transaction: ${payload.latest_transaction.status}`);
  } catch (error) {
    toast(error.message);
  }
});

$("#fillInitial").addEventListener("click", () => {
  $("#amendText").value = "Route 55 west, skip King Edward and Cumberland until 9:30.";
  $("#amendText").focus();
});
$("#fillCorrection").addEventListener("click", () => {
  $("#amendText").value = "Wait, keep Cumberland. Make it 10.";
  $("#amendText").focus();
});
$("#fillMalformed").addEventListener("click", () => {
  $("#amendText").value = "Wait, keep Cumberland. Make it.";
  $("#amendText").focus();
});
$("#resetDemo").addEventListener("click", async () => {
  if (!window.confirm("Reset the local staged change to revision 1?")) return;
  try {
    const payload = await api("/api/reset-demo", {
      method: "POST",
      body: JSON.stringify({}),
    });
    $("#amendText").value = "";
    renderAll(payload);
    toast("Demo reset to seeded revision 1.");
  } catch (error) {
    toast(error.message);
  }
});

refresh();
