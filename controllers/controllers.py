# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.website_portal.controllers.main import website_account


class website_account(website_account):

    @http.route()
    def account(self, **kw):
        """ Add sales documents to main account page """
        response = super(website_account, self).account(**kw)
        partner = request.env.user.partner_id
        timesheet_count = request.env['account.analytic.line'].search_count([
            ('partner_id.id', '=', partner.id),
        ])
        response.qcontext.update({
            'timesheet_count': timesheet_count,
        })
        return response


class WebsiteTimesheets(http.Controller):

    def _prepare_portal_layout_values(self):
        """ prepare the values to render portal layout """
        partner = request.env.user.partner_id
        if partner.user_id:
            sales_rep = partner.user_id
        else:
            sales_rep = False
        values = {
            'sales_rep': sales_rep,
            'company': request.website.company_id,
            'user': request.env.user
        }
        return values

    @http.route(
        ['/my/my_timesheets/', '/my/my_timesheets/page/<int:page>'],
        type='http', auth='user', website=True)
    def portal_my_timesheets(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        aal = request.env['account.analytic.line']

        sortings = {
            'name': {'label': _('Name'), 'order': 'name'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'is_invoiced': {
                'label': _('Is Invoived'), 'order': 'is_invoiced desc'},
            'unit_amount': {
                'label': _('Duration'), 'order': 'unit_amount desc'},
        }
        order = sortings.get(sortby, sortings['date'])['order']
        domain = [
            ('partner_id.id', '=', partner.id),
        ]
        # count for pager
        timesheet_count = int(aal.search_count(domain))
        lines = aal.search(domain, order=order)
        pager = request.website.pager(
            url="/my/my_timesheets",
            total=timesheet_count,
            page=page,
        )
        values.update({
            'lines': lines,
            'pager': pager,
            'sortings': sortings,
            'sortby': sortby,
            'default_url': '/my/my_timesheets',
        })
        return request.render(
            "website_timesheets.portal_my_timesheets", values)
