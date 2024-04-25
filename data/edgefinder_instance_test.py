#scoring of edge finder is build this way :

#cot data
# retail sentiment
# seasonality
# trend reading
# inflation
# interest rates
# gdp
# services pmi
# maniufacturing pmi
# retail sales
# employment change
# unemployment rate


#example usd data
import datetime
import pandas as pd
from economic_indicator import EconomicIndicator
from cot_indicator import COTIndicator,SeasonalityIndicator,TrendIndicator

country = 'united-states'
# country='euro-area'

start_date = datetime.datetime(2017, 10, 1)

class EdgeFinderInstance:
    def __init__(self,market,indicators = [],cot=None,seasonality=None,retail_sentiment=None,trend_reading=None):
        self.market = market
        self.indicators = indicators
        self.cot = cot
        self.seasonality = seasonality
        self.retail_sentiment = retail_sentiment
        self.trend_reading = trend_reading
        self.scores = pd.DataFrame()

    def calcuate_scores(self):
        start_date = datetime.datetime(2017, 10, 1)
        end_date = pd.to_datetime('today')
        self.cot.score_all()
        cot=self.cot.df.loc[start_date:end_date]
        # print(cot)

        self.scores=pd.DataFrame(index=cot.index,columns=['total'])

        for date in cot.index:
            #get date of data
            data=cot.loc[date]['score']
            
            #get the score of the data of all other economic data
            score=0
            for ind in self.indicators:
                lat=ind.get_latest_according_to_date(date)
                score+=lat['score']

            total=(data + score)
            
            if self.seasonality is not None:
                score+=self.seasonality.get_seasonality_score_for_month(date.month)
            if self.trend_reading is not None:
                score+=self.trend_reading.get_trend_score_for_date(date)

            #insert in scores with date as index
            self.scores.loc[date,'total']=total

    def add_seasonality_score(self,seasonality):
        for date in self.scores.index:
            self.scores.loc[date,'total']+=seasonality.get_seasonality_score_for_month(date.month)
    def add_trend_score(self,trend):
        for date in self.scores.index:
            self.scores.loc[date,'total']+=trend.get_trend_score_for_date(date)

    def cross_with_instance(self,instance):
        if type(instance) is not EdgeFinderInstance:
            raise Exception('Instance must be of type EdgeFinderInstance')
        for date in self.scores.index:
            if date in instance.scores.index:
                self.scores.loc[date,'total'] -= instance.scores.loc[date,'total']
            # self.scores.loc[date,'total']-=instance.scores.loc[date,'total']
    
    def get_bullish_bearish_signals(self):
        self.scores['bullish_signal']=self.scores['total']>4
        self.scores['bearish_signal']=self.scores['total']<-4

        bullish_signals = self.scores[self.scores['bullish_signal']]
        bearish_signals = self.scores[self.scores['bearish_signal']]

        return bullish_signals,bearish_signals



                    

    
        
    
from edgefinder_economies.US import USA
from edgefinder_economies.Japan import JPY
from edgefinder_economies.Europe import EUR
from edgefinder_economies.Australia import AUD
from edgefinder_economies.UK import GBP
from edgefinder_economies.Suisse import CHF
from edgefinder_economies.Canada import CAD
from edgefinder_economies.NewZealand import NZD


import yfinance as yf
from sklearn.preprocessing import StandardScaler


import matplotlib.pyplot as plt

scaler = StandardScaler()

usd_oil,usd_oil_cot,usd_oil_seasonality,usd_oil_trend =USA()
usdOilInstance= EdgeFinderInstance('usd',indicators=usd_oil,cot=usd_oil_cot)
usdOilInstance.calcuate_scores()

usd,usd_cot,usd_seasonality,usd_trend =USA(inverse_inflation=False)
eur,eur_cot, eur_seasonality,eur_trend =EUR(inverse_inflation=False)
jpy,jpy_cot,jpy_seasonality,jpy_trend =JPY(inverse_inflation=False)
chf,chf_cot =CHF()
cad,cad_cot =CAD(inverse_inflation=False)
nzd,nzd_cot =NZD(inverse_inflation=False)

usdInstance= EdgeFinderInstance('usd',indicators=usd,cot=usd_cot)
usdInstance.calcuate_scores()

