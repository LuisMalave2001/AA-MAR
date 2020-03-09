from odoo import http
import json

class BaseController(http.Controller):
    @http.route("/admission/student", auth="public", methods=["GET"])
    def get_languages(self, **params):
        partners = http.request.env['res.partner'].sudo().search_read([])

        headers = {'Content-Type': 'application/json'}
        body = { 'results': { 'code': 200, 'message': partners } }

        return http.Response(json.dumps(body), headers=headers)
        
