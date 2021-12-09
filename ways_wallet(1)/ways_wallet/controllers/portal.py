# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class PortalTransaction(CustomerPortal):

    def _prepare_home_portal_values(self):
        values = super(PortalTransaction, self)._prepare_home_portal_values()
        transaction_count = request.env['ways.transactions'].search_count([
            ('state', '=', 'done'),('partner_id','=',request.env.user.partner_id.id)
        ]) 

        values['transaction_count'] = transaction_count
        return values

    # ------------------------------------------------------------
    # My Invoices
    # ------------------------------------------------------------

    def _transaction_get_page_view_values(self, transaction, access_token, **kwargs):
        values = {
            'page_name': 'transaction',
            'transaction': transaction,
        }
        return self._get_page_view_values(transaction, access_token, values, 'my_transactions_history', False, **kwargs)

    @http.route(['/my/transactions', '/my/transactions/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_transactions(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        AccountTransaction = request.env['ways.transactions']

        domain = [('state', '=', 'done'),('partner_id','=',request.env.user.partner_id.id)]

        searchbar_sortings = {
            'transaction_id': {'label': _('Transaction'), 'order': 'transaction_id desc'},
            'sale_order': {'label': _('Sale Order'), 'order': 'sale_order desc'},
            'transaction_tags': {'label': _('Tags'), 'order': 'transaction_tags desc'},
            'transaction_date': {'label': _('Transaction Date'), 'order': 'transaction_date desc'},
            'transaction_type': {'label': _('Transaction Type'), 'order': 'transaction_type'},
            'state': {'label': _('State'), 'order': 'state'},
            'amount': {'label': _('Amount'), 'order': 'amount desc'},
            'amount_total': {'label': _('Balance'), 'order': 'amount_total'},
        }
        # default sort by order
        if not sortby:
            sortby = 'transaction_date'
        order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('ways.transactions', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        transaction_count = AccountTransaction.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/transactions",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=transaction_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        transactions = AccountTransaction.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_transactions_history'] = transactions.ids[:100]
        companies = http.request.env['res.partner'].sudo().search([('id','=',request.env.user.partner_id.id)])

        values.update({
            'date': date_begin,
            'transactions': transactions,
            'page_name': 'transaction',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/transactions',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'companies' :companies
        })
        return request.render("ways_wallet.portal_my_transactions", values)

    @http.route(['/my/transactions/<int:transaction_id>'], type='http', auth="public", website=True)
    def portal_my_transaction_detail(self, transaction_id, access_token=None, report_type=None, download=False, **kw):
        try:
            transaction_sudo = self._document_check_access('ways.transactions', transaction_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=transaction_sudo, report_type=report_type, report_ref='account.account_invoices', download=download)

        values = self._transaction_get_page_view_values(transaction_sudo, access_token, **kw)

        return request.render("account.portal_transaction_page", values)

    # ------------------------------------------------------------
    # My Home
    # ------------------------------------------------------------

    def details_form_validate(self, data):
        error, error_message = super(PortalAccount, self).details_form_validate(data)
        # prevent VAT/name change if invoices exist
        partner = request.env['res.users'].browse(request.uid).partner_id
        if not partner.can_edit_vat():
            if 'vat' in data and (data['vat'] or False) != (partner.vat or False):
                error['vat'] = 'error'
                error_message.append(_('Changing VAT number is not allowed once invoices have been issued for your account. Please contact us directly for this operation.'))
            if 'name' in data and (data['name'] or False) != (partner.name or False):
                error['name'] = 'error'
                error_message.append(_('Changing your name is not allowed once invoices have been issued for your account. Please contact us directly for this operation.'))
            if 'company_name' in data and (data['company_name'] or False) != (partner.company_name or False):
                error['company_name'] = 'error'
                error_message.append(_('Changing your company name is not allowed once invoices have been issued for your account. Please contact us directly for this operation.'))
        return error, error_message
