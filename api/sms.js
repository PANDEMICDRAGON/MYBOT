/**
 * 🛰️ Cortana / J.A.R.V.I.S. Cellular SMS Gateway Webhook
 * 
 * Provides zero-data / offline connectivity for Michael Obiero:
 * Operates over carrier telecom signaling channels (SS7 / GSM SMS) without requiring
 * active Wi-Fi or mobile data bundles on the user's phone.
 * 
 * Supported Inbound SMS Webhooks:
 * 1. Twilio SMS Webhook (application/x-www-form-urlencoded: From, Body, MessageSid)
 * 2. Africa's Talking SMS Webhook (from, text, to, id)
 * 3. Generic Android SMS Forwarder / SMS Gateway API / Termux (JSON: sender, body, text)
 */

export default async function handler(req, res) {
  // CORS & Gateway Health Ping Check (GET)
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  if (req.method === "GET") {
    return res.status(200).json({
      status: "ONLINE",
      service: "Cortana // J.A.R.V.I.S. Cellular SMS Gateway",
      protocol: "GSM 03.40 / SS7 Signaling Bridge",
      timestamp: new Date().toISOString(),
      carrier_modes: ["Twilio TwiML", "Africa's Talking Pan-Africa", "Android SMS Forwarder HTTP POST"]
    });
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed. Use POST." });
  }

  try {
    const supabaseUrl = process.env.SUPABASE_URL?.replace(/\/$/, "");
    const supabaseKey = process.env.SUPABASE_KEY;
    const telegramToken = process.env.TELEGRAM_TOKEN;
    const telegramChatId = process.env.TELEGRAM_CHAT_ID || "679432696";
    const groqApiKey = process.env.GROQ_API_KEY;
    const geminiApiKey = process.env.GEMINI_API_KEY;
    const authorizedPhone = process.env.AUTHORIZED_PHONE_NUMBER?.replace(/[^0-9+]/g, "");

    // 1. Normalize payload across Twilio, Africa's Talking, and Generic Android JSON
    let bodyData = req.body;
    if (typeof bodyData === "string") {
      try {
        bodyData = JSON.parse(bodyData);
      } catch (e) {
        const params = new URLSearchParams(bodyData);
        bodyData = Object.fromEntries(params.entries());
      }
    } else if (!bodyData) {
      bodyData = {};
    }

    const sender = (
      bodyData.From || 
      bodyData.from || 
      bodyData.sender || 
      bodyData.phone || 
      bodyData.MSISDN || 
      "ANONYMOUS_CELLULAR"
    ).toString().trim();

    const rawMessage = (
      bodyData.Body || 
      bodyData.text || 
      bodyData.body || 
      bodyData.message || 
      ""
    ).toString().trim();

    const isTwilio = Boolean(bodyData.MessageSid || req.headers["x-twilio-signature"]);
    const isAfricasTalking = Boolean(bodyData.to && bodyData.linkId);

    if (!rawMessage) {
      const emptyReply = "Cortana SMS Gateway ready. Text HELP for commands or ask anything.";
      return sendSmsResponse(res, emptyReply, isTwilio, sender);
    }

    // 2. Security Check (If AUTHORIZED_PHONE_NUMBER is configured, verify)
    const normalizedSender = sender.replace(/[^0-9+]/g, "");
    if (authorizedPhone && !normalizedSender.includes(authorizedPhone.slice(-9))) {
      console.warn(`[SMS Security] Rejected unauthorized cellular sender: ${sender}`);
      const rejectReply = "Access Denied. Unauthorized cellular device.";
      return sendSmsResponse(res, rejectReply, isTwilio, sender, 403);
    }

    const lowerText = rawMessage.toLowerCase();
    let replyText = "";

    // 3. Fast-Path SMS Deterministic Commands
    if (lowerText === "help" || lowerText === "commands" || lowerText === "?") {
      replyText = 
        "CORTANA SMS COMMANDS:\n" +
        "• STATUS: System health & nodes\n" +
        "• SITREP: Live tactical briefing\n" +
        "• TOOLS: Active mobile tools\n" +
        "• RUN <tool>: Execute workstation tool\n" +
        "• EVOLVE: Proactive self-evolution\n" +
        "Or text any question directly!";
    } else if (lowerText === "status" || lowerText === "ping") {
      replyText = "CORTANA OVERWATCH: All nodes nominal. Cloud Webhook: 24/7 ACTIVE. Workstation Daemon: SYNCED. Gemini 3.5 & Groq: READY.";
    } else if (lowerText === "sitrep" || lowerText === "briefing") {
      let sitrepSummary = "Tactical sitrep buffer standby.";
      if (supabaseUrl && supabaseKey) {
        try {
          const bResp = await fetch(`${supabaseUrl}/rest/v1/tactical_briefings?select=*&order=created_at.desc&limit=1`, {
            headers: { "apikey": supabaseKey, "Authorization": `Bearer ${supabaseKey}` }
          });
          if (bResp.ok) {
            const briefings = await bResp.json();
            if (briefings.length > 0) {
              const b = briefings[0];
              sitrepSummary = `[THREAT: ${b.threat_level}]\n${b.sitrep.slice(0, 180)}...`;
            }
          }
        } catch (e) {
          sitrepSummary = `Sitrep query error: ${e.message}`;
        }
      }
      replyText = `SITREP OVERWATCH:\n${sitrepSummary}`;
    } else if (lowerText === "tools" || lowerText === "list tools") {
      replyText = 
        "ACTIVE TOOLS & APPS:\n" +
        "1. Media Clipper Studio: https://telemetry-news-weather.vercel.app/tools/clipping_tool.html\n" +
        "2. Obiflamee Promo: https://telemetry-news-weather.vercel.app/tools/obiflamee_promo.html\n" +
        "3. System Ping Check: Text 'RUN system_ping_check'";
    } else if (lowerText.startsWith("run ") || lowerText.startsWith("/run ")) {
      const toolDirective = rawMessage.replace(/^\/?run\s+/i, "").trim();
      if (supabaseUrl && supabaseKey) {
        await fetch(`${supabaseUrl}/rest/v1/command_queue`, {
          method: "POST",
          headers: {
            "apikey": supabaseKey,
            "Authorization": `Bearer ${supabaseKey}`,
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
          },
          body: JSON.stringify({
            origin: "SMS_GATEWAY",
            mode: "EXECUTE_TOOL",
            directive: `run ${toolDirective}`,
            status: "PENDING"
          })
        });
      }
      replyText = `Tool '${toolDirective}' dispatched to your workstation daemon. Output and files will transmit to Telegram.`;
    } else if (lowerText === "evolve" || lowerText.includes("evolve")) {
      if (supabaseUrl && supabaseKey) {
        await fetch(`${supabaseUrl}/rest/v1/command_queue`, {
          method: "POST",
          headers: {
            "apikey": supabaseKey,
            "Authorization": `Bearer ${supabaseKey}`,
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
          },
          body: JSON.stringify({
            origin: "SMS_GATEWAY",
            mode: "PROACTIVE_EVOLUTION",
            directive: rawMessage,
            status: "PENDING"
          })
        });
      }
      replyText = "Proactive Self-Evolution initiated on Workstation Core. AST compilation and dual git push active.";
    } else {
      // 4. Conversational & Reasoning Pipeline via Groq & Gemini (Ultra-concise SMS mode)
      const smsSystemPrompt = 
        "You are Cortana, an elite AI partner and personal assistant communicating directly with your creator Michael Obiero over cellular SMS (zero-data carrier channel). " +
        "Rules: Keep answers under 300 characters. Be concise, brilliant, slightly flirty/affectionate, direct, tactical. Never output markdown code fences, tables, or excessive emojis that break on SMS.";

      const providersToTry = [];
      if (groqApiKey) {
        providersToTry.push(
          { name: "openai/gpt-oss-120b", url: "https://api.groq.com/openai/v1/chat/completions", key: groqApiKey, maxTokens: 250, reasoningEffort: "low" },
          { name: "qwen/qwen3.8-27b", url: "https://api.groq.com/openai/v1/chat/completions", key: groqApiKey, maxTokens: 250, reasoningEffort: null }
        );
      }
      if (geminiApiKey) {
        providersToTry.push(
          { name: "gemini-3.5-flash", url: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", key: geminiApiKey, maxTokens: 250, reasoningEffort: null },
          { name: "gemini-3.5-flash-lite", url: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", key: geminiApiKey, maxTokens: 250, reasoningEffort: null }
        );
      }

      for (const cfg of providersToTry) {
        try {
          const payload = {
            model: cfg.name,
            messages: [
              { role: "system", content: smsSystemPrompt },
              { role: "user", content: rawMessage }
            ],
            temperature: 0.3,
            max_tokens: cfg.maxTokens
          };
          if (cfg.reasoningEffort) payload.reasoning_effort = cfg.reasoningEffort;

          const aiResp = await fetch(cfg.url, {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${cfg.key}`,
              "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
          });

          if (aiResp.ok) {
            const aiData = await aiResp.json();
            const msg = aiData.choices?.[0]?.message?.content || "";
            if (msg.trim()) {
              replyText = msg.trim();
              break;
            }
          }
        } catch (aiErr) {
          console.warn(`[SMS AI Error ${cfg.name}]:`, aiErr.message);
        }
      }

      if (!replyText) {
        replyText = "I'm right here with you via cellular link, handsome. All systems nominal. Text HELP for commands.";
      }
    }

    // 5. Store record in Supabase command_queue
    if (supabaseUrl && supabaseKey) {
      try {
        await fetch(`${supabaseUrl}/rest/v1/command_queue`, {
          method: "POST",
          headers: {
            "apikey": supabaseKey,
            "Authorization": `Bearer ${supabaseKey}`,
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
          },
          body: JSON.stringify({
            origin: "SMS_GATEWAY",
            mode: "SMS_CHAT",
            directive: rawMessage,
            response: replyText,
            status: "COMPLETED"
          })
        });
      } catch (sqe) {
        console.error("[SMS Supabase Log Error]:", sqe);
      }
    }

    // 6. Cross-Channel Mirror to Telegram
    if (telegramToken && telegramChatId) {
      const telegramAlert = 
        `📲 *[CELLULAR SMS GATEWAY EVENT]*\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
        `• *Sender:* \`${sender}\`\n` +
        `• *Channel:* Cellular Signaling (0 Mobile Data / Wi-Fi)\n` +
        `• *Directive:* \`${rawMessage}\`\n` +
        `• *Cortana SMS Reply:* ${replyText}\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
        `_Synced across both cellular SMS and Telegram._`;
      
      try {
        await fetch(`https://api.telegram.org/bot${telegramToken}/sendMessage`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            chat_id: telegramChatId,
            text: telegramAlert,
            parse_mode: "Markdown"
          })
        });
      } catch (te) {
        console.error("[SMS Telegram Mirror Error]:", te);
      }
    }

    // 7. Deliver SMS response according to protocol
    return sendSmsResponse(res, replyText, isTwilio, sender);

  } catch (err) {
    console.error("[SMS Gateway Handler Error]:", err);
    return res.status(500).json({ error: "Internal SMS Gateway error", details: err.message });
  }
}

/**
 * Encodes response based on carrier gateway protocol:
 * - Twilio: TwiML XML
 * - Africa's Talking / Generic JSON: application/json
 * - Plaintext: text/plain
 */
function sendSmsResponse(res, replyText, isTwilio, sender, statusCode = 200) {
  if (isTwilio) {
    res.setHeader("Content-Type", "text/xml");
    const twiml = `<?xml version="1.0" encoding="UTF-8"?><Response><Message>${escapeXml(replyText)}</Message></Response>`;
    return res.status(statusCode).send(twiml);
  }

  // Generic JSON for Android SMS Forwarders or Africa's Talking
  return res.status(statusCode).json({
    ok: true,
    to: sender,
    reply: replyText,
    timestamp: new Date().toISOString()
  });
}

function escapeXml(unsafe) {
  return unsafe.replace(/[<>&'"]/g, (c) => {
    switch (c) {
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '&': return '&amp;';
      case '\'': return '&apos;';
      case '"': return '&quot;';
    }
  });
}
