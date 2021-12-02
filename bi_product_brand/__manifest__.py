# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Brand in Odoo',
    'summary': 'Apps useful for products brand on product variant brands product brands on variant product template brand category product Brand on category product category brands feature with website product brands on sales shop product brand webshop product brand',
    'description': """

    odoo Website Product Brand odoo
        
    odoo product brand on product variant website product brand
    odoo Product Brand With Website Feature product attribute brands
    odoo product variant brand product brand on variant product template brand
    odoo product brand feature with website product brand on sales
    odoo product brand on purchase product brand on invoice
    Odoo brand product Brand on product template Brand on product variants

    odoo product brands on product variant website product brands
    odoo Product Brands With Website Feature product attribute brands
    odoo product variant brands product brands on variant product template brands
    odoo product brands feature with website product brands on sales brands
    odoo product brands on purchase product brands on invoice brands
    Odoo brands product Brands on product template Brands on product variants


    odoo product category brand on product variant website product brands
    odoo Product category Brand With Website Feature product category attribute brands
    odoo product variant category brand product category brand on variant product category template brands
    odoo product category brands feature with website product brands on sales category brands
    odoo product category brand on purchase product brands on invoice brands
    Odoo brands category product Brand on category product template Brand on product variants category brand


""" ,
    'category': 'Sales',
    'version': '13.0.0.3',
    "price": 15,
    "currency": 'EUR',
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'depends': ['sale', 'stock','product'],
    'data': [
        'security/ir.model.access.csv',
        'views/brand_view.xml',
        'views/product_view_inh.xml',
    ],
    'application': True,
    'installable': True,
    "images":['static/description/Banner.png'],
    "live_test_url":'https://youtu.be/UX3gQe1xTfM',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
