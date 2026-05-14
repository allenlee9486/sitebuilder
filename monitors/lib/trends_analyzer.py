import time
import random
import pandas as pd
from pytrends.request import TrendReq

class TrendsAnalyzer:
    def __init__(self):
        # hl: language, tz: timezone offset
        # Use a list of proxies or rotate if needed, but for now let's use a standard setup
        self.pytrends = TrendReq(hl='en-US', tz=0, timeout=(10,25), retries=2, backoff_factor=0.5)
        self.benchmark = "gpts"

    def compare_with_benchmark(self, keyword, retries=3):
        """
        Compares a keyword with the benchmark 'gpts' over the last 7 days globally.
        Returns a dict with analysis or None if failed.
        """
        kw_list = [self.benchmark, keyword]
        
        for attempt in range(retries):
            try:
                # Build payload: timeframe='now 7-d' for last 7 days, geo='' for global
                self.pytrends.build_payload(kw_list, cat=0, timeframe='now 7-d', geo='', gprop='')
                
                # Interest over time
                df = self.pytrends.interest_over_time()
                
                if df.empty:
                    return None
                
                # Remove the 'isPartial' column if it exists
                if 'isPartial' in df.columns:
                    df = df.drop(columns=['isPartial'])
                
                # Analysis
                latest_values = df.iloc[-1]
                benchmark_val = latest_values[self.benchmark]
                keyword_val = latest_values[keyword]
                
                # Check for sudden spike: did it exceed benchmark in the last 24 hours?
                recent_df = df.tail(24) 
                exceeded = any(recent_df[keyword] > recent_df[self.benchmark])
                
                # Average volume
                avg_benchmark = df[self.benchmark].mean()
                avg_keyword = df[keyword].mean()
                
                return {
                    "keyword": keyword,
                    "benchmark": self.benchmark,
                    "latest_keyword": int(keyword_val),
                    "latest_benchmark": int(benchmark_val),
                    "avg_keyword": round(float(avg_keyword), 2),
                    "avg_benchmark": round(float(avg_benchmark), 2),
                    "exceeded": exceeded,
                    "is_rising": keyword_val > (avg_keyword * 1.5), 
                    "data": df.to_dict()
                }
                
            except Exception as e:
                print(f"Attempt {attempt+1} failed for {keyword}: {e}")
                if "429" in str(e):
                    # Back off more aggressively on 429
                    sleep_time = (attempt + 1) * random.uniform(10, 20)
                    print(f"Sleeping for {sleep_time:.1f}s due to 429...")
                    time.sleep(sleep_time)
                else:
                    time.sleep(random.uniform(2, 5))
                    
        return None

if __name__ == "__main__":
    # Test
    analyzer = TrendsAnalyzer()
    res = analyzer.compare_with_benchmark("Sol Cesto")
    print(res)
