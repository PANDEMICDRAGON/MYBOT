// api/sports.js - Vercel Serverless Function
// Real-time minute-by-minute EPL (Premier League) and F1 (Formula 1) Live Telemetry API

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS,POST");
  res.setHeader(
    "Access-Control-Allow-Headers",
    "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version"
  );
  res.setHeader("Cache-Control", "public, s-maxage=30, stale-while-revalidate=60");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  try {
    const [eplRes, f1NextRes, f1StandingsRes] = await Promise.allSettled([
      fetch("https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard", {
        headers: { "User-Agent": "Mozilla/5.0 (compatible; SportsWire/2.0)" }
      }),
      fetch("https://api.jolpi.ca/ergast/f1/current/next.json", {
        headers: { "User-Agent": "Mozilla/5.0 (compatible; SportsWire/2.0)" }
      }),
      fetch("https://api.jolpi.ca/ergast/f1/current/driverStandings.json", {
        headers: { "User-Agent": "Mozilla/5.0 (compatible; SportsWire/2.0)" }
      })
    ]);

    // 1. Process EPL Matches
    const eplMatches = [];
    if (eplRes.status === "fulfilled" && eplRes.value.ok) {
      const data = await eplRes.value.json();
      const events = data.events || [];
      for (const ev of events) {
        const comp = (ev.competitions && ev.competitions[0]) || {};
        const teams = comp.competitors || [];
        const home = teams.find(t => t.homeAway === "home") || {};
        const away = teams.find(t => t.homeAway === "away") || {};
        const statusObj = ev.status || {};
        const typeObj = statusObj.type || {};

        eplMatches.push({
          id: ev.id,
          name: ev.name,
          short_name: ev.shortName,
          state: typeObj.state || "pre", // 'in' = LIVE, 'pre' = UPCOMING, 'post' = FT
          status_detail: typeObj.detail || typeObj.description || "Scheduled",
          clock: statusObj.displayClock || "",
          period: statusObj.period || 0,
          date: ev.date,
          venue: comp.venue?.fullName || "",
          home: {
            name: home.team?.displayName || "Home Team",
            short: home.team?.shortDisplayName || "Home",
            abbr: home.team?.abbreviation || "H",
            score: home.score || "0",
            logo: home.team?.logo || `https://a.espncdn.com/i/teamlogos/soccer/500/${home.id}.png`
          },
          away: {
            name: away.team?.displayName || "Away Team",
            short: away.team?.shortDisplayName || "Away",
            abbr: away.team?.abbreviation || "A",
            score: away.score || "0",
            logo: away.team?.logo || `https://a.espncdn.com/i/teamlogos/soccer/500/${away.id}.png`
          }
        });
      }
    }

    // 2. Process F1 Next Race
    let f1Next = null;
    if (f1NextRes.status === "fulfilled" && f1NextRes.value.ok) {
      const data = await f1NextRes.value.json();
      const races = data.MRData?.RaceTable?.Races || [];
      if (races.length > 0) {
        const r = races[0];
        f1Next = {
          race_name: r.raceName,
          season: r.season,
          round: r.round,
          date: r.date,
          time: r.time,
          circuit: {
            name: r.Circuit?.circuitName,
            locality: r.Circuit?.Location?.locality,
            country: r.Circuit?.Location?.country
          }
        };
      }
    }

    // 3. Process F1 Driver Standings
    const f1Standings = [];
    if (f1StandingsRes.status === "fulfilled" && f1StandingsRes.value.ok) {
      const data = await f1StandingsRes.value.json();
      const lists = data.MRData?.StandingsTable?.StandingsLists || [];
      if (lists.length > 0) {
        const drivers = lists[0].DriverStandings || [];
        for (const d of drivers.slice(0, 10)) {
          f1Standings.push({
            position: d.position,
            points: d.points,
            wins: d.wins,
            driver: `${d.Driver?.givenName || ""} ${d.Driver?.familyName || ""}`.trim(),
            code: d.Driver?.code || "",
            nationality: d.Driver?.nationality || "",
            team: (d.Constructors && d.Constructors[0]?.name) || "Constructor"
          });
        }
      }
    }

    const liveEplCount = eplMatches.filter(m => m.state === "in").length;

    return res.status(200).json({
      success: true,
      updated_at: new Date().toISOString(),
      epl: {
        league: "English Premier League",
        live_count: liveEplCount,
        total_count: eplMatches.length,
        matches: eplMatches
      },
      f1: {
        next_race: f1Next,
        standings: f1Standings
      }
    });

  } catch (err) {
    return res.status(500).json({
      error: "Error aggregating live EPL and F1 sports telemetry.",
      message: err.message
    });
  }
}
