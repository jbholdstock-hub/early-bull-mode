import yfinance as yf
import json
from datetime import datetime, timedelta

# 11 Standard SPDR Sector ETFs and their core bellwether stocks
SECTOR_ETFS = {
    'XLK': {'name': 'Technology', 'stocks': ['MSFT', 'AAPL', 'NVDA', 'AVGO', 'ORCL']},
    'XLC': {'name': 'Communication Services', 'stocks': ['META', 'GOOGL', 'NFLX', 'TMUS']},
    'XLY': {'name': 'Consumer Discretionary', 'stocks': ['AMZN', 'TSLA', 'HD', 'NKE']},
    'XLF': {'name': 'Financials', 'stocks': ['JPM', 'BAC', 'MS', 'GS', 'V']},
    'XLI': {'name': 'Industrials', 'stocks': ['GE', 'CAT', 'HON', 'UNP', 'LMT']},
    'XLE': {'name': 'Energy', 'stocks': ['XOM', 'CVX', 'COP', 'SLB', 'EOG']},
    'XLV': {'name': 'Healthcare', 'stocks': ['LLY', 'UNH', 'JNJ', 'ABBV']},
    'XLP': {'name': 'Consumer Staples', 'stocks': ['PG', 'COST', 'KO', 'WMT']},
    'XLB': {'name': 'Materials', 'stocks': ['LIN', 'APD', 'SHW', 'FCX']},
    'XLRE': {'name': 'Real Estate', 'stocks': ['PLD', 'AMT', 'EQIX']},
    'XLU': {'name': 'Utilities', 'stocks': ['NEE', 'SO', 'DUK', 'CEG']}
}

end_date = datetime.today()
start_date = end_date - timedelta(days=150)

# Step 1: Rank Sector ETFs by 3-Month Momentum
etf_rankings = {}
for ticker, info in SECTOR_ETFS.items():
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if len(df) >= 60:
            p_start = float(df['Close'].iloc[-60].item())
            p_end = float(df['Close'].iloc[-1].item())
            ret_3m = ((p_end - p_start) / p_start) * 100
            etf_rankings[ticker] = {
                'name': info['name'],
                'return_3m': round(ret_3m, 2),
                'price': round(p_end, 2),
                'stocks': info['stocks']
            }
    except Exception:
        pass

# Sort all 11 sectors by performance descending
sorted_sectors = sorted(etf_rankings.items(), key=lambda x: x[1]['return_3m'], reverse=True)

leading_etfs = []
improving_etfs = []
all_sectors_list = []
candidate_stocks = []

stock_history_start = end_date - timedelta(days=365)

# Step 2: Classify Ranks and Scan Components
for rank, (ticker, info) in enumerate(sorted_sectors, start=1):
    if rank <= 3:
        status = 'leading'
    elif rank <= 6:
        status = 'improving'
    elif rank <= 9:
        status = 'weakening'
    else:
        status = 'lagging'

    sector_entry = {
        'ticker': ticker,
        'name': info['name'],
        'price': info['price'],
        'return_3m': info['return_3m'],
        'status': status,
        'rank': rank
    }
    all_sectors_list.append(sector_entry)

    # Segregate Leading vs Improving ETFs
    if status == 'leading':
        leading_etfs.append(sector_entry)
    elif status == 'improving':
        improving_etfs.append(sector_entry)

    # Check stocks inside Leading & Improving sectors for Early Stage 2 Breakouts
    if status in ['leading', 'improving']:
        for stock in info['stocks']:
            try:
                sdf = yf.download(stock, start=stock_history_start, end=end_date, progress=False)
                if len(sdf) < 200:
                    continue

                sdf['50_MA'] = sdf['Close'].rolling(window=50).mean()
                sdf['200_MA'] = sdf['Close'].rolling(window=200).mean()
                sdf = sdf.dropna(subset=['50_MA', '200_MA'])

                price = float(sdf['Close'].iloc[-1].item())
                ma50 = float(sdf['50_MA'].iloc[-1].item())
                ma200 = float(sdf['200_MA'].iloc[-1].item())

                # Condition: Golden Cross where Price is within 6% of the 50 MA launchpad
                if ma50 > ma200 and price <= (ma50 * 1.06):
                    was_below = sdf['50_MA'] < sdf['200_MA']
                    days_cross = 999
                    if was_below.any():
                        last_below_idx = was_below.to_numpy().nonzero()[0][-1]
                        days_cross = int(len(sdf) - 1 - last_below_idx)

                    if days_cross <= 20:  # Fresh crossover
                        candidate_stocks.append({
                            'ticker': stock,
                            'name': stock,
                            'sector': info['name'],
                            'price': round(price, 2),
                            'ma50': round(ma50, 2),
                            'ma200': round(ma200, 2),
                            'daysCross': days_cross,
                            'parent_status': status
                        })
            except Exception:
                pass

# Step 3: Package payload
payload = {
    'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
    'leading_etfs': leading_etfs,
    'improving_etfs': improving_etfs,
    'sectors': all_sectors_list,
    'candidate_stocks': candidate_stocks
}

with open('data.json', 'w') as f:
    json.dump(payload, f, indent=2)

print("Scan complete. data.json generated with separate Leading and Improving ETF sets.")
