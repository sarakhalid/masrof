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
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
from odoo import api, fields, models, _, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):

    _inherit = 'res.partner'
    
    # @api.constrains('phone')
    # def check_duplicate_phone(self):
    #      for record in self:
    #         if record.phone:
    #             user_id = self.env['res.partner'].search([('phone','=',record.phone)])
    #             if user_id and len(user_id) >1:
    #                 raise ValidationError(_('Phone number already exist'))
    #

class ResUsers(models.Model):

    _inherit = 'res.users'
    
    
    @api.constrains('phone')
    def check_duplicate_phone(self):
         for record in self:  
             if record.phone: 
                user_id = self.env['res.users'].search([('phone','=',record.phone)])
                if user_id and len(user_id) >1:
                    raise ValidationError(_('Phone number already exist'))
    
    

    otp = fields.Char(string="Otp")
    
    
    @classmethod
    def _login(cls, db, login, password):
        if not password:
            return False
        user_id = False
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                user = self.search([('login', '=', login)])
                if user:
                    user_id = user.id
                    self.env.cr.execute(
                        "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
                        [user_id]
                    )
                    hashed = self.env.cr.fetchone()[0]
                    # if not password == hashed+'mobile_otp_login':
                    #     user.sudo(user_id).check_credentials(password)
                    user.sudo(user_id)._update_last_login()
        except AccessDenied:
            user_id = False

        status = "successful" if user_id else "failed"
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        _logger.info("Login %s for db:%s login:%s from %s", status, db, login, ip)

        return user_id
    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: