# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number
from odoo.tools import remove_accents
import logging
import re
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime


class PlatformPlatform(models.Model):
    _name = 'platform.platform'


    name = fields.Char(string="Platform Name"  , required=True ) 
    owner  = fields.Many2one("res.users", string="Owner"  , required=True ) 
    id_number = fields.Char(string="the ID number"  , required=True ) 
    commercial_register = fields.Char(string="Commercial Register"  , required=True ) 
    account_id  = fields.Many2one("account.account", string="Account"  , required=True ) 
    date = fields.Date("Date created")

    
