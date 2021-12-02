# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################


import pytz
import requests
import datetime
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.mobikul.tool.help import _displayWithCurrency, _get_image_url, _changePricelist, remove_htmltags, AQUIRER_REF_CODES, STATUS_MAPPING, _get_next_reference,EMPTY_ADDRESS
from odoo import http,_
from odoo.http import request, route

from odoo import api, fields, models,tools, _
from odoo.exceptions import ValidationError
from datetime import datetime, date,timedelta
from odoo.addons.mobikul.tool.service import WebServices
from odoo.addons.payment_hyperpay.data.payment_icon import payment_icon
from odoo.addons.payment_hyperpay.controllers.main import _get_checkout_id
import urllib, urllib.request, urllib.parse




from collections import defaultdict
try:
	from urllib.parse import urlencode
	from urllib.request import build_opener, Request, HTTPHandler
	from urllib.error import HTTPError, URLError
except ImportError:
	from urllib import urlencode
	from urllib2 import build_opener, Request, HTTPHandler, HTTPError, URLError
import json

import logging
_logger = logging.getLogger(__name__)



class RespaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    def _invoice_sale_orders(self):
        if self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice'):
            for trans in self.filtered(lambda t: t.sale_order_ids):
                ctx_company = {'company_id': trans.acquirer_id.company_id.id,
                               'force_company': trans.acquirer_id.company_id.id}
                trans = trans.with_context(**ctx_company)
                trans.sale_order_ids._force_lines_to_invoice_policy_order()
                mobikul_reference_code=trans.acquirer_id.mobikul_reference_code
                if (mobikul_reference_code not in ['COD']):
                    invoices = trans.sale_order_ids._create_invoices()
                    trans.invoice_ids = [(6, 0, invoices.ids)]


    # def _reconcile_after_transaction_done(self):
    #     # Validate invoices automatically upon the transaction is posted.
    #     invoices = self.mapped('invoice_ids').filtered(lambda inv: inv.state == 'draft')
    #     invoices.post()
    #
    #     # Create & Post the payments.
    #     payments = defaultdict(lambda: self.env['account.payment'])
    #     for trans in self:
    #         print('mobikul_reference_code',trans.acquirer_id.mobikul_reference_code)
    #         print('mobikul_reference_code2', trans.acquirer_id.mobikul_reference_code)
    #         if trans.payment_id:
    #             payments[trans.acquirer_id.company_id.id] += trans.payment_id
    #             continue
    #
    #         payment_vals = trans._prepare_account_payment_vals()
    #         payment = self.env['account.payment'].sudo().create(payment_vals)
    #         print(payment)
    #
    #         payments[trans.acquirer_id.company_id.id] += payment
    #
    #         # Track the payment to make a one2one.
    #         trans.payment_id = payment
    #         #if(trans.acquirer_id.mobikul_reference_code not in ['COD']):
    #
    #
    #         for company in payments:
    #             payments[company].with_context(force_company=company, company_id=company).post()


class ResPartner(models.Model):
    _inherit = 'res.partner'
    last_mobikul_so_id = fields.Many2one('sale.order', string='Last Order from Mobikul App')
    banner_image = fields.Binary('Banner Image', attachment=True)
    platformType = fields.Char('Platform Type', readonly=True)
    countSales = fields.Integer(string='Sale Order Count')
    fixed_otp=fields.Boolean("Fixed OTP")
    token_ids = fields.One2many('fcm.registered.devices', 'customer_id',
                                string='Registered Devices', readonly=True)







