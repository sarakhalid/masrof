# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = 'pos.order'


    @api.model
    def create_from_ui(self, orders, draft=False):
        if orders[0]['data']['statement_ids']:
            statement_ids = orders[0]['data']['statement_ids']
            if statement_ids[0][2]['payment_method_id']:
                total_amount = 0.0
                for line in orders[0]['data']['lines']:
                    total_amount +=  line[2]['price_subtotal'] 
                payment_method_id = statement_ids[0][2]['payment_method_id']
                payment_method = self.env['pos.payment.method'].browse(payment_method_id)
                if payment_method.is_wallet:
                    line = self.env['wallet.line'].search([('student', '=', orders[0]['data']['partner_id'])])
                    pos_reference = orders[0]['data']['name']
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> pos_reference = ",pos_reference)
                    new_transaction = self.env['wallet.transactions'].create({
			    'wallet': line.wallet.id,
			    'partner_id': orders[0]['data']['partner_id'],
			    'amount': total_amount,
                            'transaction_type':'debit',
                            'currency_id':payment_method.company_id.currency_id.id,
                            'pos_order':pos_reference,
			})
                    new_transaction.state='done'
                    print ("order = ",payment_method.is_wallet)


        order_ids = []
        for order in orders:
            existing_order = False
            if 'server_id' in order['data']:
                existing_order = self.env['pos.order'].search(['|', ('id', '=', order['data']['server_id']), ('pos_reference', '=', order['data']['name'])], limit=1)
            if (existing_order and existing_order.state == 'draft') or not existing_order:
                order_ids.append(self._process_order(order, draft, existing_order))

        return self.env['pos.order'].search_read(domain = [('id', 'in', order_ids)], fields = ['id', 'pos_reference'])



class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_wallet = fields.Boolean('Is Wallet?' , default=False)


class PosConfig(models.Model):
    _inherit = 'pos.config'


    owner = fields.Many2one('res.users', string='Owner',domain=[('partner_type','=','contractor')])





