import calendar
import cot_reports as cot
import pandas as pd
import yfinance as yf
import numpy as np


global backup_cot
backup_cot=pd.DataFrame()

class COTIndicator:
    def __init__(self,market, year=None, report_type='legacy_fut', ):
        self.year = year
        self.report_type = report_type
        self.market = market
        self.df = pd.DataFrame()
    
    def get_cot_data(self):
        
        # Declare backup_cot as a global variable
        global backup_cot
        # Example: cot_year()
        raw=pd.DataFrame()
        if backup_cot.empty==False:
            raw = backup_cot
        else:
            if self.year:
                raw = cot.cot_year(year=self.year,cot_report_type = self.report_type)
                backup_cot = raw
            else:
                # raw = cot.cot_all(cot_report_type = self.report_type)
                raw = cot.cot_year(year=2024,cot_report_type = self.report_type)
                backup_cot = raw
                # raw.to_csv('cot_all.csv')


        #filter only gold data cotntains word gold in it
        # df = raw[raw['Market and Exchange Names']=='GOLD - COMMODITY EXCHANGE INC.']
        self.df = raw[raw['Market and Exchange Names']==self.market]
        # self.df = raw[raw['Market and Exchange Names'].str.contains(self.market)]

        #s&p 500
        # df = raw[raw['Market and Exchange Names']=='E-MINI S&P 500 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE']

        #161227
        #161220
        #161213 ...


        self.df=self.df[['As of Date in Form YYMMDD','Noncommercial Positions-Long (All)','Noncommercial Positions-Short (All)','Noncommercial Positions-Spreading (All)',"Open Interest (All)"]]
        self.df.columns=['date','long','short','spreading','open_interest']
        self.df['net'] = self.df['long'] - self.df['short']

        #loop through dataframe and convert date to 20xx-xx-xx or 19xx-xx-xx, depending on the year, if year is greater than 50 then 19xx else 20xx, and handle case of when length of date is less than 6
        for index, row in self.df.iterrows():
            date = str(row['date'])
            if len(date)==3:
                date='20000'+date
            if len(date)==4:
                date='2000'+date
            if len(date)==5:
                date='200'+date
            if len(date)==6:
                if int(date[:2])>50:
                    date='19'+date
                else:
                    date='20'+date
            self.df.at[index,'date'] = date
            
        self.df.to_csv('cot_usd_.csv')




        #convert date to datetime
        self.df['date'] = pd.to_datetime(self.df['date'])

        self.df.drop_duplicates(subset='date',keep="first",inplace=True)


        self.df.set_index('date',inplace=True)

        #remove duplicates by date


        #sort by date
        self.df.sort_values(by='date',inplace=True)
        #set date as index

        #inverse the order of the dataframe
        # df = df.iloc[::-1]



        #long and short percentage
        self.df['long_percentage'] = self.df['long']/(self.df['long']+self.df['short']) * 100
        self.df['short_percentage'] = self.df['short']/(self.df['long']+self.df['short']) * 100
        # #change in long and short
        self.df['long_change'] = self.df['long'].diff()
        self.df['short_change'] = self.df['short'].diff()

        self.df['long_change_percentage']=self.df['long_change']/self.df['long'] * 100
        self.df['short_change_percentage']=self.df['short_change']/self.df['short'] * 100
        self.df['open_interest_change'] = self.df['open_interest'].diff()


        #week over week change in net position
        self.df['change_in_net'] = self.df['net'].diff() / self.df['net'] * 100

    def score_latest(self):
        latest_cot = self.df.iloc[-1]
        return self.score(latest_cot)

    def score_all(self):
        self.df['score'] = self.df.apply(self.score,axis=1)
        return self.df['score']
        
    def score(self,element):
        score = 0
        if element['long_percentage'] >= 60:
            score = score + 1
        if element['short_percentage'] >= 60:
            score = score - 1
        if element['long_change_percentage'] > 0:
            score = score + 1
        if element['long_change_percentage']  < 0:
            score = score - 1        
        if element['short_change_percentage'] > 0:
            score = score - 1
        if element['short_change_percentage'] < 0:
            score = score + 1
        if element['change_in_net'] > 0:
            score = score + 1
        if element['change_in_net'] < 0:
            score = score - 1
        if score > 3:
            return 3
        if score < -3:
            return -3
        return score
    
            

    def to_csv(self):
        self.df.to_csv(f"cot_{self.market}.csv")
        






