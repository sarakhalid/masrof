# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number
from odoo.tools import remove_accents
import logging
import re


class e_wallet(models.Model):
    _name = 'e.wallet'
    _rec_name = 'wallet_no'


    @api.depends('transactions_ids')
    def _compute_transactions_ids(self):
        amount = 0.0
        for order in self:
            for line in order.transactions_ids:
                amount = line.amount_total
            order.transactions_count = amount


    def action_view_transactions(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''


        action = self.env.ref('e_wallet.action_wallet_transactions_form').read()[0]


        transactions = self.mapped('transactions_ids')
        if len(transactions) > 1:
            action['domain'] = [('id', 'in', transactions.ids)]
        elif transactions:
            form_view = [(self.env.ref('e_wallet.view_wallet_transactions_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = transactions.id
        # Prepare the context.
        picking_id = transactions
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = transactions[0]
        print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  picking_id = ",picking_id)

        return action




   

    wallet_no = fields.Char(string="E-Wallet Number"  , required=True ,default=lambda self: _('New') ,readonly=True) 
    responsable = fields.Many2one('res.partner', string='Wallet Owner',domain=[('responsable_rank','=',True)])
    restriction = fields.Boolean(string='Wallet Restrictions' , default=False)
    restriction_type = fields.Selection([('amount', 'Amount'),('percentage', 'Percentage')],string="Restriction Type")
    
    total_amount = fields.Float(string='Total Amount', digits=0)
    line_ids = fields.One2many('wallet.line','wallet', string='Lines')
    transactions_ids = fields.One2many('wallet.transactions','wallet', string='Transfers')
    transactions_count = fields.Integer(string='Total Amount', compute='_compute_transactions_ids')

    
 
    @api.model
    def create(self, vals):
          vals['wallet_no'] = self.env['ir.sequence'].next_by_code('e.wallet') or _('New')
          return super(e_wallet, self).create(vals)




class wallet_line(models.Model):
    _name = 'wallet.line'


    student = fields.Many2one('res.partner', string='student',required=True ,domain=[('student_rank','=',True)])
    limit = fields.Float(string='Limit in Day')  
    amount = fields.Float(string='Amount available')
    wallet = fields.Many2one('e.wallet', string='wallet')


    @api.onchange('student')
    def _onchange_student(self):
        self.limit = self.student.school_type.limit



