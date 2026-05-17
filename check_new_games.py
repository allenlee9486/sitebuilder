
import sqlite3
import os
from datetime import datetime, timedelta

def query_db(db_path, platform_name):
    if not os.path.exists(db_path):
        return []
    
    results = []
    try:
        conn = sqlite3.connect(db_path)
        # 获取 7 天内的记录
        q = "SELECT name, game_id, first_date FROM first_seen WHERE first_date >= date('now', '-7 days') ORDER BY first_date DESC"
        cursor = conn.execute(q)
        for row in cursor.fetchall():
            results.append({
                "name": row[0],
                "url": row[1],
                "date": row[2],
                "platform": platform_name
            })
        conn.close()
    except Exception as e:
        print(f"Error querying {db_path}: {e}")
    return results

def main():
    all_new = []
    # 这里的路径根据之前的上下文推测
    dbs = [
        ('monitors/general/data/general.db', 'General'),
        ('monitors/crazygames/data/crazygames.db', 'CrazyGames'),
        ('monitors/itch/data/itch.db', 'Itch.io')
    ]
    
    for db_path, name in dbs:
        all_new.extend(query_db(db_path, name))
    
    if not all_new:
        print("No new games found in the last 7 days across all monitored sites.")
        return

    print(f"--- Found {len(all_new)} new games in the last 7 days ---")
    for game in all_new[:50]: # 只展示前 50 条
        print(f"[{game['platform']}] {game['name']} | {game['date']} | {game['url']}")

if __name__ == "__main__":
    main()
