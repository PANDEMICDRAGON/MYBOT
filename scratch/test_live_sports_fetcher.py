import httpx
import asyncio
import json
from datetime import datetime, timezone

async def fetch_live_sports():
    async with httpx.AsyncClient(timeout=10) as client:
        # 1. EPL Scoreboard
        epl_matches = []
        try:
            r = await client.get("https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard")
            if r.status_code == 200:
                events = r.json().get("events", [])
                for ev in events:
                    comp = ev.get("competitions", [{}])[0]
                    teams = comp.get("competitors", [])
                    home_team = next((t for t in teams if t.get("homeAway") == "home"), {})
                    away_team = next((t for t in teams if t.get("homeAway") == "away"), {})
                    status_info = ev.get("status", {})
                    state = status_info.get("type", {}).get("state", "pre")  # pre, in, post
                    detail = status_info.get("type", {}).get("detail", "")
                    clock = status_info.get("displayClock", "")

                    epl_matches.append({
                        "id": ev.get("id"),
                        "name": ev.get("name"),
                        "home": {
                            "name": home_team.get("team", {}).get("displayName", "Home"),
                            "short": home_team.get("team", {}).get("shortDisplayName", "Home"),
                            "abbr": home_team.get("team", {}).get("abbreviation", "H"),
                            "score": home_team.get("score", "0"),
                            "logo": home_team.get("team", {}).get("logo", "")
                        },
                        "away": {
                            "name": away_team.get("team", {}).get("displayName", "Away"),
                            "short": away_team.get("team", {}).get("shortDisplayName", "Away"),
                            "abbr": away_team.get("team", {}).get("abbreviation", "A"),
                            "score": away_team.get("score", "0"),
                            "logo": away_team.get("team", {}).get("logo", "")
                        },
                        "state": state,  # "in" = LIVE, "pre" = UPCOMING, "post" = FT
                        "clock": clock,
                        "status_detail": detail,
                        "date": ev.get("date"),
                        "venue": comp.get("venue", {}).get("fullName", "")
                    })
        except Exception as e:
            print("EPL fetch error:", e)

        # 2. F1 Next Race
        f1_next = {}
        try:
            r = await client.get("https://api.jolpi.ca/ergast/f1/current/next.json")
            if r.status_code == 200:
                races = r.json().get("MRData", {}).get("RaceTable", {}).get("Races", [])
                if races:
                    race = races[0]
                    f1_next = {
                        "race_name": race.get("raceName"),
                        "round": race.get("round"),
                        "season": race.get("season"),
                        "date": race.get("date"),
                        "time": race.get("time"),
                        "circuit": {
                            "name": race.get("Circuit", {}).get("circuitName"),
                            "locality": race.get("Circuit", {}).get("Location", {}).get("locality"),
                            "country": race.get("Circuit", {}).get("Location", {}).get("country")
                        }
                    }
        except Exception as e:
            print("F1 Next error:", e)

        # 3. F1 Standings (Top 10)
        f1_standings = []
        try:
            r = await client.get("https://api.jolpi.ca/ergast/f1/current/driverStandings.json")
            if r.status_code == 200:
                lists = r.json().get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
                if lists:
                    for d in lists[0].get("DriverStandings", [])[:10]:
                        f1_standings.append({
                            "position": d.get("position"),
                            "points": d.get("points"),
                            "wins": d.get("wins"),
                            "driver": f"{d.get('Driver', {}).get('givenName')} {d.get('Driver', {}).get('familyName')}",
                            "code": d.get("Driver", {}).get("code"),
                            "nationality": d.get("Driver", {}).get("nationality"),
                            "team": d.get("Constructors", [{}])[0].get("name", "")
                        })
        except Exception as e:
            print("F1 Standings error:", e)

        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "epl": {
                "matches": epl_matches,
                "live_count": sum(1 for m in epl_matches if m["state"] == "in"),
                "total_count": len(epl_matches)
            },
            "f1": {
                "next_race": f1_next,
                "driver_standings": f1_standings
            }
        }
        print("SUMMARY:")
        print(f"EPL: {len(epl_matches)} matches ({payload['epl']['live_count']} live)")
        print(f"F1 Next: {f1_next.get('race_name')} at {f1_next.get('circuit', {}).get('name')}")
        print(f"F1 Top Standings: {len(f1_standings)} drivers")
        return payload

if __name__ == "__main__":
    asyncio.run(fetch_live_sports())
