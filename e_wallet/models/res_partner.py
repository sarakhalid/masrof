# -*- coding: utf
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _rec_name = 'full_name'





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
        if len(transactions) == 0:
            action['domain'] = [('id', '=', 0)]
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
            if transactions:
                picking_id = transactions[0]
            else :
                picking_id =[]


        return action





    @api.depends('name','second_name','third_name','fourth_name')
    def comp_name(self):
        for record in self:        
            if record.responsable_rank or record.student_rank :
                record.full_name = (record.name or '')+' '+(record.second_name or '')+' '+(record.third_name or '')+' '+(record.fourth_name or '')
            else :
                record.full_name = record.name

    full_name = fields.Char(compute='comp_name', store=True)
    second_name = fields.Char(string='Second Name')
    third_name = fields.Char(string='Third Name'  )
    fourth_name = fields.Char(string='Fourth Name' )
    responsable_rank = fields.Boolean(default=False)
    student_rank = fields.Boolean(default=False)
    identification = fields.Char(string='Identification Number'  )
    birthday = fields.Date(string='Birth Day'  )
    birthday2 = fields.Date(string='Birth Day2'  )
    

    responsible = fields.Many2one('res.partner', string='Responsible',domain=[('responsable_rank','=', True)])
    school_id = fields.Many2one('res.company', string='School')
    school_type = fields.Many2one('school.type', string='Educational level')
    class_room = fields.Many2one('class.room', string='Class room')
    in_wallet = fields.Boolean(string='This student added to wallet '  )
    needy = fields.Boolean(string='This student needy'  )
    password = fields.Char(string='Password' )
    rand_token = fields.Char(string='Rand token' ,store=True)


    transactions_ids = fields.One2many('wallet.transactions','responsable', string='Transfers')
    transactions_count = fields.Integer(string='Total Amount', compute='_compute_transactions_ids')

	

    @api.model_create_multi
    def create(self, vals_list):
        search_partner_mode = self.env.context.get('res_partner_search_mode')
        is_responsable = search_partner_mode == 'responsable'
        if search_partner_mode:
            for vals in vals_list:
                if is_responsable and 'responsable_rank' not in vals:
                    vals['responsable_rank'] = True

        is_responsable = search_partner_mode == 'student'
        if search_partner_mode:
            for vals in vals_list:
                if  'student_rank' not in vals:
                    vals['student_rank'] = True
        #name = vals_list['first_name']+" "+vals_list['second_name']+" "+vals_list['third_name']+" "+vals_list['fourth_name']
       # vals['name'] =name
        return super().create(vals_list)



    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        partner = self
        name = partner.full_name or ''

        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
            if not partner.is_company:
                name = self._get_contact_name(partner, name)
        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')
        if self._context.get('address_inline'):
            name = name.replace('\n', ', ')
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)
        return name


class ResUsers(models.Model):
    _inherit = 'res.users'

    partner_type = fields.Selection([('s_manager', 'Schools managers'), ('education_manager', 'Director of Education Department'),('s_advisor', 'Student advisor'), ('fund_officer', 'Fund Officer'),('contractor', 'contractors'), ], string="Type")
    education_administration = fields.Many2one('education.administration', string='Education Administration')
    Bank_account_number = fields.Char(string='Bank account number' )


    def add_wallet(self):
        print ("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG ")


