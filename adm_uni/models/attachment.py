# -*- coding: utf-8 -*-

from odoo import models, fields


class Attachments(models.Model):
    _inherit = "ir.attachment"

    inquiry_id = fields.Many2one("adm_uni.inquiry")