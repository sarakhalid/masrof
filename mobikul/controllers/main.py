# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from pdb import set_trace

import werkzeug
import requests
import pytz
from odoo.addons.mobikul.tool.service import WebServices
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.mobikul.tool.help import _displayWithCurrency, _get_image_url, _changePricelist, remove_htmltags, AQUIRER_REF_CODES, STATUS_MAPPING, _get_next_reference,EMPTY_ADDRESS
from odoo import http,_
from odoo.http import request, route
from odoo.fields import Datetime, Date, Selection
from unidecode import unidecode
from odoo.exceptions import UserError
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment_hyperpay.data.payment_icon import payment_icon
from odoo.addons.payment_hyperpay.controllers.main import _get_checkout_id
from datetime import date, datetime,timedelta
import urllib, urllib.request, urllib.parse



try:
    from urllib.parse import urlencode
    from urllib.request import build_opener, Request, HTTPHandler
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib import urlencode
    from urllib2 import build_opener, Request, HTTPHandler, HTTPError, URLError

import json
import re
import math, random
import logging
_logger = logging.getLogger(__name__)


test_domain = "https://test.oppwa.com"
live_domain = "https://oppwa.com"


def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(4):
        OTP += digits[int(math.floor(random.random() * 10))]
    return OTP


