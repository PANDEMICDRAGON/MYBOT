import httpx
import json

def test_apis():
    # 1. ESPN Premier League Scoreboard
    try:
        r = httpx.get("https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard", timeout=10)
        print("ESPN EPL Status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            events = data.get("events", [])
            print(f"EPL Matches found: {len(events)}")
            for e in events[:4]:
                name = e.get("name")
                status = e.get("status", {}).get("type", {}).get("detail")
                clock = e.get("status", {}).get("displayClock", "")
                competitions = e.get("competitions", [{}])[0]
                competitors = competitions.get("competitors", [])
                score_str = " vs ".join([f"{c.get('team', {}).get('shortDisplayName')} ({c.get('score', '0')})" for c in competitors])
                print(f"  [EPL] {name} -> {score_str} | Status: {status} ({clock})")
    except Exception as ex:
        print("EPL error:", ex)

    # 2. Formula 1 Ergast / Jolpica next race & standings
    try:
        r = httpx.get("https://api.jolpi.ca/ergast/f1/current/next.json", timeout=10)
        print("\nJolpica F1 Next Race Status:", r.status_code)
        if r.status_code == 200:
            mrData = r.json().get("MRData", {}).get("RaceTable", {})
            races = mrData.get("Races", [])
            if races:
                race = races[0]
                print(f"  [F1 NEXT] {race.get('raceName')} at {race.get('Circuit', {}).get('circuitName')}, {race.get('Circuit', {}).get('Location', {}).get('country')}")
                print(f"     Date: {race.get('date')} {race.get('time', '')}")
    except Exception as ex:
        print("F1 Next Race error:", ex)

    # 3. Formula 1 Driver Standings
    try:
        r = httpx.get("https://api.jolpi.ca/ergast/f1/current/driverStandings.json", timeout=10)
        print("\nJolpica F1 Driver Standings Status:", r.status_code)
        if r.status_code == 200:
            standings_lists = r.json().get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
            if standings_lists:
                drivers = standings_lists[0].get("DriverStandings", [])
                print("  [F1 TOP 5 DRIVERS]:")
                for d in drivers[:5]:
                    pos = d.get("position")
                    name = f"{d.get('Driver', {}).get('givenName')} {d.get('Driver', {}).get('familyName')}"
                    pts = d.get("points")
                    team = d.get("Constructors", [{}])[0].get("name", "")
                    print(f"     P{pos}: {name} ({team}) - {pts} pts")
    except Exception as ex:
        print("F1 Standings error:", ex)

    # 4. ESPN F1 Racing Scoreboard
    try:
        r = httpx.get("https://site.api.espn.com/apis/site/v2/sports/racing/f1/scoreboard", timeout=10)
        print("\nESPN F1 Scoreboard Status:", r.status_code)
        if r.status_code == 200:
            f1_events = r.json().get("events", [])
            print(f"  ESPN F1 Events: {len(f1_events)}")
            for ev in f1_events[:2]:
                print(f"     {ev.get('name')} | Status: {ev.get('status', {}).get('type', {}).get('detail')}")
    except Exception as ex:
        print("ESPN F1 error:", ex)

if __name__ == "__main__":
    test_apis()
