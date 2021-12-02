# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 seeroo IT SOLUTIONS PVT.LTD(<http://www.seeroo.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name' : 'OTP Login',
    'version' : '1.0.00',
    'summary': 'Module for otp login.',
    'description': "OTP LOGIN",
    'category': 'Base',
    'depends' : ['base_setup','auth_signup','website'],
    'images': [
        'static/description/banner.jpg',
        ],
    # 'data': [
    #
    #
    #     'views/res_company_view.xml',
    #     'views/general_settings_view.xml',
    #     'views/otp.xml',
    #
    # ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'author': 'Seeroo IT Solutions',
    'website': 'https://www.seeroo.com',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: