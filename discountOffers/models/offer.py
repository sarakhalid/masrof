# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################
import logging
import pytz
from decimal import Decimal
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
_logger = logging.getLogger(__name__)

class offer(models.Model):
    _name = "discount.offer"

    name=fields.Char("Title", required=1,translate=1)
    date_start=fields.Date('Start Date', required=1)
    date_end=fields.Date('End Date', required=1)
    typeoffer=fields.Selection([('percentage','Percentage Price'),('price','fixed Price'),('bundle','Bundle')],default="percentage",string="offer Type", required=1)
    product_id = fields.Many2one('product.product',string="Product", required=1)

    percent_price = fields.Float('Percentage Price')
    fixed_price = fields.Float('Fixed Price')
    min_quantity = fields.Float('Min. Quantity')
    pricelist_id = fields.Many2one('product.pricelist',string='Pricelist',required=1)
    state = fields.Selection([('draft','darft'),('run','run')],default="draft",string="Status")
    priceAfteroffer = fields.Float('Price After Offer',compute="compute_priceAfteroffer")
    def compute_priceAfteroffer(self):
        for order in self:
            if(order.product_id and order.typeoffer):
                if(order.typeoffer=="price" or order.typeoffer=="bundle"):
                    order.priceAfteroffer=order.fixed_price
                else:
                    priseAfteroffer=0.00000
                    priseAfteroffer=Decimal(order.product_id.list_price)-round((Decimal(order.percent_price*order.product_id.list_price/100)),3)
                    #priseAfteroffer=order.product_id.list_price-((order.percent_price*order.product_id.list_price/100))
                    print('priseAfteroffer',priseAfteroffer)
                    order.priceAfteroffer = round(priseAfteroffer,2)
    def run(self):
        for order in self:
            item=self.env['product.pricelist.item']
            if(order.typeoffer=="price" or order.typeoffer=="bundle" ):
                value={'date_start':order.date_start,
                        'date_end':order.date_end,
                        'product_id':order.product_id.id,
                        'fixed_price':order.fixed_price,
                       'min_quantity':order.min_quantity,
                       'pricelist_id':order.pricelist_id.id,
                       'offer_msg':order.name,
                       'name':order.product_id.name,
                       'applied_on':"0_product_variant",
                       "compute_price":"fixed",
                       "is_display_timer":True,


                       }
                print(value)
                g = item.sudo().create(value)
            else:
                value = {'date_start': order.date_start,
                         'date_end': order.date_end,
                         'product_id': order.product_id.id,
                         'percent_price': order.percent_price,
                         'min_quantity': order.min_quantity,
                         'pricelist_id': order.pricelist_id.id,
                         'name':order.product_id.name,
                          'applied_on':"0_product_variant",
                          "compute_price": "percentage",
                          "is_display_timer":True,
                         }
                g=item.sudo().create(value)
                print('ffff',g)


            order.write({'state':'run'})






