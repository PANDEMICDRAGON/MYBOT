// api/image.js - Vercel Serverless Function
// High-Fidelity Holographic Visual Synthesis Engine powered by Black Forest Labs FLUX.1
// Operates 24/7 on Vercel's global edge infrastructure with direct Telegram photo relay.

export default async function handler(req, res) {
  // CORS & Security Headers
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, x-operator-passcode");

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

  // Style matrix modifier tokens
  const styleModifiers = {
    photorealistic: "masterpiece, 8k photorealistic portrait, intricate facial details, sharp focus, cinematic studio lighting, shot on 35mm lens, subsurface scattering, octane render",
    cybernetic: "holographic cybernetic AI construct, glowing cyan and electric blue neural circuits, translucent particle matrix, Stark Industries / Halo Cortana UNSC aesthetic, volumetric neon lighting, 8k octane render",
    cinematic: "cinematic movie still, dramatic chiaroscuro lighting, shallow depth of field, anamorphic lens flare, 8k resolution, IMAX masterpiece, atmospheric particles and mist",
    anime: "masterpiece anime digital artwork, crisp lines, Makoto Shinkai vibrant aesthetic, Studio Ghibli cinematic lighting, stunning atmospheric composition",
    octane3d: "3D Octane render, raytraced reflections, metallic and glass textures, photorealistic materials, Unreal Engine 5 aesthetic, volumetric lighting, 8k"
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

    const style = (params.style || "photorealistic").toLowerCase();
    const ratio = params.ratio || "1:1";
    const dimensions = ratioMap[ratio] || ratioMap["1:1"];
    const shouldRelayTelegram = params.relay_telegram === true || params.relay_telegram === "true";
    const seed = params.seed ? parseInt(params.seed, 10) : Math.floor(Math.random() * 1000000);

    // Build enhanced prompt
    const modifier = styleModifiers[style] || styleModifiers.photorealistic;
    const finalPrompt = `${rawPrompt}, ${modifier}`;

    // Direct FLUX.1 generation endpoint (Black Forest Labs FLUX.1 via high-speed edge CDN)
    const encodedPrompt = encodeURIComponent(finalPrompt);
    const imageUrl = `https://image.pollinations.ai/prompt/${encodedPrompt}?model=flux&width=${dimensions.width}&height=${dimensions.height}&nologo=true&seed=${seed}`;

    let telegramDispatched = false;
    let telegramError = null;

    // Relay to Telegram if requested
    if (shouldRelayTelegram && token && authorizedChatId) {
      try {
        const caption = 
          `🎨 *[CORTANA VISUAL SYNTHESIS // FLUX.1 CORE]*\n` +
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
          `✨ *Subject:* \`${rawPrompt}\`\n` +
          `⚙️ *Engine:* \`Black Forest Labs FLUX.1 (${dimensions.width}x${dimensions.height})\`\n` +
          `🔮 *Aesthetic:* \`${style.toUpperCase()}\` | *Seed:* \`${seed}\`\n` +
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
          `_Visual asset synthesized and delivered directly to your phone._`;

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
          // Retry without parse_mode in case of formatting mismatch
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
      model: "Black Forest Labs FLUX.1",
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
