# Import necessaries libraries

import mstrio
import pandas as pd
import getpass
from mstrio.connection import Connection
from mstrio.project_objects import Report
from .custom_objects.reportv2 import ReportV2

import pickle

# Set variables
BASE_URL = "http://agdgdap06.agdcorp.com.ar:8080/MicroStrategyLibrary/api/"
PROJECT_ID = '626B1C35484F245187E0868090F1C506'
USR = "consultas"
PASSWORD = 'consultas'
# STOCK_ID = '2273FA8F418706C9CCDAC6986027139F'  # Stock Recomendador Warehouse Todos los Depositos
STOCK_ID = '106435304ACC54268D09FB880849EB13'  # Stock Recomendador Warehouse (Puede usar prompts)
SALES_ID = '72B9ACBB478848E8882271A652BA42BB'
PREFERENCES_ID = '247B78AD4160C83FBE1CC39BD22B4508'

def extraer_datos_micro():
	# Connect with the project
	conn = Connection(BASE_URL, USR, PASSWORD, project_id=PROJECT_ID, ssl_verify=False)
	try:
		# Get Preferences report
		preferences_report = Report(connection=conn, id=PREFERENCES_ID, parallel=False)
		preferences_df = preferences_report.to_dataframe()
		#preferences_df.head()

		# Get Sales report
		sales_report = Report(connection=conn, id=SALES_ID, parallel=False)
		sales_df = sales_report.to_dataframe()
		#sales_df.head()

		# Get Stock Report
		# stock_report = Report(connection=conn, id=STOCK_ID, parallel=False)
		stock_report = ReportV2(connection=conn, id=STOCK_ID)
		stock_df = stock_report.to_dataframe()
		#stock_df.head()
	except Exception as e:
		conn.close()
		raise
	conn.close()
	return preferences_df,sales_df,stock_df




#preferences_df,sales_df,stock_df = extraer_datos_micro()

#print(sales_df.columns)
#print(stock_df.columns)
#print(preferences_df.columns)


#data_stock, data_ov = procesamiento_datos(preferences_df, sales_df, stock_df)


#pickle.dump(stock_df, open("data_stock_limpio_I.pickle", "wb")) 
#pickle.dump(sales_df, open("data_ov_limpio_I.pickle", "wb")) 
#pickle.dump(preferences_df, open("preferences_df_limpio_I.pickle", "wb")) 




