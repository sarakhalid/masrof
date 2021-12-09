# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import ValidationError
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.osv import expression
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class WebsiteSaleWallet(WebsiteSale):
    






    @http.route('/shop/payment', type='http', auth='public', website=True)
    def payment(self, **post):
        request = super(WebsiteSaleWallet, self).payment(**post)
        companies = http.request.env['res.partner'].sudo().search([('id','=',request.qcontext['partner'])])
        request.qcontext['companies'] = companies
        return request





    
    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
 

        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if transaction_id:
            tx = request.env['payment.transaction'].sudo().browse(transaction_id)
            assert tx in order.transaction_ids()
        elif order:
            tx = order.get_portal_last_transaction()
        else:
            tx = None

        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> tx.partner_id.wallet_amount = ",tx.partner_id.wallet_amount)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.tx.amount",tx.amount)
        if tx.partner_id.wallet_amount < tx.amount :
            print ("#################################################################")
            response = request.render('ways_wallet.not_enough_balance', {})
            return response

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if order and not order.amount_total and not tx:
            order.with_context(send_email=True).action_confirm()
            return request.redirect(order.get_portal_url())

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        PaymentProcessing.remove_payment_transaction(tx)
        print ("################################################ sara = ",request.env['wallet.reference'].sudo().search([('from_sale', '=', True)], limit=1).id)
        
        acquirers = tx.acquirer_id
        if acquirers :
        
            if acquirers.is_wallet == True :
                vals= {
           # 'transaction_id': self.env['ir.sequence'].next_by_code('ways.transactions') or _('New') ,
           # 'transaction_date': fields.Datetime.now,
            'ewallet_id': tx.acquirer_id.id ,
            'transaction_type': 'debit' ,
            'partner_id': tx.partner_id.id ,
            'reference': request.env['wallet.reference'].sudo().search([('from_sale', '=', True)], limit=1).id ,
            'currency_id': tx.currency_id.id ,
            'amount':tx.amount,
            'state':'draft',
            'sale_order':order.id,
        		}
                transactions = request.env['ways.transactions'].create(vals)
                transactions.action_confirm()

        sale_order_id = request.website.sale_get_order()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>sale_order_id",sale_order_id)
        for sale in tx.sale_order_ids:
            for line in sale.order_line:
                if line.product_id.is_wallet:
                    vals= {
               # 'transaction_id': self.env['ir.sequence'].next_by_code('ways.transactions') or _('New') ,
               # 'transaction_date': fields.Datetime.now,
                'transaction_type': 'credit' ,
                'partner_id': order.partner_id.id ,
                'reference': request.env['wallet.reference'].sudo().search([('from_sale', '=', True)], limit=1).id ,
                'currency_id': order.currency_id.id ,
                'amount':line.price_subtotal,
                'state':'draft',
                'sale_order':order.id,
                    }
                    transactions = request.env['ways.transactions'].create(vals)
                    transactions.action_confirm()

        return request.redirect('/shop/confirmation')





    @http.route(['/add_wallet'], type='json', auth="user", methods=['POST'], website=True, csrf=False)
    def add_wallet(self, product_id=22, line_id=22, add_qty=22, set_qty=22, display=True):
        """This route is called when changing quantity from the cart or adding
        a product from the wishlist."""
        response = request.render('ways_wallet.not_enough_balance', {})
        return response

        print ("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG ")
        order = request.env['sale.order'].sudo().search([('id', '=', 85)], limit=1)
        if order.state != 'draft':
            request.website.sale_reset()
            return {}
        for line in order.order_line:
            product_id = line.product_id.id
            line_id = line.id 
            add_qty=line.product_uom_qty
            set_qty=line.product_uom_qty
        value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)
        print ("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  value",value)
        print ("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  order.cart_quantity",order.cart_quantity)
        if not order.cart_quantity:
            request.website.sale_reset()
            return value
        print ("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  order",order)
        order = request.website.sale_get_order()
        value['cart_quantity'] = order.cart_quantity
        print ("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  value['cart_quantity']",value['cart_quantity'])


        value['website_sale.cart_lines'] = request.env['ir.ui.view'].render_template("website_sale.cart_lines", {
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': order._cart_accessories()
        })
        value['website_sale.short_cart_summary'] = request.env['ir.ui.view'].render_template("website_sale.short_cart_summary", {
            'website_sale_order': order,
        })
        return value


