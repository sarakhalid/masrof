# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
import uuid
import re
import hashlib
import datetime
from functools import wraps
from ast import literal_eval
from base64 import b64decode
import json
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import werkzeug
from odoo.http import request, Controller, route
from datetime import date, datetime,timedelta
from odoo.fields import Datetime, Date, Selection
from odoo import fields, models, api, _



from odoo import _
from odoo.addons.mobikul.tool.help import _displayWithCurrency, _get_image_url, remove_htmltags
import logging
import datetime
_logger = logging.getLogger(__name__)


class xml(object):

    @staticmethod
    def _encode_content(data):
        # .replace('&', '&amp;')
        return data.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

    @classmethod
    def dumps(cls, apiName, obj):
        _logger.warning("%r : %r" % (apiName, obj))
        if isinstance(obj, dict):
            return "".join("<%s>%s</%s>" % (key, cls.dumps(apiName, obj[key]), key) for key in obj)
        elif isinstance(obj, list):
            return "".join("<%s>%s</%s>" % ("I%s" % index, cls.dumps(apiName, element), "I%s" % index) for index, element in enumerate(obj))
        else:
            return "%s" % (xml._encode_content(obj.__str__()))

    @staticmethod
    def loads(string):
        def _node_to_dict(node):
            if node.text:
                return node.text
            else:
                return {child.tag: _node_to_dict(child) for child in node}
        root = ET.fromstring(string)
        return {root.tag: _node_to_dict(root)}


