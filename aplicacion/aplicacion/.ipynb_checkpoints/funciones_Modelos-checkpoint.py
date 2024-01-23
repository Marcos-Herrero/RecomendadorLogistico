
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import pickle
import pulp as pl




from aplicacion.conexion_a_base import *
#from conexion_a_base import *

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', 100)
pd.options.display.float_format = '{:,.6f}'.format

periodicty = 'trimestral'

#from aplicacion.conexion_a_base import *
#from aplicacion.extract_data import *
# ===============================================
# LECTURA DE DATOS
# ===============================================

def get_data_sample(data_stock, data_ov, n_muestra_ov, n_muestra_prod):
	
	random_state=28
	
	# Tamaño de muestras de OV y productos
	sample_OV = pd.Series(data_ov['nro_orden'].unique()).sample(n=n_muestra_ov, random_state=random_state).values
	sample_prod = pd.Series(data_stock['articulo'].unique()).sample(n=n_muestra_prod, random_state=random_state).values

	# Muestras de OV y productos
	data_ov = data_ov[(data_ov['nro_orden'].isin(sample_OV)) & (data_ov['articulo'].isin(sample_prod))]
	data_stock = data_stock[data_stock['articulo'].isin(sample_prod)]
	
	return data_stock, data_ov


def filtering_picking_sell_orders(data_ov):
	# Flag: Ordenes de ventas que requieren picking
	data_ov['picking'] = np.where(data_ov['pallets_solicitados'] - data_ov['pallets_solicitados'].round(0)==0, 0, 1)
	
	# Filtrado de registros de ordenes de venta que requieren picking 
	data_ov = data_ov[data_ov['picking']==1]
	
	return data_ov


def data_extraction(sample=False, n_OV=30, n_prod=18):
	"""
	Lectura de datos de Stock y Ordenes de Venta y toma de muestra de datos (opcional)
	
	"""
	
	# ==== LECTURA DE DATOS DE STOCK ====
	#data_stock = pd.read_excel('../../../Data/Raw/Stock Disponible en Depositos_POC2.xlsx')
	#data_stock = pd.read_excel('../../../Data/Raw/StockDisponible_TomaMinimo_Test1.xlsx')
	#data_stock = pd.read_excel('../../../Data/Raw/StockDisponible_NoHayStockSuficiente_Test2.xlsx')
	#data_stock = pd.read_excel('../../../Data/Raw/Stock Disponible en Depósitos.xlsx')
	data_stock = pd.read_excel('../data/Raw/Stock Disponible en Depósitos.xlsx')


	
	# Limpiar nombres de columnas
	data_stock.rename(columns={'Fecha de Vencimiento': 'vencimiento', 'Dias al Vencimiento': 'vida_util', 'Cajas Disponibles': 'cajas', 'SKU': 'articulo',
						},
					inplace=True)
	data_stock.columns = data_stock.columns.str.normalize('NFKD')\
						.str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
	
	# Creación de columna "lote"
	data_stock = data_stock.assign(lote=lambda x: x.vencimiento.astype('str').str.replace('-', ''))
	
	# Limpieza de espacios en columna "deposito", en nombres de los depósitos (para evitar errores en la creación de las variables de decisión)
	data_stock['deposito'] = data_stock['deposito'].str.strip()
	
	#Eliminar filas con datos nulos
	#data_stock.dropna(axis=1, inplace=True)
	
	# ==== LECTURA DE DATOS DE ORDENES DE VENTA ====
	data_ov = pd.read_excel('../../../Data/Raw/Datos de Ordenes de Venta_POC2.xlsx')
	#data_ov = pd.read_excel('../../../Data/Raw/OrdenesDeVenta_TomaMinimo_Test1.xlsx')
	#data_ov = pd.read_excel('../../../Data/Raw/OrdenesDeVenta_NoHayStockSuficiente_Test2.xlsx')
	print(data_ov.shape)
	# Limpiar nombres de columnas
	data_ov.rename(columns={'Artículo': 'articulo', 'Unnamed: 3': 'descripcion', 'Nº Orden': 'to_or',
						'Cajas Solicitadas': 'cant_orden', 'Unnamed: 1': 'nro_orden', 
						},
				inplace=True)
	data_ov.columns = data_ov.columns.str.normalize('NFKD')\
					.str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower().str.replace(' ', '_')
	#print(data_stock.shape)
	# Filtrado de registros de ordenes de venta que requieren picking  
	data_ov = filtering_picking_sell_orders(data_ov) # MODIFICA GENERAR DOS ORDENES DE VENTA UNA CON PCIKING Y OTRA SIN PICKING
	print(data_ov.shape)
	# Filtrado de stock solo tomando articulos que van a ser pedidos por las OV
	#print(data_stock.shape)
	sample_prod= data_stock['articulo'].unique() 
	#print(data_stock.shape)
	#data_stock = data_stock[(data_stock['articulo'].isin(sample_prod)) & (data_stock['articulo'].isin(data_ov['articulo'].unique()))] # rompia pq tenia distos tipos
	data_stock=data_stock[(data_stock['articulo'].isin(sample_prod)) & (data_stock['articulo'].isin(data_ov['articulo'].astype(str).unique()))]
	#print(data_stock.shape)
	if sample:
		# CREAR UNA MUESTRA DE DATOS
		data_stock, data_ov = get_data_sample(data_stock, data_ov, n_OV, n_prod)
	print(data_ov.shape)
	return data_stock, data_ov


def data_extraction_(sheet_name_stock='Stock 11-06', sheet_name_OV='Ordenes de Venta 11-06', sample=False, n_OV=30, n_prod=18):
	"""
	Lectura de datos de Stock y Ordenes de Venta y toma de muestra de datos (opcional)
	
	"""
	
	# LECTURA DE DATOS DE STOCK
	data_stock = pd.read_excel('Stock_OV_AGD.xlsx', sheet_name=sheet_name_stock)
	data_stock = data_stock.assign(vida_util=lambda x: (x.vencimiento - today)/timedelta(days=1))
	data_stock['vida_util'] = round(data_stock['vida_util'], 0)
	# Limpiar nombres de columnas
	data_stock.columns = data_stock.columns.str.normalize('NFKD')\
						.str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()

	# LECTURA DE DATOS DE ORDENES DE VENTA
	data_ov = pd.read_excel('Stock_OV_AGD.xlsx', sheet_name=sheet_name_OV)
	data_ov.rename(columns={'2º número de artículo': 'articulo', 'Nº de la orden': 'nro_orden',
							'Suma de Cantidad Ordenada': 'cant_orden'}, inplace=True)

	if sample:
		# CREAR UNA MUESTRA DE DATOS
		data_stock, data_ov = get_data_sample(data_stock, data_ov, n_OV, n_prod)
		
	return data_stock, data_ov








