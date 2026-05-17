
from monitors.lib.trends_analyzer import TrendsAnalyzer
import pandas as pd

analyzer = TrendsAnalyzer()
keyword = "SiNiSistar 2"
res = analyzer.compare_with_benchmark(keyword)
if res:
    print(f"Keyword: {res['keyword']}")
    print(f"Benchmark: {res['benchmark']}")
    print(f"Latest: {res['latest_keyword']} vs {res['latest_benchmark']}")
    print(f"Exceeded: {res['exceeded']}")
    # print data
    df = pd.DataFrame(res['data'])
    print(df.tail(10))
else:
    print("No data found for SiNiSistar 2")
