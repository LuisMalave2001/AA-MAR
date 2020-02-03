# -*- coding: utf-8 -*-
from odoo import models, fields

class AdmissionPreferredContactTime(models.Model):
    _name = "adm_uni.contact_time"
    
    name = fields.Char("Name")
    from_time = fields.Float("From Time")
    to_time = fields.Float("To Time")