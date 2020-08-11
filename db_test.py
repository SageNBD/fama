from pymongo import MongoClient
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import pandas as pd
import datetime
import yfinance as yf

def get_collections(db, assets):
    asset_collection = {} # Create collection for each asset
    for asset in assets:
        asset_collection[asset] = db[asset]

    return asset_collection

def create_dataframes(assets):
    dataframes = {}
    ticker = {
            'ambev': 'abev3.sa',
            'petrobras': 'petr3.sa',
            'itau': 'itub3.sa'
    }
    for asset in assets:
        dataframes[asset] = yf.download(
                ticker[asset],
                start='2019-5-1',
                end='2019-5-31')['Adj Close']
    return dataframes

#
# Score: [-1, 1]
# Depender da qntd de notícias
#
# Solução 1: pol_score(), num_news
#       final_score = pol_score() / num_news
# Solução 2: final_score = pol_score
# 
if __name__ == "__main__":
    # MongoDB Setup
    client = MongoClient('localhost', 27017)
    assert('fama' in client.list_database_names())
    db = client.fama

    # Sentiment Intensity Analyser
    sia = SIA()

    assets = ['itau', 'ambev', 'petrobras']

    asset_collection = get_collections(db, assets)
    dataframes = create_dataframes(assets)
    print(dataframes)

    for asset in assets:
        curr = datetime.datetime(2019, 5, 1)
        end = datetime.datetime(2019, 5, 31)
        
        print(asset)
        while curr != end:
            docs = asset_collection[asset].find(
                    {"date": curr.strftime("%d/%m/%y")}
            )
            pol_score = 0
            for doc in docs:
                pol_score += (
                    sia.polarity_scores(doc['headline'])['compound']
                    + sia.polarity_scores(doc['body'])['compound']
                )
            print(f'\t{curr.strftime("%d/%m/%y")}: {pol_score}')

            curr += datetime.timedelta(days=1)