# =====================
# Depuración de datos
# =====================

# Stock por Vencer
def get_stock_to_expire(data_stock):
	return data_stock[data_stock['vida_util']<120]


# Depuración data de inventario
def get_depurated_stock(data_stock):
	data_stock = data_stock[data_stock['cajas'] > 0]   # El valor negativo curarlo o eliminarlo??

	# Para no emplear productos con menos de 120 de vida útil, se elimina estos regsitros
	#data_stock = data_stock[data_stock['vida_util']>=120]
	
	return data_stock








# =====================
## Feature Engineering
# =====================

def get_period(data_stock, periodicty):
	
#     if periodicty == 'quincenal':
#         data_stock = data_stock.assign(periodo=lambda x: x.vencimiento.dt.year.astype('str') + '-' + x.vencimiento.dt.month.astype('str'))
	if periodicty == 'mensual':
		data_stock = data_stock.assign(periodo=lambda x: x.vencimiento.dt.year.astype('str') + '-' + x.vencimiento.dt.month.astype('str'))
	elif periodicty == 'bimestral':
		data_stock = data_stock.assign(periodo=lambda x: x.vencimiento.dt.year.astype('str') + '-' + (np.ceil(x.vencimiento.dt.month/2)).astype('int').astype('str'))
	# Trimestres de vencimiento
	elif periodicty == 'trimestral':    
		data_stock = data_stock.assign(periodo=lambda x: x.vencimiento.dt.year.astype('str') + '-' + x.vencimiento.dt.quarter.astype('str'))
	
	return data_stock


### Valores únicos
def unique_valuesF(data_stock, data_ov):
	
	# Depósitos
	id_depositos = data_stock['deposito'].unique()

	# Articulos o productos
	id_productos = sorted(data_stock['articulo'].unique())

	# Ordenes de venta
	id_ov = sorted(data_ov['nro_orden'].unique())

	# Periodos
	periodos = sorted(data_stock['periodo'].unique())
	
	unique_values = {
					'id_depositos': id_depositos, 
					'id_productos': id_productos,
					'id_ov': id_ov, 
					'periodos': periodos
	}
	
	return unique_values


# Cantidades de valores únicos
def number_of_categories(data_stock, data_ov):
	
	# Depósitos
	n_depositos = data_stock['deposito'].nunique()

	# Articulos o productos
	n_articulos = data_stock['articulo'].nunique()

	# Ordenes de venta
	n_ordenes = data_ov['nro_orden'].nunique()

	# Periodos
	n_periodos = data_stock['periodo'].nunique()
	
	number_of_categories = {
					'n_depositos': n_depositos, 
					'n_productos': n_articulos, 
					'n_ordenes': n_ordenes, 
					'n_periodos': n_periodos
	}
	
	return number_of_categories


### Cantidad por Grupos-stock: trimestres vs depósito
def get_ovstock_group_quantity(data_stock, unique_values):
	
	df_gstock = data_stock.groupby(['articulo', 'deposito', 'periodo']).agg({'cajas': np.sum})
	df_gstock = df_gstock.reindex(pd.MultiIndex.from_product([unique_values['id_productos'],
															unique_values['id_depositos'],
															unique_values['periodos'],  
															], 
															),               
								fill_value=0, 
								)
	
	return df_gstock


### Cálculo de vida útil
def get_useful_life(data_stock, unique_values):
	# Vida útil promedio para cada trimestre por depósito
	vu_periodo = (1/data_stock.groupby(['deposito', 'periodo']).agg({'vida_util': np.mean})).round(5)

	vu_periodo = vu_periodo.reindex(pd.MultiIndex.from_product([unique_values['id_depositos'],
																unique_values['periodos']  
															], 
															)
								)
	vu_periodo = vu_periodo.assign(GStock=['_'.join(vu_periodo.index[i]) for i in range(len(vu_periodo))]).fillna(0)
	
	return vu_periodo


### COSTOS: Vida útil por productoXgstock
def get_stock_ov_group_usefullife(vu_periodo, unique_values):
	dicc_OVProdXGrupoStock = {f"{periodo}_{prod}_{ov}": vu for periodo, vu in zip(vu_periodo['GStock'],
																				vu_periodo['vida_util'])\
							for ov in unique_values['id_ov']
							for prod in unique_values['id_productos']

						}  # round(vu[0], 6)

	df_OVProdXGrupoStock = pd.Series(dicc_OVProdXGrupoStock)
	
	return df_OVProdXGrupoStock





# ======================
# Variables de Decisión 
# ======================

# Variables de Decisión Enteras
def get_decision_variables_and_costs(df_OVProdXGrupoStock):
	
	# Lista de Variables de Decisión (formato: xxxx_xxxx_x_xxxxxxxxxx_xxxxxx, codDeposito_año_trimestre_codArticulo_codOV)
	ov_variable_names = df_OVProdXGrupoStock.index
	
	# Creación de Lista de Variables de Decisión: discretas, con restricción de no negatividad
	decision_variables = [pl.LpVariable(ov_variable_names[i], 
								cat = pl.LpInteger,  #"Integer", 
								lowBound = 0) for i in range(len(ov_variable_names))]
	
	# Vector de costos
	costs = df_OVProdXGrupoStock.values
	
	return decision_variables, costs


# Construcción de la Matriz de las Variables de Decision 
def get_decision_variables_matrix(n_categ, decision_variables):
	
	# Dimensión de la Matriz de Variables de Decision (Orden: n_dep x n_periodos x n_ov x n_productos)  ##[dep][periodos][ov]
	dim_matrix = n_categ['n_depositos'], n_categ['n_periodos'], n_categ['n_ordenes'], n_categ['n_productos']

	# Matriz de Variables de Decision
	DV_matrix = np.reshape(np.array(decision_variables), dim_matrix)
	
	return DV_matrix