class MobikulApi(WebServices):
    @route('/mobikul/getPdf', type='http', auth="public", csrf=False, website=True, methods=['POST', 'GET'])
    def getpdf(self, **kwargs):
        sale_order_id=int(kwargs['orderId'])
        if(sale_order_id):
            pdf = request.env.ref('sale.action_report_saleorder').sudo().render_qweb_pdf([sale_order_id])[0]
            # pdf = request.env['report'].sudo().get_pdf(['/report/pdf/account.report_invoice/%s' % sale_order_id],'sale.report_saleorder',data=None)
            pdfhttpheader=[('Content-Type','application/pdf'),('Content-Length', len(pdf))]
            return request.make_response(pdf,headers=pdfhttpheader)







    @route('/mobikul/checkoutstest', type='http', auth="public", csrf=False, website=True, methods=['POST', 'GET'])
    def checkoutstest(self, **kwargs):
        result = []

        url = "https://test.oppwa.com/v1/checkouts"
        data = {
            'entityId': '8a8294174b7ecb28014b9699220015ca',
            'amount': '92.00',
            'currency': 'EUR',
            'paymentBrand': 'VISA',
            'paymentType': 'DB',
            'card.number': '4200000000000000',
            'card.holder': 'Jane Jones',
            'card.expiryMonth': '05',
            'card.expiryYear': '2034',
            'card.cvv': '123'
        }
        try:
            opener = build_opener(HTTPHandler)
            request = Request(url, data=urlencode(data).encode('utf-8'))
            request.add_header('Authorization', 'Bearer OGE4Mjk0MTc0YjdlY2IyODAxNGI5Njk5MjIwMDE1Y2N8c3k2S0pzVDg=')
            request.get_method = lambda: 'POST'
            response = opener.open(request)
            response2=json.loads(response.read())
            checkouts_id = response2.get('id')

            result.append(response2.get('id'))
        except HTTPError as e:
            result.append(json.loads(e.read()))

        except URLError as e:
            result.append(e.reason)
        values = {
            'checkoutstest': result
        }
        return self._response('checkoutstest', values)
    @route('/mobikul/paymentLive', type='http', auth="public", csrf=False, website=True, methods=['POST', 'GET'])
    def paymentlive(self, **kwargs):
        result = []
        if (kwargs['acquirerId']):
            acq = request.env['payment.acquirer'].sudo().search([('id', '=', int(kwargs['acquirerId']))])
            live_domain2 = "https://oppwa.com/v1/payments"
            test_domain2 = "https://test.oppwa.com/v1/payments"
            url = ''
            if (acq.state == 'enabled'):
                url = live_domain2
            else:
                url = test_domain2
            data ={}
            if(kwargs['brand']=='MADA' or kwargs['brand']=='VISA' or kwargs['brand']=='MASTER'):
                data = {
                    'entityId': acq.hyperpay_merchant_id,
                    'amount': kwargs['amount'],
                    'currency': 'SAR',
                    'paymentBrand': kwargs['brand'],
                    'paymentType': 'DB',
                    'card.number': kwargs['cardNumber'],
                    'card.holder': kwargs['cardHolder'],
                    'card.expiryMonth': kwargs['cardExpiryMonth'],
                    'card.expiryYear': kwargs['cardExpiryYear'],
                    'card.cvv': kwargs['cardCvv'],
                    'shopperResultUrl': 'mayarmarket.com',
                }
            elif (kwargs['brand']=='APPLEPAY'):
                data = {
                    'entityId': acq.hyperpay_merchant_id,
                    'amount': kwargs['amount'],
                    'currency': 'SAR',
                    'paymentBrand': kwargs['brand'],
                    'paymentType': 'DB',
                    'card.number': kwargs['cardNumber'],
                    'card.holder': kwargs['cardHolder'],
                    'card.expiryMonth': kwargs['cardExpiryMonth'],
                    'card.expiryYear': kwargs['cardExpiryYear'],
                    'threeDSecure.verificationId' : kwargs['threeDSecureVerificationId'],
                    'threeDSecure.eci' : kwargs['threeDSecureEci'],
                    'applePay.source' : 'web',
                    'shopperResultUrl': 'mayarmarket.com',
                }
            try:
                opener = build_opener(HTTPHandler)
                # request = Request(url, data=urlencode(data).encode('utf-8'))
                request2 = Request('https://oppwa.com/v1/payments', data=urlencode(data).encode('utf-8'))
                request2.add_header('Authorization', 'Bearer ' + acq.hyperpay_authorization)
                request2.get_method = lambda: 'POST'
                response = opener.open(request2)
                response2 = json.loads(response.read())
                result.append(response2)
            except HTTPError as e:
                result.append(json.loads(e.read()))
            except URLError as e:
                result.append(e.reason)
            values = {
                'paymentlive': result
            }
            return self._response('paymentlive', values)






    # @route('/mobikul/paymentLive', type='http', auth="public", csrf=False, website=True, methods=['POST', 'GET'])
    # def paymentlive(self, **kwargs):
    #     acq=[]
    #     result = []
    #     if (kwargs.get('acquirerId')):
    #         acq = request.env['payment.acquirer'].sudo().search([('id', '=', kwargs.get('acquirerId'))], limit=1)
    #     live_domain2 = "https://oppwa.com/v1/payments"
    #     test_domain2 = "https://test.oppwa.com/v1/payments"
    #     url = ''
    #     if (acq.state == 'enabled'):
    #         url = live_domain2
    #     else:
    #         url = test_domain2
    #     # data = {
    #     #     'entityId': '8ac9a4c8750277f301750319bca90b14',
    #     #     'amount': '1.00',
    #     #     'currency': 'SAR',
    #     #     'paymentBrand': 'MADA',
    #     #     'paymentType': 'DB',
    #     #     'card.number': '4847831040711258',
    #     #     'card.holder':'AHMEDALMOKASHFI MODHAWY',
    #     #     'card.expiryMonth': '12',
    #     #     'card.expiryYear':'2023',
    #     #     'card.cvv': '927',
    #     #     'shopperResultUrl':'mayarmarket.com',
    #     # }
    #     data = {
    #         'entityId': acq.hyperpay_merchant_id,
    #         'amount': kwargs.get('amount'),
    #         'currency': 'SAR',
    #         'paymentBrand': kwargs.get('brand'),
    #         'paymentType': 'DB',
    #         'card.number': kwargs.get('cardNumber'),
    #         'card.holder': kwargs.get('cardHolder'),
    #         'card.expiryMonth': kwargs.get('cardExpiryMonth'),
    #         'card.expiryYear': kwargs.get('cardExpiryYear'),
    #         'card.cvv': kwargs.get('cardCvv'),
    #         'shopperResultUrl': 'mayarmarket.com',
    #     }
    #     try:
    #         opener = build_opener(HTTPHandler)
    #         # request = Request(url, data=urlencode(data).encode('utf-8'))
    #         request = Request('https://oppwa.com/v1/payments', data=urlencode(data).encode('utf-8'))
    #         # request.add_header('Authorization', 'Bearer OGFjOWE0Yzg3NTAyNzdmMzAxNzUwMzE3NDU4ZDBhYmF8RnRXQkhiZTc2NA==')
    #         request.add_header('Authorization', 'Bearer ' + acq.hyperpay_authorization)
    #         request.get_method = lambda: 'POST'
    #         response = opener.open(request)
    #         response2 = json.loads(response.read())
    #         checkouts_id = response2.get('id')
    #         # checkouts_live_domain2 = checkouts_live_domain2+'/'+checkouts_id+'/payment'
    #         # request = Request(checkouts_live_domain2, data=urlencode(data).encode('utf-8'))
    #         # request.add_header('Authorization', 'Bearer OGFjOWE0Yzg3NTAyNzdmMzAxNzUwMzE3NDU4ZDBhYmF8RnRXQkhiZTc2NA==')
    #         # request.get_method = lambda: 'POST'
    #         # response = opener.open(request)
    #         response2 = json.loads(response.read())
    #
    #         result.append(response2)
    #     except HTTPError as e:
    #         result.append(json.loads(e.read()))
    #
    #     except URLError as e:
    #         result.append(e.reason)
    #
    #     values = {
    #         'paymentlive': result
    #     }
    #     return self._response('paymentlive', values)


    @http.route('/mobikul/paymentTest', type='http', auth="public", csrf=False, website=True, methods=['POST', 'GET'] )
    def paymenttest(self, **kwargs):
        result=[]

        url = "https://test.oppwa.com/v1/payments"
        data = {
            'entityId': '8a8294174b7ecb28014b9699220015ca',
            'amount': '92.00',
            'currency': 'EUR',
            'paymentBrand': 'VISA',
            'paymentType': 'DB',
            'card.number': '4200000000000000',
            'card.holder': 'Jane Jones',
            'card.expiryMonth': '05',
            'card.expiryYear': '2034',
            'card.cvv': '123'
        }
        try:
            opener = build_opener(HTTPHandler)
            request = Request(url, data=urlencode(data).encode('utf-8'))
            request.add_header('Authorization', 'Bearer OGE4Mjk0MTc0YjdlY2IyODAxNGI5Njk5MjIwMDE1Y2N8c3k2S0pzVDg=')
            request.get_method = lambda: 'POST'
            response = opener.open(request)
            result.append(json.loads(response.read()))
        except HTTPError as e:
            result.append(json.loads(e.read()))

        except URLError as e:
            result.append(e.reason)
        values = {
            'paymenttest': result
        }
        return self._response('paymenttest', values)



    #-------------------------------
    @route('/mobikul/payment/hyperpay/checkout/create', type='http', auth="public", csrf=False, website=True, methods=['POST', 'GET'])
    def create_hyperpay_checkout(self, **post):
        tx = request.env['payment.transaction'].sudo().search([('id', '=', int(post.get('txId', 0)))])
        if tx:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            acq = tx.acquirer_id
            partner_id = tx.partner_id
            kwargs = {
                "auth": "Bearer " + acq.hyperpay_authorization,
                "entityId": acq.hyperpay_merchant_id,
                "amount": '%.2f' % tx.amount,
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
                "customer.givenName": partner_id.name or '',
                "customer.surname": partner_id.name or '',
                "customer.email": partner_id and partner_id.email or '',
                "customer.mobile": partner_id and partner_id.mobile or partner_id.phone or '',
                "customer.phone": partner_id and partner_id.phone or partner_id.mobile or '',
            }
            resp = _get_checkout_id(**kwargs)
            tx.hyperpay_checkout_id = resp.get('id')
            domain = live_domain if acq.state == 'enabled' else test_domain
            # payment_acq = request.env['payment.acquirer'].sudo()
            # hyperpay =payment_acq.search([('name','=','HyperPay')])
            payment_icons = acq.payment_icon_ids.mapped('name')
            data_brands = "VISA"
            if (len(payment_icon) > 1):
                brands = [payment_icon[i.upper()] for i in payment_icons if i.upper() in payment_icon.keys()]
                data_brands = brands and " ".join(brands) or data_brands

            resp = {
                "checkoutId": resp.get('id', ''),
                'domain': domain,
                'baseUrl': 'https://mayarmarket.com',
                'dataBrands': data_brands,
                'acq': acq.id,
            }
            return self._response('checkoutId', resp)
    @route('/mobikul/payment/hyperpay/result', type='http', auth="public", csrf=False, website=True, methods=['POST', 'GET'])
    def mobikul_check_result(self, **post):
        tx = request.env['payment.transaction'].sudo().search([('id', '=', int(post.get('txId', 0)))])
        if tx:
            acq = tx.acquirer_id
            _logger.info("Payment Acquirer is this %r", acq)
            if acq.state == 'enabled':
                url = live_domain
            else:
                url = test_domain
            url += '/' + post.get('resourcePath') + "?entityId=%s" % (acq.hyperpay_merchant_id)
            headers = {
                "Authorization": "Bearer " + acq.hyperpay_authorization,
            }
            # hitting the hypperpay api and get the data in response
            resp = requests.get(url=url, headers=headers).json()
            resp2 = resp.get('result', {})

            return self._response('result', resp2)




    @route('/mobikul/payment/hyperpay/payment/status', type='http', auth="public", csrf=False, website=True, methods=['POST', 'GET'])
    def request(self, **post):
        result = []
        tx = request.env['payment.transaction'].sudo().search([('id', '=', int(post.get('txId', 0)))])
        if tx:
            if tx.hyperpay_checkout_id:
                acq = tx.acquirer_id
                url = "https://oppwa.com/v1/checkouts/"+tx.hyperpay_checkout_id+"/payment"
                url += '?entityId='+acq.hyperpay_merchant_id
                try:
                    opener = build_opener(HTTPHandler)
                    request2 = Request(url, data=b'')
                    request2.add_header('Authorization',
                                       "Bearer " + acq.hyperpay_authorization)
                    request2.get_method = lambda: 'GET'
                    response = opener.open(request2)
                    result.append(json.loads(response.read()))


                except HTTPError as e:
                    return json.loads(e.read())
                except URLError as e:
                    return e.reason
                resp = {
                    "result": result,
                }
                return self._response('result', resp)




    # ---------
    @route('/mobikul/editItemList', type='http', auth="public", csrf=False, website=True, methods=['PUT','POST'])
    def editItemList(self, **kwargs):
        result = {}
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)

        if response.get('success'):
            product = request.env['quick.products.list'].sudo().search([
                ('product_id.id', '=', kwargs['productId']), ('line_id.id', '=', kwargs['listId'])], limit=1)
            if product:
                product.sudo().write(
                    {'product_id': kwargs['productId'], 'line_id': kwargs['listId'], 'qty': kwargs['qty']})
                result.update({'message': "This Item was Edit"})
            else:
                result.update({'message': "This Item does not exist"})
        values = {
            'editItemList': result
        }
        return self._response('editItemList', result)

    @route('/mobikul/addItemList', type='http', auth="public", csrf=False, website=True, methods=['POST'])
    def addItemList(self, **kwargs):
        result = {}
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            product = request.env['quick.products.list'].sudo().search([
                ('product_id.id', '=', kwargs['productId']),('line_id.id','=',kwargs['listId'])], limit=1)
            if len(product)>0:
                result.update({'message': "This Item is exist","success":False})

            else:
                product = request.env['quick.products.list'].sudo().create({'product_id':kwargs['productId'],'line_id':kwargs['listId'],'qty':1})

                result.update({'message': "The Item was  add successful","success":True})
        values = {
            'addItemList': result
        }
        return self._response('addItemList', result)

    @route('/mobikul/deleteItemList', type='http', auth="public", csrf=False, methods=['DELETE','POST'])
    def deleteItemList(self, **kwargs):
        result = {}
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            product = request.env['quick.products.list'].sudo().search([
                ('product_id.id', '=', kwargs['productId']), ('line_id.id', '=', kwargs['listId'])], limit=1)
            if product:
                product.sudo().unlink()
                result.update({'message': "The deletion was successful","success":True})
            else:
                result.update({'message': "This Item does not exist","success":False})
        values = {
            'removetemList': result
        }
        return self._response('removetemList', result)
    @route('/mobikul/deleteList', type='http', auth="public", csrf=False,  methods=['DELETE'])
    def deleteList(self, **kwargs):
        result = {}
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            product = request.env['quick.order'].sudo().search([
                ('id', '=', kwargs['listId'])],limit=1)
            if product:
                product.sudo().unlink()
                result.update({'message': "The deletion was successful","success":True})
            else:
                result.update({'message': "This list does not exist","success":False})
        values = {
            'deleteList': result
        }
        return self._response('deleteList', result)


    @route('/mobikul/editList', type='http', auth="public", csrf=False, methods=['PUT'])
    def edit_List(self, **kwargs):
        result = {}
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            product = request.env['quick.order'].sudo().search([
                ('id', '=', kwargs['listId'])], limit=1)
            if product:
                product.sudo().write(
                    {'name': kwargs['listName']}
                )
                result.update({'message': "Modified successfully","success":True})
                order_id = request.env['quick.order'].sudo().search([
                    ('id', '=', kwargs['listId'])])

                result.update({'listId': order_id.id,
                               'listName': order_id.name,
                               'userId': order_id.store_user_id,
                               'listType':order_id.listType,
                               })
            else:
                result.update({'message': "This list does not exist","success":False})
                result.update({'listId': 0,
                               'listName': '',
                               'userId': 0,
                               })

        values = {
            'editList': result
        }
        return self._response('editList', result)


    @route('/mobikul/createList', type='http', auth="public", csrf=False, methods=['POST'] )
    def create_list(self, **kwargs):
        result = {}
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            user = response.get("context").get("user")
            if user:
                quickorder = request.env['quick.order'].search([
                    ('name', '=', kwargs['listName']),
                    ('store_user_id', '=', user.id)])
                if quickorder:
                    result.update({'message':"The list already exists","success":False,})
                    result.update({'listId': quickorder.id,
                                   'listName': quickorder.name,
                                   'userId': quickorder.store_user_id,
                                   'listType': quickorder.listType,
                                   })

                else:
                    val = {'name': kwargs['listName'],
                           'store_user_id': user.id,
                           'listType':int(kwargs['listType'])}
                    order_id = request.env['quick.order'].sudo().create(val)
                    result.update({'message':"A new list has been added successfully","success":True,})
                    result.update({'listId': order_id.id,
                                   'listName': order_id.name,
                                   'userId': order_id.store_user_id,
                                   'listType': order_id.listType,
                                   })

            values = {
                'createList': result
            }
            return self._response('createList', result)

    @route('/mobikul/getList', type='http', auth="public", csrf=False,  methods=['GET'])
    def getlist(self, **kwargs):
        result = []
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            user = response.get("context").get("user")
            if user:
                quickorder = request.env['quick.order'].search([
                    ('store_user_id', '=', user.id)])
                if (len(quickorder) > 0):
                    for order in quickorder:
                        count = 0.0
                        for line in order.sudo().quick_products2:
                            count=count+line.qty

                        result.append({'listId': order.id,
                                       'listName': order.name,
                                       'userId': order.store_user_id,
                                       'listType': order.listType,
                                       'count':count,
                                       })
            values = {
                'getList': result,
                "success": True,
            }
            return self._response('getList', values)

    @route('/mobikul/getListDetails', type='http', auth="public", csrf=False, methods=['GET'])
    def getListDetails(self, **kwargs):
        result = {}
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            user = response.get("context").get("user")
            local = response.get('context', {})
            if user:
                quickorder = request.env['quick.order'].search([
                    ('store_user_id', '=', user.id),('id','=',int(kwargs['listId']))])
                if (len(quickorder) > 0):
                    for order in quickorder:
                        result.update({'listId': order.id,
                                       'listName': order.name,
                                       'userId': order.store_user_id,
                                       'listType': order.listType,
                                       })
                        reslut2=[]
                        for record in order.sudo().quick_products2:
                            isOffer = False
                            offerPrice = 0.0,
                            msgOffer = ""

                            today = datetime.today()
                            offer = request.env['discount.offer'].sudo().search(
                                [('product_id.id', '=', record.product_id.id), ('date_start', '<=', today),
                                 ('date_end', '>=', today)], limit=1)

                            if (offer):
                                isOffer = True
                                offerPrice = offer.priceAfteroffer
                                msgOffer = offer.name

                            reslut2.append({'ItemId':record.id,
                                            'productId':record.product_id.id,
                                            'productName':record.product_id.name,
                                            'qty':record.qty,
                                            'thumbNail': _get_image_url(self.base_url, 'product.product', record.product_id.id, 'image_1920',
                                        record.product_id.write_date),
                                            'uomQty': record.product_id.product_tmpl_id.uom_QTY or '',
                                            'priceUnit': _displayWithCurrency(local.get('lang_obj'), record.product_id.list_price,
                                                                  local.get('currencySymbol'), local.get('currencyPosition')),
                                            'isOffer': isOffer,
                                            'offerPrice': _displayWithCurrency(local.get('lang_obj'), offerPrice,
                                                                               local.get('currencySymbol', ""),
                                                                               local.get('currencyPosition', "")),

                                            'msgOffer': msgOffer,

                                            })
                           
                        result.update({'listItem':reslut2})

            values = {
                'getListDetails': result
            }
            return self._response('getList', result)

    @route('/mobikul/listToCart', csrf=False, type='http', auth="public", methods=['POST'])
    def getlistToCart(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            Mobikul = response.get("context").get("mobikul_obj")
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            last_order = Partner.last_mobikul_so_id
            local = response.get('context', {})
            listId = request.env['quick.order'].sudo().search([('id', '=', int(kwargs['listId']))])

            result = {}

            context = response.get("context")
            addr = Partner.address_get(['delivery'])
            so_data = {
                'partner_id': Partner.id,
                'pricelist_id': context.get('pricelist').id,
                'payment_term_id': Partner.property_payment_term_id.id,
                'team_id': context.get("teamId"),
                'partner_invoice_id': Partner.id,
                'partner_shipping_id': addr['delivery'],
                'user_id': context.get("salespersonId"),
            }

            company = context.get("pricelist").company_id

            # if company:
            #     so_data['company_id'] = company.id
            if not last_order:
                new_order = request.env['sale.order'].sudo(1).create(so_data)

                Partner.write({'last_mobikul_so_id': new_order.id})

        if listId:
            for line in listId.sudo().quick_products2:
                result2 = Mobikul.add_to_cart(line.product_id.id, self._mData.get("set_qty"),
                                              line.qty, response.get("context"))
            result = {'success': True, 'message': 'add List to cart success !!!'}
        else:
            result = {'success': False, 'message': 'list  not found !!!'}
        response.update(result)
        return self._response('List', response)

    @route('/mobikul/livechat', type='http', auth="public", csrf=False,  methods=['POST', 'GET'])
    def channel_list(self, **kw):
        # display the list of the channel
        channels = request.env['im_livechat.channel'].sudo().search([('website_published', '=', True)])
        data=[]
        for order in channels:
            user_id_data=[]
            for user_id in order.user_ids:
                user_id_data.append(user_id.id)

            data.append({'id':order.id,'name':order.name,'buttonText':order.button_text,'defaultMessage':order.default_message,'team':user_id_data})

        values = {
            'channels': data
        }
        return self._response('channels', values)

    @http.route('/mobikul/livechat/getsession', type="http", auth='public', csrf=False,method=['GET'])
    def getsession(self, **kwargs):
        """ Override to use visitor name instead of 'Visitor' whenever a visitor start a livechat session. """
        result = {}
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
            visitor_sudo = request.env.ref('base.public_user')
            if visitor_sudo:
                anonymous_name = visitor_sudo.partner_id.display_name
                result.update({'anonymous_name': anonymous_name})
                channels = request.env['im_livechat.channel'].sudo().search([('website_published', '=', True)], limit=1)
                result.update({'channels': channels.id})
                channels_user_name = ''
                for user_id in channels.user_ids:
                    channels_user_name += str(user_id.partner_id.display_name) + ','

                seesion_name = str(visitor_sudo.partner_id.display_name) + ',' + str(channels_user_name)
                session = request.env['mail.channel'].sudo().create(
                    {'livechat_channel_id': channels.id, 'name': seesion_name, 'livechat_active':True})
                message = request.env['mail.message'].sudo().create({'email_from': visitor_sudo.partner_id.email,
                                                                     'author_id': visitor_sudo.partner_id.id,
                                                                     'model': 'mail.channel',
                                                                     'message_type': 'sms',
                                                                     'subtype_id': request.env.ref(
                                                                         'mail.mt_comment').id,
                                                                     'body': channels.default_message,
                                                                     'partner_ids': [(4, visitor_sudo.partner_id.id)],
                                                                     'res_id': session.id,

                                                                     })
                result.update({'sessionId': session.id})


        if response.get('success'):
            visitor_sudo = response.get("context").get("user")

            if visitor_sudo:
                anonymous_name = visitor_sudo.partner_id.display_name
                result.update({'anonymous_name':anonymous_name})
                channels = request.env['im_livechat.channel'].sudo().search([('website_published', '=', True)],limit=1)
                result.update({'channels': channels.id})
                channels_user_name=''
                for user_id in channels.user_ids:
                    channels_user_name +=str(user_id.partner_id.display_name)+','


                seesion_name=str(visitor_sudo.partner_id.display_name)+','+str(channels_user_name)
                session=request.env['mail.channel'].sudo().create({'livechat_channel_id':channels.id,'name':seesion_name,})
                message=request.env['mail.message'].sudo().create({'email_from': visitor_sudo.partner_id.email,
                                                        'author_id': visitor_sudo.partner_id.id,
                                                        'model': 'mail.channel',
                                                        'message_type': 'sms',
                                                        'subtype_id': request.env.ref('mail.mt_comment').id,
                                                        'body':  channels.default_message,
                                                        'partner_ids': [(4,visitor_sudo.partner_id.id)],
                                                        'res_id':session.id,

                                                        })

                result.update({'sessionId': session.id})





        values={'channelsChat':result}
        return self._response('channels', values)

    @http.route('/mobikul/livechat/postChat', type="http", auth='public', csrf=False,method=['POST'])
    def postChat(self, **kwargs):
        """ Override to use visitor name instead of 'Visitor' whenever a visitor start a livechat session. """
        result = {}
        session = request.env['mail.channel'].sudo().search([('id','=',int(kwargs['sessionId']))])
        livechat_channel_id=session.livechat_channel_id

        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
            visitor_sudo = request.env.ref('base.public_user')
            if visitor_sudo:

                message = request.env['mail.message'].sudo().create({'email_from': visitor_sudo.partner_id.email,
                                                                     'author_id': visitor_sudo.partner_id.id,
                                                                     'model': 'mail.channel',
                                                                     'message_type': kwargs['messageType'],
                                                                     'subtype_id': request.env.ref('mail.mt_comment').id,

                                                                     'body': kwargs['msg'],
                                                                     #'partner_ids': [(4, livechat_channel_id.user_ids.partner_id.id)],


                                                                     'channel_ids':[(4, 1)],
                                                                     'res_id':int(kwargs['sessionId']),
                                                                     })
                session.sudo().write({'channel_message_ids':[(4,message.id)]})
                # request.message_post(body='This receipt has been validated!', message_type='notification',
                #                   subtype='mail.mt_comment', author_id='visitor_sudo.partner_id.id',
                #                   notification_ids='livechat_channel_id.user_ids.partner_id.id')


        if response.get('success'):
            visitor_sudo = response.get("context").get("user")
            if visitor_sudo:
                anonymous_name = visitor_sudo.partner_id.display_name
                channels_user_name = ''
                message = request.env['mail.message'].sudo().create({'email_from': visitor_sudo.partner_id.email,
                                                                     'author_id': visitor_sudo.partner_id.id,
                                                                     'model': 'mail.channel',
                                                                     'message_type': kwargs['messageType'],
                                                                     'subtype_id': request.env.ref(
                                                                     'mail.mt_comment').id,
                                                                     'body': kwargs['msg'],
                                                                     'partner_ids': [(4, visitor_sudo.partner_id.id)],
                                                                     'res_id': int(kwargs['sessionId']),
                                                                  })
        values = {'message': "POST successfully"}
        return self._response('channels', values)

    @http.route('/mobikul/livechat/getSessionData', type="http", auth='public', csrf=False,method=['GET'])
    def get_session(self, **kwargs):
        """ Override to use visitor name instead of 'Visitor' whenever a visitor start a livechat session. """
        result = []

        session = request.env['mail.channel'].sudo().search([('id','=',kwargs['sessionId'])])
        for order in session.message_ids:
            result.append({'msg': order.body,'author_id':order.author_id.display_name,'date':str(order.create_date.strftime('%Y-%m-%d %H:%M:%S'))})

        values = {'chat': result}
        return self._response('chat', values)

    @route('/mobikul/getDeliverySchedule', csrf=False, type='http', auth="public", methods=['POST', 'GET'])
    def getDeliverySchedule(self, **kwargs):
        result = []
        delivery_schedule_data_id = request.env.ref('mobikul.start_end_delivery_schedule_data').id
        if (delivery_schedule_data_id):
            delivery_schedule_data = request.env['start.end.delivery.schedule'].sudo().search([('id', '=',delivery_schedule_data_id)])
            result.append({'startTime': delivery_schedule_data.start_time or 0.0,'endTime':delivery_schedule_data.end_time or 0.0})
        delivery_schedule = {'delivery_schedule': result}
        return self._response('delivery_schedule', delivery_schedule)

    @route('/mobikul/checkPostCode', csrf=False, type='http', auth="public", methods=['POST', 'GET'])
    def checkPostCode(self, **kwargs):
        result = []
        checkPostCode = {}
        zip_code = request.env['zip.code'].sudo().search([('zip', '=', kwargs['postcode'])])
        if(len(zip_code)>0):
            checkPostCode.update({'postcode':True})
        else:
            checkPostCode.update({'postcode': False})
        return self._response('checkPostCode', checkPostCode)

    @route('/mobikul/updateaccount', csrf=False, type='http', auth="public", methods=['POST', 'GET'])
    def updateaccount(self, **kwargs):
        otp=kwargs['otp']
        result = []
        user_old = request.env['res.users'].sudo().search([('id', '=', kwargs['userId'])], limit=1)
        if(kwargs['email']):
            if (user_old.login != kwargs['email'] or user_old.name != kwargs['name']):
                edit_data = {'login': kwargs['email'],
                             'name': kwargs['name']
                             }
                user_old.sudo().write(edit_data)
                user_id = request.env['res.users'].sudo().search([('id', '=', kwargs['userId'])], limit=1)
                if (user_old.partner_id.email != kwargs['email'] or user_old.partner_id.name != kwargs['name']):
                    user_old.partner_id.sudo().write({'email': kwargs['email'],
                                                      'name': kwargs['name']
                                                      })
                result.append({'user': user_id.id, 'name': user_id.name, 'login': user_id.login, 'password': otp,
                               'phone': user_id.phone, 'customerid': user_id.partner_id.id,
                               'customer_register': 'old', })
        else:
            if (user_old.name != kwargs['name']):
                edit_data = {
                             'name': kwargs['name']
                             }
                user_old.sudo().write(edit_data)
                user_id = request.env['res.users'].sudo().search([('id', '=', kwargs['userId'])], limit=1)
                if (user_old.partner_id.name != kwargs['name']):
                    user_old.partner_id.sudo().write({'email': kwargs['email']})
                result.append({'user': user_id.id, 'name': user_id.name, 'login': user_id.login, 'password': otp,
                               'phone': kwargs['phone'], 'customerid': user_id.partner_id.id,
                               'customer_register': 'old', })
        registerphone = {'updateaccount': result}
        return self._response('updateaccount', registerphone)


    @route('/mobikul/registerphone', csrf=False, type='http', auth="public", methods=['POST', 'GET'])
    def registerphone(self, **kwargs):

        result = []
        do_signup={}
        otp=kwargs['otp']
        phonenumber = unidecode(str(kwargs['phone']))
        if(kwargs['email']):
            do_signup = {'phone': phonenumber,
                         'login': kwargs['email'],
                         'name': kwargs['name'],
                         'sel_groups_1_8_9': '8',
                         }
        else:
            do_signup = {'phone': phonenumber,
                         'login': phonenumber,
                         'name': kwargs['name'],
                         'sel_groups_1_8_9': '8',
                         }
        user_id = request.env['res.users'].sudo().create(do_signup)
        user_id.partner_id.sudo().write({'country_id':192,'email':user_id.login})
        change_password_wizard = request.env['change.password.wizard'].sudo().create(
            {'user_ids': [(0, 0, {'user_id': user_id.id, 'new_passwd': otp})]})
        change_password_wizard.change_password_button()

        request.env.cr.execute(
            "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
            [user_id.id]
        )
        hashed = request.env.cr.fetchone()[0]
        result.append({'user': user_id.id, 'name':user_id.name,'login':user_id.login, 'password': otp,'phone': user_id.phone,'customerid':user_id.partner_id.id, 'customer_register': 'old', })

        registerphone = {'registerphone': result}
        return self._response('registerphone', registerphone)
    @route('/mobikul/loginphone', csrf=False, type='http', auth="public", methods=['POST','GET'])
    def loginphone(self,  **kwargs):
        phonenumber = kwargs['phone']
        phonenumber =unidecode(str(kwargs['phone']))
        print (phonenumber,'phonenumber')

        phone = int(phonenumber)
        phone2 = '966' + str(phone)
        otp = generateOTP()
        message=''
        Mtype=''
        mtype2=''
        values={}
        response = self._authenticate(True, **kwargs)
        local = response.get('context', {})
        lang_obj=local.get('lang_obj').iso_code
        user_id = request.env['res.users'].sudo().search([('phone', '=', phonenumber)], limit=1)
        if(user_id.id==105 ):
            otp='1234'
            print('otp :',otp)
        if(user_id.partner_id.fixed_otp):
            otp = "0410"
            print('otp2 :', otp)
        else:
            if (lang_obj == 'ar'):
                values = {'user': 'Mayarmarket',
                          'passwd': 'Mayar1234',
                          'message': 'كود التفعيل هو : ' + otp,
                          'mobilenumber': phone2,
                          'mtype': 'LNG',

                          }

            else:
                values = {'user': 'Mayarmarket',
                          'passwd': 'Mayar1234',
                          'message': 'Activation code is : ' + otp,
                          'mobilenumber': phone2,
                          'mtype': 'N',

                          }
        result = []


        if user_id:


            url = "http://www.smscountry.com/smscwebservice_bulk.aspx"

            data = urllib.parse.urlencode(values)
            data = data.encode('utf-8')
            request2 = urllib.request.Request(url, data)
            response2 = urllib.request.urlopen(request2)

            request.env.cr.execute(
                "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
                [user_id.id]
            )
            hashed = request.env.cr.fetchone()[0]
            change_password_wizard = request.env['change.password.wizard'].sudo().create(
                {'user_ids': [(0, 0, {'user_id': user_id.id, 'new_passwd': otp})]})
            change_password_wizard.change_password_button()
            result.append({'user': user_id.id, 'name': user_id.name,'login':user_id.login,'password': otp, 'phone': kwargs['phone'],
                           'customerid': user_id.partner_id.id, 'customer_register': 'old','otp_original': otp, })


        else:

            url = "http://www.smscountry.com/smscwebservice_bulk.aspx"
            data = urllib.parse.urlencode(values)
            data = data.encode('utf-8')
            request2 = urllib.request.Request(url, data)
            response2 = urllib.request.urlopen(request2)
            result.append({'phone': kwargs['phone'], 'otp_original': otp, 'customer_register': 'new', })
        loginphone = {'register': result}
        return self._response('loginphone', loginphone)


    @route('/mobikul/getSubCategories', csrf=False, type='http', auth="public", methods=['POST','GET'])
    def getSubCategories(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        mainCategoryid=kwargs['mainCategoryid']
        result = []
        all_cats = request.env['mobikul.category'].sudo().search([('parent_id.id', '=', mainCategoryid)])
        for cat in all_cats:
            result.append([{
                "id": cat.id,
                "name": cat.name,
                "image": _get_image_url(self.base_url, 'mobikul.category', cat.id, 'icon',
                                        cat.write_date),}])
        SubCategories={'SubCategories':result}
        #response.update(SubCategories)
        return self._response('SubCategories', SubCategories)

    @route('/mobikul/getSubCategories2', csrf=False, type='http', auth="public", methods=['POST', 'GET'])
    def getSubCategories2(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        Mobikul = response.get("context").get("mobikul_obj")
        mainCategoryid = kwargs['mainCategoryid']
        result = []

        all_cats = request.env['mobikul.category'].sudo().search([('parent_id.id', '=', mainCategoryid)])
        all_cats2 = request.env['mobikul.category'].sudo().search([('id', '=', mainCategoryid)])

        for cat in all_cats:
            result.append({
                "id": cat.id,
                "name": cat.name,
                "image": _get_image_url(self.base_url, 'mobikul.category', cat.id, 'icon',
                                        cat.write_date), })
        result.append({
            "id": all_cats2.id,
            "name": Mobikul.categories_all_name,
            "image": _get_image_url(self.base_url, 'mobikul.category', all_cats2.id, 'icon',
                                    all_cats2.write_date), })
        SubCategories = {'SubCategories': result}
        # response.update(SubCategories)
        return self._response('SubCategories', SubCategories)
    @route('/mobikul/splashPageData', csrf=False, type='http', auth="none", methods=['POST'])
    def getSplashPageData(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        if response.get('success'):
            Mobikul = response.get("context").get("mobikul_obj")
            if 'login' in self._lcred:
                result = Mobikul.authenticate(self._lcred, True, self._sLogin, context={
                    'base_url': self.base_url})
                response.update(result)
            result = Mobikul.getDefaultData()
            response.update(result)
            response['sortData'] = [
                ("Price: High to Low", "price desc"),
                ("Price: Low to High", "price asc"),
                ("Discounts", "id asc"),
                ("Popularity", "id asc"),
                ("Newest First", "id desc"),
            ]
            response['message'] = "Splash Data."
            response.update(self._languageData(Mobikul))
            if response.get('addons', {}).get('review'):
                response['RatingStatus'] = [
                    ("1", _("Poor")),
                    ("2", _("Ok")),
                    ("3", _("Good")),
                    ("4", _("Very Good")),
                    ("5", _("Excellent")),
                ]
        return self._response('splashPageData', response)

    @route('/mobikul/customer/login', csrf=False, type='http', auth="none", methods=['POST'])
    def login(self, **kwargs):
        kwargs['detailed'] = True
        response = self._authenticate(True, **kwargs)
        self._tokenUpdate(customer_id=response.get('customerId'))
        return self._response('login', response)

    @route('/mobikul/customer/signOut', csrf=False, type='http', auth="none", methods=['POST'])
    def signOut(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        if response.get('success'):
            response['message'] = "Have a Good Day !!!"
            self._tokenUpdate()
        return self._response('signOut', response)

    @route('/mobikul/customer/signUp', csrf=False, type='http', auth="public", methods=['POST'])
    def signUp(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        if response.get('success'):
            createNotification = False
            Mobikul = response.get("context").get("mobikul_obj")
            result = Mobikul.signUp(self._mData)
            response.update(result)
            if response['success'] and response.get('addons', {}).get('email_verification'):
                if not self._mData.get('authUserId', False):
                    response["message"] = _(
                        "An email has been sent to your email address. Please verify it.")
                    createNotification = True
            if response['success']:
                context = response.get("context")
                #homepage = {}

                login = {}
                if self._mData.get('authUserId', False):
                    cred = {'authUserId': self._mData.get(
                        'authUserId', ""), 'authProvider': self._mData.get('authProvider', "")}
                else:
                    cred = {'login': self._mData.get(
                        'login', ""), 'pwd': self._mData.get('password', "")}
                login = Mobikul.authenticate(cred, True, self._sLogin,
                                             context=context)
                _logger.info("++++++++%r",login)
                if login['context']:
                    del login['context']
                response.update({"login": login, "cred": cred})
                homepage = Mobikul.homePage(self._mData, context)
                homepage.update(self._languageData(Mobikul))
                response.update({"homepage": homepage})
            self._tokenUpdate(customer_id=response.get('customerId'))
            if response.get("message", "").startswith("Created"):
                createNotification = True
            if createNotification:
                self._pushNotification(self._mData.get("fcmToken", ""),
                                       customer_id=response.get('customerId'))
        return self._response('signUp', response)

    @route('/mobikul/customer/resetPassword', csrf=False, type='http', auth="none", methods=['POST'])
    def resetPassword(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        if response.get('success'):
            Mobikul = request.env['mobikul'].sudo()
            result = Mobikul.resetPassword(self._mData.get('login', False))
            response.update(result)
        return self._response('resetPassword', response)


    @route('/mobikul/homepage', csrf=False, type='http', auth="public", methods=['POST'])
    def getHomepage(self, **kwargs):
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            Mobikul = response.get("context").get("mobikul_obj")
            response.update(self._languageData(Mobikul))
            result = Mobikul.homePage(self._mData, response.get("context"))
            response.update(result)
            response['message'] = "Homepage Data."
            if(response.get('customerId')):
                self._tokenUpdate(customer_id=response.get('customerId'))
            if response.get('addons', {}).get('wishlist') and response.get('customerId'):
                response['wishlist'] = self._website_Wishlist(response.get('customerId'))
        return self._response('homepage', response)

    @route('/mobikul/search', csrf=False, type='http', auth="public", methods=['POST'])
    def getSearchData(self, **kwargs):
        global result, result
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)

        else:
            response = self._authenticate(False, **kwargs)

        if response.get('success'):
            Mobikul = response.get("context").get("mobikul_obj")
            result = Mobikul.fetch_products(context=response.get("context"), **self._mData)
            response['offset'] = result.get('offset')
            response['tcount'] = result.get('tcount')

            # response.update(result)
            # response['message'] = "Search result."

        if response.get('addons', {}).get('wishlist') and response.get('customerId'):
                response['wishlist'] = self._website_Wishlist(response.get('customerId'))

        new_product = []

        isWishlist = False
        if response.get('customerId'):
            local = response.get('context', {})
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            last_order = Partner.last_mobikul_so_id

            if(len(result.get('products'))>0):
                for product in result.get('products'):
                    isOffer=False
                    offerPrice=0.0,
                    msgOffer=""

                    today = datetime.today()
                    #offer=request.env['discount.offer'].sudo().search([('product_id.id','=',int(product.get('productId'))),('date_start', '>', today), ('date_end', '<=', today)],limit=1)
                    offer=request.env['discount.offer'].sudo().search([('product_id.id','=',int(product.get('productId'))),('date_start', '<=', today),('date_end', '>=', today)],limit=1)

                    if(offer):

                        isOffer = True
                        offerPrice = offer.priceAfteroffer
                        msgOffer = offer.name

                    productImage=[]
                    productImage.append(product.get('thumbNail'))
                    product_id_id = product.get('productId')
                    images_products = request.env['product.image'].sudo().search([('product_tmpl_id', '=',product_id_id)])
                    if(len(images_products)>0):
                        for image in images_products:
                            if(image.image_1920):
                                productImage.append( _get_image_url(self.base_url, 'product.image', image.id, 'image_1920',
                                                            image.write_date))


                    wishlistObj = request.env['product.wishlist'].sudo()
                    wishlistdata = wishlistObj.search([('product_id', '=',product_id_id),('partner_id', '=', response.get('customerId'))],limit=1)

                    if(len(wishlistdata)>0):
                        isWishlist=True
                    else:
                        isWishlist = False
                    product_id=[]
                    if(last_order):
                        product_id = last_order.order_line.sudo().search([('product_id', '=', product_id_id),('order_id','=',last_order.id)], limit=1)
                    if (len(product_id) > 0):
                        cart_qty = product_id.product_uom_qty
                        lineId=product_id.id
                        new_product.append({
                            'templateId': product.get('templateId'),
                            'name': product.get('name'),
                            'priceUnit': product.get('priceUnit'),
                            'priceReduce': product.get('priceReduce'),
                            'productId': product.get('productId'),
                            'productCount': product.get('productCount'),
                            'description': product.get('description'),
                            'uomQty': product.get('uomQty'),
                            'qtyAvailable': product.get('qtyAvailable'),
                            'thumbNail': product.get('thumbNail'),
                            'cartQty': cart_qty,
                            'lineId':lineId,
                            'isWishlist':isWishlist,
                            'productImages': productImage,
                            'isOffer' : isOffer,
                            'offerPrice': _displayWithCurrency(local.get('lang_obj'), offerPrice,
                                                 local.get('currencySymbol', ""),
                                                 local.get('currencyPosition', "")),

                             'msgOffer' : msgOffer,

                        })

                    else:
                        cart_qty = 0
                        lineId=0

                        new_product.append({
                            'templateId': product.get('templateId'),
                            'name': product.get('name'),
                            'priceUnit': product.get('priceUnit'),
                            'priceReduce': product.get('priceReduce'),
                            'productId': product.get('productId'),
                            'productCount': product.get('productCount'),
                            'description': product.get('description'),
                            'uomQty': product.get('uomQty'),
                            'qtyAvailable': product.get('qtyAvailable'),
                            'thumbNail': product.get('thumbNail'),
                            'cartQty': cart_qty,
                            'lineId':lineId,
                            'isWishlist':isWishlist,
                            'productImages':productImage,
                            'isOffer': isOffer,
                            'offerPrice': _displayWithCurrency(local.get('lang_obj'), offerPrice,
                                                 local.get('currencySymbol', ""),
                                                 local.get('currencyPosition', "")),
                            'msgOffer': msgOffer,
                        })
            else:
                response['success'] = False
            new_product = {'products': new_product}
            response.update(new_product)
            response['message'] = "Search result."
        else:
            if(len(result.get('products'))>0):
                for product in result.get('products'):
                    isOffer = False
                    offerPrice = 0.0,
                    msgOffer = ""

                    today = datetime.today()
                    # offer=request.env['discount.offer'].sudo().search([('product_id.id','=',int(product.get('productId'))),('date_start', '>', today), ('date_end', '<=', today)],limit=1)
                    offer = request.env['discount.offer'].sudo().search(
                        [('product_id.id', '=', int(product.get('productId'))), ('date_start', '<=', today),
                         ('date_end', '>=', today)], limit=1)

                    if (offer):
                        isOffer = True
                        offerPrice = offer.priceAfteroffer
                        msgOffer = offer.name

                    cart_qty = 0
                    lineId = 0
                    productImage = []
                    productImage.append(product.get('thumbNail'))
                    product_id_id = product.get('productId')
                    images_products = request.env['product.image'].sudo().search([('product_tmpl_id', '=', product_id_id)])
                    local = response.get('context', {})
                    if (len(images_products) > 0):
                        for image in images_products:
                            if (image.image_1920):
                                productImage.append(_get_image_url(self.base_url, 'product.image', image.id, 'image_1920',
                                                            image.write_date))

                    isWishlist = False
                    new_product.append({
                        'templateId': product.get('templateId'),
                        'name': product.get('name'),
                        'priceUnit': product.get('priceUnit'),
                        'priceReduce': product.get('priceReduce'),
                        'productId': product.get('productId'),
                        'productCount': product.get('productCount'),
                        'description': product.get('description'),
                        'uomQty': product.get('uomQty'),
                        'qtyAvailable': product.get('qtyAvailable'),
                        'thumbNail': product.get('thumbNail'),
                        'cartQty': cart_qty,
                        'lineId':lineId,
                        'isWishlist':isWishlist,
                        'productImages': productImage,
                        'isOffer': isOffer,
                        'offerPrice': _displayWithCurrency(local.get('lang_obj'), offerPrice,
                                                           local.get('currencySymbol', ""),
                                                           local.get('currencyPosition', "")),
                        'msgOffer': msgOffer,
                    })
            else:
                response['success'] = False
            new_product = {'products': new_product}
            response.update(new_product)
            response['message'] = "Search result."
        return self._response('search', response)


















    @route(['/mobikul/sliderProducts/<int:slider_id>'], type='http', auth="public", csrf=False, methods=['GET', 'POST'])
    def getSliderProducts(self, slider_id, **kwargs):
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('addons', {}).get('wishlist') and response.get('customerId'):
            response['wishlist'] = self._website_Wishlist(response.get('customerId'))
        if response.get('success'):
            PSlider = request.env['mobikul.product.slider'].sudo().search([('id', '=', slider_id)])
            if PSlider:
                context = response.get("context")
                context.update({
                    'limit': response.get('itemsPerPage', 5),
                    'offset': self._mData.get('offset', 0),
                    'order': self._mData.get('order', None),
                })
                response.update(PSlider.get_product_data(context))
                response['message'] = "Product slider ."
            else:
                response.update({'success': False, 'message': 'Product Slider not found !!!'})
        return self._response('sliderProducts', response)

    @route('/mobikul/template/<int:template_id>', csrf=False, type='http', auth="public", methods=['POST'])
    def getTemplateData(self, template_id, **kwargs):
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        local = response.get('context', {})
        if response.get('success'):
            wishlist = []
            if response.get('addons', {}).get('wishlist') and response.get('customerId'):
                wishlist = self._website_Wishlist(response.get('customerId', 0))
            TemplateObj = request.env['product.template'].sudo()
            Template = TemplateObj.search([('id', '=', template_id)])
            if Template:
                result = {
                    'templateId'	: Template.id,
                    'name'			: Template.name or "",
                    'attributes'	: [],
                    "images": [],
                    "message": "Template detail."
                }
                if response.get('addons', {}).get('review'):
                    result.update({
                        'avg_rating': Template.avg_review(),
                        'total_review': len(Template.fetch_active_review(Template.id))
                    })
                if response.get('addons', {}).get('odoo_marketplace'):
                    if Template.marketplace_seller_id and Template.marketplace_seller_id.website_published:
                        result.update({
                            'seller_info': {
                                'seller_profile_url'	: "/myTemplateseller/%s" % Template.marketplace_seller_id.id,
                                'marketplace_seller_id'	: Template.marketplace_seller_id.id,
                                'seller_name'			: Template.marketplace_seller_id.name,
                                'seller_profile_image'	: self.get_marketplace_image_url(self.base_url, 'res.partner', Template.marketplace_seller_id.id, 'profile_image', Template.marketplace_seller_id.write_date),
                                'average_rating'		: Template.marketplace_seller_id.avg_review(),
                                'total_reviews'			: len(Template.marketplace_seller_id.seller_review_ids.filtered(lambda r: (r.active == True and r.state == "pub"))),
                                'message'				: str(Template.marketplace_seller_id.total_active_recommendation()[1])+" positive feedback (%s ratings)" % Template.marketplace_seller_id.avg_review()
                            }
                        })
                    else:
                        result.update({
                            'seller_info': None
                        })
                prd_images = [_get_image_url(
                    self.base_url, 'product.image', im.id, 'image_1920', im.write_date) for im in Template.product_template_image_ids]
                for ali in Template.attribute_line_ids:
                    temp = {
                        "name": ali.attribute_id.name or "",
                        "attributeId": ali.attribute_id.id,
                        "type": ali.attribute_id.display_type,
                        "newVariant": ali.attribute_id.create_variant,
                        "values": []
                    }
                    for v in ali.value_ids:
                        temp["values"].append({
                            "name": v.name or "",
                            "valueId": v.id,
                            "htmlCode": v.html_color or "",
                            "newVariant": ali.attribute_id.create_variant,
                        })
                    result['attributes'].append(temp)

                comb_info = Template._get_combination_info(combination=False, product_id=False,add_qty=1, pricelist=local.get("pricelist"), parent_combination=False, only_template=False)
                result.update({
                    'priceUnit'		: _displayWithCurrency(local.get('lang_obj'), comb_info['has_discounted_price'] and comb_info['list_price'] or comb_info['price'], local.get('currencySymbol'), local.get('currencyPosition')),
                    'priceReduce'	: comb_info['has_discounted_price'] and _displayWithCurrency(local.get('lang_obj'), comb_info['price'], local.get('currencySymbol'), local.get('currencyPosition')) or "",
                    'productId'		: Template.product_variant_id and Template.product_variant_id.id or '',
                    'productCount'	: Template.product_variant_count,
                    'description'	: Template.description_sale or "",
                    "alternativeProducts": [{
                        "templateId": product.id,
                        "name": product.name,
                        "image": _get_image_url(self.base_url, 'product.template', product.id, 'image_1024', product.write_date),
                    }
                        for product in Template.alternative_product_ids
                    ],
                    'thumbNail'		: _get_image_url(self.base_url, 'product.template', Template.id, 'image_1920', Template.write_date),
                    'images'		: [_get_image_url(self.base_url, 'product.template', Template.id, 'image_1920', Template.write_date)] + prd_images,
                    'absoluteUrl': '%sshop/product/%s' % (self.base_url, slug(Template)),
                    "addedToWishlist": Template.product_variant_id.id in wishlist,
                    'variants'	: []
                })
                if Template.product_variant_count > 1:
                    for var in Template.product_variant_ids:
                        comb_info = Template._get_combination_info(combination=False, product_id=var.id,add_qty=1, pricelist=local.get("pricelist"), parent_combination=False, only_template=False)
                        temp = {
                            "productId": var.id,
                            'images': [_get_image_url(self.base_url, 'product.product', var.id, 'image_1920', var.write_date)] + prd_images,
                            'absoluteUrl': '%sshop/product/%s' % (self.base_url, slug(var)),
                            'priceReduce': comb_info['has_discounted_price'] and _displayWithCurrency(local.get('lang_obj'), comb_info['price'], local.get('currencySymbol'), local.get('currencyPosition')) or "",
                            'priceUnit': _displayWithCurrency(local.get('lang_obj'), comb_info['has_discounted_price'] and comb_info['list_price'] or comb_info['price'], local.get('currencySymbol'), local.get('currencyPosition')),
                            "combinations": [],
                            "addedToWishlist": var.id in wishlist,
                        }
                        for ptavi in var.product_template_attribute_value_ids:
                            temp["combinations"].append({
                                "valueId": ptavi.product_attribute_value_id and ptavi.product_attribute_value_id.id,
                                "attributeId": ptavi.attribute_id and ptavi.attribute_id.id,
                            })
                        result['variants'].append(temp)
            else:
                result = {'success': False, 'message': 'Template not found !!!'}
            response.update(result)
        return self._response('template', response)

    @route('/mobikul/my/promoCode', csrf=False, type='http', auth="none", methods=['POST'])
    def getMyPromoCode(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            if Partner:
                result = {}
                local = response.get('context', {})


                if self._mData.get('promoCode'):
                    promoCode = self._mData.get('promoCode')
                    promo = request.env['sale.coupon.program'].sudo().search([('promo_code','=',promoCode)],limit=1)
                    promoData=[]
                    if(promo):
                        if(promo.rule_date_from or promo.rule_date_to):
                            today = datetime.today()
                            if((promo.rule_date_from<= today)and(promo.rule_date_to >= today)):
                                promoData.append({'name': promo.name, 'promoCode': promo.promo_code})
                                result = {'success': True,'promoData':promoData}

                            else:
                                result = {'success': False, }


                        else:
                            promoData.append({'name':promo.name,'promoCode':promo.promo_code})
                            result = {'success': True,'promoData':promoData}
                    else:
                        result = {'success': False, }
                else:
                    result = {'success': False, }
                response.update(result)

        return self._response('promCode', response)

    @route('/mobikul/my/orders', csrf=False, type='http', auth="none", methods=['POST'])
    def getMyOrders(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            if Partner:
                result = {}
                local = response.get('context', {})
                #_logger.info("+++++++ %r",local)
                fields = ['name', 'create_date', 'state', 'amount_total', 'partner_shipping_id','customer_state','font','background','delivery_boy','delivery_boy_phone','delivery_method']
                SaleOrder = request.env['sale.order'].sudo()
                #date = Datetime.convert_to_display_name()
                domain = [
                    ('partner_id', '=', Partner.id),
                    ('state', 'not in', ('sent','draft'))
                ]
                if self._mData.get('date_from', False) and self._mData.get('date_to', False):
                    domain += [('create_date', '>', self._mData.get('date_from')),
                               ('create_date', '<=', self._mData.get('date_to'))]

                result['tcount'] = SaleOrder.search_count(domain)
                orders = SaleOrder.search_read(domain, limit=1000, offset=self._mData.get('offset', 0), order="id desc", fields=fields)
                # orders = SaleOrder.search_read(domain, limit=self._mData.get('limit', response.get(
                #     'itemsPerPage', 5)), offset=self._mData.get('offset', 0),  order="id desc", fields=fields)
                result['recentOrders'] = []
                state_value = dict(SaleOrder.fields_get(["state"],['selection'])['state']["selection"])
                customer_state_value = dict(SaleOrder.fields_get(["customer_state"],['selection'])['customer_state']["selection"])


                for order in orders:
                    ShippingAdd = PartnerObj.search([('id', '=', order['partner_shipping_id'][0])])
                    phone=''
                    pickup=True
                    if(order['delivery_boy_phone']):
                        phone = order['delivery_boy_phone']
                        phone='+966'+phone
                    if (order['delivery_method']):
                        delivery_method=request.env['delivery.carrier'].sudo().search([('id','=',int(order['delivery_method'][0]))])
                        pickup=delivery_method.pickup


                    temp = {
                        'id': order['id'],
                        'name': order['name'] or "",
                        'create_date': Datetime.convert_to_display_name(Datetime,order['create_date'],Partner),
                        'shipping_address': ShippingAdd and self.mobikul_display_address(ShippingAdd._display_address(), ShippingAdd.name) or "",
                        'shipAdd_url': ShippingAdd and '/mobikul/my/address/%s' % ShippingAdd.id or "",
                        'amount_total': _displayWithCurrency(local.get('lang_obj'), order['amount_total'], local.get('currencySymbol', ""), local.get('currencyPosition', "")),
                        #'status': state_value[order['state']],
                        'status': customer_state_value[order['customer_state']],
                        'font': order['font'],
                        'background': order['background'],
                        'deliveryBoyPhone':phone,
                        'pickup':pickup,
                        'canReorder': True,
                        'url': "/mobikul/my/order/%s" % order['id'],
                    }
                    #date = Datetime.convert_to_display_name(Datetime,order['create_date'],Partner)
                    #_logger.info("DATE--------%r",date)
                    result['recentOrders'].append(temp)
                    result['message'] = "Orders lists."
            else:
                result = {'success': False, 'message': 'Customer not found !!!'}
            response.update(result)
        return self._response('orders', response)

    @route('/mobikul/deliveryBoyLocation/<int:order_id>', csrf=False, type='http', auth="none", methods=['POST'])
    def deliveryBoyLocation(self, order_id, **kwargs):
        response = self._authenticate(True, **kwargs)
        result={}

        if response.get('success'):
            result.update({'message':response.get('message'),'success': True,})


            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            orderObj = request.env['sale.order'].sudo()
            Order = orderObj.search([('id', '=', order_id)])
            state_value = dict(orderObj.fields_get(["state"],['selection'])['state']["selection"])
            customer_state_value = dict(orderObj.fields_get(["customer_state"], ['selection'])['customer_state']["selection"])
            if Order:
                phone = ''
                if (Order.delivery_boy_phone):
                    phone = Order.delivery_boy_phone
                local = response.get('context', {})
                result.update({
                    'status': customer_state_value[Order.customer_state],
                    'latitude': Order.delivery_boy.partner_latitude or 0.0,
                    'longitude':Order.delivery_boy.partner_longitude or 0.0,
                    'accuracy' : Order.delivery_boy.accuracy or 0.0,
                    'altitude' :  Order.delivery_boy.altitude or 0.0,
                    'altitudeAccuracy' :  Order.delivery_boy.altitudeAccuracy or 0.0,
                    'heading' : Order.delivery_boy.heading or 0.0,
                    'speed' :  Order.delivery_boy.speed or 0.0,
                })
            else:
                result.update( {'success': False, 'message': 'Order not found !!!'})
            response.update(result)
        return self._response('deliveryBoyLocation', result)

    @route('/mobikul/my/order/<int:order_id>', csrf=False, type='http', auth="none", methods=['POST'])
    def getMyOrder(self, order_id, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            Mobikul = request.env['mobikul.terms'].sudo().search([], limit=1)
            orderObj = request.env['sale.order'].sudo()
            Order = orderObj.search([('id', '=', order_id)])
            state_value = dict(orderObj.fields_get(["state"], ['selection'])['state']["selection"])
            customer_state_value = dict(
                orderObj.fields_get(["customer_state"], ['selection'])['customer_state']["selection"])
            if Order:
                phone = ""
                pickup_location=""
                pickup=False
                pickup_latitude=""
                pickup_longitude=""
                pickupPhone=""
                if (Order.delivery_boy_phone):
                    phone = Order.delivery_boy_phone
                    phone="+966"+phone
                if(Order.delivery_method.pickup):
                    pickup=Order.delivery_method.pickup
                    if (Order.warehouse_id):
                        pickup_latitude=Order.warehouse_id.partner_id.partner_latitude
                        pickup_longitude = Order.warehouse_id.partner_id.partner_longitude
                        pickupPhone= Order.warehouse_id.partner_id.phone
                        pickup_location='https://www.google.com/maps/?q='+str(pickup_latitude)+','+str(pickup_longitude)

                local = response.get('context', {})

                result = {
                    'name': Order.name or "",
                    'create_date': Datetime.convert_to_display_name(Datetime, Order.create_date, Partner) or "",
                    'amount_total': _displayWithCurrency(local.get('lang_obj'), Order.amount_total,
                                                         local.get('currencySymbol', ""),
                                                         local.get('currencyPosition', "")),
                    # 'status': state_value[Order.state],
                    'status': customer_state_value[Order.customer_state],
                    'amount_untaxed': _displayWithCurrency(local.get('lang_obj'), Order.amount_untaxed,
                                                           local.get('currencySymbol', ""),
                                                           local.get('currencyPosition', "")),
                    'amount_tax': _displayWithCurrency(local.get('lang_obj'), Order.amount_tax,
                                                       local.get('currencySymbol', ""),
                                                       local.get('currencyPosition', "")),
                    'shipping_address': self.mobikul_display_address(Order.partner_shipping_id._display_address(),
                                                                     Order.partner_shipping_id.name),
                    'shipAdd_url': '/mobikul/my/address/%s' % Order.partner_shipping_id.id,
                    'billing_address': self.mobikul_display_address(Order.partner_invoice_id._display_address(),
                                                                    Order.partner_invoice_id.name),
                    'font': Order.font,
                    'background': Order.background,
                    'deliveryBoyPhone':phone,
                    'deliveryBoyName': str(Order.delivery_boy.name) or "",
                    'latitude': str(Order.delivery_boy.partner_latitude),
                    'longitude': str(Order.delivery_boy.partner_longitude),
                    'pickupLocation':str(pickup_location),
                    'pickup':pickup,
                    'pickupLatitude':str(pickup_latitude),
                    'pickupLongitude':str(pickup_longitude),
                    'pickupPhone':str(pickupPhone),
                    'whatsAppPhone':str(Mobikul.whatsapp_phone)

                }
                result['items'] = []

                for line in Order.order_line:
                    if response.get('addons', {}).get('website_sale_delivery') and line.is_delivery:
                        shippingMethod = {
                            "tax": [tax.name for tax in line.tax_id],
                            "name": line.order_id.carrier_id.name,
                            "description": line.order_id.carrier_id.website_description or "",
                            "shippingId": line.order_id.carrier_id.id,
                            "total": _displayWithCurrency(local.get('lang_obj'), line.price_subtotal,
                                                          local.get('currencySymbol'), local.get('currencyPosition')),
                        }
                        result.update({"delivery": shippingMethod})
                    else:

                        temp = {
                            'name': line.product_id.name or "",
                            'product_name': line.product_id.name or "",
                            'qty': "%s %s" % (line.product_uom_qty, line.product_uom.name),
                            'price_unit': _displayWithCurrency(local.get('lang_obj'), line.price_unit,
                                                               local.get('currencySymbol', ""),
                                                               local.get('currencyPosition', "")),
                            'price_subtotal': _displayWithCurrency(local.get('lang_obj'), line.price_subtotal,
                                                                   local.get('currencySymbol', ""),
                                                                   local.get('currencyPosition', "")),
                            'price_tax': _displayWithCurrency(local.get('lang_obj'), line.price_tax,
                                                              local.get('currencySymbol', ""),
                                                              local.get('currencyPosition', "")),
                            'price_total': _displayWithCurrency(local.get('lang_obj'), line.price_total,
                                                                local.get('currencySymbol', ""),
                                                                local.get('currencyPosition', "")),
                            'discount': "%s" % (line.discount and "%s %%" % line.discount or ""),
                            'state': state_value[line.state],
                            'thumbNail'	: _get_image_url(self.base_url, 'product.product', line.product_id and line.product_id.id or "", 'image_1920', line.product_id and line.product_id.write_date),
                            "templateId": line.product_id and line.product_id.product_tmpl_id.id or "",
                        }
                        result['items'].append(temp)
                        result['message'] = "Order details."
            else:
                result = {'success': False, 'message': 'Order not found !!!'}
            response.update(result)
        return self._response('orders', response)
    @route('/mobikul/my/reorder/<int:order_id>', csrf=False, type='http', auth="none", methods=['POST'])
    def getreMyOrder(self, order_id, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            Mobikul = response.get("context").get("mobikul_obj")
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            last_order = Partner.last_mobikul_so_id
            local = response.get('context', {})
            orderObj = request.env['sale.order'].sudo()
            Order = orderObj.search([('id', '=', order_id)])
            state_value = dict(orderObj.fields_get(["state"], ['selection'])['state']["selection"])
            customer_state_value = dict(
                orderObj.fields_get(["customer_state"], ['selection'])['customer_state']["selection"])
            result = {}
            if(last_order):
                print('hello')
            else:
                #result = Mobikul._create_so2(Partner,response.get("context"))
                context=response.get("context")
                addr = Partner.address_get(['delivery'])
                so_data = {
                    'partner_id': Partner.id,
                    'pricelist_id': context.get('pricelist').id,
                    'payment_term_id': Partner.property_payment_term_id.id,
                    'team_id': context.get("teamId"),
                    'partner_invoice_id': Partner.id,
                    'partner_shipping_id': addr['delivery'],
                    'user_id': context.get("salespersonId"),
                }

                company = context.get("pricelist").company_id

                # if company:
                #     so_data['company_id'] = company.id
                new_order = request.env['sale.order'].sudo(1).create(so_data)

                Partner.write({'last_mobikul_so_id': new_order.id})



            if Order:
                for line in Order.order_line:
                    if (response.get('addons', {}).get('website_sale_delivery') and line.is_delivery) or (line.product_id.sale_ok != True) :
                        shippingMethod = {}

                    else:
                        result2 = Mobikul.add_to_cart(line.product_id.id, self._mData.get("set_qty"),
                                                      line.product_uom_qty, response.get("context"))
                result = {'success': True, 'message': 're Order success !!!'}
            else:
                result = {'success': False, 'message': 'Order not found !!!'}
            response.update(result)
        return self._response('orders', response)



    @route('/mobikul/my/parking/<int:order_id>', csrf=False, type='http', auth="none", methods=['POST','PUT'])
    def getparking(self, order_id, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            Mobikul = response.get("context").get("mobikul_obj")
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            orderObj = request.env['sale.order'].sudo()
            Order = orderObj.search([('id', '=', order_id)])
            state_value = dict(orderObj.fields_get(["state"], ['selection'])['state']["selection"])
            customer_state_value = dict(
                orderObj.fields_get(["customer_state"], ['selection'])['customer_state']["selection"])
            if Order:

                phone = ''
                warehouse_id = Order.warehouse_id
                if (Order.delivery_boy_phone):
                    phone = Order.delivery_boy_phone
                pickup_location = ''
                if (Order.delivery_method.pickup):
                    pickup = Order.delivery_method.pickup
                    if (Order.warehouse_id):
                        partner_latitude = Order.warehouse_id.partner_id.partner_latitude
                        partner_longitude = Order.warehouse_id.partner_id.partner_longitude
                        pickup_location = 'https://www.google.com/maps/?q=' + str(partner_latitude) + ',' + str(
                            partner_longitude)
                local = response.get('context', {})
                result={}
                result['parking'] = []
                if request.httprequest.method in ["POST"]:
                    for line in warehouse_id.parking:
                        if (line.state == 'available'):
                            temp = {'parkingId': line.id, 'name': line.name, 'orderId': Order.id}
                            result['parking'].append(temp)
                    result.update({'success': True, 'message': 'parking success !!!'})
                if request.httprequest.method in ["PUT"]:
                    result.pop('parking')
                    response.pop('addons')
                    parking = request.env['pickup.location.parking'].sudo().search([('id','=',int(self._mData.get('parkingId', 0)))])
                    parking.sudo().write({'state':'notavailable','partner_id':Order.partner_id.id,'sale_order':Order.id})
                    result.update({'success': True, 'message': 'put parking success !!!'})


            else:
                result = {'success': False, 'message': 'Order not found !!!'}
            response.update(result)
        return self._response('orders', response)



    @route('/mobikul/my/addresses', csrf=False, type='http', auth="none", methods=['POST'])
    def getMyAddresses(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            Partner = response.get("context").get("partner")
            PartnerObj = request.env['res.partner'].sudo()
            if Partner:
                result = {}
                domain = [
                    ('id', 'child_of', Partner.commercial_partner_id.ids),
                    ('id', 'not in', [Partner.id]),('type','=','delivery'),
                ]
                result['tcount'] = PartnerObj.search_count(domain) + 1
                addresses = PartnerObj.search(domain, limit=self._mData.get('limit', response.get(
                    'itemsPerPage', 5)), offset=self._mData.get('offset', 0),  order="id desc")
                # result['addresses'] = [
                #     {
                #         'name': Partner.name,
                #         'url': "/mobikul/my/address/%s" % Partner.id,
                #         'addressId': Partner.id,
                #     }
                # ]
                # if self._checkFullAddress(Partner):
                #     result['addresses'][0]['display_name'] = self.mobikul_display_address(
                #         Partner._display_address(), Partner.name)
                # else:
                #     result['addresses'][0]['display_name'] = EMPTY_ADDRESS
                # in result['addresses'][0] zero index address is billing address other is shipping address

                result['addresses'] = []
                if(len(addresses)>0):
                    for address in addresses:
                        temp = {
                            'name': address.name,
                            'display_name': address._display_address() != EMPTY_ADDRESS and self.mobikul_display_address(
                                address._display_address(), address.name) or address._display_address(),
                            'latitude': str(address.partner_latitude) or "",
                            'longitude': str(address.partner_longitude) or "",
                            'url': "/mobikul/my/address/%s" % address.id,
                            'addressId': address.id,

                        }
                        result['addresses'].append(temp)
                        result['message'] = "Address lists"
                else:
                    result['message'] = "EMPTY ADDRESS"




            else:
                result = {'success': False, 'message': 'Customer not found !!!'}
            response.update(result)
        return self._response('orders', response)

    @route('/mobikul/my/address/default/<int:address_id>', csrf=False, type='http', auth="none", methods=['PUT'])
    def setDefaultAddress(self, address_id, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            PartnerObj = request.env['res.partner'].sudo()
            Address = PartnerObj.search([('id', '=', address_id)])
            if Address:
                response.update({'message': 'Updated successfully.'})
            else:
                response.update({'success': False, 'message': 'Address not found !!!'})
        return self._response('address', response)

    @route('/mobikul/my/address/new', csrf=False, type='http', auth="public", methods=['POST'])
    def addMyAddress(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            PartnerObj = request.env['res.partner'].sudo()
            vals = {
                "name": self._mData.get('name', ""),
                "street": self._mData.get('street', ""),
                "zip": self._mData.get('zip', ""),
                "city": self._mData.get('city', ""),
                "phone": self._mData.get('phone', ""),
                "comment": self._mData.get('comment', ""),

                # "customer": 1,
                "type": "delivery",
                "commercial_partner_id": int(response.get('customerId')),
                "parent_id": int(response.get('customerId')),
            }
            if(self._mData.get('latitude')):
               vals["partner_latitude"] = float(self._mData["latitude"])
               vals["partner_longitude"] = float(self._mData["longitude"])

            try:
                if self._mData.get("state_id"):
                    if request.env['res.country.state'].sudo().browse(int(self._mData["state_id"])).exists():
                        vals["state_id"] = int(self._mData["state_id"])
                if self._mData.get("country_id"):
                    if request.env['res.country'].sudo().browse(int(self._mData["country_id"])).exists():
                        vals["country_id"] = int(self._mData["country_id"])

                vals["country_id"] = int(192)


                PartnerObj.create(vals)
                result = {'message': 'Created successfully.'}
            except Exception as e:
                result = {'success': False, 'message': 'Error: Invalid Data < %r >' % e}
            response.update(result)
        return self._response('address', response)

    @route('/mobikul/my/address/<int:address_id>', csrf=False, type='http', auth="none", methods=['POST', 'PUT', 'DELETE'])
    def getMyAddress(self, address_id, **kwargs):
        global result
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            PartnerObj = request.env['res.partner'].sudo()
            Address = PartnerObj.search([('id', '=', address_id)])
            if Address:
                if request.httprequest.method in ["POST"]:
                    result = {
                        'name': Address.name or "",
                        'street': Address.street or "",
                        'zip': Address.zip or "",
                        'city': Address.city or "",
                        'state_id': Address.state_id and Address.state_id.id or "",
                        # 'country_id': Address.country_id and Address.country_id.id or "",
                        'country_id': Address.country_id.name  or "",
                        'phone': Address.phone or "",
                        "comment":Address.comment or "",
                        "latitude":str(Address.partner_latitude),
                        "longitude": str(Address.partner_longitude),
                    }
                elif request.httprequest.method == "PUT":
                    Address.name = self._mData.get('name', Address.name)
                    Address.street = self._mData.get('street', Address.street)
                    Address.zip = self._mData.get('zip', Address.zip)
                    Address.city = self._mData.get('city', Address.city)
                    Address.phone = self._mData.get('phone', Address.phone)
                    Address.comment = self._mData.get('comment', Address.comment)
                    Address.partner_latitude= self._mData.get('latitude', Address.partner_latitude)
                    Address.partner_longitude= self._mData.get('longitude',  Address.partner_longitude)

                    try:
                        if self._mData.get("state_id"):
                            if request.env['res.country.state'].sudo().browse(int(self._mData["state_id"])).exists():
                                Address.state_id = int(self._mData["state_id"])
                        if self._mData.get("country_id"):
                            if request.env['res.country'].sudo().browse(int(self._mData["country_id"])).exists():
                                Address.country_id = int(self._mData["country_id"])
                        result = {'message': 'Updated successfully.'}
                    except Exception as e:
                        result = {'success': False, 'message': 'Error: Invalid Data'}
                elif request.httprequest.method == "DELETE":
                    if response.get('customerId') != address_id:
                        Address.active = False
                        result = {'message': 'Deleted successfully.'}
                    else:
                        result = {'success': False, 'message': _(
                            'Error: You can`t delete Billing Address.')}
            else:
                result = {'success': False, 'message': 'Address not found !!!'}
            response.update(result)
        return self._response('address', response)

    @route('/mobikul/my/account', csrf=False, type='http', auth="none", methods=['POST'])
    def getMyAccount(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            Partner = response.get("context").get("partner")
            if Partner:
                result = {
                    'name': {'required': True, 'label': _("Your name"), 'value': Partner.name or ""},
                    'email': {'required': True, 'readonly': True, 'label': _("Email"), 'value': Partner.email or ""},
                    'phone': {'label': _("Phone"), 'value': Partner.phone or ""},
                    'street': {'label': _("Street"), 'value': Partner.street or ""},
                    'street2': {'label': _("Street2"), 'value': Partner.street2 or ""},
                    'city': {'label': _("City"), 'value': str(Partner.city) or ""},
                    'zip': {'label': _("Zip / Postal Code"), 'value': Partner.zip or ""},
                    'country_id': {'label': _("Country"), 'value': str(Partner.country_id and Partner.country_id.id) or ""},
                    'state_id': {'label': _("State"), 'value': str(Partner.state_id and Partner.state_id.id) or ""},
                }
                result['message'] = "My Account Details."
            else:
                result = {'success': False, 'message': 'Account not found !!!'}
            response.update(result)
        return self._response('account', response)

    @route('/mobikul/localizationData', csrf=False, type='http', auth="none", methods=['POST'])
    def getLocalizationData(self, **kwargs):
        if request.httprequest.headers.get("Login"):
            print("ssssssssssssssssssssssssssSSSSSS")
            response = self._authenticate(True, **kwargs)
        else:
            print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            Mobikul = response.get("context").get("mobikul_obj")
            StateObj = request.env['res.country.state'].sudo()
            countries = Mobikul.fetch_countries()
            if countries:
                result = {'countries': []}
                state_ids = []
                for country in countries:
                    states = []
                    if country['state_ids']:
                        states = StateObj.search_read(
                            [('id', 'in', country['state_ids'])], fields=['name'])
                    result['countries'].append({
                        'id': country['id'],
                        'name': country['name'],
                        'states': states,
                    })
                    result['message'] = "Localization Data."
            else:
                result = {'success': False, 'message': 'Account not found !!!'}
            response.update(result)
        return self._response('account', response)

    def _website_Wishlist(self, customer_id, product_id=False):
        result = []
        wishlists = request.env['product.wishlist'].sudo().search(
            [('partner_id', '=', customer_id)])
        for wishlist in wishlists:
            result.append(wishlist.product_id.id)
        return result

    @route(['/mobikul/mycart', '/mobikul/mycart/<int:line_id>'], csrf=False, type='http', auth="none", methods=['POST', 'PUT', 'DELETE'])
    def getMyCart(self, line_id=0, **kwargs):
        response = self._authenticate(True, **kwargs)
        _logger.info("MYCART")
        if response.get('success'):
            result = {"message": "Cart Detils."}
            local = response.get('context', {})

            lang_obj = local.get('lang_obj').iso_code

            Partner = local.get("partner")
            if Partner:
                if request.httprequest.method == "POST":
                    last_order = Partner.last_mobikul_so_id
                    if last_order:
                        result = {
                            "name": last_order.name,
                            "subtotal": {"title": _("Subtotal"),
                                         "value": _displayWithCurrency(local.get('lang_obj'), last_order.amount_untaxed, local.get('currencySymbol'), local.get('currencyPosition')),
                                         },
                            "tax": {"title": _("Taxes"),
                                    "value": _displayWithCurrency(local.get('lang_obj'), last_order.amount_tax, local.get('currencySymbol'), local.get('currencyPosition')),
                                    },
                            "grandtotal": {"title": _("Total"),
                                           "value": _displayWithCurrency(local.get('lang_obj'), last_order.amount_total, local.get('currencySymbol'), local.get('currencyPosition')),
                                           },
                            "amount": {"title": _("Amount"),
                                           "value":  last_order.amount_total or 0.0,

                                           },
                            "items": []
                        }
                        for item in last_order.order_line:
                            if (response.get('addons', {}).get('website_sale_delivery') and item.is_delivery) or (item.product_id.sale_ok != True):
                                shippingMethod = {
                                    "tax": [tax.name for tax in item.tax_id],
                                    "name": item.order_id.carrier_id.name,
                                    "description": item.order_id.carrier_id.website_description or "",
                                    "shippingId": item.order_id.carrier_id.id,
                                    "total": _displayWithCurrency(local.get('lang_obj'), item.price_subtotal,
                                                                  local.get('currencySymbol'), local.get('currencyPosition')),
                                }
                                result.update({"delivery": shippingMethod})
                            else:
                                prof=request.env['product.product'].sudo().search([('id','=',item.product_id.id)])
                                isOffer = False
                                offerPrice = 0.0,
                                msgOffer = ""

                                today = datetime.today()
                                # offer=request.env['discount.offer'].sudo().search([('product_id.id','=',int(product.get('productId'))),('date_start', '>', today), ('date_end', '<=', today)],limit=1)
                                offer = request.env['discount.offer'].sudo().search(
                                    [('product_id.id', '=', item.product_id.id), ('date_start', '<=', today),
                                     ('date_end', '>=', today)], limit=1)
                                if(offer):
                                    isOffer = True
                                    offerPrice = offer.priceAfteroffer
                                    msgOffer = offer.name



                                temp = {
                                    "lineId": item.id,
                                    #"templateId": item.product_id and item.product_id.product_tmpl_id.id or "",
                                    "templateId": item.product_id.id,

                                    #"name": item.product_id and item.product_id.display_name or item.name,
                                    "name":prof.name or  "",

                                    "thumbNail": _get_image_url(self.base_url, 'product.product', item.product_id and item.product_id.id or "", 'image_1920', item.product_id and item.product_id.write_date),
                                    "priceReduce": item.price_reduce < item.price_unit and _displayWithCurrency(local.get('lang_obj'), item.price_reduce, local.get('currencySymbol'), local.get('currencyPosition')) or "",
                                    "priceUnit": _displayWithCurrency(local.get('lang_obj'), item.product_id.list_price, local.get('currencySymbol'), local.get('currencyPosition')),
                                    "uomQty": item.product_id.uom_QTY or '',
                                    'qtyAvailable': item.product_id.qty_available,
                                    "qty": item.product_uom_qty,
                                    "total": _displayWithCurrency(local.get('lang_obj'), item.price_subtotal, local.get('currencySymbol'), local.get('currencyPosition')),
                                    "discount": item.discount and "(%d%% OFF)" % item.discount or "",
                                    'isOffer': isOffer,
                                    'offerPrice': _displayWithCurrency(local.get('lang_obj'), offerPrice,
                                                                       local.get('currencySymbol', ""),
                                                                       local.get('currencyPosition', "")),

                                    'msgOffer': msgOffer,
                                }
                                #print(temp,'temp2')
                               
                                result['items'].append(temp)
                        if not len(result['items']):
                            result['message'] = _('Your Shopping Bag is empty.')
                    else:
                        result = {'message': _('Your Shopping Bag is empty.')}
                else:
                    OrderLineObj = request.env['sale.order.line'].sudo()
                    OrderLine = OrderLineObj.search([('id', '=', line_id)])
                    Order_id = OrderLine.order_id
                    if Order_id:
                        if request.httprequest.method == "PUT":
                            result = {'message': 'Updated successfully.','lineId':OrderLine.id}
                            add_qty = None
                            set_qty = None
                            if self._mData.get('set_qty'):
                                set_qty = self._mData['set_qty']
                            elif self._mData.get('add_qty'):
                                add_qty = int(self._mData['add_qty'])

                            if add_qty or set_qty:
                                print('add_qty2',add_qty)
                                Order_id.with_context(local)._cart_update(
                                    product_id=OrderLine.product_id.id,
                                    line_id=OrderLine.id,
                                    add_qty=add_qty and int(add_qty) or 0,
                                    set_qty=set_qty and int(set_qty) or 0,
                                    product_custom_attribute_values=False,
                                    no_variant_attribute_values=False
                                )
                                isOffer = False
                                offerPrice = 0.0,
                                msgOffer = ""

                                today = datetime.today()
                                # offer=request.env['discount.offer'].sudo().search([('product_id.id','=',int(product.get('productId'))),('date_start', '>', today), ('date_end', '<=', today)],limit=1)

                                # offer = request.env['discount.offer'].sudo().search(
                                #     [('product_id.id', '=', OrderLine.product_id.id), ('date_start', '<=', today),
                                #      ('date_end', '>=', today)], limit=1)
                                # if (offer):
                                #     isOffer = True
                                #     offerPrice = offer.priceAfteroffer
                                #     msgOffer = offer.name
                                # result = {'message': 'Updated successfully.',
                                #
                                #           'lineId': OrderLine.id,
                                #           "templateId": OrderLine.product_id.id,
                                #
                                #           # "name": item.product_id and item.product_id.display_name or item.name,
                                #           "name": OrderLine.product_id.name or "",
                                #
                                #           "thumbNail": _get_image_url(self.base_url, 'product.product',
                                #                                       OrderLine.product_id and OrderLine.product_id.id or "",
                                #                                       'image_1920',
                                #                                       OrderLine.product_id and OrderLine.product_id.write_date),
                                #           "priceReduce": OrderLine.price_reduce < OrderLine.price_unit and _displayWithCurrency(
                                #               local.get('lang_obj'), OrderLine.price_reduce, local.get('currencySymbol'),
                                #               local.get('currencyPosition')) or "",
                                #           "priceUnit": _displayWithCurrency(local.get('lang_obj'),
                                #                                             OrderLine.product_id.list_price,
                                #                                             local.get('currencySymbol'),
                                #                                             local.get('currencyPosition')),
                                #           "uomQty": OrderLine.product_id.uom_QTY or '',
                                #           'qtyAvailable': OrderLine.product_id.qty_available,
                                #           "qty": OrderLine.product_uom_qty,
                                #           "total": _displayWithCurrency(local.get('lang_obj'), OrderLine.price_subtotal,
                                #                                         local.get('currencySymbol'),
                                #                                         local.get('currencyPosition')),
                                #           "discount": OrderLine.discount and "(%d%% OFF)" % OrderLine.discount or "",
                                #           'isOffer': isOffer,
                                #           'offerPrice': _displayWithCurrency(local.get('lang_obj'), offerPrice,
                                #                                              local.get('currencySymbol', ""),
                                #                                              local.get('currencyPosition', "")),
                                #
                                #           'msgOffer': msgOffer,
                                #           }
                            else:
                                result = {'message': 'Wrong request.'}
                        elif request.httprequest.method == "DELETE":
                            try:
                                result = {'message': '%s' % (
                                    OrderLine.product_id and OrderLine.product_id.name or OrderLine.name)+_(' was removed from your Shopping Bag.')}
                                OrderLine.unlink()
                            except:
                                result = {'message': 'Please try again after some time.'}
                        else:
                            result = {'message': 'Wrong request.'}
                    else:
                        result = {'message': 'No matching product found !!!'}
            else:
                result = {'success': False, 'message': 'Account not found !!!'}
            response.update(result)
        return self._response('cart', response)

    @route('/mobikul/mycart/setToEmpty', csrf=False, type='http', auth="none", methods=['DELETE'])
    def setToEmpty(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            result = {}
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            if Partner:
                last_order = Partner.last_mobikul_so_id
                if last_order:
                    try:
                        result = {'message': _('Your Shopping Bag has been set to Empty.')}
                        last_order.order_line.unlink()
                        result['cartCount'] = last_order.cart_count
                    except:
                        result = {'message': 'Please try again after some time.'}
                else:
                    result = {'message': _('Your Shopping Bag is already empty.')}
            else:
                result = {'success': False, 'message': 'Account not found !!!'}
            response.update(result)
        return self._response('setToEmpty', response)

    @route('/mobikul/mycart/addToCart2', csrf=False, type='http', auth="public", methods=['POST'])
    def addToCart2(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            Mobikul = response.get("context").get("mobikul_obj")
            result = Mobikul.add_to_cart2(self._mData.get("productId"), self._mData.get(
                "set_qty"), self._mData.get("add_qty"),self._mData.get("customerId"), response.get("context"))
            response.update(result)
        return self._response('addToCart', response)
    @route('/mobikul/mycart/addToCart', csrf=False, type='http', auth="public", methods=['POST'])
    def addToCart(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            Mobikul = response.get("context").get("mobikul_obj")
            result = Mobikul.add_to_cart(self._mData.get("productId"), self._mData.get(
                "set_qty"), self._mData.get("add_qty"), response.get("context"))
            response.update(result)
        return self._response('addToCart', response)

    @route(['/mobikul/ShippingMethods'], csrf=False, type='http', auth="none", methods=['GET'])
    def getAvailableShippingMethods(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success') and response.get('addons', {}).get('website_sale_delivery'):
            context = response.get("context", {})
            Partner = context.get("partner")
            user =context.get("user")
            SaleOrder = Partner.with_context(**context).last_mobikul_so_id
            saleOrderAmount=SaleOrder.amount_total
            ShippingMethods = SaleOrder.sudo()._get_delivery_methods()
            local = response.get('context', {})
            lang_obj = local.get('lang_obj').iso_code
            tz = pytz.timezone('Asia/Riyadh')
            now = datetime.now(tz=tz)
            current_time = now.strftime("%H:%M")
            today = datetime.now(tz=tz)
            tomorrow =today + timedelta(days = 1)
            am = 'am'
            pm = 'pm'
            daysArbic={'Saturday':'السبت','Sunday':'الأحد','Monday':'الاثنين','Tuesday':'الثلاثاء','Wednesday':'الاربعاء','Thursday':'الخميس','Friday':'الجمعة',}

            today_name = today.strftime("%A")
            today_name2 = today.strftime("%A")

            tomorrow_name2 = tomorrow.strftime("%A")
            tomorrow_name = "Tomorrow"

            if(lang_obj=='ar'):
                am='ص'
                pm='م'
                today_name=daysArbic.get(today_name)
                tomorrow_name = daysArbic.get(tomorrow_name)
                tomorrow_name="غداً"
            d1 = today.strftime("%d/%m/%Y")
            tomorrowd2 = tomorrow.strftime("%d/%m/%Y")

            if ShippingMethods:
                result = []


                for method in ShippingMethods:
                    today_data = {}
                    if (method.delivery_hour):
                        floattime = now.hour + method.delivery_hour + now.minute / 60.
                        delivery_schedule_today = []
                        if (today_name2 == "Friday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_friday', '!=', 1)],order='start_time asc')
                        if (today_name2 == "Saturday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_saturday', '!=', 1)],order='start_time asc')
                        if (today_name2 == "Sunday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_sunday', '!=', 1)],order='start_time asc')
                        if (today_name2 == "Monday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_monday', '!=', 1)],order='start_time asc')
                        if (today_name2 == "Tuesday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_tuesday', '!=', 1)],order='start_time asc')
                        if (today_name2 == "Wednesday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_wednesday', '!=', 1)],order='start_time asc')
                        if (today_name2 == "Thursday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_thursday', '!=', 1)],order='start_time asc')
                        # else:
                        #     delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                        #         [('start_time', '>', floattime)])
                        today_data.update({'name': today_name, 'date': d1})
                        schedule = []
                        for order in delivery_schedule_today:
                            if (order.start_time > 12):
                                if ((order.start_time % 12) > 1.0):
                                    result_start_time = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod((order.start_time - 12.0) * 60, 60)) + pm
                                else:
                                    result_start_time = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod((order.start_time ) * 60, 60)) + pm

                                # result_start_time = '{0:02.0f}:{1:02.0f}'.format(
                                #     *divmod((order.start_time - 12.0) * 60, 60)) + pm
                            else:
                                result_start_time = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(order.start_time * 60, 60)) + am
                            if (order.end_time > 12):
                                result_end_time = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod((order.end_time - 12.0) * 60, 60)) + pm
                            else:
                                result_end_time = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(order.end_time * 60, 60)) + am

                            # result_start_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(order.start_time * 60, 60))
                            # result_end_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(order.end_time * 60, 60))
                            schedule.append(
                                {'startTime': result_start_time, 'endTime': result_end_time,
                                 'scheduleId': order.id})
                            # schedule.append(
                            #     {'startTime': str(result_start_time) + 'w', 'endTime': result_end_time,
                            #      'scheduleId': order.id})
                            # if (user.id == 105):
                            #     schedule = []
                        today_data.update({'schedule': schedule})

                    else:

                        floattime = now.hour + 1.0 + now.minute / 60.0
                        delivery_schedule_today = []
                        if (today_name2 == "Friday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_friday', '!=', 1)],order='start_time asc')
                        if (today_name2 == "Saturday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_saturday', '!=', 1)],order='start_time asc')
                        if (today_name2 == "Sunday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_sunday', '!=', 1)],order='start_time asc')
                        if (today_name2 == "Monday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_monday', '!=', 1)],order='start_time asc')
                        if (today_name2 == "Tuesday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_tuesday', '!=', 1)],order='start_time asc')
                        if (today_name2 == "Wednesday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_wednesday', '!=', 1)],order='start_time asc')
                        if (today_name2 == "Thursday"):
                            delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                                [('start_time', '>', floattime), ('hide_on_thursday', '!=', 1)],order='start_time asc')

                        # else:
                        #     delivery_schedule_today = request.env['delivery.schedule'].sudo().search(
                        #     [('start_time', '>', floattime)])
                        today_data.update({'name': today_name, 'date': d1})
                        schedule = []
                        for order in delivery_schedule_today:
                            if (order.start_time > 12):
                                if ((order.start_time % 12) > 1.0):
                                    result_start_time = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod((order.start_time - 12.0) * 60, 60)) + pm
                                else:
                                    result_start_time = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod((order.start_time ) * 60, 60)) + pm

                                # result_start_time = '{0:02.0f}:{1:02.0f}'.format(
                                #     *divmod((order.start_time - 12.0) * 60, 60)) + pm
                            else:
                                result_start_time = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(order.start_time * 60, 60)) + am
                            if (order.end_time > 12):
                                result_end_time = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod((order.end_time - 12.0) * 60, 60)) + pm
                            else:
                                result_end_time = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(order.end_time * 60, 60)) + am

                            schedule.append(
                                {'startTime': result_start_time, 'endTime': result_end_time,
                                 'scheduleId': order.id})
                            # if (user.id == 105):
                            #     schedule = []
                        today_data.update({'schedule': schedule})
                    delivery_schedule_tomorrow = []
                    if (tomorrow_name2 == "Friday"):
                        delivery_schedule_tomorrow = request.env['delivery.schedule'].sudo().search(
                            [('hide_on_friday', '!=', 1)],order='start_time asc')
                    if (tomorrow_name2 == "Saturday"):
                        delivery_schedule_tomorrow = request.env['delivery.schedule'].sudo().search(
                            [('hide_on_saturday', '!=', 1)],order='start_time asc')
                    if (tomorrow_name2 == "Sunday"):
                        delivery_schedule_tomorrow = request.env['delivery.schedule'].sudo().search(
                            [('hide_on_sunday', '!=', 1)],order='start_time asc')
                    if (tomorrow_name2 == "Monday"):
                        delivery_schedule_tomorrow = request.env['delivery.schedule'].sudo().search(
                            [('hide_on_monday', '!=', 1)],order='start_time asc')
                    if (tomorrow_name2 == "Tuesday"):
                        delivery_schedule_tomorrow = request.env['delivery.schedule'].sudo().search(
                            [('hide_on_tuesday', '!=', 1)],order='start_time asc')
                    if (tomorrow_name2 == "Wednesday"):
                        delivery_schedule_tomorrow = request.env['delivery.schedule'].sudo().search(
                            [('hide_on_wednesday', '!=', 1)],order='start_time asc')
                    if (tomorrow_name2 == "Thursday"):
                        delivery_schedule_tomorrow = request.env['delivery.schedule'].sudo().search(
                            [('hide_on_thursday', '!=', 1)],order='start_time asc')

                    # else:
                    #     delivery_schedule_tomorrow = request.env['delivery.schedule'].sudo().search([])
                    tomorrow_data = {}
                    tomorrow_data.update({'name': tomorrow_name, 'date': tomorrowd2})
                    schedule2 = []
                    for order2 in delivery_schedule_tomorrow:
                        if (order2.start_time >= 12):
                            if((order2.start_time % 12)>1.0):
                                result_start_time2 = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod((order2.start_time - 12.0) * 60, 60)) + pm
                            else:
                                result_start_time2 = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod((order2.start_time) * 60, 60)) + pm



                        else:
                            result_start_time2 = '{0:02.0f}:{1:02.0f}'.format(
                                *divmod((order2.start_time) * 60, 60)) + am
                        if (order2.end_time >= 12):
                            result_end_time2 = '{0:02.0f}:{1:02.0f}'.format(
                                *divmod((order2.end_time - 12.0) * 60, 60)) + pm
                        else:
                            result_end_time2 = '{0:02.0f}:{1:02.0f}'.format(*divmod(order2.end_time * 60, 60)) + am
                        schedule2.append(
                            {'startTime': result_start_time2, 'endTime': result_end_time2, 'scheduleId': order2.id})
                    tomorrow_data.update({'schedule': schedule2})
                    pickup_location = []
                    if (method.pickup == True):
                        warehouse = request.env['stock.warehouse'].sudo().search(
                            [('is_pickup_available', '=', True)])
                        for warehouseid in warehouse:
                            pickup_location.append({'id': warehouseid.id, 'name': warehouseid.name,
                                                    'pickupLatitude': warehouseid.partner_id.partner_latitude,
                                                    'pickupLongitude': warehouseid.partner_id.partner_longitude,
                                                    'pickupPhone': warehouseid.partner_id.phone})



                    result.append({
                        "name": method.name,
                        "id": method.id,
                        'pickup': method.pickup,
                        'minimumOrderAmout':method.minimum_order_amout or 0.0,
                        'shiftEmpty':method.shift_empty or "",
                        'deliveryHour': int(method.delivery_hour) or 1,
                        "description": method.website_description or "",
                        "price": _displayWithCurrency(context.get('lang_obj'),
                                                      method.rate_shipment(SaleOrder).get('price'),
                                                      context.get('currencySymbol', ""),
                                                      context.get('currencyPosition', "")),
                        'saleOrderAmount':saleOrderAmount or 0.0,
                        'today': today_data,
                        # 'today': tomorrow_data,
                        'tomorrow': tomorrow_data,
                        'pickupLocation': pickup_location,
                    })

                    #if(method.minimum_order_amout):




                result = {'ShippingMethods': result, "message": "Shipping methods list"}
            else:
                result = {'success': False, 'message': 'No Active Shipping methods found.'}
        else:
            result = {'success': False, 'message': 'Website Sale Delivery is not install.'}
        response.update(result)
        return self._response('getAvailableShippingMethods', response)
    #
    # @route(['/mobikul/ShippingMethods'], csrf=False, type='http', auth="none", methods=['GET'])
    # def getAvailableShippingMethods(self, **kwargs):
    #     response = self._authenticate(True, **kwargs)
    #     if response.get('success') and response.get('addons', {}).get('website_sale_delivery'):
    #         context =  response.get("context",{})
    #         Partner = context.get("partner")
    #         SaleOrder = Partner.with_context(**context).last_mobikul_so_id
    #         ShippingMethods = SaleOrder.sudo()._get_delivery_methods()
    #         if ShippingMethods:
    #             result = []
    #             for method in ShippingMethods:
    #
    #                 result.append({
    #                     "name": method.name,
    #                     "id": method.id,
    #                     'pickup': method.pickup,
    #                     'deliveryHour':method.delivery_hour or 1,
    #                     "description": method.website_description or "",
    #                     "price": _displayWithCurrency(context.get('lang_obj'), method.rate_shipment(SaleOrder).get('price'),
    #                                                   context.get('currencySymbol', ""), context.get('currencyPosition', "")),
    #                 })
    #             result = {'ShippingMethods': result, "message": "Shipping methods list"}
    #         else:
    #             result = {'success': False, 'message': 'No Active Shipping methods found.'}
    #     else:
    #         result = {'success': False, 'message': 'Website Sale Delivery is not install.'}
    #     response.update(result)
    #     return self._response('getAvailableShippingMethods', response)


    @route('/mobikul/paymentAcquirers', csrf=False, type='http', auth="none", methods=['POST'])
    def getPaymentAcquirer(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            result = {}
            AcquirerObj = request.env['payment.acquirer'].sudo()
            Acquirers = AcquirerObj.search_read([('is_mobikul_available', '=', 1), ('mobikul_reference_code', 'in', AQUIRER_REF_CODES)], fields=[
                'name', 'pre_msg', 'mobikul_reference_code', 'mobikul_extra_key', 'write_date'])
            context = response.get("context")
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            addapplePay=request.env['fcm.registered.devices'].sudo().search([('customer_id.id','=',Partner.id),('platformType','=','ios')],limit=1)
            if(Partner.platformType=='ios'):
                Acquirers = AcquirerObj.search_read(
                    [('is_mobikul_available', '=', 1), ], fields=[
                        'name', 'pre_msg', 'mobikul_reference_code', 'mobikul_extra_key', 'write_date'])

            # if(int(context.get("user")[0])==105):
            #     Acquirers = AcquirerObj.search_read(
            #         [('is_mobikul_available', '=', 1), ], fields=[
            #             'name', 'pre_msg', 'mobikul_reference_code', 'mobikul_extra_key', 'write_date'])


            if Acquirers:
                result = {'acquirers': Acquirers}
                for index, value in enumerate(result['acquirers']):
                    result['acquirers'][index]['thumbNail'] = _get_image_url(
                        self.base_url, 'payment.acquirer', result['acquirers'][index]['id'], 'image_128', result['acquirers'][index]['write_date'])
                    result['acquirers'][index]['description'] = remove_htmltags(
                        result['acquirers'][index].pop('pre_msg')) or ""
                    result['acquirers'][index]['code'] = result['acquirers'][index].pop(
                        'mobikul_reference_code') or ""
                    result['acquirers'][index]['extraKey'] = result['acquirers'][index].pop(
                        'mobikul_extra_key') or ""
                    result['acquirers'][index].pop('write_date', None)
                result['message'] = "Payment Acquirer list."
            else:
                result = {'success': False, 'message': _('No Active Payment methods found.')}
            response.update(result)
        return self._response('paymentAcquirer', response)

    @route('/mobikul/orderReviewData', csrf=False, type='http', auth="none", methods=['POST'])
    def getOrderReviewData(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            context = response.get("context",{})
            Mobikul = context.get("mobikul_obj")
            paymentTerms = Mobikul._getPaymentTerms()
            response.update(paymentTerms)
            Acquirer = request.env['payment.acquirer'].sudo().browse(
                int(self._mData.get('acquirerId')))
            if Acquirer:
                user = context.get("user")
                if user:
                    if response.get('addons', {}).get('email_verification') and context.get("websiteObj").restrict_unverified_users:
                        if user.wk_token_verified:
                            result = self._orderReview(user, response, Acquirer)
                        else:
                            response.update({'success': False, 'message': _(
                                "You can't place your order, please verify your account")})
                    else:
                        response.update(self._orderReview(user, response, Acquirer))
                else:
                    response.update({'success': False, 'message': _('Account not found !!!')})
            else:
                response.update({'success': False, 'message': _(
                    'No Payment methods found with given id.')})
        return self._response('orderReviewData', response)

    @route('/mobikul/placeMyOrder', csrf=False, type='http', auth="public", methods=['POST'])
    def placeMyOrder(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            if self._mData.get('transaction_id'):
                response.update(self.placeOrder(response.get('context')))
            else:
                response.update({'success': False, 'message': _('Transaction Id not found !!!')})
        return self._response('placeMyOrder', response)

    @route('/mobikul/deleteProfileImage', csrf=False, type='http', auth="none", methods=['DELETE'])
    def deleteProfileImage(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            result = {}
            User = response.get("context").get("user")
            if User:
                User.write({'image_1920': False})
                response.update({"message": _("Profile Image Deleted Successfully.")})
            else:
                response.update({'success': False, 'message': _('Account not found !!!')})
        return self._response('deleteProfileImage', response)

    @route('/mobikul/saveMyDetails', csrf=False, type='http', auth="none", methods=['POST'])
    def saveMyDetails(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            result = {}
            Userobj = request.env['res.users'].sudo()
            User = Userobj.browse(response.get('userId'))
            if User:
                result['message'] = _("Updated Successfully.")
                if self._mData.get('image'):
                    try:
                        User.write({'image_1920': self._mData['image']})
                        result['customerProfileImage'] = _get_image_url(
                            self.base_url, 'res.partner', User.partner_id.id, 'image_1920', User.partner_id.write_date)
                    except Exception as e:
                        result['message'] = _("Please try again later")+" %r" % e
                if self._mData.get('name'):
                    User.write({'name': self._mData['name']})
                if self._mData.get('password'):
                    User.write({'password': self._mData['password']})
            else:
                result = {'success': False, 'message': _('Account not found !!!')}
            response.update(result)
        return self._response('saveMyDetails', response)

    @route('/mobikul/registerFcmToken', csrf=False, type='http', auth="none", methods=['POST'])
    def registerFcmToken(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        if response.get('success'):
            customer_id = False
            if self._mData.get("customerId"):
                customer_id = int(self._mData["customerId"])
            self._tokenUpdate(customer_id=customer_id)
            response.update({'message': _('Request completed !')})
        return self._response('registerFcmToken', response)

    @route('/mobikul/notificationMessages', csrf=False, type='http', auth="none", methods=['POST'])
    def getNotificationMessages(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            fields = ['id', 'name', 'title', 'subtitle', 'body', 'banner',
                      'icon', 'period', 'datatype', 'is_read', 'write_date']
            domain = [('customer_id', '=', Partner.id)]
            Message = request.env['mobikul.notification.messages'].sudo()
            notification_message = Message.search_read(domain, limit=self._mData.get('limit', response.get(
                'itemsPerPage', 5)), offset=self._mData.get('offset', 0),  order="id desc", fields=fields)
            for msg in notification_message:
                msg['name'] = msg['name'] or ""
                msg['title'] = msg['title'] or ""
                msg['subtitle'] = msg['subtitle'] or ""
                msg['body'] = msg['body'] or ""
                msg['icon'] = _get_image_url(
                    self.base_url, 'mobikul.notification.messages', msg['id'], 'icon', msg['write_date'])
                msg['banner'] = _get_image_url(
                    self.base_url, 'mobikul.notification.messages', msg['id'], 'banner', msg['write_date'])
                msg.pop('write_date')
            result = {'all_notification_messages': notification_message}
            response.update(result)

        return self._response('notificationMessages', response)

    @route('/mobikul/notificationMessage/<int:message_id>', csrf=False, type='http', auth="none",  methods=['POST', 'PUT', 'DELETE'])
    def getNotificationMessageDetails(self, message_id, **kwargs):
        global result
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            MessageObj = request.env['mobikul.notification.messages'].sudo()
            message = MessageObj.search(
                [('id', '=', message_id), ('customer_id', '=', response.get('customerId'))])
            if message:
                if request.httprequest.method == "POST":
                    message.is_read = True
                    result = {
                        'id': message.id,
                        'name': message.name or "",
                        'create_date': Datetime.to_string(message.create_date),
                        'title': message.title or "",
                        'subtitle': message.subtitle or "",
                        'body': message.body or "",
                        'icon': _get_image_url(self.base_url, 'mobikul.notification.messages', message.id, 'icon', message.write_date),
                        'banner': _get_image_url(self.base_url, 'mobikul.notification.messages', message.id, 'banner', message.write_date),
                        'period': message.period,
                        'is_read': message.is_read,
                        'datatype': message.datatype,
                        'success': True,
                        'message': 'Successfull'
                    }
                elif request.httprequest.method == "DELETE":
                    message.active = False
                    result = {'success': True, 'message': _('Deleted Successfully')}
                elif request.httprequest.method == "PUT":
                    message.is_read = self._mData.get('is_read', message.is_read)
                    result = {'success': True, 'message': _('Updated Successfully')}
            else:
                result = {'success': False, 'message': _('Message not Found')}
            response.update(result)
        return self._response('notificationMessageDetails', response)

    @route('/mobikul/my/wishlists', csrf=False, type='http', auth="none", methods=['POST'])
    def getMyWishlists(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):

            TemplateObj = request.env['product.template'].sudo()
            if response.get('addons', {}).get('wishlist') and response.get('customerId'):
                wishlists = []
                Partner = response.get("context").get("partner")
                last_order = Partner.last_mobikul_so_id
                local = response.get('context', {})
                for wishlist in Partner.wishlist_ids:
                    Template = TemplateObj.search([('id', '=', wishlist.product_id.product_tmpl_id.id)])
                    comb_info = Template._get_combination_info(combination=False, product_id=False,add_qty=1, pricelist=local.get("pricelist"), parent_combination=False, only_template=False)
                    if wishlist.product_id:
                        cart_qty = 0.0
                        lineId = 0
                        product_id = []
                        if (last_order):
                            product_id = last_order.order_line.sudo().search(
                                [('product_id', '=', wishlist.product_id.id), ('order_id', '=', last_order.id)], limit=1)
                            if (len(product_id) > 0):
                                cart_qty = product_id.product_uom_qty
                                lineId = product_id.id
                        prof = request.env['product.product'].sudo().search([('id', '=', wishlist.product_id.id)])
                        isOffer = False
                        offerPrice = 0.0,
                        msgOffer = ""

                        today = datetime.today()
                        offer = request.env['discount.offer'].sudo().search(
                            [('product_id.id', '=', prof.id), ('date_start', '<=', today),
                             ('date_end', '>=', today)], limit=1)

                        if (offer):
                            isOffer = True
                            offerPrice = offer.priceAfteroffer
                            msgOffer = offer.name

                        _logger.info("++++++++++++++++++++++ %r",local.get("pricelist").discount_policy == 'with_discount')
                        _logger.info("+++++++ %r",comb_info['has_discounted_price'])
                        _logger.info(request.env.user)
                        product_detail = {
                            'id': wishlist.id,
                            #'id': wishlist.product_id.id,
                            "name": prof.name,
                            "thumbNail": _get_image_url(self.base_url, 'product.product', wishlist.product_id.id, 'image_1920', wishlist.product_id.write_date),

                            "priceReduce": comb_info['has_discounted_price']  and _displayWithCurrency(local.get('lang_obj'), comb_info['price'], local.get('currencySymbol'), local.get('currencyPosition')) or "",
                            'priceUnit'		: _displayWithCurrency(local.get('lang_obj'), comb_info['has_discounted_price']  and comb_info['list_price'] or comb_info['price'], local.get('currencySymbol'), local.get('currencyPosition')),
                            #'priceReduce'	: comb_info['has_discounted_price'] and _displayWithCurrency(local.get('lang_obj'), comb_info['price'], local.get('currencySymbol'), local.get('currencyPosition')) or "",

                            #"priceUnit": _displayWithCurrency(local.get('lang_obj'), wishlist.product_id.lst_price, local.get('currencySymbol'), local.get('currencyPosition')),
                            #"productId": wishlist.product_id.id,
                            "productId": wishlist.product_id.id,
                            #"productId": wishlist.product_id.product_tmpl_id.id,
                            "templateId": wishlist.product_id.product_tmpl_id.id,
                            'qtyAvailable': wishlist.product_id.qty_available,

                            "cartQty":cart_qty,
                            "lineId":lineId,
                            'isOffer': isOffer,
                            'offerPrice': _displayWithCurrency(local.get('lang_obj'), offerPrice,
                                                               local.get('currencySymbol', ""),
                                                               local.get('currencyPosition', "")),

                            'msgOffer': msgOffer,


                        }
                        #print('product_detail',product_detail)
                        wishlists.append(product_detail)
                #print(wishlists)
                result = {
                    'success': True,
                    "wishLists": wishlists,
                    'message': 'success'
                }
            else:
                result = {'success': False, 'message': 'Wishlist is not Active !!!'}
            response.update(result)
        return self._response('myWishlists', response)

    @route('/my/removeWishlist/<int:wishlist_id>', csrf=False, type='http', auth="none",  methods=['DELETE'])
    def removeWishlist(self, wishlist_id, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            if response.get('addons', {}).get('wishlist'):
                result = {'success': False, 'message': 'Wishlist Id Not Found'}
                try:
                    wishlist = request.env['product.wishlist'].sudo().search(
                        [('id', '=', wishlist_id), ('partner_id', '=', response.get('customerId'))])
                    if wishlist:
                        wishlist.unlink()
                        result.update({'success': True,
                                       'message': 'Item removed'
                                       })
                except Exception as e:
                    result.update({
                        'success': False,
                        'message': 'Please try again later %r' % e,
                    })
            else:
                result = {'success': False, 'message': 'Wishlist is not Active !!!'}
            response.update(result)
        return self._response('removeWishlist', response)

    @route('/my/removeFromWishlist/<int:product_id>', csrf=False, type='http', auth="none",  methods=['DELETE'])
    def removeFromWishlist(self, product_id, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            if response.get('addons', {}).get('wishlist'):
                result = {
                    'success': False,
                    'message': 'ProductId Not Found in wishlist',
                }
                try:
                    wishlist = request.env['product.wishlist'].sudo().search(
                        [('product_id', '=', product_id), ('partner_id', '=', response.get('customerId'))])
                    if wishlist:
                        wishlist.unlink()
                        result.update({'success': True, 'message': 'Item removed'})
                except Exception as e:
                    result.update({'success': False, 'message': 'Please try again later %r' % e})
            else:
                result = {'success': False, 'message': 'Wishlist is not Active !!!'}
            response.update(result)
        return self._response('removeFromWishlist', response)

    @route('/my/addToWishlist', csrf=False, type='http', auth="public", methods=['POST'])
    def addToWishlist(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            if response.get('addons', {}).get('wishlist') and response.get('customerId'):
                result = self.add2Ws(response.get("context"), self._mData.get("productId"))
            else:
                result = {'success': False, 'message': 'Wishlist is not Active !!!'}
            response.update(result)
        return self._response('addToWishlist', response)

    @route('/my/wishlistToCart', csrf=False, type='http', auth="public", methods=['POST'])
    def moveWishlistToCart(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            if response.get('addons', {}).get('wishlist') and response.get('customerId'):
                wishlistObj = request.env['product.wishlist'].sudo()
                wishlist = wishlistObj.search(
                    [('id', '=', self._mData.get("wishlistId")), ('partner_id', '=', response.get('customerId'))])
                result = request.env['mobikul'].sudo().add_to_cart(
                    wishlist.product_id.id, 0, self._mData.get("add_qty", 1), response.get("context"))
                if result.get("success"):
                    wishlist.unlink()
                    result = {'success': True, 'message': _('Item moved to Bag')}
                else:
                    result = {'success': False, 'message': _('Please try again later')}
            else:
                result = {'success': False, 'message': 'Wishlist is not Active !!!'}
            response.update(result)
        return self._response('moveWishlistToCart', response)

    @route('/my/cartToWishlist', csrf=False, type='http', auth="public", methods=['POST'])
    def moveCartToWishlist(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            if response.get('addons', {}).get('wishlist'):
                OrderLine = request.env['sale.order.line'].sudo().search(
                    [('id', '=', self._mData.get('line_id'))])
                if OrderLine:
                    result = self.add2Ws(response.get('context'), OrderLine.product_id.id)
                    if result.get("success"):
                        OrderLine.unlink()
                else:
                    result = {'success': False, 'message': _('Order not found')}
            else:
                result = {'success': False, 'message': 'Wishlist is not Active !!!'}
            response.update(result)
        return self._response('moveCartToWishlist', response)

    # @route('/mobikul/signup/terms', csrf=False, type='http', auth="none", methods=['GET'])
    # def signupTermsCondition(self, **kwargs):
    #     response = self._authenticate(False, **kwargs)
    #     Mobikul = response.get("context").get("mobikul_obj")
    #     if response.get('success'):
    #         response.update(
    #             {'success': True, 'termsAndConditions': Mobikul.signup_terms_and_condition})
    #     else:
    #         response.update(
    #             {'success': False, 'message': "signup Terms and conditions is disable."})
    #     return self._response('termsAndConditions', response)
    #
    # @route('/mobikul/aboutus', csrf=False, type='http', auth="none", methods=['GET'])
    # def about_us(self, **kwargs):
    #     response = self._authenticate(False, **kwargs)
    #     Mobikul = response.get("context").get("mobikul_obj")
    #     if response.get('success'):
    #         response.update(
    #             {'success': True, 'aboutus': Mobikul.about_us})
    #     else:
    #         response.update(
    #             {'success': False, 'message': "signup Terms and conditions is disable."})
    #     return self._response('aboutus', response)

    # @route('/mobikul/privacypolicy', csrf=False, type='http', auth="none", methods=['GET'])
    # def privacypolicy(self, **kwargs):
    #     response = self._authenticate(False, **kwargs)
    #     Mobikul = response.get("context").get("mobikul_obj")
    #     if response.get('success'):
    #         response.update(
    #             {'success': True, 'privacypolicy': Mobikul.privacy_policy})
    #     else:
    #         response.update(
    #             {'success': False, 'message': "signup Terms and conditions is disable."})
    #     return self._response('privacypolicy', response)

    @route('/mobikul/signup/terms', csrf=False, type='http', auth="none", methods=['GET'])
    def signupTermsCondition(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        Mobikul = request.env['mobikul.terms'].sudo().search([],limit=1)
        if response.get('success'):
            response.update(
                {'success': True, 'termsAndConditions': Mobikul.signup_terms_and_condition})
        else:
            response.update(
                {'success': False, 'message': "signup Terms and conditions is disable."})
        return self._response('termsAndConditions', response)

    @route('/mobikul/aboutus', csrf=False, type='http', auth="none", methods=['GET'])
    def about_us(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        Mobikul = request.env['mobikul.terms'].sudo().search([],limit=1)
        if response.get('success'):
            response.update(
                {'success': True, 'aboutus': Mobikul.about_us})
        else:
            response.update(
                {'success': False, 'message': "signup Terms and conditions is disable."})
        return self._response('aboutus', response)

    @route('/mobikul/version', csrf=False, type='http', auth="none", methods=['GET'])
    def mobikulVersion(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        Mobikul = request.env['mobikul'].sudo().search([], limit=1)
        if response.get('success'):
            response.update(
                {'success': True, 'iosVersion': Mobikul.ios_version,'androidVersion': Mobikul.android_version,'msgVersion':Mobikul.msg_version})
        else:
            response.update(
                {'success': False, 'message': "version is disable."})
        return self._response('version', response)

    @route('/mobikul/privacypolicy', csrf=False, type='http', auth="none", methods=['GET'])
    def privacypolicy(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        Mobikul = request.env['mobikul.terms'].sudo().search([],limit=1)
        if response.get('success'):
            response.update(
                {'success': True, 'privacypolicy': Mobikul.privacy_policy})
        else:
            response.update(
                {'success': False, 'message': "signup Terms and conditions is disable."})
        return self._response('privacypolicy', response)





    @route('/product/reviews', csrf=False, type='http', auth="none", methods=['POST'])
    def getProductReview(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        if response.get('success'):
            if response.get('addons', {}).get('review'):
                product_reviews = []
                reviewObj = request.env['user.review'].sudo()
                domain = [('template_id', '=', self._mData.get(
                    'template_id')), ('state', '=', 'pub')]
                fields = ['customer', 'customer_image', 'email', 'likes', 'dislikes',
                          'rating', 'title', 'msg', 'create_date', 'partner_id', 'write_date']
                product_reviews = reviewObj.search_read(domain, limit=self._mData.get('limit', response.get(
                    'itemsPerPage', 5)), offset=self._mData.get('offset', 0),  order="id desc", fields=fields)
                for review in product_reviews:
                    review['customer_image'] = _get_image_url(
                        self.base_url, 'user.review', review['id'], 'customer_image', review['write_date'])
                    review['create_date'] = request.env['mobikul'].sudo(
                    ).easy_date(review['create_date'])
                    if response.get('addons', {}).get('email_verification'):
                        res_partner = request.env['res.partner'].sudo().browse(
                            review.get('partner_id') and review.get('partner_id')[0])
                        del review['partner_id']
                        review['is_email_verified'] = res_partner and res_partner.user_ids and res_partner.user_ids.wk_token_verified or False
                result = {'product_reviews': product_reviews, "reviewCount": len(product_reviews)}

            else:
                result = {'success': False, 'message': _('Review Module not install !!!')}
            response.update(result)
        return self._response('ProductReview', response)

    @route('/my/saveReview', csrf=False, type='http', auth="none", methods=['POST'])
    def addReview(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            Mobikul = response.get("context").get("mobikul_obj")
            result = {}
            if response.get('addons', {}).get('review'):
                Partner = response.get("context").get("partner")
                if Partner:
                    vals = {
                        "title": self._mData.get("title"),
                        'msg': self._mData.get("detail"),
                        "rating": self._mData.get("rate"),
                        'partner_id': Partner.id,
                        "template_id": self._mData.get("template_id"),
                        "customer": Partner.name,
                        "email": Partner.email,
                        "customer_image": Partner.image
                    }
                    try:
                        request.env['user.review'].sudo().create(vals)
                        if Mobikul.review_defaults().get('auto_publish'):
                            result = {'success': True, 'message': _('Thanks for your review.')}
                        else:
                            result = {'success': True, 'message': Mobikul.review_defaults().get(
                                'message_when_unpublish')}
                    except Exception as e:
                        result = {'success': False, 'message': _('Please try again later')}
                else:
                    result = {'success': False, 'message': _('Account not found !!!')}
            else:
                response.update({'success': False, 'message': _('Review Module not install !!!')})
            response.update(result)
        return self._response('addReview', response)

    @route('/review/likeDislike', csrf=False, type='http', auth="none", methods=['POST'])
    def addLikeDislike(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        likeDislikeObj = request.env['review.like.dislike'].sudo()
        # it assume that review module is installed
        if response.get('success') and self._mData.get("review_id"):
            review = request.env['user.review'].sudo().browse(int(self._mData.get("review_id")))
            if review:
                ld_exist = likeDislikeObj.search(
                    [("customer_id", "=", response.get('userId')), ("review_id", "=", review.id)])
                vals = {
                    "customer_id": response.get('userId'),
                    'like': self._mData.get("ishelpful"),
                    "dislike": not self._mData.get("ishelpful"),
                    'review_id': review.id,
                }
                if ld_exist:
                    try:
                        ld_exist.write(vals)
                        result = {'success': True, 'message': _('Thank you for your feedback.')}
                    except Exception as e:
                        result = {'success': False, 'message': _('Please try again later')}
                else:
                    try:
                        likeDislikeObj.sudo().create(vals)
                        result = {'success': True, 'message': _('Thank you for your feedback.')}
                    except Exception as e:
                        result = {'success': False, 'message': _('Please try again later')}
            else:
                result = {'success': False, 'message': _('Review not found !!!')}
            response.update(result)
        else:
            response["message"] = _("You need to login first !")
        return self._response('addLikeDislike', response)

    @route('/send/verifyEmail', csrf=False, type='http', auth="none", methods=['POST'])
    def verifyEmail(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        Mobikul = response.get("context").get("mobikul_obj")
        context = response.get("context",{})
        if response.get('success'):
            if response.get('addons', {}).get('email_verification') :
                user = response.get("context").get("user")
                if not user.wk_token_verified:
                    user.send_verification_email(user.id)
                    response['message'] = _("Verification email sent successfully.")
                    response['success'] = True
                else:
                    response['message'] = _("Email already verified.")
                    response['success'] = False
            else:
                response.update({'success': False, 'message': _(
                    'Email Verification Module not install !!!')})
        return self._response('verifyEmail', response)

    @route('/my/Template/seller/<int:seller_id>', csrf=False, type='http', auth="public",  methods=['GET'])
    def productSellerInfo(self, seller_id, **kwargs):
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            if response.get('addons', {}).get('odoo_marketplace'):
                # context = response.get('context', {})
                sellerDetail = self.seller_profile_info(seller_id, response)

                if sellerDetail:
                    result = {'SellerInfo': sellerDetail,
                              'success': True, 'message': _('Seller Found !!!')}
                else:
                    result = {'success': False, 'message': _('Seller Not Found !!!')}
            else:
                result = {'success': False, 'message': _('Marketplace is not Active !!!')}

            if response.get('addons', {}).get('wishlist') and response.get('customerId'):
                wishlists = self._website_Wishlist(response.get('customerId', 0))
                result.update({'wishlists': wishlists})
            response.update(result)
        return self._response('productSellerInfo', response)

    def seller_profile_info(self, seller_id, response):

        MobikulObj = response.get("context").get('mobikul_obj')
        detail = {}
        sellerDetail = request.env['res.partner'].sudo().search(
            [('id', '=', seller_id), ('seller', '=', True)])
        if sellerDetail:
            detail = {
                "seller_id"				: sellerDetail.id,
                'name'					: sellerDetail.name,
                'email'					: sellerDetail.email,
                'average_rating'		: sellerDetail.avg_review(),
                'total_reviews'			: len(sellerDetail.seller_review_ids.filtered(lambda r: (r.active == True and r.state == "pub"))),
                'sales_count'			: sellerDetail.seller_sales_count(),
                'product_count'			: sellerDetail.seller_products_count(),
                'seller_profile_image'	: self.get_marketplace_image_url(self.base_url, 'res.partner', sellerDetail.id, 'profile_image', sellerDetail.write_date),
                'seller_profile_banner'	: self.get_marketplace_image_url(self.base_url, 'res.partner', sellerDetail.id, 'profile_banner', sellerDetail.write_date),
                'create_date'			: Datetime.to_string(sellerDetail.create_date),
                'state'					: sellerDetail.state_id.name or "",
                'country'				: sellerDetail.country_id.name or "",
                'phone'					: sellerDetail.phone or "",
                'mobile'				: sellerDetail.mobile or "",
                'profile_msg'			: remove_htmltags(sellerDetail.profile_msg or ""),
                'return_policy'			: remove_htmltags(sellerDetail.return_policy or ""),
                'shipping_policy'		: remove_htmltags(sellerDetail.shipping_policy or ""),

            }
            seller_review = []
            reviews = sellerDetail.fetch_active_review2(sellerDetail.id, 0, 2)
            seller_review = self.getSellerReviewsDetail(reviews)
            detail.update({'seller_reviews': seller_review})
            self._mData = {"domain": "[('marketplace_seller_id','=',%d)]" % sellerDetail.id,
                            "order": "create_date desc, id desc",
                            "limit": 5}
            cont = response.get("context")
            # if 'pricelist' in cont:
            #     cont.pop("pricelist")
            sellerProducts = MobikulObj.fetch_products(context=cont,**self._mData)

            detail.update({'sellerProducts': sellerProducts})
        return detail

    def getSellerReviewsDetail(self, reviewsObj):
        reviewsDetail = []
        for review in reviewsObj:
            reviewsDetail.append({
                "create_date": Datetime.to_string(review.create_date),
                "rating": review.rating,
                "not_helpful": review.not_helpful,
                "total_votes": review.total_votes,
                "display_name": review.display_name,
                "message_is_follower": review.message_is_follower,
                "title": review.title,
                "id": review.id,
                "msg": review.msg,
                "helpful": review.helpful,
                "email": review.email,
                "name": review.partner_id.name,
                "image": _get_image_url(self.base_url, 'res.partner', review.partner_id.id, 'profile_image', review.partner_id.write_date),
            })
        return reviewsDetail
#
#     # view all the product of sellers api "http://192.168.1.86:8010/mobikul/search"
#     # {"domain": "[('marketplace_seller_id','=',117)]", "offset": 0, "limit":100}
#
    @route('/mobikul/marketplace', csrf=False, type='http', auth="public",  methods=['GET'])
    def marketplace(self, **kwargs):
        PartnerObj = request.env['res.partner'].sudo()
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            if response.get('addons', {}).get('odoo_marketplace'):
                lst = []
                context = response.get('context', {})
                mobikul = context.get('mobikul_obj')
                website_id = mobikul and mobikul.website_id
                result = {
                    "banner": website_id and website_id.mp_landing_page_banner and _get_image_url(self.base_url, 'website', website_id.id, 'mp_landing_page_banner', website_id.write_date) or self.base_url+"odoo_marketplace/static/src/img/Hero-Banner.png",
                    "heading": _("Still Selling Offline? Start Selling Online."),
                    }
                sellersObj = PartnerObj.search(
                    [('seller', '=', True), ('state', '=', 'approved'), ('website_published', '=', True)], limit=5)
                for seller in sellersObj:
                    sellerDetail = self.seller_profile_info(seller.id, response)
                    lst.append(sellerDetail)
                result.update({'SellersDetail': lst, 'success': True,
                               'message': _('Marketplace page !!!')})
            else:
                result = {'success': False, 'message': _('Marketplace is not Active !!!')}
            response.update(result)
            if response.get('addons', {}).get('wishlist') and response.get('customerId'):
                response['wishlist'] = self._website_Wishlist(response.get('customerId'))
        return self._response('marketplace', response)
#
    def get_marketplace_image_url(self, base_url, model_name, record_id, field_name, write_date, width=0, height=0):
        """ Returns a local url that points to the image field of a given browse record only for marketplace """
        # format of marketplace image url "base_url+/ marketplace / image / 139 / res.partner / profile_banner"
        write_date = re.sub("[^\d]", "", Datetime.to_string(write_date))

        if base_url and not base_url.endswith("/"):
            base_url = base_url + "/"
        if width or height:
            return '%swebsite/image/%s/%s/%s/%sx%s?unique=%s' % (base_url, model_name, record_id, field_name, width, height, write_date)
        else:
            return '%swebsite/image/%s/%s/%s?unique=%s' % (base_url, model_name, record_id, field_name, write_date)

    def checkReviewEligibility(self, seller_id, customer_id):
        """
        this method is responsible for marketplace ['/seller/review/check'] controller
        """

        sol_objs = request.env["sale.order.line"].sudo().search([("product_id.marketplace_seller_id", "=", seller_id), (
            "order_id.partner_id", "=", customer_id), ("order_id.state", "in", ["sale", "done"])])
        for_seller_total_review_obj = request.env["seller.review"].sudo().search(
            [('marketplace_seller_id', '=', seller_id), ('partner_id', '=', customer_id)])

        # This code must be used in create of review
        if len(sol_objs.ids) == 0:
            result = {"success": False, "message": _(
                "You have to purchase a product of this seller first.")}
        elif len(for_seller_total_review_obj.ids) >= len(sol_objs.ids):
            result = {"success": False, "message": _(
                "According to your purchase your review limit is over.")}
        else:
            result = {"success": True, "message": _("Eligible for write a review")}
        return result
#
    @route('/my/review/seller/<int:seller_id>', csrf=False, type='http', auth="none",  methods=['GET', 'POST'])
    def reviewSeller(self, seller_id, **kwargs):
        SellReviewObj = request.env['seller.review'].sudo()
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            if response.get('addons', {}).get('odoo_marketplace'):
                seller = request.env['res.partner'].s(
                    [('id', '=', seller_id), ('seller', '=', True)])
                if seller:
                    if request.httprequest.method == "GET":
                        sellerReviewDetail = SellReviewObj.search(
                            [('marketplace_seller_id', '=', seller_id), ('active', '=', True), ('state', '=', 'pub')])
                        reviewsDetail = self.getSellerReviewsDetail(sellerReviewDetail)
                        result = {
                            'SellerReview': reviewsDetail,
                            "seller_image": self.get_marketplace_image_url(self.base_url, 'res.partner', seller.id, 'image_1920', seller.write_date),
                            'seller_profile_image': self.get_marketplace_image_url(self.base_url, 'res.partner', seller.id, 'profile_image', seller.write_date),
                            'sellerReviewCount': len(sellerReviewDetail),
                            'success': True,
                            'message': _('Seller Found !!!')
                        }
                    elif request.httprequest.method == "POST":
                        result = self.checkReviewEligibility(seller_id, response.get('customerId'))
                        if result.get('success'):
                            if self._mData.get('msg') and self._mData.get('rating') and self._mData.get('title'):
                                review = {
                                    'msg': self._mData.get('msg'),
                                    'rating': int(self._mData.get('rating')),
                                    'title': self._mData.get('title'),
                                    'marketplace_seller_id': seller_id,
                                    "partner_id": response.get('customerId')
                                }
                                review_obj = request.env['seller.review'].sudo().with_context({'mail_create_nosubscribe':True}).create(review)
                                result = {'success': True, 'message': _(
                                    'Review create successfully for seller id')+'%s' % seller_id}
                            else:
                                result = {'success': False, 'message': _(
                                    'Pass the params properly for create review!!!')}
                    else:
                        result = {'success': False, 'message': _('Wrong Request')}
                else:
                    result = {'success': False, 'message': _('Seller not Found.')}

            else:
                result = {'success': False, 'message': 'Marketplace is not Active !!!'}
            response.update(result)
        return self._response('reviewSeller', response)

    @route(['/mobikul/marketplace/seller/review/vote/<int:review_id>'], csrf=False, type='http', auth="none",  methods=['POST'])
    def sellerReviewVote(self, review_id, **kwargs):
        review_help_obj = request.env['review.help'].sudo()
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            if response.get('addons', {}).get('odoo_marketplace'):
                ishelpful = self._mData.get('ishelpful') and "yes" or "no"
                vote_exist = review_help_obj.search(
                    [('seller_review_id', '=', review_id), ('customer_id', '=', response.get('customerId'))])

                if vote_exist:
                    vote_exist[0].write({"review_help": ishelpful})
                    result = {'success': True, 'message': _(
                        'seller review vote update successfully !!!')}
                else:
                    review_help_obj.sudo().create({"customer_id": response.get(
                        'customerId'), "seller_review_id": review_id, "review_help": ishelpful})
                    result = {'success': True, 'message': _(
                        'seller review vote create successfully !!!')}
            else:
                result = {'success': False, 'message': _('Marketplace is not Active !!!')}
            response.update(result)
        return self._response('sellerReviewVote', response)
#
    @route(['/mobikul/marketplace/seller/orderlines'], csrf=False, type='http', auth="none", methods=['POST'])
    def sellerOrderLines(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            if Partner and Partner.seller:
                if response.get('addons', {}).get('odoo_marketplace'):
                    result = {'success': True}
                    context = response.get('context', {})
                    SaleOrderLine = request.env['sale.order.line'].sudo()
                    domain = [('marketplace_seller_id', '=', response.get('customerId'))]
                    if self._mData.get('state'):
                        domain += [('marketplace_state', '=', self._mData.get('state'))]
                    result['tcount'] = SaleOrderLine.search_count(domain)
                    orderline = SaleOrderLine.search(domain, limit=self._mData.get('limit', response.get('itemsPerPage', 5)),
                                                     offset=self._mData.get('offset', 0), order="id desc")
                    result['sellerOrderLines'] = []
                    for order in orderline:
                        temp = {
                            'line_id': order.id,
                            'create_date': Datetime.to_string(order.create_date),
                            'order_reference': order.order_id.id,
                            'customer': order.order_partner_id.name,
                            'product': order.product_id.name,
                            'price_unit': _displayWithCurrency(context.get('lang_obj'), order.price_unit,
                                                               context.get('currencySymbol', ""), context.get('currencyPosition', "")),
                            'quantity': order.product_uom_qty,
                            'sub_total': _displayWithCurrency(context.get('lang_obj'), order.price_subtotal,
                                                              context.get('currencySymbol', ""), context.get('currencyPosition', "")),
                            'delivered_qty': order.qty_delivered,
                            'order_state': order.state,
                            'marketplace_state': order.marketplace_state,
                            'description': order.name,
                        }
                        result['sellerOrderLines'].append(temp)
                else:
                    result = {'success': False, 'message': ('Marketplace is not Active !!!')}
            else:
                result = {'success': False, 'message': ('Customer is not a seller !!!')}
            response.update(result)
        return self._response('sellerOrderLines', response)
#
    @route(['/mobikul/marketplace/seller/orderline/<int:line_id>'], csrf=False, type='http', auth="none", methods=['GET'])
    def sellerOrderLinesDetail(self, line_id, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            if Partner and Partner.seller:
                if response.get('addons', {}).get('odoo_marketplace'):
                    result = {'success': True}
                    context = response.get('context', {})
                    SaleOrderLine = request.env['sale.order.line'].sudo()
                    domain = [('id', '=', line_id)]
                    orderline = SaleOrderLine.search(domain)
                    result['sellerOrderLineDetail'] = {
                        'line_id': orderline.id,
                        'create_date': Datetime.to_string(orderline.create_date),
                        'order_reference': orderline.order_id.id,
                        'customer': orderline.order_partner_id.name,
                        'product': orderline.product_id.name,
                        'price_unit': _displayWithCurrency(context.get('lang_obj'), orderline.price_unit,
                                                           context.get('currencySymbol', ""),
                                                           context.get('currencyPosition', "")),
                        'quantity': orderline.product_uom_qty,
                        'sub_total': _displayWithCurrency(context.get('lang_obj'), orderline.price_subtotal,
                                                          context.get('currencySymbol', ""),
                                                          context.get('currencyPosition', "")),
                        'delivered_qty': orderline.qty_delivered,
                        'order_state': orderline.state,
                        'marketplace_state': orderline.marketplace_state,
                        'description': orderline.name,
                        'order_payment_acquirer': orderline.order_payment_acquirer_id.id and orderline.order_payment_acquirer_id.id or "",
                        'delivery_method': orderline.order_id.carrier_id and orderline.order_id.carrier_id.id or ""

                    }

                else:
                    result = {'success': False, 'message': 'Marketplace is not Active !!!'}
            else:
                result = {'success': False, 'message': 'Customer is not a seller !!!'}
            response.update(result)
        return self._response('sellerOrderLinesDetail', response)

    # {"domain": "[('marketplace_seller_id','=',65),('status','=','approved')]", "offset": 0, "limit": 100}
#
    @route(['/mobikul/marketplace/seller/ask'], csrf=False, type='http', auth="none", methods=['POST'])
    def sellerAsk(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            if Partner and Partner.seller:
                ask_Query = "<p><b>%s</b></p><p>%s</p>" % (
                    self._mData.get('title') or "", self._mData.get('body'))
                mail_id = Partner.message_post(
                    body=ask_Query, message_type='comment', subtype="mail.mt_comment", author_id=response.get('customerId'))
                if mail_id:
                    result = {'message': _('Seller query is posted Successfully'), 'success': True}
                else:
                    result = {'message': 'Something went wrong in posted query', 'success': False}
            else:
                result = {'success': False, 'message': 'Customer is not a seller !!!'}
            response.update(result)
        return self._response('sellerAsk', response)
#
    @route(['/mobikul/marketplace/seller/product'], csrf=False, type='http', auth="none", methods=['POST'])
    def sellerProduct(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            TemplateObj = request.env['product.template'].sudo()
            if Partner and Partner.seller:
                context = response.get('context', {})
                domain = [('marketplace_seller_id', '=', response.get('customerId'))]
                if self._mData.get('state'):
                    domain += [('status', '=', self._mData.get('state'))]
                productDetailsCount = TemplateObj.search_count(domain)
                productDetails = TemplateObj.search(domain, limit=self._mData.get('limit', response.get(
                    'itemsPerPage', 5)), offset=self._mData.get('offset', 0),  order="id desc")
                slr_product = []
                for prd in productDetails:
                    temp = {
                        "name": prd.name,
                        'templateId': prd.id,
                        'state': prd.status,
                        'thumbNail': _get_image_url(self.base_url, 'product.template', prd.id, 'image_1920', prd.write_date),
                        'seller': prd.marketplace_seller_id.name,
                        'qty': prd.qty_available,

                        'priceUnit': _displayWithCurrency(context.get('lang_obj'), prd.list_price, context.get('currencySymbol', ""), context.get('currencyPosition', "")),
                    }
                    slr_product.append(temp)
                result = {'success': True, 'sellerProduct': slr_product,
                          "tcount": productDetailsCount, "offset": self._mData.get('offset', 0)}
            else:
                result = {'success': False, 'message': 'Customer is not a seller !!!'}
            response.update(result)
        return self._response('sellerProduct', response)
#
    @route(['/mobikul/marketplace/seller/dashboard'], csrf=False, type='http', auth="none", methods=['GET'])
    def sellerDashboard(self, **kwargs):
        Mobikul = request.env["mobikul"].sudo()
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            PartnerObj = request.env['res.partner'].sudo()
            Partner = PartnerObj.browse(response.get('customerId'))
            if Partner and Partner.seller:
                sellerData = Mobikul.sellerDashboardData(seller_Obj=Partner)
                result = {'success': True, 'sellerDashboard': sellerData}
            else:
                result = {'success': False, 'message': 'Customer is not a seller !!!'}
            response.update(result)
        return self._response('sellerDashboard', response)

    @route(['/mobikul/marketplace/seller/terms'], csrf=False, type='http', auth="none", methods=['GET'])
    def sellerTermCond(self, **kwargs):
        response = self._authenticate(False, **kwargs)
        context = response.get('context')
        website = context.get('websiteObj')[0]
        term_and_condition = website and website.mp_term_and_condition
        if response.get('success'):
            result = {
                "term_and_condition": term_and_condition and remove_htmltags(term_and_condition) or "",
            }
            response.update(result)
        return self._response('sellerTermCond', response)

    @route(['/mobikul/marketplace/become/seller'], csrf=False, type='http', auth="none", methods=['POST'])
    def becomeSeller(self, **kwargs):
        global result
        Mobikul = request.env["mobikul"].sudo()
        UserObj = request.env['res.users'].sudo()
        response = self._authenticate(True, **kwargs)
        if response.get('success'):
            user = UserObj.browse([response.get('userId')])
            _logger.info("++++++++++++++ %r",self._mData)
            if not user.partner_id.seller:
                if self._mData.get('url_handler') and Mobikul.checkSellerUniqueUrl(self._mData.get('url_handler')):
                    Mobikul.set_marketplace_group_user(user)
                    user.partner_id.seller = True
                    user.partner_id.url_handler = self._mData.get('url_handler')
                    user.partner_id.country_id = self._mData.get('country_id')
                    result = {'success': True, 'message': 'Successfully became a seller'}
                else:
                    result = {'success': False, 'message': _(
                        "Seller profile 'url_handler' is not unique or absent.")}
            else:
                result = {'success': False, 'message': 'Customer is already a seller'}
        response.update(result)
        return self._response('becomeSeller', response)


    @route(['/mobikul/gdpr/deactivate'], csrf=False, type='http', auth="none", methods=['POST'])
    def deactivateAccount(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        UserObj = request.env['res.users'].sudo()
        result = {}
        if response.get('success'):
            user = UserObj.browse([response.get('userId')])
            if response.get('addons', {}).get('odoo_gdpr'):
                requestObj = request.env['gdpr.request'].sudo()
                if self._mData.get('type') == "temporary":
                    user.active = False
                    result = {'success': True, 'message': 'Your Account is temporary deactivated.'}
                elif self._mData.get('type') == "permanent":
                    requestVals = {
                        "partner_id": user.partner_id.id,
                        "operation_type": "all",
                        "action_type": "delete",
                        "state": "pending"
                    }
                    requestObj.create(requestVals)
                    user.active = False
                    result = {'success': True, 'message': 'Your Account is permananetly deactivated.'}
                else:
                    result = {'success': False,
                              'message': 'Type not found!. Niether permanent nor temporary '}
            else:
                result = {'success': False, 'message': 'Odoo GDPR is not install.'}
        response.update(result)
        return self._response('deactivateAccount', response)
#
    @route(['/mobikul/gdpr/download'], csrf=False, type='http', auth="none", methods=['GET'])
    def downloadAccount(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        UserObj = request.env['res.users'].sudo()
        result = {}
        if response.get('success'):
            user = UserObj.browse([response.get('userId')])
            if response.get('addons', {}).get('odoo_gdpr'):
                gdprRequest = request.env['gdpr.request'].sudo()
                downloadReq = gdprRequest.search([("partner_id", "=", user.partner_id.id), (
                    "action_type", "=", "download"), ("operation_type", "=", "all")], order="id desc", limit=1)
                if downloadReq:
                    if downloadReq.state == "pending":
                        result = {
                            "downloadRequest": False,
                            "downloadMessage": "We have already received your request, it is in pending state.",
                            "downloadUrl": ""
                        }
                    elif downloadReq.state == "cancel":
                        result = {
                            "downloadRequest": False,
                            "downloadMessage": "Your request is cancel by Admin, for more info contact support.",
                            "state": "cancel",
                            "downloadUrl": ""
                        }
                    elif downloadReq.state == "done":
                        result = {
                            "downloadRequest": False,
                            "state": "done",
                            "downloadMessage": "Your Download is ready, it will expire in 30 days.",
                            "downloadUrl": self.base_url+"web/content/%s?download=true" % downloadReq.attach_id.id
                        }
                    else:
                        result = {
                            "downloadMessage": "Something Went Wrong",
                        }
                else:
                    result = {
                        "downloadRequest": True,
                        "downloadMessage": "",
                        "downloadUrl": ""
                    }
            else:
                result = {'success': False, 'message': 'Odoo GDPR is not install.'}
        response.update(result)
        return self._response('downloadAccount', response)
#
    @route(['/mobikul/gdpr/downloadRequest'], csrf=False, type='http', auth="none", methods=['POST'])
    def downloadRequest(self, **kwargs):
        response = self._authenticate(True, **kwargs)
        UserObj = request.env['res.users'].sudo()
        result = {}
        if response.get('success'):
            user = UserObj.browse([response.get('userId')])
            if response.get('addons', {}).get('odoo_gdpr'):
                requestObj = request.env['gdpr.request'].sudo()
                if self._checkAlreadyRequest(requestObj, user):
                    result = {'success': False,
                              'message': 'Your download request is already submitted.'}
                else:
                    requestVals = {
                        "partner_id": user.partner_id.id,
                        "operation_type": "all",
                        "action_type": "download",
                        "state": "pending"
                    }
                    requestObj.create(requestVals)
                    result = {'success': True,
                              'message': 'Your download request is submitted successfully.'}
            else:
                result = {'success': False, 'message': 'Odoo GDPR is not install.'}
        response.update(result)
        return self._response('downloadRequest', response)

    def _checkAlreadyRequest(self, requestObj, user):
        domain = [
            ("partner_id", "=", user.partner_id.id),
            ("operation_type", "=", "all"),
            ("action_type", "=", "download"),
            ("state", "=", "pending"),
        ]
        req = requestObj.search(domain)
        return req and True or False
