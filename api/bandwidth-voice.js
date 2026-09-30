import {
  challengeBasicAuth,
  collectJson,
  publicOrigin,
  verifyBasicAuth,
  xmlEscape,
} from "./bandwidth-common.js";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.setHeader("Allow", "POST");
    res.end("Method Not Allowed");
    return;
  }

  if (
    !verifyBasicAuth(
      req,
      "BANDWIDTH_WEBHOOK_USERNAME",
      "BANDWIDTH_WEBHOOK_PASSWORD",
    )
  ) {
    challengeBasicAuth(res);
    return;
  }

  let event;
  try {
    event = await collectJson(req);
  } catch {
    res.statusCode = 400;
    res.end("Invalid JSON");
    return;
  }

  const accountId = String(event.accountId || "");
  const callId = String(event.callId || "");
  const caller = String(event.from || "");
  const called = String(event.to || "");
  const configuredAccountId = String(process.env.BANDWIDTH_ACCOUNT_ID || "");

  if (!accountId || !callId) {
    res.statusCode = 400;
    res.end("Missing Bandwidth call identity");
    return;
  }
  if (configuredAccountId && accountId !== configuredAccountId) {
    res.statusCode = 403;
    res.end("Unexpected Bandwidth account");
    return;
  }

  const streamUser = String(process.env.BANDWIDTH_STREAM_USERNAME || "");
  const streamPass = String(process.env.BANDWIDTH_STREAM_PASSWORD || "");
  if (!streamUser || !streamPass) {
    res.statusCode = 503;
    res.end("Bandwidth stream credentials are not configured");
    return;
  }

  const origin = publicOrigin(req);
  const wsOrigin = origin.replace(/^http/i, "ws");
  const streamUrl = `${wsOrigin}/api/bandwidth-stream`;

  const bxml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <SpeakSentence>You reached ERRATA phone capture. Speak one transit service change after the tone. Your words will be reviewed before anything is applied.</SpeakSentence>
  <StartStream name="errata_phone" mode="bidirectional" tracks="inbound"
    destination="${xmlEscape(streamUrl)}"
    destinationUsername="${xmlEscape(streamUser)}"
    destinationPassword="${xmlEscape(streamPass)}">
    <StreamParam name="caller" value="${xmlEscape(caller)}" />
    <StreamParam name="called" value="${xmlEscape(called)}" />
    <StreamParam name="call_id" value="${xmlEscape(callId)}" />
  </StartStream>
  <StopStream name="errata_phone" wait="true"/>
</Response>`;

  res.statusCode = 200;
  res.setHeader("Content-Type", "application/xml; charset=utf-8");
  res.end(bxml);
}
