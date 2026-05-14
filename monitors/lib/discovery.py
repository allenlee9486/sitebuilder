import re
from .sitemap_parser import fetch_sitemap, parse_sitemap

def discover_crazygames_new():
    """Finds new game URLs from CrazyGames sitemap."""
    index_url = "https://www.crazygames.com/sitemap-index.xml"
    index_content = fetch_sitemap(index_url)
    index_items = parse_sitemap(index_content)
    
    # Look for the 'en' sitemap
    en_sitemap_url = None
    for item in index_items:
        if "/en/sitemap" in item['loc']:
            en_sitemap_url = item['loc']
            break
            
    if not en_sitemap_url:
        return []
        
    en_content = fetch_sitemap(en_sitemap_url)
    en_items = parse_sitemap(en_content)
    
    # Games are usually https://www.crazygames.com/game/slug
    game_urls = []
    # Only process the last 100 entries to focus on newest
    for item in en_items[-100:]:
        loc = item['loc']
        if "/game/" in loc:
            slug = loc.split("/game/")[-1]
            game_urls.append({"name": slug, "slug": slug, "url": loc, "platform": "crazygames"})
            
    return game_urls

def discover_itch_new():
    """Finds new game URLs from itch.io sitemap."""
    url = "https://itch.io/sitemap.xml"
    content = fetch_sitemap(url)
    items = parse_sitemap(content)
    
    game_urls = []
    # Process last 100 entries
    for item in items[-100:]:
        loc = item['loc']
        # Games are usually https://username.itch.io/game-slug
        if ".itch.io/" in loc and loc.count("/") == 3:
            slug = loc.split("/")[-1]
            game_urls.append({"name": slug, "slug": slug, "url": loc, "platform": "itch"})
            
    return game_urls

def discover_steam_new():
    """Finds new game URLs from Steam sitemap."""
    index_url = "https://store.steampowered.com/sitemap/sitemap_index.xml"
    index_content = fetch_sitemap(index_url)
    index_items = parse_sitemap(index_content)
    
    # Look for the last apps sitemap (usually contains newer apps)
    apps_sitemaps = [item['loc'] for item in index_items if "sitemap_apps" in item['loc']]
    
    if not apps_sitemaps:
        return []
        
    apps_sitemap_url = apps_sitemaps[-1]
    apps_content = fetch_sitemap(apps_sitemap_url)
    apps_items = parse_sitemap(apps_content)
    
    game_urls = []
    # Process last 100 entries
    for item in apps_items[-100:]:
        loc = item['loc']
        match = re.search(r"/app/(\d+)/([^/]+)", loc)
        if match:
            app_id = match.group(1)
            name = match.group(2).replace("_", " ")
            game_urls.append({"name": name, "id": app_id, "url": loc, "platform": "steam"})
            
    return game_urls
