# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number
from odoo.tools import remove_accents
import logging
import re


class EducationAdministration(models.Model):
    _name = 'education.administration'
 

    name = fields.Char(string="Name"  , required=True) 
    ministerial_number = fields.Char(string="Ministerial number"  ) 
    phone = fields.Char(string="Phone" ) 
    manager_id = fields.Many2one('res.users', string='Manager',domain=[('partner_type','=','education_manager')])
    services_manage_id = fields.Many2one('res.users', string='Student Services Manager ',domain=[('partner_type','=','s_advisor')])
    school_ids = fields.One2many('res.company','education_id', string='school')
    office_ids = fields.One2many('office.office', 'education_id', string='office')




class OfficeOffice(models.Model):
    _name = 'office.office'
 

    name = fields.Char(string="Name"  , required=True) 

    education_id = fields.Many2one('education.administration', string='education_id')

