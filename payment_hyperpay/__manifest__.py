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
  "name"                 :  "Hyperpay Payment Acquirer",
  "summary"              :  """Website Hyper Pay Payment Acquirer""",
  "category"             :  "Website",
  "version"              :  "1.2.2",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Anuj Kumar Chhetri",
  "website"              :  "https://store.webkul.com/odoo-hyperpay-payment-acquirer.html",
  "description"          :  """Odoo Hyperpay Payment Gateway
Payment Gateway
Hyperpay
hyper pay
payment methods
website payment method
Hyperpay integration
Payment acquirer
Payment processing
Payment processor
Website payments
Sale orders payment
Customer payment
Integrate hyperpay payment acquirer in Odoo
Integrate hyperpay payment gateway in Odoo""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=payment_hyperpay",
  "depends"              :  [
                             'payment',
                             'website_sale',
                            ],
  "data"                 :  [
                             'views/payment_views.xml',
                             'views/payment_hyperpay_templates.xml',
                             'views/website_assets.xml',
                             'data/payment_acquirer_data.xml',
                            ],
  "demo"                 :  [],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  99.0,
  "currency"             :  "USD",
  "post_init_hook"       :  "create_missing_journal_for_acquirers",
}