jpyInstance= EdgeFinderInstance('jpy',indicators=jpy,cot=jpy_cot)
jpyInstance.calcuate_scores()

chfInstance= EdgeFinderInstance('chf',indicators=chf,cot=chf_cot)
chfInstance.calcuate_scores()

eurInstance= EdgeFinderInstance('eur',indicators=eur,cot=eur_cot)
eurInstance.calcuate_scores()

cadInstance= EdgeFinderInstance('cad',indicators=cad,cot=cad_cot)
cadInstance.calcuate_scores()

nzdInstance= EdgeFinderInstance('nzd',indicators=nzd,cot=nzd_cot)
nzdInstance.calcuate_scores()


#cross with usd instance
eurInstance.cross_with_instance(usdInstance)
eurusdSeasonality=SeasonalityIndicator('EURUSD=X')
eurusdTrend=TrendIndicator('EURUSD=X')
eurInstance.add_seasonality_score(eurusdSeasonality)
eurInstance.add_trend_score(eurusdTrend)
eurInstance.scores.to_csv("EURUSD.csv")

gold_cot=COTIndicator(market='GOLD - COMMODITY EXCHANGE INC.')
gold_cot.get_cot_data()

goldInstance= EdgeFinderInstance('gold',indicators=[],cot=gold_cot)
goldInstance.calcuate_scores()

oil_cot=COTIndicator(market='WTI FINANCIAL CRUDE OIL - NEW YORK MERCANTILE EXCHANGE')
oil_cot.get_cot_data()





oilInstance= EdgeFinderInstance('oil',indicators=usd_oil,cot=oil_cot)
oilInstance.calcuate_scores()
# oilInstance.cross_with_instance(usdOilInstance)
oilSeasonality=SeasonalityIndicator('CL=F')
oilTrend=TrendIndicator('CL=F')
oilInstance.add_seasonality_score(oilSeasonality)
oilInstance.add_trend_score(oilTrend)


#cross with usd instance
#gold becomes XAUUSD
goldInstance.cross_with_instance(usdInstance)
xauusdSeasonality=SeasonalityIndicator('GC=F')
xauusdTrend=TrendIndicator('GC=F')
goldInstance.add_seasonality_score(xauusdSeasonality)
goldInstance.add_trend_score(xauusdTrend)

# print(xauusdSeasonality.df)
# xauusdSeasonality.df.to_csv("xauseas.csv")

print("LATEST XAUUSD CROSS")

for index,ind in enumerate(usd):
    usd_lat=ind.get_latest_record()
    print(f"{ind.indicator} : {- (usd_lat['score'])}")
print("GOLD COT",gold_cot.score_latest())
print("GOLD seasoanlity",xauusdSeasonality.get_seasonality_score_for_month(pd.to_datetime('today').month))
print("GOLD trend",xauusdTrend.df['score'].iloc[-1])


usdChfInstance= EdgeFinderInstance('usdchf',indicators=usd,cot=usd_cot)

usdChfInstance.calcuate_scores()

usdChfInstance.cross_with_instance(chfInstance)

ucSeas=SeasonalityIndicator('CHF=X')
usdChfInstance.add_seasonality_score(ucSeas)
ucTr=TrendIndicator('CHF=X')
usdChfInstance.add_trend_score(ucTr)

print("LATEST USDCHF CROSS")
for index,ind in enumerate(usd):
    usd_lat=ind.get_latest_record()
    chf_lat=chf[index].get_latest_record()
    print(f"{ind.indicator} : {usd_lat['score'] - chf_lat['score']}")

print("USDCHF COT",usd_cot.score_latest() - chf_cot.score_latest())
print("USDCHF seasoanlity",ucSeas.get_seasonality_score_for_month(pd.to_datetime('today').month))
print("USDCHF trend",ucTr.df['score'].iloc[-1])


usdCadInstance= EdgeFinderInstance('usdcad',indicators=usd,cot=usd_cot)

usdCadInstance.calcuate_scores()

usdCadInstance.cross_with_instance(cadInstance)

cadSeas=SeasonalityIndicator('CAD=X')
usdCadInstance.add_seasonality_score(cadSeas)
cadTr=TrendIndicator('CAD=X')
usdCadInstance.add_trend_score(cadTr)

