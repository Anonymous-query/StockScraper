import re
from StockScraper.bse import BSE
from datetime import datetime, timedelta
import pandas as pd

bse = BSE(download_folder='./')

# Get today's date and calculate the start and end of the current week
today = datetime.today().date()
start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
end_of_week = start_of_week + timedelta(days=4)  # Sunday of the current week

# Find the next week
next_monday = today + timedelta(days=-today.weekday(), weeks=1)
next_saturday = next_monday + timedelta(days=5)

action_data = bse.actions(segment="equity", 
                          from_date=next_monday, 
                          to_date=next_saturday,
                          by_date='ex'
            )

# Initialize the DataFrame with the specified columns
dividend_data = pd.DataFrame(columns=['Company Name', 'Ex-Dividend Date', 'Dividend', 'Stock Price', 'Earning'])

INVESTMENT_VALUE = 100000

data = []
for action in action_data:
    purpose = action['Purpose']
    quote_data = bse.quote(action['scrip_code'])
    if 'Dividend' in purpose:
        match = re.search(r"Rs\.\s*-\s*([\d.]+)", purpose)
        rp_format = f"{float(match.group(1)):.2f}"
        earnings = bse.calculat_earning_dividend(quote_data.get('LTP'), rp_format.format(), INVESTMENT_VALUE)
        data.append({
            "Company Name": action.get('long_name'),
            'Ex-Dividend Date': action.get('Ex_date'),
            'Dividend': rp_format.format(),
            "Stock Price": quote_data.get('LTP'),
            "Earning": int(earnings)
        })


new_rows = pd.DataFrame(data)
dividend_data = pd.concat([dividend_data, new_rows], ignore_index=True)

print(dividend_data)
dividend_data.to_excel(
    f'dividend_data{next_monday.strftime('%m_%d')}To{next_saturday.strftime('%m_%d')}.xlsx',
    index=False)

bse.exit()