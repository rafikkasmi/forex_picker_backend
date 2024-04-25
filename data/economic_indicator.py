# Import necessary libraries
import pandas as pd
from fredapi import Fred
import datetime
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from math import sqrt
from sklearn.metrics import mean_absolute_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
import numpy as np
import dbnomics
import requests

#historic for nmi and pmi

historic_nmi=[56,54.4,53.1,53.7,52.2,56,58.6,54.4,55.4,53.9,53,54,51.6,53.1,55.2,56.3,56,58.7,59.6,58.6,57.1,59.3,56.2,56.7,56.9,56.5,57.8,55.7,56,60.3,59,56.9,59.1,55.9,55.3,53.5,53.4,54.5,55.7,52.9,56.5,55.5,51.4,57.1,54.8,57.2,57.2,56.5,57.6,55.2,57.5,56.9,57.4,53.9,55.3,59.8,60.1,57.4,55.9,59.9,59.5,58.8,56.8,58.6,59.1,55.7,58.5,61.6,60.3,60.7,57.6,56.7,59.7,56.1,55.5,56.9,55.1,53.7,56.4,52.6,54.7,53.9,55,55.5,57.3,52.5]
#this data is from mars 2013 to april 2020 ,make it in that
historic_nmi_dates=pd.date_range(start='2013-03-01',freq='M', end='2020-05-01')
historic_nmi_df=pd.DataFrame(historic_nmi,columns=['value'],index=historic_nmi_dates)


historic_pmi=[54.2,51.3,50.7,49,50.9,55.4,55.7,56.2,56.4,57.3,57,51.3,53.2,53.7,54.9,55.4,55.3,57.1,59,56.6,59,58.7,55.5,53.5,52.9,51.5,51.5,52.8,53.5,52.7,51.1,50.2,50.1,48.6,48.2,48.2,49.5,51.8,50.8,51.3,53.2,52.6,49.4,51.5,51.9,53.2,54.7,56,57.7,57.2,54.8,54.9,57.8,56.3,58.8,60.8,58.7,58.2,59.7,59.1,60.8,59.3,57.3,58.7,58.1,61.3,59.8,57.7,59.3,54.1,56.6,54.2,55.3,52.8,52.1,51.7,51.2,49.1,47.8,48.3,48.1,47.2,50.9,50.1,49.1,41.5]
#this data is from mars 2013 to april 2020 ,make it in that
historic_pmi_dates=pd.date_range(start='2013-03-01',freq='M', end='2020-05-01')
historic_pmi_df=pd.DataFrame(historic_pmi,columns=['value'],index=historic_pmi_dates)


class EconomicIndicator:
    def __init__(self, indicator,thresholds, scores,frequency='M',score_based_on='yoy',is_negative=False,denominator=None,is_percentage=False,datasource='fred',provider=None,country=None,name=""):
        self.name = name
        self.indicator = indicator
        self.fred = Fred(api_key='aca6076f59303e9cb2267bf2f16f80a9')
        self.df = pd.DataFrame()
        self.thresholds = thresholds
        self.scores = scores
        self.score_based_on = score_based_on
        self.frequency = frequency
        self.is_negative = is_negative
        self.denominator = denominator
        self.is_percentage = is_percentage
        self.datasource = datasource
        self.provider = provider
        self.country = country


    def get_data(self):
        start_date = datetime.datetime(1946, 1, 1)
        end_date = datetime.datetime(2023, 12, 1)
        data = None
        if(self.datasource == 'fred'):
            data = self.fred.get_series(self.indicator)
            # data = self.fred.get_series(self.indicator,start_date,end_date)
            if(self.denominator != None):
                data = data / self.fred.get_series(self.denominator)
                # data = data / self.fred.get_series(self.denominator,start_date,end_date)
            if(self.is_percentage):
                data = data * 100
        elif(self.datasource == 'dbnomics'):
            data = dbnomics.fetch_series(
                provider_code=self.provider,
                dataset_code=self.indicator,
            )
            data=data[['original_period','value']]
            #make date the index
            data['date'] = pd.to_datetime(data['original_period'])
            data.set_index('date', inplace=True)
            #filter by date
            data = data[['value']]
            #this is for the sake of testing the correlation with historical data as i dont have archive of pmi and nmi
            if(self.indicator=="pmi"):
                #append the historic data
                data = pd.concat([historic_pmi_df,data])
            elif(self.indicator=="nm-pmi"):
                #append the historic data
                data = pd.concat([historic_nmi_df,data])
        elif(self.datasource == 'fxempire'):
            #get data from fxempire
            data = self._get_from_fxempire()
        else:
            print('Data source not supported')
            return
        # data = data.loc[start_date:end_date]
        self.df = pd.DataFrame(data, columns=['value'])
        self.df.dropna(inplace=True)
        self.df['date'] = pd.to_datetime(self.df.index)
        self.df.set_index('date', inplace=True)
        if(self.frequency == 'M'):
            self.convert_to_monthly()
        elif (self.frequency == 'Y'):
            self.df = self.df.resample('Y').mean()
            self.df.dropna(inplace=True)
        elif (self.frequency == 'W'):
            self.df = self.df.resample('W').mean()
            self.df.dropna(inplace=True)
        elif (self.frequency == 'Q'):
            self.df = self.df.resample('Q').mean()
            self.df.dropna(inplace=True)
        if(self.score_based_on != 'yoy' and self.score_based_on != 'mom'):
            return;

        #if Quarterly data, calculate change from previous year
        if(self.score_based_on == 'yoy'):
            yoy=self.df['value']
            if(self.frequency == 'Q'):
                yoy = self.df['value'].pct_change(4) * 100
            elif (self.frequency == 'M'):
                yoy = self.df['value'].pct_change(12) * 100
            else:
                return
            self.df['yoy'] = yoy
            self.df['yoy'] = self.df['yoy'].round(2)
            self.df.dropna(inplace=True)
        elif(self.score_based_on == 'mom'):     
            mom=self.df['value']
            # if(self.frequency == 'M'):
            mom = self.df['value'].pct_change(1) * 100
            # else:
            #     return
            self.df['mom'] = mom
            self.df['mom'] = self.df['mom'].round(2)
            self.df.dropna(inplace=True)


    def to_csv(self):
        name = self.indicator
        #remove / from name
        name = name.replace('/','_')
        self.df.to_csv('US/' +name + '.csv')

    def fit_ets(self,forcast_duration=1):
        print("LAST DATE",self.df[self.score_based_on].isna().sum())

        # model_es = ExponentialSmoothing(self.df[self.score_based_on], trend='add', seasonal='add', seasonal_periods=12)
        model_es = ExponentialSmoothing(self.df[self.score_based_on], trend='add')
        model_fit_es = model_es.fit()
        forecast_es = model_fit_es.forecast(steps=forcast_duration)
        last_date = self.df.index[-1]
        forecast_index = pd.date_range(start=last_date, periods=forcast_duration+1, freq=self.frequency)[1:]
        # Set the date range as the index of the forecast
        forecast_es.index = forecast_index
        forecast_es.name = self.score_based_on

        return pd.DataFrame(forecast_es)
    
    def fit_sarimax(self,forcast_duration=2):
        model_sarimax = SARIMAX(self.df[self.score_based_on], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        model_fit_sarimax = model_sarimax.fit(disp=False)
        forecast_sarimax = model_fit_sarimax.forecast(steps=forcast_duration)
        last_date = self.df.index[-1]
        forecast_index = pd.date_range(start=last_date, periods=forcast_duration+1, freq=self.frequency)[1:]

        # Set the date range as the index of the forecast
        forecast_sarimax.index = forecast_index
        #change head name to match the forecast_es
        forecast_sarimax.name = self.score_based_on
        return pd.DataFrame(forecast_sarimax)
    
    def calculate_score(self):
        self.df['score'] = self.df[self.score_based_on].apply(self.__calculate_score)
            

    def __calculate_score(self, yoy):
        for i, threshold in enumerate(self.thresholds):
            if yoy >= threshold:
                return -self.scores[i] if self.is_negative else self.scores[i]
        return -self.scores[-1] if self.is_negative else self.scores[-1]  # return -10 if yoy is less than -1.5

    def convert_to_monthly(self):
        self.df = self.df.resample('M').mean()
        self.df.dropna(inplace=True)

    def get_latest_record(self):
        return self.df.iloc[-1]
    
    def get_previous_record(self):
        return self.df.iloc[-2]
    
    def calculate_score_for(self,_df):
        _df['score'] = _df[self.score_based_on].apply(self.__calculate_score)
        return _df

    def get_score_forcast(self,forcast_duration=2):
        # forecast = self.fit_ets(forcast_duration)
        forecast = self.fit_sarimax(forcast_duration)
        forecast = self.calculate_score_for(forecast)
        return forecast
    
    def get_latest_according_to_date(self, date):
        # print(date,self.indicator)
        # print(self.df)
        if self.frequency == 'Y':
            data = self.df.loc[self.df.index.year <= date.year].sort_index()
            return data.asof(date) if not data.empty else None
        elif self.frequency == 'Q':
            data = self.df.loc[(self.df.index.year < date.year) | 
                            ((self.df.index.year == date.year) & (self.df.index.quarter <= date.quarter))].sort_index()
            return data.asof(date) if not data.empty else None
        elif self.frequency == 'M':
            data = self.df.loc[(self.df.index.year < date.year) | 
                            ((self.df.index.year == date.year) & (self.df.index.month <= date.month))].sort_index()
            return data.asof(date) if not data.empty else None
        else:
            return None
        
    #private function to scrape data from fxempire
    def _get_from_fxempire(self):
        #api request
        # data= requests.get(f"https://www.fxempire.com/api/v1/en/macro-indicators/{country}/{data}/history?latest=100000")
        #add mozilla as user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        data= requests.get(f"https://www.fxempire.com/api/v1/en/macro-indicators/{self.country}/{self.indicator}/history?latest=10000000000000000",headers=headers)

        #convert to json
        data = data.json()
        #convert to dataframe
        #in there you will find attributes close, make it as value,and timestamp as date and index of dataframe
        data = pd.DataFrame(data)
        try:
            if data['close'].empty:
                return
            data['value'] = data['close']
            data['date'] = pd.to_datetime(data['timestamp'],unit='s')
            data.set_index('date',inplace=True)
            data = data[['value']]
            return data
        except KeyError as e:
            print(f"KeyError: {e}. The DataFrame may not have the expected columns.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

