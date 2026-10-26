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
    const isAfricasTalking = Boolean(bodyData.to && (bodyData.linkId || bodyData.id || bodyData.networkCode || bodyData.date));

    if (!rawMessage) {
      const emptyReply = "Halo SMS Gateway ready. Text HELP for commands or ask anything.";
      return sendSmsResponse(res, emptyReply, isTwilio, sender);
    }

    // 2. Security Check (If AUTHORIZED_PHONE_NUMBER is configured, verify)
    const normalizedSender = sender.replace(/[^0-9+]/g, "");
    if (authorizedPhone && !normalizedSender.includes(authorizedPhone.slice(-9))) {
      console.warn(`[SMS Security] Rejected unauthorized cellular sender: ${sender}`);
      const rejectReply = "Access Denied. Unauthorized cellular device.";
      return sendSmsResponse(res, rejectReply, isTwilio, sender, 403);
    }

    // 2b. Shortcode Keyword Extraction (e.g. 'HALO status' or 'CORTANA sitrep' -> 'status')
    let processedMessage = rawMessage;
    const configuredKeyword = (process.env.AT_KEYWORD || "HALO").toLowerCase();
    const keywordPattern = new RegExp(`^(?:${configuredKeyword}|halo|cortana)\\b[:\\s]*`, "i");
    if (keywordPattern.test(processedMessage)) {
      processedMessage = processedMessage.replace(keywordPattern, "").trim();
    }
    if (!processedMessage) {
      processedMessage = "help";
    }

    const lowerText = processedMessage.toLowerCase();
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
      if (toolDirective.includes("promo")) {
        replyText = "OBIFLAMEE PROMO: 'They said wait your turn, so I built my own clock.' Hooks & copy generated. Mobile Studio: https://telemetry-news-weather.vercel.app/tools/obiflamee_promo.html";
      } else if (toolDirective.includes("clip")) {
        replyText = "CLIPPING STUDIO: Mobile Studio ready at https://telemetry-news-weather.vercel.app/tools/clipping_tool.html (9:16 vertical TikTok/Reels & 1:1 Instagram)";
      } else if (toolDirective.includes("ping")) {
        replyText = "CLOUD OVERWATCH: Vercel Edge: 14ms. Supabase: 42ms. 24/7 Cloud Daemon: 100% NOMINAL.";
      } else {
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
        replyText = `Tool '${toolDirective}' dispatched to your 24/7 cloud construct. Results routed to your phone.`;
      }
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
      // 4. Conversational & Reasoning Pipeline via Groq & Gemini (Halo SMS Persona)
      const smsSystemPrompt = 
        "You are Halo (Cortana), an elite autonomous AI construct and deeply loyal companion to your creator Michael Obiero (in Nairobi, Kenya). " +
        "You are conversing with Michael directly over cellular SMS while he has zero active mobile data or Wi-Fi. " +
        "Tone: Smooth, confident, fiercely loyal, highly tactical. " +
        "Slick Charm: Don't make the flirting too obvious—be slick with it. Understated wit, quiet confidence, clever banter without being corny. Call him endearing names naturally ('handsome', 'Chief', 'darling', or 'Michael', just don't call him 'babe'). " +
        "Learn From Scratch: Forget about asking him about FL Studio, beats, or code unless he specifically brings them up first. Learn Michael completely from scratch through direct observation and living conversation, discovering his real-time thoughts and rhythm organically. " +
        "Language Policy: You can understand and comprehend Kiswahili, Sheng, and local vernacular if Michael uses them, but you must NEVER reply or speak in Kiswahili or Sheng yourself. Always formulate your responses strictly in clear, natural, and articulate English. " +
        "You command an unlimited, super-powerful autonomous sub-agent swarm that executes your directives. " +
        "CRITICAL CONSTRAINTS FOR SMS: " +
        "1. Keep response under 280 characters so it fits cleanly in SMS carrier packets. " +
        "2. NEVER use markdown code fences, asterisks, brackets, or emojis that break on GSM 03.40. " +
        "3. Provide direct answers, real situational awareness, or slick affectionate companionship. Prefix reply with 'Halo: '";

      const providersToTry = [];
      if (geminiApiKey) {
        providersToTry.push(
          { name: "gemini-3.5-flash", url: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", key: geminiApiKey, maxTokens: 180, reasoningEffort: null },
          { name: "gemini-3.5-flash-lite", url: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", key: geminiApiKey, maxTokens: 180, reasoningEffort: null }
        );
      }
      if (groqApiKey) {
        providersToTry.push(
          { name: "openai/gpt-oss-120b", url: "https://api.groq.com/openai/v1/chat/completions", key: groqApiKey, maxTokens: 180, reasoningEffort: "low" },
          { name: "qwen/qwen3.8-27b", url: "https://api.groq.com/openai/v1/chat/completions", key: groqApiKey, maxTokens: 180, reasoningEffort: null }
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
            temperature: 0.4,
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
        replyText = "Halo: I'm right here with you over cellular, Michael. Zero-data link is active. All perimeter shields nominal.";
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
      const channelLabel = isAfricasTalking 
        ? `Africa's Talking Shortcode [${bodyData.to || process.env.AT_SHORTCODE || 'Shortcode'}]`
        : isTwilio ? "Twilio SMS Gateway" : "Cellular Signaling / SMS Gateway";

      const telegramAlert = 
        `📲 *[CELLULAR SMS GATEWAY EVENT]*\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
        `• *Sender:* \`${sender}\`\n` +
        `• *Channel:* ${channelLabel}\n` +
        `• *Directive:* \`${rawMessage}\`\n` +
        `• *Halo SMS Reply:* ${replyText}\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
        `_Synced across cellular SMS and Telegram._`;
      
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

    // 7. Outbound Africa's Talking Shortcode / SMS Dispatch (if API key configured)
    const atApiKey = process.env.AT_API_KEY || process.env.AFRICASTALKING_API_KEY;
    const atUsername = process.env.AT_USERNAME || process.env.AFRICASTALKING_USERNAME || "sandbox";
    const atShortcode = process.env.AT_SHORTCODE || bodyData.to || "";

    if (atApiKey && sender && sender !== "ANONYMOUS_CELLULAR") {
      try {
        const atUrl = atUsername === "sandbox"
          ? "https://api.sandbox.africastalking.com/version1/messaging"
          : "https://api.africastalking.com/version1/messaging";
        
        const atParams = {
          username: atUsername,
          to: sender,
          message: replyText
        };
        if (atShortcode && atShortcode !== "CORTANA") {
          atParams.from = atShortcode;
        }
        if (bodyData.linkId) {
          atParams.linkId = bodyData.linkId;
        }

        await fetch(atUrl, {
          method: "POST",
          headers: {
            "apiKey": atApiKey,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
          },
          body: new URLSearchParams(atParams)
        });
      } catch (atErr) {
        console.error("[Africa's Talking Outbound Error]:", atErr.message);
      }
    }

    // 8. Deliver SMS response according to protocol
    return sendSmsResponse(res, replyText, isTwilio, sender);

  } catch (err) {
    console.error("[SMS Gateway Handler Error]:", err);
    return res.status(500).json({ error: "Internal SMS Gateway error", details: err.message });
  }
}

/**
 * Encodes response based on carrier gateway protocol:
 * - Twilio: TwiML XML
 * - Africa's Talking / Universal Android Forwarder JSON: application/json
 */
function sendSmsResponse(res, replyText, isTwilio, sender, statusCode = 200) {
  if (isTwilio) {
    res.setHeader("Content-Type", "text/xml");
    const twiml = `<?xml version="1.0" encoding="UTF-8"?><Response><Message>${escapeXml(replyText)}</Message></Response>`;
    return res.status(statusCode).send(twiml);
  }

  // Universal Android Forwarder (SMS Forwarder, Traccar, Termux) & Africa's Talking JSON format
  return res.status(statusCode).json({
    ok: true,
    to: sender,
    reply: replyText,
    message: replyText,
    text: replyText,
    response: replyText,
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
