#!/usr/bin/env python3
"""
全平台监控高级简报 (Master Trend Report v2)
聚合 Roblox, Steam, CrazyGames, itch.io 数据
增加基于 Sitemap 的新游戏发现机制与 Google Trends (vs GPTs) 深度分析
"""

import sqlite3
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

# 确保可以导入 lib 模块
sys.path.append(str(Path(__file__).parent))

from lib.discovery import discover_crazygames_new, discover_itch_new, discover_steam_new
from lib.trends_analyzer import TrendsAnalyzer

MONITORS_DIR = Path(__file__).parent
REPORT_DIR = MONITORS_DIR / "data" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def run_collection():
    """第一步：运行所有平台的采集脚本，确保数据是最新的"""
    collect_script = MONITORS_DIR / "collect_all.py"
    if collect_script.exists():
        print("🚀 正在触发全平台数据采集...")
        subprocess.run([sys.executable, str(collect_script)], check=True)
    else:
        print("⚠️ 未找到 collect_all.py，跳过即时采集。")

def get_db_connection(platform):
    db_map = {
        "roblox": MONITORS_DIR / "roblox" / "data" / "roblox-trends.db",
        "steam": MONITORS_DIR / "steam" / "data" / "steam-trends.db",
        "crazygames": MONITORS_DIR / "crazygames" / "data" / "crazygames.db",
        "itch": MONITORS_DIR / "itch" / "data" / "itch.db"
    }
    path = db_map.get(platform)
    if path and path.exists():
        return sqlite3.connect(str(path))
    return None

def get_new_games_from_sitemaps():
    """从 Sitemap 发现新游戏并对比数据库，找出真正的“新”游戏"""
    print("🔍 正在通过 Sitemap 扫描各平台新游戏...")
    all_new = []
    
    platforms = {
        "steam": discover_steam_new,
        "crazygames": discover_crazygames_new,
        "itch": discover_itch_new
    }
    
    for platform, discover_fn in platforms.items():
        try:
            candidates = discover_fn()
            conn = get_db_connection(platform)
            if not conn: continue
            
            # 获取数据库中已有的 ID/Slug
            cursor = conn.execute("SELECT game_id FROM first_seen")
            seen = set([str(row[0]) for row in cursor.fetchall()])
            
            platform_new_count = 0
            for c in candidates:
                game_id = str(c.get('id') or c.get('slug'))
                if game_id not in seen:
                    all_new.append(c)
                    platform_new_count += 1
                    # 记录到数据库，标记为 Sitemap 发现
                    conn.execute("INSERT OR IGNORE INTO first_seen (game_id, name, first_date, category) VALUES (?, ?, ?, ?)",
                                 (game_id, c['name'], datetime.now(timezone.utc).strftime("%Y-%m-%d"), "SitemapDiscovery"))
            
            conn.commit()
            conn.close()
            print(f"✅ {platform.upper()}: 扫描完成，发现 {platform_new_count} 个新游戏")
        except Exception as e:
            print(f"❌ {platform.upper()} 扫描失败: {e}")
            
    return all_new

def analyze_roblox():
    conn = get_db_connection("roblox")
    if not conn: return "❌ 数据库未找到"
    
    try:
        timestamps = conn.execute("SELECT DISTINCT timestamp FROM snapshots ORDER BY timestamp DESC LIMIT 2").fetchall()
        if len(timestamps) < 1: return "⚠️ 数据不足"
        
        latest_ts = timestamps[0][0]
        prev_ts = timestamps[1][0] if len(timestamps) > 1 else latest_ts
        
        q = """
        SELECT name, players, 
               (SELECT players FROM snapshots s2 WHERE s2.game_id = s1.game_id AND s2.timestamp = ?) as prev_players
        FROM snapshots s1
        WHERE timestamp = ?
        ORDER BY players DESC
        LIMIT 10
        """
        rows = conn.execute(q, (prev_ts, latest_ts)).fetchall()
        conn.close()
        
        lines = []
        for name, curr, prev in rows:
            prev = prev if prev is not None else 0
            change_str = ""
            if prev > 0:
                diff = ((curr - prev) / prev) * 100
                change_str = f" ({'+' if diff > 0 else ''}{diff:.1f}%)"
            lines.append(f"- **{name}**: {curr:,} 在线{change_str}")
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ 分析错误: {e}"