# Variables de Decisión Binarias
def get_binary_decision_variables(n_categ):
	
	# Construir los subindices de las variables de decisión (esto será un proceso dinámico que se ajusta a los depósitos que contengan el dataset)
	bin_var_matrix_dim = (n_categ['n_ordenes'], n_categ['n_depositos'])  # Indices: comb: OV-depósito)
	bin_var_index = [f"{i}_{j}" for i in list(range(1, bin_var_matrix_dim[0] + 1)) for j in range(1, bin_var_matrix_dim[1]+1)]
	# print("Variable Indices:", bin_var_index)

	# Creación de matriz de variables binarias (dimensión: n_comb x n_muestra_prod)
	bin_var_matrix = pl.LpVariable.matrix("Y", bin_var_index, cat = "Integer", lowBound = 0 , upBound=1)
	bin_var_matrix = np.array(bin_var_matrix).reshape(bin_var_matrix_dim)
	# print("Variables Binarias/Matriz de asignación:\n", bin_var_matrix)
	
	return bin_var_matrix







# ==============================
# Construcción de Restricciones
# ==============================

# Adicionar restricciones de cantidad de depósitos
def add_warehouses_quantity_restriction(optimizacion_model, bin_var_matrix, rest_dep=1):

	for idx, lista_bin in enumerate(bin_var_matrix):
		# Contrucción de inecuaciones de restricciones de cantidad de depósitos
		#print(idx, lista_bin)
		#print("lista_bin",lista_bin)
		#print(type(lista_bin))
		#print(len(lista_bin))
		#print(type(lista_bin[0]))

		ineq = pl.lpSum(var for var in lista_bin) <= rest_dep
#         print(ineq, end='\n\n')
		# Agregar al modelo las inecuaciones de restricciones: armar pedidos empleando stock de a lo sumo 2 depositos
		optimizacion_model += (ineq, f"Restricción de {rest_dep} depósito {idx}")
	
	return optimizacion_model


# Adicionar restricciones de cantidades de Producto/OVs
def add_products_quantity_restriction_per_sell_order(optimizacion_model, data_ov, unique_values, n_categ, DV_matrix, bin_var_matrix):
	# Valores limites para la Restricciones de cantidad de articulo por OV
	df_restr_Prod_OV = data_ov.groupby(['articulo',
									'nro_orden'])\
					.agg({'cant_orden': 'sum'}).reindex(pd.MultiIndex.from_product([unique_values['id_productos'],
																					unique_values['id_ov'],
																					],

																				),
														fill_value=0,
														)
	restr_Prod_OV = df_restr_Prod_OV.values
	
	# Agregar al modelo las inecuaciones de restricciones máximas de Ordenes de Venta:  ##[prod][ov][dep]
	i = 0
	for prod in range(n_categ['n_productos']):  # producto
		cont_ov = 0
		for ov in range(n_categ['n_ordenes']):  # ov
			lista_var = [DV_matrix[dep][periodo][ov][prod] for periodo in range(n_categ['n_periodos']) for dep in range(n_categ['n_depositos'])]
			ineq = pl.lpSum(var for var in lista_var) <= restr_Prod_OV[i]
			#ineq = pl.lpSum(var for var in lista_var) > restr_Prod_OV[i] * valor%
			#ineq = pl.lpSum(var for var in lista_var) == restr_Prod_OV[i]

			i += 1
			cont_ov += 1
#             print(ineq, end='\n\n')
			optimizacion_model += (ineq, "Restricciones de cantidad ProdXOV Total " + str(i))
		
		
	# Agregar al modelo las inecuaciones de restricciones máximas de productos por orden de venta:  ##[dep][periodos][ov][prod]
	i = 0
	for dep in range(n_categ['n_depositos']):  # deposito
		j = 0
		for prod in range(n_categ['n_productos']):  # producto
			cont_ov = 0
			for ov in range(n_categ['n_ordenes']):  # ov
				i += 1
				lista_var = [DV_matrix[dep][period][ov][prod] for period in range(n_categ['n_periodos'])]
				ineq = pl.lpSum(var for var in lista_var) <= restr_Prod_OV[j]*bin_var_matrix[cont_ov][dep]
				#ineq = pl.lpSum(var for var in lista_var) == restr_Prod_OV[j]*bin_var_matrix[cont_ov][dep]
				j += 1
				cont_ov += 1
#                 print(ineq, end='\n\n')
				optimizacion_model += (ineq, "Restricciones de ProdXOV por Depósito " + str(i))
	
	return optimizacion_model


# Adicionar restricciones de cantidad de Inventario (Producto/Grupo-stock)
def add_stock_group_quantity_restriction_per_product(optimizacion_model, df_gstock, unique_values, n_categ, vu_periodo, DV_matrix):
	
	id_GStock = vu_periodo['GStock'].values
	
	df_restr_total_ProdGStock = df_gstock.copy() 
	df_restr_total_ProdGStock = df_restr_total_ProdGStock.assign(GStock=['_'.join(df_restr_total_ProdGStock.index[i][1:]) for i in range(len(df_restr_total_ProdGStock))])
	df_restr_total_ProdGStock.reset_index(inplace=True)
	df_restr_total_ProdGStock = df_restr_total_ProdGStock.set_index(['level_0', 'GStock'])[['cajas']]
	df_restr_total_ProdGStock = df_restr_total_ProdGStock.reindex(pd.MultiIndex.from_product([unique_values['id_productos'], 
																							id_GStock],
																							),
																)
	restr_total_ProdGStock = df_restr_total_ProdGStock.values
	
	# Inecuaciones de producto/grupo de stock
	cont = 0   ##[dep][periodo][ov][prod] --> periodo-dep-prod+ov
	for prod in range(n_categ['n_productos']):
		for dep in range(n_categ['n_depositos']): 
			for periodo in range(n_categ['n_periodos']):
				lista_var = [DV_matrix[dep][periodo][ov][prod] for ov in range(n_categ['n_ordenes'])]
				ineq = pl.lpSum(var for var in lista_var) <= restr_total_ProdGStock[cont]
#                 print(ineq, end='\n\n')
				cont += 1
				optimizacion_model += (ineq, "Restricciones de G-Stock" + str(cont))
	
	return optimizacion_model






