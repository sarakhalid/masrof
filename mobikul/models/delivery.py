# from odoo import fields,api, models
#
#
# class DeliveryCarrier(models.Model):
#     _inherit = 'delivery.carrier'
#
#     # @api.multi
#     def mobikul_publish_button(self):
#         self.ensure_one()
#         self.is_mobikul_available = not self.is_mobikul_available
#         return True
#
#     is_mobikul_available = fields.Boolean(default=False)
