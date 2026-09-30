import { createServer } from "node:http";
import { WebSocket, WebSocketServer } from "ws";
import {
  errataRequest,
  publicOrigin,
  replaceCallBxml,
  signReviewToken,
  verifyBasicAuth,
  xmlEscape,
} from "./bandwidth-common.js";

const MAX_PENDING_AUDIO_CHUNKS = 400;

function assemblyUrl() {
  const url = new URL("wss://streaming.assemblyai.com/v3/ws");
  url.searchParams.set("sample_rate", "8000");
  url.searchParams.set("encoding", "pcm_mulaw");
  url.searchParams.set("speech_model", "universal-3-5-pro");
  url.searchParams.set("mode", "balanced");
  url.searchParams.set("format_turns", "true");
  url.searchParams.set("language_codes", JSON.stringify(["en", "fr"]));
  url.searchParams.set(
    "agent_context",
    "You reached ERRATA phone capture. Speak one transit service change.",
  );
  url.searchParams.set(
    "keyterms_prompt",
    JSON.stringify(["Route 55", "King Edward", "Cumberland"]),
  );
  return url.toString();
}

function safeClose(socket) {
  try {
    if (socket && socket.readyState === WebSocket.OPEN) socket.close();
  } catch {}
}

function directionLabel(direction) {
  if (direction === 1 || direction === "1") return "west";
  if (direction === 0 || direction === "0") return "east";
  return "direction pending";
}

function reviewSpeech(preview) {
  const candidate = preview?.candidate || {};
  const route = String(candidate.route || "—").replace(/^R(?=\d+$)/, "");
  const direction = directionLabel(candidate.direction);
  const end = candidate.end_time ? String(candidate.end_time).slice(0, 5) : "—";
  const stops = Array.isArray(candidate.skip_stops)
    ? candidate.skip_stops.join(", ")
    : "";
  return (
    `ERRATA preview. Route ${route} ${direction}. ` +
    `Stops skipped: ${stops || "none"}. End time ${end}. ` +
    "Nothing has been applied. Press 1 to apply this reviewed change, or 2 to discard it."
  );
}

function clarificationSpeech(preview) {
  const guidance = preview?.guidance || {};
  return (
    "ERRATA needs clarification. " +
    String(
      guidance.message ||
        preview?.reason ||
        "The spoken instruction could not be safely interpreted.",
    ) +
    " Nothing was applied."
  );
}

function reviewBxml({ origin, preview, transcript, callId }) {
  const token = signReviewToken({
    callId,
    transcript,
    canonicalRevision: preview.canonical_revision,
    canonicalHash: preview.canonical_hash,
    exp: Math.floor(Date.now() / 1000) + 120,
  });
  const gatherUrl = `${origin}/bandwidth/gather?token=${encodeURIComponent(token)}`;
  const user = String(process.env.BANDWIDTH_WEBHOOK_USERNAME || "");
  const pass = String(process.env.BANDWIDTH_WEBHOOK_PASSWORD || "");

  return `<?xml version="1.0" encoding="UTF-8"?>
<Bxml>
  <Gather gatherUrl="${xmlEscape(gatherUrl)}" gatherMethod="POST" maxDigits="1" firstDigitTimeout="12"
    username="${xmlEscape(user)}" password="${xmlEscape(pass)}">
    <SpeakSentence>${xmlEscape(reviewSpeech(preview))}</SpeakSentence>
  </Gather>
  <SpeakSentence>No selection received. Nothing was applied.</SpeakSentence>
  <Hangup/>
</Bxml>`;
}

function clarificationBxml(preview) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<Bxml>
  <SpeakSentence>${xmlEscape(clarificationSpeech(preview))}</SpeakSentence>
  <Hangup/>
