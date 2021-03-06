# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from ..utils import formatting

from . import selection_options as sel_opt

status_types = [
    ("stage", "Stage"),
    ("submitted_form", "Submitted Form"),
    ("fact_integration", "Facts Integration"),
    ("cancelled", "Cancelled"),
    ("return_for_update", "Return for Update"),
]

ss_types = [
    ("merit", "Merit"),
    ("degree_program", "Degree Program"),
    ("both", "Both"),
]

class ApplicationStatus(models.Model):
    _name = "adm_uni.application.status"
    _order = "sequence"
    
    name = fields.Char(string="Status Name")
    description = fields.Text(string="Description")
    sequence = fields.Integer(readonly=True, default=-1)
    fold = fields.Boolean(string="Fold")
    type = fields.Selection(status_types, string="Type", default='stage')
    
    partner_id = fields.Many2one("res.partner", string="Customer")
    
    task_ids = fields.One2many("adm_uni.application.task", "status_id", "Status Ids")

    @api.model
    def create(self, values):
        next_order = self.env['ir.sequence'].next_by_code('sequence.application.task')

        values['sequence'] = next_order
        return super().create(values)


class Application(models.Model):
    _name = "adm_uni.application"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _read_group_status_ids(self, stages, domain, order):
        status_ids = self.env['adm_uni.application.status'].search([])
        return status_ids
    
    # Admission Information
    preferred_degree_program = fields.Many2one("adm_uni.degree_program",
                                               string="Preferred Degree Program")
    
    # Demographic
    name = fields.Char(string="Name", default="Undefined", readonly=True)
    first_name = fields.Char(string="First Name", default="")
    middle_name = fields.Char(string="Middle Name", default="")
    last_name = fields.Char(string="Last Name", default="")
    date_of_birth = fields.Date(string="Date of birth")
    gender = fields.Selection(sel_opt.genders, string="Gender")
    father_name = fields.Char("Father name")
    mother_name = fields.Char("Mother name")

    # Contact
    email = fields.Char(string="Email", related="partner_id.email", index=True)
    phone = fields.Char(string="Phone", related="partner_id.phone")
    other_contacts_ids = fields.One2many("adm_uni.application.other_contacts", "application_id", string="Other Contacts")
    
    # School
    current_school = fields.Char(string="Current School")
    current_school_address = fields.Char(string="Current School Address")
    
    previous_school = fields.Char(string="Previous School")
    previous_school_address = fields.Char(string="Previous School Address")
    
    gpa = fields.Float("GPA")
    cumulative_grades = fields.Float("Cumulative Grade")
    regional_exam_grade = fields.Char("Regional Grade")
    bac_grade = fields.Char("BAC Grade")

    # Scholarship information´
    merit_or_degree_ss = fields.Boolean("Merit or Degree scholarship")
    merit_or_degree_type = fields.Selection(ss_types,string="Type of scholarship")
    
    need_based_scholarship = fields.Boolean("Need-Based scholarship")
    
    # Skills
    language_ids = fields.One2many("adm_uni.application.languages", "application_id",
                                    string="Languages")
    
    # Location
    country_id = fields.Many2one("res.country", related="partner_id.country_id", string="Country")
    state_id = fields.Many2one("res.country.state", related="partner_id.state_id", string="State")
    city = fields.Char(string="City", related="partner_id.city")
    street_address = fields.Char(string="Street Address", related="partner_id.street")
    zip = fields.Char("zip", related="partner_id.zip")
    
    # Documentation
    letter_of_motivation_id = fields.Many2one("ir.attachment", string="Letter of motivation")
    cv_id = fields.Many2one("ir.attachment", string="C.V")
    grade_transcript_id = fields.Many2one("ir.attachment", string="Grade transcript")
    letters_of_recommendation_id = fields.Many2one("ir.attachment", string="Letter of recommendation")

    # Meta
    contact_time_id = fields.Many2one("adm_uni.contact_time",
                                   string="Preferred contact time")
    
    partner_id= fields.Many2one("res.partner", string="Contact")
    status_id = fields.Many2one("adm_uni.application.status",
                                string="Status", group_expand="_read_group_status_ids")
    task_ids = fields.Many2many("adm_uni.application.task")

    inquiry_id = fields.Many2one("adm_uni.inquiry")

    state_tasks = fields.One2many(string="State task", related="status_id.task_ids")

    status_type = fields.Selection(string="Status Type", related="status_id.type")
    forcing = False

    @api.multi
    def _move_to_status(self, status_name):
        status_id = False
        status_ids_ordered = self.env['adm_uni.application.status'].search([], order="sequence")
        for status in status_ids_ordered:
            if status.type == status_name:
                status_id = status
                break
        return self.write({
            'status_id': status_id.id,
        })
       

    def move_submitted_form(self):
        self._move_to_status("submitted_form")

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super().message_get_suggested_recipients() 
        try:
            for inquiry in self:
                if inquiry.email:
                    inquiry._message_add_suggested_recipient(recipients, partner=self.partner_id,email=inquiry.email, reason=_('Custom Email Luis'))
        except exceptions.AccessError:  # no read access rights -> just ignore suggested recipients because this imply modifying followers
            pass
        return recipients

    def force_back(self):
        status_ids_ordered = self.env['adm_uni.application.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index -= 1
        if index >= 0:
            next_status = status_ids_ordered[index]
            self.forcing = True
            self.status_id = next_status

    def force_next(self):
        status_ids_ordered = self.env['adm_uni.application.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index += 1
        if index < len(status_ids_ordered):
            next_status = status_ids_ordered[index]
            self.forcing = True
            self.status_id = next_status
    
    def move_to_next_status(self):
        self.forcing = False
        status_ids_ordered = self.env['adm_uni.application.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                # print("Encontrado! -> {}".format(index))
                break
            index += 1

        index += 1
        if index < len(status_ids_ordered):
            next_status = status_ids_ordered[index]

            if self.status_id.type == 'done':
                raise exceptions.except_orm(_('Application completed'), _('The Application is already done'))
            elif self.status_id.type == 'cancelled':
                raise exceptions.except_orm(_('Application cancelled'), _('The Application cancelled'))
            else:
                self.status_id = next_status

    def cancel(self):
        self._move_to_status("cancelled")
        #===============================================================================================================
        # status_ids_ordered = self.env['adm_uni.application.status'].search([], order="sequence")
        # for status in status_ids_ordered:
        #     if status.type == 'cancelled':
        #         self.status_id = status
        #         break
        #===============================================================================================================

    @api.onchange("first_name", "middle_name", "last_name")
    def _set_full_name(self):
        self.name = formatting.format_name(self.first_name, self.middle_name, self.last_name) 

    @api.onchange("country_id")
    def _onchange_country_id(self):
        res = {}
        if self.country_id:
            res['domain'] = {'state_id': [('country_id', '=', self.country_id.id)]}

    @api.model
    def create(self, values):
        first_status = self.env['adm_uni.application.status'].search([], order="sequence")[0]
        values['status_id'] = first_status.id
        values['name'] = formatting.format_name(values['first_name'], values['middle_name'], values['last_name']) 
        return super(Application, self).create(values)

    @api.multi
    def write(self, values):

        status_ids = self.env['adm_uni.application.status'].search([])

        partner_related_fields = dict()
        # "related" in self.fields_get()["email"]
        # Se puede hacer totalmente dinamico, no lo hago ahora por falta de tiempo
        # Pero sin embargo, es totalmente posible. 
        # Los no related directamente no tiene related, y los que si son
        # tiene el campo related de la siguiente manera: (model, field)
        # fields = self.fields_get()
        
        if "country" in values:
            partner_related_fields["country_id"] = values["country"]
        if "state" in values:
            partner_related_fields["state_id"] = values["state"]
        if "city" in values:
            partner_related_fields["city"] = values["city"]
        if "street_address" in values:
            partner_related_fields["street"] = values["street_address"]
        if "zipCode" in values:
            partner_related_fields["zip"] = values["zipCode"]
            
        self.partner_id.write(partner_related_fields)

        # print(status_ids)
        
        if "status_id" in values and not self.forcing:
            if not self.state_tasks & self.task_ids == self.state_tasks and self:
                raise exceptions.ValidationError("All task are not completed")
        else:
            self.forcing = False

        return super(Application, self).write(values)

    @api.multi
    def unlink(self):
        print("Borrado")
        return super(Application, self).unlink()

    # Mail integration
    # message_follower_ids

class ApplicationOtherContacts(models.Model):
    _name = "adm_uni.application.other_contacts"
    
    contact_name = fields.Char("Contact Name")
    contact_identification = fields.Char("Contact Identification")
    
    application_id = fields.Many2one("adm_uni.application", string="Application")
    

class ApplicationTasks(models.Model):
    _name = "adm_uni.application.task"

    name = fields.Char("Name")
    description = fields.Char("Description")
    status_id = fields.Many2one("adm_uni.application.status", string="Status")
    
    
class AdmissionApplicationLanguages(models.Model):
    _name = "adm_uni.application.languages"
    
    language_id = fields.Many2one("adm_uni.languages", string="Language")
    language_level_id = fields.Many2one("adm_uni.languages.level", string="Language Level")
    application_id = fields.Many2one("adm_uni.application", string="Application")

    
