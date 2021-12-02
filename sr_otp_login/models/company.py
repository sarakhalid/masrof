# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 seeroo IT SOLUTIONS PVT.LTD(<http://www.seeroo.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, tools, _

from odoo.http import request

import base64


    
    
class ResCompany(models.Model):
    _inherit = 'res.company'
    
    use_otp_login = fields.Boolean(string="Use Otp Login")
    otp_message = fields.Text(string="Otp Message")
    otp_message_url = fields.Text(string="OTP Url")
    phone_key = fields.Char(string="Phone Key Value")
    message_key = fields.Char(string="Message Key Value")