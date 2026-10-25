// api/command.js - Vercel Serverless Function
// Bridges Mobile Web HUD to Supabase command_queue using service role credentials

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS,PATCH,DELETE,POST,PUT");
  res.setHeader(
    "Access-Control-Allow-Headers",
    "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, x-operator-passcode"
  );

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  const supabaseUrl = (process.env.SUPABASE_URL || "https://vutamfqgckrzsnbcgrne.supabase.co").replace(/\/$/, "");
  const supabaseKey = process.env.SUPABASE_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1dGFtZnFnY2tyenNuYmNncm5lIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MjkyMTU3MCwiZXhwIjoyMTA4NDk3NTcwfQ.apKPZ82_p8pmpvcXoayE5JLYtubg3Uc6WSfOZ76v1t4";

  if (req.method === "GET") {
    try {
      const { id } = req.query;
      const queryUrl = id 
        ? `${supabaseUrl}/rest/v1/command_queue?id=eq.${id}&select=*`
        : `${supabaseUrl}/rest/v1/command_queue?select=*&order=created_at.desc&limit=10`;
      const resp = await fetch(queryUrl, {
        method: "GET",
        headers: {
          "apikey": supabaseKey,
          "Authorization": `Bearer ${supabaseKey}`,
          "Content-Type": "application/json"
        }
      });
      if (!resp.ok) {
        return res.status(resp.status).json({ error: "Failed to fetch command_queue" });
      }
      const data = await resp.json();
      return res.status(200).json(id ? (data[0] || null) : data);
    } catch (err) {
      return res.status(500).json({ error: "Server error querying command", details: err.message });
    }
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed. Use GET or POST." });
  }

  try {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    let { origin = "WEB", mode = "CHAT", directive = "", passcode = "" } = body;

    if (!directive && (body.command === "port_scan" || body.command === "fingerprint" || body.command === "port_audit")) {
      const targetIp = body.target_ip || "192.168.100.1";
      const profile = (body.profile || body.port_profile || "standard").toLowerCase();
      directive = `/portscan ${targetIp} ${profile}`;
      mode = "PORT-SCAN";
    }

    if (!directive || !directive.trim()) {
      return res.status(400).json({ error: "Directive or valid command target is required." });
    }

    const supabaseUrl = (process.env.SUPABASE_URL || "https://vutamfqgckrzsnbcgrne.supabase.co").replace(/\/$/, "");
    const supabaseKey = process.env.SUPABASE_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1dGFtZnFnY2tyenNuYmNncm5lIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MjkyMTU3MCwiZXhwIjoyMTA4NDk3NTcwfQ.apKPZ82_p8pmpvcXoayE5JLYtubg3Uc6WSfOZ76v1t4";

    const insertPayload = {
      origin: origin,
      mode: mode,
      directive: directive.trim(),
      status: "PENDING"
    };

    const resp = await fetch(`${supabaseUrl}/rest/v1/command_queue`, {
      method: "POST",
      headers: {
        "apikey": supabaseKey,
        "Authorization": `Bearer ${supabaseKey}`,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
      },
      body: JSON.stringify(insertPayload)
    });

    if (!resp.ok) {
      const errText = await resp.text();
      return res.status(resp.status).json({
        error: "Supabase command_queue insertion rejected.",
        details: errText
      });
    }

    const createdRows = await resp.json();
    return res.status(200).json({
      success: true,
      message: "Directive successfully queued for autonomous execution.",
      queued: Array.isArray(createdRows) ? createdRows[0] : createdRows
    });
  } catch (error) {
    return res.status(500).json({
      error: "Internal server error queuing directive.",
      message: error.message
    });
  }
}