# =================================================================
# Construcción del Modelo de Optimización y Obtención de Solución
# =================================================================
def get_optimizacion_model(decision_variables, costs, rest_dep=1):
	
	print(data_ov.head()) 
	# Instanciar tipo de problema de optimización como Maximización
	optimizacion_model = pl.LpProblem(name = "Supply-SellOrden-Problem",
							sense = pl.LpMaximize)   
	# Construcción de la F.O.
	obj_func = pl.lpSum(decision_variables*costs)
	
	optimizacion_model += obj_func
	
	#==================================
	# Adicionar restricciones al modelo
	#==================================
	# Adicionar restricciones de cantidad de depósitos
	optimizacion_model = add_warehouses_quantity_restriction(optimizacion_model, bin_var_matrix, rest_dep)
	
	# Adicionar restricciones de cantidades de Producto/OVs
	optimizacion_model = add_products_quantity_restriction_per_sell_order(optimizacion_model, data_ov, unique_values, n_categ, DV_matrix, bin_var_matrix)

	# Adicionar restricciones de cantidad de Inventario (Producto/Grupo-stock)
	optimizacion_model = add_stock_group_quantity_restriction_per_product(optimizacion_model, df_gstock, unique_values, n_categ, vu_periodo, DV_matrix)

	# Obtención de la solución de optimización
	solver_e = pl.getSolver('COIN_CMD')
	optimizacion_model.solve(solver_e)

	# Status de la solución (Optimal, Not Solved, Infeasible, Unbounded, Undefined)
	status = pl.LpStatus[optimizacion_model.status]
	if status == 'Optimal':
		print(f'Se obtuvo una SOLUCIÓN ÓPTIMA, con {optimizacion_model.numVariables()} variables de decisión')
		
		# Llamar a la función de obtención de tablas de salida
		### AGREGAR LLAMADA A LA FUNCIÓN
		
	else:
		print(f'NO se obtuvo una SOLUCIÓN ÓPTIMA. El status de solución es {status}. \n¡Revisar código fuente!')
	
	return optimizacion_model









# =================================================================
# Capa de algoritmos greedy: Se encarga de encotrar los lotes con menor vida util (a nivel dia)
# =================================================================
def greedyAlg(newStock,Cantidad):

	acum=0
	sol= {}
	while acum <Cantidad: 
		
		vidaUtilMin=newStock.iloc[0]
		lote = newStock.iloc[0].lote
		cantCajas = newStock.iloc[0].cajas
		acum = acum + cantCajas

		if acum<Cantidad:
			sol[lote]=cantCajas
			newStock= newStock.iloc[1: , :]
			continue
		elif acum==Cantidad:
			sol[lote]=cantCajas
			newStock= newStock.iloc[1: , :]
			break
		else:
			cantidadNecesaria = Cantidad-(acum -cantCajas)
			sol[lote]=cantidadNecesaria
			newStock.loc[newStock.lote==lote,"cajas"]= cantCajas-cantidadNecesaria 
			break

	   
	return [newStock,sol]




def updateSalida(aux,solLotesCant,nOV):
	for lote, cantidad in solLotesCant.items():
		aux.loc[aux.Lote==lote, nOV]=cantidad

	return aux




def GetLotesXArtPerDep(aux, newStock, solDict):
	
	salida= pd.DataFrame()
	for NordenVenta, cantidad in solDict.items():

		aux[NordenVenta] = 0
		
		if cantidad==0:
			continue
		else:
			res = greedyAlg(newStock,cantidad)
			newStock = res[0] #chequear
			salida=updateSalida(aux,res[1],NordenVenta)

	return salida




def CapaGreedy(data_stock,OVsalidaCapaPL):

	salida = pd.DataFrame(columns=OVsalidaCapaPL.columns)

	for i in range(len(OVsalidaCapaPL)):


		grupo = OVsalidaCapaPL.iloc[i]

		deposito = grupo.Deposito
		periodo = grupo.Periodo
		articulo = grupo.Articulo

		newStock =  data_stock[(data_stock.articulo==articulo) & (data_stock.deposito==deposito) & (data_stock.cajas>0) & (data_stock.periodo==periodo) ][['lote','vida_util','cajas']]
		newStock=newStock.set_index('vida_util').sort_index(ascending=True)

		longitud = newStock.lote.shape[0]

		aux= pd.DataFrame( {"Deposito": [deposito]*longitud, "Periodo" : [periodo]*longitud, "Articulo": [articulo]*longitud, "Lote":newStock.lote})
		  
		ordenesDict= grupo.iloc[3:-1].to_dict() #quito las primeras 3 columanas y la ultuma para quedarme solo con OVs cant

		aux = GetLotesXArtPerDep(aux, newStock, ordenesDict)

		salida= pd.concat([salida,aux])

	return salida, newStock








# =================================================================
# PERFORMANCE
# =================================================================

#puedo entregar a partir de 120 dias

def performance(data_stock):

	Vence10Dias = data_stock.query('vida_util<130').sum()
	Vence30Dias = data_stock.query('vida_util<150').sum()
	Vence90Dias = data_stock.query('vida_util<210').sum()
	Vence180Dias = data_stock.query('vida_util<300').sum()

	print(Vence10Dias)
	print(Vence30Dias)
	print(Vence90Dias)
	print(Vence180Dias)

	return 0

def performance_antes_desp(data_stock,data_stock_N):

	Vence10Dias = data_stock.query('vida_util<130').sum()['cajas']
	Vence30Dias = data_stock.query('vida_util<150').sum()['cajas']
	Vence90Dias = data_stock.query('vida_util<210').sum()['cajas']
	Vence180Dias = data_stock.query('vida_util<300').sum()['cajas']
	

	Vence10DiasN = data_stock_N.query('vida_util<130').sum()['cajas']
	Vence30DiasN = data_stock_N.query('vida_util<150').sum()['cajas']
	Vence90DiasN = data_stock_N.query('vida_util<210').sum()['cajas']
	Vence180DiasN = data_stock_N.query('vida_util<300').sum()['cajas']

	print(" Articulos con 10 dias a vencer :",Vence10Dias)
	print(" Articulos con 30 dias a vencer :",Vence30Dias)
	print(" Articulos con 90 dias a vencer :",Vence90Dias)
	print(" Articulos con 10 dias a vencer :",Vence180Dias)
	
    
	#print(" Articulos con 10 dias a vencer se redujeron a un:",Vence10DiasN/Vence10Dias*100)
	#print(" Articulos con 30 dias a vencer se redujeron a un:",Vence30DiasN/Vence30Dias*100)
	#print(" Articulos con 90 dias a vencer se redujeron a un:",Vence90DiasN/Vence90Dias*100)
	#print(" Articulos con 10 dias a vencer se redujeron a un:",Vence180DiasN/Vence180Dias*100)
	if Vence10Dias==0:
		p1=0
	else:	
		p1=round(Vence10DiasN/Vence10Dias*100)
	p2=round(Vence30DiasN/Vence30Dias*100)
	p3=round(Vence90DiasN/Vence90Dias*100)
	p4=round(Vence180DiasN/Vence180Dias*100)
	
	
	return p1,p2,p3,p4

	


