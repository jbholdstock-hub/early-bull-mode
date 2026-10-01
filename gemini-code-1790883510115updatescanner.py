import yfinance as yf
import pandas as pd
import json
from datetime import datetime, timedelta

SECTOR_ETFS = {
    'XLK': 'Technology',
    'XLC': 'Communication Services',
    'XLY': 'Consumer Discretionary',
    'XLF': 'Financials',
    'XLI': 'Industrials',
    'XLE': 'Energy',
    'XLV': 'Healthcare',
    'XLP': 'Consumer Staples',
    'XLB': 'Materials',
    'XLRE': 'Real Estate',
    'XLU': 'Utilities'
}

end_date = datetime.today()
start_date = end_date - timedelta(days=120)

# 1. Fetch ETF data & rank relative strength
etf_data = {}
for ticker, name in SECTOR_ETFS.items():
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    if len(df) >= 60:
        p_start = float(df['Close'].iloc[-60].item())
        p_end = float(df['Close'].iloc[-1].item())
        ret_3m = ((p_end - p_start) / p_start) * 100
        etf_data[ticker] = {'name': name, 'return_3m': round(ret_3m, 2), 'price': round(p_end, 2)}

# Sort by 3-month return
sorted_etfs = sorted(etf_data.items(), key=lambda x: x[1]['return_3m'], reverse=True)

# 2. Classify Leading vs. Improving
sectors_output = []
for rank, (ticker, info) in enumerate(sorted_etfs, start=1):
    # Top 3 are Leading; ranks 4 to 6 are Improving; lower are Weakening/Lagging
    if rank <= 3:
        status = 'leading'
    elif rank <= 6:
        status = 'improving'
    elif rank <= 9:
        status = 'weakening'
    else:
        status = 'lagging'
    
    sectors_output.append({
        'ticker': ticker,
        'name': info['name'],
        'price': info['price'],
        'return_3m': info['return_3m'],
        'status': status,
        'rank': rank
    })

payload = {
    'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
    'sectors': sectors_output
}

with open('data.json', 'w') as f:
    json.dump(payload, f, indent=2)

print("Market scan complete. data.json written successfully.")