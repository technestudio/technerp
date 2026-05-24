# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class AccountMoveLineWithHoldings(models.Model):
    _inherit = "account.move.line"

    tsc_cod_retencion_islr = fields.Char(string="ISLR withholding code")

    def get_withholding_context(self):
        self.ensure_one()
        data = {}

        if self.move_id.move_type not in {"in_invoice", "in_refund", "in_receipt"}:
            return data

        if self.move_id.invoice_tax_id:
            data["iva_tax_id"] = self.move_id.invoice_tax_id.id

        length = len(
            self.move_id.invoice_line_ids.filtered(
                lambda line: any(tax.withholding_type == "islr" for tax in line.tax_ids)
            )
        )

        if length > 0:
            data["islr_subtracting"] = self.move_id.subtracting / length

        return data

    def _convert_to_tax_base_line_dict(self):
        res = super()._convert_to_tax_base_line_dict()
        res["extra_context"].update(self.get_withholding_context())
        return res

    @api.depends(
        "tax_ids",
        "currency_id",
        "partner_id",
        "analytic_distribution",
        "balance",
        "partner_id",
        "move_id.partner_id",
        "move_id.invoice_tax_id",
        "price_unit",
        "quantity",
    )
    def _compute_all_tax(self):
        return super()._compute_all_tax()