class SaleOrder(models.Model):
    _inherit = "sale.order"
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Waiting'),
        ('processing','Processing'),
        ('verification', 'Verification'),
        ('ready', 'Ready'),
        ('transit','transit'),
        ('delivery','out for delivery'),
        ('done', 'delivered'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    customer_state = fields.Selection([
        ('accepted', 'accepted '),
        ('processed', 'on process'),
        ('delivery', 'out for delivery'),
        ('delivered', 'delivered'),
    ], string='Customer Status ', readonly=True, copy=False, index=True, tracking=3, compute='def_customer_state')

    cart_count = fields.Integer(compute='_compute_cart_count', string='Cart Count')
    shipping_time = fields.Date('Shipping Time')
    font = fields.Char('Font', compute='def_customer_state')
    background = fields.Char('background', compute='def_customer_state')
    delivery_schedule = fields.Many2one('delivery.schedule',string='Delivery Schedule')
    delivery_schedule = fields.Many2one('delivery.schedule', string='Delivery Schedule')
    delivery_boy = fields.Many2one('res.partner', string='Delivery boy')
    delivery_boy_phone = fields.Char(related='delivery_boy.phone', string='Delivery boy Phone')
    zip = fields.Char(related='partner_shipping_id.zip',string='zip')
    zip_category = fields.Many2one('zip.category',string='zip Category',compute='get_zip_category')
    delivery_method = fields.Many2one('delivery.carrier', string='Shipping Methods')
    payment_acquirer = fields.Many2one('payment.acquirer',string='Payment Method')

    def payment_status(self):
        tz = pytz.timezone('Asia/Riyadh')
        #now = datetime.now(tz=tz)
        #now =datetime.datetime.now()
        #previous_date=now - datetime.timedelta(days=2)
        previous_date = fields.Datetime.now() - timedelta(days=2)
        result = []
        #tx = self.env['payment.transaction'].sudo().search(['&','&',('state', '=', 'draft'),('partner_id.last_mobikul_so_id.state','=','draft'),('create_date', ">", now.strftime('%Y-%m-%d'))])
        #tx = self.env['payment.transaction'].sudo().search(['&',('state', '=', 'draft'),('acquirer_id.provider','=','hyperpay'),('create_date', ">", previous_date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT))])
        tx = self.env['payment.transaction'].sudo().search(
            [('state', '=', 'draft'), ('acquirer_id.provider', '=', 'hyperpay'),
             ('create_date', ">", previous_date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT))])
        count=0
        if(len(tx)>0):
            for t in tx:
                for order in t.sale_order_ids:
                    if(order.state=="draft"):
                        count+=1
                        print(order.name)
                        if t.hyperpay_checkout_id:
                            result=[]
                            acq = t.acquirer_id
                            url = "https://oppwa.com/v1/checkouts/"+t.hyperpay_checkout_id+"/payment"
                            url += '?entityId='+acq.hyperpay_merchant_id

                            try:
                                opener = build_opener(HTTPHandler)
                                request = Request(url, data=b'')
                                request.add_header('Authorization',
                                                   "Bearer " + acq.hyperpay_authorization)

                                request.get_method = lambda: 'GET'
                                response = opener.open(request)

                                result.append(json.loads(response.read()))

                                print('reslut',result)
                                result3=[]
                                result3= result[0].get('result',{})
                                resp2 =result3.get('code', {})
                                print('resp2',resp2)
                                if(resp2=="000.000.000"):
                                    order.sudo().action_confirm()
                                    order.res_partner.sudo().write({"last_order":None})

                                    print('transaction pending')
                            except HTTPError as e:
                                print( "heelo")

        print(count,'count')
        # print('tx',len(tx))
        # for t in tx:
        #
        #     if t.hyperpay_checkout_id:
        #         acq = t.acquirer_id
        #         url = "https://oppwa.com/v1/checkouts/"+t.hyperpay_checkout_id+"/payment"
        #         url += '?entityId='+acq.hyperpay_merchant_id
        #         try:
        #             opener = build_opener(HTTPHandler)
        #             request2 = Request(url, data=b'')
        #             request2.add_header('Authorization',
        #                                "Bearer " + acq.hyperpay_authorization)
        #             request2.get_method = lambda: 'GET'
        #             response = opener.open(request2)
        #             result.append(json.loads(response.read()))
        #             resp2 = result.get('code', {})
        #             print('resp2',resp2)
        #         except HTTPError as e:
        #             print( "")










    def get_zip_category(self):
        for order in self:
            if(order.zip):
                zip_code=self.env['zip.code'].sudo().search([('zip','=',order.zip)],limit=1)
                if(len(zip_code)>0):
                    self.zip_category=zip_code.zip_category.id
                else:
                    self.zip_category = None
            else:
                self.zip_category = None
    def def_customer_state(self):
        for order in self:
            if(order.state=='draft' or order.state=='sent' or order.state=='sale'    ):
                order.customer_state = 'accepted'
                order.font = '#F2B544'
                order.background = '#FDF3E1'
            elif((order.state=='processing' or order.state=='verification' or order.state=='ready' or order.state=='transit') and order.delivery_method.pickup!=True  ):
                order.customer_state = 'processed'
                order.font = '#F04A4A'
                order.background = '#FDE2E2'
            elif (order.state == 'delivery' ):
                order.customer_state = 'delivery'
                order.font = '#18345C'
                order.background = '#FFD9C7'
            elif (order.state == 'ready' and order.delivery_method.pickup==True ):
                order.customer_state = 'delivery'
                order.font = '#18345C'
                order.background = '#FFD9C7'
            else:
                order.customer_state = 'delivered'
                order.font = '#56C596'
                order.background ='#E4F6EE'
    # @api.multi
    @api.depends('order_line.product_uom_qty', 'order_line.product_id')
    def _compute_cart_count(self):
        is_wesiteSaleDelivery = self.env['mobikul'].sudo(
        ).check_mobikul_addons().get('website_sale_delivery')
        for order in self:
            if is_wesiteSaleDelivery:
                order.cart_count = int(
                    sum([line.product_uom_qty for line in order.order_line if not line.is_delivery]))
            else:
                order.cart_count = int(sum(order.mapped('order_line.product_uom_qty')))


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    is_mobikul_available = fields.Boolean(
        'Visible in Mobikul', copy=False,
        help="Make this payment acquirer available on App")
    mobikul_reference_code = fields.Char(
        'Mobikul Reference Code', copy=False,
        help="Unique Code in order to integrate it with Mobikul App.")
    mobikul_pre_msg = fields.Text('Message to Display', copy=False,
                                  translate=True, help="this field is depricated from mobikul")
    mobikul_extra_key = fields.Char('Extra Keys', copy=False)
