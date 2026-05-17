
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from monitors.lib.trends_analyzer import TrendsAnalyzer

def main():
    analyzer = TrendsAnalyzer()
    keywords = [
        "Rob Brainrot 2",
        "Escape Wavesio",
        "Fishing Hook",
        "Space Dash",
        "Zombie Derby 2",
        "Rush Race",
        "Cobb Can Move"
    ]
    
    print(f"--- Google Trends Analysis vs 'gpts' (7 days global) ---")
    
    for kw in keywords:
        print(f"\nAnalyzing: {kw}")
        res = analyzer.compare_with_benchmark(kw)
        if res:
            if res['exceeded']:
                print(f"  🔴 RATING: EXPLOSIVE (Exceeded gpts)")
            else:
                print(f"  ⚪ RATING: LOW (Below gpts)")
            print(f"  Latest Score: {kw} ({res['latest_keyword']}) vs GPTs ({res['latest_benchmark']})")
        else:
            print("  ⚠️ Trends data unavailable.")

if __name__ == "__main__":
    main()
