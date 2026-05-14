#!/usr/bin/env python3
"""
全平台监控高级简报 (Master Trend Report)
聚合 Roblox, Steam, CrazyGames 数据，识别跨平台趋势和高潜力机会。
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

MONITORS_DIR = Path(__file__).parent
REPORT_DIR = MONITORS_DIR / "data" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def format_delta(current, previous):
    if previous == 0: return "New!"
    delta = current - previous
    pct = (delta / previous) * 100
    return f"{'+' if delta > 0 else ''}{pct:.1f}%"

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

def analyze_roblox():
    conn = get_db_connection("roblox")
    if not conn: return "❌ 数据库未找到"
    
    # 找到最近两个时间点的快照进行对比
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
            change = format_delta(curr, prev)
            lines.append(f"- **{name}**: {curr:,} 在线 ({change})")
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ 分析错误: {e}"

def analyze_steam():
    conn = get_db_connection("steam")
    if not conn: return "❌ 数据库未找到"
    
    try:
        # 识别新进入 Top Sellers 的游戏
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        new_games = conn.execute("SELECT name FROM first_seen WHERE first_date = ? LIMIT 10", (today,)).fetchall()
        
        # 获取当前 Top 10
        latest_ts = conn.execute("SELECT MAX(timestamp) FROM snapshots").fetchone()[0]
        top_10 = conn.execute("SELECT name FROM snapshots WHERE timestamp = ? LIMIT 10", (latest_ts,)).fetchall()
        conn.close()
        
        section = "#### 🔥 当前 Top 10 (Sellers)\n"
        section += "\n".join([f"{i+1}. {r[0]}" for i, r in enumerate(top_10)])
        
        if new_games:
            section += "\n\n#### ✨ 今日新上榜\n"
            section += "\n".join([f"- {r[0]}" for r in new_games])
        return section
    except Exception as e:
        return f"⚠️ 分析错误: {e}"

def analyze_crazygames():
    conn = get_db_connection("crazygames")
    if not conn: return "❌ 数据库未找到"
    
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        new_games = conn.execute("SELECT name, category FROM first_seen WHERE first_date = ? LIMIT 10", (today,)).fetchall()
        
        latest_ts = conn.execute("SELECT MAX(timestamp) FROM snapshots").fetchone()[0]
        latest_games = conn.execute("SELECT name, category FROM snapshots WHERE timestamp = ? LIMIT 10", (latest_ts,)).fetchall()
        conn.close()
        
        section = "#### 🆕 最新上线\n"
        if new_games:
            section += "\n".join([f"- {r[0]} *[{r[1]}]*" for r in new_games])
        else:
            section += "\n".join([f"- {r[0]} *[{r[1]}]*" for r in latest_games])
        return section
    except Exception as e:
        return f"⚠️ 分析错误: {e}"

def analyze_itch():
    conn = get_db_connection("itch")
    if not conn: return "❌ 数据库未找到"
    
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        new_games = conn.execute("SELECT name, author FROM first_seen WHERE first_date = ? LIMIT 10", (today,)).fetchall()
        
        latest_ts = conn.execute("SELECT MAX(timestamp) FROM snapshots").fetchone()[0]
        latest_games = conn.execute("SELECT name, author FROM snapshots WHERE timestamp = ? LIMIT 10", (latest_ts,)).fetchall()
        conn.close()
        
        section = "#### 🌟 热门推荐\n"
        if new_games:
            section += "\n".join([f"- {r[0]} *by {r[1]}*" for r in new_games])
        else:
            section += "\n".join([f"- {r[0]} *by {r[1]}*" for r in latest_games])
        return section
    except Exception as e:
        return f"⚠️ 分析错误: {e}"

def main():
    now = datetime.now(timezone.utc)
    ts_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    report_filename = REPORT_DIR / f"master-report-{now.strftime('%Y-%m-%d')}.md"
    
    roblox_data = analyze_roblox()
    steam_data = analyze_steam()
    crazy_data = analyze_crazygames()
    itch_data = analyze_itch()
    
    report_content = f"""# 🌐 Sitebuilder 全平台趋势简报
> 生成时间: {ts_str}

## 🎮 Roblox 实时热度 (Online Players)
{roblox_data}

## 🚂 Steam 市场动态 (Top Sellers)
{steam_data}

## ⚡ CrazyGames 网页端新盘
{crazy_data}

## 🎨 itch.io 独立游戏动态
{itch_data}

---
## 💡 建站决策建议
1. **跨平台验证**: 检查 Steam 热门游戏是否有对应的 Roblox 模组或 CrazyGames 版本，这类游戏自带流量。
2. **新盘抢占**: 关注 CrazyGames "最新上线" 中分类为 *Action* 或 *Clicker* 的游戏，这类游戏最容易通过工具页（如计算器）切入。
3. **独立游戏潜力**: itch.io 的热门游戏往往是未来大火游戏的雏形，适合提前布局 SEO 关键词。
4. **数据驱动**: 优先选择 Roblox 中增长率（括号内百分比）为正且在线人数 > 5000 的游戏进行 Step 1 研究。
"""

    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print("="*50)
    print(f"✅ 全平台高级简报已生成!")
    print(f"文件位置: {report_filename}")
    print("="*50)
    print("\n[Roblox 摘要]")
    print(roblox_data.split('\n')[0] if '\n' in roblox_data else roblox_data)
    print("\n[Steam 摘要]")
    print(steam_data.split('\n')[1] if len(steam_data.split('\n')) > 1 else "查看完整报告")
    print("="*50)

if __name__ == "__main__":
    main()
