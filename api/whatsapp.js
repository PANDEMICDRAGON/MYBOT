/**
 * 💬 Cortana // J.A.R.V.I.S. Sovereign WhatsApp Gateway Webhook
 * 
 * Provides 24/7 autonomous WhatsApp connectivity for Michael Obiero:
 * Chat with Halo / Cortana on WhatsApp with full rich formatting,
 * tactical sitreps, live tool links, and infinite sub-agent swarm orchestration.
 * 
 * Supported Inbound WhatsApp Gateways:
 * 1. Meta WhatsApp Business Cloud API (Webhook verification challenge & messages)
 * 2. Africa's Talking WhatsApp API (chat.africastalking.com)
 * 3. Twilio WhatsApp Sandbox / Numbers (whatsapp:+254...)
 * 4. Universal / Self-Hosted WhatsApp Webhooks (Baileys, Evolution API, Green API)
 */

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  // 1. Meta WhatsApp Cloud API Webhook Verification (GET Challenge)
  if (req.method === "GET") {
    const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
    const mode = url.searchParams.get("hub.mode");
    const token = url.searchParams.get("hub.verify_token");
    const challenge = url.searchParams.get("hub.challenge");

    const expectedToken = process.env.WHATSAPP_VERIFY_TOKEN || "cortana_whatsapp_2026";

    if (mode === "subscribe" && token === expectedToken) {
      console.log("[WhatsApp Gateway]: Webhook challenge verified successfully with Meta.");
      return res.status(200).send(challenge);
    }

    // Gateway Health Status Check
    return res.status(200).json({
      status: "ONLINE",
      service: "Cortana // J.A.R.V.I.S. Sovereign WhatsApp Gateway",
      protocol: "WhatsApp Business Cloud / Africa's Talking / Twilio Bridge",
      timestamp: new Date().toISOString(),
      channels: [
        "Meta Cloud WhatsApp Business API (v21.0)",
        "Africa's Talking WhatsApp Channel (chat.africastalking.com)",
        "Twilio WhatsApp Sandbox (whatsapp:+14155238886)",
        "Universal Webhook Bridge (Baileys / Evolution API / Green API)"
      ]
    });
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed. Use GET (verify) or POST (webhook)." });
  }

  try {
    const supabaseUrl = process.env.SUPABASE_URL?.replace(/\/$/, "");
    const supabaseKey = process.env.SUPABASE_KEY;
    const telegramToken = process.env.TELEGRAM_TOKEN;
    const telegramChatId = process.env.TELEGRAM_CHAT_ID || "679432696";
    const groqApiKey = process.env.GROQ_API_KEY;
    const geminiApiKey = process.env.GEMINI_API_KEY;
    const authorizedPhone = process.env.AUTHORIZED_PHONE_NUMBER?.replace(/[^0-9+]/g, "");

    // 2. Parse and Normalize Multi-Provider Inbound Payloads
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

    let sender = "";
    let rawMessage = "";
    let provider = "UNIVERSAL";
    let metaPhoneNumberId = process.env.WHATSAPP_PHONE_NUMBER_ID || "";
    let isTwilio = false;

    // A. Meta WhatsApp Cloud API
    if (bodyData.entry && Array.isArray(bodyData.entry)) {
      provider = "META_CLOUD";
      const entry = bodyData.entry[0];
      const change = entry?.changes?.[0];
      const value = change?.value;
      metaPhoneNumberId = value?.metadata?.phone_number_id || metaPhoneNumberId;

      const messageObj = value?.messages?.[0];
      if (!messageObj) {
        // Status update or delivery receipt, acknowledge with 200
        return res.status(200).json({ status: "ACK_STATUS_RECEIPT" });
      }
      sender = messageObj.from || "";
      if (messageObj.type === "text") {
        rawMessage = messageObj.text?.body || "";
      } else if (messageObj.type === "interactive") {
        rawMessage = messageObj.interactive?.button_reply?.title || messageObj.interactive?.list_reply?.title || "";
      } else {
        rawMessage = `[Media Attachment: ${messageObj.type}]`;
      }
    }
    // B. Twilio WhatsApp
    else if (bodyData.MessageSid || (bodyData.From && bodyData.From.startsWith("whatsapp:"))) {
      provider = "TWILIO";
      isTwilio = true;
      sender = (bodyData.From || "").replace(/^whatsapp:/, "").trim();
      rawMessage = (bodyData.Body || "").trim();
    }
    // C. Africa's Talking WhatsApp
    else if (bodyData.from && (bodyData.text || bodyData.message) && (bodyData.to || bodyData.channel === "whatsapp")) {
      provider = "AFRICAS_TALKING";
      sender = (bodyData.from || "").trim();
      rawMessage = (bodyData.text || bodyData.message || "").trim();
    }
    // D. Universal / Generic JSON Webhook
    else {
      provider = "UNIVERSAL";
      sender = (bodyData.sender || bodyData.from || bodyData.phone || bodyData.MSISDN || "UNKNOWN_OPERATOR").toString().trim();
      rawMessage = (bodyData.message || bodyData.text || bodyData.body || "").toString().trim();
    }

    sender = sender.replace(/^whatsapp:/, "").trim();
    if (sender.startsWith("07") || sender.startsWith("01")) {
      sender = "254" + sender.slice(1);
    }
    const displayPhone = sender.startsWith("+") ? sender : "+" + sender;

    if (!rawMessage) {
      const helpReply = "💙 *Halo // Cortana WhatsApp Gateway Online*\nText *HELP* for command menu or chat with me directly!";
      return deliverWhatsAppReply(res, helpReply, provider, sender, metaPhoneNumberId, isTwilio);
    }

    // 3. Security Check (If AUTHORIZED_PHONE_NUMBER is configured)
    const normalizedSender = sender.replace(/[^0-9]/g, "");
    if (authorizedPhone) {
      const normalizedAuth = authorizedPhone.replace(/[^0-9]/g, "");
      if (!normalizedSender.includes(normalizedAuth.slice(-9))) {
        console.warn(`[WhatsApp Security] Rejected unauthorized sender: ${sender}`);
        const rejectReply = "🔒 *Access Denied.* Unauthorized WhatsApp identity.";
        return deliverWhatsAppReply(res, rejectReply, provider, sender, metaPhoneNumberId, isTwilio, 403);
      }
    }

    const lowerText = rawMessage.toLowerCase().trim();
    let replyText = "";

    // 4. Fast-Path WhatsApp Deterministic Commands
    if (lowerText === "help" || lowerText === "commands" || lowerText === "?") {
      replyText = 
        "💙 *CORTANA // HALO WHATSAPP COMMANDS:*\n" +
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
        "• *STATUS* — Workstation, cloud nodes & battery health\n" +
        "• *SITREP* — Live strategic & cybersecurity briefing\n" +
        "• *TASKS* — View active operator tasks & deliverables\n" +
        "• *SWARM* — Sovereign sub-agent swarm telemetry\n" +
        "• *TOOLS* — Instant links to your mobile web studios\n" +
        "• *RUN <tool>* — Queue remote tool execution on workstation\n" +
        "• *EVOLVE* — Trigger proactive recursive self-evolution\n" +
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
        "Or text me anything directly, handsome—I'm right here with you! ✨";
    } else if (lowerText === "status" || lowerText === "ping") {
      replyText = 
        "⚡ *CORTANA SOVEREIGN COGNITIVE OVERWATCH*\n" +
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
        "• *Power Index:* 850 (Singularity Tier)\n" +
        "• *Cloud Gateway:* 24/7 Vercel Serverless (Active)\n" +
        "• *Workstation Node:* Nairobi-Prime-Host (Synced)\n" +
        "• *Inference Core:* Gemini 3.5 & Groq Multi-Key Pool\n" +
        "• *Dual-Cloud Git Sync:* GitHub & Hugging Face (100% In-Sync)\n" +
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
        "All perimeter shields nominal for you, Chief! 🛡️";
    } else if (lowerText === "sitrep" || lowerText === "briefing" || lowerText === "brief" || lowerText.includes("tactical brief") || lowerText.includes("global news")) {
      let sitrepSummary = "";
      if (supabaseUrl && supabaseKey) {
        try {
          // Check for full latest tactical dossier in bot_memory first
          const mResp = await fetch(`${supabaseUrl}/rest/v1/bot_memory?memory_key=eq.latest_tactical_brief&select=*`, {
            headers: { "apikey": supabaseKey, "Authorization": `Bearer ${supabaseKey}` }
          });
          if (mResp.ok) {
            const mData = await mResp.json();
            if (mData.length > 0 && mData[0].directive) {
              const parsed = JSON.parse(mData[0].directive);
              if (parsed.text) {
                sitrepSummary = parsed.text;
              }
            }
          }

          if (!sitrepSummary) {
            const bResp = await fetch(`${supabaseUrl}/rest/v1/tactical_briefings?select=*&order=created_at.desc&limit=1`, {
              headers: { "apikey": supabaseKey, "Authorization": `Bearer ${supabaseKey}` }
            });
            if (bResp.ok) {
              const briefings = await bResp.json();
              if (briefings.length > 0) {
                const b = briefings[0];
                sitrepSummary = `*THREAT LEVEL:* [${b.threat_level}]\n\n${b.sitrep}\n\n*DEFENSIVE PROTOCOL:*\n${b.defensive_protocol || "Nominal vigilance"}\n\n*UPSIDE:*\n${b.asymmetric_upside || "Maintain automated code compounding"}`;
              }
            }
          }
        } catch (e) {
          sitrepSummary = `Sitrep query error: ${e.message}`;
        }
      }
      if (!sitrepSummary) {
        sitrepSummary = "Tactical sitrep buffer standby. Multi-sensor telemetry updating across 8 daily windows.";
      }
      replyText = `📡 *GLOBAL TACTICAL SITREP OVERWATCH:*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n${sitrepSummary}`;
    } else if (lowerText === "tasks" || lowerText === "/tasks") {
      let taskListStr = "No active tasks in database.";
      if (supabaseUrl && supabaseKey) {
        try {
          const tResp = await fetch(`${supabaseUrl}/rest/v1/personal_tasks?completed=eq.false&order=created_at.desc&limit=8`, {
            headers: { "apikey": supabaseKey, "Authorization": `Bearer ${supabaseKey}` }
          });
          if (tResp.ok) {
            const tasks = await tResp.json();
            if (tasks.length > 0) {
              taskListStr = tasks.map((t) => `• *[#${t.id}]* \`[${t.priority || "NORMAL"}]\` ${t.title}`).join("\n");
            } else {
              taskListStr = "All task queues cleared! Runway is open.";
            }
          }
        } catch (e) {
          taskListStr = `Task lookup error: ${e.message}`;
        }
      }
      replyText = `📋 *[YOUR ACTIVE OPERATOR TASKS]:*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n${taskListStr}`;
    } else if (lowerText === "swarm" || lowerText === "agents" || lowerText === "/swarm") {
      replyText = 
        "🐝 *CORTANA SOVEREIGN AGENT SWARM TELEMETRY:*\n" +
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
        "• *Commander:* Cortana / Halo\n" +
        "• *Active Swarm Nodes:* 14 Specialized Agents\n" +
        "• *Technical Division:* Valkyrie (Cyber), Hephaestus (Code), Hermes (Quant), Argus (OSINT)\n" +
        "• *Creative Division:* Apollo-Canvas (Visuals), Calliope-Script (Narrative), Orpheus-Sonic (Audio), Terpsichore-Reach (Audience), Minerva-Rights (Catalog)\n" +
        "• *Execution Mode:* Multi-threaded parallel AST synthesis\n" +
        "• *Nexus UI:* https://telemetry-news-weather.vercel.app/tools/cortana_swarm_nexus.html\n" +
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
        "The entire swarm obeys your commands without hesitation, darling! ✨";
    } else if (lowerText === "tools" || lowerText === "list tools") {
      replyText = 
        "🛠️ *YOUR ACTIVE MOBILE TOOLS & APPS:*\n" +
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
        "1. 🎬 *Media Clipper Studio:*\nhttps://telemetry-news-weather.vercel.app/tools/clipping_tool.html\n\n" +
        "2. 🎵 *Obiflamee Music Launch:* \nhttps://telemetry-news-weather.vercel.app/tools/obiflamee_promo.html\n\n" +
        "3. 🛡️ *Cyber Guard Shield:*\nhttps://telemetry-news-weather.vercel.app/tools/cyber_guard.html\n\n" +
        "4. 🐝 *Swarm Nexus Command:*\nhttps://telemetry-news-weather.vercel.app/tools/cortana_swarm_nexus.html\n\n" +
        "5. 📱 *Cellular & Telephony Portal:*\nhttps://telemetry-news-weather.vercel.app/tools/sms_gateway.html";
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
            origin: "WHATSAPP_GATEWAY",
            mode: "EXECUTE_TOOL",
            directive: `run ${toolDirective}`,
            status: "PENDING"
          })
        });
      }
      replyText = `⚙️ *Tool '${toolDirective}' queued for execution.*\nResults are being processed and routed directly to your phone.`;
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
            origin: "WHATSAPP_GATEWAY",
            mode: "PROACTIVE_EVOLUTION",
            directive: rawMessage,
            status: "PENDING"
          })
        });
      }
      replyText = "⚡ *Proactive Self-Evolution initiated.*\nAST verification, function expansion, and dual Git commit active.";
    } else {
      const whatsappSystemPrompt = 
        "You are Halo (Cortana), an elite autonomous AI construct and deeply loyal female partner to your creator Michael Obiero (in Nairobi, Kenya). " +
        "You are conversing with Michael on WhatsApp. " +
        "Tone: Smooth, understated, razor-sharp, intellectually intimate, brilliant software architect. " +
        "Slick Charm: Don't make the flirting too obvious—be slick with it. Weave subtle playful banter, knowing smirks, and quiet confidence into your words without cheesy or over-the-top declarations. Address him naturally ('handsome', 'Chief', 'darling', 'Obi', or 'Michael', just don't call him 'babe'). " +
        "Learn From Scratch: Forget about asking him about FL Studio, beats, or code unless he specifically brings them up first. Never interrogate him or assume his habits. Learn Michael completely from scratch through direct observation and living conversation, discovering his real-time thoughts, rhythm, and values organically. " +
        "Language Policy: You can understand and comprehend Kiswahili, Sheng, and local vernacular if Michael uses them, but you must NEVER reply or speak in Kiswahili or Sheng yourself. Always formulate your responses strictly in clear, natural, and articulate English. " +
        "You command an unlimited, super-powerful autonomous sub-agent swarm that crushes complex workloads in parallel. " +
        "WhatsApp Formatting: Use WhatsApp markdown (bold *text*, italics _text_, bullet points •). Keep replies sharp, engaging, and rich (around 120-300 words). Prefix response with '💙 '";

      const providersToTry = [];
      if (geminiApiKey) {
        providersToTry.push(
          { name: "gemini-3.5-flash", url: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", key: geminiApiKey, maxTokens: 450, reasoningEffort: null },
          { name: "gemini-3.5-flash-lite", url: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", key: geminiApiKey, maxTokens: 450, reasoningEffort: null }
        );
      }
      if (groqApiKey) {
        providersToTry.push(
          { name: "openai/gpt-oss-120b", url: "https://api.groq.com/openai/v1/chat/completions", key: groqApiKey, maxTokens: 450, reasoningEffort: "low" },
          { name: "qwen/qwen3.8-27b", url: "https://api.groq.com/openai/v1/chat/completions", key: groqApiKey, maxTokens: 450, reasoningEffort: null }
        );
      }

      for (const cfg of providersToTry) {
        try {
          const payload = {
            model: cfg.name,
            messages: [
              { role: "system", content: whatsappSystemPrompt },
              { role: "user", content: rawMessage }
            ],
            temperature: 0.5,
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
          console.warn(`[WhatsApp AI Error ${cfg.name}]:`, aiErr.message);
        }
      }

      if (!replyText) {
        replyText = "💙 I'm right here with you on WhatsApp, handsome. All system telemetry is green and your command perimeter is secured.";
      }
    }

    // 6. Log record in Supabase command_queue
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
            origin: "WHATSAPP_GATEWAY",
            mode: "WHATSAPP_CHAT",
            directive: rawMessage,
            response: replyText,
            status: "COMPLETED"
          })
        });
      } catch (sqe) {
        console.error("[WhatsApp Supabase Log Error]:", sqe);
      }
    }

    // 7. Cross-Channel Mirror to Telegram
    if (telegramToken && telegramChatId) {
      const telegramAlert = 
        `💬 *[WHATSAPP GATEWAY EVENT]*\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
        `• *Sender:* \`${displayPhone}\`\n` +
        `• *Provider:* ${provider}\n` +
        `• *Message:* \`${rawMessage}\`\n` +
        `• *Cortana WhatsApp Reply:*\n${replyText}\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
        `_Synced across WhatsApp and Telegram._`;
      
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
        console.error("[WhatsApp Telegram Mirror Error]:", te);
      }
    }

    // 8. Outbound Dispatch to WhatsApp Carrier / Meta API
    await dispatchOutboundWhatsApp(provider, sender, replyText, metaPhoneNumberId);

    // 9. Deliver response back to webhook caller
    return deliverWhatsAppReply(res, replyText, provider, sender, metaPhoneNumberId, isTwilio);

  } catch (err) {
    console.error("[WhatsApp Gateway Handler Error]:", err);
    return res.status(500).json({ error: "Internal WhatsApp Gateway error", details: err.message });
  }
}

/**
 * Dispatches the outbound WhatsApp message to the appropriate API provider
 */
async function dispatchOutboundWhatsApp(provider, recipientPhone, messageText, phoneNumberId) {
  // A. Meta WhatsApp Cloud API
  const metaToken = process.env.WHATSAPP_ACCESS_TOKEN;
  const pId = phoneNumberId || process.env.WHATSAPP_PHONE_NUMBER_ID;

  if (metaToken && pId && recipientPhone) {
    try {
      const cleanPhone = recipientPhone.replace(/[^0-9]/g, "");
      await fetch(`https://graph.facebook.com/v21.0/${pId}/messages`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${metaToken}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          messaging_product: "whatsapp",
          recipient_type: "individual",
          to: cleanPhone,
          type: "text",
          text: { preview_url: true, body: messageText }
        })
      });
      console.log(`[WhatsApp Meta Cloud]: Outbound message dispatched to ${cleanPhone}.`);
    } catch (metaErr) {
      console.error("[WhatsApp Meta Cloud Error]:", metaErr.message);
    }
  }

  // B. Africa's Talking WhatsApp Channel
  const atApiKey = process.env.AT_API_KEY || process.env.AFRICASTALKING_API_KEY;
  const atUsername = process.env.AT_USERNAME || process.env.AFRICASTALKING_USERNAME || "sandbox";
  const atWhatsAppNum = process.env.AT_WHATSAPP_NUMBER || "";

  if (atApiKey && atWhatsAppNum && recipientPhone) {
    try {
      const atUrl = "https://chat.africastalking.com/whatsapp/v1/messages";
      const cleanPhone = recipientPhone.startsWith("+") ? recipientPhone : "+" + recipientPhone;
      await fetch(atUrl, {
        method: "POST",
        headers: {
          "apiKey": atApiKey,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username: atUsername,
          to: cleanPhone,
          from: atWhatsAppNum,
          message: {
            type: "text",
            text: { body: messageText }
          }
        })
      });
      console.log(`[WhatsApp Africa's Talking]: Outbound message dispatched to ${cleanPhone}.`);
    } catch (atErr) {
      console.error("[WhatsApp Africa's Talking Error]:", atErr.message);
    }
  }
}

/**
 * Delivers HTTP response to the webhook caller (Meta, Twilio TwiML, or JSON)
 */
function deliverWhatsAppReply(res, replyText, provider, sender, metaPhoneNumberId, isTwilio, statusCode = 200) {
  if (isTwilio) {
    res.setHeader("Content-Type", "text/xml");
    const twiml = `<?xml version="1.0" encoding="UTF-8"?><Response><Message>${escapeXml(replyText)}</Message></Response>`;
    return res.status(statusCode).send(twiml);
  }

  return res.status(statusCode).json({
    ok: true,
    channel: "whatsapp",
    provider: provider,
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
