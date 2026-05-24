# -*- coding: utf-8 -*-

from collections import defaultdict
import inspect

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

VAT_DEFAULT = 'XXXXX'


class AccountTax(models.Model):
    _inherit = "account.tax"

    withholding_type = fields.Selection(
        selection=[
            ("iva", "VAT withholding"),
            ("islr", "ISLR withholding"),
        ],
        string="Type retention"
    )
    disable_vat = fields.Boolean(
        string="Disable VAT",
        help="If checked, the VAT withholding will not be calculated."
    )

    def _get_move_line_from_stack(self):
        """
        Introspect the stack to find the account.move.line involved in the computation.
        This allows us to retrieve the withholding context (iva_tax_id, islr_subtracting)
        without overriding account.move.line methods (_compute_totals, _compute_all_tax).
        """
        frame = inspect.currentframe()
        try:
            while frame:
                if 'line' in frame.f_locals:
                    line = frame.f_locals['line']
                    # We check for the _name attribute to ensure it is an Odoo model, 
                    # and specifically account.move.line to correspond with the expected variable in _compute_totals
                    if hasattr(line, '_name') and line._name == 'account.move.line':
                        return line
                frame = frame.f_back
        finally:
            del frame
        return None

    def compute_all(
        self, price_unit,
        currency=None, quantity=1.0, product=None, partner=None,
        is_refund=False, handle_price_include=True, include_caba_tags=False,
        fixed_multiplicator=1
    ):
        res = super().compute_all(
            price_unit, currency, quantity,
            product, partner, is_refund,
            handle_price_include, include_caba_tags,
            fixed_multiplicator
        )

        if not product or not res['taxes'] or quantity <= 0.0:
            return res

        # Try to get context data from self._context first (backward compatibility or explicit overwrite)
        iva_tax_id_id = self._context.get('iva_tax_id')
        subtracting = self._context.get('islr_subtracting')

        # If not present in context, look up the stack for the account.move.line
        if not iva_tax_id_id and subtracting is None:
            line = self._get_move_line_from_stack()
            if line:
                # Use the method defined in account.move.line to get the needed data
                # We assume get_withholding_context returns a dict with 'iva_tax_id' and 'islr_subtracting'
                ctx_data = line.get_withholding_context()
                iva_tax_id_id = ctx_data.get('iva_tax_id')
                subtracting = ctx_data.get('islr_subtracting', 0.0)

        # Ensure defaults if we still didn't find anything
        if subtracting is None: 
            subtracting = 0.0

        iva_tax_id = self.env["account.tax"].browse(iva_tax_id_id) if iva_tax_id_id else None
        
        # Compute VAT
        tax_base_amount = defaultdict(float)

        for data_tax in res['taxes']:
            tax_id = self.filtered(lambda t: t.id == data_tax["id"])

            if iva_tax_id and tax_id.withholding_type not in {"iva", "islr"} and not tax_id.disable_vat:
                tax_base_amount[tax_id] += data_tax["amount"]

            elif subtracting is not None and tax_id.withholding_type == "islr":
                data_tax["amount"] += fixed_multiplicator * subtracting

        if sum(tax_base_amount.values()) == 0.0:
            return res
        
        tax_repartition_lines = (
            is_refund
            and iva_tax_id.refund_repartition_line_ids
            or iva_tax_id.invoice_repartition_line_ids
        )
        tax_repartition_lines_refs = {
            line.id: line.vat_tax_id
            for line in tax_repartition_lines
            if line.vat_tax_id and line.vat_tax_id in tax_base_amount
        }

        for tax_id, amount in tax_base_amount.items():
            vat_tax_summary = iva_tax_id.compute_all(
                amount,
                currency,
                partner=partner,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
                include_caba_tags=include_caba_tags,
                fixed_multiplicator=fixed_multiplicator,
            )

            vat_tax_amount = sum(tax["amount"] for tax in vat_tax_summary["taxes"])
            if vat_tax_amount == 0.0:
                continue

            # Merge
            for base_tags in vat_tax_summary["base_tags"]:
                if base_tags not in res["base_tags"]:
                    res["base_tags"].append(base_tags)

            if tax_repartition_lines_refs:
                try:
                    tax_temp = next(
                        tax for tax in vat_tax_summary["taxes"]
                        if tax_repartition_lines_refs.get(tax["tax_repartition_line_id"]) == tax_id
                    ).copy()
                except StopIteration as error:
                    raise ValidationError(
                        _("You must correctly configure the withholding repartition lines")
                    ) from error

                tax_temp["name"] = f"{tax_temp['name']} ({tax_id.name})"
                tax_temp["amount"] = vat_tax_amount

                res["taxes"].append(tax_temp)
            else:
                res["taxes"].extend(vat_tax_summary["taxes"])

            res["total_included"] += vat_tax_amount

        return res

    @api.constrains('refund_repartition_line_ids', 'repartition_line_ids')
    def _validate_unique_vat_tax_by_repartition_line(self):
        for tax in self:
            irls = tax.invoice_repartition_line_ids.filtered("vat_tax_id").mapped(
                lambda t: t.vat_tax_id.id
            )
            rrls = tax.refund_repartition_line_ids.filtered("vat_tax_id").mapped(
                lambda t: t.vat_tax_id.id
            )

            if len(irls) != len(set(irls)) or len(rrls) != len(set(rrls)):
                raise ValidationError(_("The VAT tax must be unique by repartition line."))


class AccountTaxRepartitionLine(models.Model):
    _inherit = "account.tax.repartition.line"

    vat_tax_id = fields.Many2one(
        comodel_name="account.tax",
        string="Associated VAT Tax",
        domain=[
            ("type_tax_use", "=", "purchase"),
            ("withholding_type", "=", False),
            ("disable_vat", "=", False),
            ("amount", ">", 0.0),
        ],
        help="Select the VAT tax to apply."
    )
