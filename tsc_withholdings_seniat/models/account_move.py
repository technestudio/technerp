# -*- coding: utf-8 -*-

from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

VAT_DEFAULT = 'XXXXX'


class AccountMoveWithHoldings(models.Model):
    _inherit = "account.move"

    invoice_tax_id = fields.Many2one(
        comodel_name='account.tax',
        string="VAT withholding",
        domain=[
            ("withholding_type", "=", "iva"),
            ("type_tax_use", "=", "purchase"),
            ("active", "=", True)
        ],
        required=False,
    )
    withholding_iva = fields.Monetary(
        string='VAT withholding ',
        store=True,
        compute='_compute_withholding',
        currency_field='company_currency_id'
    )
    withholding_islr = fields.Monetary(
        string='ISLR withholding ',
        store=True,
        compute='_compute_withholding',
        currency_field='company_currency_id'
    )
    withholding_islr_base = fields.Monetary(
        string='ISLR base withholding',
        store=True,
        compute='_compute_withholding',
        currency_field='company_currency_id'
    )
    sequence_withholding_iva = fields.Char(
        string="VAT withholding sequence",
        readonly=True,
        store=True,
        copy=False
    )
    sequence_withholding_islr = fields.Char(
        string="ISLR withholding sequence",
        readonly=True,
        store=True,
        copy=False
    )
    reference_number = fields.Char(
        string="Invoice number",
        copy=False
    )
    invoice_control_number = fields.Char(
        string="Invoice control number",
        copy=False
    )
    subtracting = fields.Monetary(
        string='Subtrahend',
        default=0.0,
        currency_field='company_currency_id'
    )

    # Fields to export
    withholding_agent_vat = fields.Char(
        string="RIF of the Withholding Agent",
        compute="_compute_fields_to_export",
        store=False,
        copy=False,
        readonly=True
    )
    retained_subject_vat = fields.Char(
        string="RIF of the Withholding Taxpayer",
        compute="_compute_fields_to_export",
        store=False,
        copy=False,
        readonly=True
    )
    withholding_number = fields.Char(
        string="Withholding number",
        compute="_compute_fields_to_export",
        store=False,
        copy=False,
        readonly=True
    )
    aliquot_iva = fields.Float(
        string="VAT rate",
        compute="_compute_fields_to_export",
        copy=False,
    )
    withholding_percentage_islr = fields.Float(
        string="Withholding percentage",
        compute="_compute_fields_to_export",
        copy=False,
    )
    withholding_code_islr = fields.Char(
        string="Withholding code",
        compute="_compute_fields_to_export",
        copy=False,
    )
    amount_tax_iva = fields.Monetary(
        string="Total taxes (VAT)",
        compute="_compute_fields_to_export",
        store=False,
        copy=False,
        readonly=True,
        currency_field='company_currency_id'
    )
    amount_tax_islr = fields.Monetary(
        string="Total taxes (ISLR)",
        compute="_compute_fields_to_export",
        store=False,
        copy=False,
        readonly=True,
        currency_field='company_currency_id'
    )
    amount_total_iva = fields.Monetary(
        string="Total less VAT withholdings",
        compute="_compute_fields_to_export",
        store=False,
        copy=False,
        readonly=True,
        currency_field='company_currency_id'
    )
    vat_exempt_amount_iva = fields.Monetary(
        string="VAT exempt amount",
        compute="_compute_fields_to_export",
        store=False,
        copy=False,
        readonly=True,
        currency_field='company_currency_id'
    )
    vat_exempt_amount_islr = fields.Monetary(
        string="Amount exempt from ISLR",
        compute="_compute_fields_to_export",
        store=False,
        copy=False,
        readonly=True,
        currency_field='company_currency_id'
    )
    amount_total_islr = fields.Monetary(
        string="Total less ISLR withholdings",
        compute="_compute_fields_to_export",
        store=False,
        copy=False,
        readonly=True,
        currency_field='company_currency_id'
    )
    amount_total_purchase = fields.Monetary(
        string="Total purchase",
        compute="_compute_fields_to_export",
        store=False,
        copy=False,
        readonly=True,
        currency_field='company_currency_id'
    )
    withholding_opp_iva = fields.Monetary(
        string='VAT withholding   ',
        compute="_compute_fields_to_export",
        store=False,
        copy=False,
        readonly=True,
        currency_field='company_currency_id'
    )
    withholding_opp_islr = fields.Monetary(
        string='Total retained',
        compute="_compute_fields_to_export",
        store=False,
        copy=False,
        readonly=True,
        currency_field='company_currency_id'
    )
    total_withheld = fields.Monetary(
        string='ISLR withholding',
        compute="_compute_fields_to_export",
        store=False,
        copy=False,
        readonly=True,
        currency_field='company_currency_id'
    )
    tsc_tax_withholding_date = fields.Date(
        string='Tax withholding date',
        help=(
            'Date on which the withholding taxes associated with the '
            'invoice are withheld. For the purposes of the withholding '
            'voucher, this corresponds to the date of issue'
        ),
        index=True,
        copy=True,
        tracking=True,
        default=fields.Date.context_today
    )

    withholding_iva_generated_by_payment_id = fields.Many2one(
        "account.payment",
        string="Payment that generated the VAT withholding",
        copy=False,
        readonly=True,
    )
    withholding_islr_generated_by_payment_id = fields.Many2one(
        "account.payment",
        string="Payment that generated the ISLR withholding",
        copy=False,
        readonly=True,
    )

    @api.constrains('reference_number', 'partner_id', 'move_type')
    def _check_reference_number_partner_id(self):
        for move in self:
            if move.reference_number:
                if self.search_count([
                    ('reference_number', '=', move.reference_number),
                    ('partner_id', '=', move.partner_id.id),
                    ('move_type', '=', move.move_type),
                    ('id', '!=', move.id)
                ]):
                    raise ValidationError(_(
                        'The Invoice Number is already registered in another document associated with this supplier. '
                        'Please verify the information'
                    ))

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)

        if options.get("action_id") in {
            self.env['ir.model.data']._xmlid_to_res_id("account.action_move_in_invoice_type"),
            self.env['ir.model.data']._xmlid_to_res_id("account.action_move_in_refund_type"),
            self.env['ir.model.data']._xmlid_to_res_id("account.action_move_journal_line"),
        }:
            return res

        print_ids = {
            self.env['ir.model.data']._xmlid_to_res_id("tsc_withholdings_seniat.report_tax_withholding_iva"),
            self.env['ir.model.data']._xmlid_to_res_id("tsc_withholdings_seniat.report_tax_withholding_islr")
        }

        action_ids = {
            self.env['ir.model.data']._xmlid_to_res_id("tsc_withholdings_seniat.action_tax_generate_withholding_iva"),
            self.env['ir.model.data']._xmlid_to_res_id("tsc_withholdings_seniat.action_tax_generate_withholding_islr")
        }

        for view_type in ("list", "form"):
            if res["views"].get(view_type) and (toolbar := res['views'][view_type].get("toolbar")):
                    if "action" in toolbar:
                        toolbar["action"] = [
                            action for action in toolbar["action"]
                            if action["id"] not in action_ids
                        ]
                    
                    if "print" in toolbar:
                        toolbar["print"] = [
                            action for action in toolbar["print"]
                            if action["id"] not in print_ids
                        ]

        return res

    @api.depends('subtracting', 'invoice_tax_id', 'amount_tax', 'line_ids', 'line_ids.tax_line_id')
    def _compute_withholding(self):
        for move in self:
            amount_total_withholding_iva = 0.0
            amount_total_withholding_islr = 0.0

            if move.is_purchase_document(True):
                for line in move.line_ids:
                    if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
                        if line.tax_line_id.withholding_type == "iva":
                            amount_total_withholding_iva += line.amount_currency
                        elif line.tax_line_id.withholding_type == "islr":
                            amount_total_withholding_islr += line.amount_currency

            move.withholding_iva = amount_total_withholding_iva
            move.withholding_islr_base = amount_total_withholding_islr - move.subtracting
            move.withholding_islr = amount_total_withholding_islr

    def validation_generation_withholding(self, label_value, label_sequence):
        is_one = len(self) == 1
        partner_id = None

        for move in self:
            if partner_id != move.partner_id.id:
                if partner_id is None:
                    partner_id = move.partner_id.id
                else:
                    raise ValidationError(_(
                        "Please select invoices from the same supplier "
                        "to generate the corresponding withholding tax"
                    ))

            if not is_one and move[label_sequence]:
                raise ValidationError(_(
                    "Please select only invoices that do not have such "
                    "withholdings already associated with them"
                ))

            if move.state != "posted" or not move[label_value]:
                raise ValidationError(_(
                    "Please select invoices that have information "
                    "to generate this type of withholding"
                ))

    def generate_withholding_iva(self):
        self.validation_generation_withholding("withholding_iva", "sequence_withholding_iva")
        if len(self) == 1:
            self._generate_withholding_iva()
        else:
            sequence_iva = False

            for move in self:
                if move.withholding_iva != 0.0 and not move.sequence_withholding_iva:
                    sequence_iva = self.env['ir.sequence'].next_by_code('account.move.withholding.iva')
                break

            for move in self:
                if move.withholding_iva != 0.0 and not move.sequence_withholding_iva and sequence_iva:
                    move.validation_generation_withholding("withholding_iva", "sequence_withholding_iva")
                    move.sequence_withholding_iva = sequence_iva

    def _generate_withholding_iva(self):
        if not self.sequence_withholding_iva:
            self.sequence_withholding_iva = self.env["ir.sequence"].next_by_code(
                "account.move.withholding.iva"
            )

    def generate_withholding_islr(self):
        self.validation_generation_withholding("withholding_islr", "sequence_withholding_islr")
        if len(self) == 1:
            self._generate_withholding_islr()
        else:
            sequence_islr = False

            for move in self:
                if move.withholding_islr != 0.0 and not move.sequence_withholding_islr:
                    sequence_islr = self.env['ir.sequence'].next_by_code('account.move.withholding.islr')
                break

            for move in self:
                if move.withholding_islr != 0.0 and not move.sequence_withholding_islr and sequence_islr:
                    move.validation_generation_withholding("withholding_islr", "sequence_withholding_islr")
                    move.sequence_withholding_islr = sequence_islr

    def _generate_withholding_islr(self):
        if not self.sequence_withholding_islr:
            self.sequence_withholding_islr = self.env["ir.sequence"].next_by_code(
                "account.move.withholding.islr"
            )

    def get_vat_withholding_detail(self) -> list[dict[str, float]]:
        self.ensure_one()
        assert self.is_purchase_document(True)

        amounts = ([], [])
        total = 0.0
        totals = defaultdict(float)

        for line in self.line_ids:
            if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
                if line.tax_line_id.withholding_type != 'islr' and not line.tax_line_id.disable_vat:
                    amounts[line.tax_line_id.withholding_type == 'iva'].append((
                        line.name,
                        line.tax_line_id.id,
                        line.tax_line_id.amount,
                        line.amount_currency
                    ))
            elif line.display_type in ('product', 'rounding') and line.quantity > 0.0:
                total += line.amount_currency
                for tax_id in line.tax_ids:
                    if not tax_id.withholding_type and not tax_id.disable_vat:
                        totals[tax_id.id] += line.amount_currency

        return [
            dict(
                aliquot=aliquot,
                amount_tax=vat,
                amount_withholding=self.direction_sign * abs(withholding),
                base_amount=totals[tax_id],
                exempt_amount=total - totals[tax_id],
            ) for (_, tax_id, aliquot, vat), (*_, withholding) in zip(*map(
                lambda a: sorted(a, key=lambda x: x[0]),
                amounts
            ))
        ]

    @api.depends(
        "invoice_tax_id",
        "subtracting",
        "sequence_withholding_iva",
        "sequence_withholding_islr",
        "withholding_iva",
        "withholding_islr"
    )
    def _compute_fields_to_export(self):
        self.withholding_agent_vat = self.env.company.vat and self.env.company.vat.upper() or VAT_DEFAULT

        for move in self:
            move.retained_subject_vat = move.partner_id.vat and move.partner_id.vat.upper() or VAT_DEFAULT

            # common
            amount_total_purchase = 0

            # vat
            withholding_iva = 0.0
            withholding_number = "0"
            aliquot_iva = set()
            amount_tax_iva = 0
            amount_total_iva = 0
            vat_exempt_amount_iva = 0

            # it
            withholding_islr = 0.0
            amount_tax_islr = 0
            amount_total_islr = 0
            withholding_percentage_islr = 0
            withholding_code_islr = ''
            vat_exempt_amount_islr = 0
            total_withheld = 0

            if move.is_purchase_document(True):
                total_tax, total_untaxed = 0.0, 0.0

                for line in move.line_ids:
                    if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
                        # Tax amount.
                        if line.tax_line_id.withholding_type == "iva":
                            withholding_iva += line.amount_currency

                        elif line.tax_line_id.withholding_type == "islr":
                            withholding_islr += line.amount_currency

                        elif not line.tax_line_id.disable_vat:
                            total_tax += line.amount_currency

                        if line.tax_line_id.amount != 0.0:
                            if (
                                not line.tax_line_id.withholding_type
                                and not line.tax_line_id.disable_vat
                            ):
                                aliquot_iva.add(line.tax_line_id.amount)

                            if (
                                withholding_percentage_islr == 0.0
                                and line.tax_line_id.withholding_type == "islr"
                            ):
                                withholding_percentage_islr = -line.tax_line_id.amount

                    elif line.display_type in ('product', 'rounding') and line.quantity > 0.0:
                        # Untaxed amount.
                        total_untaxed += line.amount_currency

                        if not line.tax_ids or not any(
                            tax.amount != 0.0 for tax in line.tax_ids
                            if not tax.withholding_type
                        ):
                            vat_exempt_amount_iva += line.amount_currency

                        if not line.tax_ids or not any(
                            tax.amount != 0.0 for tax in line.tax_ids
                            if tax.withholding_type == "islr"
                        ):
                            vat_exempt_amount_islr += line.amount_currency

                        if (
                            not withholding_code_islr
                            and line.tsc_cod_retencion_islr
                            and line.tax_ids.filtered(lambda tax: tax.withholding_type == 'islr')
                        ):
                            withholding_code_islr = line.tsc_cod_retencion_islr

                amount_total_purchase = total_untaxed + total_tax

                if withholding_iva != 0.0:
                    date = move.tsc_tax_withholding_date or move.invoice_date or move.date
                    withholding_number = f"{date:%Y%m}{move.sequence_withholding_iva:>08}"
                    amount_tax_iva = total_tax + withholding_iva
                    amount_total_iva = total_untaxed + amount_tax_iva

                if withholding_islr != 0.0:
                    total_withheld = withholding_islr - move.direction_sign * move.subtracting
                    amount_tax_islr = total_tax + total_withheld
                    amount_total_islr = total_untaxed + total_tax + withholding_islr

            move.withholding_opp_iva = withholding_iva
            move.withholding_opp_islr = withholding_islr
            move.amount_total_purchase = amount_total_purchase
            move.withholding_number = withholding_number
            move.aliquot_iva = sum(aliquot_iva)
            move.amount_tax_iva = amount_tax_iva
            move.amount_total_iva = amount_total_iva
            move.amount_tax_islr = amount_tax_islr
            move.amount_total_islr = amount_total_islr
            move.withholding_percentage_islr = withholding_percentage_islr
            move.withholding_code_islr = withholding_code_islr
            move.vat_exempt_amount_iva = vat_exempt_amount_iva
            move.vat_exempt_amount_islr = vat_exempt_amount_islr
            move.total_withheld = total_withheld

    @api.onchange("invoice_tax_id")
    def _onchange_invoice_tax(self):
        self._compute_tax_totals()

    def validate_subtracting(self):
        if abs(self.subtracting) > abs(self.withholding_islr_base):
            raise ValidationError(_(
                'The value of the ISLR Subtrahend must be less '
                'than or equal to the ISLR Withholding. Please change '
                'the value of the subtrahend to "0.00" if not applicable or '
                'to a value less than or equal to the withholding'
            ))

    @api.onchange("subtracting")
    def _onchance_subtracting(self):
        self.ensure_one()
        self._compute_tax_totals()
        self.validate_subtracting()

    @api.constrains('subtracting')
    def _check_subtracting(self):
        for move in self:
            move.validate_subtracting()

    def action_post(self):
        if self.filtered(lambda move: (
            move.move_type in {'in_invoice', 'in_refund', 'in_receipt'}
            and move.line_ids.filtered(
                lambda line: not line.tsc_cod_retencion_islr and any(
                    tax.withholding_type == 'islr' for tax in line.tax_ids
                )
            )
        )):
            raise ValidationError(
                _("Please, indicate the ISLR withholding code"))
        return super().action_post()

    def js_assign_outstanding_line(self, line_id):
        super().js_assign_outstanding_line(line_id)
        if self.move_type in {"in_invoice", "in_refund"}:
            if self.withholding_islr != 0.0:
                self.generate_withholding_islr()
            if self.withholding_iva != 0.0:
                self.generate_withholding_iva()