def porcentaje_ordenes_completadas(data_ov,solucion):

	cantidad_OV = data_ov.nro_orden.nunique()

	cantida_OV_completadas = solucion.nro_orden.nunique()

	return cantida_OV_completadas/cantidad_OV*100








def unique_valuesF(data_stock, data_ov):
	#print("test1")
	
	# Depósitos
	id_depositos = data_stock['deposito'].unique()

	# Articulos o productos
	id_productos = sorted(data_stock['articulo'].unique())

	# Ordenes de venta
	id_ov = sorted(data_ov['nro_orden'].unique())

	# Periodos
	periodos = sorted(data_stock['periodo'].unique())
	
	unique_values = {
					'id_depositos': id_depositos, 
					'id_productos': id_productos,
					'id_ov': id_ov, 
					'periodos': periodos
	}
	
	return unique_values






# =================================================================
# Construcción del Modelo de Optimización y Obtención de Solución
# =================================================================
def get_optimizacion_model_new(data_ov,unique_values,n_categ,vu_periodo, decision_variables, costs, rest_dep=1):
	
	#print(data_ov.head()) 
	# Instanciar tipo de problema de optimización como Maximización
	optimizacion_model = pl.LpProblem(name = "Supply-SellOrden-Problem",
							sense = pl.LpMaximize)   
	# Construcción de la F.O.
	obj_func = pl.lpSum(decision_variables*costs)
	
	optimizacion_model += obj_func
	
	#==================================
	# Adicionar restricciones al modelo
	#==================================
	# Adicionar restricciones de cantidad de depósitos
	optimizacion_model = add_warehouses_quantity_restriction(optimizacion_model, bin_var_matrix, rest_dep)
	
	# Adicionar restricciones de cantidades de Producto/OVs
	optimizacion_model = add_products_quantity_restriction_per_sell_order(optimizacion_model, data_ov, unique_values, n_categ, DV_matrix, bin_var_matrix)

	# Adicionar restricciones de cantidad de Inventario (Producto/Grupo-stock)
	optimizacion_model = add_stock_group_quantity_restriction_per_product(optimizacion_model, df_gstock, unique_values, n_categ, vu_periodo, DV_matrix)

	# Obtención de la solución de optimización
	solver_e = pl.getSolver('COIN_CMD')
	optimizacion_model.solve(solver_e)

	# Status de la solución (Optimal, Not Solved, Infeasible, Unbounded, Undefined)
	status = pl.LpStatus[optimizacion_model.status]
	if status == 'Optimal':
		print(f'Se obtuvo una SOLUCIÓN ÓPTIMA, con {optimizacion_model.numVariables()} variables de decisión')
		
		# Llamar a la función de obtención de tablas de salida
		### AGREGAR LLAMADA A LA FUNCIÓN
		
	else:
		print(f'NO se obtuvo una SOLUCIÓN ÓPTIMA. El status de solución es {status}. \n¡Revisar código fuente!')
	
	return optimizacion_model

# =================================================================
# FUNCIONES PRINCIPALES
# =================================================================

# =================================================================
# ALGORITMO PRINCIPAL: Toma las ordenes de venta, la tabla de stock,
# de cuantos depositos se puede despachar cada orden y el porcentaje minimo de cumplimiento
# Se le aplica el modelo de programacion lineal y luego un algoritmo greddy. 
# retorna una tabla donde indica de donde despachar cada producto para cada cliente ( indicando lote, deposito, )
# =================================================================



def extraccion_datos(depositos,is_picking):

	# usar depositos y es picking para filtrar ordenes de venta y stock HACER
	data_stock = pickle.load(open("data/data_stock_limpio.pickle", "rb"))
	data_stock=get_depurated_stock(data_stock)
	data_stock.articulo = pd.to_numeric(data_stock.articulo)

	data_ov = pickle.load(open("data/OV_por_grupo_dia_minimo.pickle", "rb"))


	return data_ov,data_stock





# divide un dataframe en grupos de tamaños mas pequeños 
def make_reduced_groups(data_ov,nro_elms_grupo):
    NUMERO_MAXIMOS_ELEMENTOS = nro_elms_grupo

    
    list_salidas = []


    lista_nro_ordenes_de_venta = data_ov.nro_orden.unique()

    aux = pd.DataFrame(columns=data_ov.columns)
    cont = 0
    for i in lista_nro_ordenes_de_venta:

        df_cliente = data_ov[data_ov['nro_orden']==i]
        if (cont <NUMERO_MAXIMOS_ELEMENTOS):
            aux = pd.concat([aux,df_cliente])
            cont = cont + df_cliente.shape[0]
        else:    
            list_salidas.append(aux)
            aux = df_cliente 
            cont = df_cliente.shape[0]
    list_salidas.append(aux)        
    return list_salidas

def algoritmo_principal(data_ov, data_stock, cant_depositos, cumplimiento):
	salida_vacia= pd.DataFrame(
    {"Deposito":[],
    "Periodo":[],
    "Articulo":[],
    "Lote":[],
    "nro_orden":[],
    "cantidad_a_despachar":[]})
######################### BORAR################
	#data_ov.pop(120)

