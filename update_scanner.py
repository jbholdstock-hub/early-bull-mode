import yfinance as yf
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

etf_data = {}
for ticker, name in SECTOR_ETFS.items():
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if len(df) >= 60:
            p_start = float(df['Close'].iloc[-60].item())
            p_end = float(df['Close'].iloc[-1].item())
            ret_3m = ((p_end - p_start) / p_start) * 100
            etf_data[ticker] = {'name': name, 'return_3m': round(ret_3m, 2), 'price': round(p_end, 2)}
    except Exception:
        pass

sorted_etfs = sorted(etf_data.items(), key=lambda x: x[1]['return_3m'], reverse=True)

sectors_output = []
for rank, (ticker, info) in enumerate(sorted_etfs, start=1):
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

print("Scan complete. data.json generated.")