class SaleOrderDashboard(models.Model):
    _name = "sale.order.schedule.dashboard"

    def get_delivery_schedule(self):
        for order in self:
            # now = datetime.now()
            # current_time = now.strftime("%H:%M")
            # floattime=current_time.hour + current_time.minute / 60.0
            tz = pytz.timezone('Asia/Riyadh')
            now = datetime.now(tz=tz)
            tz = pytz.timezone('Asia/Riyadh')
            now = datetime.now(tz=tz)
            current_time = now.strftime("%H:%M")
            today = datetime.now(tz=tz)


            daysArbic = {'Saturday': 'السبت', 'Sunday': 'الأحد', 'Monday': 'الاثنين', 'Tuesday': 'الثلاثاء',
                         'Wednesday': 'الاربعاء', 'Thursday': 'الخميس', 'Friday': 'الجمعة', }

            today_name = today.strftime("%A")


            floattime = now.hour + now.minute / 60.0
            delivery_schedule_now=[]
            if(today_name=="Friday"):
                delivery_schedule_now = self.env['delivery.schedule'].sudo().search(['&','&',('start_time', '<=', floattime),('end_time', '>', floattime),('hide_on_friday','!=',1)],limit=1)
            if (today_name == "Saturday"):
                delivery_schedule_now = self.env['delivery.schedule'].sudo().search(
                    ['&', '&', ('start_time', '<=', floattime), ('end_time', '>', floattime),
                     ('hide_on_saturday', '!=', 1)], limit=1)
            if (today_name == "Sunday"):
                delivery_schedule_now = self.env['delivery.schedule'].sudo().search(
                    ['&', '&', ('start_time', '<=', floattime), ('end_time', '>', floattime),
                     ('hide_on_sunday', '!=', 1)], limit=1)
            if (today_name == "Monday"):
                delivery_schedule_now = self.env['delivery.schedule'].sudo().search(
                    ['&', '&', ('start_time', '<=', floattime), ('end_time', '>', floattime),
                     ('hide_on_monday', '!=', 1)], limit=1)
            if (today_name == "Tuesday"):
                delivery_schedule_now = self.env['delivery.schedule'].sudo().search(
                    ['&', '&', ('start_time', '<=', floattime), ('end_time', '>', floattime),
                     ('hide_on_tuesday', '!=', 1)], limit=1)
            if (today_name == "Wednesday"):
                delivery_schedule_now = self.env['delivery.schedule'].sudo().search(
                    ['&', '&', ('start_time', '<=', floattime), ('end_time', '>', floattime),
                     ('hide_on_wednesday', '!=', 1)], limit=1)
            if (today_name == "Thursday"):
                delivery_schedule_now = self.env['delivery.schedule'].sudo().search(
                    ['&', '&', ('start_time', '<=', floattime), ('end_time', '>', floattime),
                     ('hide_on_thursday', '!=', 1)], limit=1)
            print('delivery_schedule_now',len(delivery_schedule_now))
            if(delivery_schedule_now):
                order.delivery_schedule1 = delivery_schedule_now.id
                next_delivery_schedule = self.env['delivery.schedule'].sudo().search([('start_time', '=',  delivery_schedule_now.end_time)],limit=1)
                if(next_delivery_schedule):
                    self.delivery_schedule2 = next_delivery_schedule.id
                else:
                    self.delivery_schedule2 = 1
                pevious_delivery_schedule = self.env['delivery.schedule'].sudo().search([('end_time', '=',  delivery_schedule_now.start_time)],limit=1)
                if(pevious_delivery_schedule):
                    self.delivery_schedule3 = pevious_delivery_schedule.id
                else:
                    self.delivery_schedule3=1


            else:
                self.delivery_schedule1 = 1
                self.delivery_schedule2 = 1
                self.delivery_schedule3 = 1





    def _get_count(self):
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        #now = datetime.datetime.now(tz=tz)


        sale_count = self.env['sale.order'].search(
            ['&','&',('state', '=', 'sale'),('delivery_schedule','=',self.delivery_schedule1.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        processing_count = self.env['sale.order'].search(
            ['&','&',('state', '=', 'processing'),('delivery_schedule','=',self.delivery_schedule1.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        verification_count = self.env['sale.order'].search(
            ['&','&',('state', '=', 'verification'),('delivery_schedule','=',self.delivery_schedule1.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        ready_count = self.env['sale.order'].search(
            ['&','&',('state', '=', 'ready'),('delivery_schedule','=',self.delivery_schedule1.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        transit_count = self.env['sale.order'].search(
            ['&','&',('state', '=', 'transit'),('delivery_schedule','=',self.delivery_schedule1.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        delivery_count = self.env['sale.order'].search(
            ['&','&',('state', '=', 'delivery'),('delivery_schedule','=',self.delivery_schedule1.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        done_count= self.env['sale.order'].search(
            ['&','&',('state', '=', 'done'),('delivery_schedule','=',self.delivery_schedule1.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        total_count = self.env['sale.order'].search(
            ['&', ('delivery_schedule', '=', self.delivery_schedule1.id),
             ('shipping_time', '=', now.strftime('%Y-%m-%d'))])

        sale_count2 = self.env['sale.order'].search(
            ['&','&',('state', '=', 'sale'), ('delivery_schedule', '=', self.delivery_schedule2.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        processing_count2 = self.env['sale.order'].search(
            ['&','&',('state', '=', 'processing'), ('delivery_schedule', '=', self.delivery_schedule2.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        verification_count2 = self.env['sale.order'].search(
            ['&','&',('state', '=', 'verification'), ('delivery_schedule', '=', self.delivery_schedule2.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        ready_count2 = self.env['sale.order'].search(
            ['&','&',('state', '=', 'ready'), ('delivery_schedule', '=', self.delivery_schedule2.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        transit_count2 = self.env['sale.order'].search(
            ['&','&',('state', '=', 'transit'), ('delivery_schedule', '=', self.delivery_schedule2.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        delivery_count2 = self.env['sale.order'].search(
            ['&','&',('state', '=', 'delivery'), ('delivery_schedule', '=', self.delivery_schedule2.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        done_count2 = self.env['sale.order'].search(
            ['&', '&', ('state', '=', 'done'), ('delivery_schedule', '=', self.delivery_schedule2.id),
             ('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        total_count2 = self.env['sale.order'].search(
            ['&', ('delivery_schedule', '=', self.delivery_schedule2.id),
             ('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        sale_count3 = self.env['sale.order'].search(
            ['&','&',('state', '=', 'sale'), ('delivery_schedule', '=', self.delivery_schedule3.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        processing_count3 = self.env['sale.order'].search(
            ['&','&',('state', '=', 'processing'), ('delivery_schedule', '=', self.delivery_schedule3.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        verification_count3 = self.env['sale.order'].search(
            ['&','&',('state', '=', 'verification'), ('delivery_schedule', '=', self.delivery_schedule3.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        ready_count3 = self.env['sale.order'].search(
            ['&','&',('state', '=', 'ready'), ('delivery_schedule', '=', self.delivery_schedule3.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        transit_count3 = self.env['sale.order'].search(
            ['&','&',('state', '=', 'transit'), ('delivery_schedule', '=', self.delivery_schedule3.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        delivery_count3 = self.env['sale.order'].search(
            ['&','&',('state', '=', 'delivery'), ('delivery_schedule', '=', self.delivery_schedule3.id),('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        done_count3 = self.env['sale.order'].search(
            ['&', '&', ('state', '=', 'done'), ('delivery_schedule', '=', self.delivery_schedule3.id),
             ('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        total_count3 = self.env['sale.order'].search(
            ['&', ('delivery_schedule', '=', self.delivery_schedule3.id),
             ('shipping_time', '=', now.strftime('%Y-%m-%d'))])
        self.sale_count_schedule1 = len(sale_count)
        self.processing_count_schedule1 = len(processing_count)
        self.verification_count_schedule1 = len(verification_count)
        self.ready_count_schedule1 = len(ready_count)
        self.transit_count_schedule1 = len(transit_count)
        self.delivery_count_schedule1 = len(delivery_count)
        self.done_count_schedule1 = len(done_count)
        self.total_count_schedule1 = len(total_count)

        self.sale_count_schedule2 = len(sale_count2)
        self.processing_count_schedule2 = len(processing_count2)
        self.verification_count_schedule2 = len(verification_count2)
        self.ready_count_schedule2 = len(ready_count2)
        self.transit_count_schedule2 = len(transit_count2)
        self.delivery_count_schedule2 = len(delivery_count2)
        self.done_count_schedule2 = len(done_count2)
        self.total_count_schedule2 = len(total_count2)

        self.sale_count_schedule3 = len(sale_count3)
        self.processing_count_schedule3 = len(processing_count3)
        self.verification_count_schedule3 = len(verification_count3)
        self.ready_count_schedule3 = len(ready_count3)
        self.transit_count_schedule3 = len(transit_count3)
        self.delivery_count_schedule3 = len(delivery_count3)
        self.done_count_schedule3 = len(done_count3)
        self.total_count_schedule3 = len(total_count3)


    def to_confirmed(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.sale_count_schedule1>0):
            action['domain'] = ['&', '&', ('state', '=', 'sale'), ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule1.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def to_processing(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.processing_count_schedule1>0):
            action['domain'] = ['&', '&', ('state', '=', 'processing'),
                                ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule1.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    def to_verification(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.verification_count_schedule1>0):
            action['domain'] = ['&', '&', ('state', '=', 'verification'),
                                ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule1.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    def to_ready(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.ready_count_schedule1>0):
            action['domain'] = ['&', '&', ('state', '=', 'ready'),
                                ('delivery_schedule', '=', self.delivery_schedule1.id),
                                ('shipping_time', '=', now.strftime('%Y-%m-%d'))]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def to_transit(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.transit_count_schedule1>0):
            action['domain'] = ['&', '&', ('state', '=', 'transit'), ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule1.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    def to_delivery(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.delivery_count_schedule1>0):
            action['domain'] = ['&', '&', ('state', '=', 'delivery'), ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule1.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def to_confirmed2(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.sale_count_schedule2>0):
            action['domain'] = ['&', '&', ('state', '=', 'sale'), ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule2.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def to_processing2(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.processing_count_schedule2>0):
            action['domain'] = ['&', '&', ('state', '=', 'processing'),
                                ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule2.id)]
        else:
            action = {'type': 'ir.actions.act_window_close'}

        action['name'] = action2.name
        return action
    def to_verification2(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.verification_count_schedule2>0):
            action['domain'] = ['&', '&', ('state', '=', 'verification'),
                                ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule2.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    def to_ready2(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.ready_count_schedule2>0):
            action['domain'] = [('state', '=', 'ready'), ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule2.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def to_transit2(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.transit_count_schedule2>0):
            action['domain'] = ['&', '&', ('state', '=', 'transit'), ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule2.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action
    def to_delivery2(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.delivery_count_schedule2>0):
            action['domain'] = ['&', '&', ('state', '=', 'delivery'), ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule2.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def to_confirmed3(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.sale_count_schedule3>0):
            action['domain'] = ['&', '&', ('state', '=', 'sale'), ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule3.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def to_processing3(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.processing_count_schedule3>0):
            action['domain'] = ['&', '&', ('state', '=', 'processing'),
                                ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule3.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    def to_verification3(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.verification_count_schedule3>0):
            action['domain'] = ['&', '&', ('state', '=', 'verification'),
                                ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule3.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    def to_ready3(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.ready_count_schedule3>0):
            action['domain'] = ['&', '&', ('state', '=', 'ready'), ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule3.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action

    def to_transit3(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)
        if(self.transit_count_schedule3>0):
            action['domain'] = ['&', '&', ('state', '=', 'transit'), ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule3.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    def to_delivery3(self):
        inv_obj = self.env['sale.order']
        imd = self.env['ir.model.data']
        action2 = imd.xmlid_to_object('sale.action_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(tz=tz)

        if(self.delivery_count_schedule3>0):
            action['domain'] = ['&', '&', ('state', '=', 'delivery'), ('shipping_time', '=', now.strftime('%Y-%m-%d')),
                                ('delivery_schedule', '=', self.delivery_schedule3.id)]
            action['name'] = action2.name
        else:
            action = {'type': 'ir.actions.act_window_close'}





        return action

    # @api.multi
    # def foo():
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_view_reload',
    #     }

    color = fields.Integer(string='Color Index')
    name = fields.Char(string="Name")
    sale_count_schedule1 = fields.Integer(compute='_get_count')
    processing_count_schedule1 = fields.Integer(compute='_get_count')
    verification_count_schedule1 = fields.Integer(compute='_get_count')
    ready_count_schedule1 = fields.Integer(compute='_get_count')
    transit_count_schedule1 = fields.Integer(compute='_get_count')
    delivery_count_schedule1 = fields.Integer(compute='_get_count')
    done_count_schedule1 = fields.Integer(string='Done count',compute='_get_count')
    total_count_schedule1 = fields.Integer(compute='_get_count')

    sale_count_schedule2 = fields.Integer(compute='_get_count')
    processing_count_schedule2 = fields.Integer(compute='_get_count')
    verification_count_schedule2 = fields.Integer(compute='_get_count')
    ready_count_schedule2 = fields.Integer(compute='_get_count')
    transit_count_schedule2 = fields.Integer(compute='_get_count')
    delivery_count_schedule2 = fields.Integer(compute='_get_count')
    done_count_schedule2 = fields.Integer(string='Done count', compute='_get_count')
    total_count_schedule2= fields.Integer(compute='_get_count')

    sale_count_schedule3 = fields.Integer(compute='_get_count')
    processing_count_schedule3 = fields.Integer(compute='_get_count')
    verification_count_schedule3 = fields.Integer(compute='_get_count')
    ready_count_schedule3 = fields.Integer(compute='_get_count')
    transit_count_schedule3 = fields.Integer(compute='_get_count')
    delivery_count_schedule3 = fields.Integer(compute='_get_count')
    done_count_schedule3 = fields.Integer(string='Done count', compute='_get_count')
    total_count_schedule3 = fields.Integer(compute='_get_count')

    delivery_schedule1 = fields.Many2one('delivery.schedule', compute='get_delivery_schedule')
    delivery_schedule2 = fields.Many2one('delivery.schedule', compute='get_delivery_schedule')
    delivery_schedule3 = fields.Many2one('delivery.schedule', compute='get_delivery_schedule')




