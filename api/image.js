// api/image.js - Vercel Serverless Function
// High-Fidelity Humanlike Visual Synthesis & Avatar Engine
// Powered by Higgsfield AI SOUL v2 & Black Forest Labs FLUX.1 Realism
// Operates 24/7 on Vercel's global edge infrastructure with direct Telegram photo relay.

export default async function handler(req, res) {
  // CORS & Security Headers
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, x-operator-passcode, x-higgsfield-key");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  const token = process.env.TELEGRAM_TOKEN;
  const authorizedChatId = process.env.TELEGRAM_CHAT_ID || process.env.AUTHORIZED_CHAT_ID || "679432696";
  const supabaseUrl = (process.env.SUPABASE_URL || "https://vutamfqgckrzsnbcgrne.supabase.co").replace(/\/$/, "");
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_KEY || "";

  // Dimension mapping by aspect ratio
  const ratioMap = {
    "1:1": { width: 1024, height: 1024, label: "Square Avatar (1:1)" },
    "9:16": { width: 768, height: 1344, label: "Mobile Portrait (9:16)" },
    "16:9": { width: 1344, height: 768, label: "Cinematic Landscape (16:9)" },
    "4:5": { width: 896, height: 1120, label: "Portrait (4:5)" }
  };

  // Aesthetic modifiers optimized for authentic human realism (eliminates artificial plastic/CGI look)
  const styleModifiers = {
    humanlike: "hyper-realistic candid portrait of an authentic real human being, lifelike expressive eyes with natural moisture and fine reflections, natural skin pores, realistic skin micro-texture, subtle natural imperfections, authentic subsurface scattering, real human hair texture, soft directional studio lighting, shot on 85mm f/1.4 lens, 35mm photograph, shallow depth of field, creamy bokeh, real photography, no plastic skin, no 3d render, no cgi, no doll",
    photorealistic: "masterpiece 35mm portrait photograph, natural human skin texture with real pores, authentic subsurface scattering, sharp eyes, natural lighting, shot on 85mm f/1.4 lens, raw candid photograph, no 3d render, no cartoon, no plastic",
    editorial: "high-fashion editorial magazine portrait photograph, authentic human model, natural skin texture, sophisticated studio lighting, shot on Hasselblad medium format camera, Vogue aesthetic, 8k",
    cinematic: "cinematic 35mm motion picture still, authentic human characters, natural skin tones, dramatic soft lighting, shallow depth of field, Panavision anamorphic lens, realistic film grain, photorealistic",
    cybernetic: "futuristic cybernetic human portrait, real human face with subtle chrome neural inlays, translucent holographic HUD reflections, volumetric lighting, photorealistic cinematic portrait"
  };

  try {
    let params = {};
    if (req.method === "GET") {
      params = req.query || {};
    } else {
      params = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    }

    const rawPrompt = (params.prompt || "").trim();
    if (!rawPrompt) {
      return res.status(400).json({ error: "Visual prompt is required." });
    }

    const style = (params.style || "humanlike").toLowerCase();
    const ratio = params.ratio || "1:1";
    const dimensions = ratioMap[ratio] || ratioMap["1:1"];
    const shouldRelayTelegram = params.relay_telegram === true || params.relay_telegram === "true";
    const seed = params.seed ? parseInt(params.seed, 10) : Math.floor(Math.random() * 1000000);

    // Build enhanced prompt
    const modifier = styleModifiers[style] || styleModifiers.humanlike;
    const finalPrompt = `${rawPrompt}, ${modifier}`;

    // Higgsfield AI API Credential Check
    const hfKey = params.higgsfield_key || req.headers["x-higgsfield-key"] || process.env.HIGGSFIELD_KEY || 
      (process.env.HIGGSFIELD_KEY_ID && process.env.HIGGSFIELD_KEY_SECRET ? `${process.env.HIGGSFIELD_KEY_ID}:${process.env.HIGGSFIELD_KEY_SECRET}` : null);

    let imageUrl = null;
    let engineUsed = "Black Forest Labs FLUX.1 Realism";

    // 1. TIER 1: If Higgsfield API credentials present, synthesize via Higgsfield SOUL v2
    if (hfKey && (params.engine === "higgsfield" || !params.engine)) {
      try {
        const hfRes = await fetch("https://api.higgsfield.ai/higgsfield-ai/soul/v2/standard", {
          method: "POST",
          headers: {
            "Authorization": `Key ${hfKey}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            prompt: finalPrompt,
            resolution: "1080p",
            aspect_ratio: ratio === "9:16" ? "9:16" : (ratio === "16:9" ? "16:9" : "1:1"),
            enhance_prompt: true
          }),
          signal: AbortSignal.timeout(15000)
        });

        if (hfRes.ok) {
          const hfData = await hfRes.json();
          const statusUrl = hfData.status_url;
          if (statusUrl) {
            // Poll for completion (up to 12 attempts * 4s = ~48s)
            for (let i = 0; i < 12; i++) {
              await new Promise(resolve => setTimeout(resolve, 4000));
              const pollRes = await fetch(statusUrl, {
                headers: { "Authorization": `Key ${hfKey}` },
                signal: AbortSignal.timeout(10000)
              });
              if (pollRes.ok) {
                const pollData = await pollRes.json();
                if (pollData.status === "completed" && pollData.output) {
                  imageUrl = Array.isArray(pollData.output) ? pollData.output[0] : (pollData.output.url || pollData.output);
                  engineUsed = "Higgsfield AI SOUL v2";
                  break;
                } else if (pollData.status === "failed" || pollData.status === "canceled") {
                  break;
                }
              }
            }
          }
        }
      } catch (hfErr) {
        console.warn("[Higgsfield SOUL Dispatch Fallback]:", hfErr.message);
      }
    }

    // 2. TIER 2: High-Performance FLUX.1 Realism Engine (Active Default / Fallback)
    if (!imageUrl) {
      const encodedPrompt = encodeURIComponent(finalPrompt);
      imageUrl = `https://image.pollinations.ai/prompt/${encodedPrompt}?model=flux-realism&width=${dimensions.width}&height=${dimensions.height}&nologo=true&seed=${seed}`;
      engineUsed = "Black Forest Labs FLUX.1 Realism";
    }

    let telegramDispatched = false;
    let telegramError = null;

    // Relay to Telegram if requested
    if (shouldRelayTelegram && token && authorizedChatId) {
      try {
        const caption = 
          `👤 *[CORTANA HUMANLIKE AVATAR // ${engineUsed.toUpperCase()}]*\n` +
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
          `✨ *Subject:* \`${rawPrompt}\`\n` +
          `⚙️ *Engine:* \`${engineUsed} (${dimensions.width}x${dimensions.height})\`\n` +
          `🔬 *Aesthetic:* \`${style.toUpperCase()} (Photorealistic Human)\` | *Seed:* \`${seed}\`\n` +
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
          `_Lifelike human avatar synthesized and delivered directly to your phone._`;

        const tgRes = await fetch(`https://api.telegram.org/bot${token}/sendPhoto`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            chat_id: authorizedChatId,
            photo: imageUrl,
            caption: caption,
            parse_mode: "Markdown"
          })
        });

        if (tgRes.ok) {
          telegramDispatched = true;
        } else {
          // Retry without parse_mode in case of markdown formatting mismatch
          const tgRes2 = await fetch(`https://api.telegram.org/bot${token}/sendPhoto`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              chat_id: authorizedChatId,
              photo: imageUrl,
              caption: caption.replace(/[*_`]/g, "")
            })
          });
          telegramDispatched = tgRes2.ok;
          if (!tgRes2.ok) {
            telegramError = await tgRes2.text();
          }
        }
      } catch (tgEx) {
        console.error("[Telegram Image Relay Error]:", tgEx);
        telegramError = tgEx.message;
      }
    }

    // Persist latest generation metadata in Supabase
    if (supabaseUrl && supabaseKey) {
      try {
        const record = {
          prompt: rawPrompt,
          enhanced_prompt: finalPrompt,
          image_url: imageUrl,
          style: style,
          ratio: ratio,
          width: dimensions.width,
          height: dimensions.height,
          seed: seed,
          engine: engineUsed,
          telegram_sent: telegramDispatched,
          created_at: new Date().toISOString()
        };

        await fetch(`${supabaseUrl}/rest/v1/bot_memory?on_conflict=memory_key`, {
          method: "POST",
          headers: {
            "apikey": supabaseKey,
            "Authorization": `Bearer ${supabaseKey}`,
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
          },
          body: JSON.stringify({
            memory_key: "latest_generated_image",
            directive: JSON.stringify(record)
          })
        });
      } catch (sbEx) {
        console.warn("[Supabase Image Save Error]:", sbEx);
      }
    }

    return res.status(200).json({
      status: "SUCCESS",
      image_url: imageUrl,
      prompt: rawPrompt,
      enhanced_prompt: finalPrompt,
      style: style,
      ratio: ratio,
      dimensions: dimensions,
      seed: seed,
      model: engineUsed,
      higgsfield_enabled: Boolean(hfKey),
      telegram_dispatched: telegramDispatched,
      telegram_error: telegramError,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error("[Visual Synthesis Error]:", error);
    return res.status(500).json({
      error: "Visual synthesis engine encountered an internal fault.",
      details: error.message
    });
  }
}
