# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
import re
import logging

import dateutil.parser
import pytz
from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
import pprint
from odoo.fields import Datetime

_logger = logging.getLogger(__name__)


class AcquirerWallet(models.Model):
    _inherit = 'payment.acquirer'

    is_wallet = fields.Boolean(string = 'Is Wallet ?',default=False)
    website_tag= fields.Selection([
        ('redemption', 'Redemption'),
        ('cancel_fees', 'Cancellation Fees'),('cancel_amount', 'Cancelled Wallet Amount')], string='Website Debit Tag', required=True, default='redemption')
    show_transactions = fields.Boolean(string ='Show Transactions')
    image = fields.Binary(string='Wallet Image')



