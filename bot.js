require("dotenv").config();

process.on("unhandledRejection", (err) => {
  console.error("Unhandled Rejection:", err);
});

process.on("uncaughtException", (err) => {
  console.error("Uncaught Exception:", err);
});

const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
} = require("@whiskeysockets/baileys");

const Pino = require("pino");
const qrcode = require("qrcode-terminal");
const axios = require("axios");

const TARGET_GROUP_ID = process.env.TARGET_GROUP_ID;
const RECEIVER_URL = `http://127.0.0.1:${process.env.RECEIVER_PORT}`;

if (!TARGET_GROUP_ID || !process.env.RECEIVER_PORT) {
  console.error("❌ ENV belum lengkap.");
  process.exit(1);
}

if (!TARGET_GROUP_ID.endsWith("@g.us")) {
  console.warn("⚠ TARGET_GROUP_ID bukan format group.");
}

let isConnecting = false;
let sock;
let reconnectAttempts = 0;
const MAX_RECONNECT_DELAY = 60000;

const processedMessages = new Map();
const MESSAGE_TTL = 60 * 1000;

// ================= CLEAN OLD MESSAGE CACHE =================
setInterval(() => {
  const now = Date.now();
  for (const [id, timestamp] of processedMessages.entries()) {
    if (now - timestamp > MESSAGE_TTL) {
      processedMessages.delete(id);
    }
  }
}, 30000);

// ================= SAFE AXIOS POST =================
async function postWithRetry(url, payload, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await axios.post(url, payload, { timeout: 5000 });
    } catch (err) {
      if (i === retries - 1) throw err;
      await new Promise((res) => setTimeout(res, 1000));
    }
  }
}

// ================= START BOT =================
async function startBot() {
  if (isConnecting) return;
  isConnecting = true;

  console.log("🚀 Starting WhatsApp bot...");

  const { state, saveCreds } = await useMultiFileAuthState("auth_info");

  sock = makeWASocket({
    auth: state,
    logger: Pino({ level: "silent" }),
    browser: ["Ubuntu", "Chrome", "20.0"],
  });

  sock.ev.on("creds.update", saveCreds);

  // ================= CONNECTION =================
  sock.ev.on("connection.update", (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      console.log("\n📱 Scan QR Code:");
      qrcode.generate(qr, { small: true });
    }

    if (connection === "open") {
      console.log("✅ WhatsApp connected");
      isConnecting = false;
      reconnectAttempts = 0;
    }

    if (connection === "close") {
      const statusCode = lastDisconnect?.error?.output?.statusCode;

      console.log("❌ Connection closed:", statusCode ?? "unknown");

      isConnecting = false;

      if (statusCode !== DisconnectReason.loggedOut) {
        reconnectAttempts++;
        const delay = Math.min(
          10000 * reconnectAttempts,
          MAX_RECONNECT_DELAY
        );
        console.log(`⏳ Reconnecting in ${delay / 1000}s...`);
        setTimeout(startBot, delay);
      } else {
        console.log("❌ Logged out. Delete 'auth_info' and scan QR again.");
      }
    }
  });

  // ================= MESSAGE HANDLER =================
  sock.ev.on("messages.upsert", async ({ messages }) => {
    try {
      const msg = messages?.[0];
      if (!msg || !msg.message) return;
      if (msg.key.fromMe) return;

      const from = msg.key.remoteJid;

      // ignore broadcast & status
      if (from === "status@broadcast") return;
      if (!from.endsWith("@g.us")) return;

      if (from !== TARGET_GROUP_ID) return;

      const msgId = msg.key.id;

      if (processedMessages.has(msgId)) return;
      processedMessages.set(msgId, Date.now());

      const text =
        msg.message.conversation ||
        msg.message.extendedTextMessage?.text;

      if (!text) return;

      console.log(
        `📩 [${new Date().toISOString()}] ${msg.key.participant} → ${text}`
      );

      await postWithRetry(`${RECEIVER_URL}/received`, {
        text,
        sender: msg.key.participant,
        timestamp: msg.messageTimestamp,
      });

      console.log("✔ Terkirim ke receiver");
    } catch (err) {
      console.error("❌ Error di message handler:", err.message);
    }
  });
}

// ================= GRACEFUL SHUTDOWN =================
process.on("SIGINT", async () => {
  console.log("🛑 Shutting down bot...");
  if (sock) {
    try {
      await sock.logout();
    } catch (err) {}
  }
  process.exit(0);
});

// ================= START =================
startBot();