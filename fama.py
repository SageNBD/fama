from pymongo import MongoClient
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import pandas as pd
import datetime
import yfinance as yf
from pytrends.request import TrendReq

def get_collections(db, assets):
    asset_collection = {} # Create collection for each asset
    for asset in assets:
        asset_collection[asset] = db[asset]

    return asset_collection

def setup_db(assets):
    # MongoDB Setup
    client = MongoClient('localhost', 27017)
    assert('fama' in client.list_database_names())
    db = client.fama
    
    asset_collection = get_collections(db, assets)
    
    return db, asset_collection
    
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

def get_trends(assets):
    pytrends = TrendReq(hl='pt-BR')
    pytrends.build_payload(kw_list=assets, 
                            timeframe='2016-01-01 2019-12-31',
                            geo='BR',
                            cat=7)
    df_trends = pytrends.interest_over_time()
    
    return df_trends

def populate_dictionary(sia):
    print('Reading data from Excel sheet...')
    df_dictionary = pd.read_excel('sheets/dictionary.xlsx').filter(
                                ['Word', 'Negative_Unity', 'Positive_Unity'])
    new_words = {}
    print('Creating dictionary...', end=' ')
    for index, row in df_dictionary.iterrows():
        if row['Negative_Unity'] or row['Positive_Unity']:
            neg = row['Negative_Unity']
            pos = row['Positive_Unity']
            
            value = pos if pos != 0 else -neg
            
            new_words[row['Word'].lower()] = value
    print('DONE')
    sia.lexicon.update(new_words)

def setup_sia():
    # Sentiment Intensity Analyser
    sia = SIA()
    populate_dictionary(sia)
    return sia

def calc_polarity_scores(assets, asset_collection, sia):
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
            
            #num_docs = docs.count()
            #score.append(pol_score / num_docs if num_docs else .0)
            score.append(pol_score)
            
            curr += datetime.timedelta(days=1)
        
        scores_df[asset] = pd.DataFrame(
                        {'Pol Score': score}, 
                        index=pd.date_range(start=start, end=end)
        )
        print('DONE')  
    
    return scores_df

def merge_dataframes(scores_df, hist_data, trend_df):
    df = {}
    for asset in assets: # Merge each dataframe
        tmp = {}
        # Join each dataframe
        tmp = scores_df[asset].join(hist_data[asset]).join(
                                        trend_df.filter([asset]))
        # Fill each day with associated week trend value
        tmp[asset].ffill(inplace=True)
        # Dismiss days with no trading
        tmp.dropna(subset=['Adj Close'], inplace=True)
        
        # Create returns column 
        tmp['Returns'] = (
            tmp['Adj Close'] / tmp['Adj Close'].shift(1) - 1
        )
        # Shift polarity scores down to predict prices
        tmp['Pred Score'] = tmp['Pol Score'].shift(1)
        df[asset] = tmp
        
    return df

if __name__ == "__main__":
    assets = ['itau', 'ambev', 'petrobras']
    db, asset_collection = setup_db(assets)
    sia = setup_sia()

    scores_df = calc_polarity_scores(assets, asset_collection, sia)
    hist_data = get_historical_data(assets)
    trend_df = get_trends(assets)

    df = merge_dataframes(scores_df, hist_data, trend_df)

    for asset in assets:
        df[asset].to_csv(f'dados_{asset}.csv')
        df[asset].to_excel(f'dados_{asset}.xlsx', engine='xlsxwriter')