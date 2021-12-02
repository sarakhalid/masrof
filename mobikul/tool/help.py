# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################
import random
import string
import re
from odoo import fields
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


def _changePricelist(pricelist_id):
    return{
        'currencySymbol': " "+pricelist_id.currency_id.symbol or "",
        'currencyPosition': pricelist_id.currency_id.position or "",
    }


def _displayWithCurrency(lang_obj, amount, symbol, position):
    fmt = "%.{0}f".format(2)  # currency.decimal_places
    formatted_amount = lang_obj.format(
        fmt, amount, grouping=True, monetary=True)  # currency.round(amount)
    return " %s%s" % (symbol, formatted_amount) if position == "before" else "%s%s" % (formatted_amount, symbol)


def _lang_get(cls):
    return cls.env['res.lang'].get_installed()


def _default_unique_key(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def _get_image_url(base_url, model_name, record_id, field_name, write_date=0, width=0, height=0):
    """ Returns a local url that points to the image field of a given browse record. """
    if base_url and not base_url.endswith("/"):
        base_url = base_url+"/"
    if width or height:
        return '%sweb/image/%s/%s/%s/%sx%s?unique=%s' % (base_url, model_name, record_id, field_name, width, height, re.sub('[^\d]', '', fields.Datetime.to_string(write_date)))
    else:
        return '%sweb/image/%s/%s/%s?unique=%s' % (base_url, model_name, record_id, field_name, re.sub('[^\d]', '', fields.Datetime.to_string(write_date)))


def _getProductData(p_data, context={}):
    base_url = context.get("base_url")
    currency_symbol = context.get("currencySymbol")
    currency_position = context.get("currencyPosition")
    lang_obj = context.get("lang_obj")
    pricelist = context.get("pricelist", False)
    result = []
    Mobikul = context.get("mobikul_obj")
    for prod in p_data:
        qty_available=0.0

        if(Mobikul.available_in_stock):
            if(prod.sh_is_bundle==True):
                if (prod.is_mobikul_available3 == True):
                    comb_info = prod.with_context(**context)._get_combination_info(combination=False, product_id=False,
                                                                                   add_qty=1, pricelist=pricelist,
                                                                                   parent_combination=False,
                                                                                   only_template=False)
                    qty_available=prod.qty_available_bundle
                    result.append({
                        'templateId': prod.id or '',
                        'name': prod.name or '',
                        # 'priceUnit': _displayWithCurrency(lang_obj, comb_info['has_discounted_price'] and comb_info['list_price'] or
                        #                                   comb_info['price'] or 0, ' ', currency_symbol, currency_position),

                        'priceUnit': _displayWithCurrency(lang_obj, prod.list_price or 0, currency_symbol,
                                                          currency_position),
                        # 'priceReduce': comb_info['has_discounted_price'] and _displayWithCurrency(lang_obj,
                        #                                                                           comb_info[
                        #                                                                               'price'] or 0,
                        #                                                                           currency_symbol,
                        #                                                                           currency_position) or "",
                        'priceReduce':  _displayWithCurrency(lang_obj, prod.list_price or 0, currency_symbol,
                                                          currency_position),
                        'productId': prod.product_variant_id and prod.product_variant_id.id or '',
                        'productCount': prod.product_variant_count or 0,
                        'description': prod.description_sale or '',
                        'uomQty': prod.uom_QTY or '',
                        'qtyAvailable': qty_available,
                        'thumbNail': _get_image_url(base_url, 'product.template', prod.id, 'image_1920',
                                                    prod.write_date)
                    })
            else:
                if (prod.is_mobikul_available2 == True):
                    comb_info = prod.with_context(**context)._get_combination_info(combination=False, product_id=False,
                                                                                   add_qty=1, pricelist=pricelist,
                                                                                   parent_combination=False,
                                                                                   only_template=False)
                    qty_available = prod.qty_available
                    result.append({
                        'templateId': prod.id or '',
                        'name': prod.name or '',
                        # 'priceUnit': _displayWithCurrency(lang_obj, comb_info['has_discounted_price'] and comb_info['list_price'] or
                        #                                   comb_info['price'] or 0, ' ', currency_symbol, currency_position),

                        'priceUnit': _displayWithCurrency(lang_obj, prod.list_price or 0, currency_symbol,
                                                          currency_position),
                        'priceReduce': comb_info['has_discounted_price'] and _displayWithCurrency(lang_obj,
                                                                                                  comb_info[
                                                                                                      'price'] or 0,
                                                                                                  currency_symbol,
                                                                                                  currency_position) or "",
                        'productId': prod.product_variant_id and prod.product_variant_id.id or '',
                        'productCount': prod.product_variant_count or 0,
                        'description': prod.description_sale or '',
                        'uomQty': prod.uom_QTY or '',
                        'qtyAvailable': qty_available,
                        'thumbNail': _get_image_url(base_url, 'product.template', prod.id, 'image_1920',
                                                    prod.write_date)
                    })





        else:
            comb_info = prod.with_context(**context)._get_combination_info(combination=False, product_id=False,
                                                                           add_qty=1, pricelist=pricelist,
                                                                           parent_combination=False,
                                                                           only_template=False)
            qty_available = prod.qty_available
            result.append({
                'templateId': prod.id or 0,
                'name': prod.name or '',
                # 'priceUnit': _displayWithCurrency(lang_obj, comb_info['has_discounted_price'] and comb_info['list_price'] or
                #                                   comb_info['price'] or 0, ' ', currency_symbol, currency_position),

                'priceUnit': _displayWithCurrency(lang_obj, prod.list_price or 0, currency_symbol, currency_position),
                'priceReduce': comb_info['has_discounted_price'] and _displayWithCurrency(lang_obj,
                                                                                          comb_info['price'] or 0,
                                                                                          currency_symbol,
                                                                                          currency_position) or "",
                'productId': prod.product_variant_id and prod.product_variant_id.id or '',
                'productCount': prod.product_variant_count or 0,
                'description': prod.description_sale or '',
                'uomQty': prod.uom_QTY or '',
                'qtyAvailable':qty_available,
                'thumbNail': _get_image_url(base_url, 'product.template', prod.id, 'image_1920', prod.write_date)
            })
    return result


def _get_product_fields():
    return ['name', 'product_variant_id', 'product_variant_count', 'price', 'description_sale', 'lst_price',  'is_mobikul_available','write_date','qty_available']


def _get_product_domain():
   # , ('qty_available', ">", 0.0)
    return [("sale_ok", "=", True), ("is_mobikul_available", "=", True)]


def _easy_date(time=False):
    """
    Get a datetime object or a timestamp and return a
    easy read string like 'Just now', 'Yesterday', '3 months ago',
    'Year ago'.
    """
    now = datetime.now()
    if type(time) is str:
        time = fields.Datetime.from_string(time)
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(int(day_diff / 7)) + " weeks ago"
    if day_diff < 365:
        return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"


TAG_RE = re.compile(r'<[^>]+>')


def remove_htmltags(text):
    return TAG_RE.sub('', text)


AQUIRER_REF_CODES = [
    'COD', 'STRIPE_E', 'STRIPE_W', "AUTHORIZE_NET","HYPERPAY",
    "2_CHECKOUT", "PAYFORT_SADAD", "PAYFORT", "PAYTABS","PAYULATAM","CASH"
]


STATUS_MAPPING = {
    "STRIPE": {'succeeded': 'done', 'pending': 'pending', 'failed': 'error'},
}

EMPTY_ADDRESS = "\n\n  \n"


def _get_next_reference(order_name):
    return order_name+"-"+str(uuid.uuid4())[:5]
