# -*- coding: utf-8 -*-

from odoo import http
from . import base_controller as base
import json
from datetime import datetime
from datetime import date

#controlador encargado de devolver data de estudiantes, para insertarlo en FACTS
class StudentController(http.Controller):
    #definiendo la url desde donde va ser posible acceder, tipo de metodo, cors para habiltiar accesos a ip externas.
    @http.route("/admission/adm_uni", auth="public", methods=["GET"], cors='*')
    # define una funcion principal
    def get_adm_uni(self, **params): 
        #crea una variable con el modelo desde donde se va a tomar la información
        students = http.request.env['adm_uni.inquiry']        
        
        #filtro del modelo basados en parametros de la url
        search_domain = [("country_id", "=", int(params['country_id']))] if "country_id" in params else []
        
        #Tomar informacion basado en el modelo y en el domain IDS
        students_record = students.search(search_domain)      
        
        #Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
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
            
            #crea una variable con el modelo desde donde se va a tomar la información
            attachments = http.request.env['ir.attachment']        
        
            #filtro del modelo basados en parametros de la url
            search_domain_attach = [("res_model", "=", "adm_uni.inquiry"),("res_id","=",record["id"])]
        
            #Tomar informacion basado en el modelo y en el domain IDS
            attachments_record = attachments.search(search_domain_attach)      
        
            #Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            attachments_values = attachments_record.read(["id"])    
            record["attachIds"] = json.dumps(attachments_values)
            
        #students_values.append("test")
        #pintar la información obtenida, esto lo utilizamos para parsearlo en el ajax.         
        return json.dumps(students_values)

