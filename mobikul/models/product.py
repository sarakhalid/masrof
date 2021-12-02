# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################
from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError


import logging
_logger = logging.getLogger(__name__)

class deliverySchedule(models.Model):
	_name = 'delivery.schedule'
	name = fields.Char('Schedule',translate=True,compute='getschedulename')
	start_time = fields.Float('Start Time')
	end_time = fields.Float('End Time')
	hide_on_friday=fields.Boolean('Hide On Friday')
	hide_on_saturday = fields.Boolean('Hide On Saturday')
	hide_on_sunday = fields.Boolean('Hide On Sunday')
	hide_on_monday = fields.Boolean('Hide On Monday')
	hide_on_tuesday = fields.Boolean('Hide On Tuesday')
	hide_on_wednesday = fields.Boolean('Hide On Wednesday')
	hide_on_thursday = fields.Boolean('Hide On Thursday')


	def getschedulename(self):
		for order in self:
			result_start_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(order.start_time * 60, 60))
			result_end_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(order.end_time * 60, 60))
			order.name = result_start_time + ' - ' + result_end_time

class pickupLocation_parking(models.Model):
	_name = 'pickup.location.parking'
	name = fields.Integer('pickup location',translate=True)
	state= fields.Selection(selection=[('available','Available'),('notavailable','Not Available')],string='State',default='available')
	partner_id= fields.Many2one('res.partner',string='Customer')
	sale_order=fields.Many2one('sale.order',string='Order NO')
	stock_parking=fields.Many2one('stock.warehouse','Warehouse')


class stockWarehouse(models.Model):
	_inherit = 'stock.warehouse'
	is_pickup_available = fields.Boolean("Available on App",)
	name = fields.Char('Warehouse', index=True, required=True, default=lambda self: self.env.company.name,translate=True)
	parking=fields.One2many('pickup.location.parking','stock_parking',string='Parking')


class brand_brand(models.Model):
	_inherit = "product.brand"
	name = fields.Char( string='Brand Name',store=True,translate=True,copied=True,website_form_blacklisted=True)
	is_available=fields.Boolean("Published on App",  help="Allow the end user to choose this brand to Published on App ")






class start_end_deliverySchedule(models.Model):
	_name = 'start.end.delivery.schedule'
	start_time=fields.Float('Start Time')
	end_time = fields.Float('End Time')

	def unlink(self):
		for order in self:
			raise UserError(_('You can not delete  this data! '))
		return super(start_end_deliverySchedule, self).unlink()
class ShippingMethods(models.Model):
	_inherit = "delivery.carrier"
	pickup = fields.Boolean('Pickup')
	delivery_hour=fields.Float('Minimum delivery hour')
	minimum_order_amout=fields.Float('Minimum Order Amout')
	shift_empty = fields.Char('shift Empty')
class productproduct(models.Model):
	_inherit="product.product"
	def name_get(self):
		# TDE: this could be cleaned a bit I think

		def _name_get(d):
			name = d.get('name', '')
			uom_QTY=d.get('uom_QTY','')
			code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
			if code:
				if(uom_QTY):
					name = '[%s] %s %s' % (code, name,uom_QTY)
				else:
					name = '[%s] %s' % (code, name)
			return (d['id'], name)

		partner_id = self._context.get('partner_id')
		if partner_id:
			partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
		else:
			partner_ids = []
		company_id = self.env.context.get('company_id')

		# all user don't have access to seller and partner
		# check access and use superuser
		self.check_access_rights("read")
		self.check_access_rule("read")

		result = []

		# Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
		# Use `load=False` to not call `name_get` for the `product_tmpl_id`
		self.sudo().read(['name', 'default_code', 'product_tmpl_id'], load=False)

		product_template_ids = self.sudo().mapped('product_tmpl_id').ids

		if partner_ids:
			supplier_info = self.env['product.supplierinfo'].sudo().search([
				('product_tmpl_id', 'in', product_template_ids),
				('name', 'in', partner_ids),
			])
			# Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
			# Use `load=False` to not call `name_get` for the `product_tmpl_id` and `product_id`
			supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
			supplier_info_by_template = {}
			for r in supplier_info:
				supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
		for product in self.sudo():
			variant = product.product_template_attribute_value_ids._get_combination_name()

			name = variant and "%s (%s)" % (product.name, variant) or product.name
			sellers = []
			if partner_ids:
				product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
				sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
				if not sellers:
					sellers = [x for x in product_supplier_info if not x.product_id]
				# Filter out sellers based on the company. This is done afterwards for a better
				# code readability. At this point, only a few sellers should remain, so it should
				# not be a performance issue.
				if company_id:
					sellers = [x for x in sellers if x.company_id.id in [company_id, False]]
			if sellers:
				for s in sellers:
					seller_variant = s.product_name and (
							variant and "%s (%s)" % (s.product_name, variant) or s.product_name
					) or False
					mydict = {
						'id': product.id,
						'name': seller_variant or name,
						'default_code': s.product_code or product.default_code,
					}
					temp = _name_get(mydict)
					if temp not in result:
						result.append(temp)
			else:
				mydict = {
					'id': product.id,
					'name': name,
					'default_code': product.default_code,
					'uom_QTY':product.uom_QTY,
				}
				result.append(_name_get(mydict))
		return result
class product_product(models.Model):
	_inherit="product.product"
	uom_QTY=fields.Char('UOM QTY',translate=True)
	is_promotion=fields.Boolean('Is Promotion')

class ProductTemplate(models.Model):
	_inherit = "product.template"


	# @api.multi
	def mobikul_publish_button(self):
		self.ensure_one()
		self.is_mobikul_available = not self.is_mobikul_available
		return True

	brand_id=fields.Many2one('product.brand',string='internal brand')
	mobikul_categ_ids = fields.Many2many('mobikul.category', string='Mobikul Product Category')
	mobikul_status = fields.Selection([
	    ('empty', 'Display Nothing'),
	    ('in_stock', 'In-Stock'),
	    ('out_stock', 'Out-of-Stock'),
	], "Product Availability", default='empty', help="Adds an availability status on the mobikul product page.")
	is_mobikul_available = fields.Boolean("Published on App", default=1, help="Allow the end user to choose this price list")
	is_mobikul_available2 = fields.Boolean("Published on App", default=1, help="Allow the end user to choose this price list")
	is_mobikul_available3 = fields.Boolean("bundle on App Available")
	qty_available_bundle = fields.Float("Qty Available")

	uom_QTY=fields.Char('UOM QTY',translate=True)
	is_promotion = fields.Boolean('Is Promotion')
	def _cron_brand(self):
		order2=self.env['product.template'].search([('brand_id','!=',None)])
		for order in order2:
			if(order.brand_id == None):
				print('brand None')





class ProductPublicCategory(models.Model):
	_inherit = 'product.public.category'
	# this field is added for mobikul category merge
	mobikul_cat_id = fields.Many2one('mobikul.category', 'Mobikul Category')




class CrmTeam(models.Model):
	_inherit = "crm.team"

	mobikul_ids = fields.One2many('mobikul', 'salesteam_id', string='Mobikul', help="Mobikul is using these sales team.")

class zip_code(models.Model):
	_name='zip.code'
	name=fields.Many2one('zip.area','Area Name')
	zip=fields.Char('ZIP')
	zip_category=fields.Many2one('zip.category',string='Category')
class zip_category(models.Model):
	_name='zip.category'
	name=fields.Char('Category')
class zip_area(models.Model):
	_name='zip.area'
	name=fields.Char('Area')