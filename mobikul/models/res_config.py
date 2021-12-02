# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
import logging
_logger = logging.getLogger(__name__)


class MobikulConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _default_mobikul(self):
        return self.env['mobikul'].search([], limit=1).id

    # # @api.multi
    def open_default_user(self):
        action = self.env.ref('base.action_res_users').read()[0]
        action['context'] = self.env.context
        action['res_id'] = self.env.ref('base.default_user').id
        action['views'] = [[self.env.ref('base.view_users_form').id, 'form']]
        return action

    mobikul_app = fields.Many2one('mobikul', string="Mobikul APP",
                                  default=_default_mobikul, required=True)
    app_name = fields.Char('App Name', related='mobikul_app.name')

    # product_limit = fields.Integer('Limit Products per page', related='mobikul_app.product_limit')
    # mobikul_salesperson_id = fields.Many2one('res.users', related='mobikul_app.salesperson_id', string='Salesperson',readonly=False	)
    # mobikul_salesteam_id = fields.Many2one('crm.team', related='mobikul_app.salesteam_id', string='Sales Team',readonly=False)
    # mobikul_default_lang = fields.Many2one('res.lang', related='mobikul_app.default_lang', string='Default Language',readonly=False)
    # mobikul_currency_id = fields.Many2one('res.currency', related='mobikul_app.currency_id', string='Default Currency',readonly=False)
    # mobikul_pricelist_id = fields.Many2one('product.pricelist', related='mobikul_app.pricelist_id', string='Default Pricelist',readonly=False)

    mobikul_reset_password = fields.Boolean(
        string='Enable password reset', help="This allows users to trigger a password reset from App")
    mobikul_signup = fields.Boolean(string='Enable customer sign up')
    mobikul_allow_guest = fields.Boolean(string='Allow Guests to view products on App.')
    mobikul_signup_template_user_id = fields.Many2one(
        'res.users', string='Template user for new users created through App')
    module_auth_oauth = fields.Boolean(
        string='Allow social login (Gmail,Facebook,etc)', help="Use external authentication providers (OAuth)")
    mobikul_gmail_signin = fields.Boolean(string='Gmail SignIn')
    mobikul_facebook_signin = fields.Boolean(string='Facebook SignIn')
    mobikul_twitter_signin = fields.Boolean(string='Twitter SignIn')

    module_email_verification = fields.Boolean(
        string='Verify Email on signUp', help="Verify user email on SignUp")
    module_website_sale_wishlist = fields.Boolean(
        string='Allow Website Sale Wishlist on App.', help="Use default Addon to add Wishlist in website")
    module_website_sale_delivery = fields.Boolean(
        string='Allow Website Sale Delivery on App.', help="Use default Addon to add Website Delivery in website")
    module_wk_review = fields.Boolean(
        string='Allow Product Review feature on App.', help="Use external Addon to add review feature in website")
    module_odoo_marketplace = fields.Boolean(
        string='Allow Odoo Marketplace on App.', help="Use external Addon to add Multi Vendor Marketplace in website")

    module_odoo_gdpr = fields.Boolean(
        string='Allow Odoo GDPR on App.', help="Use default Addon to add GDPR in website")

    @api.onchange('pricelist_id')
    def onchange_currency_id_set(self):
        self.currency_id = self.pricelist_id.currency_id

    @api.onchange('mobikul_signup')
    def onchange_currency_id_set(self):
        if self.mobikul_signup:
            self.auth_signup_uninvited = "b2c"
        else:
            self.auth_signup_uninvited = "b2b"

    @api.model
    def get_values(self):
        res = super(MobikulConfigSettings, self).get_values()
        IrConfigParam = self.env['ir.config_parameter']
        # we use safe_eval on the result, since the value of the parameter is a nonempty string
        res.update(
            mobikul_reset_password=safe_eval(IrConfigParam.get_param(
                'auth_signup.reset_password', 'False')),
            mobikul_signup=safe_eval(IrConfigParam.get_param(
                'auth_signup.allow_uninvited', 'False')),
            mobikul_signup_template_user_id=safe_eval(
                IrConfigParam.get_param('auth_signup.template_user_id', 'False')),
            mobikul_allow_guest=safe_eval(IrConfigParam.get_param('mobikul.allow_guest', 'False')),
            mobikul_gmail_signin=safe_eval(
                IrConfigParam.get_param('mobikul.gmail_signin', 'False')),
            mobikul_facebook_signin=safe_eval(
                IrConfigParam.get_param('mobikul.facebook_signin', 'False')),
            mobikul_twitter_signin=safe_eval(
                IrConfigParam.get_param('mobikul.twitter_signin', 'False')),
        )
        return res

    # @api.multi
    def set_values(self):
        self.ensure_one()
        super(MobikulConfigSettings, self).set_values()
        IrConfigParam = self.env['ir.config_parameter']
        # we store the repr of the values, since the value of the parameter is a required string
        IrConfigParam.set_param('auth_signup.reset_password', repr(self.mobikul_reset_password))
        IrConfigParam.set_param('auth_signup.allow_uninvited', repr(self.mobikul_signup))
        IrConfigParam.set_param('auth_signup.template_user_id',
                                repr(self.mobikul_signup_template_user_id.id))
        IrConfigParam.set_param('mobikul.allow_guest', repr(self.mobikul_allow_guest))
        IrConfigParam.set_param('mobikul.gmail_signin', repr(self.mobikul_gmail_signin))
        IrConfigParam.set_param('mobikul.facebook_signin', repr(self.mobikul_facebook_signin))
        IrConfigParam.set_param('mobikul.twitter_signin', repr(self.mobikul_twitter_signin))

    def open_mobikul_conf(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mobikul-App Configuration',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mobikul',
            'res_id': self.mobikul_app.id,
            'target': 'current',
        }
