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
        start_date = datetime.datetime(2022, 10, 1)
        end_date = pd.to_datetime('today')
        self.cot.score_all()
        cot=self.cot.df.loc[start_date:end_date]
        # print(cot)

        self.scores=pd.DataFrame(index=cot.index,columns=['total'])
        all_data_names=["inflation","core_inflation","interest_rate","gdp","services_pmi","manufacturing_pmi","retail_sales","nfp","unemployment_rate"]
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
            for i,ind in enumerate(all_data_names):
                if i < len(self.indicators):
                    self.scores.loc[date,ind] = self.indicators[i].get_latest_according_to_date(date)['score']
                else:
                    self.scores.loc[date,ind] = 0


    def add_seasonality_score(self,seasonality):
        for date in self.scores.index:
            self.scores.loc[date,'total']+=seasonality.get_seasonality_score_for_month(date.month)
            self.scores.loc[date,'seasonality'] = seasonality.get_seasonality_score_for_month(date.month)
    def add_trend_score(self,trend):
        for date in self.scores.index:
            self.scores.loc[date,'total']+=trend.get_trend_score_for_date(date)
            self.scores.loc[date,'trend'] = trend.get_trend_score_for_date(date)

    def cross_with_instance(self,instance):
        if type(instance) is not EdgeFinderInstance:
            raise Exception('Instance must be of type EdgeFinderInstance')
        #if type=='default':
        all_data_names=["inflation","core_inflation","interest_rate","gdp","services_pmi","manufacturing_pmi","retail_sales","nfp","unemployment_rate"]
        for date in self.scores.index:
            if date in instance.scores.index:
                self.scores.loc[date,'total'] -= instance.scores.loc[date,'total']
                for i,ind in enumerate(instance.indicators):
                    if ind is not None:
                        self.scores.loc[date,all_data_names[i]] -= ind.get_latest_according_to_date(date)['score']
                        
        # elif type == 'forex':
        #     for date in self.scores.index:
        #         if date in instance.scores.index:
        #             #we loop through all the indicators and get the same indicator from the other instance, and compare the value
                        
                        
    def get_bullish_bearish_signals(self):
        self.scores['bullish_signal']=self.scores['total']>5
        self.scores['bearish_signal']=self.scores['total']<-5

        bullish_signals = self.scores[self.scores['bullish_signal']]
        bearish_signals = self.scores[self.scores['bearish_signal']]

        return bullish_signals,bearish_signals