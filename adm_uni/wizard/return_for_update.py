# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ReturnForUpdate(models.TransientModel):
    _name = "adm_uni.return.for.update"
    _description = "Return to module"

    
    @api.multi
    def send_to_return_for_update(self):
        application_ids = self.env['adm_uni.application'].browse(self.env.context.get('active_ids'))
        return application_ids._move_to_status('return_for_update')
