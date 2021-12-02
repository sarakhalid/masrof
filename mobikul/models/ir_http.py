# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################

from odoo import api, models
from odoo import SUPERUSER_ID
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    rerouting_limit = 10
    _geoip_resolver = None

    # @classmethod
    def binary_content(self, xmlid=None, model='ir.attachment', id=None, field='datas',
        unique=False, filename=None, filename_field='datas_fname', download=False,
        mimetype=None, default_mimetype='application/octet-stream',
        access_token=None):
        env = request.env
        obj = None
        if xmlid:
            obj = env.ref(xmlid, False)
        elif id and model in env:
            obj = env[model].browse(int(id))
        if obj and 'is_mobikul_available' in obj._fields:
            if env[obj._name].sudo().search([('id', '=', obj.id), ('is_mobikul_available', '=', True)]):
                self = self.sudo()
        if obj and obj._name == "res.partner" and field in ("image_1920", "profile_banner", "profile_image", "banner_image"):
            self = self.sudo()
        return super(Http, self).binary_content(
        xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
        filename_field=filename_field, download=download, mimetype=mimetype,
        default_mimetype=default_mimetype, access_token=access_token)
