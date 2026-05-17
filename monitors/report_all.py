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
import urllib.request
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta

# 确保可以导入 lib 模块
sys.path.append(str(Path(__file__).parent))

from lib.discovery import discover_crazygames_new, discover_itch_new, discover_steam_new, discover_custom_sites
from lib.trends_analyzer import TrendsAnalyzer

# --- Roblox 元数据补全 ---

def enrich_roblox_metadata(conn):
    """补全 Roblox 游戏的真实创建时间"""
    cursor = conn.cursor()
    # 优先补全活跃人数高的游戏
    cursor.execute("""
        SELECT DISTINCT game_id 
        FROM snapshots 
        WHERE timestamp = (SELECT MAX(timestamp) FROM snapshots)
        AND game_id IN (SELECT game_id FROM first_seen WHERE created_at IS NULL)
        ORDER BY players DESC
        LIMIT 50
    """)
    rows = cursor.fetchall()
    if not rows:
        return

    print(f"🔄 正在补全 {len(rows)} 个 Roblox 热门游戏的原始元数据...")
    
    place_ids = [row[0] for row in rows]
    place_to_universe = {}
    
    for pid in place_ids:
        try:
            url = f"https://apis.roblox.com/universes/v1/places/{pid}/universe"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                uid = data.get("universeId")
                if uid:
                    place_to_universe[pid] = str(uid)
            time.sleep(0.1)
        except:
            continue
            
    if not place_to_universe:
        return
        
    universe_ids = list(set(place_to_universe.values()))
    game_info_map = {}
    
    # 批量获取 (Roblox API 限制每次 ~50-100)
    for i in range(0, len(universe_ids), 50):
        batch = universe_ids[i:i+50]
        try:
            ids_str = ",".join(map(str, batch))
            url = f"https://games.roblox.com/v1/games?universeIds={ids_str}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                for g in data.get('data', []):
                    game_info_map[str(g['id'])] = g
            time.sleep(0.2)
        except:
            continue

    for pid, uid in place_to_universe.items():
        info = game_info_map.get(uid)
        if info:
            created_at = info.get('created', '').split('T')[0]
            cursor.execute(
                "UPDATE first_seen SET universe_id = ?, created_at = ? WHERE game_id = ?",
                (uid, created_at, pid)
            )
    conn.commit()

# --- Steam 元数据补全 ---

def enrich_steam_metadata(conn):
    """补全 Steam 游戏的真实发布日期"""
    cursor = conn.cursor()
    cursor.execute("SELECT game_id FROM first_seen WHERE created_at IS NULL LIMIT 50")
    rows = cursor.fetchall()
    if not rows:
        return

    print(f"🔄 正在补全 {len(rows)} 个 Steam 游戏的原始发布日期...")
    for (app_id,) in rows:
        try:
            url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                if data and str(app_id) in data and data[str(app_id)]['success']:
                    release_info = data[str(app_id)]['data'].get('release_date', {})
                    date_str = release_info.get('date', '')
                    clean_date = None
                    
                    # 尝试解析多种日期格式
                    formats = ["%d %b, %Y", "%b %d, %Y", "%Y-%m-%d", "%d %B %Y", "%B %d %Y"]
                    for fmt in formats:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            clean_date = dt.strftime("%Y-%m-%d")
                            break
                        except ValueError: continue
                    
                    if not clean_date:
                        # 尝试更简单的正则提取 YYYY
                        year_match = re.search(r'(\d{4})', date_str)
                        if year_match: clean_date = f"{year_match.group(1)}-01-01"
                    
                    if clean_date:
                        cursor.execute("UPDATE first_seen SET created_at = ? WHERE game_id = ?", (clean_date, app_id))
            time.sleep(0.5)
        except Exception as e:
            continue
    conn.commit()

def enrich_general_metadata(conn, platform):
    """补全通用平台（CrazyGames, itch.io）的发布日期"""
    cursor = conn.cursor()
    # 增加补全数量
    cursor.execute("SELECT game_id, name FROM first_seen WHERE created_at IS NULL LIMIT 30")
    rows = cursor.fetchall()
    if not rows:
        return

    print(f"🔄 正在补全 {len(rows)} 个 {platform} 游戏的发布日期...")
    for game_id, name in rows:
        try:
            url = game_id if game_id.startswith("http") else f"https://www.{platform}.com/game/{game_id}"
            if platform == "itch": url = game_id
            
            headers = {"User-Agent": "Mozilla/5.0"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode('utf-8')
                found_date = None
                
                # 增强的正则匹配
                if platform == "crazygames":
                    date_patterns = [
                        r'"datePublished"\s*:\s*"(.*?)"',
                        r'"firstPublishedAt"\s*:\s*"(.*?)"',
                        r'"dateCreated"\s*:\s*"(.*?)"'
                    ]
                elif platform == "itch":
                    date_patterns = [
                        r'published_at&quot;:&quot;(.*?)&quot;',
                        r'"datePublished"\s*content="(.*?)"',
                        r'datetime="(.*?)"',
                        r'"published_at"\s*:\s*"(.*?)"',
                        r'Published\s*</span>\s*<abbr\s*title="(.*?)"'
                    ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                    if match:
                        found_date_raw = match.group(1).strip()
                        found_date = found_date_raw.split(' ')[0].split('T')[0]
                        
                        # 处理 "12 days ago"
                        if "ago" in found_date_raw.lower():
                            days_match = re.search(r'(\d+)\s*day', found_date_raw, re.I)
                            if days_match:
                                days = int(days_match.group(1))
                                found_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
                            elif "yesterday" in found_date_raw.lower():
                                found_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
                        
                        if re.match(r'^\d{4}-\d{2}-\d{2}', found_date):
                            print(f"  ✅ Found date for {name}: {found_date}")
                            cursor.execute("UPDATE first_seen SET created_at = ? WHERE game_id = ?", (found_date, game_id))
                            break
            time.sleep(0.3)
        except:
            continue
    conn.commit()

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
        "itch": MONITORS_DIR / "itch" / "data" / "itch.db",
        "general": MONITORS_DIR / "general" / "data" / "general.db"
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
        "itch": discover_itch_new,
        "general": discover_custom_sites
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

# 排除掉那些老牌大盘，即使数据库是刚建立的
ROBLOX_GIANT_BLACKLIST = [
    "4924922222", # Brookhaven
    "920587237",  # Adopt Me!
    "2753915549", # Blox Fruits
    "142823291",  # Murder Mystery 2
    "8737899170", # Pet Simulator 99
    "6872265039", # BedWars
    "15532962292",# Sol's RNG
    "10449761463",# The Strongest Battlegrounds
    "9391468976", # Jujutsu Shenanigans
    "17625359962",# RIVALS
    "12985361032",# Metro Life
    "18687417158",# Forsaken (Original)
    "79546208627805", # 99 Nights in the Forest
    "109983668079237", # Steal a Brainrot
    "89469502395769", # Kick a Lucky Block
    "95082159892680", # +1 Speed Keyboard Escape
]

def analyze_roblox():
    conn = get_db_connection("roblox")
    if not conn: return "❌ 数据库未找到", []
    
    try:
        # 0. 补全元数据
        enrich_roblox_metadata(conn)
        
        # 1. 获取最新时间戳和相关时间窗口
        max_ts_row = conn.execute("SELECT MAX(timestamp) FROM snapshots").fetchone()
        if not max_ts_row or not max_ts_row[0]: return "⚠️ 数据不足", []
        
        max_ts = max_ts_row[0]
        try:
            now_utc = datetime.strptime(max_ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        except ValueError:
            now_utc = datetime.strptime(max_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            
        t24 = (now_utc - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
        t72 = (now_utc - timedelta(hours=72)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 2. 趋势分析查询
        q = """
        WITH stats AS (
            SELECT 
                game_id, 
                MAX(name) as name,
                AVG(CASE WHEN timestamp >= ? THEN players ELSE NULL END) as avg_24h,
                AVG(CASE WHEN timestamp >= ? AND timestamp < ? THEN players ELSE NULL END) as avg_prev_72h
            FROM snapshots
            GROUP BY game_id
        ),
        age_info AS (
            SELECT game_id, first_date, created_at
            FROM first_seen
        )
        SELECT 
            s.game_id, s.name, s.avg_24h, s.avg_prev_72h, a.first_date, a.created_at
        FROM stats s
        LEFT JOIN age_info a ON s.game_id = a.game_id
        WHERE s.avg_24h > 200
        ORDER BY s.avg_24h DESC
        """
        
        rows = conn.execute(q, (t24, t72, t24)).fetchall()
        conn.close()
        
        rising_stars = []
        display_lines = []
        
        for gid, name, curr_avg, prev_avg, first_date, created_at in rows:
            if gid in ROBLOX_GIANT_BLACKLIST:
                continue
                
            curr_avg = curr_avg or 0
            prev_avg = prev_avg or 0
            growth = 0
            if prev_avg > 0:
                growth = ((curr_avg - prev_avg) / prev_avg) * 100
            
            # 严格的新盘判定逻辑
            is_new = False
            age = 999
            if created_at:
                fd = datetime.strptime(created_at, "%Y-%m-%d").date()
                age = (now_utc.date() - fd).days
                # 只有真实创建于 30 天内的才叫新盘
                if age <= 30:
                    is_new = True
            
            # 如果没有抓到创建时间，绝对不标注为“新盘”，仅标注“监控新发现”
            is_discovery = False
            if not created_at and first_date:
                fd = datetime.strptime(first_date, "%Y-%m-%d").date()
                if (now_utc.date() - fd).days <= 2:
                    is_discovery = True

            # 评分逻辑
            score = 0
            if is_new:
                score += 60
                if age <= 7: score += 20
            elif is_discovery:
                score += 20 # 仅作为发现分
            
            if growth > 30: score += 30
            if growth > 100: score += 40
            
            score += min(curr_avg / 2000, 10)

            # 标签
            tags = []
            if is_new: 
                tags.append(f"🆕 新盘 ({age}d)")
            elif is_discovery:
                tags.append("🔍 监控新发现")
            
            if growth > 30: 
                tags.append(f"🚀 暴涨 {growth:.0f}%")
            
            status_str = " | ".join(tags) if tags else "活跃"
            
            # 推荐门槛：必须是新盘且有一定热度，或者老盘但有极高增长
            if (is_new and curr_avg > 500) or (growth > 50 and curr_avg > 1000):
                rising_stars.append({
                    "name": name,
                    "score": score,
                    "platform": "roblox",
                    "url": f"https://www.roblox.com/games/{gid}",
                    "badge": f"⭐ {score:.0f} [{status_str}]"
                })

            if len(display_lines) < 12:
                link = f"https://www.roblox.com/games/{gid}"
                display_lines.append(f"- **[{name}]({link})**: {int(curr_avg):,} 在线 ({status_str})")

        return "\n".join(display_lines), rising_stars
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return f"⚠️ 分析错误: {e}", []

def generate_trends_analysis(new_games):
    """对新发现的游戏进行 Google Trends 对比分析"""
    if not new_games:
        return "✨ 暂无新发现的游戏需要进行 Trends 分析。", []
    
    analyzer = TrendsAnalyzer()
    sections = []
    recommendations = []
    
    # 核心逻辑：对所有新发现的游戏进行 Trends 分析
    # 按照平台分组，每组取最新的 5 个，总数控制在 20 个以内以防 429
    platform_groups = {}
    for g in new_games:
        p = g['platform']
        if p not in platform_groups: platform_groups[p] = []
        platform_groups[p].append(g)
    
    to_analyze = []
    for p in platform_groups:
        to_analyze.extend(platform_groups[p][:5])
    
    to_analyze = to_analyze[:20]
    
    print(f"📈 正在对 {len(to_analyze)} 个重点新发现进行 Google Trends 分析 (7天全球 vs gpts)...")
    
    for game in to_analyze:
        name = game['name']
        res = analyzer.compare_with_benchmark(name)
        
        if res:
            # 只有当趋势图曾高于 gpts 时才标记为强烈推荐
            if res['exceeded']:
                badge = "🔴 **强烈推荐 (EXPLOSIVE)**"
                score = 100
            elif res['latest_keyword'] > res['latest_benchmark'] * 0.7:
                badge = "🟠 **重点关注 (HOT)**"
                score = 70
            else:
                badge = "⚪ 观察中 (低于基准)"
                score = 10
            
            # 如果高于基准词，进入推荐名单
            if res['exceeded']:
                recommendations.append({
                    "name": name,
                    "score": score,
                    "platform": game['platform'],
                    "url": game['url'],
                    "badge": badge
                })

            # 展示结果
            platform_label = f"{game['platform'].upper()}"
            if 'domain' in game: platform_label += f": {game['domain']}"
            
            section = f"### [{platform_label}] {name}\n"
            section += f"- **趋势评级**: {badge}\n"
            section += f"- **数据对比**: {name} (`{res['latest_keyword']}`) vs GPTs (`{res['latest_benchmark']}`)\n"
            section += f"- **最高点突破**: {'✅ 是' if res['exceeded'] else '❌ 否'}\n"
            section += f"- **链接**: [点击访问]({game['url']})\n"
            sections.append(section)
        else:
            sections.append(f"### [{game['platform'].upper()}] {name}\n- ⚠️ Trends 数据不可用 (搜索量极低)\n- **链接**: [点击访问]({game['url']})")
    
    return "\n".join(sections), recommendations

# Steam 巨头黑名单
STEAM_GIANT_BLACKLIST = [
    "730",     # Counter-Strike 2
    "578080",  # PUBG
    "1172470", # Apex Legends
    "2344520", # Diablo IV
    "1665460", # eFootball
    "2483190", # Forza Horizon 6 (用户提到的老游戏/大IP)
    "1962700", # Subnautica 2
]

def analyze_steam():
    """分析 Steam 数据库中的最新趋势"""
    try:
        conn = get_db_connection("steam")
        if not conn: return "⚠️ Steam 数据库连接失败"
        
        # 补全元数据
        enrich_steam_metadata(conn)
        
        # 获取最新的快照时间
        latest_ts = conn.execute("SELECT MAX(timestamp) FROM snapshots").fetchone()[0]
        
        # 仅获取最近 7 天内新发现的游戏
        q = """
        SELECT s.game_id, s.name, f.created_at
        FROM snapshots s
        JOIN first_seen f ON s.game_id = f.game_id
        WHERE s.timestamp = ? 
        AND f.created_at >= date('now', '-7 days')
        ORDER BY f.created_at DESC, s.name ASC
        LIMIT 15
        """
        rows = conn.execute(q, (latest_ts,)).fetchall()
        conn.close()
        
        if not rows:
            return "✨ 暂无 7 天内上线的新游数据。"
            
        lines = []
        now = datetime.now(timezone.utc).date()
        
        for gid, name, created_at in rows:
            dt = datetime.strptime(created_at, "%Y-%m-%d").date()
            age = (now - dt).days
            link = f"https://store.steampowered.com/app/{gid}"
            lines.append(f"- **[{name}]({link})** (🆕 {age}d) [NEW]")
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ 分析错误: {e}"

def analyze_crazygames():
    conn = get_db_connection("crazygames")
    if not conn: return "❌ 数据库未找到"
    
    try:
        # 补全元数据
        enrich_general_metadata(conn, "crazygames")
        
        latest_ts = conn.execute("SELECT MAX(timestamp) FROM snapshots").fetchone()[0]
        # 获取最近 7 天内监控新发现或新上线的游戏
        q = """
        SELECT s.name, s.slug, s.category, f.created_at, f.first_date
        FROM snapshots s
        JOIN first_seen f ON s.game_id = f.game_id
        WHERE s.timestamp = ?
        AND (
            (f.created_at IS NOT NULL AND f.created_at >= date('now', '-7 days'))
            OR (f.first_date IS NOT NULL AND f.first_date >= date('now', '-7 days'))
        )
        ORDER BY COALESCE(f.created_at, f.first_date) DESC, s.name ASC
        LIMIT 15
        """
        rows = conn.execute(q, (latest_ts,)).fetchall()
        conn.close()
        
        if not rows:
            return "✨ 暂无 7 天内上线的新游数据。"
            
        lines = []
        now = datetime.now(timezone.utc).date()
        
        for name, slug, cat, created_at, first_date in rows:
            # 优先使用 release_date (created_at)，如果没有则使用发现日期
            date_str = created_at or first_date
            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            age = (now - dt).days
            link = f"https://www.crazygames.com/game/{slug}"
            label = "NEW" if created_at else "DISCOVERED"
            lines.append(f"- **[{name}]({link})** *[{cat}]* (🆕 {age}d) [{label}]")
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ 分析错误: {e}"

def analyze_itch():
    conn = get_db_connection("itch")
    if not conn: return "❌ 数据库未找到"
    
    try:
        # 补全元数据
        enrich_general_metadata(conn, "itch")
        
        latest_ts = conn.execute("SELECT MAX(timestamp) FROM snapshots").fetchone()[0]
        # 获取最近 7 天内监控新发现或新上线的游戏
        q = """
        SELECT s.name, s.link, s.author, f.created_at, f.first_date
        FROM snapshots s
        JOIN first_seen f ON s.game_id = f.game_id
        WHERE s.timestamp = ?
        AND (
            (f.created_at IS NOT NULL AND f.created_at >= date('now', '-7 days'))
            OR (f.first_date IS NOT NULL AND f.first_date >= date('now', '-7 days'))
        )
        ORDER BY COALESCE(f.created_at, f.first_date) DESC, s.name ASC
        LIMIT 15
        """
        rows = conn.execute(q, (latest_ts,)).fetchall()
        conn.close()
        
        if not rows:
            return "✨ 暂无 7 天内上线的新游数据。"
            
        lines = []
        now = datetime.now(timezone.utc).date()
        
        for name, link, author, created_at, first_date in rows:
            date_str = created_at or first_date
            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            age = (now - dt).days
            label = "NEW" if created_at else "DISCOVERED"
            lines.append(f"- **[{name}]({link})** *by {author}* (🆕 {age}d) [{label}]")
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ 分析错误: {e}"

def main():
    now = datetime.now(timezone.utc)
    ts_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    report_filename = REPORT_DIR / f"master-report-{now.strftime('%Y-%m-%d')}.md"
    
    print("="*50)
    print(f"🚀 开始全自动趋势分析工作流: {ts_str}")
    print("="*50)
    
    # 1. 运行即时采集
    run_collection()
    
    # 2. 收集待分析的候选游戏 (Sitemap 发现 + 平台新盘)
    candidates = []
    
    # 2.1 Sitemap 发现
    new_discovery = get_new_games_from_sitemaps()
    candidates.extend(new_discovery)
    
    # 2.2 Roblox 潜力新盘
    roblox_data, roblox_stars = analyze_roblox()
    for star in roblox_stars:
        candidates.append({
            "name": star['name'],
            "url": star['url'],
            "platform": star['platform']
        })
        
    # 2.3 Steam 潜力新盘
    steam_conn = get_db_connection("steam")
    if steam_conn:
        now_date = datetime.now(timezone.utc).date()
        # 按发现时间降序排列，优先分析最新的
        q = "SELECT name, game_id, created_at FROM first_seen WHERE created_at IS NOT NULL ORDER BY created_at DESC"
        for name, gid, created_at in steam_conn.execute(q).fetchall():
            try:
                dt = datetime.strptime(created_at, "%Y-%m-%d").date()
                age = (now_date - dt).days
                # 严格限制：只监控上线 7 天内的 Steam 游戏
                if age <= 7:
                    candidates.append({
                        "name": name,
                        "url": f"https://store.steampowered.com/app/{gid}",
                        "platform": "steam",
                        "age": age
                    })
            except: pass
        steam_conn.close()

    # 2.4 CrazyGames & itch.io 潜力新盘
    for platform in ["crazygames", "itch"]:
        conn = get_db_connection(platform)
        if conn:
            now_date = datetime.now(timezone.utc).date()
            q = """
            SELECT name, game_id, created_at, first_date 
            FROM first_seen 
            WHERE (created_at IS NOT NULL AND created_at >= date('now', '-7 days'))
            OR (first_date IS NOT NULL AND first_date >= date('now', '-7 days'))
            ORDER BY COALESCE(created_at, first_date) DESC
            """
            for name, gid, created_at, first_date in conn.execute(q).fetchall():
                try:
                    date_str = created_at or first_date
                    dt = datetime.strptime(date_str, "%Y-%m-%d").date()
                    age = (now_date - dt).days
                    url = gid if gid.startswith("http") else (f"https://www.crazygames.com/game/{gid}" if platform == "crazygames" else gid)
                    candidates.append({
                        "name": name,
                        "url": url,
                        "platform": platform,
                        "age": age
                    })
                except: pass
            conn.close()

    # 去重候选名单 (根据 URL)
    seen_urls = set()
    unique_candidates = []
    for c in candidates:
        if c['url'] not in seen_urls:
            unique_candidates.append(c)
            seen_urls.add(c['url'])

    # 按“新鲜度”排序，优先分析刚上线 1-3 天的游戏
    unique_candidates.sort(key=lambda x: x.get('age', 99))

    # 3. 执行统一的 Trends 分析
    trends_section, recommendations = generate_trends_analysis(unique_candidates)
    
    # 4. 生成报告数据
    steam_data = analyze_steam()
    crazy_data = analyze_crazygames()
    itch_data = analyze_itch()
    
    # 5. 综合潜力建站推荐 (仅展示超过 GPTs 的爆款)
    potential_summary = "✨ 暂无搜索热度超过 GPTs 的爆款新盘。"
    if recommendations:
        # 按分数降序排列
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        rec_lines = []
        for i, rec in enumerate(recommendations[:6]):
            rec_lines.append(f"{i+1}. **{rec['name']}** ({rec['platform'].upper()}) - {rec['badge']} [立即研究]({rec['url']})")
        potential_summary = "\n".join(rec_lines)

    report_content = f"""# 🌐 Sitebuilder 全平台趋势简报
> 生成时间: {ts_str}

## 🎯 今日潜力建站推荐 (Top 5)
> 优先筛选：搜索热度在过去 7 天内曾超过基准词 "gpts" 的新盘。

{potential_summary}

---

## 🚨 实时趋势预警 & 新盘发现
{trends_section}

## 🎮 Roblox 实时热度 & 趋势
{roblox_data}

## 🚂 Steam 市场动态 (Top Sellers)
{steam_data}

## ⚡ CrazyGames 网页端新盘
{crazy_data}

## 🎨 itch.io 独立游戏动态
{itch_data}

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
