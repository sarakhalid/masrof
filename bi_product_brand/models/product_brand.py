# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, tools
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare

class Brand(models.Model):
    _name = 'product.brand'

    def total_items(self):
        for record in self:
            product_count = 0
            if record.product_ids:
                product_count = len(record.product_ids.ids)
            record.tot_items = product_count
   

    name = fields.Char('Brand Name')
    image = fields.Binary('Image')
    seq = fields.Integer('Sequence')
    tot_items = fields.Integer('Total No. of Items', compute='total_items')
    product_ids = fields.Many2many('product.template', string='Products', ondelete='cascade')
    
    @api.model
    def create(self, value):
        brand = super(Brand, self).create(value)
        for products in brand.product_ids:
            products.update({'brand_id': brand.id})
        return brand

    def write(self,value):
        brand = super(Brand, self).write(value)
        for products in self.product_ids:
            if not products.brand_id or products.brand_id.id != self.id:
                products.update({'brand_id': self.id})
        return brand
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:           
