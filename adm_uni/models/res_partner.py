'''
Created on Feb 1, 2020

@author: LuisMora
'''
from ..utils import formatting
from odoo import models, fields, api

class ResPartnerExtended(models.Model):
    _inherit = ["res.partner"]
    
    uni_application_id = fields.Many2one("adm_uni.application", string="Application")
    uni_inquiry_id = fields.Many2one("adm_uni.inquiry", string="Inquiry")
    is_in_application = fields.Boolean("Is in Application?")

    first_name  = fields.Char("First Name")#, store=True, related="uni_application_id.first_name")
    middle_name = fields.Char("Middle Name")#, store=True, related="uni_application_id.first_name")
    last_name   = fields.Char("Last Name") #, store=True, related="uni_application_id.first_name")

    name = fields.Char(index=True, compute="_compute_name", store=True)

    @api.depends("first_name", "middle_name", "last_name")
    def _compute_name(self):
        for record in self:
            record.name = formatting.format_name(record.first_name, record.middle_name, record.last_name)

