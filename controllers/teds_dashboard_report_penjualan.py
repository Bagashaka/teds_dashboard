import openerp.http as http 
from openerp.http import request
from openerp.addons.rest_api.controllers.main import *
from datetime import date,timedelta,datetime,date
import logging
_logger = logging.getLogger(__name__)

def invalid_response(status, error, info,method):
    if method == 'POST':
        return {
            'error': error,
            'error_descrip': info,
        }

    elif method == 'GET':
        return werkzeug.wrappers.Response(
            status=status,
            content_type='application/json; charset=utf-8',
            response=json.dumps({
                'error': error,
                'error_descrip': info,
            }),
        )

def invalid_token(method):
    _logger.error("Token is expired or invalid!")    
    return invalid_response(401, 'invalid_token', "Token is expired or invalid!",method)

def check_valid_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        access_token = request.httprequest.headers.get('access_token')
        method = request.httprequest.method
        if not access_token:
            info = "Missing access token in request header!"
            error = 'access_token_not_found'
            _logger.error(info)
            return invalid_response(400, error, info,method)

        access_token_data = request.env['oauth.access_token'].sudo().search(
            [('token', '=', access_token)], order='id DESC', limit=1)

        if access_token_data._get_access_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_token(method)

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap

class TedsDashboardReportPenjualan(http.Controller):

    @http.route('/api/dashboard/report/penjualan', type='http', auth='none', methods=['GET'], csrf=False)
    @check_valid_token
    def get_report_penjualan(self, **kwargs):
        try:
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')

            if start_date and not end_date:
                error = 'missing_end_date'
                info = "End date is missing while start date is provided."
                _logger.error(info)
                return invalid_response(400, error, info, 'GET')
            elif end_date and not start_date:
                error = 'missing_start_date'
                info = "Start date is missing while end date is provided."
                _logger.error(info)
                return invalid_response(400, error, info, 'GET')

            if start_date and end_date:
                # Convert string dates to datetime objects
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                # Jika kedua tanggal ada, gunakan parameter tersebut
                sales_data = request.env['dashboard.report.penjualan'].get_sales_data(start_date, end_date)
            else:
                # Jika kedua tanggal tidak ada, gunakan query tanpa parameter tanggal
                sales_data = request.env['dashboard.report.penjualan'].get_sales_no_date()
            # Call the method from DashboardReportPenjualan model
            return json.dumps({'sales_data': sales_data})
        
        except Exception as e:
            error = 'internal_server_error'
            info = "An error occurred while processing the request: {}".format(str(e))
            _logger.error(info)
            return invalid_response(500, error, info, 'GET')