###############################################	

	soluciones =[] # vamos a guardar la solucion para cada grupo de vida util pretendido
	new_stock =data_stock # se arranca con todo el stock

	#print("STOCK ACTUAL:",new_stock.deposito.unique())
	for i in data_ov:

		print("grupo:",i)
		print("CANTIDAD DE ORDENES A COMPLETAR:",data_ov[i]['nro_orden'].nunique())


		lista_grupos_reducidos = make_reduced_groups(data_ov[i],30)
		print("Cantidad de subgrupos:",len(lista_grupos_reducidos))
		for grupo_df in lista_grupos_reducidos:


			#tiempo_minimo_de_vida = ordenes_de_venta_picking[i]
			stock_para_grupo = new_stock[new_stock['vida_util'] >= i ] 
			sample_prod= stock_para_grupo['articulo'].unique() 
			#print(sample_prod)
			#print(stock_para_grupo[(stock_para_grupo['articulo'].isin(data_ov[i]['articulo'].unique()))].shape)
			stock_para_grupo=stock_para_grupo[(stock_para_grupo['articulo'].isin(sample_prod)) & (stock_para_grupo['articulo'].isin(grupo_df['articulo'].unique()))] 
		
			print("Stock actual:",stock_para_grupo.shape)
			#print(stock_para_grupo.shape)
			#print(stock_para_grupo.columns)
			#print(data_ov[i])
			size_grupo_stock,_=stock_para_grupo.shape
			if size_grupo_stock ==0:
				continue


			#break	
			#print(stock_para_grupo)
			new_stock1, solucion = apply_lp_greedy_model(stock_para_grupo, grupo_df, cant_depositos, cumplimiento)



			#chequeo si la solucion es vacia
			#print("SOLUCION:",solucion.head())
			print(solucion.shape)
			solucion_size,_= solucion.shape
			if solucion_size <1:
				print("Solucion vacia")
				continue

			multi = solucion.set_index(['Deposito', 'Periodo', 'Articulo', 'Lote'])
			final = multi.stack().to_frame().reset_index()
			#print(final.columns)
			final.columns=['Deposito','Periodo','Articulo','Lote','nro_orden','cantidad_a_despachar']
			#print(final.columns)
			#print(final.info())
			final=final[final['cantidad_a_despachar']>0]
			#print("TEST SALIDA STOCKS")
			#print(final.columns)
			#print(stock_para_grupo.info())
			final_x_lote=final.groupby(['Deposito','Lote','Articulo']).sum().reset_index()
			# ACTUALZIACION DEL STOCK
			#print(final_x_lote.columns)
			#print(new_stock.columns)
			new_stock= pd.merge(new_stock,final_x_lote,how ='left',left_on=['deposito','articulo','lote'], right_on = ['Deposito','Articulo','Lote',])
			new_stock['cantidad_a_despachar'] = new_stock['cantidad_a_despachar'].fillna(0)
			new_stock['cajas']=new_stock['cajas'] - new_stock['cantidad_a_despachar']
			#print("Nombre columnas:",new_stock.columns)
			
			#new_stock=new_stock.drop([ 'Deposito', 'Periodo', 'Articulo', 'Lote', 'nro_orden', 'cantidad_a_despachar'],axis=1)
			#new_stock=new_stock.drop([ 'Deposito', 'Lote','Articulo', 'cantidad_a_despachar'],axis=1)
			new_stock= new_stock[ ['deposito', 'articulo', 'descripcion', 'lote', 'vencimiento','vida_util', 'cajas_x_pallets', 'cajas', 'periodo']]
			#print("Nombre columnas:",new_stock.columns)
			
			new_stock=new_stock.query('cajas>0')


			soluciones.append(final)
			
			#print("Nombre columnas:",new_stock.columns)
			#break
			
	print("Cantidad de soluciones",len(soluciones))	
	if len(soluciones)>0:
		df= pd.concat(soluciones)
	else:
		df = salida_vacia
	#df.columns=['Deposito','Periodo','Articulo','Lote','nro_orden','cantidad_a_despachar']
	#df=df[df['cantidad_a_despachar']>0]
	#df.to_excel('tabla_final1.xlsx') 
	#print("salida",df)
	print("ORDENES COMPLEATADAS",df.nro_orden.nunique())
	#print("STOCK ANTES DE IR AL MAIN",new_stock.columns)
	return new_stock, df

	

def main(cant_depositos, cumplimiento, lotes_c_picking, lotes_s_picking ):

	#data_ov = pickle.load(open("data_ov_limpio.pickle", "rb"))
	#data_stock= pickle.load(open("data_stock_limpio.pickle", "rb"))

	#data_ov= data_ov.astype({"boca_de_entrega":"int64","articulo":"int64","nro_orden":"int64","cant_orden":"int64"}) 
	#data_ov= data_ov.astype({"Boca de Entrega":"int64","articulo":"int64",})
	#data_stock= data_stock.astype({"vida_util":"float64", "vencimiento":"datetime64[ns]","cajas_x_pallets":"float64","cajas":"int64"})
	data_ov_I = pickle.load(open("data_ov_limpio_I.pickle", "rb"))
	data_stock_I= pickle.load(open("data_stock_limpio_I.pickle", "rb"))
	preferencias_I = pickle.load(open("preferences_df_limpio_I.pickle", "rb"))
	
	
	

	data_ov, data_stock = procesamiento_datos(preferencias_I, data_ov_I, data_stock_I)
	try:
		data_ov_c_picking,data_stock_c_picking = filtros_y_tratamiento_datos(data_ov,data_stock,lotes_c_picking,True)
	except Exception as e:
		print(e)

	print("procesamiento ordenes con picking")
	
	try:
		newstock, salida_c_picking = algoritmo_principal(data_ov_c_picking, data_stock_c_picking, cant_depositos, cumplimiento)
	except Exception as e:
		print(e)

	# Tratamiento ordenes con picking
	data_ov_s_picking,data_stock_s_picking = filtros_y_tratamiento_datos(data_ov,data_stock,lotes_s_picking,False)


	#Agrego el stock de picking al de no picking
	data_stock_s_picking=pd.concat([data_stock_s_picking,newstock])
	#############
	print("procesamiento ordenes SIN picking")
	newstock,salida_s_picking = algoritmo_principal(data_ov_s_picking,data_stock_s_picking, cant_depositos, cumplimiento)


	salida = pd.concat([salida_c_picking,salida_s_picking])
	#salida=salida_c_picking # borrar - solo prueba
	
	#return salida
	#send_data()
	#salida=salida.rename(columns={'level_4':'nro_orden','0':'cantidad_a_despachar'})
	#print(data_ov.nro_orden.nunique())
	#print(salida.nro_orden.nunique())
	metrica_porcentaje_ordenes_completadas=porcentaje_ordenes_completadas(data_ov,salida)
	p1,p2,p3,p4 = performance_antes_desp(data_stock,newstock)


	#ENVIO DE DATOS

	fecha = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
	parametros= str({'depositos':cant_depositos,'cumplimiento':cumplimiento,'lotes_c_picking':lotes_c_picking,'lotes_s_picking':lotes_s_picking})
	salidas = str({'metrica_porcentaje_ordenes_completadas':metrica_porcentaje_ordenes_completadas,'Vence10DiasN':p1,'Vence30DiasN':p2,'Vence90DiasN':p3,'Vence180DiasN':p4})
	metricasLog = {'fecha_rec':[fecha],'parametros': [parametros],'salidas': [salidas]}
	metricasLog = pd.DataFrame(data=metricasLog)
	#print(salidas)
	#print(metricasLog)
	#print(salida.columns, data_stock.columns, data_ov.columns)
	salida_base=formato_datos(salida,data_stock,data_ov)
	envio_datos(salida_base,metricasLog)
	salida_base.reindex(columns=['orden_de_venta','articulo_id','articulo_desc','deposito','lote','cantidad_a_despachar','vida_util','cliente_id','nombre_del_cliente','fecha_rec']).reset_index(drop=True).to_excel('./templates/salida_final.xlsx',index=False)
	#print(type(parametros))
	#print(salidas)
	salida=salida.drop_duplicates()
	salida.to_excel('tabla_final1.xlsx') 
	return metrica_porcentaje_ordenes_completadas,newstock
	# ADAPTACION DE SALIDA




	



