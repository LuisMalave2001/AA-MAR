# -*- coding: utf-8 -*-
from odoo import http
from ..utils import formatting
import base64


def get_parameters():
    return http.request.httprequest.args


def post_parameters():
    return http.request.httprequest.form


class Admission(http.Controller):

    @http.route("/admission-university/inquiry", auth="public", methods=["POST"], website=True, csrf=False)
    def add_inquiry(self, **params):

        InquiryEnv = http.request.env["adm_uni.inquiry"]

        if "email" in params:
            params["email"] = params["email"].lower()
            email_count = InquiryEnv.sudo().search_count( [("email", "=", params["email"])] )
            if email_count > 0:
                response = http.request.render('adm_uni.template_repeated_email')
                return response


        field_ids = http.request.env.ref("adm_uni.model_adm_uni_inquiry").sudo().field_id
        fields = [field_id.name for field_id in field_ids]
        keys = params.keys() & fields
        result = {k:params[k] for k in keys}
        field_types = {field_id.name:field_id.ttype for field_id in field_ids}

        many2one_fields = [name for name, value in field_types.items() if value == "many2one"]
        for key in result.keys():
            if key in many2one_fields:
                result[key] = int(result[key])
                if result[key] == -1:
                    result[key] = False
                    pass    
        
        if result:
            new_inquiry = InquiryEnv.sudo().create(result)

        response = http.request.render('adm_uni.template_inquiry_sent')
        return response

    @http.route("/admission-university/inquiry", auth="public", methods=["GET"], website=True)
    def admission_web(self, **params):
        countries = http.request.env['res.country']
        contact_times = http.request.env['adm_uni.contact_time']
        degree_programs = http.request.env['adm_uni.degree_program']

        response = http.request.render('adm_uni.template_admission_inquiry', {
            'countries': countries.search([]),
            'contact_time_ids': contact_times.browse(contact_times.search([])),
            'degree_program_ids': degree_programs.browse(degree_programs.search([])),
        })
        return response
    
     #===================================================================================================================
     # @http.route("/")
     # def
     #===================================================================================================================
#    @http.route("/admission-university/inquiry", auth="public", methods=["POST"], website=True, csrf=True)
#    def write_application(self, inquiry_id, **params):
#        field_ids = http.request.env.ref("adm_.model_adm_uni_inquiry").sudo().field_id
#        fields = [field_id.name for field_id in field_ids]
#        keys = params.keys() & fields
#        result = {k:params[k] for k in keys}
#        field_types = {field_id.name:field_id.ttype for field_id in field_ids}
#        
#        # if field_id.ttype != 'one2many' and field_id.ttype != 'many2many'
#            
#        many2one_fields = [name for name, value in field_types.items() if value == "many2one"]
#        for key in result.keys():
#            if key in many2one_fields:
#                result[key] = int(result[key])
#                if result[key] == -1:
#                    result[key] = False
#                    pass    
        
        #===============================================================================================================
        # one2many_fields = [name for name, value in field_types.items() if value == "one2many"]
        # many2many_fields = [name for name, value in field_types.items() if value == "many2many"]
        #  
        # for key in post_params.keys():
        #     if key in many2many_fields:
        #         pass
        #===============================================================================================================
        
#        if result:
#            http.request.env["adm_uni.inquiry"].browse([application_id]).sudo().write(result)
            
#        return http.request.redirect(http.request.httprequest.referrer)




        # Personal Info
        #first_name = params["txtFirstName"]
        #last_name = params["txtLastName"]
        #middle_name = params["txtMiddleName"]
        #birthdate = params["txtBirthdate"]
        
        # Contact
        #phone = params["txtPhone"]
        #email = params["txtEmail"]
        
        
        #contact_time_id = int(params["selPreferredContactTime"]) if params["selPreferredContactTime"] else False
        #degree_program_id = int(params["selPreferredDegreeProgram"]) if params["selPreferredDegreeProgram"] else False
        
        #new_student_dict = {
        #    'first_name': first_name,
        #    'middle_name': middle_name,
        #    'last_name': last_name,
        #    'birthdate': birthdate,
        #    
        #    'email': email,
        #    'phone': phone,
        #    
        #    'current_school': current_school,
        #    'current_school_address': current_school_address,

        #    'country_id': country,
        #    'state_id': state,
        #    'city': city,
        #    'street_address': street_address,
        #    'zip': zipCode,
        #    
        #    'preferred_degree_program': degree_program_id,
        #    'contact_time_id': contact_time_id,
        #}
        
        #InquiryEnv = http.request.env["adm_uni.inquiry"]
        #student = InquiryEnv.sudo().create(new_student_dict)
        
        #response = http.request.render('adm_uni.template_inquiry_sent')
        #return response
