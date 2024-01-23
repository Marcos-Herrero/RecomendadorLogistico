from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField, BooleanField, DecimalField
from wtforms.validators import DataRequired, NumberRange

depositos = [
    'CDGD',
    'CDPI',
    'CDVM',
    'CDCAU',
    'CDLDC',
    'CDLDC3',
    'CDLDC4',
    'CDVMZPA',
    'CDPED'
    ]

class FormParametros(FlaskForm):
    cumplimiento = DecimalField('Porcentaje de cumplimiento',
                                validators=[NumberRange(min=0,
                                                    max=100,
                                                    message="El valor ingresado debe estar entre 0 y 100"
                                                    ),
                                            DataRequired(),
                                ])
                                
    # cdgd_pick = BooleanField('CDGD con picking?')
    # cdpi_pick = BooleanField('CDPI con picking?')
    # cdvm_pick = BooleanField('CDVM con picking?')
    # cdcau_pick = BooleanField('CDCAU con picking?')
    # cdldc_pick = BooleanField('CDLDC con picking?')
    # cdldc3_pick = BooleanField('CDLDC3 con picking?')
    # cdldc4_pick = BooleanField('CDLDC4 con picking?')
    # cdvmzpa_pick = BooleanField('CDVMZPA con picking?')

    cdgd_pick = BooleanField('CDGD')
    cdpi_pick = BooleanField('CDPI')
    cdvm_pick = BooleanField('CDVM')
    cdcau_pick = BooleanField('CDCA')
    cdldc_pick = BooleanField('CDLDC')
    cdldc3_pick = BooleanField('CDLDC3')
    cdldc4_pick = BooleanField('CDLDC4')
    cdvmzpa_pick = BooleanField('CDVMZPA')
    cdped_pick = BooleanField('CDPED')

    depositos = SelectField("Cantidad de depósitos", choices=[(1, "1"), (2, "2")])
    submit = SubmitField('Submit')
