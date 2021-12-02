# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number
from odoo.tools import remove_accents
import logging
import re


class wallet_transactions(models.Model):
    _name = 'wallet.transactions'


    @api.depends('amount')
    def _compute_amount_total(self):
        lines = self.env['wallet.transactions'].search([('wallet', '=', self.wallet.id),('state', '=', 'done')])
        amount = 0.0
        for line in lines:
            if line.transaction_type == 'credit':
                amount += line.amount
            if line.transaction_type == 'debit':
                amount -= line.amount            
        self.amount_total= amount




    transaction_id = fields.Char(string="Transaction Number"  , required=True ,default=lambda self: _('New') ,readonly=True) 
    transaction_date = fields.Datetime(string='Transaction Date', required=True, index=True, default=fields.Datetime.now)
    wallet = fields.Many2one('e.wallet', string='E-Wallet')
    partner_id = fields.Many2one('res.partner', string='Student', domain=[('student_rank','=',True)])
    transaction_type = fields.Selection([
        ('credit', 'Credit'),
        ('debit', 'Debit')], string='Type', required=True, default='credit')
    amount = fields.Float(string='Amount', digits=0)
    currency_id = fields.Many2one("res.currency",  string="Currency")
    amount_total = fields.Float(string='Total Converted Amount',readonly=True, compute='_compute_amount_total')
    journal_id = fields.Many2one('account.journal', string='Journal')
    account_id = fields.Many2one('account.account', string='Account Journal')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')

    pos_order = fields.Char( string='Pos Reference')
    responsable = fields.Many2one('res.partner', string='responsable')
 
    @api.model
    def create(self, vals):
          vals['transaction_id'] = self.env['ir.sequence'].next_by_code('wallet.transactions') or _('New')
          return super(wallet_transactions, self).create(vals)




    @api.onchange('wallet')
    def _onchange_wallet(self):
        self.responsable = self.wallet.responsable.id



    def action_confirm(self):
        self.state='done'
        return True
