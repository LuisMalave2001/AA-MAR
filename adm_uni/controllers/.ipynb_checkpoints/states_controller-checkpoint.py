# -*- coding: utf-8 -*-

from odoo import http
from . import base_controller as base
import json


class StateController(http.Controller):
    @http.route("/admission/states", auth="public", methods=["GET"])
    def get_states(self, **params):
        # print(http.request.httprequest.args.getlist("test"))
        states = http.request.env['res.country.state']
        search_domain = [("country_id", "=", int(params['country_id']))] if "country_id" in params else []
        states_record = states.search(search_domain)
        states_values = states_record.read(["name", "country_id"])
        return json.dumps(states_values)
    
    @http.route("/admission/adm_uni", auth="public", methods=["GET"])
    def get_adm_uni(self, **params):
        # print(http.request.httprequest.args.getlist("test"))
        students = http.request.env['adm_uni.inquiry']
        search_domain = [("country_id", "=", int(params['country_id']))] if "country_id" in params else []
        students_record = students.search(search_domain)
        students_values = states_record.read(["first_name", "last_name","name","id"])
        # states.sudo().write();
        return json.dumps(students_values)

    