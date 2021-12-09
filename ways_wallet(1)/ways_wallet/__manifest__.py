{
    'name': 'Ways Wallet on Website',
    "version": "1.0",
    'depends': ['base','website','website_sale','payment'],
    "summary": "",
    'website': 'http://www.ways.sa',
    "author": "Ways",
    "category": "websit",
    "description": """
    
""",
    'data': [

        'views/transactions_view.xml',
        'views/configuration_view.xml',
        'views/ir_sequence_data.xml',
        'views/wallet_website_menu.xml',
       # 'views/wallet_templates.xml',
        'views/wallet_template_transation.xml',
        'security/ir.model.access.csv',
        'data/payment_acquirer_data.xml',
        'views/payment_views.xml',

        
    ],
    
    'js': [
 'static/src/js/wallet.js'
		],
    'application': 'True',
}
