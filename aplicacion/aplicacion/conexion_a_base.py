import pymssql

import pandas as pd



# ---- COMPLETAR ----
server =  "172.30.0.63"
port = "1065"
database = 'DWCORP'
username = 'proc'
password = 'proc'


#---- SOLO DE PRUEBA ----
from datetime import datetime
 

 
date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
 

d = {'orden_de_venta': ['123'], 'articulo_id': [3], 'deposito': ['GG'], 'lote': ['2022-2'], 'cantidad_a_despachar': [100],'vida_util': [30],'cliente_id': ['8'],'nombre_del_cliente': ['cat'], 'articulo_desc':['aceite'],'fecha_rec':[date]}
df = pd.DataFrame(data=d)


d2 = {'fecha_rec':[date],'parametros': ['test'],'salidas': ['test']}
df2 = pd.DataFrame(data=d2)

print(df2)



def formato_datos(salida,data_stock,data_ov):
	fecha = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
	tabla_final=salida.drop(['Periodo'],axis=1)
	aux= data_stock[['articulo','lote','deposito','vida_util','descripcion']]



	tabla_final = pd.merge(tabla_final,aux,how ='left',left_on=['Articulo','Lote','Deposito'], right_on = ['articulo','lote','deposito'])
	tabla_final=tabla_final.drop(['Deposito','Articulo','Lote'],axis=1)

	aux2=data_ov[['nro_orden','boca_de_entrega','articulo','nombre_del_cliente']]
	aux2['nro_orden']=aux2['nro_orden'].astype(str)

	tabla_final = pd.merge(tabla_final,aux2,how ='left',left_on=['nro_orden','articulo'], right_on = ['nro_orden','articulo'])

	tabla_final=tabla_final[ ['articulo','lote','deposito','nro_orden','cantidad_a_despachar','vida_util','descripcion','boca_de_entrega','nombre_del_cliente']]
	tabla_final['fecha_rec']= fecha
	#tabla_final['nombre_del_cliente']="AGD"

	tabla_final=tabla_final.rename(columns={'nro_orden':'orden_de_venta','articulo':'articulo_id','boca_de_entrega':'cliente_id','descripcion':'articulo_desc'})
	
	tabla_final=tabla_final.drop_duplicates()

	return tabla_final


def envio_datos(salida,metricas):

	#SALIDA

	#cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
	cnxn = pymssql.connect(server=server, port=port, user=username, password=password, database=database)
	cursor = cnxn.cursor()
	print(cnxn)

	#borramos la informacion que tenia esta tabla
	#cursor.execute("TRUNCATE TABLE DWCORP.dbo.H0_LYD_RECOMENDADOR_LOGISTICA")
	#print("done")

	# Insertamos el dataFrame
	# tener en cuenta que los primeros nombres de las variables corresponden a la tabla de sql-Server y  los segundos a las del dataframe

	for index, row in salida.iterrows():
		cursor.execute("INSERT INTO  DWCORP.dbo.H0_LYD_RECOMENDADOR_LOGISTICA (orden_de_venta, articulo_id,deposito,lote, cantidad_a_despachar,vida_util,cliente_id,nombre_del_cliente,articulo_desc,fecha_rec) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(row.orden_de_venta, row.articulo_id, row.deposito, row.lote, row.cantidad_a_despachar, row.vida_util, row.cliente_id, row.nombre_del_cliente, row.articulo_desc, row.fecha_rec))

	# METRICAS

	for index, row in metricas.iterrows():
		cursor.execute("INSERT INTO  DWCORP.dbo.H0_LYD_RECOMENDADOR_LOGISTICA_LOG (fecha_rec, parametros, salidas) values(%s,%s,%s)",(row.fecha_rec, row.parametros, row.salidas))

	cnxn.commit()
	cnxn.close()

	print("Los datos se enviaron con exito a la base de datos")



