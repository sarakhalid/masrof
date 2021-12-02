# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _ ,tools
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID
import psycopg2
import itertools
from odoo.exceptions import ValidationError, except_orm

class ProductBrand(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.brand', 'Brand')
    

    @api.model
    def create(self,vals):
        brand = super(ProductBrand, self).create(vals)
        if vals.get('brand_id'):
            brand_brw = self.env['product.brand'].browse(vals.get('brand_id'))
            brand_brw.write({'product_ids': [(4, brand.id)]})
        return brand
    

    def write(self,value):
        brand = super(ProductBrand, self).write(value)
        if value.get('brand_id'):
            brand_brw = self.env['product.brand'].browse(value.get('brand_id'))
            brand_brw.write({'product_ids': [(4, self.id)]})
            products = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
            for product_variants in products:
                product_variants.update({'brand_id': self.brand_id.id})
        return brand

    def create_variant_ids(self):
        Product = self.env["product.product"]
        AttributeValues = self.env['product.attribute.value']
        for tmpl_id in self.with_context(active_test=False):
            # adding an attribute with only one value should not recreate product
            # write this attribute on every product to make sure we don't lose them
            variant_alone = tmpl_id.attribute_line_ids.filtered(lambda line: len(line.value_ids) == 1).mapped('value_ids')
            for value_id in variant_alone:
                updated_products = tmpl_id.product_variant_ids.filtered(lambda product: value_id.attribute_id not in product.mapped('attribute_value_ids.attribute_id'))
                updated_products.write({'attribute_value_ids': [(4, value_id.id)],
                    'brand_id':tmpl_id.brand_id.id,
                })

            # iterator of n-uple of product.attribute.value *ids*
            variant_matrix = [
                AttributeValues.browse(value_ids)
                for value_ids in itertools.product(*(line.value_ids.ids for line in tmpl_id.attribute_line_ids if line.value_ids[:1].attribute_id.create_variant))
            ]

            # get the value (id) sets of existing variants
            existing_variants = {frozenset(variant.attribute_value_ids.ids) for variant in tmpl_id.product_variant_ids}
            # -> for each value set, create a recordset of values to create a
            #    variant for if the value set isn't already a variant
            to_create_variants = [
                value_ids
                for value_ids in variant_matrix
                if set(value_ids.ids) not in existing_variants
            ]

            # check product
            variants_to_activate = self.env['product.product']
            variants_to_unlink = self.env['product.product']
            for product_id in tmpl_id.product_variant_ids:
                if not product_id.active and product_id.attribute_value_ids.filtered(lambda r: r.attribute_id.create_variant) in variant_matrix:
                    variants_to_activate |= product_id
                elif product_id.attribute_value_ids.filtered(lambda r: r.attribute_id.create_variant) not in variant_matrix:
                    variants_to_unlink |= product_id
            if variants_to_activate:
                variants_to_activate.write({'active': True})

            # create new product
            for variant_ids in to_create_variants:
                new_variant = Product.create({
                    'product_tmpl_id': tmpl_id.id,
                    'attribute_value_ids': [(6, 0, variant_ids.ids)],
                    'brand_id':tmpl_id.brand_id.id,
                })

            # unlink or inactive product
            for variant in variants_to_unlink:
                try:
                    with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                        variant.unlink()
                # We catch all kind of exception to be sure that the operation doesn't fail.
                except (psycopg2.Error, except_orm):
                    variant.write({'active': False})
                    pass
        return True




class product_product(models.Model):
    _inherit = 'product.product'
	
    brand_id = fields.Many2one('product.brand', 'Brand')
    
       

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
