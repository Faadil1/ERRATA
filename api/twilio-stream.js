import { createServer } from "node:http";
import twilio from "twilio";
import { WebSocket, WebSocketServer } from "ws";

const MAX_PENDING_AUDIO_CHUNKS = 400;
const PREVIEW_SMS_PREFIX = "ERRATA preview — NOT APPLIED";
const APPLIED_SMS_PREFIX = "ERRATA applied";

function requestOrigin(request) {
  const configured = String(process.env.ERRATA_PUBLIC_ORIGIN || "").trim().replace(/\/$/, "");
  if (configured) return configured;

  const forwardedHost = String(request.headers["x-forwarded-host"] || "").split(",")[0].trim();
  const host = forwardedHost || request.headers.host;
  const proto = String(request.headers["x-forwarded-proto"] || "https").split(",")[0].trim();
  return `${proto}://${host}`;
}

function websocketValidationUrl(request) {
  const origin = requestOrigin(request);
  return origin + request.url;
}

function validateTwilioUpgrade(request) {
  const authToken = process.env.TWILIO_AUTH_TOKEN;
  if (!authToken) return false;
  const signature = String(request.headers["x-twilio-signature"] || "");
  if (!signature) return false;

  return twilio.validateRequest(
    authToken,
    signature,
    websocketValidationUrl(request),
    {},
  );
}

async function sendSms({ to, body }) {
  const accountSid = process.env.TWILIO_ACCOUNT_SID;
  const authToken = process.env.TWILIO_AUTH_TOKEN;
  const from = process.env.TWILIO_SMS_FROM || process.env.TWILIO_PHONE_NUMBER;

  if (!accountSid || !authToken || !from || !to) {
    return {
      ok: false,
      status: 0,
      detail: "SMS_REVIEW_CHANNEL_NOT_CONFIGURED",
    };
  }

  const params = new URLSearchParams({
    To: to,
    From: from,
    Body: body.slice(0, 1500),
  });

  const response = await fetch(
    `https://api.twilio.com/2010-04-01/Accounts/${encodeURIComponent(accountSid)}/Messages.json`,
    {
      method: "POST",
      headers: {
        Authorization:
          "Basic " +
          Buffer.from(`${accountSid}:${authToken}`).toString("base64"),
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: params.toString(),
    },
  );

  let detail = "";
  try {
    const payload = await response.json();
    detail = payload.sid || payload.message || payload.code || "";
  } catch {
    detail = await response.text();
  }

  return {
    ok: response.ok,
    status: response.status,
    detail: String(detail || "").slice(0, 220),
  };
}

function normalizeRoute(route) {
  return String(route || "—").replace(/^R(?=\d+$)/, "");
}

function directionLabel(direction) {
  if (direction === 1 || direction === "1") return "west";
  if (direction === 0 || direction === "0") return "east";
  return "direction pending";
}

function previewSmsBody(preview) {
  const candidate = preview?.candidate || {};
  const stops = Array.isArray(candidate.skip_stops)
    ? candidate.skip_stops.join(", ")
    : "";
  const route = normalizeRoute(candidate.route);
  const direction = directionLabel(candidate.direction);
  const end = candidate.end_time ? String(candidate.end_time).slice(0, 5) : "—";

  if (preview?.status === "READY_TO_APPLY") {
    return (
      `${PREVIEW_SMS_PREFIX}. Route ${route} ${direction}; ` +
      `skip: ${stops || "none"}; end: ${end}. ` +
      `Canonical rev ${preview.canonical_revision} is unchanged. ` +
      "Press 1 on the active call to apply this captured turn, or 2 to discard it."
    );
  }

  const guidance = preview?.guidance || {};
  return (
    `${PREVIEW_SMS_PREFIX}. Needs clarification. ` +
    `${guidance.message || preview?.reason || "ERRATA could not prepare a safe amendment."} ` +
    `${guidance.next_action || "Restate the service change."} ` +
    `Canonical rev ${preview?.canonical_revision ?? "—"} remains unchanged.`
  );
}

function appliedSmsBody(payload) {
  const state = payload?.state || {};
  const stops = Array.isArray(state.skip_stops)
    ? state.skip_stops.map((stop) => stop.stop_name || stop.stop_id).join(", ")
    : "";
  return (
    `${APPLIED_SMS_PREFIX}. Same change_id ${state.change_id || "—"}, rev ${state.revision ?? "—"}. ` +
    `Route ${normalizeRoute(state.route)} ${directionLabel(state.direction)}; ` +
    `skip: ${stops || "none"}; end: ${state.end_time ? String(state.end_time).slice(0, 5) : "—"}. ` +
    `Hash ${String(state.state_hash || "").slice(0, 12)}. Commit remains a separate protected action.`
  );
}

async function errataRequest(origin, path, { method = "GET", body = null, sessionToken = null } = {}) {
  const headers = {};
  if (body !== null) headers["Content-Type"] = "application/json";
  if (sessionToken) headers["X-ERRATA-Session"] = sessionToken;

  const response = await fetch(origin + path, {
    method,
    headers,
    body: body === null ? undefined : JSON.stringify(body),
  });

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = { detail: await response.text() };
  }

  if (!response.ok) {
    throw new Error(payload?.detail || payload?.error || `ERRATA HTTP ${response.status}`);
  }

  const token = payload?._session_token || sessionToken;
  if (payload && Object.prototype.hasOwnProperty.call(payload, "_session_token")) {
    delete payload._session_token;
  }

  return { payload, sessionToken: token };
}

