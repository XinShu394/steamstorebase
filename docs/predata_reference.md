# Historical Data Reference (Predata)

The `predata/` directory contains historical data from a previous version of the crawler. 
**These files are for reference only and should NOT be imported as live data.**

## Purpose
- **Schema Reference**: Used to understand expected fields (e.g., pricing structure, date formats).
- **Gap Analysis**: Used to identify missing features in the new crawler (e.g., Tags, Reviews).
- **Seed List**: The `app_id` list from `games.csv` can be used to seed the task queue if the Steam Web API is unreachable.

## Structure
- `games/games.csv`: Basic metadata (AppID, Name, Price).
- `reviews/reviews.csv`: Review scores and counts (including SteamSpy data).
- `tags/tags.csv`: User tags.

## Policy
- **Do Not Import**: The new system must fetch fresh data from Steam APIs/Store.
- **Do Not Rely On**: The data format in `predata` (e.g., CSV) differs from our new storage format (SQLite/JSON).
