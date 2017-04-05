# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from odoo import http, _
from odoo.http import request
from odoo.addons.website_portal.controllers.main import website_account

# Zodziu ismesti details you company_id
# Paspaudus timesheets atsidaro lists su menesiai ir savaiteim
# tada paspaudus saveite tik tada rodo timesheetus
# tai pat prideti total prie duration kad rodytu kiek is viso pradirbta


def _aal_date(line_date):
    r = datetime.strptime(line_date, "%Y-%m-%d")
    return (r.year, r.month, r.day)

items_per_page = 20


class website_account(website_account):

    @http.route()
    def account(self, **kw):
        response = super(website_account, self).account(**kw)
        partner = request.env.user.partner_id
        timesheet_count = request.env['account.analytic.line'].search_count([
            ('partner_id.id', '=', partner.id),
        ])
        response.qcontext.update({
            'timesheet_count': timesheet_count,
        })
        return response

    @http.route(
        ['/my/my_timesheets/', '/my/my_timesheets/page/<int:page>'],
        type='http', auth='user', website=True)
    def portal_my_timesheets(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        aal = request.env['account.analytic.line']

        sortings = {
            'date': {'label': _('Newest'), 'order': 'date desc'},
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
        pager = request.website.pager(
            url="/my/my_timesheets",
            total=timesheet_count,
            page=page,
            step=self._items_per_page,
        )
        lines = aal.search(
            domain, order=order, limit=self._items_per_page,
            offset=pager['offset']
        )
        for line in lines:
            dt = datetime.strptime(line.date, "%Y-%m-%d").isocalendar()[1]
        all_weeks = datetime.now().isocalendar()[1]
        ls = []
        for i in range(1, all_weeks):
            ls.append(i)
        list_week = len(ls)
        values.update({
            'lines': lines,
            'pager': pager,
            'sortings': sortings,
            'sortby': sortby,
            'page_name': 'my_timesheets',
            'default_url': '/my/my_timesheets',
        })
        return request.render(
            "website_timesheets.portal_my_timesheets", values)
