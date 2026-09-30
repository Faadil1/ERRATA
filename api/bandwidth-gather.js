import {
  challengeBasicAuth,
  collectJson,
  errataRequest,
  publicOrigin,
  verifyBasicAuth,
  verifyReviewToken,
  xmlEscape,
} from "./bandwidth-common.js";

function successBxml(payload) {
  const state = payload?.state || {};
  const route = String(state.route || "—").replace(/^R(?=\d+$)/, "");
  const end = state.end_time ? String(state.end_time).slice(0, 5) : "—";
  return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <SpeakSentence>Applied. Same change identity, revision ${xmlEscape(state.revision ?? "—")}. Route ${xmlEscape(route)} ends at ${xmlEscape(end)}. Commit remains a separate protected action.</SpeakSentence>
  <Hangup/>
</Response>`;
}

function safeMessage(text) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <SpeakSentence>${xmlEscape(text)}</SpeakSentence>
  <Hangup/>
</Response>`;
}

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

  const url = new URL(req.url, publicOrigin(req));
  const token = url.searchParams.get("token") || "";
  let review;
  try {
    review = verifyReviewToken(token);
  } catch (error) {
    res.statusCode = 403;
    res.end("Invalid review token");
    return;
  }

  const callId = String(event.callId || "");
  if (!callId || callId !== String(review.callId || "")) {
    res.statusCode = 403;
    res.end("Call identity mismatch");
    return;
  }

  const digit = String(event.digits || event.digit || "");
  if (digit === "2") {
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/xml; charset=utf-8");
    res.end(safeMessage("Discarded. Nothing was applied."));
    return;
  }

  if (digit !== "1") {
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/xml; charset=utf-8");
    res.end(safeMessage("No valid confirmation was received. Nothing was applied."));
    return;
  }

  try {
    const origin = publicOrigin(req);
    const initial = await errataRequest(origin, "/api/change");
    const preview = await errataRequest(origin, "/api/preview/voice", {
      method: "POST",
      body: { text: String(review.transcript || "") },
      sessionToken: initial.sessionToken,
    });

    if (
      preview.payload?.status !== "READY_TO_APPLY" ||
      Number(preview.payload?.canonical_revision) !== Number(review.canonicalRevision) ||
      String(preview.payload?.canonical_hash || "") !== String(review.canonicalHash || "")
    ) {
      res.statusCode = 200;
      res.setHeader("Content-Type", "application/xml; charset=utf-8");
      res.end(
        safeMessage(
          "ERRATA refused the phone apply because the reviewed canonical state no longer matches. Nothing was applied.",
        ),
      );
      return;
    }

    const applied = await errataRequest(origin, "/api/amend/voice", {
      method: "POST",
      body: {
        text: String(review.transcript || ""),
        assemblyai_session_id: `bandwidth:${callId}`,
        boundary: "BandwidthDTMF1",
        client_captured_at: new Date().toISOString(),
      },
      sessionToken: preview.sessionToken,
    });

    const ok = applied.payload?.latest_transaction?.status === "APPLIED";
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/xml; charset=utf-8");
    res.end(
      ok
        ? successBxml(applied.payload)
        : safeMessage("ERRATA did not apply the phone preview. Nothing should be assumed changed."),
    );
  } catch (error) {
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/xml; charset=utf-8");
    res.end(
      safeMessage(
        "ERRATA phone apply failed safely. Nothing should be assumed applied.",
      ),
    );
  }
}
