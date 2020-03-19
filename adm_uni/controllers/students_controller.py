# -*- coding: utf-8 -*-

from odoo import http
from . import base_controller as base
import json
from datetime import datetime
from datetime import date


class StudentController(http.Controller):
    @http.route("/admission/adm_uni", auth="public", methods=["GET"], cors='*')
    def get_adm_uni(self, **params):
        # print(http.request.httprequest.args.getlist("test"))
        students = http.request.env['adm_uni.inquiry']        
        search_domain = [("country_id", "=", int(params['country_id']))] if "country_id" in params else []  
        students_record = students.search(search_domain)        
        students_values = students_record.read(["id","city","country_id","state_id", "street_address","zip","first_name","middle_name","last_name","name","email","birthdate","gender","phone", "status_id","current_school","current_school_address","__last_update","create_date","create_uid","write_date","write_uid"])

        # Se recorre por cada estudiante
        for record in students_values:
            
            # Convertir fechas a string
            record["birthdate"] = record["birthdate"].strftime('%m/%d/%Y')
            # Es lo mismo que:
            # date_of_birth = record["birthdate"]
            # date_of_birth = date_of_birth.strftime('%m/%d/%Y')
            # record["birthdate"] = date_of_birth
            
            record["__last_update"] = record["__last_update"].strftime('%m/%d/%Y')
            record["create_date"] = record["create_date"].strftime('%m/%d/%Y')
            record["write_date"] = record["write_date"].strftime('%m/%d/%Y')          
                    
        return json.dumps(students_values)

