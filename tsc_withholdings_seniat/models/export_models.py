# -*- coding: utf-8 -*-

from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_tax_withholdings_export(self, withholding_type):
        ref = 'tsc_withholdings_seniat.action_tax_withholdings_%s_export' % withholding_type
        action = self.env.ref(ref).sudo().read([
            'binding_model_id', 'binding_type', 'binding_view_types',
            'display_name', 'name', 'res_model', 'target',
            'type', 'view_id', 'view_mode', 'views',
        ])[0]
        return dict(action, context={'default_invoice_ids': self.ids, "wizard": True})

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)

        if options.get("action_id") in {
            self.env['ir.model.data']._xmlid_to_res_id("account.action_move_in_invoice_type"),
            self.env['ir.model.data']._xmlid_to_res_id("account.action_move_in_refund_type"),
            self.env['ir.model.data']._xmlid_to_res_id("account.action_move_journal_line"),
        }:
            return res

        action_ids = {
            self.env['ir.model.data']._xmlid_to_res_id("tsc_withholdings_seniat.action_tax_withholdings_iva_export_wizard"),
            self.env['ir.model.data']._xmlid_to_res_id("tsc_withholdings_seniat.action_tax_withholdings_islr_export_wizard")
        }

        for view_type in ("list", "form"):
            if res["views"].get(view_type) and (toolbar := res['views'][view_type].get("toolbar")):
                    if "action" in toolbar:
                        toolbar["action"] = [
                            action for action in toolbar["action"]
                            if action["id"] not in action_ids
                        ]

        return res
