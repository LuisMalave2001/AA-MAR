# -*- coding: utf-8 -*-
from odoo import http
from datetime import datetime
import base64
import logging


def get_parameters():
    return http.request.httprequest.args

def post_parameters():
    return http.request.httprequest.form

def file_parameters():
    return http.request.httprequest.files

_logger_ = logging.getLogger()

class Admission(http.Controller):
    
    def get_partner(self):
        return http.request.env["res.users"].browse([http.request.session.uid]).partner_id
    
    @http.route("/admission-university/application", auth="public", methods=["GET"], website=True)
    def admission_web(self, **params):
        contact_id = self.get_partner()       
        application_id = contact_id.uni_application_id
        
        if not application_id:
            return http.request.render('adm_uni.template_no_application_error')
        
        application_status_ids = http.request.env["adm_uni.application.status"].browse(http.request.env["adm_uni.application.status"].search([])).ids
        contact_time_ids = http.request.env["adm_uni.contact_time"].browse(http.request.env["adm_uni.contact_time"].search([])).ids
        degree_program_ids = http.request.env["adm_uni.degree_program"].browse(http.request.env["adm_uni.degree_program"].search([])).ids
        
        language_ids = http.request.env['adm_uni.languages'].browse(http.request.env['adm_uni.languages'].search([]))
        language_level_ids = http.request.env['adm_uni.languages.level'].browse(http.request.env['adm_uni.languages.level'].search([]))
        
        response = http.request.render('adm_uni.template_admission_application', {
            'contact_id': contact_id,
            'application_status_ids': application_status_ids,
            'language_ids': language_ids.ids,
            'language_level_ids': language_level_ids.ids,
            'contact_time_ids': contact_time_ids,
            'degree_program_ids': degree_program_ids,
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

    @http.route("/admission-university/application", auth="public", methods=["POST"], website=True, csrf=False)
    def add_admission(self, **params):
        
        contact_id = self.get_partner()
        application_id = contact_id.uni_application_id
        
        if not application_id:
            return http.request.render('adm_uni.template_no_application_error')
            
        if "txtMiddleName" not in params:
            params["txtMiddleName"] = ""
            
        # Personal Info
        gender = params["selGender"] if params["selGender"] else False
        father_name = params["txtFatherName"] if params["txtFatherName"] else False
        mother_name = params["txtMotherName"] if params["txtMotherName"] else False
        
        # School information
        previous_school = params["txtPreviousSchool"] if params["txtPreviousSchool"] else False
        gpa = params["txtGPA"] if params["txtGPA"] else False
        cumulative_grades = params["txtCumulativeGrade"] if params["txtCumulativeGrade"] else False
        regional_exam_grade = params["txtRegionalExam"] if params["txtRegionalExam"] else False
        bac_grade = params["txtBACGrade"] if params["txtBACGrade"] else False
         
        
        merit_or_degree_ss = params["want_scholarship"] if "want_scholarship" in params and params["want_scholarship"] else False
        merit_or_degree_type = params["scholarship_type"] if "scholarship_type" in params and params["scholarship_type"] else False
        need_based_scholarship = params["scholarship_considered"] if "scholarship_considered" in params and params["scholarship_considered"] else False
         
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
            
            'previous_school': previous_school,
            'gpa': gpa,
            'cumulative_grades': cumulative_grades,
            'regional_exam_grade': regional_exam_grade,
            'bac_grade': bac_grade,
            
            'merit_or_degree_ss': merit_or_degree_ss,
            'merit_or_degree_type': merit_or_degree_type,
            'need_based_scholarship': need_based_scholarship,
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
            
        
        contact_names = post_parameters().getlist("txtContactName")
        contact_ids    = post_parameters().getlist("txtContactId")
        
        languages = post_parameters().getlist("selLanguage")
        language_levels = post_parameters().getlist("selLanguageLevel")
        
        # Adding Languages
        LanguageEnv = http.request.env["adm_uni.application.languages"]
        for i, language in enumerate(languages):
            if language != "-1" and language_levels[i] != "-1":
                LanguageEnv.create({
                    "language_id": language,
                    "language_level_id": language_levels[i],
                    "application_id":   application_id.id,
                })
        
        # Adding contact
        OtherContactsEnv = http.request.env["adm_uni.application.other_contacts"]
        for i, contact_name in enumerate(contact_names):
            if (len(contact_name.strip()) > 0 and
                len(contact_ids[i].strip()) > 0):
                
                OtherContactsEnv.create({
                    "contact_name": contact_name,
                    "contact_identification": contact_ids[i],
                    "application_id":   application_id.id,
                })
        
        application_id.sudo().write({
            'letter_of_motivation_id': motivation_id,
            'cv_id': cv_id,
            'grade_transcript_id': grade_transcript_id,
            'letters_of_recommendation_id': letters_of_recommendation_id,
        })
        
        application_id.move_completed_form()
        
#         PartnerEnv = http.request.env["res.partner"]
        
        contact_id.sudo().write({"is_in_application": True})
        
        return http.request.redirect('/admission-university/application')
