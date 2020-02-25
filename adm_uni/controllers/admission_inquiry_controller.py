# -*- coding: utf-8 -*-
from odoo import http
from ..utils import formatting
import base64


def get_parameters():
    return http.request.httprequest.args


def post_parameters():
    return http.request.httprequest.form


class Admission(http.Controller):

    #===================================================================================================================
    # @http.route("/")
    # def
    #===================================================================================================================

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

    @http.route("/admission-university/inquiry", auth="public", methods=["POST"], website=True, csrf=False)
    def add_inquiry(self, **params):
        if "txtMiddleName" not in params:
            params["txtMiddleName"] = ""
            
        # Personal Info
        first_name = params["txtFirstName"]
        last_name = params["txtLastName"]
        middle_name = params["txtMiddleName"]
        birthdate = params["txtBirthdate"]
        
        # Contact
        phone = params["txtPhone"]
        email = params["txtEmail"]
        
        # School information
        current_school = params["txtCurrentSchool"]
        current_school_address = params["txtCurrentSchoolAddress"]
        
        # Location
        country = params["selCountry"]
        state = params["selState"] if params["selState"] != "-1" else False
        city = params["txtCity"]
        street_address = params["txtStreetAddress"]
        zipCode = params["txtZip"]
        
        
        contact_time_id = int(params["selPreferredContactTime"]) if params["selPreferredContactTime"] else False
        degree_program_id = int(params["selPreferredDegreeProgram"]) if params["selPreferredDegreeProgram"] else False
        
        new_student_dict = {
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'birthdate': birthdate,
            
            'email': email,
            'phone': phone,
            
            'current_school': current_school,
            'current_school_address': current_school_address,

            'country_id': country,
            'state_id': state,
            'city': city,
            'street_address': street_address,
            'zip': zipCode,
            
            'preferred_degree_program': degree_program_id,
            'contact_time_id': contact_time_id,
        }
        
        InquiryEnv = http.request.env["adm_uni.inquiry"]
        student = InquiryEnv.sudo().create(new_student_dict)
        
        response = http.request.render('adm_uni.template_inquiry_sent')
        return response
