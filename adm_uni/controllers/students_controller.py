# -*- coding: utf-8 -*-

from odoo import http
from . import base_controller as base
import json

class StudentController(http.Controller):
    @http.route("/admission/adm_uni", auth="public", methods=["GET"])
    def get_adm_uni(self, **params):
        # print(http.request.httprequest.args.getlist("test"))
        students = http.request.env['adm_uni.inquiry']
        search_domain = [("country_id", "=", int(params['country_id']))] if "country_id" in params else []
        students_record = students.search(search_domain)
	students_values = students_record.read(["id","city","country_id","create_uid","current_school","current_school_address","email","first_name","gender","last_name","name","phone","state_id","street_address","write_uid","zip"]) 
        return json.dumps(states_values)

