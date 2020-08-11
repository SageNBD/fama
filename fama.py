from pymongo import MongoClient
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import pandas as pd
import datetime
import yfinance as yf
import numpy as np

def get_collections(db, assets):
    asset_collection = {} # Create collection for each asset
    for asset in assets:
        asset_collection[asset] = db[asset]

    return asset_collection

def get_historical_data(assets):
    hist_data = {}
    ticker = {
            'ambev': 'abev3.sa',
            'petrobras': 'petr3.sa',
            'itau': 'itub3.sa'
    }
    for asset in assets:
        hist_data[asset] = pd.DataFrame(yf.download(
                ticker[asset],
                start='2016-1-1',
                end='2019-12-31')['Adj Close'])
    return hist_data

# MongoDB Setup
client = MongoClient('localhost', 27017)
assert('fama' in client.list_database_names())
db = client.fama

# Sentiment Intensity Analyser
sia = SIA()

assets = ['itau', 'ambev', 'petrobras']

asset_collection = get_collections(db, assets)
hist_data = get_historical_data(assets)

scores_df = {}

for asset in assets:
    start = datetime.datetime(2016, 1, 1)
    end = datetime.datetime(2019, 12, 31)
    
    score = []
    curr = start
    print(f'Getting pol scores for {asset}...', end=' ')
    while curr <= end:
        docs = asset_collection[asset].find(
            {"date": curr.strftime("%d/%m/%y")}
        )
        
        pol_score = 0
        for doc in docs:
            pol_score += (
                sia.polarity_scores(doc['headline'])['compound']
                + sia.polarity_scores(doc['body'])['compound']
            )
        
        score.append(pol_score)
        curr += datetime.timedelta(days=1)
    
    scores_df[asset] = pd.DataFrame({'Pol Score': score}, index=pd.date_range(start=start, end=end))
    print('DONE')

dataframes = {}
for asset in assets:
    #dataframes[asset] = hist_data[asset].join(scores_df[asset])
    dataframes[asset] = scores_df[asset].join(hist_data[asset])
    dataframes[asset].bfill(inplace=True)