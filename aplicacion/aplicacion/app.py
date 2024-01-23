#timer
from __future__ import print_function
import itertools
import time
from flask import send_file
from flask import Flask, render_template, request, current_app
from flask import url_for, redirect # para poder redirigir la pagina
from flask_bootstrap import Bootstrap

import forms; from forms import FormParametros
import funciones_Modelos; from funciones_Modelos import *
# import extract_data; from extract_data import *

import sys

#temporal luego borrar
import pandas as pd
import pickle



app = Flask(__name__)
#app.run(debug=True)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
Bootstrap(app)

#Borrar nombres_lotes y depositos
nombres_lotes = [
	"CDGD",
	"CDPI",
	"CDVM",
	"CDCAU",
	"CDLDC",
	"CDLDC3",
	"CDLDC4",
	"CDVMZPA",
	'CDPED'
]
#depositos = ["DEP01", "DEP02", "DEP03", "DEP04"]





# se setea como 'home' a 'Seleccion Parametros'
#@app.route('/')
#def inicio():
#    return render_template("inicio.html")

#@app.route('/consulta', methods=["get", "post"])
#def render_result():
#    return render_template("consulta.html")

@app.route("/result/",methods=["get"])
def result():
	return send_file('templates/salida_final.xlsx',mimetype='text/xlsx',attachment_filename='resultado_final.xlsx',as_attachment=True)

@app.route("/", methods=["get", "post"])
def index():
	return render_template('inicio.html') # Para mostrar un espera mietras se descargan los reportes

@app.route('/generar-reporte')
def generar_reporte():
	print("extraigo reporte")
	#time.sleep(8) 
	#preferences_df,sales_df,stock_df = extraer_datos_micro()
	"""
	pickle.dump(stock_df, open("data_stock_limpio_I.pickle", "wb")) 
	pickle.dump(sales_df, open("data_ov_limpio_I.pickle", "wb")) 
	pickle.dump(preferences_df, open("preferences_df_limpio_I.pickle", "wb"))
	"""
	return redirect(url_for('inicio'))

@app.route('/inicio')
def inicio():

	data_ov_I = pickle.load(open("aplicacion\\aplicacion\\datos\\data_ov_limpio_I.pickle", "rb"))
	data_stock_I= pickle.load(open("aplicacion\\aplicacion\\datos\\data_stock_limpio_I.pickle", "rb"))
	preferencias_I = pickle.load(open("aplicacion\\aplicacion\\datos\\preferences_df_limpio_I.pickle", "rb"))

	data_ov, data_stock = procesamiento_datos(preferencias_I, data_ov_I, data_stock_I)
	pickle.dump(data_ov, open("aplicacion\\aplicacion\\datos\\data_ov.pickle", "wb")) 
	pickle.dump(data_stock, open("aplicacion\\aplicacion\\datos\\data_stock.pickle", "wb")) 	


	print("STOCK ACTUAL:",data_stock["deposito"].unique())
	depositos = list(data_stock["deposito"].unique())	


	form = FormParametros(request.form)
	return render_template("seleccion_parametros.html",form = form, depositos=depositos)

@app.route("/confirmar", methods=["get", "post"])
def seleccion_parametros():
	
		#form = FormParametros(request.form)
		cantidad_depositos = int(request.form['depositos'])
		cumplimiento =  int(request.form['cumplimiento'])
		depositos_seleccionados = request.form.getlist('depositos_agregados[]')
		print("entra seleccion_parametros")
		print("cantidad_depositos:", cantidad_depositos,"tipo:",type(cantidad_depositos))
		print("porcentaje cumplimiento:", cumplimiento,"tipo:",type(cumplimiento))
		print("depositos seleccionados: ",depositos_seleccionados, "tipo:",type(depositos_seleccionados))
		data_stock = pickle.load(open("aplicacion\\aplicacion\\datos\\data_stock.pickle", "rb"))
		depositos = list(data_stock["deposito"].unique())
		#print("new_deposit:", new_deposit)
		#print("df", df_test.columns)
		print("depositos con picking",depositos_seleccionados)
		print("depositos sin picking",depositos)
		t = time.time()
		#resultado = 33
		#resultado, stock_final = main(cantidad_depositos, cumplimiento, depositos_seleccionados, depositos )
		resultado= round(resultado)
		elapsed = time.time() - t
		print("done in:",elapsed)
		return render_template("resultado.html", resultado=resultado)
		#return render_template("seleccion_parametros.html",form=form, depositos=depositos)
	
		#return render_template("error.html", error="No puedo realizar la operación")
"""
		if(cumplimiento % 1 == 0):
			time.sleep(8)
			return render_template("resultado.html", resultado=resultado)
		else:
			return render_template("seleccion_parametros.html",depositos=depositos)
	else:
		return render_template("seleccion_parametros.html",depositos=depositos)
"""


@app.errorhandler(404)
def page_not_found(error):
	return render_template("error.html", error="Página no encontrada..."), 404

app.run(debug=True)