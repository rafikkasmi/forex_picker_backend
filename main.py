from flask import Flask, request, jsonify, make_response,render_template
from flask_sqlalchemy import SQLAlchemy
from database import db, init_app
from os import environ
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')  or "mysql+pymysql://root:0000@localhost:3306/a1trading"
# or "sqlite:///example.db"

init_app(app)

from models.models import Indicator, IndicatorsData
with app.app_context(): 
    db.create_all()


# from routes.users import user_routes

# app.register_blueprint(user_routes)


    
from data.edgefinder_economies.US import USA
from data.edgefinder_economies.Japan import JPY
from data.edgefinder_economies.Europe import EUR
from data.edgefinder_economies.Australia import AUD
from data.edgefinder_economies.UK import GBP
from data.edgefinder_economies.Suisse import CHF
from data.edgefinder_economies.Canada import CAD
from data.edgefinder_economies.NewZealand import NZD


import yfinance as yf
from data.cot_indicator import COTIndicator,SeasonalityIndicator,TrendIndicator
from data.edgefinder_instance import EdgeFinderInstance

@app.route('/')
def home():

    usd_inflation_negative,usd_inflation_negative_cot,usd_inflation_negative_seasonality,usd_inflation_negative_trend =USA()
    usd,usd_cot,usd_seasonality,usd_trend =USA(inverse_inflation=False)
    eur,eur_cot, eur_seasonality,eur_trend =EUR(inverse_inflation=False)
    jpy,jpy_cot,jpy_seasonality,jpy_trend =JPY(inverse_inflation=False)
    chf,chf_cot =CHF(inverse_inflation=False)
    cad,cad_cot =CAD(inverse_inflation=False)
    gbp,gbp_cot =GBP(inverse_inflation=False)
    nzd,nzd_cot =NZD(inverse_inflation=False)
    aud,aud_cot =AUD(inverse_inflation=False)


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

    gbpInstance= EdgeFinderInstance('gbp',indicators=gbp,cot=gbp_cot)
    gbpInstance.calcuate_scores()
    

    usdInflationNegativeInstance= EdgeFinderInstance('usd_without_inflation',indicators=usd_inflation_negative,cot=usd_inflation_negative_cot)
    usdInflationNegativeInstance.calcuate_scores()

    #create eurusd instance
    eurusdInstance= EdgeFinderInstance('eurusd',indicators=eur,cot=eur_cot)
    eurusdInstance.calcuate_scores()
    eurusdInstance.cross_with_instance(usdInstance)
    eurusdSeasonality=SeasonalityIndicator('EURUSD=X')
    eurusdTrend=TrendIndicator('EURUSD=X')
    eurusdInstance.add_seasonality_score(eurusdSeasonality)
    eurusdInstance.add_trend_score(eurusdTrend)
    #create eurjpy
    eurjpyInstance= EdgeFinderInstance('eurjpy',indicators=eur,cot=eur_cot)
    eurjpyInstance.calcuate_scores()
    eurjpyInstance.cross_with_instance(jpyInstance)
    eurjpySeasonality=SeasonalityIndicator('EURJPY=X')
    eurjpyTrend=TrendIndicator('EURJPY=X')
    eurjpyInstance.add_seasonality_score(eurjpySeasonality)
    eurjpyInstance.add_trend_score(eurjpyTrend)

    #create eurchf
    eurchfInstance= EdgeFinderInstance('eurchf',indicators=eur,cot=eur_cot)
    eurchfInstance.calcuate_scores()
    eurchfInstance.cross_with_instance(chfInstance)
    eurchfSeasonality=SeasonalityIndicator('EURCHF=X')
    eurchfTrend=TrendIndicator('EURCHF=X')
    eurchfInstance.add_seasonality_score(eurchfSeasonality)
    eurchfInstance.add_trend_score(eurchfTrend)

    #usdjpy
    usdjpyInstance= EdgeFinderInstance('usdjpy',indicators=usd,cot=usd_cot)
    usdjpyInstance.calcuate_scores()
    usdjpyInstance.cross_with_instance(jpyInstance)
    usdjpySeasonality=SeasonalityIndicator('JPY=X')
    usdjpyTrend=TrendIndicator('JPY=X')
    usdjpyInstance.add_seasonality_score(usdjpySeasonality)
    usdjpyInstance.add_trend_score(usdjpyTrend)

    #usdchf
    usdchfInstance= EdgeFinderInstance('usdchf',indicators=usd,cot=usd_cot)
    usdchfInstance.calcuate_scores()
    usdchfInstance.cross_with_instance(chfInstance)
    usdchfSeasonality=SeasonalityIndicator('CHF=X')
    usdchfTrend=TrendIndicator('CHF=X')
    usdchfInstance.add_seasonality_score(usdchfSeasonality)
    usdchfInstance.add_trend_score(usdchfTrend)

    #usdcad
    usdcadInstance= EdgeFinderInstance('usdcad',indicators=usd,cot=usd_cot)
    usdcadInstance.calcuate_scores()
    usdcadInstance.cross_with_instance(cadInstance)
    usdcadSeasonality=SeasonalityIndicator('CAD=X')
    usdcadTrend=TrendIndicator('CAD=X')
    usdcadInstance.add_seasonality_score(usdcadSeasonality)
    usdcadInstance.add_trend_score(usdcadTrend)

    #gbpusd
    gbpusdInstance= EdgeFinderInstance('gbpusd',indicators=gbp,cot=gbp_cot)
    gbpusdInstance.calcuate_scores()
    gbpusdInstance.cross_with_instance(usdInstance)
    gbpusdInstance.add_seasonality_score(SeasonalityIndicator('GBPUSD=X'))
    gbpusdInstance.add_trend_score(TrendIndicator('GBPUSD=X'))

    #gbpjpy
    gbpjpyInstance= EdgeFinderInstance('gbpjpy',indicators=gbp,cot=gbp_cot)
    gbpjpyInstance.calcuate_scores()
    gbpjpyInstance.cross_with_instance(jpyInstance)
    gbpjpyInstance.add_seasonality_score(SeasonalityIndicator('GBPJPY=X'))
    gbpjpyInstance.add_trend_score(TrendIndicator('GBPJPY=X'))

    #gbpchf
    gbpchfInstance= EdgeFinderInstance('gbpchf',indicators=gbp,cot=gbp_cot)
    gbpchfInstance.calcuate_scores()
    gbpchfInstance.cross_with_instance(chfInstance)
    gbpchfInstance.add_seasonality_score(SeasonalityIndicator('GBPCHF=X'))
    gbpchfInstance.add_trend_score(TrendIndicator('GBPCHF=X'))

    #gbpcad
    gbpcadInstance= EdgeFinderInstance('gbpcad',indicators=gbp,cot=gbp_cot)
    gbpcadInstance.calcuate_scores()
    gbpcadInstance.cross_with_instance(cadInstance)
    gbpcadInstance.add_seasonality_score(SeasonalityIndicator('GBPCAD=X'))
    gbpcadInstance.add_trend_score(TrendIndicator('GBPCAD=X'))

    #nzdusd
    nzdusdInstance= EdgeFinderInstance('nzdusd',indicators=nzd,cot=nzd_cot)
    nzdusdInstance.calcuate_scores()
    nzdusdInstance.cross_with_instance(usdInstance)
    nzdusdInstance.add_seasonality_score(SeasonalityIndicator('NZDUSD=X'))
    nzdusdInstance.add_trend_score(TrendIndicator('NZDUSD=X'))

    #nzdjpy
    nzdjpyInstance= EdgeFinderInstance('nzdjpy',indicators=nzd,cot=nzd_cot)
    nzdjpyInstance.calcuate_scores()
    nzdjpyInstance.cross_with_instance(jpyInstance)
    nzdjpyInstance.add_seasonality_score(SeasonalityIndicator('NZDJPY=X'))
    nzdjpyInstance.add_trend_score(TrendIndicator('NZDJPY=X'))


    #audusd
    audusdInstance= EdgeFinderInstance('audusd',indicators=aud,cot=aud_cot)
    audusdInstance.calcuate_scores()
    audusdInstance.cross_with_instance(usdInstance)
    audusdInstance.add_seasonality_score(SeasonalityIndicator('AUDUSD=X'))
    audusdInstance.add_trend_score(TrendIndicator('AUDUSD=X'))

    #audjpy
    audjpyInstance= EdgeFinderInstance('audjpy',indicators=aud,cot=aud_cot)
    audjpyInstance.calcuate_scores()
    audjpyInstance.cross_with_instance(jpyInstance)
    audjpyInstance.add_seasonality_score(SeasonalityIndicator('AUDJPY=X'))
    audjpyInstance.add_trend_score(TrendIndicator('AUDJPY=X'))

    #audchf
    audchfInstance= EdgeFinderInstance('audchf',indicators=aud,cot=aud_cot)
    audchfInstance.calcuate_scores()
    audchfInstance.cross_with_instance(chfInstance)
    audchfInstance.add_seasonality_score(SeasonalityIndicator('AUDCHF=X'))
    audchfInstance.add_trend_score(TrendIndicator('AUDCHF=X'))

    #audcad
    audcadInstance= EdgeFinderInstance('audcad',indicators=aud,cot=aud_cot)
    audcadInstance.calcuate_scores()
    audcadInstance.cross_with_instance(cadInstance)
    audcadInstance.add_seasonality_score(SeasonalityIndicator('AUDCAD=X'))
    audcadInstance.add_trend_score(TrendIndicator('AUDCAD=X'))

    


    #gold
    gold_cot=COTIndicator(market='GOLD - COMMODITY EXCHANGE INC.')
    gold_cot.get_cot_data()

    goldInstance= EdgeFinderInstance('gold',indicators=[],cot=gold_cot)
    goldInstance.calcuate_scores()    
    goldInstance.cross_with_instance(usdInstance)
    xauusdSeasonality=SeasonalityIndicator('GC=F')
    xauusdTrend=TrendIndicator('GC=F')
    goldInstance.add_seasonality_score(xauusdSeasonality)
    goldInstance.add_trend_score(xauusdTrend)


    #oil
    oil_cot=COTIndicator(market='WTI FINANCIAL CRUDE OIL - NEW YORK MERCANTILE EXCHANGE')
    oil_cot.get_cot_data()
    oilInstance= EdgeFinderInstance('oil',indicators=usd_inflation_negative,cot=oil_cot)
    oilInstance.calcuate_scores()
    oilSeasonality=SeasonalityIndicator('CL=F')
    oilTrend=TrendIndicator('CL=F')
    oilInstance.add_seasonality_score(oilSeasonality)
    oilInstance.add_trend_score(oilTrend)


    #us30
    us30_cot=COTIndicator(market='DJIA Consolidated - CHICAGO BOARD OF TRADE')
    us30_cot.get_cot_data()

    us30_instance= EdgeFinderInstance('us30',indicators=usd,cot=us30_cot)
    us30_instance.calcuate_scores()

    us30_seasonality=SeasonalityIndicator('^DJI')
    us30_trend=TrendIndicator('^DJI')

    us30_instance.add_seasonality_score(us30_seasonality)
    us30_instance.add_trend_score(us30_trend)

    #nasdaq
    nasdaq_cot=COTIndicator(market='NASDAQ-100 Consolidated - CHICAGO MERCANTILE EXCHANGE')
    nasdaq_cot.get_cot_data()

    nasdaq_instance= EdgeFinderInstance('nasdaq',indicators=usd,cot=nasdaq_cot)
    nasdaq_instance.calcuate_scores()

    nasdaq_seasonality=SeasonalityIndicator('^IXIC')
    nasdaq_trend=TrendIndicator('^IXIC')

    nasdaq_instance.add_seasonality_score(nasdaq_seasonality)
    nasdaq_instance.add_trend_score(nasdaq_trend)

    #s&p500
    sp500_cot=COTIndicator(market='S&P 500 Consolidated - CHICAGO MERCANTILE EXCHANGE')
    sp500_cot.get_cot_data()

    sp500_instance= EdgeFinderInstance('sp500',indicators=usd,cot=sp500_cot)
    sp500_instance.calcuate_scores()
    
    sp500_instance.add_seasonality_score(SeasonalityIndicator('^GSPC'))
    sp500_instance.add_trend_score(TrendIndicator('^GSPC'))


    #nikkei
    # nikkei_cot=COTIndicator(market='NIKKEI STOCK AVERAGE - CHICAGO MERCANTILE EXCHANGE')
    # nikkei_cot.get_cot_data()

    # nikkei_instance= EdgeFinderInstance('nikkei',indicators=jpy,cot=nikkei_cot)

    # nikkei_instance.calcuate_scores()
    # nikkei_instance.add_seasonality_score(SeasonalityIndicator('^N225'))
    # nikkei_instance.add_trend_score(TrendIndicator('^N225'))

    all_instances=[eurusdInstance,eurjpyInstance,eurchfInstance,usdjpyInstance,usdchfInstance,usdcadInstance,gbpusdInstance,gbpjpyInstance,gbpchfInstance,gbpcadInstance,goldInstance,oilInstance,us30_instance,nasdaq_instance,sp500_instance,nzdusdInstance,nzdjpyInstance,audusdInstance,audjpyInstance,audchfInstance,audcadInstance]

    all_data_names=["inflation","core_inflation","interest_rate","gdp","services_pmi","manufacturing_pmi","retail_sales","nfp","unemployment_rate","seasonality","trend"]
    latest_scores={}
    details_scores={}

    for instance in all_instances:
        #if isnot empty and latest exists
        if len(instance.scores['total'])>0:
            latest_scores[instance.market.upper()]=instance.scores['total'].iloc[-1]
            #get all other columns beside total
            details_scores[instance.market.upper()]=instance.scores.drop(columns=['total']).iloc[-1].values



    
    print(details_scores)
    #if not empty sort by value
    if len(latest_scores)>0:
        latest_scores={k: v for k, v in sorted(latest_scores.items(), key=lambda item: item[1],reverse=True)}

    

    return render_template('index.html',latest_scores=latest_scores,details_scores=details_scores,all_data_names=all_data_names)