def filtros_y_tratamiento_datos(data_ov,data_stock,lotes_a_tomar,is_picking):
	
	periodicty = 'trimestral'
	# Procesamiento de las ordenes de venta

	# Creacion atributo que determina si es con picking (1 significa que se requiere picking)
	data_ov['picking'] = np.where(data_ov['pallets_solicitados'] - data_ov['pallets_solicitados'].round(0)==0, 0, 1)
	aux = data_ov.groupby(by=['nro_orden']).max()['picking']
	aux = aux.reset_index()
	data_ov = data_ov.drop(columns=['picking'])
	data_ov = pd.merge(data_ov,aux,left_on="nro_orden",right_on="nro_orden")
	
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

	return dict_de_DF_por_dias_minimos,data_stock





def apply_lp_greedy_model(data_stock, data_ov,rest_dep, porcentaje_cumplimiento):

	salida_vacia= pd.DataFrame(
    {"Deposito":[],
    "Periodo":[],
    "Articulo":[],
    "Lote":[],
    "nro_orden":[],
    "cantidad_a_despachar":[]})

	global df_gstock, DV_matrix, bin_var_matrix, split_bin
	

	n_categ = number_of_categories(data_stock, data_ov)
	unique_values = unique_valuesF(data_stock, data_ov)

	
	df_gstock = get_ovstock_group_quantity(data_stock, unique_values)


	vu_periodo = get_useful_life(data_stock, unique_values)

	df_OVProdXGrupoStock = get_stock_ov_group_usefullife(vu_periodo, unique_values)

	decision_variables, costs = get_decision_variables_and_costs(df_OVProdXGrupoStock)

	DV_matrix = get_decision_variables_matrix(n_categ, decision_variables)

	bin_var_matrix = get_binary_decision_variables(n_categ)

	optimizacion_model = get_optimizacion_model_new(data_ov,unique_values,n_categ,vu_periodo, decision_variables, costs, rest_dep=rest_dep)
	#%%time
	optimizacion_model.solve()

	status = pl.LpStatus[optimizacion_model.status]

	#print(status)

	print("capa PL con exito, numero de varibles:")
	print(optimizacion_model.numVariables())

	# CONVERSION DE SOLUCION A DF CON FORMATO ADECUADO PARA SER PROCESADO POR CAPA GREEDY

	solution_PL = pd.Series({solution.name: solution.value() for solution in optimizacion_model.variables()}, 
							name='cantidad').dropna()
	solution_PL = solution_PL.astype('int')
	split = solution_PL.index.str.split('_')
	n_total = int(n_categ['n_depositos']*n_categ['n_ordenes']*n_categ['n_productos']*n_categ['n_periodos'])
	split_DV = split[:n_total]
	split_bin = split[n_total:]
	df_optimal_solution = solution_PL[:n_total].to_frame()

	df_optimal_solution = df_optimal_solution.assign(deposito = [sp[0] for sp in split_DV])
	df_optimal_solution = df_optimal_solution.assign(periodo = ['-'.join(sp[1:3]) for sp in split_DV])
	df_optimal_solution = df_optimal_solution.assign(articulo = [sp[3] for sp in split_DV])
	df_optimal_solution = df_optimal_solution.assign(nro_orden = [sp[4] for sp in split_DV])

	solution_table = pd.pivot_table(df_optimal_solution, values='cantidad', 
									index=['deposito', 'periodo', 'articulo'], 
									columns='nro_orden', aggfunc='sum')


	# RESTRICCION DE PORCENTAJE MINIMO DE CUMPLIMIENTO   

	CatidadesEsperadas=data_ov.groupby('nro_orden')['cant_orden'].agg('sum').reset_index()

	CatidadesPredichas = solution_table.sum().reset_index()
	CatidadesPredichas.columns=['nro_orden','cantidadPredicha']
	CatidadesPredichas=CatidadesPredichas.astype({'nro_orden':'int'})

	OV_PedidasCumplidas=pd.merge(left=CatidadesEsperadas,right=CatidadesPredichas)
	OV_PedidasCumplidas['porcentaje']= OV_PedidasCumplidas.cantidadPredicha/OV_PedidasCumplidas.cant_orden*100

	# Existe el caso donde no se puede completar ninguna orden en un grupo de vida util minima
	ordenesCompletas=OV_PedidasCumplidas[OV_PedidasCumplidas['porcentaje'] >= porcentaje_cumplimiento ]['nro_orden']

	print("ORDENES COMPLETAS:")

	n=len(ordenesCompletas)
	print(n)
	if n==0:
		print("NO TENGO PEDIDOS PARA ARMAR")
		return data_stock, salida_vacia
  

	solution_table_filtrado=solution_table[ordenesCompletas.apply(str)]

	with pd.ExcelWriter(f'Auxiliar.xlsx') as writer: solution_table_filtrado.to_excel(writer, sheet_name='Solución Óptima')
	OVsalidaCapaPL = pd.read_excel('Auxiliar.xlsx')


	# CAPA DE ALGORITMOS GREEDY

	OVsalidaCapaPL.deposito = pd.Series(OVsalidaCapaPL.deposito).fillna(method='ffill')
	OVsalidaCapaPL.periodo = pd.Series(OVsalidaCapaPL.periodo).fillna(method='ffill')
	OVsalidaCapaPL.rename(columns={'deposito': 'Deposito', 'periodo': 'Periodo', 'articulo': 'Articulo' },inplace=True)
	OVsalidaCapaPL['Lote']='NaN'

	solucion_final_nivel_lote, final_stock = CapaGreedy(data_stock,OVsalidaCapaPL)


	return final_stock, solucion_final_nivel_lote