</Bxml>`;
}

const server = createServer((req, res) => {
  res.statusCode = 426;
  res.setHeader("Content-Type", "text/plain; charset=utf-8");
  res.end("Upgrade Required");
});

const wss = new WebSocketServer({ noServer: true });

server.on("upgrade", (request, socket, head) => {
  if (
    !verifyBasicAuth(
      request,
      "BANDWIDTH_STREAM_USERNAME",
      "BANDWIDTH_STREAM_PASSWORD",
    )
  ) {
    socket.write(
      'HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm="ERRATA Bandwidth Stream"\r\nConnection: close\r\n\r\n',
    );
    socket.destroy();
    return;
  }

  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit("connection", ws, request);
  });
});

wss.on("connection", (bandwidthWs, request) => {
  const origin = publicOrigin(request);
  const assemblyKey = String(process.env.ASSEMBLYAI_API_KEY || "");
  const configuredAccountId = String(process.env.BANDWIDTH_ACCOUNT_ID || "");

  let aaiWs = null;
  let pendingAudio = [];
  let accountId = "";
  let callId = "";
  let latestTranscript = "";
  let finalized = false;
  let initialized = false;
  let sessionToken = null;

  async function initializeErrata() {
    if (initialized) return;
    const result = await errataRequest(origin, "/api/change");
    sessionToken = result.sessionToken;
    initialized = true;
  }

  async function moveCallToReview(preview, transcript) {
    const bxml =
      preview?.status === "READY_TO_APPLY"
        ? reviewBxml({ origin, preview, transcript, callId })
        : clarificationBxml(preview);

    await replaceCallBxml({
      accountId,
      callId,
      bxml,
    });
  }

  function openAssemblyStream() {
    if (aaiWs || !assemblyKey) return;
    aaiWs = new WebSocket(assemblyUrl(), {
      headers: { Authorization: assemblyKey },
    });

    aaiWs.on("open", () => {
      for (const chunk of pendingAudio) aaiWs.send(chunk);
      pendingAudio = [];
    });

    aaiWs.on("message", async (data) => {
      let event;
      try {
        event = JSON.parse(data.toString());
      } catch {
        return;
      }

      if (event.type !== "Turn" || !event.end_of_turn || finalized) return;
      const transcript = String(event.transcript || "").trim();
      if (!transcript) return;

      finalized = true;
      latestTranscript = transcript;

      try {
        await initializeErrata();
        const result = await errataRequest(origin, "/api/preview/voice", {
          method: "POST",
          body: { text: transcript },
          sessionToken,
        });
        sessionToken = result.sessionToken;
        await moveCallToReview(result.payload, transcript);
      } catch {
        try {
          await replaceCallBxml({
            accountId,
            callId,
            bxml: `<?xml version="1.0" encoding="UTF-8"?><Bxml><SpeakSentence>ERRATA phone preview failed safely. Nothing was applied.</SpeakSentence><Hangup/></Bxml>`,
          });
        } catch {}
      } finally {
        safeClose(aaiWs);
      }
    });

    aaiWs.on("close", () => {
      aaiWs = null;
    });
  }

  bandwidthWs.on("message", async (raw) => {
    let message;
    try {
      message = JSON.parse(raw.toString());
    } catch {
      return;
    }

    if (message.eventType === "start") {
      accountId = String(message.metadata?.accountId || "");
      callId = String(message.metadata?.callId || "");
      if (
        !accountId ||
        !callId ||
        (configuredAccountId && accountId !== configuredAccountId)
      ) {
        safeClose(bandwidthWs);
        return;
      }

      try {
        await initializeErrata();
      } catch {
        safeClose(bandwidthWs);
        return;
      }
      openAssemblyStream();
      return;
    }

    if (message.eventType === "media") {
      if (message.track && message.track !== "inbound") return;
      const payload = message.payload;
      if (!payload || finalized) return;
      const audio = Buffer.from(payload, "base64");
      if (aaiWs?.readyState === WebSocket.OPEN) {
        aaiWs.send(audio);
      } else if (pendingAudio.length < MAX_PENDING_AUDIO_CHUNKS) {
        pendingAudio.push(audio);
      }
      return;
    }

    if (message.eventType === "stop") {
      safeClose(aaiWs);
    }
  });

  bandwidthWs.on("close", () => safeClose(aaiWs));
  bandwidthWs.on("error", () => safeClose(aaiWs));
});

export default server;
