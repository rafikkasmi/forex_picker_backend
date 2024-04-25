#get economic data and seed them into the database

from main import db,app
from models.models import Indicator, IndicatorsData,COTIndicator

from data.edgefinder_economies.US import USA
from data.edgefinder_economies.Europe import EUR
from data.edgefinder_economies.UK import GBP
from data.edgefinder_economies.Japan import JPY
from data.edgefinder_economies.Canada import CAD
from data.edgefinder_economies.Australia import AUD
from data.edgefinder_economies.NewZealand import NZD
from data.edgefinder_economies.Suisse import CHF




usd,usd_cot,usd_seasonality,usd_trend = USA()
eur,eur_cot,eur_seasonality,eur_trend = EUR()
jpy,jpy_cot,jpy_seasonality,jpy_trend = JPY()
uk,uk_cot = GBP()
cad,cad_cot = CAD()
aud,aud_cot = AUD()
nzd,nzd_cot = NZD()
chf,chf_cot = CHF()


all_currencies=[usd,eur,jpy,uk,cad,aud,nzd,chf];
all_currencies_cot=[usd_cot,eur_cot,jpy_cot,uk_cot,cad_cot,aud_cot,nzd_cot,chf_cot];
# all_currencies_cot=[aud_cot,nzd_cot,chf_cot];
all_currencies_names=["USD","EUR","JPY","UK","CAD","AUD","NZD","CHF"]
# all_currencies_names=["AUD","NZD","CHF"]

all_data_names=["inflation","core_inflation","interest_rate","gdp","services_pmi","manufacturing_pmi","retail_sales","employment-change","unemployment_rate"]

# for data_name in all_data_names:
#     new_indicator = Indicator(name=data_name,description=f"US {data_name}",country="US",frequency="M",indicator_type="economic")
#     with app.app_context():
#         db.session.add(new_indicator)
#         db.session.commit()



# print(usd)


# from data.cot_indicator import COTIndicator

import numpy as np
import pandas as pd
import math
MAX_VALUE = 1000  # replace with a suitable large number
MIN_VALUE = -1000  # replace with a suitable small number
def handle_value(x):
    if isinstance(x, pd.Series):
        return x.apply(handle_value)
    elif np.isinf(x) and x > 0:
        return 1
    elif np.isinf(x) and x < 0:
        return -1
    elif np.isnan(x):
        return None
    else:
        return x

# for i,currency_cot in enumerate(all_currencies_cot):
#     for date in currency_cot.df.index:
#         if date in currency_cot.df.index:
#             row = currency_cot.df.loc[date]
#             currency_cot.df.dropna(inplace=True)

#             new_cot = COTIndicator(
#                 date=date,
#                 asset=all_currencies_names[i],
#                 long=handle_value(row['long']),
#                 short=handle_value(row['short']),
#                 open_interest=handle_value(row['open_interest']),
#                 net=handle_value(row['net']),
#                 change_in_net=handle_value(row['change_in_net']),
#                 long_change_percentage=handle_value(row['long_change_percentage']),
#                 short_change_percentage=handle_value(row['short_change_percentage']),
#                 score=0
#             )
#             with app.app_context():
#                 db.session.add(new_cot)
#                 db.session.commit()
#         else:
#             print(f"Date {date} not found in DataFrame index.")

#     print(f"Seeded {all_currencies_names[i]} cot data")


for i,currency_elements in enumerate(all_currencies):
    #loop through all currency_elements and get name of the element
    currency_elements_names = [element.name for element in currency_elements]
    for element in currency_elements:
        data_name = element.name
        print(f"Seeding {data_name} for {all_currencies_names[i]}")
        for date in element.df.index:
            if date in element.df.index:
                row = element.df.loc[date]
                print(row)
            else:
                print(f"Date {date} not found in DataFrame index.")


