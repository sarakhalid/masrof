# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Odoo Mobile App Builder ( Android & IOS )",
  "summary"              :  """This module allows you to convert your shop sales very easily with a native mobile application ( Android & IOS ).""",
  "category"             :  "Sales",
  "version"              :  "1.2.4",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/odoo-mobile-app.html",
  "description"          :  """""",
  "live_test_url"        :  "http://demo.webkul.com/web/login",
  "depends"              :  ['base','website_sale','sr_otp_login','delivery', 'payment',
                             'payment_hyperpay','stock','discountOffers',],
    #
  "data"                 :  [
                             'security/mobikul_security.xml',
                             'security/ir.model.access.csv',
                             'data/mobikul_data.xml',
                             'data/mobikul_sequence.xml',
                             'views/product_view.xml',
                             'views/order_view.xml',
                             'views/mobikul_views.xml',
                             'views/res_config_view.xml',
                             'views/menus.xml',
                             'views/sync_cat_view.xml',
                            ],
  "demo"                 :  ['data/demo_data_view.xml'],
  "css"                  :  [],
  "js"                   :  [],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  358.30,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}
