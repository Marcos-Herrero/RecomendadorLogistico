import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import pickle
import funciones_Modelos; from funciones_Modelos import *


def procesamiento_datos(data_pref,data_ov,data_stock):
	#data_ov.rename(columns={'Artículo@LITM': 'articulo', 'ArtÃ­culo@Descripcion': 'descripcion', 'NÂº Orden@Tipo Documento': 'to_or','Cajas Solicitadas': 'cant_orden', 'Nº Orden@Nro. Documento': 'nro_orden','Boca de entrega':'boca_de_entrega','Pallets Solicitados':'pallets_solicitados'},inplace=True)
	data_ov.columns=['to_or', 'nro_orden', 'articulo', 'descripcion','Boca de Entrega','cant_orden','pallets_solicitados']
	data_ov.columns = data_ov.columns.str.normalize('NFKD')\
					.str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower().str.replace(' ', '_')


	#print("columnas dataov:",data_ov.columns)
	#data_ov= data_ov.astype({"Boca de Entrega":"int64","articulo":"int64","nro_orden":"int64","cant_orden":"int64"}) 
	data_ov= data_ov.astype({"boca_de_entrega":"int64","articulo":"int64","nro_orden":"int64","cant_orden":"int64",'pallets_solicitados':"float64"}) 

	print(data_ov.columns)
	# tratamiento preferencia de clientes
	data_pref.rename(columns={'Boca de Entrega@Cliente (Facturación) None':'Boca de Entrega', 'Boca de Entrega@DESC' : 'Boca de Entrega DescripciÃ³n','Artículo@Cliente (Facturación) None' : 'articulo','Boca de Entrega@DESC':'nombre_del_cliente' },inplace=True)

    #data_pref = data_pref[['Boca de Entrega','articulo','nombre_del_cliente']]
	#print(data_pref.columns)

	data_pref= data_pref[['Boca de Entrega','articulo','nombre_del_cliente','Dias Mínimo']]
	data_pref= data_pref.astype({"Boca de Entrega":"int64","articulo":"int64","Dias Mínimo":"int64"})




	# ==== TRATAMIENTO DE DATOS DE ORDENES DE VENTA Y JOIN CON PREFERENCIAS DE CLIENTES====
	
	# Se selecciona el Dia minimo mas grande para cada cliente para asegurar el cumplimineto minimo

	preferencia_de_clientes = data_pref.groupby(['Boca de Entrega','nombre_del_cliente'])['Dias Mínimo'].max().reset_index()

	data_ov = pd.merge(data_ov,preferencia_de_clientes,left_on="boca_de_entrega",right_on="Boca de Entrega")

	# ====TRATAMIENTO DE STOCK ====

	
	# Limpiar nombres de columnas
	data_stock.columns= ['lote','vencimiento','vida_util','descripcion','deposito','cajas_x_pallets','articulo','cajas']
	data_stock.columns = data_stock.columns.str.normalize('NFKD')\
		.str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
	

	data_stock= data_stock.astype({"vida_util":"float64", "vencimiento":"datetime64[ns]","cajas_x_pallets":"float64","cajas":"int64",'articulo':'int64'}) 


	#data_stock = data_stock.assign(lote=lambda x: x.vencimiento.astype('str').str.replace('-', '')) # BORRAR Y USAR EL LOTE NUEVO
	
	# Limpieza de espacios en columna "deposito", en nombres de los depÃ³sitos (para evitar errores en la creaciÃ³n de las variables de decisiÃ³n)
	data_stock['deposito'] = data_stock['deposito'].str.strip()
	

	# Filtrado cuando hay 0 cajas o negativos
	data_stock = data_stock[data_stock['cajas'] > 0]
	#print(data_stock.cajas.describe())
	print(data_ov.columns)
	return data_ov,data_stock




def filtros_y_tratamiento_datos(data_ov,data_stock,lotes_a_tomar,is_picking):
	
	periodicty = 'trimestral'
	# Procesamiento de las ordenes de venta

	# Creacion atributo que determina si es con picking (1 significa que se requiere picking)
	data_ov['picking'] = np.where(data_ov['pallets_solicitados'] - data_ov['pallets_solicitados'].round(0)==0, 0, 1)
	
	if (is_picking==True):
		data_ov = data_ov[data_ov['picking']==1]
	else:
		data_ov = data_ov[data_ov['picking']==0]
	
	# ==== CREACION DE TABLA PARA CADA GRUPO DE DIA MINIMO SOLICITADO (PICKING) ====
    
	dict_de_DF_por_dias_minimos={}

	#quedan ordenadas por dias de vida  util para luego poder iterar sobre ellos  en un orden optimo
	for dias in sorted(list(data_ov['Dias Mínimo'].unique())):
		print(dias)
		aux = data_ov[data_ov['Dias Mínimo'] == dias]
		print("tamaño de ordenes con",dias,"dias:",aux.shape)
		dict_de_DF_por_dias_minimos[dias]=aux

	# Toma solo stock con depositos dados y agrega periodo
	data_stock = get_period(data_stock, periodicty)

	data_stock =data_stock[data_stock['deposito'].isin(lotes_a_tomar)]
	#print(sorted(list(data_ov['Dias Mínimo'].unique())))
	return dict_de_DF_por_dias_minimos,data_stock    