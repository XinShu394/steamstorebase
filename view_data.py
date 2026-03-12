"""
数据库查看工具 - 方便查看爬取的数据
"""
import sqlite3
import json
from datetime import datetime

class DataViewer:
    def __init__(self):
        self.conn_games = sqlite3.connect('data/steam_data.db')
        self.conn_tasks = sqlite3.connect('data/tasks.db')
    
    def show_summary(self):
        """显示数据概览"""
        print("=" * 80)
        print("STEAM CRAWLER - 数据概览")
        print("=" * 80)
        
        # Games统计
        cursor = self.conn_games.cursor()
        cursor.execute("SELECT COUNT(*) FROM games")
        total_games = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM games WHERE categories_json IS NOT NULL")
        with_categories = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(updated_at), MAX(updated_at) FROM games")
        oldest, newest = cursor.fetchone()
        
        print(f"\n【游戏数据】")
        print(f"  总游戏数: {total_games}")
        print(f"  包含Categories: {with_categories}")
        print(f"  最早记录: {oldest}")
        print(f"  最新记录: {newest}")
        
        # Reviews统计
        cursor.execute("SELECT COUNT(*) FROM reviews")
        total_reviews = cursor.fetchone()[0]
        print(f"  评论数据: {total_reviews}")
        
        # Tasks统计
        cursor = self.conn_tasks.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status ORDER BY status")
        print(f"\n【爬取进度】")
        for status, count in cursor.fetchall():
            print(f"  {status}: {count:,}")
    
    def show_latest_games(self, limit=10):
        """显示最新爬取的游戏"""
        print(f"\n{'=' * 80}")
        print(f"最新爬取的 {limit} 个游戏")
        print("=" * 80)
        
        cursor = self.conn_games.cursor()
        cursor.execute(f"""
            SELECT g.steam_appid, g.name, g.type, g.price_final, g.currency,
                   g.categories_json, g.genres_json, g.tags_json, g.updated_at,
                   r.review_score_desc, r.total_reviews
            FROM games g
            LEFT JOIN reviews r ON g.steam_appid = r.steam_appid
            ORDER BY g.updated_at DESC
            LIMIT {limit}
        """)
        
        for row in cursor.fetchall():
            appid, name, gtype, price, currency, cats, genres, tags, updated, review_desc, total_reviews = row
            
            print(f"\n[{appid}] {name}")
            print(f"  类型: {gtype}")
            print(f"  价格: {price/100 if price else 0} {currency or 'USD'}")
            print(f"  更新时间: {updated}")
            
            if cats:
                cats_list = json.loads(cats)
                print(f"  分类 ({len(cats_list)}): {', '.join(cats_list[:5])}")
            
            if genres:
                genres_list = json.loads(genres)
                print(f"  类型: {', '.join(genres_list)}")
            
            if tags:
                tags_list = json.loads(tags)
                print(f"  标签: {', '.join(tags_list[:8])}")
            
            if review_desc:
                print(f"  评价: {review_desc} ({total_reviews:,} 评论)")
    
    def search_game(self, keyword):
        """搜索游戏"""
        print(f"\n{'=' * 80}")
        print(f"搜索: '{keyword}'")
        print("=" * 80)
        
        cursor = self.conn_games.cursor()
        cursor.execute("""
            SELECT steam_appid, name, type, price_final, currency
            FROM games
            WHERE name LIKE ?
            ORDER BY name
            LIMIT 20
        """, (f"%{keyword}%",))
        
        results = cursor.fetchall()
        if not results:
            print("  未找到匹配的游戏")
            return
        
        print(f"\n找到 {len(results)} 个结果:\n")
        for appid, name, gtype, price, currency in results:
            price_str = f"{price/100 if price else 0} {currency or 'USD'}"
            print(f"  [{appid}] {name} ({gtype}) - {price_str}")
    
    def show_game_detail(self, appid):
        """显示游戏详细信息"""
        print(f"\n{'=' * 80}")
        print(f"游戏详情 - AppID: {appid}")
        print("=" * 80)
        
        cursor = self.conn_games.cursor()
        cursor.execute("""
            SELECT g.*, r.review_score, r.review_score_desc, 
                   r.total_positive, r.total_negative, r.total_reviews
            FROM games g
            LEFT JOIN reviews r ON g.steam_appid = r.steam_appid
            WHERE g.steam_appid = ?
        """, (appid,))
        
        row = cursor.fetchone()
        if not row:
            print(f"  未找到 AppID {appid}")
            return
        
        # 解析数据
        cols = [desc[0] for desc in cursor.description]
        data = dict(zip(cols, row))
        
        print(f"\n基础信息:")
        print(f"  AppID: {data['steam_appid']}")
        print(f"  名称: {data['name']}")
        print(f"  类型: {data['type']}")
        print(f"  免费: {'是' if data['is_free'] else '否'}")
        print(f"  发售日期: {data['release_date']}")
        print(f"  价格: {data['price_final']/100 if data['price_final'] else 0} {data['currency'] or 'USD'}")
        
        if data['categories_json']:
            cats = json.loads(data['categories_json'])
            print(f"\n分类 ({len(cats)}):")
            for i, cat in enumerate(cats, 1):
                print(f"  {i}. {cat}")
        
        if data['genres_json']:
            genres = json.loads(data['genres_json'])
            print(f"\n官方类型:")
            print(f"  {', '.join(genres)}")
        
        if data['tags_json']:
            tags = json.loads(data['tags_json'])
            print(f"\n用户标签 (前10个):")
            print(f"  {', '.join(tags[:10])}")
        
        if data['review_score_desc']:
            print(f"\n评论统计:")
            print(f"  评分: {data['review_score']}/10 - {data['review_score_desc']}")
            print(f"  好评: {data['total_positive']:,}")
            print(f"  差评: {data['total_negative']:,}")
            print(f"  总计: {data['total_reviews']:,}")
            if data['total_reviews'] > 0:
                positive_rate = data['total_positive'] / data['total_reviews'] * 100
                print(f"  好评率: {positive_rate:.1f}%")
        
        print(f"\n数据更新: {data['updated_at']}")
    
    def export_to_json(self, output_file='export_games.json', limit=100):
        """导出数据到JSON文件"""
        cursor = self.conn_games.cursor()
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
        
        cols = [desc[0] for desc in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            data = dict(zip(cols, row))
            # 解析JSON字段
            if data['categories_json']:
                data['categories'] = json.loads(data['categories_json'])
                del data['categories_json']
            if data['genres_json']:
                data['genres'] = json.loads(data['genres_json'])
                del data['genres_json']
            if data['tags_json']:
                data['tags'] = json.loads(data['tags_json'])
                del data['tags_json']
            results.append(data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n已导出 {len(results)} 个游戏到 {output_file}")
    
    def close(self):
        self.conn_games.close()
        self.conn_tasks.close()

def main():
    viewer = DataViewer()
    
    while True:
        print("\n" + "=" * 80)
        print("数据查看菜单")
        print("=" * 80)
        print("1. 数据概览")
        print("2. 查看最新游戏 (10个)")
        print("3. 查看更多游戏 (50个)")
        print("4. 搜索游戏")
        print("5. 查看游戏详情")
        print("6. 导出数据到JSON")
        print("0. 退出")
        print("-" * 80)
        
        choice = input("请选择 (0-6): ").strip()
        
        if choice == '1':
            viewer.show_summary()
        elif choice == '2':
            viewer.show_latest_games(10)
        elif choice == '3':
            viewer.show_latest_games(50)
        elif choice == '4':
            keyword = input("输入游戏名称关键词: ").strip()
            if keyword:
                viewer.search_game(keyword)
        elif choice == '5':
            appid = input("输入游戏AppID: ").strip()
            if appid.isdigit():
                viewer.show_game_detail(int(appid))
        elif choice == '6':
            limit = input("导出数量 (默认100): ").strip()
            limit = int(limit) if limit.isdigit() else 100
            viewer.export_to_json(limit=limit)
        elif choice == '0':
            print("\n再见！")
            break
        else:
            print("\n无效选择，请重试")
    
    viewer.close()

if __name__ == "__main__":
    main()
