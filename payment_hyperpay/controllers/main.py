# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

import requests
import werkzeug
from werkzeug import urls
import json
from odoo import http
import urllib
# from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo.addons.payment_hyperpay.data.payment_icon import payment_icon

import logging
_logger = logging.getLogger(__name__)

test_domain = "https://test.oppwa.com"
live_domain = "https://oppwa.com"

def _get_checkout_id(**params):
    auth = params.pop('auth', '')
    env = params.pop('env')
    if env == 'enabled':
        domain = live_domain
    else:
        domain = test_domain
        # params['testMode'] = 'EXTERNAL'
    url_string = domain + "/v1/checkouts"

    # url = _build_url_w_params(url_string, params)
    headers = {
    "Authorization" :   auth,
    }
    try:
        r = requests.post(url=url_string, data=params, headers=headers)
        r = r.json()
        if 'parameterErrors' in r.get('result'):
            raise Exception
        return r
    except Exception as e:
        return {}

class HyperPayController(http.Controller):

    @http.route('/payment/hyperpay/checkout/create', type='json', auth='public', csrf=False)
    def create_hyperpay_checkout(self, **post):
        tx = request.env['payment.transaction'].sudo().search([('id','=',int(post.get('txId', 0)))])
        if tx:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            acq = tx.acquirer_id
            partner_id = tx.partner_id
            kwargs = {
                    "auth": "Bearer " + acq.hyperpay_authorization,
                    "entityId": acq.hyperpay_merchant_id,
                    "amount": '%.2f'%tx.amount,
                    "currency": tx.currency_id and tx.sudo().currency_id.name or '',
                    "paymentType": "DB",
                    "env": acq.state,
                    "customParameters[SHOPPER_tx_id]": tx.id,
                    "merchantTransactionId": tx.id,
                    "billing.street1": partner_id.street or '',
                    "billing.street2": partner_id.street2 or '',
                    "billing.city": partner_id.city or '',
                    "billing.state": partner_id.state_id.name or '',
                    "billing.postcode": partner_id.zip or '',
                    "billing.country": partner_id.country_id.code or '',
                    "customer.givenName":partner_id.name or '',
                    "customer.surname":partner_id.name or '',
                    "customer.email": partner_id and partner_id.email or '',
                    "customer.mobile": partner_id and partner_id.mobile or partner_id.phone or '',
                    "customer.phone": partner_id and partner_id.phone or partner_id.mobile or '',
                    }
            resp = _get_checkout_id(**kwargs)
            tx.hyperpay_checkout_id = resp.get('id')
            domain = live_domain if acq.state == 'enabled' else test_domain
            #payment_acq = request.env['payment.acquirer'].sudo()
            #hyperpay =payment_acq.search([('name','=','HyperPay')])
            payment_icons = acq.payment_icon_ids.mapped('name')
            data_brands = "VISA"
            if(len(payment_icon)>1):
                brands = [payment_icon[i.upper()] for i in payment_icons if i.upper() in payment_icon.keys()]
                data_brands = brands and " ".join(brands) or data_brands

            resp = {
                    "checkoutId": resp.get('id',''),
                    'domain': domain,
                    'base_url': base_url,
                    'data_brands':data_brands,
                    'acq':acq.id
                    }
        return resp


    @http.route('/payment/hyperpay/result', type='http', auth='public', csrf=False)
    def hyperpay_shopper_result(self, **post):
        acq = request.env['payment.acquirer'].sudo().search([('id', '=', post.get('acq'))])
        if acq.state == 'enabled':
            url = live_domain
        else:
            url = test_domain
        url += '/' + post.get('resourcePath')+"?entityId=%s"%(acq.hyperpay_merchant_id)
        headers = {
        "Authorization" :  "Bearer " + acq.hyperpay_authorization,
        }
        resp = requests.get(url=url, headers=headers).json()

        _logger.info("-----/payment/hyperpay/result-----response------------%r----", resp)

        payment = request.env['payment.transaction'].sudo()
        tx = payment.search([('hyperpay_checkout_id', '=', post.get('id',''))])
        tx = resp.get('customParameters',{}).get('SHOPPER_tx_id') or tx and tx.id or ''
        resp.update({'tx_id': tx})
        if tx:
            PaymentProcessing.add_payment_transaction(payment.browse(int(tx)))

        res = payment.form_feedback(resp, 'hyperpay')
        return werkzeug.utils.redirect('/payment/process')