class WebServices(Controller):

    def __decorateMe(func):
        @wraps(func)
        def wrapped(inst, *args, **kwargs):
            inst._mData = request.httprequest.data and json.loads(
                request.httprequest.data.decode('utf-8')) or {}
            _logger.info(inst._mData)
            inst._mAuth = request.httprequest.authorization and (request.httprequest.authorization.get(
                'password') or request.httprequest.authorization.get("username")) or None
            inst.base_url = request.httprequest.host_url
            inst._lcred = {}
            inst._sLogin = False
            inst.auth = True
            inst._mLang = request.httprequest.headers.get("lang") or None
            inst._mPricelist = request.httprequest.headers.get("pricelist") or None
            if request.httprequest.headers.get("Login"):
                try:
                    inst._lcred = literal_eval(
                        b64decode(request.httprequest.headers["Login"]).decode('utf-8'))
                except:
                    inst._lcred = {"login": None, "pwd": None}
            elif request.httprequest.headers.get("SocialLogin"):
                inst._sLogin = True
                try:
                    inst._lcred = literal_eval(
                        b64decode(request.httprequest.headers["SocialLogin"]).decode('utf-8'))
                except:
                    inst._lcred = {"authProvider": 1, "authUserId": 1234567890}
            else:
                inst.auth = False
            return func(inst, *args, **kwargs)
        return wrapped

    def _available_api(self):
        API = {
            'homepage': {
                'description': 'HomePage API',
                'uri': '/mobikul/homepage'
            },
            'sliderProducts': {
                'description': 'Product(s) of given Product Slider Record',
                'uri': '/mobikul/sliderProducts/&lt;int:product_slider_id&gt;',
            },
            'login': {
                'description': 'Customer Login',
                'uri': '/mobikul/customer/login',
            },
            'signUp': {
                'description': 'Customer signUp',
                'uri': '/mobikul/customer/signUp',
            },
            'resetPassword': {
                'description': 'Customer Reset Password',
                'uri': '/mobikul/customer/resetPassword',
            },
            'splashPageData': {
                'description': 'Default data to saved at app end.',
                'uri': '/mobikul/splashPageData',
            },
            'getSubCategories':
                {
                    'description': 'get SubCategories',
                    'url':'/mobikul/getSubCategories'
                },
            'register':
                {
                    'description': 'get register',
                    'url': '/mobikul/register'
                },
            'loginphone':
                {
                    'description': 'get loginphone',
                    'url': '/mobikul/loginphone'
                }
            ,
            'listToCart':
                {
                    'description': 'listToCart',
                    'url': '/mobikul/listToCart',
                },
            'registerphone':
                {
                    'description': 'get registerphone',
                    'url': '/mobikul/registerphone'
                }
            ,
            'checkPostCode':
                {
                    'description': 'get checkPostCode',
                    'url': '/mobikul/checkPostCode'
                }
            ,
            'getDeliverySchedule':
                {
                    'description': 'get getDeliverySchedule',
                    'url': '/mobikul/getDeliverySchedule'
                }
            ,
            'livechat':
                {
                    'description': 'get livechat',
                    'url': '/mobikul/livechat',
                }
            ,
            'getsession':
                {
                    'description': 'get livechat/getsession',
                    'url': '/mobikul/livechat/getsession',
                }
            ,
            'postChat':
                {
                    'description': 'post livechat/postChat',
                    'url': '/mobikul/livechat/postChat',
                }
            ,
            'getSessionData':
                {
                    'description': 'get livechat/getSessionData',
                    'url': '/mobikul/livechat/getSessionData',
                }
            ,

            'getList':
                {
                    'description': 'get getList',
                    'url': '/mobikul/getList',
                }
                  ,
            'getListDetails':
                {
                    'description': 'get getListDetails',
                    'url': '/mobikul/getListDetails',
                },
            'createList':
                {
                    'description': 'get createlist',
                    'url': '/mobikul/createList',
                }
            ,
            'editList':
                {
                    'description': 'get editList',
                    'url': '/mobikul/editList',
                },
            'deleteList':
                {
                    'description': 'get deleteList',
                    'url': '/mobikul/deleteList'
                },

            'deleteItemList':
                {
                    'description': 'deleteItemList',
                    'url': '/mobikul/deleteItemList',
                }
                ,
            'addItemList':
                {
                    'description': 'addItemList',
                    'url': '/mobikul/addItemList',
                }
            ,
            'editItemList':
                {
                    'description': 'editItemList',
                    'url': '/mobikul/editItemList',
                }
            ,
            'removetemList':
                {
                    'description': 'removetemList',
                    'url': '/mobikul/removetemList',
                }
            ,

            'paymentTest':
                {
                    'description': 'get paymentTest',
                    'url': '/mobikul/paymentTest',
                }
            ,
            'paymentLive':
                {
                    'description': 'get deleteList',
                    'url': '/mobikul/paymentLive',
                },
            'mobikul/payment':
                {
                    'description': 'get payment',
                    'url': '/mobikul/payment/hyperpay/checkout/create',
                },
            'mobikul/privacypolicy':
                {
                    'description': 'get payment',
                    'url': '/mobikul/privacypolicy',
                },
            'mobikul/aboutus':
                {
                    'description': 'get aboutus',
                    'url': '/mobikul/aboutus',
                },
            'mobikul/getPdf':
                {
                    'description': 'get getPdf',
                    'url': '/mobikul/getPdf',
                },
            '/mobikul/deliveryBoyLocation':
                {
                    'description': 'get deliveryBoyLocation',
                    'url':'/mobikul/deliveryBoyLocation',
                },
            '/mobikul/my/reOrder':
                {
                    'description': 'post reorder',
                    'url': '/mobikul/my/reOrder',
                },
            '/mobikul/my/parking':
                {
                    'description': 'post parking',
                    'url': '/mobikul/my/parking',
                },
            '/mobikul/mycart/addToCart2':
                {
                    'description': 'post addToCart2',
                    'url': '/mobikul/mycart/addToCart2',
                },
            '/mobikul/my/promoCode':
                {
                    'description': 'post promoCode',
                    'url': '/mobikul/my/promoCode',
                },
            '/mobikul/version':
                {
                    'description': 'post version',
                    'url': 'mobikul/version',
                },









        }
        return API

    def _wrap2xml(self, apiName, data):
        resp_xml = "<?xml version='1.0' encoding='UTF-8'?>"
        resp_xml += '<odoo xmlns:xlink="http://www.w3.org/1999/xlink">'
        resp_xml += "<%s>" % apiName
        resp_xml += xml.dumps(apiName, data)
        resp_xml += "</%s>" % apiName
        resp_xml += '</odoo>'
        return resp_xml

    def _response(self, apiName, response, ctype='json'):
        if response.get("context"):
            response.pop("context")
        if 'local' in response:
            response.pop("local")
        if ctype == 'json':
            mime = 'application/json; charset=utf-8'
            body = json.dumps(response)
        else:
            mime = 'text/xml'
            body = self._wrap2xml(apiName, response)
        headers = [
            ('Content-Type', mime),
            ('Content-Length', len(body))
        ]
        return werkzeug.wrappers.Response(body, headers=headers)

    @__decorateMe
    def _authenticate(self, auth, **kwargs):
        if 'api_key' in kwargs:
            api_key = kwargs.get('api_key')
        elif request.httprequest.authorization:
            api_key = request.httprequest.authorization.get(
                'password') or request.httprequest.authorization.get("username")
        else:
            api_key = False
        Mobikul = request.env['mobikul'].sudo().search([], limit=1)
        payload = {"lang": self._mLang, "base_url": self.base_url,
                   "pricelist": self._mPricelist, "mobikul_obj": Mobikul}
        response = Mobikul._validate(api_key, payload)
        if not response.get('success'):
            return response
        if auth:
            result = Mobikul.authenticate(self._lcred, kwargs.get(
                'detailed', False), self._sLogin, context=response.get("context"))
            response.update(result)
        request.context = dict(response.get("context"))
        return response

    @route('/mobikul/', csrf=False, type='http', auth="none")
    def index(self, **kwargs):
        """ HTTP METHOD : request.httprequest.method
        """
        response = self._authenticate(False, **kwargs)
        if response.get('success'):
            data = self._available_api()
            return self._response('mobikulApi', data, 'xml')
        else:
            headers = [
                ('WWW-Authenticate', 'Basic realm="Welcome to Odoo Webservice, please enter the authentication key as the login. No password required."')]
            return werkzeug.wrappers.Response('401 Unauthorized %r' % request.httprequest.authorization, status=401, headers=headers)

    def _languageData(self, mobikul):
        temp = {
            'defaultLanguage': (mobikul.default_lang.code, mobikul.default_lang.name),
            'allLanguages': [(id.code, id.name) for id in mobikul.language_ids],
            'TermsAndConditions': mobikul.enable_term_and_condition
        }
        return temp

    def mobikul_display_address(self, address, name=""):
        return (name or "") + (name and "\n" or "") + address

    def _checkFullAddress(self, Partner):
        mandatory_fields = ["street", "city", "state_id", "zip", "country_id"]
        val = [True if mf == "state_id" and not Partner.country_id.state_ids else getattr(
            Partner, mf) for mf in mandatory_fields]
        return all(val)

    def _getAquirerCredentials(self, order_name, Acquirer, response,txn,order):

        #_logger.info("+++%s",pay_url)
        if Acquirer.mobikul_reference_code == 'COD':
            return {'status': True, 'code': 'COD', 'auth': False}
        elif Acquirer.mobikul_reference_code == 'STRIPE_W':
            Transaction = request.env['payment.transaction'].sudo()
            return {'status': True, 'paymentReference': Transaction.get_next_reference(order_name), 'code': 'STRIPE', 'auth': True, 'secret_key': Acquirer.stripe_checkout_client_secret_key, 'publishable_key': Acquirer.stripe_checkout_publishable_key}
        elif Acquirer.mobikul_reference_code == 'STRIPE_E':
            Transaction = request.env['payment.transaction'].sudo()
            return {'status': True, 'paymentReference': Transaction.get_next_reference(order_name), 'code': 'STRIPE', 'auth': True, 'secret_key': Acquirer.stripe_secret_key, 'publishable_key': Acquirer.stripe_publishable_key}
        elif Acquirer.mobikul_reference_code == 'PAYULATAM':
            pay_url = "%sapp/payment/payulatam?tx_refrence=%s&acquirer_id=%s&txn_id=%s&amount=%s&currency=%s&partner_email=%s"%(self.base_url,txn.reference,Acquirer.id,txn.id,order.amount_total,order.pricelist_id.currency_id.name,order.partner_id.email)
            Transaction = request.env['payment.transaction'].sudo()
            return {'status': True, 'code': 'PAYULATAM', 'auth': True,'url': pay_url}
        elif Acquirer.mobikul_reference_code == 'HYPERPAY':
            pay_url = "%sapp/payment/hyperpay/checkout/create?tx_refrence=%s&acquirer_id=%s&txn_id=%s&amount=%s&currency=%s&partner_email=%s"%(self.base_url,txn.reference,Acquirer.id,txn.id,order.amount_total,order.pricelist_id.currency_id.name,order.partner_id.email)
            Transaction = request.env['payment.transaction'].sudo()
            return {'status': True, 'code': 'HYPERPAY', 'auth': True,'url': pay_url}
        else:
            return {'status': False, 'message': _('Payment Mode not Available.')}

    def _getAquirerState(self, Acquirer, status=False):

        if Acquirer.mobikul_reference_code in ['COD']:
            return "pending"
        elif Acquirer.mobikul_reference_code in ['STRIPE_W', 'STRIPE_E']:
            return STATUS_MAPPING['STRIPE'].get(status, 'pending')
        else:
            return "pending"

    def _orderReview(self, user, response, Acquirer):
        last_order = user.partner_id.last_mobikul_so_id
        partner_ido=request.env['res.partner'].sudo().search([('id','=',user.partner_id.id)],limit=1)
        if(partner_ido.email==False):
            partner_ido.sudo().write({'email': partner_ido.phone})


        if(partner_ido.country_id.id != 192):
            partner_ido.sudo().write({'country_id':192})


        if last_order and len(last_order.order_line):
            local = response.get('context', {})
            payment_icons=""

            Acquirer_state="TEST"
            if(Acquirer.id):
                last_order.payment_acquirer = Acquirer.id
                payment_icons = Acquirer.payment_icon_ids.mapped('name')[0]
                if(Acquirer.state=="enabled"):
                    Acquirer_state="LIVE"



            if self._mData.get('pickupLocationId'):
                last_order.warehouse_id = int(self._mData.get('pickupLocationId'))

            if self._mData.get('shippingAddressId'):
                last_order.partner_shipping_id = int(self._mData.get('shippingAddressId'))
            if self._mData.get('shippingTime'):

                shippingTime =self._mData.get('shippingTime')
                date_time_obj = datetime.datetime.strptime(shippingTime, '%d/%m/%Y')
                last_order.shipping_time =date_time_obj
            if self._mData.get('scheduleId'):
                last_order.delivery_schedule = int(self._mData.get('scheduleId'))
            if self._mData.get('comment'):
                last_order.note = self._mData.get('comment')
            if self._mData.get('promoCode'):
                promoCode = self._mData.get('promoCode')
                apply_coupon=request.env['sale.coupon.apply.code'].sudo()
                #.create({'coupon_code': promoCode})
                apply_coupon.apply_coupon(last_order,promoCode)


            if response.get('addons', {}).get('website_sale_delivery') and self._mData.get("shippingId"):
                last_order.delivery_method = int(self._mData.get('shippingId'))
                last_order.sudo()._check_carrier_quotation(force_carrier_id=int(self._mData.get("shippingId")))
            last_order.sudo().recompute_coupon_lines()
            result = {
                "orderId":last_order.id,
                "name": last_order.name,
                "billingAddress": self.mobikul_display_address(last_order.partner_invoice_id._display_address(), last_order.partner_invoice_id.name),
                "shippingAddress": self.mobikul_display_address(last_order.partner_shipping_id._display_address(), last_order.partner_shipping_id.name),
                "paymentAcquirer": Acquirer.name or "",
                "paymentAcquirerCode": Acquirer.mobikul_reference_code or "",
                "paymentAcquirerState": Acquirer_state or "",
                "paymentAcquirerBrand": payment_icons or "",
                "subtotal": {"title": _("Subtotal"),
                             "value": _displayWithCurrency(local.get('lang_obj'), last_order.amount_untaxed, local.get('currencySymbol'), local.get('currencyPosition')),
                             },
                "tax": {"title": _("Taxes"),
                        "value": _displayWithCurrency(local.get('lang_obj'), last_order.amount_tax, local.get('currencySymbol'), local.get('currencyPosition')),
                        },
                "grandtotal": {"title": _("Total"),
                               "value": _displayWithCurrency(local.get('lang_obj'), last_order.amount_total, local.get('currencySymbol'), local.get('currencyPosition')),
                               },
                "amount": last_order.amount_total,
                "currency": last_order.pricelist_id.currency_id.name or "",
                "items": [],
            }
            discount=0.0
            deliverycount=0
            is_delivery=last_order.order_line.sudo().search([('order_id.id','=',last_order.id),('is_delivery','=','1')])
            for item in last_order.order_line:
                if response.get('addons', {}).get('website_sale_delivery') and item.is_delivery:
                    deliverycount +=1
                    prof = request.env['delivery.carrier'].sudo().search([('id', '=', item.order_id.carrier_id.id)])

                    shippingMethod = {
                        "tax": [tax.name for tax in item.tax_id],
                        "name": prof.name,
                        "description": prof.website_description or "",
                        "shippingId": item.order_id.carrier_id.id,
                        "total": _displayWithCurrency(local.get('lang_obj'), item.price_subtotal,
                                                      local.get('currencySymbol'), local.get('currencyPosition')),
                    }
                    result.update({"delivery": shippingMethod,"subtotal": {"title": _("Subtotal"),
                             "value": _displayWithCurrency(local.get('lang_obj'), last_order.amount_untaxed-item.price_subtotal, local.get('currencySymbol'), local.get('currencyPosition')),
                             },
                                   })
                else:
                    product_id = item.product_id
                    prof = request.env['product.product'].sudo().search([('id', '=', item.product_id.id)])

                    comb_info = product_id.product_tmpl_id.with_context(local)._get_combination_info(combination=False, product_id=product_id.id,add_qty=1, pricelist=local.get("pricelist"), parent_combination=False, only_template=False)
                    uomQty=product_id.product_tmpl_id.uom_QTY
                    isOffer = False
                    offerPrice = 0.0,
                    msgOffer = ""
                    priceUnit=prof.list_price
                    if(priceUnit==0.0):
                        priceUnit=item.price_unit

                    today = fields.date.today()

                    # # offer=request.env['discount.offer'].sudo().search([('product_id.id','=',int(product.get('productId'))),('date_start', '>', today), ('date_end', '<=', today)],limit=1)
                    offer = request.env['discount.offer'].sudo().search(
                        [('product_id.id', '=', prof.id), ('date_start', '<=', today),
                         ('date_end', '>=', today)], limit=1)
                    if (offer):
                        isOffer = True
                        offerPrice = offer.priceAfteroffer
                        msgOffer = offer.name
                        print('msgOffer', msgOffer)
                        discount +=((prof.list_price-offerPrice)*item.product_uom_qty)

                    # if (user.id == 105):

                    #     print(today,'today')

                    if(uomQty):
                        pass
                    else:
                        uomQty="1"

                    temp = {
                        "lineId": item.id,
                        "templateId": product_id and product_id.product_tmpl_id.id or "",
                        "name": prof.name,
                        "uomQty":str(uomQty),
                       # "name": product_id and product_id.display_name or item.name,
                        "thumbNail": _get_image_url(self.base_url, 'product.product', product_id and product_id.id or "", 'image_512', product_id and product_id.write_date),
                        "priceReduce": comb_info['has_discounted_price'] and _displayWithCurrency(local.get('lang_obj'), comb_info['price'], local.get('currencySymbol'), local.get('currencyPosition')) or "",
                        #"priceUnit": _displayWithCurrency(local.get('lang_obj'), comb_info['has_discounted_price'] and comb_info['list_price'] or comb_info['price'],local.get('currencySymbol'), local.get('currencyPosition')),
                        #"priceUnit": _displayWithCurrency(local.get('lang_obj'), item.price_subtotal, local.get('currencySymbol'), local.get('currencyPosition')),
                        "priceUnit": _displayWithCurrency(local.get('lang_obj'), priceUnit,
                                                          local.get('currencySymbol'), local.get('currencyPosition')),

                        "qty": item.product_uom_qty,
                        "total": _displayWithCurrency(local.get('lang_obj'), item.price_subtotal, local.get('currencySymbol'), local.get('currencyPosition')),
                        "discount": item.discount and "(%d%% OFF)" % item.discount or "",
                        'isOffer': isOffer,
                        'offerPrice': _displayWithCurrency(local.get('lang_obj'), offerPrice,
                                                           local.get('currencySymbol', ""),
                                                           local.get('currencyPosition', "")),

                        'msgOffer': msgOffer,
                    }
                    print('temp',temp)
                    result['items'].append(temp)



            vals = {
                'acquirer_id': Acquirer.id,
                'return_url': ''
            }
            txn = last_order._create_payment_transaction(vals)
            result['transaction_id'] = txn.id
            result['paymentData'] = self._getAquirerCredentials(last_order.name, Acquirer, response,txn,last_order)
            result['paymentData'].update({'customer_email': last_order.partner_id.email})
            result.update({"discount": {"title": _("Discount"),
                                        "value": _displayWithCurrency(local.get('lang_obj'), discount,
                                                                      local.get('currencySymbol'),
                                                                      local.get('currencyPosition')),
                                        }, })
            print('result2',result)
        else:
            result = {'success': False, 'message': _('Add some products in order to proceed.')}
        return result

    def _tokenUpdate(self, customer_id=False):
        FcmRegister = request.env['fcm.registered.devices'].sudo()
        partner=request.env['res.partner'].sudo().search([('id','=',int(customer_id))],limit=1)
        if(self._mData.get("fcmDeviceId")!=""):
            already_registered = FcmRegister.search(
                [('device_id', '=', self._mData.get("fcmDeviceId"))])
            if already_registered:
                already_registered.write(
                    {'token': self._mData.get("fcmToken"), 'customer_id': customer_id,'platformType':self._mData.get("platformType", ""),
                    'version': self._mData.get("version", ""),})
                partner.write({'platformType':self._mData.get("platformType", "")})

            else:
                if(customer_id and self._mData.get("fcmDeviceId", "")!=""):
                    FcmRegister.create({
                        'token': self._mData.get("fcmToken", ""),
                        'device_id': self._mData.get("fcmDeviceId", ""),
                        'description': "%r" % self._mData,
                        'customer_id': customer_id,
                        'platformType':self._mData.get("platformType", ""),
                        'version': self._mData.get("version", ""),

                    })
                    partner.write({'platformType': self._mData.get("platformType", "")})
        return True

    def _pushNotification(self, token, condition='signup', customer_id=False):
        notifications = request.env['mobikul.push.notification.template'].sudo().search([
            ('condition', '=', condition)])
        for n in notifications:
            n._send({'to': token}, customer_id)
        return True
    def _pushNotification2(self, token, condition='signup', customer_id=False):
        notifications = request.env['mobikul.push.notification.template'].sudo().search([
            ('condition', '=', condition)])
        to_data = dict(to=token or "")
        result = notifications.sudo()._send(
            to_data, customer_id)
        return True



    def add2Ws(self, context, product_id):
        wishlistObj = request.env['product.wishlist'].sudo()
        p = request.env['product.product'].sudo().browse(int(product_id))
        partner_id = context.get("partner").id
        try:
            wishlist = wishlistObj.search([("partner_id","=",partner_id),("product_id","=",p.id)])
            if wishlist:
                result = {'success':False,'message':"Item already in Wishlist"}
            else:
                wishlistObj._add_to_wishlist(
                    context.get("pricelist").id,
                    context.get("currency_id"),
                    context.get("website_id"),
                    p._get_combination_info_variant()['price'],
                    p.id,
                    partner_id
                )
                result = {'success': True,
                          'message': _("Item moved to Wishlist")
                          }
        except Exception as e:
            result = {
                'success': False,
                'message': _('Please try again later'),
                'detail': 'Error Details: %r' % e,
            }
        return result

    def _sendPaymentAcknowledge(self, last_order, Partner, txn, context):
        result = {}
        if txn.state != 'error':
            context.update({"send_email": True})
            last_order.with_context(context).action_confirm()
            last_order._send_order_confirmation_mail()
            Partner.last_mobikul_so_id = False
            device_id = request.env['fcm.registered.devices'].sudo().search(
                [('customer_id', '=', Partner.id)], limit=1)
            notification_template = request.env['mobikul.push.notification.template'].sudo().search(
                [('condition', '=', 'orderplaced')], limit=1)
            # self._pushNotification(self._mData.get("fcmToken", ""), condition='orderplaced',
            #                        customer_id=Partner.id)
            self._pushNotification2(token=device_id and device_id.token, condition='orderplaced',
                                   customer_id=Partner.id)

            # if (device_id and notification_template):
            #     to_data = dict(to=device_id and device_id.token or "")
            #     result = notification_template.sudo()._send(
            #         to_data, device_id and device_id.customer_id and device_id.customer_id.id or False)

            result.update({
                'url': "/mobikul/my/order/%s" % last_order.id,
                'name': last_order.name,
                'cartCount': 0,
                'success': True,
                'message': _('Your order') + ' %s ' % (last_order.name) + _('has been placed successfully.'),
                'transaction_id': txn.id,
            })
            if txn.state in ['pending', 'draft']:
                result.update({'txn_msg': remove_htmltags(txn.acquirer_id.pending_msg)})
            elif txn.state == 'done':
                result.update({'txn_msg': remove_htmltags(txn.acquirer_id.done_msg)})
            elif txn.state == 'cancel':
                result.update({'txn_msg': remove_htmltags(txn.acquirer_id.cancel_msg)})
            else:
                result.update({'txn_msg': 'No transaction state found..'})

        else:
            result.update({
                'transaction_id': txn.id,
                'success': False,
                'message': "ERROR",
                'txn_msg': txn.state_message or "ERROR"
            })
        return result

    def placeOrder(self, context):
        result = {}
        Partner = context.get("partner")

        if Partner:
            last_order = Partner.last_mobikul_so_id
            Partner.countSales=Partner.countSales+1
            orderId=last_order.id
            if last_order:
                if int(self._mData.get('transaction_id')) in last_order.transaction_ids.mapped('id'):
                    txn = request.env['payment.transaction'].sudo().browse(
                        [int(self._mData.get('transaction_id'))])
                    txn._post_process_after_done()
                    #_logger.info("++++++++%r",last_order.invoice_status)
                    #last_order.invoice_status='invoiced'
                    #_logger.info("++++++++%r",last_order.invoice_status)
                    paymentStatus=self._mData.get('paymentStatus')

                    tx_values = {
                        'type': 'form',
                        'state': self._getAquirerState(txn.acquirer_id, self._mData.get('paymentStatus')),
                        'acquirer_reference': self._mData.get('acquirer_reference') or "acquirer_reference key is absent in payload data.",
                        "state_message": 'MOBIKUL',
                    }
                    txn.write(tx_values)

                    result.update(self._sendPaymentAcknowledge(last_order, Partner, txn, context))

                    _logger.info("------result--%r--", result)
                    result.update({'orderId':orderId})


                else:
                    result = {'success': False, 'message': _(
                        'Transaction Id not found in order.')}
            else:
                result = {'success': False, 'message': _(
                    'Add some products in order to proceed.')}
        else:
            result = {'success': False, 'message': ('Account not found !!!')}
        return result
