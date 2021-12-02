# -*- coding: utf-8 -*-
#################################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
#################################################################################
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)


class WebsiteSaleInherit(WebsiteSale):

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        partner = request.env.user.partner_id
        partner.last_website_so_id = False
        return super(WebsiteSaleInherit, self).payment_confirmation(**post)
