# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number
from odoo.tools import remove_accents
import logging
import re


class wallet_feeding (models.Model):
    _name = 'wallet.feeding'

    wallet = fields.Many2one('e.wallet', string='Wallet')
    amount = fields.Float(string='Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')

    def action_confirm(self):
        new_transaction = self.env['wallet.transactions'].create({
	    'wallet': self.wallet.id,

	    'amount': self.amount,
	    'transaction_type':'credit',
	  #  'currency_id':self.wallet.currency_id.id,
})
        new_transaction.state='done'
        self.state = 'done'



class add_student (models.Model):
    _name = 'add.student'

    wallet = fields.Many2one('e.wallet', string='Wallet',required=True)
    student = fields.Many2one('res.partner', string='Student', required=True, domain=[('student_rank','=',True),('in_wallet','=',False)])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')

    def action_confirm(self):
        self.student.in_wallet =  True
        self.student.needy =  False
        self.env['wallet.line'].create({
	    'student': self.student.id,
	    'limit': 0,
	    'wallet':self.wallet.id
})
        self.state='done'
  

        return True



class remove_student (models.Model):
    _name = 'remove.student'

    wallet = fields.Many2one('e.wallet', string='Wallet')
    student = fields.Many2one('res.partner', string='Student', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')


    @api.onchange('wallet')
    def _onchange_wallet(self):
        action = {}
        res=[]
        for line in self.wallet.line_ids:
            res.append(line.student.id)
        action['domain'] = {'student': [('id', 'in', res)]}
        return action


    def action_confirm(self):
        self.student.in_wallet =  False
        for line in self.wallet.line_ids:
            if line.student.id == self.student.id:
                line.unlink()

        self.state='done'
        return True