class SeasonalityIndicator:
    def __init__(self,market ):
        self.market = market
        self.df = pd.DataFrame()
        today_date = pd.to_datetime('today')
        ago_years_ago = '2010-01-01'
        self.df = yf.download(self.market, start=ago_years_ago, end=today_date, interval="1mo")
        #remove 2020 data
        # self.df = self.df[self.df.index.year != 2020 ]
        self.df = self.df[self.df.index.year != 2008 ]
        # calculate average return for each month
        # self.df["return"] = (self.df['Close'] - self.df['Open'] )/ self.df['Open']
        self.df["return"] = self.df['Close'].pct_change()
        self.df = self.df.dropna()
        self.df['return'] = self.df['return']*100
        self.df['month'] = self.df.index.month
        # self.df['month'] = self.df['month'].apply(lambda x: calendar.month_abbr[x])
        self.df = self.df.groupby('month').mean()
        self.df['month'] = self.df.index
        #sort the data by return
        self.df = self.df.sort_values(by='return',ascending=False)
        self.df=self.df[['return']]
                

    
    def get_seasonality_for_month(self,month):
        return self.df.loc[month].values[0]

    def get_seasonality_score_for_month(self,month):
        seasonality= self.df.loc[month].values[0]
        if seasonality > 0:
            return 1
        if seasonality < 0:
            return -1
        return 0
    
class TrendIndicator:
    def __init__(self,market ):
        self.market = market
        self.df = pd.DataFrame()
        today_date = pd.to_datetime('today')
        ago_years_ago = '2010-01-01'
        self.df = yf.download(self.market, start=ago_years_ago, end=today_date, interval="1d")
        #remove 2020 data
        # self.df = self.df[self.df.index.year != 2020 ]
        #calculate 5, 8, and 21 days exponential moving average
        self.df['5d'] = self.df['Close'].ewm(span=5, adjust=False).mean()
        self.df['8d'] = self.df['Close'].ewm(span=8, adjust=False).mean()
        self.df['21d'] = self.df['Close'].ewm(span=21, adjust=False).mean()

        #score this way, if 5d > 8d > 21d, score is 2, 5d <= 8d and 8d > 21d 1 , 5d = 8d , 8d < 21d -2 , 5d < 8d < 21d -1 , 5d > 8d < 21d 0
        self.df['score'] = 0
        self.df.loc[(self.df['5d'] > self.df['8d']) & (self.df['8d'] > self.df['21d']), 'score'] = 2
        self.df.loc[(self.df['5d'] <= self.df['8d']) & (self.df['8d'] > self.df['21d']), 'score'] = 1
        self.df.loc[(self.df['5d'] == self.df['8d']) & (self.df['8d'] < self.df['21d']), 'score'] = -2
        self.df.loc[(self.df['5d'] < self.df['8d']) & (self.df['8d'] < self.df['21d']), 'score'] = -1
        self.df.loc[(self.df['5d'] > self.df['8d']) & (self.df['8d'] < self.df['21d']), 'score'] = 0

        self.df=self.df[['5d','8d','21d','score']]

    def get_latest_trend_score(self):
        return self.df.iloc[-1]['score']
    
    def get_trend_score_for_date(self,date):
        return self.df.loc[date]['score']
                

    


# #test usoil
# oilSeasonality = SeasonalityIndicator('^DJI')

# print(oilSeasonality.get_seasonality_for_month(

#date 2023-01-03 00:00:00
# date= pd.to_datetime('2023-01-03 00:00:00')
# trendTest= TrendIndicator('^DJI')
# print(trendTest.df)
# print(trendTest.get_trend_score_for_month(date))


# #s&p500
# spSeasonality = SeasonalityIndicator("^GSPC")
# print(spSeasonality.df)

# #nasdaq
# nasdaqSeasonality = SeasonalityIndicator("^IXIC")
# print(nasdaqSeasonality.df)