print("LATEST USDCAD CROSS")
for index,ind in enumerate(usd):
    usd_lat=ind.get_latest_record()
    cad_lat=cad[index].get_latest_record()
    print(f"{ind.indicator} : {usd_lat['score'] - cad_lat['score']}")
print("USDCAD COT",usd_cot.score_latest() - cad_cot.score_latest())
print("USDCAD seasoanlity",cadSeas.get_seasonality_score_for_month(pd.to_datetime('today').month))
print("USDCAD trend",cadTr.df['score'].iloc[-1])


#nzd usd

nzdUsdInstance= EdgeFinderInstance('nzdusd',indicators=nzd,cot=nzd_cot)

nzdUsdInstance.calcuate_scores()

nzdUsdInstance.cross_with_instance(usdInstance)

nzdUsdSeas=SeasonalityIndicator('NZDUSD=X')
nzdUsdInstance.add_seasonality_score(nzdUsdSeas)

nzdUsdTr=TrendIndicator('NZDUSD=X')

nzdUsdInstance.add_trend_score(nzdUsdTr)

print("LATEST NZDUSD CROSS")

for index,ind in enumerate(nzd):
    nzd_lat=ind.get_latest_record()
    usd_lat=usd[index].get_latest_record()
    print(f"{ind.indicator} : {nzd_lat['score'] - usd_lat['score']}")

print("NZDUSD COT",nzd_cot.score_latest() - usd_cot.score_latest())
print("NZDUSD seasoanlity",nzdUsdSeas.get_seasonality_score_for_month(pd.to_datetime('today').month))
print("NZDUSD trend",nzdUsdTr.df['score'].iloc[-1])



us30_cot=COTIndicator(market='DJIA Consolidated - CHICAGO BOARD OF TRADE')
us30_cot.get_cot_data()

us30_instance= EdgeFinderInstance('us30',indicators=usd_oil,cot=us30_cot)
us30_instance.calcuate_scores()

us30_seasonality=SeasonalityIndicator('^DJI')
us30_trend=TrendIndicator('^DJI')

us30_instance.add_seasonality_score(us30_seasonality)
us30_instance.add_trend_score(us30_trend)

print("LATEST US30 CROSS")
for index,ind in enumerate(usd):
    usd_lat=ind.get_latest_record()
    print(f"{ind.indicator} : {usd_lat['score']}")

print("US30 COT",us30_cot.score_latest())
print("US30 seasoanlity",us30_seasonality.get_seasonality_score_for_month(pd.to_datetime('today').month))
print("US30 trend",us30_trend.df['score'].iloc[-1])

import sys
sys.exit()


#usd instance becomes USDJPY
# usdInstance.cross_with_instance(jpyInstance)
# # usdInstance=jpyInstance

# usdJpySeasonality=SeasonalityIndicator('JPY=X')
# usdJpyTrend=TrendIndicator('JPY=X')

# usdInstance.add_seasonality_score(usdJpySeasonality)
# usdInstance.add_trend_score(usdJpyTrend)

# print("USD JPY:")
# print(usdInstance.scores)
# usdInstance.scores.to_csv("USDJPY.csv")
#usd instace becomes USDCHF
# usdInstance.cross_with_instance(chfInstance)

# usdChfSeasonality=SeasonalityIndicator('CHF=X')
# usdChfTrend=TrendIndicator('CHF=X')

# usdInstance.add_seasonality_score(usdChfSeasonality)
# usdInstance.add_trend_score(usdChfTrend)

# print(usdInstance.scores)

# usd becomes USDCAD
usdInstance.cross_with_instance(cadInstance)

usdCadSeasonality=SeasonalityIndicator('CAD=X')
usdCadTrend=TrendIndicator('CAD=X')

usdInstance.add_seasonality_score(usdCadSeasonality)
usdInstance.add_trend_score(usdCadTrend)

usdInstance.scores.to_csv("USDCAD.csv")

print(usdInstance.scores)


plt.figure(50)
#eurusd
bullish_signals_eurusd,bearish_signals_eurusd = eurInstance.get_bullish_bearish_signals()


