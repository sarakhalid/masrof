from odoo import api, fields, models, _
from odoo.exceptions import Warning,UserError
from odoo.http import request


class ways_transactions(models.Model):
    _name = 'ways.transactions'






    transaction_id = fields.Char(string='Transaction id', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    transaction_date = fields.Datetime(string='Transaction Date', required=True, index=True, default=fields.Datetime.now)
    ewallet_id = fields.Many2one('payment.acquirer', string='E-Wallet',domain="[('is_wallet','=',True)]")
    partner_id = fields.Many2one('res.partner', string='Customer', required=True,)
    transaction_type = fields.Selection([
        ('credit', 'Credit'),
        ('debit', 'Debit')], string='Type', required=True, default='credit')
    transaction_tags = fields.Many2many('transaction.tags', string='Tag',domain="[('active', '=', True), ('tag_type', '=', transaction_type)]")
    reference = fields.Many2one('wallet.reference', string='Reference') 
    amount = fields.Float(string='E-Wallet Amount')
    currency_id = fields.Many2one("res.currency",  string="Currency", required=True)
    amount_total = fields.Float(string='Total Converted Amount',readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal')
    account_id = fields.Many2one('account.account', string='Account Journal')
    record = fields.Char(string='Record')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')
    sale_order = fields.Many2one('sale.order' , string='Sale Order')


    @api.model
    def create(self, vals):
          vals['transaction_id'] = self.env['ir.sequence'].next_by_code('ways.transactions') or _('New')
          return super(ways_transactions, self).create(vals)



    def action_confirm(self):
        amount = self.partner_id.wallet_amount
        if self.transaction_type == 'credit':
            amount += self.amount
        if self.transaction_type == 'debit':
            amount -= self.amount   
        
        self.amount_total = amount
        self.partner_id.wallet_amount =amount
        self.state='done'
        return True
        
        
    def _compute_access_url(self):
        super(ways_transactions, self)._compute_access_url()
        for transaction in self.filtered(lambda transaction: transaction.is_transaction()):
            transaction.access_url = '/my/transactions/%s' % (transaction.id)
 
  
    def is_transaction(self, include_receipts=False):
        return True





