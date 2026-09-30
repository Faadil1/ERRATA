import crypto from "node:crypto";

export function safeEqualText(a, b) {
  const left = Buffer.from(String(a || ""));
  const right = Buffer.from(String(b || ""));
  if (left.length !== right.length) return false;
  return crypto.timingSafeEqual(left, right);
}

export function verifyBasicAuth(req, usernameEnv, passwordEnv) {
  const expectedUser = String(process.env[usernameEnv] || "");
  const expectedPass = String(process.env[passwordEnv] || "");
  if (!expectedUser || !expectedPass) return false;

  const header = String(req.headers.authorization || "");
  if (!header.startsWith("Basic ")) return false;

  let decoded = "";
  try {
    decoded = Buffer.from(header.slice(6), "base64").toString("utf8");
  } catch {
    return false;
  }
  const split = decoded.indexOf(":");
  if (split < 0) return false;
  const user = decoded.slice(0, split);
  const pass = decoded.slice(split + 1);
  return safeEqualText(user, expectedUser) && safeEqualText(pass, expectedPass);
}

export function challengeBasicAuth(res) {
  res.statusCode = 401;
  res.setHeader("WWW-Authenticate", 'Basic realm="ERRATA Bandwidth"');
  res.end("Authentication required");
}

export function publicOrigin(req) {
  const configured = String(process.env.ERRATA_PUBLIC_ORIGIN || "")
    .trim()
    .replace(/\/$/, "");
  if (configured) return configured;
  const forwardedHost = String(req.headers["x-forwarded-host"] || "")
    .split(",")[0]
    .trim();
  const host = forwardedHost || req.headers.host;
  const proto = String(req.headers["x-forwarded-proto"] || "https")
    .split(",")[0]
    .trim();
  return `${proto}://${host}`;
}

export function xmlEscape(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

export async function collectJson(req) {
  if (
    req.body &&
    typeof req.body === "object" &&
    !Buffer.isBuffer(req.body)
  ) {
    return req.body;
  }
  if (typeof req.body === "string") {
    return req.body ? JSON.parse(req.body) : {};
  }
  if (Buffer.isBuffer(req.body)) {
    const raw = req.body.toString("utf8");
    return raw ? JSON.parse(raw) : {};
  }
  return await new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (chunk) => chunks.push(Buffer.from(chunk)));
    req.on("end", () => {
      try {
        const raw = Buffer.concat(chunks).toString("utf8");
        resolve(raw ? JSON.parse(raw) : {});
      } catch (error) {
        reject(error);
      }
    });
    req.on("error", reject);
  });
}

export async function errataRequest(
  origin,
  path,
  { method = "GET", body = null, sessionToken = null } = {},
) {
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
    throw new Error(
      payload?.detail || payload?.error || `ERRATA HTTP ${response.status}`,
    );
  }

  const token = payload?._session_token || sessionToken;
  if (payload && Object.prototype.hasOwnProperty.call(payload, "_session_token")) {
    delete payload._session_token;
  }
  return { payload, sessionToken: token };
}

function reviewSecret() {
  return String(
    process.env.BANDWIDTH_PHONE_HMAC_KEY ||
    process.env.ERRATA_SESSION_HMAC_KEY ||
    "",
  );
}

export function signReviewToken(payload) {
  const secret = reviewSecret();
  if (!secret) throw new Error("BANDWIDTH_PHONE_HMAC_KEY is not configured");
  const encoded = Buffer.from(JSON.stringify(payload), "utf8").toString("base64url");
  const signature = crypto
    .createHmac("sha256", secret)
    .update(encoded)
    .digest("base64url");
  return `${encoded}.${signature}`;
}

export function verifyReviewToken(token) {
  const secret = reviewSecret();
  if (!secret) throw new Error("BANDWIDTH_PHONE_HMAC_KEY is not configured");
  const [encoded, signature] = String(token || "").split(".");
  if (!encoded || !signature) throw new Error("Invalid review token");
  const expected = crypto
    .createHmac("sha256", secret)
    .update(encoded)
    .digest("base64url");
  if (!safeEqualText(signature, expected)) {
    throw new Error("Invalid review token signature");
  }
  const payload = JSON.parse(Buffer.from(encoded, "base64url").toString("utf8"));
  if (!payload.exp || Number(payload.exp) < Math.floor(Date.now() / 1000)) {
    throw new Error("Expired review token");
  }
  return payload;
}

let cachedAccessToken = null;
let cachedAccessTokenExpiresAt = 0;

export async function bandwidthAccessToken() {
  if (
    cachedAccessToken &&
    cachedAccessTokenExpiresAt > Date.now() + 30_000
  ) {
    return cachedAccessToken;
  }

  const clientId = String(process.env.BANDWIDTH_CLIENT_ID || "");
  const clientSecret = String(process.env.BANDWIDTH_CLIENT_SECRET || "");
  if (!clientId || !clientSecret) {
    throw new Error("Bandwidth OAuth credentials are not configured");
  }

  const response = await fetch(
    "https://api.bandwidth.com/api/v1/oauth2/token",
    {
      method: "POST",
      headers: {
        Authorization:
          "Basic " +
          Buffer.from(`${clientId}:${clientSecret}`).toString("base64"),
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: "grant_type=client_credentials",
    },
  );
  if (!response.ok) {
    throw new Error(`Bandwidth OAuth failed: HTTP ${response.status}`);
  }
  const payload = await response.json();
  cachedAccessToken = String(payload.access_token || "");
  const expiresIn = Number(payload.expires_in || 300);
  cachedAccessTokenExpiresAt = Date.now() + expiresIn * 1000;
  if (!cachedAccessToken) throw new Error("Bandwidth OAuth returned no access token");
  return cachedAccessToken;
}

export async function replaceCallBxml({ accountId, callId, bxml }) {
  const accessToken = await bandwidthAccessToken();
  const response = await fetch(
    `https://voice.bandwidth.com/api/v2/accounts/${encodeURIComponent(accountId)}/calls/${encodeURIComponent(callId)}/bxml`,
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/xml",
      },
      body: bxml,
    },
  );
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(
      `Bandwidth Update Call BXML failed: HTTP ${response.status} ${detail.slice(0, 300)}`,
    );
  }
  return true;
}
