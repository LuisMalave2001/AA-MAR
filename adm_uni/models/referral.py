# -*- coding: utf-8 -*-

from odoo import fields, models

class Referrals(models.Model):

    _name = "adm_uni.referral"
    _description = "A referral for application form"

    name = fields.Char("Referral", required=True, translate=True)
    translatable_name = fields.Char("Referral Translate", required=True, translate=True)