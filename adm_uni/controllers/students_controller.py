# -*- coding: utf-8 -*-

from odoo import http
from . import base_controller as base
import json

class StudentController(http.Controller):
    @http.route("/admission/adm_uni", auth="public", methods=["GET"], cors='*')
    def get_adm_uni(self, **params):
        # print(http.request.httprequest.args.getlist("test"))
        students = http.request.env['adm_uni.inquiry']        
        search_domain = [("country_id", "=", int(params['country_id']))] if "country_id" in params else []  
        students_record = students.search(search_domain)
        students_values = students_record.read(["id","city","country_id","state_id", "street_address","zip","first_name","last_name","name","email"])
        
        return json.dumps(students_values)

