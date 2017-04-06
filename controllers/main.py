# -*- coding: utf-8 -*-

from collections import OrderedDict

from datetime import date, datetime
from odoo import http, _
from odoo.http import request
from odoo.addons.website_portal.controllers.main import website_account

# tada paspaudus saveite, rodo timesheetus tos savaites
# tai pat prideti total prie duration kad rodytu kiek is viso pradirbta

# naujas
# week defaultine turetu but naujausia week


def _aal_date(line_date):
    r = datetime.strptime(line_date, "%Y-%m-%d")
    return date(r.year, r.month, r.day)

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
    def portal_my_timesheets(self, page=1, sortby=None, week=None, **kw):
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
        domain = [('partner_id.id', '=', partner.id)]
        # count for pager
        timesheet_count = int(aal.search_count(domain))
        pager = request.website.pager(
            url="/my/my_timesheets",
            url_args={'sortby': sortby, 'week': week},
            total=timesheet_count,
            page=page,
            step=self._items_per_page,
        )
        lines = aal.search(
            domain, order=order, limit=self._items_per_page,
            offset=pager['offset']
        )
        week_filters = OrderedDict({
            'all': {'label': _('All'), 'domain': []},
        })

        # Line week
        for line in lines:
            line_dt = _aal_date(line.date)  # is stringo i data
            week_n = line_dt.isocalendar()[1]  # eilutes savaite
        all_weeks = datetime.now().isocalendar()[1]  # dabartine savaite pvz 13

        # All weeks
        ls = []
        for i in range(all_weeks, 0, -1):
            ls.append(i)

        # convert week number to date
        today = date.today()
        year = today.year

        # import datetime
        # d = "2013-W26"
        # r = datetime.datetime.strptime(d + '-0', "%Y-W%W-%w")

        def week_and_year(nr_week, nr_year):
            return ('%s-%s') % (nr_year, int(nr_week))

        ds = week_and_year(week, year)

        # year_week = week_and_year(week, year)

        def full_date(year_and_week):
            s = datetime.strptime(ds + '-0', "%Y-%W-%w")
            return date(s.year, s.month, s.day)

        if week:
            year_week = week_and_year(week, year)
            dt = full_date(year_week)
            import pdb; pdb.set_trace()
        else:
            None

        wik = _aal_date(line.date).isocalendar()[1]
        for week_number in ls:
            week_filters.update(
                {str(week_number): {'label': week_number,
                                    'domain': [()]
                                    # 'domain': [("savaites prad", '<=', 'date', '<=', "savaites pabaiga")]
                                    }})
        # import pdb; pdb.set_trace()

        domain += week_filters.get(week, week_filters['all'])['domain']
        values.update({
            'lines': lines,
            'pager': pager,
            'sortings': sortings,
            'week_filters': week_filters,
            'sortby': sortby,
            'week': week,
            'page_name': 'my_timesheets',
            'default_url': '/my/my_timesheets',
            'ls': ls,
            'week_n': week_n,
            'line_dt': line_dt,
            'aal': aal,
            'wik': wik,
        })
        return request.render(
            "website_timesheets.portal_my_timesheets", values)
