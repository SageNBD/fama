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

def populate_dictionary(sia):
    print('Reading data from Excel sheet...')
    df_dictionary = pd.read_excel('dictionary.xlsx').filter(
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
    
    petr = {
        'moro': -1.60591526778577,
        'lava': -1.60591526778577,
        'jato': -1.60591526778577,
        'STF': -1.60591526778577      
    }
    sia.lexicon.update(petr)

    
# MongoDB Setup
client = MongoClient('localhost', 27017)
assert('fama' in client.list_database_names())
db = client.fama

# Sentiment Intensity Analyser
sia = SIA()
populate_dictionary(sia)

assets = ['itau', 'ambev', 'petrobras']

asset_collection = get_collections(db, assets)
hist_data = get_historical_data(assets)

scores_df = {}
for asset in assets: # FUNCAO
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
        
        num_docs = docs.count()
        score.append(pol_score / num_docs if num_docs else .0)
        
        curr += datetime.timedelta(days=1)
    
    scores_df[asset] = pd.DataFrame({'Pol Score': score}, 
                                    index=pd.date_range(start=start, end=end)
                                    )
    print('DONE')

df = {}
for asset in assets: # FUNCAO
    df[asset] = scores_df[asset].join(hist_data[asset])
    #df[asset].bfill(inplace=True)
    df[asset].dropna(inplace=True)
    df[asset]['Returns'] = (
        df[asset]['Adj Close'] / df[asset]['Adj Close'].shift(1) - 1
    )
    df[asset]['Pred Score'] = df[asset]['Pol Score'].shift(1)

df_pred = {}
df_corr = {}
for asset in assets:
    df_pred[asset] = df[asset].filter(['Pred Score', 'Returns'])
    df_corr[asset] = df_pred[asset].corr()
    
df_pred_final = {}
df_corr2 = {}
for asset in assets:
    df_pred_final[asset] = df_pred[asset][(df_pred[asset]['Pred Score'] >= 0.5) |
                                (df_pred[asset]['Pred Score'] <= -0.5)]
    df_corr2[asset] = df_pred_final[asset].corr()