# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Masrof Platform',
    'version' : '1.0',
    'summary': '',
    'sequence': 10,
    'description': """

    """,
    'category': 'Sales',
    'depends': ['base','point_of_sale'],
    'data': [
       'security/account_security.xml',
       'security/ir.model.access.csv',
       'views/ir_sequence_data.xml',
       'views/ewallet_view.xml',
       'views/res_partner_view.xml',
       'views/transactions_view.xml',
       'views/pos_order_view.xml',
       'views/school_view.xml',
       'views/wallet_operations.xml',
       'views/education_administration.xml',
       'views/contract_view.xml',
       'views/add_action_template.xml',
       'data/e_wallet_data.xml',
       'views/wallet_template_transation.xml',
       'views/platform_view.xml',
       'views/res_users_js_call.xml',

    ],

    'qweb':[
        'static/src/xml/button.xml',
],
   
    'installable': True,
    'application': True,
    'auto_install': False,

}
