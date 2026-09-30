import twilio from "twilio";

function collectBody(req) {
  if (req.body && typeof req.body === "object" && !Buffer.isBuffer(req.body)) {
    return Promise.resolve(req.body);
  }
  if (typeof req.body === "string") {
    return Promise.resolve(Object.fromEntries(new URLSearchParams(req.body)));
  }
  if (Buffer.isBuffer(req.body)) {
    return Promise.resolve(Object.fromEntries(new URLSearchParams(req.body.toString("utf8"))));
  }

  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (chunk) => chunks.push(Buffer.from(chunk)));
    req.on("end", () => {
      try {
        const raw = Buffer.concat(chunks).toString("utf8");
        resolve(Object.fromEntries(new URLSearchParams(raw)));
      } catch (error) {
        reject(error);
      }
    });
    req.on("error", reject);
  });
}

function publicOrigin(req) {
  const configured = String(process.env.ERRATA_PUBLIC_ORIGIN || "").trim().replace(/\/$/, "");
  if (configured) return configured;

  const forwardedHost = String(req.headers["x-forwarded-host"] || "").split(",")[0].trim();
  const host = forwardedHost || req.headers.host;
  const proto = String(req.headers["x-forwarded-proto"] || "https").split(",")[0].trim();
  return `${proto}://${host}`;
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.setHeader("Allow", "POST");
    res.end("Method Not Allowed");
    return;
  }

  const authToken = process.env.TWILIO_AUTH_TOKEN;
  if (!authToken) {
    res.statusCode = 503;
    res.end("TWILIO_AUTH_TOKEN is not configured");
    return;
  }

  const params = await collectBody(req);
  const signature = String(req.headers["x-twilio-signature"] || "");
  const origin = publicOrigin(req);
  const requestUrl = origin + req.url;

  const valid = twilio.validateRequest(
    authToken,
    signature,
    requestUrl,
    params,
  );

  if (!valid) {
    res.statusCode = 403;
    res.end("Invalid Twilio signature");
    return;
  }

  const caller = String(params.From || "");
  const called = String(params.To || "");
  const callSid = String(params.CallSid || "");

  const wsOrigin = origin.replace(/^http/i, "ws");
  const streamUrl = `${wsOrigin}/api/twilio-stream`;

  const response = new twilio.twiml.VoiceResponse();
  response.say(
    {
      voice: "Polly.Joanna",
    },
    "You reached ERRATA phone capture. Speak one transit service change. " +
      "ERRATA will text the interpreted preview to this phone. " +
      "After the message arrives, press 1 to apply or 2 to discard. " +
      "You can then speak another correction, or hang up."
  );

  const connect = response.connect();
  const stream = connect.stream({ url: streamUrl });
  stream.parameter({ name: "caller", value: caller });
  stream.parameter({ name: "called", value: called });
  stream.parameter({ name: "call_sid", value: callSid });

  response.say(
    {
      voice: "Polly.Joanna",
    },
    "Your ERRATA phone session has ended."
  );

  res.statusCode = 200;
  res.setHeader("Content-Type", "application/xml; charset=utf-8");
  res.end(response.toString());
}
