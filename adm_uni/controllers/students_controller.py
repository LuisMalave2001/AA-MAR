# -*- coding: utf-8 -*-

from odoo import http
from . import base_controller as base
import json
from datetime import date
from datetime import datetime

class StudentController(http.Controller):
    @http.route("/admission/adm_uni", auth="public", methods=["GET"], cors='*')        
    def get_adm_uni(self, **params):
        # print(http.request.httprequest.args.getlist("test"))
        students = http.request.env['adm_uni.inquiry']    
        search_domain = [("country_id", "=", int(params['country_id']))] if "country_id" in params else []        
        students_record = students.search(search_domain)        
        fecha_str = datetime.strftime(date_object, '%dd/%mm/%Y')        
        students_values = students_record.read(["id","city","country_id","state_id", "street_address","zip","first_name","last_name","name","status_id"]) 
        
        
        
fecha_str = "14/07/2014"
date_object = datetime.strptime(fecha_str, '%dd/%mm/%Y')

fecha_str = datetime.strftime(date_object, '%dd/%mm/%Y')

students_values[0]= fecha_str
        
        
        return json.dumps(students_values)

