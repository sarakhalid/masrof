from odoo import api, fields, models, _
from odoo.exceptions import Warning,UserError
from odoo.http import request


class website_ewallet(models.Model):
    _name = 'website.ewallet'


    name = fields.Char(string='Name')
    website_tag= fields.Selection([
        ('redemption', 'Redemption'),
        ('cancel_fees', 'Cancellation Fees'),('cancel_amount', 'Cancelled Wallet Amount')], string='Website Debit Tag', required=True, default='redemption')
    show_transactions = fields.Boolean(string ='Show Transactions')
    active = fields.Boolean(string ='active')
    image = fields.Binary(string='Wallet Image')

  



class transaction_tags(models.Model):
    _name = 'transaction.tags'


    name = fields.Char(string='Name')
    tag_type = fields.Selection([
        ('credit', 'Credit'),
        ('debit', 'Debit')], string='Type', required=True, default='credit')
    active = fields.Boolean(string ='active',default=True)


class res_partner(models.Model):
    _inherit = 'res.partner'



    @api.depends('transactions_ids')
    def _compute_transactions_ids(self):
        self.transactions_count = self.wallet_amount


    def action_view_transactions(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''


        action = self.env.ref('ways_wallet.action_ways_transactions').read()[0]


        transactions = self.mapped('transactions_ids')
        if len(transactions) > 1:
            action['domain'] = [('id', 'in', transactions.ids)]
        elif transactions:
            form_view = [(self.env.ref('ways_wallet.view_ways_transactions_form').id, 'form')]
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




    transactions_ids = fields.One2many('ways.transactions', 'partner_id', string='Transfers')
    transactions_count = fields.Integer(string='Transactions', compute='_compute_transactions_ids')
    wallet_amount = fields.Float(string='E-Wallet Amount')
    
    
    
class product_product(models.Model):
    _inherit = 'product.product'
    
    is_wallet = fields.Boolean(string="is wallet")



class wallet_reference(models.Model):
    _name = 'wallet.reference'

    name = fields.Char(string='Name', required=True)
    from_sale = fields.Boolean(string='From Sale', default=False)