function assemblyUrl() {
  const url = new URL("wss://streaming.assemblyai.com/v3/ws");
  url.searchParams.set("sample_rate", "8000");
  url.searchParams.set("encoding", "pcm_mulaw");
  url.searchParams.set("speech_model", "universal-3-5-pro");
  url.searchParams.set("mode", "balanced");
  url.searchParams.set("format_turns", "true");
  url.searchParams.set("voice_focus", "near-field");
  url.searchParams.set("language_codes", JSON.stringify(["en", "fr"]));
  url.searchParams.set(
    "agent_context",
    "You reached ERRATA phone capture. Speak one transit service change."
  );
  url.searchParams.set(
    "keyterms_prompt",
    JSON.stringify(["Route 55", "King Edward", "Cumberland"])
  );
  return url.toString();
}

function safeClose(socket) {
  try {
    if (socket && socket.readyState === WebSocket.OPEN) socket.close();
  } catch {}
}

const server = createServer((req, res) => {
  res.statusCode = 426;
  res.setHeader("Content-Type", "text/plain; charset=utf-8");
  res.end("Upgrade Required");
});

const wss = new WebSocketServer({ noServer: true });

server.on("upgrade", (request, socket, head) => {
  if (!validateTwilioUpgrade(request)) {
    socket.write("HTTP/1.1 401 Unauthorized\r\nConnection: close\r\n\r\n");
    socket.destroy();
    return;
  }

  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit("connection", ws, request);
  });
});

