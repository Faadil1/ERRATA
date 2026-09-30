
const $ = (selector) => document.querySelector(selector);

let current = null;
let errataSessionToken = window.localStorage.getItem("errata.session-token") || null;

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

async function api(path, options = {}, allowSessionRetry = true) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (errataSessionToken) {
    headers["X-ERRATA-Session"] = errataSessionToken;
  }

  const response = await fetch(path, {
    ...options,
    headers,
  });

  let payload;
  try {
    payload = await response.json();
  } catch {
    payload = {};
  }

  if (response.status === 401 && errataSessionToken && allowSessionRetry) {
    errataSessionToken = null;
    window.localStorage.removeItem("errata.session-token");
    return api(path, options, false);
  }

  if (!response.ok) {
    throw new Error(payload.detail || payload.error || `HTTP ${response.status}`);
  }

  if (payload?._session_token) {
    errataSessionToken = payload._session_token;
    window.localStorage.setItem("errata.session-token", errataSessionToken);
    delete payload._session_token;
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
  const chronological = [...(data.history || [])];
  const history = [...chronological].reverse();
  const applied = chronological.filter((item) => item.status === "APPLIED");
  const revisions = [
    { revision: 1, label: "seeded context" },
    ...applied.map((item) => ({
      revision: item.revision,
      label: (item.diff || []).map((d) => d.field).join(" · ") || "amendment",
    })),
  ];
  const seen = new Set();
  const uniqueRevisions = revisions.filter((item) => {
    const key = String(item.revision);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  $("#timeline").innerHTML = `
    <div class="panel-heading">
      <div>
        <div class="eyebrow">ONE IDENTITY / VERSIONED REPAIR</div>
        <h2>Same change_id. Minimal revisions. No fork.</h2>
      </div>
      <div class="eyebrow">${history.length} EVENT${history.length === 1 ? "" : "S"}</div>
    </div>
    <div class="revision-rail">
      ${uniqueRevisions.map((item) => `
        <div class="revision-node ${Number(item.revision) === Number(data.state.revision) ? "active" : ""}">
          <div class="rev">rev${escapeHtml(item.revision)}</div>
          <div class="same-id">${escapeHtml(data.state.change_id)}</div>
          <div class="same-id">${escapeHtml(item.label)}</div>
        </div>
      `).join("")}
    </div>
    ${history.length ? `<div class="timeline-list">${history.map((item) => `
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
        </div>`).join("")}</div>`
      : `<div class="empty-note">Revision 1 is seeded. Voice amendments will repair this same change identity.</div>`}
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

function renderConsumer(data) {
  const s = data.state || {};
  const impact = data.impact || null;
  const artifact = data.artifact || {};
  const evidence = data.external_evidence || {};
  const referenceConsumer = evidence.official_bindings_consumer || {};
  const decodedConsumer = data.downstream_consumer || {};
  const route = String(s.route || "—").replace(/^R(?=\d+$)/, "");
  const direction = s.direction === 1 || s.direction === "1"
    ? "west"
    : s.direction === 0 || s.direction === "0"
      ? "east"
      : "direction pending";
  const skipped = Array.isArray(s.skip_stops)
    ? s.skip_stops.map((item) => item.stop_name || item.stop_id)
    : [];
  const hasOperationalShape = Boolean(s.route && s.end_time);
  const message = hasOperationalShape
    ? `Service change on route ${route} ${direction} until ${String(s.end_time).slice(0, 5)}.`
    : "No rider-facing service change is materialized yet.";
  const stopLine = skipped.length
    ? `Stops not served: ${skipped.join(", ")}.`
    : "No skipped stops in the current candidate.";

  $("#consumerPanel").innerHTML = `
    <div class="eyebrow">DOWNSTREAM CONSUMER PREVIEW</div>
    <h2>What another transit system would receive</h2>
    <p>The card below is rendered from the same canonical state and GTFS-RT candidate — not from separate demo copy.</p>
    <div class="consumer-phone">
      <div class="consumer-phone-top">
        <span>DEMO RIDER FEED</span>
        <span>${escapeHtml(s.status || "STAGED")}</span>
      </div>
      <div class="consumer-route">Route ${escapeHtml(route)} · ${escapeHtml(direction)}</div>
      <div class="consumer-message">${escapeHtml(message)} ${escapeHtml(stopLine)}</div>
      <div class="consumer-proof">
        <span>same change_id · ${escapeHtml(s.change_id || "—")} · rev ${escapeHtml(s.revision ?? "—")}</span>
        <span>GTFS-RT candidate · ${escapeHtml(artifact.status || "NOT_GENERATED")}</span>
        <span>independent wire decode · ${escapeHtml(decodedConsumer.status || "NOT_AVAILABLE")}</span>
        <span>decoded feed · v${escapeHtml(decodedConsumer.feed_version || "—")} · ${escapeHtml(decodedConsumer.entity_count ?? "—")} entities</span>
        <span>decoded trips · ${escapeHtml((decodedConsumer.trip_ids || []).join(", ") || "—")}</span>
        <span>decoded skipped stops · ${escapeHtml((decodedConsumer.skipped_stop_ids || []).join(", ") || "—")}</span>
        <span>artifact · ${escapeHtml(shortHash(decodedConsumer.sha256 || artifact.sha256))}</span>
        <span>official bindings reference · ${referenceConsumer.pass ? "PASS" : "REFERENCE ONLY"}</span>
      </div>
    </div>
    <div class="consumer-truth">
      This panel is decoded from the generated protobuf through ERRATA's independent minimal wire consumer. It is not a live STO/agency publication or a claim that Transit/Google consumed this session.
    </div>
  `;
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
  renderConsumer(data);
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
$("#fillBilingual")?.addEventListener("click", () => {
  $("#amendText").value = "Wait, garde Cumberland. Make it 10.";
  $("#amendText").focus();
});
$("#jumpToVoice")?.addEventListener("click", () => {
  document.querySelector(".voice-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
  window.setTimeout(() => $("#startVoice")?.focus(), 350);
});
$("#resetDemo").addEventListener("click", async () => {
  if (!window.confirm("Reset the local staged change to revision 1?")) return;
  try {
    const payload = await api("/api/reset-demo", {
      method: "POST",
      body: JSON.stringify({}),
    });
    $("#amendText").value = "";
    voiceCapture.ghostAttempt = null;
    renderGhostAttempt();
    renderAll(payload);
    toast("Demo reset to seeded revision 1.");
  } catch (error) {
    toast(error.message);
  }
});


// --- Recording-audit refinements: safer reference flow + above-fold truth ---
function referencePhase(data) {
  const history = data.history || [];
  const applied = history.filter((item) => item.status === "APPLIED").length;
  const stale = history.some((item) => item.status === "STALE_REVIEW");
  if (data.state.status === "COMMITTED") return 5;
  if (stale) return 4;
  if (applied >= 2) return 3;
  if (applied >= 1) return 2;
  return 1;
}

function renderReferenceGuide(data) {
  const phase = referencePhase(data);
  const steps = [
    ["1", "Stage base change"],
    ["2", "Apply correction"],
    ["3", "Test stale review"],
    ["4", "Commit current hash"],
  ];
  const completeAll = phase === 5;
  const advisory = phase === 2
    ? "Reference walkthrough: apply the correction next. Revision 2 is technically commit-ready, but committing now seals the change."
    : phase === 5
      ? "Reference walkthrough complete. Reset the demo before testing another amendment or negative path."
      : "This guide is presentation-only; canonical state and commit authority remain controlled by the shared core.";

  $("#referenceGuide").innerHTML = `
    <div class="guide-head">
      <div>
        <div class="eyebrow">REFERENCE WALKTHROUGH</div>
        <h2>Prove the amendment, refusal, then commit</h2>
      </div>
      <div class="guide-phase">${completeAll ? "COMPLETE" : "STEP " + phase + " / 4"}</div>
    </div>
    <div class="guide-steps">
      ${steps.map(([num, label], index) => {
        const step = index + 1;
        const state = completeAll || step < phase ? "complete" : step === phase ? "active" : "pending";
        return `<div class="guide-step ${state}">
          <span class="guide-num">${num}</span>
          <span>${escapeHtml(label)}</span>
        </div>`;
      }).join("")}
    </div>
    <div class="guide-advisory">${escapeHtml(advisory)}</div>
  `;
}

renderChangeHeader = function(data) {
  const s = data.state;
  const skips = s.skip_stops?.length
    ? s.skip_stops.map((x) => x.stop_name).join(", ")
    : "None";
  const windowText = s.start_time || s.end_time
    ? `${s.start_time || "—"} → ${s.end_time || "—"}`
    : "—";
  $("#changeHeader").innerHTML = `
    <div class="change-topline">
      <div>
        <div class="eyebrow">CANONICAL CHANGE</div>
        <div class="change-id">${escapeHtml(s.change_id)}</div>
      </div>
      <div class="header-meta">
        <span class="truth-badge" title="${escapeHtml(data.truth_label)}">${escapeHtml(
          String(data.truth_label || "").includes("VERCEL")
            ? "VERCEL · SIGNED SESSION"
            : "LOCAL · BOUNDED"
        )}</span>
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
    <div class="canonical-strip">
      <div class="canonical-cell">
        <div class="metric-label">ROUTE</div>
        <strong>${escapeHtml(s.route || "—")}</strong>
      </div>
      <div class="canonical-cell">
        <div class="metric-label">DIRECTION</div>
        <strong>${escapeHtml(directionLabel(s.direction))}</strong>
      </div>
      <div class="canonical-cell">
        <div class="metric-label">WINDOW</div>
        <strong>${escapeHtml(windowText)}</strong>
      </div>
      <div class="canonical-cell">
        <div class="metric-label">SKIPPED</div>
        <strong>${escapeHtml(skips)}</strong>
      </div>
    </div>
  `;
};

renderLatestTransaction = function(data) {
  const tx = data.latest_transaction || {};
  const ops = tx.parsed_operations || [];
  const diff = tx.diff || [];
  const rows = diff.map((d) => `
    <tr>
      <td>${escapeHtml(d.field)}</td>
      <td class="before">${escapeHtml(fmt(d.before))}</td>
      <td class="after">${escapeHtml(fmt(d.after))}</td>
    </tr>`).join("");

  let narrative = "";
  if (tx.text) {
    narrative = `<div class="transcript-quote">“${escapeHtml(tx.text)}”</div>`;
  } else if (tx.status === "COMMITTED") {
    const authority = tx.receipt?.authority || tx.source || "explicit human review";
    narrative = `<div class="protected-action-note">Current hash committed by <strong>${escapeHtml(authority)}</strong>. Canonical semantics did not change.</div>`;
  } else if (tx.status === "STALE_REVIEW") {
    narrative = `<div class="protected-action-note">Commit refused because the reviewed hash is stale. Canonical state remains unchanged.</div>`;
  } else if (tx.status && tx.status !== "EMPTY") {
    narrative = `<div class="protected-action-note">${escapeHtml(tx.reason || tx.source || "Protected action recorded.")}</div>`;
  } else {
    narrative = `<div class="empty-note">No operator amendment yet.</div>`;
  }

  $("#latestTransaction").innerHTML = `
    <div class="panel-heading">
      <div>
        <div class="eyebrow">LATEST TRANSACTION</div>
        <h2>${statusBadge(tx.status || "EMPTY")}</h2>
      </div>
      <div class="eyebrow">REV ${escapeHtml(tx.before_revision ?? "—")} → ${escapeHtml(tx.revision ?? data.state.revision)}</div>
    </div>
    ${narrative}
    ${ops.length ? `<div class="ops-row">${ops.map((op) => `<span class="op-chip">${escapeHtml(op)}</span>`).join("")}</div>` : ""}
    ${tx.reason ? `<div class="reason-box">${escapeHtml(tx.reason)}</div>` : ""}
    ${rows ? `
      <table class="diff-table">
        <thead><tr><th>FIELD</th><th>BEFORE</th><th>AFTER</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>` : ""}
  `;
};

renderCommit = function(data) {
  const s = data.state;
  const phase = referencePhase(data);
  const commitReady = data.capabilities?.commit_ready === true;
  const isCommitted = s.status === "COMMITTED";
  const previousApplied = [...(data.history || [])]
    .reverse()
    .find((item) => item.status === "APPLIED" && item.before_hash && item.before_hash !== s.state_hash);

  if (isCommitted) {
    $("#commitPanel").innerHTML = `
      <div class="eyebrow">PROTECTED HUMAN ACTION</div>
      <h2>Reviewed state committed</h2>
      <div class="sealed-box">
        <div class="state-label">COMMITTED HASH</div>
        <div class="commit-hash">${escapeHtml(s.committed_hash || s.state_hash)}</div>
        <p>This change is sealed. Reset the demo or create a new change before authoring another amendment.</p>
      </div>
    `;
    return;
  }

  const advisory = phase === 2
    ? `<div class="commit-advisory">Reference walkthrough: correction is still pending. This revision is valid and may be committed, but doing so will intentionally end the change before the hero correction.</div>`
    : "";

  $("#commitPanel").innerHTML = `
    <div class="eyebrow">PROTECTED HUMAN ACTION</div>
    <h2>Commit reviewed state</h2>
    <p>The backend commits only if the reviewed hash still matches canonical state and blocking validators pass.</p>
    ${advisory}
    <div class="commit-box">
      <label for="reviewHash">Reviewed state hash</label>
      <input id="reviewHash" class="commit-hash" value="${escapeHtml(s.state_hash)}" autocomplete="off" />
      ${previousApplied ? `<button class="secondary small" id="useStaleHash">Load prior hash to test refusal</button>` : ""}
      <label class="confirm-row">
        <input type="checkbox" id="confirmReview">
        <span>I reviewed revision <strong>${escapeHtml(s.revision)}</strong> and intend to commit the hash shown above.</span>
      </label>
      <button class="primary" id="commitState" ${commitReady ? "" : "disabled"}>
        ${commitReady ? "Commit reviewed state" : "Commit not ready"}
      </button>
    </div>
  `;

  $("#useStaleHash")?.addEventListener("click", () => {
    $("#reviewHash").value = previousApplied.before_hash;
    $("#confirmReview").checked = false;
    toast("Prior hash loaded. Confirm review to test stale-hash refusal.");
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
};

function applyInteractionLocks(data) {
  const canAuthor = data.capabilities?.can_author !== false;
  const controls = ["#amendText", "#fillInitial", "#fillCorrection", "#fillMalformed", "#amendForm button[type='submit']"];
  controls.forEach((selector) => {
    const node = $(selector);
    if (node) node.disabled = !canAuthor;
  });
  const notice = $("#authorNotice");
  const panel = $(".transaction-panel");
  if (!canAuthor) {
    notice.innerHTML = `<div class="lock-notice"><strong>Change sealed.</strong> This committed change cannot accept further amendments. Reset the demo to start another staged change.</div>`;
    panel?.classList.add("locked");
  } else {
    notice.innerHTML = "";
    panel?.classList.remove("locked");
  }
}

renderAll = function(data) {
  current = data;
  renderConnection(data);
  renderChangeHeader(data);
  renderReferenceGuide(data);
  renderLatestTransaction(data);
  renderState(data);
  renderTimeline(data);
  renderCommit(data);
  renderConsumer(data);
  renderImpact(data);
  renderEvidence(data);
  applyInteractionLocks(data);
  syncVoiceControls(data);
};

// --- Integrated AssemblyAI browser voice capture ---
const VOICE_COPY = {
  greeting: "Hi. I’m Errata. Tell me the service change.",
  ready: "Got it. I have a safe interpretation. Review it, then apply.",
  applied: "Applied. The new revision is staged. Review before continuing.",
  incompleteTime: "I need the new end time. Say: make it 10.",
};

const voiceCapture = {
  ws: null,
  mediaStream: null,
  audioContext: null,
  sourceNode: null,
  workletNode: null,
  silentGain: null,
  finals: [],
  finalTurns: new Map(),
  partial: "",
  connected: false,
  applying: false,
  awaitingBoundaryFinal: false,
  boundaryTimer: null,
  previewTimer: null,
  previewRequest: 0,
  preview: null,
  sessionId: null,
  guidanceEnabled: true,
  speaking: false,
  speechToken: 0,
  lastGuidance: null,
  lastGuidanceSignature: "",
  guidanceVoiceName: null,
  guidanceVoices: [],
  neuralTtsAvailable: false,
  neuralVoice: null,
  neuralVoiceLabel: "AI33 voice",
  ttsProvider: "browser",
  currentAudio: null,
  currentAudioUrl: null,
  echoCooldownMs: 750,
  echoCooldownUntil: 0,
  guidanceRequestToken: 0,
  lastTtsLatencyMs: null,
  lastTtsCreditCost: null,
  lastTtsCacheHit: false,
  replaceBufferOnNextSpeech: false,
  speechStatusTimer: null,
  connectStartedAt: null,
  lastConnectMs: null,
  lastPreviewMs: null,
  guidanceGenerating: false,
  neuralPrefetches: new Map(),
  readyPrefetchStarted: false,
  evidenceEvents: [],
  ghostAttempt: null,
  speechMode: "balanced",
  assemblyContextUpdates: 0,
  assemblyKeytermUpdates: 0,
  lastAssemblyContext: null,
  bargeInEnabled: false,
  bargeInCount: 0,
};

function recordVoiceEvidence(type, detail = {}) {
  voiceCapture.evidenceEvents.push({
    at: new Date().toISOString(),
    type,
    ...detail,
  });
  if (voiceCapture.evidenceEvents.length > 80) {
    voiceCapture.evidenceEvents.splice(0, voiceCapture.evidenceEvents.length - 80);
  }
}

function renderGhostAttempt() {
  const node = $("#ghostAttempt");
  if (!node) return;
  const ghost = voiceCapture.ghostAttempt;
  if (!ghost) {
    node.classList.add("hidden");
    node.innerHTML = "";
    return;
  }

  node.classList.remove("hidden");
  node.innerHTML = `
    <div class="ghost-attempt-head">
      <span class="ghost-attempt-label">GHOST SPEECH · NOT CANONICAL</span>
      <span class="ghost-attempt-zero">0 effect · hash unchanged</span>
    </div>
    <div class="ghost-attempt-text">“${escapeHtml(ghost.text)}”</div>
    <div class="ghost-attempt-meta">
      ${escapeHtml(ghost.status || "SUPERSEDED")} · canonical rev ${escapeHtml(ghost.revision ?? "—")} · ${escapeHtml(shortHash(ghost.hash))}
    </div>
  `;
}

function setVoiceStatus(status, label = status) {
  const node = $("#voiceStatus");
  if (!node) return;
  node.dataset.status = status;
  node.textContent = label;
}

function setVoiceEngineUI() {
  const engine = $("#voiceEngine");
  const disclosure = $("#voiceDisclosure");
  const neuralSelect = $("#neuralVoice");
  const fallbackSelect = $("#guidanceVoice");

  if (engine) {
    engine.textContent = voiceCapture.neuralTtsAvailable
      ? `AI33 PRO · ${voiceCapture.neuralVoiceLabel}`
      : "BROWSER FALLBACK";
  }
  if (disclosure) {
    const metrics = voiceCapture.lastTtsLatencyMs != null
      ? ` · ${(voiceCapture.lastTtsLatencyMs / 1000).toFixed(2)}s`
      : "";
    const credits = voiceCapture.lastTtsCreditCost != null
      ? ` · ${voiceCapture.lastTtsCreditCost} new credits`
      : "";
    const cache = voiceCapture.lastTtsCacheHit ? " · cached" : "";
    disclosure.textContent = voiceCapture.neuralTtsAvailable
      ? `AI-generated voice · AI33 v3 TTS → ElevenLabs${metrics}${credits}${cache}`
      : "Uses the selected Edge/Windows voice.";
  }
  if (neuralSelect) neuralSelect.disabled = !voiceCapture.neuralTtsAvailable;
  if (fallbackSelect) {
    fallbackSelect.title = voiceCapture.neuralTtsAvailable
      ? "Used automatically only if neural TTS is unavailable."
      : "Active browser guidance voice.";
  }
}

async function loadVoiceCapabilities() {
  try {
    const capabilities = await api("/api/voice-capabilities");
    const neural = capabilities?.neural_tts || {};
    voiceCapture.neuralTtsAvailable = neural.available === true;
    voiceCapture.neuralVoice = neural.default_voice || null;
    voiceCapture.neuralVoiceLabel = neural.voices?.[0]?.label || "AI33 voice";
    voiceCapture.echoCooldownMs = Number(capabilities?.echo_cooldown_ms) || 750;
    const neuralSelect = $("#neuralVoice");
    if (neuralSelect) {
      const voices = Array.isArray(neural.voices) ? neural.voices : [];
      neuralSelect.innerHTML = voices.length
        ? voices.map((voice) =>
            `<option value="${escapeHtml(voice.id)}">${escapeHtml(voice.label || voice.id)}</option>`
          ).join("")
        : '<option value="">No AI33 voice configured</option>';
      if (voiceCapture.neuralVoice) neuralSelect.value = voiceCapture.neuralVoice;
    }
  } catch {
    voiceCapture.neuralTtsAvailable = false;
  }
  setVoiceEngineUI();
}

function assemblyAIKeytermsForState(data = current) {
  const terms = new Set(["King Edward", "Cumberland", "Route 55"]);
  const state = data?.state || {};
  if (state.route) {
    const spokenRoute = String(state.route).replace(/^R(?=\d+$)/, "");
    terms.add(`Route ${spokenRoute}`);
  }
  for (const stop of state.skip_stops || []) {
    if (stop?.stop_name) terms.add(String(stop.stop_name));
  }
  return [...terms].filter((term) => term.length <= 50).slice(0, 100);
}

function updateAssemblyAIConfiguration({ agentContext = null, keyterms = null, reason = "runtime" } = {}) {
  const ws = voiceCapture.ws;
  if (!ws || ws.readyState !== WebSocket.OPEN) return false;

  const payload = { type: "UpdateConfiguration" };
  if (agentContext) {
    payload.agent_context = String(agentContext).slice(0, 1750);
  }
  if (Array.isArray(keyterms)) {
    payload.keyterms_prompt = keyterms.slice(0, 100);
  }
  if (!payload.agent_context && !payload.keyterms_prompt) return false;

  try {
    ws.send(JSON.stringify(payload));
    if (payload.agent_context) {
      voiceCapture.assemblyContextUpdates += 1;
      voiceCapture.lastAssemblyContext = payload.agent_context;
    }
    if (payload.keyterms_prompt) {
      voiceCapture.assemblyKeytermUpdates += 1;
    }
    recordVoiceEvidence("ASSEMBLYAI_UPDATE_CONFIGURATION", {
      reason,
      agent_context: payload.agent_context || null,
      keyterms_prompt: payload.keyterms_prompt || null,
      speech_model: "universal-3-5-pro",
      mode: voiceCapture.speechMode,
    });
    renderVoiceMetrics();
    return true;
  } catch {
    return false;
  }
}

function refreshAssemblyAIStateBias(data = current, reason = "canonical-state") {
  return updateAssemblyAIConfiguration({
    keyterms: assemblyAIKeytermsForState(data),
    reason,
  });
}

function publishAssemblyAIAgentContext(text, reason = "agent-reply-complete") {
  if (!text) return false;
  return updateAssemblyAIConfiguration({
    agentContext: text,
    reason,
  });
}

function enterSpeechGuard() {
  voiceCapture.speaking = true;
  voiceCapture.echoCooldownUntil = Number.POSITIVE_INFINITY;
  if (voiceCapture.speechStatusTimer) {
    window.clearTimeout(voiceCapture.speechStatusTimer);
    voiceCapture.speechStatusTimer = null;
  }
}

function leaveSpeechGuard() {
  voiceCapture.speaking = false;
  voiceCapture.echoCooldownUntil = performance.now() + voiceCapture.echoCooldownMs;
  if (voiceCapture.connected && !voiceCapture.applying) {
    setVoiceStatus("BUFFERING", "ECHO COOLDOWN");
    if (voiceCapture.speechStatusTimer) {
      window.clearTimeout(voiceCapture.speechStatusTimer);
    }
    voiceCapture.speechStatusTimer = window.setTimeout(() => {
      voiceCapture.speechStatusTimer = null;
      if (
        voiceCapture.connected
        && !voiceCapture.applying
        && !echoGuardActive()
      ) {
        setVoiceStatus("CONNECTED", "VOICE CONNECTED");
      }
    }, voiceCapture.echoCooldownMs + 30);
  }
}

function echoGuardActive() {
  return voiceCapture.speaking || performance.now() < voiceCapture.echoCooldownUntil;
}

function stopCurrentGuidanceAudio() {
  if (voiceCapture.currentAudio) {
    try {
      voiceCapture.currentAudio.pause();
      voiceCapture.currentAudio.currentTime = 0;
    } catch {}
    voiceCapture.currentAudio = null;
  }
  if (voiceCapture.currentAudioUrl) {
    URL.revokeObjectURL(voiceCapture.currentAudioUrl);
    voiceCapture.currentAudioUrl = null;
  }
  if ("speechSynthesis" in window) {
    voiceCapture.speechToken += 1;
    window.speechSynthesis.cancel();
  }
  if (voiceCapture.speaking) leaveSpeechGuard();
}

function guidanceVoiceScore(voice) {
  const name = String(voice?.name || "").toLowerCase();
  const lang = String(voice?.lang || "").toLowerCase();
  let score = 0;

  if (lang.startsWith("en")) score += 40;
  if (lang === "en-ca") score += 24;
  if (lang === "en-us") score += 20;

  if (name.includes("natural")) score += 160;
  if (name.includes("neural")) score += 150;
  if (name.includes("online")) score += 55;

  if (name.includes("aria")) score += 90;
  if (name.includes("ava")) score += 88;
  if (name.includes("jenny")) score += 84;
  if (name.includes("emma")) score += 80;
  if (name.includes("brian")) score += 76;
  if (name.includes("guy")) score += 72;

  if (name.includes("desktop")) score -= 120;
  if (name.includes("david")) score -= 55;
  if (name.includes("zira")) score -= 45;
  if (name.includes("mark")) score -= 35;

  if (voice?.default) score += 8;
  return score;
}

function naturalVoiceLabel(voice) {
  if (!voice) return "Browser default";
  const name = String(voice.name || "Unnamed voice");
  const natural = /natural|neural|online/i.test(name) ? " · natural candidate" : "";
  return `${name} · ${voice.lang || "unknown"}${natural}`;
}

function selectGuidanceVoice() {
  const voices = voiceCapture.guidanceVoices.length
    ? voiceCapture.guidanceVoices
    : ("speechSynthesis" in window ? window.speechSynthesis.getVoices() : []);
  if (!voices.length) return null;

  if (voiceCapture.guidanceVoiceName) {
    const exact = voices.find((voice) => voice.name === voiceCapture.guidanceVoiceName);
    if (exact) return exact;
  }

  return [...voices].sort((a, b) => guidanceVoiceScore(b) - guidanceVoiceScore(a))[0] || null;
}

function populateGuidanceVoices() {
  if (!("speechSynthesis" in window)) return;
  const select = $("#guidanceVoice");
  if (!select) return;

  const voices = window.speechSynthesis.getVoices();
  voiceCapture.guidanceVoices = voices;

  if (!voices.length) {
    select.innerHTML = '<option value="">Browser default voice</option>';
    return;
  }

  const ranked = [...voices].sort((a, b) => {
    const scoreDiff = guidanceVoiceScore(b) - guidanceVoiceScore(a);
    return scoreDiff || String(a.name).localeCompare(String(b.name));
  });

  const previous = voiceCapture.guidanceVoiceName;
  const preferred = previous
    ? ranked.find((voice) => voice.name === previous)
    : ranked[0];

  voiceCapture.guidanceVoiceName = preferred?.name || null;
  select.innerHTML = ranked.map((voice, index) => {
    const selected = voice.name === voiceCapture.guidanceVoiceName ? " selected" : "";
    const prefix = index === 0 ? "Recommended — " : "";
    return `<option value="${escapeHtml(voice.name)}"${selected}>${escapeHtml(prefix + naturalVoiceLabel(voice))}</option>`;
  }).join("");
}

function guidanceSpeechText(guidance) {
  if (guidance?.speech) return String(guidance.speech);
  return [
    guidance?.headline,
    guidance?.message,
    guidance?.next_action,
  ].filter(Boolean).join(". ");
}

function renderVoiceMetrics() {
  const node = $("#voiceMetrics");
  if (!node) return;
  const connect = voiceCapture.lastConnectMs == null
    ? "Connect —"
    : `Connect ${(voiceCapture.lastConnectMs / 1000).toFixed(2)}s`;
  const interpret = voiceCapture.lastPreviewMs == null
    ? "Interpret —"
    : `Interpret ${voiceCapture.lastPreviewMs.toFixed(0)}ms`;
  const voice = voiceCapture.lastTtsLatencyMs == null
    ? "Voice —"
    : `Voice ${(voiceCapture.lastTtsLatencyMs / 1000).toFixed(2)}s${voiceCapture.lastTtsCacheHit ? " cached" : ""}`;
  const context = `STT ${voiceCapture.speechMode} · ctx ${voiceCapture.assemblyContextUpdates} · terms ${voiceCapture.assemblyKeytermUpdates}`;
  const barge = `barge ${voiceCapture.bargeInEnabled ? "on" : "off"} · ${voiceCapture.bargeInCount} interrupt${voiceCapture.bargeInCount === 1 ? "" : "s"}`;
  node.textContent = `${connect} · ${interpret} · ${voice} · ${context} · ${barge}`;
}

function syncGuidanceControls() {
  const skip = $("#skipGuidance");
  if (skip) {
    skip.disabled = !voiceCapture.guidanceGenerating && !voiceCapture.currentAudio;
  }
  const barge = $("#toggleBargeIn");
  if (barge) {
    barge.setAttribute("aria-pressed", voiceCapture.bargeInEnabled ? "true" : "false");
    barge.textContent = voiceCapture.bargeInEnabled ? "Barge-in on" : "Barge-in off";
  }
  renderVoiceMetrics();
}

async function requestNeuralGuidanceAudio(text) {
  const cacheKey = `${voiceCapture.neuralVoice || "default"}::${text}`;
  const existing = voiceCapture.neuralPrefetches.get(cacheKey);
  if (existing) return existing;

  const request = (async () => {
    const response = await fetch("/api/tts/guidance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        voice_id: voiceCapture.neuralVoice,
      }),
    });

    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const payload = await response.json();
        detail = payload.detail || payload.error || detail;
      } catch {}
      throw new Error(detail);
    }

    const serverGenerationMs = Number(response.headers.get("X-ERRATA-TTS-Generation-Ms"));
    const creditCost = response.headers.get("X-ERRATA-TTS-Credit-Cost");
    const cacheHit = response.headers.get("X-ERRATA-TTS-Cache") === "HIT";
    const blob = await response.blob();
    if (!blob.size) throw new Error("Empty neural TTS response");

    const result = {
      blob,
      serverGenerationMs,
      creditCost,
      cacheHit,
    };
    recordVoiceEvidence("TTS_GENERATED", {
      provider: "AI33 Pro",
      speech: text,
      generation_ms: Number.isFinite(serverGenerationMs) ? serverGenerationMs : null,
      credit_cost: creditCost === null || creditCost === "" ? null : Number(creditCost),
      cache_hit: cacheHit,
    });
    return result;
  })();

  voiceCapture.neuralPrefetches.set(cacheKey, request);
  try {
    return await request;
  } catch (error) {
    voiceCapture.neuralPrefetches.delete(cacheKey);
    throw error;
  }
}

function prefetchNeuralGuidance(text) {
  if (!voiceCapture.neuralTtsAvailable || !text) return;
  requestNeuralGuidanceAudio(text).catch(() => {});
}

async function speakBrowserGuidance(text) {
  if (!("speechSynthesis" in window)) return false;

  const token = ++voiceCapture.speechToken;
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  const selectedVoice = selectGuidanceVoice();
  if (selectedVoice) {
    utterance.voice = selectedVoice;
    utterance.lang = selectedVoice.lang || "en-US";
  } else {
    utterance.lang = "en-US";
  }
  utterance.rate = 0.96;
  utterance.pitch = 1;
  utterance.volume = 1;

  enterSpeechGuard();

  return new Promise((resolve) => {
    const finish = (event) => {
      if (token === voiceCapture.speechToken) leaveSpeechGuard();
      if (event?.type === "end") {
        publishAssemblyAIAgentContext(text, "browser-guidance-complete");
      }
      resolve(true);
    };
    utterance.addEventListener("end", finish, { once: true });
    utterance.addEventListener("error", finish, { once: true });
    window.speechSynthesis.speak(utterance);
  });
}

async function speakNeuralGuidance(text, requestToken) {
  const requestStarted = performance.now();
  voiceCapture.guidanceGenerating = true;
  if (voiceCapture.connected) {
    setVoiceStatus("BUFFERING", "AI33 GENERATING VOICE");
  }
  syncGuidanceControls();

  try {
    const result = await requestNeuralGuidanceAudio(text);
    if (requestToken !== voiceCapture.guidanceRequestToken) {
      return false;
    }

    const url = URL.createObjectURL(result.blob);
    const audio = new Audio(url);
    voiceCapture.currentAudio = audio;
    voiceCapture.currentAudioUrl = url;
    voiceCapture.ttsProvider = "ai33";
    voiceCapture.guidanceGenerating = false;

    if (voiceCapture.connected) {
      setVoiceStatus("BUFFERING", "ERRATA SPEAKING");
    }
    enterSpeechGuard();
    syncGuidanceControls();

    await audio.play();
    voiceCapture.lastTtsLatencyMs = Number.isFinite(result.serverGenerationMs)
      ? result.serverGenerationMs
      : Math.round(performance.now() - requestStarted);
    voiceCapture.lastTtsCreditCost =
      result.creditCost === null || result.creditCost === ""
        ? null
        : Number(result.creditCost);
    voiceCapture.lastTtsCacheHit = result.cacheHit;
    recordVoiceEvidence("TTS_PLAYBACK_STARTED", {
      provider: "AI33 Pro",
      speech: text,
      generation_ms: voiceCapture.lastTtsLatencyMs,
      cache_hit: voiceCapture.lastTtsCacheHit,
    });
    setVoiceEngineUI();
    renderVoiceMetrics();

    await new Promise((resolve, reject) => {
      audio.addEventListener("ended", resolve, { once: true });
      audio.addEventListener(
        "error",
        () => reject(new Error("Neural TTS playback failed")),
        { once: true }
      );
    });

    voiceCapture.currentAudio = null;
    URL.revokeObjectURL(url);
    voiceCapture.currentAudioUrl = null;
    leaveSpeechGuard();
    recordVoiceEvidence("TTS_PLAYBACK_COMPLETED", {
      provider: "AI33 Pro",
      speech: text,
      echo_cooldown_ms: voiceCapture.echoCooldownMs,
    });
    publishAssemblyAIAgentContext(text, "ai33-guidance-complete");
    syncGuidanceControls();
    return true;
  } catch (error) {
    voiceCapture.guidanceGenerating = false;
    if (voiceCapture.currentAudioUrl) {
      URL.revokeObjectURL(voiceCapture.currentAudioUrl);
      voiceCapture.currentAudioUrl = null;
    }
    voiceCapture.currentAudio = null;
    if (voiceCapture.speaking) leaveSpeechGuard();
    syncGuidanceControls();
    throw error;
  }
}

async function speakGuidance(text) {
  if (!voiceCapture.guidanceEnabled || !text) return;

  const requestToken = ++voiceCapture.guidanceRequestToken;
  stopCurrentGuidanceAudio();

  if (voiceCapture.neuralTtsAvailable) {
    try {
      const played = await speakNeuralGuidance(text, requestToken);
      if (played || requestToken !== voiceCapture.guidanceRequestToken) return;
    } catch (error) {
      voiceCapture.ttsProvider = "browser";
      toast(`AI33 voice unavailable; using browser fallback. ${error.message}`);
    }
  }

  if (requestToken === voiceCapture.guidanceRequestToken) {
    await speakBrowserGuidance(text);
  }
}

function renderVoiceGuide(guidance, { speak = false, forceSpeak = false } = {}) {
  if (!guidance) return;
  const panel = document.querySelector(".voice-guide");
  const headline = $("#voiceGuideHeadline");
  const message = $("#voiceGuideMessage");
  const next = $("#voiceGuideNext");
  if (!panel || !headline || !message || !next) return;

  panel.dataset.tone = guidance.tone || "neutral";
  headline.textContent = guidance.headline || "ERRATA guide";
  message.textContent = guidance.message || "";
  next.textContent = guidance.next_action
    ? `Next: ${guidance.next_action}`
    : "";

  voiceCapture.lastGuidance = guidance;
  const signature = guidanceSpeechText(guidance);
  if (speak && signature && (forceSpeak || signature !== voiceCapture.lastGuidanceSignature)) {
    voiceCapture.lastGuidanceSignature = signature;
    speakGuidance(signature);
  }
}

function setListeningGuide() {
  renderVoiceGuide({
    tone: "neutral",
    headline: "Listening",
    message: "I am transcribing this turn. Canonical state is still untouched.",
    next_action: "Finish the thought; I will interpret it when the turn closes.",
  });
}

async function previewBufferedVoiceTurn() {
  const text = voiceCapture.finals.join(" ").replace(/\s+/g, " ").trim();
  if (!text || voiceCapture.applying) return;

  const requestId = ++voiceCapture.previewRequest;
  const previewStarted = performance.now();
  renderVoiceGuide({
    tone: "neutral",
    headline: "Checking what I understood",
    message: "I am running this transcript through a disposable copy of the ERRATA core.",
    next_action: "Wait for the interpretation before applying anything.",
  });

  try {
    const preview = await api("/api/preview/voice", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    if (requestId !== voiceCapture.previewRequest) return;
    voiceCapture.lastPreviewMs = performance.now() - previewStarted;
    renderVoiceMetrics();
    voiceCapture.preview = preview;
    if (preview.status !== "READY_TO_APPLY") {
      voiceCapture.ghostAttempt = {
        text,
        status: preview.status,
        revision: preview.canonical_revision,
        hash: preview.canonical_hash,
        reason: preview.reason || null,
      };
      renderGhostAttempt();
    }
    recordVoiceEvidence("VOICE_PREVIEW", {
      text,
      status: preview.status,
      raw_status: preview.raw_status,
      reason: preview.reason || null,
      canonical_unchanged: preview.canonical_unchanged,
      canonical_revision: preview.canonical_revision,
      canonical_hash: preview.canonical_hash,
      candidate_revision: preview.candidate_revision,
      candidate_hash: preview.candidate_hash,
      preview_ms: voiceCapture.lastPreviewMs,
    });
    if (preview.status === "READY_TO_APPLY") {
      prefetchNeuralGuidance(VOICE_COPY.applied);
    }
    // Once a turn has a complete interpretation, any further speech is a new
    // draft attempt until the operator explicitly applies the current one.
    // This prevents retries/restatements from accumulating into one transcript.
    voiceCapture.replaceBufferOnNextSpeech = true;
    renderVoiceGuide(preview.guidance, { speak: true });
  } catch (error) {
    if (requestId !== voiceCapture.previewRequest) return;
    voiceCapture.preview = null;
    voiceCapture.replaceBufferOnNextSpeech = true;
    renderVoiceGuide({
      tone: "blocked",
      headline: "I could not verify this turn",
      message: error.message,
      next_action: "Keep the canonical state unchanged and retry the spoken instruction.",
    }, { speak: true });
  } finally {
    syncVoiceControls(current);
  }
}

function scheduleVoicePreview() {
  if (voiceCapture.previewTimer) window.clearTimeout(voiceCapture.previewTimer);
  voiceCapture.previewTimer = window.setTimeout(() => {
    voiceCapture.previewTimer = null;
    previewBufferedVoiceTurn();
  }, 280);
}

function voiceBufferedText() {
  return [...voiceCapture.finals, voiceCapture.partial]
    .filter(Boolean)
    .join(" ")
    .replace(/\s+/g, " ")
    .trim();
}

function renderVoiceTranscript() {
  const node = $("#voiceTranscript");
  if (!node) return;
  const text = voiceBufferedText();
  node.textContent = text || "No speech buffered.";
  node.classList.toggle("partial", Boolean(voiceCapture.partial));
  syncVoiceControls(current);
}

function clearVoiceBuffer() {
  voiceCapture.finals = [];
  voiceCapture.finalTurns.clear();
  voiceCapture.partial = "";
  voiceCapture.preview = null;
  voiceCapture.replaceBufferOnNextSpeech = false;
  voiceCapture.previewRequest += 1;
  if (voiceCapture.previewTimer) {
    window.clearTimeout(voiceCapture.previewTimer);
    voiceCapture.previewTimer = null;
  }
  renderVoiceTranscript();
}

function syncVoiceControls(data) {
  const canAuthor = data?.capabilities?.can_author !== false;
  const start = $("#startVoice");
  const apply = $("#applyVoice");
  const stop = $("#stopVoice");
  if (start) start.disabled = !canAuthor || voiceCapture.connected || voiceCapture.applying;
  if (apply) {
    apply.disabled = !canAuthor
      || !voiceCapture.connected
      || voiceCapture.applying
      || Boolean(voiceCapture.partial)
      || voiceCapture.preview?.status !== "READY_TO_APPLY";
    apply.title = voiceCapture.preview?.status === "READY_TO_APPLY"
      ? "Apply the reviewed interpretation through the canonical ERRATA core."
      : "ERRATA must safely interpret the completed turn before Apply is enabled.";
  }
  if (stop) stop.disabled = !voiceCapture.connected && !voiceCapture.mediaStream;
}

async function submitBufferedVoiceTurn() {
  if (voiceCapture.applying) return;
  const text = voiceCapture.finals.join(" ").replace(/\s+/g, " ").trim();
  if (!text) {
    setVoiceStatus("BUFFERING", "WAITING FOR FINAL");
    voiceCapture.awaitingBoundaryFinal = false;
    syncVoiceControls(current);
    return;
  }

  voiceCapture.applying = true;
  voiceCapture.awaitingBoundaryFinal = false;
  setVoiceStatus("APPLYING", "APPLYING SPOKEN TURN");
  syncVoiceControls(current);

  try {
    const payload = await api("/api/amend/voice", {
      method: "POST",
      body: JSON.stringify({
        text,
        assemblyai_session_id: voiceCapture.sessionId,
        boundary: "ForceEndpoint",
        client_captured_at: new Date().toISOString(),
      }),
    });
    const tx = payload.latest_transaction || {};
    clearVoiceBuffer();
    renderAll(payload);
    refreshAssemblyAIStateBias(payload, "canonical-amendment-applied");
    setVoiceStatus("CONNECTED", "VOICE CONNECTED");

    if (tx.status === "APPLIED") {
      const stopNames = (payload.state?.skip_stops || []).map((stop) => stop.stop_name);
      const summary = [
        payload.state?.route ? `route ${String(payload.state.route).replace(/^R(?=\d+$)/, "")}` : null,
        payload.state?.direction === 1 || payload.state?.direction === "1"
          ? "west"
          : payload.state?.direction === 0 || payload.state?.direction === "0"
            ? "east"
            : null,
        stopNames.length ? `skipping ${stopNames.join(" and ")}` : null,
        payload.state?.end_time ? `until ${payload.state.end_time.slice(0, 5)}` : null,
      ].filter(Boolean).join(", ");
      renderVoiceGuide({
        tone: "ready",
        headline: `Revision ${payload.state.revision} is staged`,
        message: `Applied through the protected human boundary: ${summary || "the interpreted amendment"}.`,
        next_action: "Review the materialized state and continue with a correction or protected commit.",
        speech: VOICE_COPY.applied,
      }, { speak: true, forceSpeak: true });
    } else {
      renderVoiceGuide({
        tone: "review",
        headline: "The turn was not applied",
        message: tx.reason || "ERRATA requires more review before this can become canonical.",
        next_action: "Restate the missing detail. Canonical state remains protected.",
        speech: "That turn was not applied. Please restate the missing detail.",
      }, { speak: true, forceSpeak: true });
    }

    recordVoiceEvidence("VOICE_APPLY_RESULT", {
      status: tx.status,
      reason: tx.reason || null,
      revision: payload.state?.revision ?? null,
      state_hash: payload.state?.state_hash ?? null,
      source: tx.source || null,
    });
    toast(`Voice transaction: ${tx.status}`);
  } catch (error) {
    setVoiceStatus("ERROR", "VOICE APPLY ERROR");
    renderVoiceGuide({
      tone: "blocked",
      headline: "I could not apply the reviewed turn",
      message: error.message,
      next_action: "Nothing should be assumed changed. Inspect the current revision before retrying.",
    }, { speak: true, forceSpeak: true });
    toast(error.message);
  } finally {
    voiceCapture.applying = false;
    syncVoiceControls(current);
  }
}

async function startVoiceCapture() {
  if (voiceCapture.connected) return;
  if (!navigator.mediaDevices?.getUserMedia || !window.AudioWorkletNode) {
    setVoiceStatus("ERROR", "BROWSER AUDIO UNSUPPORTED");
    toast("This browser does not expose the required microphone/AudioWorklet APIs.");
    return;
  }

  setVoiceStatus("BUFFERING", "CONNECTING VOICE");
  voiceCapture.connectStartedAt = performance.now();
  syncVoiceControls(current);

  const greetingSpeech = VOICE_COPY.greeting;
  prefetchNeuralGuidance(greetingSpeech);

  try {
    const [auth, mediaStream] = await Promise.all([
      api("/api/voice-token"),
      navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
      }),
    ]);

    const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
    const audioContext = new AudioContextCtor();
    await audioContext.audioWorklet.addModule("/pcm-processor.js");

    const sourceNode = audioContext.createMediaStreamSource(mediaStream);
    const workletNode = new AudioWorkletNode(audioContext, "pcm16-downsampler", {
      processorOptions: { targetSampleRate: 16000 },
    });
    const silentGain = audioContext.createGain();
    silentGain.gain.value = 0;
    sourceNode.connect(workletNode);
    workletNode.connect(silentGain);
    silentGain.connect(audioContext.destination);

    const wsUrl = new URL("wss://streaming.assemblyai.com/v3/ws");
    wsUrl.searchParams.set("sample_rate", "16000");
    wsUrl.searchParams.set("speech_model", "universal-3-5-pro");
    wsUrl.searchParams.set("mode", voiceCapture.speechMode);
    wsUrl.searchParams.set("format_turns", "true");
    wsUrl.searchParams.set("agent_context", VOICE_COPY.greeting);
    wsUrl.searchParams.set("language_codes", JSON.stringify(["en", "fr"]));
    wsUrl.searchParams.set(
      "keyterms_prompt",
      JSON.stringify(["King Edward", "Cumberland"])
    );
    wsUrl.searchParams.set("token", auth.token);

    const ws = new WebSocket(wsUrl);
    ws.binaryType = "arraybuffer";

    voiceCapture.ws = ws;
    voiceCapture.mediaStream = mediaStream;
    voiceCapture.audioContext = audioContext;
    voiceCapture.sourceNode = sourceNode;
    voiceCapture.workletNode = workletNode;
    voiceCapture.silentGain = silentGain;

    workletNode.port.onmessage = (event) => {
      const mayStreamDuringPlayback =
        voiceCapture.bargeInEnabled && voiceCapture.speaking;
      if (
        voiceCapture.ws?.readyState === WebSocket.OPEN
        && (!echoGuardActive() || mayStreamDuringPlayback)
      ) {
        voiceCapture.ws.send(event.data);
      }
    };

    ws.addEventListener("open", () => {
      voiceCapture.connected = true;
      voiceCapture.lastConnectMs = voiceCapture.connectStartedAt == null
        ? null
        : performance.now() - voiceCapture.connectStartedAt;
      renderVoiceMetrics();
      recordVoiceEvidence("VOICE_CONNECTED", {
        connect_ms: voiceCapture.lastConnectMs,
      });
      voiceCapture.lastAssemblyContext = VOICE_COPY.greeting;
      recordVoiceEvidence("ASSEMBLYAI_STREAM_CONFIG", {
        speech_model: "universal-3-5-pro",
        mode: voiceCapture.speechMode,
        language_codes: ["en", "fr"],
        context_carryover: "provider-default-on",
        agent_context_seeded: true,
        keyterms_prompt: assemblyAIKeytermsForState(current),
      });
      refreshAssemblyAIStateBias(current, "voice-session-open");
      setVoiceStatus("CONNECTED", "VOICE CONNECTED");
      syncVoiceControls(current);
      renderVoiceGuide({
        tone: "ready",
        headline: "Hello — I’m Errata",
        message: "Tell me the transit service change you need. I will show you what I understood and guide you if something is missing.",
        next_action: "Speak naturally. I will not change canonical state until you explicitly apply the interpreted turn.",
        speech: greetingSpeech,
      }, { speak: true, forceSpeak: true });
      toast("Microphone connected. ERRATA guidance is active.");
    });

    ws.addEventListener("message", async (event) => {
      let message;
      try {
        message = JSON.parse(event.data);
      } catch {
        return;
      }

      if (message.type === "Begin") {
        voiceCapture.sessionId = message.id || null;
        recordVoiceEvidence("ASSEMBLYAI_SESSION_BEGIN", {
          session_id: voiceCapture.sessionId,
        });
        return;
      }

      if (message.type === "SpeechStarted") {
        if (
          voiceCapture.bargeInEnabled
          && (voiceCapture.speaking || voiceCapture.currentAudio || voiceCapture.guidanceGenerating)
        ) {
          voiceCapture.bargeInCount += 1;
          voiceCapture.guidanceRequestToken += 1;
          voiceCapture.guidanceGenerating = false;
          stopCurrentGuidanceAudio();
          recordVoiceEvidence("VOICE_BARGE_IN", {
            trigger: "AssemblyAI SpeechStarted",
            count: voiceCapture.bargeInCount,
            canonical_revision: current?.state?.revision ?? null,
            canonical_hash: current?.state?.state_hash ?? null,
            canonical_unchanged: true,
          });
          setVoiceStatus("BUFFERING", "BARGE-IN · LISTENING");
          syncGuidanceControls();
        }
        return;
      }

      if (message.type !== "Turn") return;
      const transcript = String(message.transcript || "").trim();

      if (message.end_of_turn) {
        if (transcript) {
          const turnKey = String(
            message.turn_order
            ?? message.turn_id
            ?? message.id
            ?? `turn-${voiceCapture.finalTurns.size + 1}`
          );
          voiceCapture.finalTurns.set(turnKey, transcript);
          voiceCapture.finals = Array.from(voiceCapture.finalTurns.values());
        }
        voiceCapture.partial = "";
        renderVoiceTranscript();

        if (voiceCapture.awaitingBoundaryFinal) {
          if (voiceCapture.boundaryTimer) {
            window.clearTimeout(voiceCapture.boundaryTimer);
            voiceCapture.boundaryTimer = null;
          }
          await previewBufferedVoiceTurn();
          if (voiceCapture.preview?.status === "READY_TO_APPLY") {
            await submitBufferedVoiceTurn();
          } else {
            voiceCapture.awaitingBoundaryFinal = false;
            setVoiceStatus("BUFFERING", "NEEDS CLARIFICATION");
            syncVoiceControls(current);
          }
        } else {
          setVoiceStatus("BUFFERING", "VOICE INTERPRETING");
          scheduleVoicePreview();
        }
      } else {
        if (transcript && !voiceCapture.readyPrefetchStarted) {
          voiceCapture.readyPrefetchStarted = true;
          prefetchNeuralGuidance(VOICE_COPY.ready);
        }
        if (transcript && (voiceCapture.guidanceGenerating || voiceCapture.currentAudio)) {
          voiceCapture.guidanceRequestToken += 1;
          voiceCapture.guidanceGenerating = false;
          stopCurrentGuidanceAudio();
          recordVoiceEvidence("VOICE_REPLY_CANCELLED_BY_PARTIAL", {
            transcript,
            canonical_revision: current?.state?.revision ?? null,
            canonical_hash: current?.state?.state_hash ?? null,
            canonical_unchanged: true,
          });
          syncGuidanceControls();
        }
        if (voiceCapture.replaceBufferOnNextSpeech && transcript) {
          if (voiceCapture.preview && voiceCapture.finals.length) {
            voiceCapture.ghostAttempt = {
              text: voiceCapture.finals.join(" ").replace(/\s+/g, " ").trim(),
              status: voiceCapture.preview.status === "READY_TO_APPLY"
                ? "SUPERSEDED_BEFORE_APPLY"
                : voiceCapture.preview.status,
              revision: voiceCapture.preview.canonical_revision,
              hash: voiceCapture.preview.canonical_hash,
            };
            renderGhostAttempt();
            recordVoiceEvidence("VOICE_DRAFT_SUPERSEDED", {
              text: voiceCapture.ghostAttempt.text,
              canonical_revision: voiceCapture.ghostAttempt.revision,
              canonical_hash: voiceCapture.ghostAttempt.hash,
              canonical_unchanged: true,
            });
          }
          voiceCapture.finals = [];
          voiceCapture.finalTurns.clear();
          voiceCapture.partial = "";
          voiceCapture.preview = null;
          voiceCapture.previewRequest += 1;
          voiceCapture.replaceBufferOnNextSpeech = false;
          if (voiceCapture.previewTimer) {
            window.clearTimeout(voiceCapture.previewTimer);
            voiceCapture.previewTimer = null;
          }
        }
        voiceCapture.partial = transcript;
        voiceCapture.preview = null;
        setVoiceStatus("BUFFERING", "LISTENING / BUFFERING");
        setListeningGuide();
        renderVoiceTranscript();
      }
    });

    ws.addEventListener("error", () => {
      setVoiceStatus("ERROR", "VOICE CONNECTION ERROR");
      renderVoiceGuide({
        tone: "blocked",
        headline: "The voice connection dropped",
        message: "I cannot safely interpret new speech while the AssemblyAI stream is unavailable.",
        next_action: "Stop voice, reconnect the microphone, and retry the turn. Canonical state is unchanged.",
      }, { speak: true });
      toast("AssemblyAI streaming connection error.");
    });

    ws.addEventListener("close", () => {
      voiceCapture.connected = false;
      if (!voiceCapture.applying) setVoiceStatus("EMPTY", "DISCONNECTED");
      syncVoiceControls(current);
    });
  } catch (error) {
    setVoiceStatus("ERROR", "VOICE UNAVAILABLE");
    const name = String(error?.name || "");
    const message =
      name === "NotAllowedError"
        ? "Microphone permission was denied. Allow microphone access for this site, then retry."
        : name === "NotFoundError"
          ? "No microphone was found. Connect or enable an input device, then retry."
          : name === "NotReadableError"
            ? "The microphone is busy or unavailable to the browser. Close other capture apps and retry."
            : String(error?.message || error || "Voice capture failed.");
    renderVoiceGuide({
      tone: "blocked",
      headline: "Microphone / voice setup needs attention",
      message,
      next_action: "Canonical state is unchanged. Fix the audio issue and reconnect.",
    }, { speak: false });
    recordVoiceEvidence("VOICE_START_FAILED", {
      error_name: name || null,
      message,
      canonical_revision: current?.state?.revision ?? null,
      canonical_hash: current?.state?.state_hash ?? null,
      canonical_unchanged: true,
    });
    toast(message);
    await stopVoiceCapture({ preserveStatus: true });
  }
}

async function applyVoiceBoundary() {
  if (!voiceCapture.connected || voiceCapture.applying) return;

  voiceCapture.awaitingBoundaryFinal = true;
  setVoiceStatus("APPLYING", "FORCE ENDPOINT");
  syncVoiceControls(current);

  try {
    voiceCapture.ws.send(JSON.stringify({ type: "ForceEndpoint" }));
  } catch (error) {
    voiceCapture.awaitingBoundaryFinal = false;
    setVoiceStatus("ERROR", "VOICE BOUNDARY ERROR");
    toast(error.message);
    return;
  }

  if (voiceCapture.boundaryTimer) window.clearTimeout(voiceCapture.boundaryTimer);
  voiceCapture.boundaryTimer = window.setTimeout(async () => {
    voiceCapture.boundaryTimer = null;
    if (!voiceCapture.awaitingBoundaryFinal) return;
    if (voiceCapture.finals.length) {
      await submitBufferedVoiceTurn();
    } else {
      voiceCapture.awaitingBoundaryFinal = false;
      setVoiceStatus("BUFFERING", "WAITING FOR SPEECH");
      syncVoiceControls(current);
    }
  }, 1200);
}

async function stopVoiceCapture({ preserveStatus = false } = {}) {
  voiceCapture.guidanceRequestToken += 1;
  if (voiceCapture.speechStatusTimer) {
    window.clearTimeout(voiceCapture.speechStatusTimer);
    voiceCapture.speechStatusTimer = null;
  }
  if (voiceCapture.boundaryTimer) {
    window.clearTimeout(voiceCapture.boundaryTimer);
    voiceCapture.boundaryTimer = null;
  }
  if (voiceCapture.previewTimer) {
    window.clearTimeout(voiceCapture.previewTimer);
    voiceCapture.previewTimer = null;
  }
  voiceCapture.previewRequest += 1;

  const ws = voiceCapture.ws;
  if (ws?.readyState === WebSocket.OPEN) {
    try {
      ws.send(JSON.stringify({ type: "Terminate" }));
    } catch {
      // Connection shutdown is best-effort.
    }
  }

  voiceCapture.workletNode?.disconnect();
  voiceCapture.sourceNode?.disconnect();
  voiceCapture.silentGain?.disconnect();
  voiceCapture.mediaStream?.getTracks().forEach((track) => track.stop());
  if (voiceCapture.audioContext && voiceCapture.audioContext.state !== "closed") {
    await voiceCapture.audioContext.close();
  }
  if (ws && ws.readyState < WebSocket.CLOSING) ws.close();

  voiceCapture.ws = null;
  voiceCapture.mediaStream = null;
  voiceCapture.audioContext = null;
  voiceCapture.sourceNode = null;
  voiceCapture.workletNode = null;
  voiceCapture.silentGain = null;
  voiceCapture.connected = false;
  voiceCapture.applying = false;
  voiceCapture.awaitingBoundaryFinal = false;
  voiceCapture.sessionId = null;
  clearVoiceBuffer();
  stopCurrentGuidanceAudio();
  voiceCapture.echoCooldownUntil = 0;
  voiceCapture.speaking = false;
  if (!preserveStatus) {
    setVoiceStatus("EMPTY", "DISCONNECTED");
    renderVoiceGuide({
      tone: "neutral",
      headline: "Voice session stopped",
      message: "The microphone is disconnected. Canonical state remains exactly as shown.",
      next_action: "Start the microphone when you want another guided voice turn.",
    });
  }
  syncVoiceControls(current);
}

async function exportVoiceReceipt() {
  try {
    const receipt = await api("/api/session-receipt");
    receipt.client_voice_evidence = {
      provider: voiceCapture.ttsProvider,
      ai33_voice: voiceCapture.neuralVoiceLabel,
      assemblyai_session_id: voiceCapture.sessionId,
      connect_ms: voiceCapture.lastConnectMs,
      preview_ms: voiceCapture.lastPreviewMs,
      tts_generation_ms: voiceCapture.lastTtsLatencyMs,
      tts_credit_cost: voiceCapture.lastTtsCreditCost,
      tts_cache_hit: voiceCapture.lastTtsCacheHit,
      echo_cooldown_ms: voiceCapture.echoCooldownMs,
      exported_at: new Date().toISOString(),
    };
    receipt.client_voice_events = [...voiceCapture.evidenceEvents];
    const blob = new Blob(
      [JSON.stringify(receipt, null, 2)],
      { type: "application/json" },
    );
    const url = URL.createObjectURL(blob);
    const stamp = new Date().toISOString().replaceAll(":", "-");
    const link = document.createElement("a");
    link.href = url;
    link.download = `ERRATA-browser-voice-receipt-${stamp}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    toast("Browser voice proof receipt exported.");
  } catch (error) {
    toast(error.message);
  }
}

$("#startVoice")?.addEventListener("click", startVoiceCapture);
$("#applyVoice")?.addEventListener("click", applyVoiceBoundary);
$("#stopVoice")?.addEventListener("click", () => stopVoiceCapture());
$("#exportVoiceReceipt")?.addEventListener("click", exportVoiceReceipt);
$("#neuralVoice")?.addEventListener("change", (event) => {
  voiceCapture.neuralVoice = event.target.value || null;
  voiceCapture.neuralVoiceLabel =
    event.target.options[event.target.selectedIndex]?.textContent || "AI33 voice";
  voiceCapture.neuralPrefetches.clear();
  setVoiceEngineUI();
  toast(`AI33 voice selected: ${voiceCapture.neuralVoiceLabel}.`);
});
$("#guidanceVoice")?.addEventListener("change", (event) => {
  voiceCapture.guidanceVoiceName = event.target.value || null;
  const selected = selectGuidanceVoice();
  toast(selected ? `Voice selected: ${selected.name}` : "Browser default voice selected.");
});
$("#previewGuidanceVoice")?.addEventListener("click", () => {
  speakGuidance(
    VOICE_COPY.greeting
  );
});
if ("speechSynthesis" in window) {
  populateGuidanceVoices();
  window.speechSynthesis.addEventListener?.("voiceschanged", populateGuidanceVoices);
}
loadVoiceCapabilities();

$("#skipGuidance")?.addEventListener("click", () => {
  voiceCapture.guidanceRequestToken += 1;
  voiceCapture.guidanceGenerating = false;
  stopCurrentGuidanceAudio();
  if (voiceCapture.connected && !echoGuardActive()) {
    setVoiceStatus("CONNECTED", "VOICE CONNECTED");
  }
  recordVoiceEvidence("VOICE_REPLY_SKIPPED", {
    pending_generation: voiceCapture.guidanceGenerating,
  });
  syncGuidanceControls();
  toast("Voice reply skipped. Listening continues.");
});

$("#repeatGuidance")?.addEventListener("click", () => {
  if (voiceCapture.lastGuidance) {
    speakGuidance(guidanceSpeechText(voiceCapture.lastGuidance));
  } else {
    toast("No guidance to repeat yet.");
  }
});
$("#toggleGuidance")?.addEventListener("click", () => {
  voiceCapture.guidanceEnabled = !voiceCapture.guidanceEnabled;
  const button = $("#toggleGuidance");
  if (button) {
    button.setAttribute("aria-pressed", String(voiceCapture.guidanceEnabled));
    button.textContent = voiceCapture.guidanceEnabled
      ? "Voice guidance on"
      : "Voice guidance off";
  }
  if (!voiceCapture.guidanceEnabled) {
    voiceCapture.guidanceRequestToken += 1;
    stopCurrentGuidanceAudio();
  }
  toast(voiceCapture.guidanceEnabled ? "Voice guidance enabled." : "Voice guidance muted.");
});

$("#toggleBargeIn")?.addEventListener("click", () => {
  voiceCapture.bargeInEnabled = !voiceCapture.bargeInEnabled;
  recordVoiceEvidence("BARGE_IN_MODE_CHANGED", {
    enabled: voiceCapture.bargeInEnabled,
    echo_cancellation_requested: true,
    truth_boundary: "EXPERIMENTAL_UNTIL_HUMAN_BROWSER_PROOF",
  });
  syncGuidanceControls();
  toast(
    voiceCapture.bargeInEnabled
      ? "Barge-in enabled. User speech may interrupt ERRATA playback."
      : "Barge-in disabled. Safe half-duplex playback restored."
  );
});

window.addEventListener("beforeunload", () => {
  voiceCapture.guidanceRequestToken += 1;
  const ws = voiceCapture.ws;
  if (ws?.readyState === WebSocket.OPEN) {
    try { ws.send(JSON.stringify({ type: "Terminate" })); } catch {}
  }
  stopCurrentGuidanceAudio();
});

refresh();
