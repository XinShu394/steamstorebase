"""快速查看数据概览"""
import sqlite3
import json

conn_games = sqlite3.connect('data/steam_data.db')
conn_tasks = sqlite3.connect('data/tasks.db')

print("=" * 80)
print("STEAM CRAWLER - DATA SUMMARY")
print("=" * 80)

# Games统计
cursor = conn_games.cursor()
cursor.execute("SELECT COUNT(*) FROM games")
total_games = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM games WHERE categories_json IS NOT NULL")
with_categories = cursor.fetchone()[0]

cursor.execute("SELECT MIN(updated_at), MAX(updated_at) FROM games")
oldest, newest = cursor.fetchone()

print(f"\n[GAMES DATA]")
print(f"  Total games: {total_games}")
print(f"  With Categories: {with_categories}")
print(f"  With Genres: {with_categories}")
print(f"  Oldest record: {oldest}")
print(f"  Newest record: {newest}")

# Reviews统计
cursor.execute("SELECT COUNT(*) FROM reviews")
total_reviews = cursor.fetchone()[0]
print(f"  Review data: {total_reviews}")

# Tasks统计
cursor = conn_tasks.cursor()
cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status ORDER BY status")
print(f"\n[CRAWLING PROGRESS]")
total_tasks = 0
for status, count in cursor.fetchall():
    print(f"  {status}: {count:,}")
    total_tasks += count

print(f"  TOTAL: {total_tasks:,}")

# 计算进度
success_count = conn_tasks.cursor()
success_count.execute("SELECT COUNT(*) FROM tasks WHERE status='success'")
success = success_count.fetchone()[0]
progress = (success / total_tasks * 100) if total_tasks > 0 else 0
print(f"\n[PROGRESS]")
print(f"  Completion: {progress:.2f}%")
print(f"  Remaining: {total_tasks - success:,} tasks")

# 最新5个游戏
print(f"\n[LATEST 5 GAMES]")
cursor = conn_games.cursor()
cursor.execute("""
    SELECT steam_appid, name, price_final, currency, updated_at
    FROM games
    ORDER BY updated_at DESC
    LIMIT 5
""")

for appid, name, price, currency, updated in cursor.fetchall():
    price_str = f"${price/100:.2f}" if price else "Free"
    print(f"  [{appid}] {name} - {price_str} ({updated})")

conn_games.close()
conn_tasks.close()