wss.on("connection", (twilioWs, request) => {
  const origin = requestOrigin(request);
  const assemblyKey = process.env.ASSEMBLYAI_API_KEY;

  let aaiWs = null;
  let pendingAudio = [];
  let sessionToken = null;
  let caller = "";
  let callSid = "";
  let streamSid = "";
  let latestTranscript = "";
  let latestPreview = null;
  let previewSmsDelivered = false;
  let applying = false;
  let initialized = false;
  let closed = false;

  async function initializeErrata() {
    if (initialized) return;
    const result = await errataRequest(origin, "/api/change");
    sessionToken = result.sessionToken;
    initialized = true;
  }

  function openAssemblyStream() {
    if (aaiWs || !assemblyKey) return;

    aaiWs = new WebSocket(assemblyUrl(), {
      headers: {
        Authorization: assemblyKey,
      },
    });

    aaiWs.on("open", () => {
      for (const chunk of pendingAudio) {
        aaiWs.send(chunk);
      }
      pendingAudio = [];
    });

    aaiWs.on("message", async (data) => {
      let event;
      try {
        event = JSON.parse(data.toString());
      } catch {
        return;
      }

      if (event.type !== "Turn" || !event.end_of_turn) return;
      const transcript = String(event.transcript || "").trim();
      if (!transcript || applying) return;

      latestTranscript = transcript;
      previewSmsDelivered = false;

      try {
        await initializeErrata();
        const result = await errataRequest(origin, "/api/preview/voice", {
          method: "POST",
          body: { text: transcript },
          sessionToken,
        });
        sessionToken = result.sessionToken;
        latestPreview = result.payload;

        const sms = await sendSms({
          to: caller,
          body: previewSmsBody(latestPreview),
        });
        previewSmsDelivered = sms.ok;
      } catch (error) {
        latestPreview = null;
        previewSmsDelivered = false;
        await sendSms({
          to: caller,
          body:
            "ERRATA phone preview failed safely. Nothing was applied. " +
            String(error.message || error).slice(0, 500),
        }).catch(() => {});
      }
    });

    aaiWs.on("error", () => {
      previewSmsDelivered = false;
    });

    aaiWs.on("close", () => {
      aaiWs = null;
    });
  }

  async function applyCurrentPreview() {
    if (applying) return;
    if (!latestTranscript || latestPreview?.status !== "READY_TO_APPLY") {
      await sendSms({
        to: caller,
        body:
          "ERRATA did not apply anything. There is no safe READY_TO_APPLY phone preview. " +
          "Speak or restate the service change first.",
      }).catch(() => {});
      return;
    }
    if (!previewSmsDelivered) {
      await sendSms({
        to: caller,
        body:
          "ERRATA refused phone Apply because the review message was not delivered. " +
          "Nothing changed.",
      }).catch(() => {});
      return;
    }

    applying = true;
    try {
      const result = await errataRequest(origin, "/api/amend/voice", {
        method: "POST",
        body: {
          text: latestTranscript,
          assemblyai_session_id: callSid ? `twilio:${callSid}` : null,
          boundary: "TwilioDTMF1",
          client_captured_at: new Date().toISOString(),
        },
        sessionToken,
      });
      sessionToken = result.sessionToken;
      const payload = result.payload;
      const applied = payload?.latest_transaction?.status === "APPLIED";

      await sendSms({
        to: caller,
        body: applied
          ? appliedSmsBody(payload)
          : "ERRATA phone Apply did not mutate canonical state. Review the latest transaction before retrying.",
      });

      latestTranscript = "";
      latestPreview = null;
      previewSmsDelivered = false;
    } catch (error) {
      await sendSms({
        to: caller,
        body:
          "ERRATA phone Apply failed safely. Nothing should be assumed applied. " +
          String(error.message || error).slice(0, 500),
      }).catch(() => {});
    } finally {
      applying = false;
    }
  }

  async function discardCurrentPreview() {
    latestTranscript = "";
    latestPreview = null;
    previewSmsDelivered = false;
    await sendSms({
      to: caller,
      body: "ERRATA discarded the captured phone preview. Canonical state is unchanged.",
    }).catch(() => {});
  }

  twilioWs.on("message", async (raw) => {
    let message;
    try {
      message = JSON.parse(raw.toString());
    } catch {
      return;
    }

    if (message.event === "start") {
      streamSid = String(message.start?.streamSid || message.streamSid || "");
      callSid = String(
        message.start?.callSid ||
          message.start?.customParameters?.call_sid ||
          ""
      );
      caller = String(message.start?.customParameters?.caller || "");
      try {
        await initializeErrata();
      } catch {
        safeClose(twilioWs);
        return;
      }
      openAssemblyStream();
      return;
    }

    if (message.event === "media") {
      const payload = message.media?.payload;
      if (!payload) return;
      const audio = Buffer.from(payload, "base64");
      if (aaiWs?.readyState === WebSocket.OPEN) {
        aaiWs.send(audio);
      } else if (pendingAudio.length < MAX_PENDING_AUDIO_CHUNKS) {
        pendingAudio.push(audio);
      }
      return;
    }

    if (message.event === "dtmf") {
      const digit = String(message.dtmf?.digit || "");
      if (digit === "1") {
        await applyCurrentPreview();
      } else if (digit === "2") {
        await discardCurrentPreview();
      } else if (digit === "9") {
        safeClose(twilioWs);
      }
      return;
    }

    if (message.event === "stop") {
      closed = true;
      safeClose(aaiWs);
    }
  });

  twilioWs.on("close", () => {
    if (closed) return;
    closed = true;
    safeClose(aaiWs);
  });

  twilioWs.on("error", () => {
    closed = true;
    safeClose(aaiWs);
  });
});

export default server;
