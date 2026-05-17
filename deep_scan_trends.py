
import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.append(str(Path(__file__).parent))
from monitors.lib.trends_analyzer import TrendsAnalyzer

def get_recent_candidates():
    # 聚合全平台最近 15 天新发现的游戏
    candidates = []
    dbs = [
        ('monitors/general/data/general.db', 'general'),
        ('monitors/crazygames/data/crazygames.db', 'crazygames'),
        ('monitors/itch/data/itch.db', 'itch'),
        ('monitors/steam/data/steam.db', 'steam')
    ]
    
    for db_path, platform in dbs:
        if not os.path.exists(db_path): continue
        conn = sqlite3.connect(db_path)
        # 获取 15 天内发现的
        q = "SELECT name, game_id FROM first_seen WHERE first_date >= date('now', '-15 days') OR created_at >= date('now', '-15 days') ORDER BY COALESCE(created_at, first_date) DESC LIMIT 20"
        for row in conn.execute(q).fetchall():
            name = row[0]
            # 过滤掉一些明显的非关键词词汇
            if any(x in name.lower() for x in ['privacy', 'about us', 'contact', 'terms']): continue
            candidates.append({"name": name, "platform": platform})
        conn.close()
    return candidates

def main():
    analyzer = TrendsAnalyzer()
    candidates = get_recent_candidates()
    
    print(f"--- Deep Scan: Checking {len(candidates)} recent candidates vs 'gpts' ---")
    
    winning_candidates = []
    
    for c in candidates:
        name = c['name']
        # 清理名称中的 [domain] 标签
        clean_name = name.split("]")[-1].strip() if "]" in name else name
        
        print(f"Testing: {clean_name}...", end="", flush=True)
        res = analyzer.compare_with_benchmark(clean_name)
        
        if res:
            # 严格判定：最新值必须接近或超过 gpts，且平均值不能太低
            if res['exceeded']:
                status = "🔴 WINNER"
                winning_candidates.append({
                    "name": clean_name,
                    "platform": c['platform'],
                    "latest": res['latest_keyword'],
                    "benchmark": res['latest_benchmark'],
                    "avg": res['avg_keyword']
                })
            else:
                status = "⚪ Below"
            print(f" {status} ({res['latest_keyword']} vs {res['latest_benchmark']})")
        else:
            print(" ⚠️ No Data")

    print("\n" + "="*30)
    print("🏆 FINAL SELECTION (Current Explosive Trends)")
    print("="*30)
    if not winning_candidates:
        print("No candidates currently exceed 'gpts'. Monitoring continues...")
    else:
        for w in winning_candidates:
            print(f"- {w['name']} ({w['platform'].upper()})")
            print(f"  Latest: {w['latest']} | GPTs: {w['benchmark']} | Avg: {w['avg']}")

if __name__ == "__main__":
    main()
