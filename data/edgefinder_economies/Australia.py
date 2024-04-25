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


#example aud data
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import datetime
import pandas as pd
from economic_indicator import EconomicIndicator
from cot_indicator import COTIndicator,SeasonalityIndicator,TrendIndicator

country = 'australia'

def AUD(inverse_inflation=True):
    #scoring of edge finder is build this way :
    #get inflation data (cpi, core cpi)
    inflation = EconomicIndicator('monthly-cpi-indicator', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country=country,datasource='fxempire',frequency='M',is_negative=inverse_inflation,name="inflation")
    inflation.get_data()
    inflation.calculate_score()

    core_inflation = EconomicIndicator('core-inflation-rate', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country=country,datasource='fxempire',frequency='Q',is_negative=inverse_inflation,name="core-inflation")
    core_inflation.get_data()
    core_inflation.calculate_score()
    print(core_inflation.df)

    # core_inflation = get_from_fxempire(country,'core-inflation-rate')

    #get interest rates
    interest_rate = EconomicIndicator('interest-rate', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country=country,datasource='fxempire',frequency='M',is_negative=True,  name="interest-rate")
    interest_rate.get_data()
    interest_rate.calculate_score()

    #get gdp
    # gdp = get_from_fxempire(country,'gdp-growth-rate')
    gdp = EconomicIndicator('gdp-growth-rate', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country=country,datasource='fxempire',name="gdp-rate")
    gdp.get_data()
    gdp.calculate_score()

    #get services pmi
    services_pmi = EconomicIndicator('services-pmi', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country=country,datasource='fxempire',frequency='M',name="services-pmi")
    services_pmi.get_data()
    services_pmi.calculate_score()

    #get manufacturing pmi (ism)
    # manufacturing_pmi = EconomicIndicator('manufacturing-pmi', 
    manufacturing_pmi = EconomicIndicator('business-confidence', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country=country,datasource='fxempire',frequency='M',name="manufacturing-pmi")
    manufacturing_pmi.get_data()
    manufacturing_pmi.calculate_score()

    #get retail sales
    retail_sales = EconomicIndicator('retail-sales-mom', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country=country,datasource='fxempire',frequency='M',name="retail-sales")
    retail_sales.get_data()
    retail_sales.calculate_score()

    #get employment change
    nfp =  EconomicIndicator('employment-change', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country=country,datasource='fxempire',frequency='M',name="employment-change")
    nfp.get_data()
    nfp.calculate_score()
    # nfp = get_from_fxempire(country,'employment-change')

    #get unemployment rate
    unemployment_rate =  EconomicIndicator('unemployment-rate', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country=country,datasource='fxempire',frequency='M',is_negative=True,name="unemployment-rate")
    unemployment_rate.get_data()
    unemployment_rate.calculate_score()


    aud_cot=COTIndicator(market='AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE')
    aud_cot.get_cot_data()
    aud_cot.to_csv()
 
    
    aud=[inflation,core_inflation,interest_rate,gdp,services_pmi,manufacturing_pmi,retail_sales,nfp,unemployment_rate]

    # aud_instance=EdgeFinderInstance(market='aud',indicators=aud,cot=aud_cot,seasonality=aud_seasonality,trend_reading=aud_trend)
    return aud,aud_cot