def procesamiento_datos(data_pref,data_ov,data_stock):
	print('entro procesamiento datos')
	data_ov.rename(columns={"Nº Orden@Tipo Documento":'to_or',"Nº Orden@Nro. Documento": 'nro_orden',"Boca de entrega":'Boca de Entrega', "Artículo@LITM":'articulo',"Artículo@Descripcion": 'descripcion',"Cajas Solicitadas":'cant_orden',"Pallets Solicitados":'pallets_solicitados'},inplace=True)
	#data_ov.columns=['to_or', 'nro_orden','Boca de Entrega', 'articulo', 'descripcion','cant_orden','pallets_solicitados']
	data_ov.columns = data_ov.columns.str.normalize('NFKD')\
					.str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower().str.replace(' ', '_')


	#print("columnas dataov:",data_ov.columns)
	#data_ov= data_ov.astype({"Boca de Entrega":"int64","articulo":"int64","nro_orden":"int64","cant_orden":"int64"}) 
	data_ov= data_ov.astype({"boca_de_entrega":"int64","articulo":"int64","nro_orden":"int64","cant_orden":"int64",'pallets_solicitados':"float64"}) 
	print('data_pref to excel')
	try:
		data_pref.to_excel('data_pref_antes_rename.xlsx')
	except Exception as e:
		print(e)
	# tratamiento preferencia de clientes
	data_pref.rename(columns={'Boca de Entrega@Cliente (Facturación) None':'Boca de Entrega', 'Boca de Entrega@DESC' : 'Boca de Entrega Descripción','Artículo@Cliente (Facturación) None' : 'articulo','Boca de Entrega@DESC':'nombre_del_cliente' },inplace=True)

    #data_pref = data_pref[['Boca de Entrega','articulo','nombre_del_cliente']]
	#print(data_pref.columns)

	data_pref= data_pref[['Boca de Entrega','articulo','nombre_del_cliente','Dias Mínimo']]
	data_pref= data_pref.astype({"Boca de Entrega":"int64","articulo":"int64","Dias Mínimo":"int64"})

	data_ov.to_excel('data_ov_antes.xlsx')
	data_pref.to_excel('data_pre_antes.xlsx')


	# ==== TRATAMIENTO DE DATOS DE ORDENES DE VENTA Y JOIN CON PREFERENCIAS DE CLIENTES====
	
	# Se selecciona el Dia minimo mas grande para cada cliente para asegurar el cumplimineto minimo

	#preferencia_de_clientes = data_pref.groupby(['Boca de Entrega','nombre_del_cliente'])['Dias Mínimo'].max().reset_index()

	#data_ov = pd.merge(data_ov,preferencia_de_clientes,left_on="boca_de_entrega",right_on="Boca de Entrega")
	# UPDATE Se selecciona el Día minimo mas grande tomando en cuenta los productos de cada cliente para cada orden de venta
	preferencia_de_clientes= pd.merge(data_ov,data_pref,left_on=['boca_de_entrega','articulo'], right_on=['Boca de Entrega','articulo'],how='left')
	preferencia_de_clientes= preferencia_de_clientes[['boca_de_entrega','nombre_del_cliente','nro_orden','articulo','Dias Mínimo']]
	preferencia_de_clientes = preferencia_de_clientes.groupby(['boca_de_entrega','nombre_del_cliente','nro_orden','articulo'])['Dias Mínimo'].max().reset_index()
	data_ov = pd.merge(data_ov,preferencia_de_clientes,left_on=['boca_de_entrega','nro_orden','articulo'],right_on=['boca_de_entrega','nro_orden','articulo'])
	data_ov['Dias Mínimo'] = data_ov['Dias Mínimo'].fillna(120)

	print('pref', preferencia_de_clientes.columns)
	print('DataOV',data_ov.columns)

	# ====TRATAMIENTO DE STOCK ====

	
	# Limpiar nombres de columnas
	data_stock.rename(columns={"SKU":'articulo',"Descripción":'descripcion',"cajas_x_pallets":'cajas_x_pallets',"Depósito Padre":'deposito',"Dias al Vencimiento":'vida_util',"Lote":'lote',"Fecha de Vencimiento":'vencimiento',"Cajas Disponibles":'cajas'},inplace=True)
	#data_stock.columns=['deposito','cajas_x_pallets','articulo','lote','vencimiento','descripcion','vida_util','cajas']
	data_stock.columns = data_stock.columns.str.normalize('NFKD')\
		.str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
	

	data_stock= data_stock.astype({"vida_util":"float64", "vencimiento":"datetime64[ns]","cajas_x_pallets":"float64","cajas":"int64","articulo":"int64"}) 


	#data_stock = data_stock.assign(lote=lambda x: x.vencimiento.astype('str').str.replace('-', '')) # BORRAR Y USAR EL LOTE NUEVO
	
	# Limpieza de espacios en columna "deposito", en nombres de los depÃ³sitos (para evitar errores en la creaciÃ³n de las variables de decisiÃ³n)
	data_stock['deposito'] = data_stock['deposito'].str.strip()
	

	# Filtrado cuando hay 0 cajas o negativos
	data_stock = data_stock[data_stock['cajas'] > 0]
	#print(data_stock.cajas.describe())
	#print(data_ov.columns)
	#print(data_stock.columns)
	print('salio proc datos')
	return data_ov,data_stock