if len(bullish_signals_eurusd)>0:
    plt.scatter(bullish_signals_eurusd.index, scaler.fit_transform(bullish_signals_eurusd['total'].values.reshape(-1,1)), c=bullish_signals_eurusd['bullish_signal'], cmap='coolwarm')
if len(bearish_signals_eurusd)>0:
    plt.scatter(bearish_signals_eurusd.index, scaler.fit_transform(bearish_signals_eurusd['total'].values.reshape(-1,1)), c=bearish_signals_eurusd['bearish_signal'], cmap='coolwarm')

for date in bullish_signals_eurusd.index:
    plt.axvline(x=date, color='g', linestyle='--')
for date in bearish_signals_eurusd.index:
    plt.axvline(x=date, color='r', linestyle='--')

eurusd_prices = yf.download('EURUSD=X', start=start_date.strftime("%Y-%m-%d"), end='2024-05-01', interval='1wk')



eurInstance_weeks = eurInstance.scores.index.to_period('W')
eurusd_prices_weeks = eurusd_prices.index.to_period('W')
# Find the intersection of the weeks
common_weeks = eurInstance_weeks.intersection(eurusd_prices_weeks)

#change the index to week
eurInstance.scores.index = eurInstance_weeks
eurusd_prices.index = eurusd_prices_weeks


# calculate correlation between score and price
print("EU CORRELATION:",eurInstance.scores['total'].corr(eurusd_prices['Close']))

plt.plot(eurusd_prices.index, scaler.fit_transform(eurusd_prices['Close'].values.reshape(-1,1)), label='EURUSD')

plt.legend()

plt.figure(100)

bullish_signals_gold,bearish_signals_gold = goldInstance.get_bullish_bearish_signals()

if len(bullish_signals_gold)>0:
    plt.scatter(bullish_signals_gold.index, scaler.fit_transform(bullish_signals_gold['total'].values.reshape(-1,1)), c=bullish_signals_gold['bullish_signal'], cmap='coolwarm')
if len(bearish_signals_gold)>0:
    plt.scatter(bearish_signals_gold.index, scaler.fit_transform(bearish_signals_gold['total'].values.reshape(-1,1)), c=bearish_signals_gold['bearish_signal'], cmap='coolwarm')

#draw vertical line where bullish_signal is true
for date in bullish_signals_gold.index:
    plt.axvline(x=date, color='g', linestyle='--')
for date in bearish_signals_gold.index:
    plt.axvline(x=date, color='r', linestyle='--')

# plt.plot((goldInstance.scores['total']),label='Gold Score')
# plt.plot(scaler.fit_transform(goldInstance.scores['total'].values.reshape(-1,1)),label='Gold Score')
# plt.plot(scaler.fit_transform(yf.download('GC=F',start=start_date.strftime("%Y-%m-%d"),end='2024-05-01',interval='1wk')['Close'].values.reshape(-1,1)),label='XAUUSD')
gold_prices = yf.download('GC=F', start=start_date.strftime("%Y-%m-%d"), end='2024-05-01', interval='1wk')

# calculate correlation between score and price
#get indexs with same weeks 
print(goldInstance.scores.index)
print(gold_prices.index)

goldInstance_weeks = goldInstance.scores.index.to_period('W')
gold_prices_weeks = gold_prices.index.to_period('W')

# Find the intersection of the weeks
# Find the intersection of the weeks
common_weeks = goldInstance_weeks.intersection(gold_prices_weeks)

#change the index to week
goldInstance.scores.index = goldInstance_weeks
gold_prices.index = gold_prices_weeks




print("XAUUSD CORRELATION:", goldInstance.scores['total'].dropna().corr(gold_prices['Close'].dropna()))

plt.plot(gold_prices.index, scaler.fit_transform(gold_prices['Close'].values.reshape(-1,1)), label='XAUUSD')

plt.legend()

# print("LATEST USD")
# for ind in usd:
#         lat=ind.get_latest_record()
#         print(f"{ind.indicator} : {lat['score']}")
# print("LATEST JPY")
# for ind in jpy:
#         lat=ind.get_latest_record()
#         print(f"{ind.indicator} : {lat['score']}")

# print("LATEST USDJPY CROSS")

