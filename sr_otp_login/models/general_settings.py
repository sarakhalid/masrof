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
from ast import literal_eval

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    
    module_auth_otp = fields.Boolean("Use OTP Verification", related='company_id.use_otp_login',store=True)
    otp_message = fields.Text(string="Otp Message", related='company_id.otp_message',store=True)
    otp_message_url = fields.Text(string="OTP Url", related='company_id.otp_message_url',store=True)
    phone_key = fields.Char(string="Phone Key Value", related='company_id.phone_key',store=True)
    message_key = fields.Char(string="Message Key Value", related='company_id.message_key',store=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: