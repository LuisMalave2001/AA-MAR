# -*- coding: utf-8 -*-

import base64
import logging
import itertools

from ..utils import commons

from odoo import http
from datetime import datetime


def get_parameters():
    return http.request.httprequest.args

def post_parameters():
    return http.request.httprequest.form

def file_parameters():
    return http.request.httprequest.files

_logger_ = logging.getLogger()

class Admission(http.Controller):
    
    def get_partner(self):
        return http.request.env.user.partner_id
    
    @http.route("/admission-university/application-form", auth="public", methods=["GET"], website=True)
    def admission_web_form(self, **params):
        contact_id = self.get_partner()       
        countries = http.request.env['res.country']
        states = http.request.env['res.country.state']
        application_id = contact_id.uni_application_id
        

        if not application_id:
            return http.request.render('adm_uni.template_no_application_error')

        application_status_ids = http.request.env["adm_uni.application.status"].browse(http.request.env["adm_uni.application.status"].search([])).ids
        contact_time_ids = http.request.env["adm_uni.contact_time"].browse(http.request.env["adm_uni.contact_time"].search([])).ids
        degree_program_ids = http.request.env["adm_uni.degree_program"].browse(http.request.env["adm_uni.degree_program"].search([])).ids
        
        language_ids = http.request.env['adm_uni.languages'].browse(http.request.env['adm_uni.languages'].search([]))
        language_level_ids = http.request.env['adm_uni.languages.level'].browse(http.request.env['adm_uni.languages.level'].search([]))
        
        if application_id.status_type != 'return_for_update':
            render_template = 'adm_uni.template_admission_application'
            response = http.request.render(render_template, {
                'contact_id': contact_id,
                'application_status_ids': application_status_ids,
                'language_ids': language_ids.ids,
                'language_level_ids': language_level_ids.ids,
                'contact_time_ids': contact_time_ids,
                'degree_program_ids': degree_program_ids,
                'countries': countries.search([]),
                'states': states.search([]),
                'application_id': application_id,
            })
            return response
        
        response = http.request.render('adm_uni.template_admission_application_form', {
            'contact_id': contact_id,
            'application_status_ids': application_status_ids,
            'language_ids': language_ids.ids,
            'language_level_ids': language_level_ids.ids,
            'contact_time_ids': contact_time_ids,
            'degree_program_ids': degree_program_ids,
            'countries': countries.search([]),
            'states': states.search([]),
            'application_id': application_id,
        })
        return response
        
    @http.route("/admission-university/application", auth="public", methods=["GET"], website=True)
    def admission_web(self, **params):
        contact_id = self.get_partner()       
        countries = http.request.env['res.country']
        states = http.request.env['res.country.state']
        application_id = contact_id.uni_application_id
        
        if not application_id:
            return http.request.render('adm_uni.template_no_application_error')
        
        application_status_ids = http.request.env["adm_uni.application.status"].browse(http.request.env["adm_uni.application.status"].search([])).ids
        contact_time_ids = http.request.env["adm_uni.contact_time"].browse(http.request.env["adm_uni.contact_time"].search([])).ids
        degree_program_ids = http.request.env["adm_uni.degree_program"].browse(http.request.env["adm_uni.degree_program"].search([])).ids
        
        language_ids = http.request.env['adm_uni.languages'].browse(http.request.env['adm_uni.languages'].search([]))
        language_level_ids = http.request.env['adm_uni.languages.level'].browse(http.request.env['adm_uni.languages.level'].search([]))

        render_template = 'adm_uni.template_admission_application_form' if not contact_id.is_in_application else 'adm_uni.template_admission_application'

        response = http.request.render(render_template, {
            'contact_id': contact_id,
            'application_status_ids': application_status_ids,
            'language_ids': language_ids.ids,
            'language_level_ids': language_level_ids.ids,
            'contact_time_ids': contact_time_ids,
            'degree_program_ids': degree_program_ids,
            'countries': countries.search([]),
            'states': states.search([]),
            'application_id': application_id,
        })
        return response
    
    @http.route("/admission-university/message", auth="public", methods=["POST"], website=True, csrf=False)
    def send_message(self, **params):
        contact_id = self.get_partner()
        application_id = contact_id.uni_application_id
        
        if not application_id:
            return http.request.render('adm_uni.template_no_application_error')
        
        print("Params: {}".format(params))
        
        upload_file = params["file_upload"]
        message_body = params["message_body"]
        
        message_body=message_body.replace("\n","<br />\n")
        
        MessageEnv = http.request.env["mail.message"]
        message_id = MessageEnv.create({
            'date': datetime.today(),
            'email_from': '"{}" <{}>'.format(contact_id.name, contact_id.email),
            'author_id': contact_id.id,
            'record_name': "",
            "model": "adm_uni.application",
            "res_id": contact_id.uni_application_id.id,
            "message_type": "comment",
            "subtype_id": 1,
            "body": "<p>{}</p>".format(message_body),
        })
        
        AttachmentEnv = http.request.env["ir.attachment"]
        
        if upload_file:
            file_id = AttachmentEnv.sudo().create({
                'name': upload_file.filename,
                'datas_fname': upload_file.filename,
                'res_name': upload_file.filename,
                'type': 'binary',   
                'res_model': 'adm_uni.application',
                'res_id': contact_id.uni_application_id,
                'datas': base64.b64encode(upload_file.read()),
            })
        
        return http.request.redirect('/admission-university/application')
        
        #===============================================================================================================
        # return "Ok"
        #===============================================================================================================
    def set_contact_ids(self, application_id, params):
        post_params = post_parameters()
        
        contact_names    = post_parameters().getlist("txtContactName")
        contact_id_names = post_parameters().getlist("txtContactIdName")
        contact_ids      = list(map(int, post_parameters().getlist("other_contact_id")))

        application = http.request.env["adm_uni.application"].browse([application_id])
        
        OtherContactEnv = http.request.env["adm_uni.application.other_contacts"]
        
        # First, delete all that are not in the form, that's why the user clicked remove button.
        all_ids = set(application.other_contacts_ids.ids)
        form_ids = {id for id in contact_ids if id != -1}
            
        ids_to_delete = all_ids ^ form_ids
        unlink_commands = [ (2, id, 0) for id in ids_to_delete ]
            
        if unlink_commands:
            application.sudo().write({"other_contacts_ids": unlink_commands})
            
        # PartnerEnv = http.request.env["res.partner"]
        
        for id, name, id_name \
        in itertools.zip_longest(contact_ids, contact_names, contact_id_names, fillvalue=False):
            if id != -1:
                other_contact = OtherContactEnv.browse([id])
                other_contact.sudo().write({
                    "contact_name": name,
                    "contact_identification": id_name,
                })
            else:
                if name:
                    other_contact = OtherContactEnv.sudo().create({
                        "contact_name": name,
                        "contact_identification": id_name,
                        "application_id": application_id,
                    })

    def set_language_ids(self, application_id, params):
        post_params = post_parameters()
        
        language_types  = list(map(int, post_parameters().getlist("selLanguage")))
        language_levels = list(map(int, post_parameters().getlist("selLanguageLevel")))
        language_ids      = list(map(int, post_parameters().getlist("language_id")))

        application = http.request.env["adm_uni.application"].browse([application_id])
        
        LanguageEnv = http.request.env["adm_uni.application.languages"]
        
        # First, delete all that are not in the form, that's why the user clicked remove button.
        all_ids = set(application.language_ids.ids)
        form_ids = {id for id in language_ids if id != -1}
            
        ids_to_delete = all_ids ^ form_ids
        unlink_commands = [ (2, id, 0) for id in ids_to_delete ]
            
        if unlink_commands:
            application.sudo().write({"language_ids": unlink_commands})
            
        # PartnerEnv = http.request.env["res.partner"]
        
        for language_id, language_type, language_level \
        in itertools.zip_longest(language_ids, language_types, language_levels, fillvalue=False):
            if language_id != -1:
                other_contact = LanguageEnv.browse([language_id])
                other_contact.sudo().write({
                    "language_level_id": language_level,
                    "language_id": language_type,
                })
            else:
                if language_type != -1:
                    other_contact = LanguageEnv.sudo().create({
                        "language_level_id": language_level,
                        "language_id": language_type,
                        "application_id": application_id,
                    })


    @http.route("/admission-university/application", auth="public", methods=["POST"], website=True, csrf=False)
    def add_admission(self, **params):
        
        contact_id = self.get_partner()
        application_id = contact_id.uni_application_id
        
        if not application_id:
            return http.request.render('adm_uni.template_no_application_error')
            
        if "txtMiddleName" not in params:
            params["txtMiddleName"] = ""
            
        # Personal Info
        date_of_birth = commons.extractValueFromDict("date_of_birth", params)
        gender = params["selGender"] if params["selGender"] else False
        father_name = params["txtFatherName"] if params["txtFatherName"] else False
        mother_name = params["txtMotherName"] if params["txtMotherName"] else False
        
        # School information
        previous_school = params["txtPreviousSchool"] if "txtPreviousSchool" in params and params["txtPreviousSchool"] else False
        gpa = params["txtGPA"] if "txtGPA" in params and params["txtGPA"] else False
        cumulative_grades = params["txtCumulativeGrade"] if "txtCumulativeGrade" in params and params["txtCumulativeGrade"] else False
        regional_exam_grade = params["txtRegionalExam"] if "txtRegionalExam" in params and params["txtRegionalExam"] else False
        bac_grade = params["txtBACGrade"] if "txtBACGrade" in params and params["txtBACGrade"] else False
        
        merit_or_degree_ss = params["want_scholarship"] if "want_scholarship" in params and params["want_scholarship"] else False
        merit_or_degree_type = params["scholarship_type"] if "scholarship_type" in params and params["scholarship_type"] else False
        need_based_scholarship = params["scholarship_considered"] if "scholarship_considered" in params and params["scholarship_considered"] else False
         
        # School information
        current_school = commons.extractValueFromDict("txtCurrentSchool", params)
        current_school_address = commons.extractValueFromDict("txtCurrentSchoolAddress", params)
        
        # Location
        country = int(commons.extractValueFromDict("selCountry", params))
        state = int(params["selState"] if params["selState"] != "-1" else False)
        city = commons.extractValueFromDict("txtCity", params)
        street_address = commons.extractValueFromDict("txtStreetAddress", params)
        zipCode = commons.extractValueFromDict("txtZip", params)

        # Documentation 
        letter_of_motivation_file = params["fileLetterOfMotivation"] if params["fileLetterOfMotivation"] else False
        cv_file = params["fileCV"] if params["fileCV"] else False
        grade_transcript_file = params["fileGradeTranscript"] if params["fileGradeTranscript"] else False

        letters_of_recommendation_file = params["fileLettersOfRecommendation"] if params["fileLettersOfRecommendation"] else False
        
        # contact_time_id = params["selPreferredContactTime"]
        # preferred_degree_program = params["selPreferredDegreeProgram"]
        
        new_application_dict = {
            'gender': gender,
            'father_name': father_name,
            'mother_name': mother_name,
            'date_of_birth': date_of_birth,
            
            'previous_school': previous_school,
            'gpa': gpa,
            'cumulative_grades': cumulative_grades,
            'regional_exam_grade': regional_exam_grade,
            'bac_grade': bac_grade,
            
            'merit_or_degree_ss': merit_or_degree_ss,
            'merit_or_degree_type': merit_or_degree_type,
            'need_based_scholarship': need_based_scholarship,

            'country': country,
            'state': state,
            'city': city,
            'street_address': street_address,
            'zipCode': zipCode,

            'current_school': current_school,
            'current_school_address': current_school_address,
        }
        
        application_id.write(new_application_dict)

        AttachmentEnv = http.request.env["ir.attachment"]
        motivation_id = False
        if letter_of_motivation_file:
            motivation_id = AttachmentEnv.sudo().create({
                'name': letter_of_motivation_file.filename,
                'datas_fname': letter_of_motivation_file.filename,
                'res_name': letter_of_motivation_file.filename,
                'type': 'binary',   
                'res_model': 'adm_uni.application',
                'res_id': application_id.id,
                'datas': base64.b64encode(letter_of_motivation_file.read()),
            }).id
            
        cv_id = False
        if cv_file:
            cv_id = AttachmentEnv.sudo().create({
                'name': cv_file.filename,
                'datas_fname': cv_file.filename,
                'res_name': cv_file.filename,
                'type': 'binary',   
                'res_model': 'adm_uni.application',
                'res_id': application_id.id,
                'datas': base64.b64encode(cv_file.read()),
            }).id
        
        grade_transcript_id = False
        if grade_transcript_file:
            grade_transcript_id = AttachmentEnv.sudo().create({
                'name': grade_transcript_file.filename,
                'datas_fname': grade_transcript_file.filename,
                'res_name': grade_transcript_file.filename,
                'type': 'binary',   
                'res_model': 'adm_uni.application',
                'res_id': application_id.id,
                'datas': base64.b64encode(grade_transcript_file.read()),
            }).id
        
        letters_of_recommendation_id = False
        if letters_of_recommendation_file:
            letters_of_recommendation_id = AttachmentEnv.sudo().create({
                'name': letters_of_recommendation_file.filename,
                'datas_fname': letters_of_recommendation_file.filename,
                'res_name': letters_of_recommendation_file.filename,
                'type': 'binary',   
                'res_model': 'adm_uni.application',
                'res_id': application_id.id,
                'datas': base64.b64encode(letters_of_recommendation_file.read()),
            }).id
        
        #Adding scholarship files
        try:
            ss_attestation_salaire = file_parameters().getlist('ss_attestation_salaire')
            _logger_.info("Testing: {}".format(file_parameters()))
            
            for attachment in ss_attestation_salaire:
                attached_file = attachment.read()
                AttachmentEnv.sudo().create({
                            'name': attachment.filename,
                            'res_model': 'adm_uni.application',
                            'res_id': application_id.id,
                            'type': 'binary',
                            'datas_fname': attachment.filename,
                            'datas': base64.b64encode(attached_file),
                        })
        except AttributeError:
            pass 
           
        try: 
            ss_bulletin_de_paie = file_parameters().getlist('ss_bulletin_de_paie')
            for attachment in ss_bulletin_de_paie:
                attached_file = attachment.read()
                AttachmentEnv.sudo().create({
                            'name': attachment.filename,
                            'res_model': 'adm_uni.application',
                            'res_id': application_id.id,
                            'type': 'binary',
                            'datas_fname': attachment.filename,
                            'datas': base64.b64encode(attached_file),
                        }) 
        except AttributeError:
            pass 
             
        try:   
            ss_most_recent_tax = file_parameters().getlist('ss_most_recent_tax')
            for attachment in ss_most_recent_tax:
                attached_file = attachment.read()
                AttachmentEnv.sudo().create({
                            'name': attachment.filename,
                            'res_model': 'adm_uni.application',
                            'res_id': application_id.id,
                            'type': 'binary',
                            'datas_fname': attachment.filename,
                            'datas': base64.b64encode(attached_file),
                        }) 
        except AttributeError:
            pass 
                
        try:
            ss_other_revelants = file_parameters().getlist('ss_other_revelants')
            for attachment in ss_other_revelants:
                attached_file = attachment.read()
                AttachmentEnv.sudo().create({
                            'name': attachment.filename,
                            'res_model': 'adm_uni.application',
                            'res_id': application_id.id,
                            'type': 'binary',
                            'datas_fname': attachment.filename,
                            'datas': base64.b64encode(attached_file),
                        }) 
        except AttributeError:
            pass 
            
        self.set_contact_ids(application_id.id, params)
        self.set_language_ids(application_id.id, params)
        #contact_names    = post_parameters().getlist("txtContactName")
        #contact_id_names = post_parameters().getlist("txtContactIdName")
        #contact_ids      = post_parameters().getlist("other_contact_id")
        
        #languages       = post_parameters().getlist("selLanguage")
        #language_levels = post_parameters().getlist("selLanguageLevel")
        # language_ids    = post_parameters().getlist("other_contact_id")
        
        # Adding Languages
        #LanguageEnv = http.request.env["adm_uni.application.languages"]
        #for i, language in enumerate(languages):
        #    if language != "-1" and language_levels[i] != "-1":
        #        LanguageEnv.create({
        #            "language_id": language,
        #            "language_level_id": language_levels[i],
        #            "application_id":   application_id.id,
        #        })
        
        # Adding contact
        # OtherContactsEnv = http.request.env["adm_uni.application.other_contacts"]
        # for i, contact_name in enumerate(contact_names):
        #    if (len(contact_name.strip()) > 0 and
        #        len(contact_ids[i].strip()) > 0):
        #        
        #        OtherContactsEnv.create({
        #            "contact_name": contact_name,
        #            "contact_identification": contact_ids[i],
        #            "application_id":   application_id.id,
        #        })
        
        application_id.sudo().write({
            'letter_of_motivation_id': motivation_id,
            'cv_id': cv_id,
            'grade_transcript_id': grade_transcript_id,
            'letters_of_recommendation_id': letters_of_recommendation_id,
        })
        
        application_id.move_submitted_form()
        
#         PartnerEnv = http.request.env["res.partner"]
        
        contact_id.sudo().write({"is_in_application": True})
        
        return http.request.redirect('/admission-university/application')
