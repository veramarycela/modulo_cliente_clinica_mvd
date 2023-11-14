# -*- coding: utf-8 -*-
{
    'name': "Modulo Cliente Clinica",

    'summary': """
        Este modulo sirve para registrar los clientes de la clinica""",

    'description': """
        Este modulo sirve para registrar los clientes de la clinica
    """,

    'author': "ServiTecht",
    'website': "http://www.servitecht.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
            'views/views.xml', 
            'views/views_clinica_cliente_paciente.xml',
            'security/ir.model.access.csv',
            'report/factura_clinica_reporte.xml',
            'template/factura_clinica_template.xml',
    ],
   
}
