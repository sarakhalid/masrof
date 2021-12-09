# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'


class product_product(models.Model):
    _inherit = 'product.product'
    
    is_wallet = fields.Boolean(string="is wallet")


   
