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
        wallet = http.request.env['e.wallet'].sudo().search([('responsable','=',request.qcontext['partner'])])
        request.qcontext['wallet'] = wallet
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
        
        acquirers = tx.acquirer_id
       
        wallet = http.request.env['e.wallet'].sudo().search([('responsable','=',order.partner_id.id)])

        for sale in tx.sale_order_ids:
            for line in sale.order_line:
                if line.product_id.is_wallet:
                    vals= {
               # 'transaction_id': self.env['ir.sequence'].next_by_code('ways.transactions') or _('New') ,
               # 'transaction_date': fields.Datetime.now,
                'transaction_type': 'credit' ,
                'wallet': wallet.id ,
                'currency_id': order.currency_id.id ,
                'amount':line.price_subtotal,
                'state':'draft',

                    }
                    transactions = request.env['wallet.transactions'].create(vals)
                    transactions.action_confirm()

        return request.redirect('/shop/confirmation')



