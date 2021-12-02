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


class ContractContract(models.Model):
    _name = 'contract.contract'


    contract_no = fields.Char(string="Contract Number"  , required=True ,default=lambda self: _('New') ,readonly=True) 
    date = fields.Date("Date" ,default=fields.Datetime.now,)
    school = fields.Many2one('res.company', string='School', default=lambda self: self.env.company)
    canteen = fields.Many2one('pos.config', string='Canteen')
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    num_of_students = fields.Integer(string='Number of students')
    num_of_months = fields.Integer(string='Months rental')
    contract_type = fields.Selection([('inside_platform', 'From inside the platform'),('outside_platform', 'From outside the platform')],string="Contract Type")
    student_rental_price = fields.Float(string='Student Rental Price')
    calculation_method = fields.Selection([('fixed', 'Fixed Price'),('pers_rent', 'Percentage on the total rent'),('pers_transactions', 'Percentage on transactions'),('fee', 'Fee per transaction')],string="Platform calculation method")
    education_ratio = fields.Float(string='Education Fund Ratio')
    attachment_id = fields.Many2one('ir.attachment', string="Attachment")

    state = fields.Selection([('draft', 'Draft'),('confirmed', 'Confirmed'),('approved', 'Approved')],string="State", default='draft')


    monthly_rent = fields.Float(string='Total monthly rent')
    annual_rent = fields.Float(string='Total annual rent')
    education_fund_ratio = fields.Float(string='Total Education Fund Ratio')
    tax = fields.Float(string='value added tax')
    the_monthly_rent  = fields.Float(string='The monthly rent')

    @api.model
    def create(self, vals):
          vals['contract_no'] = self.env['ir.sequence'].next_by_code('contract.contract') or _('New')
          return super(ContractContract, self).create(vals)


    def action_confirm(self):
        self.monthly_rent = self.student_rental_price * self.num_of_students
        self.annual_rent = self.monthly_rent * self.num_of_months
        self.education_fund_ratio = (self.annual_rent * self.education_ratio)/100
        self.state='confirmed'
        return True
    def action_approve(self):
        self.state='approved'
        return True



    @api.onchange('school')
    def _onchange_school(self):
        self.num_of_students = self.school.student_count


    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date:
            date = datetime.strptime(str(self.start_date), DEFAULT_SERVER_DATE_FORMAT)
            start_date = date.replace(month=1, day=1)    
            end_date = date.replace(month=12, day=31)
            lines = self.env['school.calendar'].search_read([('date_start', '>=', start_date),('date_start', '<=', end_date),('school_id', '=', self.school.id)],['date_start'])
            date_list = [line['date_start'] for line in lines if 'date_start' in line]
            min_date = min(date_list)
            max_date = max(date_list)
            diff = ((max_date.year - min_date.year) * 12 + (max_date.month  - min_date.month )) + 1
            if max_date.month != 12 :
                self.end_date =  date.replace(month=max_date.month + 1, day=1) 
            else :
                self.end_date =  date.replace( year= max_date.year + 1 ,month=1 , day=1) 
            self.num_of_months = diff