# for index,ind in enumerate(usd):
#     usd_lat=ind.get_latest_record()
#     jpy_lat=jpy[index].get_latest_record()
#     print(f"{ind.indicator} : {usd_lat['score'] - jpy_lat['score']}")
 





plt.figure(200)


bullish_signals_uj,bearish_signals_uj = usdInstance.get_bullish_bearish_signals()

if len(bullish_signals_uj)>0:
    plt.scatter(bullish_signals_uj.index, scaler.fit_transform(bullish_signals_uj['total'].values.reshape(-1,1)), c=bullish_signals_uj['bullish_signal'], cmap='coolwarm')

if len(bearish_signals_uj)>0:
    plt.scatter(bearish_signals_uj.index, scaler.fit_transform(bearish_signals_uj['total'].values.reshape(-1,1)), c=bearish_signals_uj['bearish_signal'], cmap='coolwarm')

#draw vertical line where bullish_signal is true
for date in bullish_signals_uj.index:
    plt.axvline(x=date, color='g', linestyle='--')
for date in bearish_signals_uj.index:
    plt.axvline(x=date, color='r', linestyle='--')
# plt.plot(usdInstance.scores['total'],label='UJ Score')
# plt.plot(scaler.fit_transform(usdInstance.scores['total'].values.reshape(-1,1)),label='UJ Score')
# plt.plot(scaler.fit_transform(yf.download('JPY=X',start=start_date.strftime("%Y-%m-%d"),end='2024-05-01',interval='1wk')['Close'].values.reshape(-1,1)),label='USDJPY')
usdjpy_prices = yf.download('CAD=X', start=start_date.strftime("%Y-%m-%d"), end='2024-05-01', interval='1wk')

# calculate correlation between score and price


usdInstance_weeks = usdInstance.scores.index.to_period('W')
usdjpy_prices_weeks = usdjpy_prices.index.to_period('W')

# Find the intersection of the weeks
common_weeks = usdInstance_weeks.intersection(usdjpy_prices_weeks)

#change the index to week
usdInstance.scores.index = usdInstance_weeks
usdjpy_prices.index = usdjpy_prices_weeks

print("UJ CORRELATION:",usdInstance.scores['total'].corr(usdjpy_prices['Close']))

plt.plot(usdjpy_prices.index, scaler.fit_transform(usdjpy_prices['Close'].values.reshape(-1,1)), label='UJ')


plt.legend()

plt.figure(300)

bullish_signals_oil,bearish_signals_oil = oilInstance.get_bullish_bearish_signals()

plt.scatter(bullish_signals_oil.index, scaler.fit_transform(bullish_signals_oil['total'].values.reshape(-1,1)), c=bullish_signals_oil['bullish_signal'], cmap='coolwarm')
if len(bearish_signals_oil)>0:
    plt.scatter(bearish_signals_oil.index, scaler.fit_transform(bearish_signals_oil['total'].values.reshape(-1,1)), c=bearish_signals_oil['bearish_signal'], cmap='coolwarm')

#draw vertical line where bullish_signal is true
for date in bullish_signals_oil.index:
    plt.axvline(x=date, color='g', linestyle='--')
for date in bearish_signals_oil.index:
    plt.axvline(x=date, color='r', linestyle='--')

# plt.plot(oilInstance.scores['total'],label='Oil Score')
# plt.plot(scaler.fit_transform(oilInstance.scores['total'].values.reshape(-1,1)),label='Oil Score')
# plt.plot(scaler.fit_transform(yf.download('CL=F',start=start_date.strftime("%Y-%m-%d"),end='2024-05-01',interval='1wk')['Close'].values.reshape(-1,1)),label='Oil')
oil_prices = yf.download('CL=F', start=start_date.strftime("%Y-%m-%d"), end='2024-05-01', interval='1wk')


# calculate correlation between score and price

oilInstance_weeks = oilInstance.scores.index.to_period('W')
oil_prices_weeks = oil_prices.index.to_period('W')

# Find the intersection of the weeks
common_weeks = oilInstance_weeks.intersection(oil_prices_weeks)

#change the index to week
oilInstance.scores.index = oilInstance_weeks
oil_prices.index = oil_prices_weeks

print("OIL CORRELATION:",oilInstance.scores['total'].corr(oil_prices['Close']))

plt.plot(oil_prices.index, scaler.fit_transform(oil_prices['Close'].values.reshape(-1,1)), label='Oil')

plt.legend()



# print("==========")


us30_cot=COTIndicator(market='DJIA Consolidated - CHICAGO BOARD OF TRADE')
us30_cot.get_cot_data()

us30_instance= EdgeFinderInstance('us30',indicators=usd,cot=us30_cot)
us30_instance.calcuate_scores()

us30_seasonality=SeasonalityIndicator('^DJI')
us30_trend=TrendIndicator('^DJI')

us30_instance.add_seasonality_score(us30_seasonality)
us30_instance.add_trend_score(us30_trend)



plt.figure(400)



bullish_us30,bearish_us30 = us30_instance.get_bullish_bearish_signals()

if len(bullish_us30)>0: 
    plt.scatter(bullish_us30.index, scaler.fit_transform(bullish_us30['total'].values.reshape(-1,1)), c=bullish_us30['bullish_signal'], cmap='coolwarm')

if len(bearish_us30)>0:
    plt.scatter(bearish_us30.index, scaler.fit_transform(bearish_us30['total'].values.reshape(-1,1)), c=bearish_us30['bearish_signal'], cmap='coolwarm')

#draw vertical line where bullish_signal is true
for date in bullish_us30.index:
    plt.axvline(x=date, color='g', linestyle='--')
for date in bearish_us30.index:
    plt.axvline(x=date, color='r', linestyle='--')

# plt.plot(oilInstance.scores['total'],label='Oil Score')
# plt.plot(scaler.fit_transform(oilInstance.scores['total'].values.reshape(-1,1)),label='Oil Score')
# plt.plot(scaler.fit_transform(yf.download('CL=F',start=start_date.strftime("%Y-%m-%d"),end='2024-05-01',interval='1wk')['Close'].values.reshape(-1,1)),label='Oil')
us30_prices = yf.download('^DJI', start=start_date.strftime("%Y-%m-%d"), end='2024-05-01', interval='1wk')

us30Instance_weeks = us30_instance.scores.index.to_period('W')
us30_prices_weeks = us30_prices.index.to_period('W')

# Find the intersection of the weeks
common_weeks = us30Instance_weeks.intersection(us30_prices_weeks)

#change the index to week
us30_instance.scores.index = us30Instance_weeks
us30_prices.index = us30_prices_weeks

# calculate correlation between score and price
print("DJI CORRELATION:",us30_instance.scores['total'].corr(us30_prices['Close']))

plt.plot(us30_prices.index, scaler.fit_transform(us30_prices['Close'].values.reshape(-1,1)), label='US30')

plt.legend()


print("EURUSD SCORES")
print(eurInstance.scores)

print("USDCAD SCORES")
print(usdInstance.scores)

print("GOLD SCORES")
print(goldInstance.scores)

print("OIL SCORES")
print(oilInstance.scores)

print("US30 SCORES")
print(us30_instance.scores)



#all to csv  
eurInstance.scores.to_csv("EURUSD.csv")
usdInstance.scores.to_csv("USDCAD.csv")
goldInstance.scores.to_csv("GOLD.csv")
oilInstance.scores.to_csv("OIL.csv")
us30_instance.scores.to_csv("US30.csv")


#loop through data


def toString(pair,instance):
    string=""
    for index in instance.scores.index:
        #split date in / to get first and last day of week
        row=instance.scores.loc[index]
        date=index
        firstDay=date.to_timestamp(how='start')
        lastDay=date.to_timestamp(how='end')
        #remove time
        firstDay=firstDay.strftime("%Y-%m-%d")
        lastDay=lastDay.strftime("%Y-%m-%d")
        #get bullish and bearish signal
        total=row["total"]
        bullish_signal=row["bullish_signal"]
        bearish_signal=row["bearish_signal"]
        string+="{"+f'"{firstDay}","{lastDay}","{total}","{bullish_signal}","{bearish_signal}"'+"},\n"

    #string to file
    with open(pair+".txt", "w") as file:
        file.write(string)

toString("EURUSD",eurInstance)
toString("USDCAD",usdInstance)
toString("GOLD",goldInstance)
toString("OIL",oilInstance)
toString("US30",us30_instance)


plt.show()