def generate_trends_analysis(new_games):
    """对新发现的游戏进行 Google Trends 对比分析"""
    if not new_games:
        return "✨ 暂无新发现的游戏需要进行 Trends 分析。"
    
    analyzer = TrendsAnalyzer()
    sections = []
    
    # 为了演示和效率，只分析前 5 个最“新”的
    to_analyze = new_games[:5]
    print(f"📈 正在对 {len(to_analyze)} 个重点新游戏进行 Google Trends 分析 (Benchmark: GPTs)...")
    
    for game in to_analyze:
        name = game['name']
        res = analyzer.compare_with_benchmark(name)
        
        if res:
            badge = "⚪ 观察中"
            warning = ""
            if res['exceeded']:
                badge = "🔴 **强烈推荐 (EXPLOSIVE)**"
                warning = "\n> ⚠️ **警告**: 该游戏趋势已突破 GPTs 基准线！"
            elif res['latest_keyword'] > res['latest_benchmark'] * 0.7:
                badge = "🟠 **重点关注 (HOT)**"
            elif res['is_rising']:
                badge = "🟡 **潜力品种 (RISING)**"
            
            section = f"### [{game['platform'].upper()}] {name}\n"
            section += f"- **趋势评级**: {badge}{warning}\n"
            section += f"- **数据对比**: {name} (`{res['latest_keyword']}`) vs GPTs (`{res['latest_benchmark']}`)\n"
            section += f"- **平均热度**: {res['avg_keyword']} (基准 GPTs: {res['avg_benchmark']})\n"
            section += f"- **原始链接**: [点击访问]({game['url']})\n"
            sections.append(section)
        else:
            sections.append(f"### [{game['platform'].upper()}] {name}\n- ⚠️ Trends 数据暂不可用或搜索量过低\n- **链接**: [点击访问]({game['url']})")
            
    return "\n".join(sections)

def main():
    now = datetime.now(timezone.utc)
    ts_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    report_filename = REPORT_DIR / f"master-report-{now.strftime('%Y-%m-%d')}.md"
    
    print("="*50)
    print(f"🚀 开始全自动趋势分析工作流: {ts_str}")
    print("="*50)
    
    # 1. 运行即时采集
    run_collection()
    
    # 2. Sitemap 发现
    new_discovery = get_new_games_from_sitemaps()
    
    # 3. Trends 分析
    trends_section = generate_trends_analysis(new_discovery)
    
    # 4. 基础热度分析
    roblox_data = analyze_roblox()
    
    report_content = f"""# 🌐 Sitebuilder 全平台趋势简报
> 生成时间: {ts_str}
> 核心策略: Sitemap 发现 + Google Trends (Global, 7 Days) vs GPTs 基准

## 🚨 实时趋势预警 & 新盘发现
{trends_section}

## 🎮 Roblox 实时热度 (Top 10)
{roblox_data}

---
## 💡 建站决策建议 (基于反推逻辑)
1. **优先切入点**: 凡是标有 🔴 或 🟠 的游戏，说明其在 Google 上的搜索动量已接近或超过 GPTs。这类词具有极高的“搜索转转化”潜力。
2. **长尾布局**: 关注 Sitemap 发现的新游戏，即使 Trends 还没爆发，只要它们在 Steam 或 CrazyGames 上有位置，就说明厂商在推，适合抢占先机。
3. **内容策略**: 对于 Trends 爆发的游戏，立即执行 Step 1-3，重点分析其“工具化”可能性（如计算器、配装器）。

---
*注：报告由 Sitebuilder 监控系统自动生成，Trends 数据对比基准词为 "gpts"。*
"""

    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print("\n" + "="*50)
    print(f"✅ 报告生成成功: {report_filename}")
    print("="*50)

if __name__ == "__main__":
    main()
