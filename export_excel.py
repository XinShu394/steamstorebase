"""导出数据到Excel/CSV格式（更易查看）
Usage: python export_excel.py [limit]
Example: python export_excel.py 100
"""
import sqlite3
import json
import csv
import sys

limit = int(sys.argv[1]) if len(sys.argv) > 1 else 100

conn = sqlite3.connect('data/steam_data.db')
cursor = conn.cursor()

cursor.execute(f"""
    SELECT g.steam_appid, g.name, g.type, g.is_free, g.release_date,
           g.price_final, g.currency, g.categories_json, g.genres_json, 
           g.tags_json, g.updated_at,
           r.review_score, r.review_score_desc, r.total_positive, 
           r.total_negative, r.total_reviews
    FROM games g
    LEFT JOIN reviews r ON g.steam_appid = r.steam_appid
    ORDER BY g.updated_at DESC
    LIMIT {limit}
""")

rows = cursor.fetchall()

# 导出CSV
output_csv = f'export_games_{limit}.csv'
with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    
    # 表头
    writer.writerow([
        'AppID', 'Name', 'Type', 'Free', 'Release Date', 
        'Price (USD)', 'Categories', 'Genres', 'Tags (Top 5)',
        'Review Score', 'Review Desc', 'Positive', 'Negative', 'Total Reviews',
        'Updated At'
    ])
    
    # 数据
    for row in rows:
        appid, name, gtype, is_free, release_date, price, currency, cats, genres, tags, updated, \
        review_score, review_desc, positive, negative, total_reviews = row
        
        # 解析JSON
        cats_str = ', '.join(json.loads(cats)[:5]) if cats else ''
        genres_str = ', '.join(json.loads(genres)) if genres else ''
        tags_str = ', '.join(json.loads(tags)[:5]) if tags else ''
        
        price_usd = f"${price/100:.2f}" if price else "Free"
        
        writer.writerow([
            appid, name, gtype, 'Yes' if is_free else 'No', release_date,
            price_usd, cats_str, genres_str, tags_str,
            review_score or '', review_desc or '', positive or '', negative or '', total_reviews or '',
            updated
        ])

# 导出JSON
output_json = f'export_games_{limit}.json'
results = []
for row in rows:
    appid, name, gtype, is_free, release_date, price, currency, cats, genres, tags, updated, \
    review_score, review_desc, positive, negative, total_reviews = row
    
    game_data = {
        'appid': appid,
        'name': name,
        'type': gtype,
        'is_free': bool(is_free),
        'release_date': release_date,
        'price': price,
        'currency': currency,
        'categories': json.loads(cats) if cats else [],
        'genres': json.loads(genres) if genres else [],
        'tags': json.loads(tags) if tags else [],
        'review_score': review_score,
        'review_desc': review_desc,
        'total_positive': positive,
        'total_negative': negative,
        'total_reviews': total_reviews,
        'updated_at': updated
    }
    results.append(game_data)

with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Exported {len(rows)} games:")
print(f"  - CSV: {output_csv} (Easy to open in Excel)")
print(f"  - JSON: {output_json} (Structured data)")

conn.close()
