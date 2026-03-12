"""查看指定游戏的详细信息
Usage: python show_game.py <appid>
Example: python show_game.py 20900
"""
import sqlite3
import json
import sys

if len(sys.argv) < 2:
    print("Usage: python show_game.py <appid>")
    print("Example: python show_game.py 20900")
    sys.exit(1)

appid = int(sys.argv[1])

conn = sqlite3.connect('data/steam_data.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT g.*, r.review_score, r.review_score_desc, 
           r.total_positive, r.total_negative, r.total_reviews
    FROM games g
    LEFT JOIN reviews r ON g.steam_appid = r.steam_appid
    WHERE g.steam_appid = ?
""", (appid,))

row = cursor.fetchone()
if not row:
    print(f"Game not found: AppID {appid}")
    sys.exit(1)

cols = [desc[0] for desc in cursor.description]
data = dict(zip(cols, row))

print("=" * 80)
print(f"GAME DETAILS - AppID: {appid}")
print("=" * 80)

print(f"\n[BASIC INFO]")
print(f"  Name: {data['name']}")
print(f"  Type: {data['type']}")
print(f"  Free: {'Yes' if data['is_free'] else 'No'}")
print(f"  Release Date: {data['release_date']}")
print(f"  Price: ${data['price_final']/100:.2f}" if data['price_final'] else "  Price: Free")
print(f"  Currency: {data['currency'] or 'USD'}")

if data['categories_json']:
    cats = json.loads(data['categories_json'])
    print(f"\n[CATEGORIES] ({len(cats)})")
    for i, cat in enumerate(cats, 1):
        print(f"  {i}. {cat}")

if data['genres_json']:
    genres = json.loads(data['genres_json'])
    print(f"\n[GENRES]")
    print(f"  {', '.join(genres)}")

if data['tags_json']:
    tags = json.loads(data['tags_json'])
    print(f"\n[USER TAGS] (top 15)")
    print(f"  {', '.join(tags[:15])}")

if data['review_score_desc']:
    print(f"\n[REVIEWS]")
    print(f"  Score: {data['review_score']}/10 - {data['review_score_desc']}")
    print(f"  Positive: {data['total_positive']:,}")
    print(f"  Negative: {data['total_negative']:,}")
    print(f"  Total: {data['total_reviews']:,}")
    if data['total_reviews'] > 0:
        positive_rate = data['total_positive'] / data['total_reviews'] * 100
        print(f"  Positive Rate: {positive_rate:.1f}%")

print(f"\n[META]")
print(f"  Last Updated: {data['updated_at']}")
print(f"  Steam Store: https://store.steampowered.com/app/{appid}/")

conn.close()
