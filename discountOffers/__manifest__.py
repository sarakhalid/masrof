# -*- coding: utf-8 -*-
#################################################################################
{
  "name"                 :  "Discount Offers",
  "summary"              :  """Discount Offers""",
  "category"             :  "Sales",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Ingenious Information Technology ",
  "license"              :  "Other proprietary",
  "website"              :  "ingenious-technology.com",
  "description"          :  """""",
  "depends"              :  ['base','sales_team','sale'],
  "data"                 :  [
                            'security/ir.model.access.csv',
                            "views/offer_views.xml",
                             "views/menus.xml",
                             ],
  "demo"                 :  [],
  "css"                  :  [],
  "js"                   :  [],
  "images"               :  ['static/description/icon.jpeg'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "pre_init_hook"        :  "pre_init_check",
}
