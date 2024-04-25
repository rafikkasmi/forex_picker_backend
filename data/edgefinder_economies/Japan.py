#example jpy data
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import datetime
import pandas as pd
from economic_indicator import EconomicIndicator
from cot_indicator import COTIndicator,SeasonalityIndicator,TrendIndicator


def JPY(inverse_inflation=True):


    #inflation
    jpy_inflation = EconomicIndicator('inflation-rate', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country='japan',datasource='fxempire',frequency='M',is_negative=inverse_inflation,name="inflation")
    jpy_inflation.get_data()
    jpy_inflation.calculate_score()

    #core inflation
    jpy_core_inflation = EconomicIndicator('core-inflation-rate', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country='japan',datasource='fxempire',frequency='M',is_negative=inverse_inflation,name="core-inflation")
    jpy_core_inflation.get_data()
    jpy_core_inflation.calculate_score()


    #interest rate
    jpy_interest_rate = EconomicIndicator('interest-rate', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country='japan',datasource='fxempire',frequency='M',is_negative=True,name="interest-rate")
    jpy_interest_rate.get_data()
    jpy_interest_rate.calculate_score()

    #gdp
    jpy_gdp = EconomicIndicator('gdp-growth-rate', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country='japan',datasource='fxempire',name="gdp-rate")
    jpy_gdp.get_data()
    jpy_gdp.calculate_score()

    #services pmi
    jpy_services_pmi = EconomicIndicator('services-pmi', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country='japan',datasource='fxempire',frequency='M',   name="services-pmi")
    jpy_services_pmi.get_data()
    jpy_services_pmi.calculate_score()

    #manufacturing pmi
    jpy_manufacturing_pmi = EconomicIndicator('manufacturing-pmi', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country='japan',datasource='fxempire',frequency='M',name="manufacturing-pmi")
    jpy_manufacturing_pmi.get_data()
    jpy_manufacturing_pmi.calculate_score()

    #retail sales
    jpy_retail_sales = EconomicIndicator('retail-sales-mom', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country='japan',datasource='fxempire',frequency='M',name="retail-sales")
    jpy_retail_sales.get_data()
    jpy_retail_sales.calculate_score()

    #employment change
    jpy_nfp =  EconomicIndicator('employment-rate', 
                                    [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country='japan',datasource='fxempire',frequency='M',name="employment-change")
    jpy_nfp.get_data()
    jpy_nfp.calculate_score()

    #unemployment rate
    jpy_unemployment_rate =  EconomicIndicator('unemployment-rate', 
            [0.01,0,-0.01],
                                    [1,  0, -1],score_based_on="mom",country='japan',datasource='fxempire',frequency='M',is_negative=True,name="unemployment-rate")
    jpy_unemployment_rate.get_data()
    jpy_unemployment_rate.calculate_score()

    jpy=[jpy_inflation,jpy_core_inflation,jpy_interest_rate,jpy_gdp,jpy_services_pmi,jpy_manufacturing_pmi,jpy_retail_sales,jpy_nfp,jpy_unemployment_rate]

    jpy_cot=COTIndicator(market='JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE')
    jpy_cot.get_cot_data()

    jpy_seasonality= SeasonalityIndicator("^SPJPYFP")

    jpy_trend= TrendIndicator("^SPJPYFP")

    jpy=[jpy_inflation,jpy_core_inflation,jpy_interest_rate,jpy_gdp,jpy_services_pmi,jpy_manufacturing_pmi,jpy_retail_sales,jpy_nfp,jpy_unemployment_rate]

    # jpy_instance=EdgeFinderInstance(market='jpy',indicators=jpy,cot=jpy_cot,seasonality=jpy_seasonality,trend_reading=jpy_trend)
    return jpy,jpy_cot,jpy_seasonality,jpy_trend

