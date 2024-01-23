#timer
from __future__ import print_function
import itertools
import time
from flask import send_file
from flask import Flask, render_template, request, current_app
from flask_bootstrap import Bootstrap
from aplicacion.forms import FormParametros
from aplicacion.funciones_Modelos import *
from aplicacion.extract_data import *

import sys
# Completar
# from ... import main

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
Bootstrap(app)

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
# se setea como 'home' a 'Seleccion Parametros'
# @app.route('/')
# def inicio():
#     return render_template("inicio.html")

# @app.route('/consulta', methods=["get", "post"])
# def render_result():
#     return render_template("consulta.html")

@app.route("/result/",methods=["get"])
def result():
	return send_file('templates/salida_final.xlsx',mimetype='text/xlsx',attachment_filename='resultado_final.xlsx',as_attachment=True)

@app.route("/", methods=["get", "post"])
def seleccion_parametros():
	form = FormParametros(request.form)
	if form.validate_on_submit():
		depositos = int(form.depositos.data)
		cumplimiento = int(form.cumplimiento.data)

		lotes = []
		c_picking, s_picking = [], []
		lotes_c_picking, lotes_s_picking = [], []

		lotes.append(form.cdgd_pick.data)
		lotes.append(form.cdpi_pick.data)
		lotes.append(form.cdvm_pick.data)
		lotes.append(form.cdcau_pick.data)
		lotes.append(form.cdldc_pick.data)
		lotes.append(form.cdldc3_pick.data)
		lotes.append(form.cdldc4_pick.data)
		lotes.append(form.cdvmzpa_pick.data)
		# agrego deposito 'CDPED'
		lotes.append(form.cdped_pick.data)

		i = 0 
		for lote in lotes:
			c_picking.append(i) if lote else s_picking.append(i)
			i += 1

		lotes_c_picking = [nombres_lotes[lote] for lote in c_picking]
		lotes_s_picking = [nombres_lotes[lote] for lote in s_picking]

		try:
			print("ready")
			t = time.time()
			timestamp_str = str(t)
			preferences_df,sales_df,stock_df = extraer_datos_micro()

			#Guardo datos en carpeta historial
			preferences_df.to_csv(f"historial_input/preferences_{timestamp_str}.csv")
			sales_df.to_csv(f"historial_input/sales_{timestamp_str}.csv")
			stock_df.to_csv(f"historial_input/stock_{timestamp_str}.csv")

			pickle.dump(stock_df, open("data_stock_limpio_I.pickle", "wb")) 
			pickle.dump(sales_df, open("data_ov_limpio_I.pickle", "wb")) 
			pickle.dump(preferences_df, open("preferences_df_limpio_I.pickle", "wb")) 

			resultado,stock_final = main(depositos, cumplimiento, lotes_c_picking, lotes_s_picking )

			resultado= round(resultado)
			elapsed = time.time() - t
			print("done in:",elapsed)
		except Exception as e:
			print('Ocurrio una Excepción:', e)
			return render_template("error.html",
								   error="No puedo realizar la operación")
		if(cumplimiento % 1 == 0):
			time.sleep(8)
			return render_template("resultado.html", resultado=resultado)
		else:
			return render_template("seleccion_parametros.html", form=form)
	else:
		return render_template("seleccion_parametros.html", form=form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="Página no encontrada..."), 404

