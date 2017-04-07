# -*- coding: utf-8 -*-

from collections import OrderedDict

from datetime import date, datetime, timedelta
from odoo import http, _
from odoo.http import request
from odoo.addons.website_portal.controllers.main import website_account

# Gal net susikurt nauja moduli
# ir ten padaryt viska kaip cia tik ,
# padaryt javascript date pickeri kur leistu pasirinkti date_last_stage_update
# esu uz bookmarkines
# o nauaj daryti nes tas geras,
# isisaugot ir daryt normalu tik ne su savaitem o su DATE pickeriu ir js


def _aal_date(line_date):
    r = datetime.strptime(line_date, "%Y-%m-%d")
    return date(r.year, r.month, r.day)


def _week_and_year(nr_week, nr_year):
    nr_week = int(nr_week)
    return ('%s-%s') % (nr_year, nr_week)


def _full_date(year_and_week):
    s = datetime.strptime(year_and_week + '-0', "%Y-%W-%w")
    return date(s.year, s.month, s.day)

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

        all_weeks = datetime.now().isocalendar()[1]
        domain = [('partner_id.id', '=', partner.id)]
        timesheet_count = int(aal.search_count(domain))
        today = date.today()
        year = today.year

        # sortings = {
        #     'date': {'label': _('Newest'), 'order': 'date desc'},
        #     'is_invoiced': {
        #         'label': _('Is Invoived'), 'order': 'is_invoiced desc'},
        #     'unit_amount': {
        #         'label': _('Duration'), 'order': 'unit_amount desc'},
        # }
        #
        # order = sortings.get(sortby, sortings['date'])['order']
        pager = request.website.pager(
            url="/my/my_timesheets",
            url_args={'week': week},
            # url_args={'sortby': sortby, 'week': week},
            total=timesheet_count,
            page=page,
            step=self._items_per_page,
        )
        week_filters = OrderedDict({
            'all': {'label': _('All'), 'domain': []},
        })

        ls = []
        for i in range(all_weeks, 0, -1):
            ls.append(i)

        for week_number in ls:
                week_filters.update({str(week_number): {
                    'label': week_number, 'domain': []
                }})
        if week:
            if str(week) is ('all'):
                for week_number in ls:
                    week_filters.update({str(week_number): {
                        'label': week_number, 'domain': []
                    }})
            else:
                if week != ('all'):
                    year_week = _week_and_year(str(week), year)
                    dt = _full_date(year_week)
                    begining_of_the_week = dt - timedelta(days=6)
                    end_of_the_week = begining_of_the_week + timedelta(days=6)

                    for week_number in ls:
                        week_filters.update({str(week_number): {
                            'label': week_number, 'domain': [
                                ('date',  '>=', str(begining_of_the_week)),
                                ('date', '<=', str(end_of_the_week))]
                        }})
        domain += week_filters.get(week, week_filters['all'])['domain']

        lines = aal.search(
            domain, limit=self._items_per_page,
            offset=pager['offset']  # order=order,
        )
        values.update({
            'lines': lines,
            'pager': pager,
            # 'sortings': sortings,
            'week_filters': week_filters,
            'sortby': sortby,
            'week': week,
            'page_name': 'my_timesheets',
            'default_url': '/my_timesheets',
            'ls': ls,
            'aal': aal,
            'total_duration': sum(lines.mapped('unit_amount'))
        })

        return request.render(
            "website_timesheets.portal_my_timesheets", values)
