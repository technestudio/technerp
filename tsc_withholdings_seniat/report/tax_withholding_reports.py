# -*- coding: utf-8 -*-

from datetime import datetime
from functools import partial
from itertools import groupby

from odoo import _, api, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Datetime
from odoo.tools.misc import formatLang


class QueryDict(dict):
    def __getattr__(self, attr):
        try:
            return self.__getitem__(attr)
        except KeyError:
            return super(QueryDict, self).__getattr__(attr)

    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)


class MixinTaxWithholdingReport(models.AbstractModel):
    _name = "report.tsc_withholdings_seniat.mixin"
    _description = "Tax Withholding Mixin Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        objs = self.env["account.move"].browse(docids)
        return {
            "f": partial(formatLang, self.env),
            "data": self.get_data(objs),
            "now": self.now(),
        }

    def validate_record(self, record):
        if not record.invoice_date:
            raise ValidationError(
                _("Invoice/Reimbursement date is required to validate this document")
            )

        if not record.reference_number:
            raise ValidationError(_("Withholding requires the Invoice Number"))

        if not record.invoice_control_number:
            raise ValidationError(_("Withholding requires the Invoice Control Number"))

        if not record.partner_id:
            raise ValidationError(_("Withholding requires the Supplier"))

    def now(self):
        return Datetime.context_timestamp(self, datetime.now())

    _name_data_default = (
        "company_name",
        "company_vat",
        "vendor_name",
        "vendor_vat",
        "accounting_date",
        "tsc_tax_withholding_date",
        "number_withholding",
        "company_street",
    )

    def _funckey(self, value: dict):
        return tuple(value.get(name) for name in self._name_data_default)

    def extract_data_by_default(self, record):
        return {
            "company_name": self.env.company.name.upper(),
            "company_vat": record.withholding_agent_vat,
            "vendor_name": record.partner_id.name.upper(),
            "vendor_vat": record.retained_subject_vat,
            "invoice_date": record.invoice_date,
            "accounting_date": (
                record.tsc_tax_withholding_date
                or record.invoice_date
                or self.now()
            ),
            "tsc_tax_withholding_date": record.tsc_tax_withholding_date,
            "invoice_control_number": record.invoice_control_number or "N/A",
            "reference_number": (
                record.reference_number
                or (record.name if record.state == "posted" else _("To be defined"))
            ),
        }

    def extract_data(self, record, defaults):
        raise NotImplementedError("You must implement this method in your report")

    def get_validated_data(self, record):
        self.validate_record(record)
        defaults = self.extract_data_by_default(record)
        data = self.extract_data(record, defaults) or {}
        data.update(defaults)
        return QueryDict(data)

    def get_data(self, records):
        return [
            QueryDict(zip(self._name_data_default, index), invoices=list(values))
            for index, values in groupby(
                sorted(map(self.get_validated_data, records), key=self._funckey),
                self._funckey,
            )
        ]

    def convert_currency(self, record):
        withholding_currency = self.env.ref("base.VES")
        if record.currency_id == withholding_currency:
            return lambda x: x
        return partial(
            record.currency_id._convert,
            to_currency=withholding_currency,
            company=self.env.company,
            date=record.invoice_date or record.date,
        )


class TaxWithholdingIVAReport(models.AbstractModel):
    _name = "report.tsc_withholdings_seniat.template_tax_withholding_iva"
    _description = "Tax Withholding IVA Report"
    _inherit = "report.tsc_withholdings_seniat.mixin"

    def extract_data(self, record, defaults):
        c = self.convert_currency(record)

        is_debit_note = (
            record.move_type in {"in_invoice", "out_invoice"}
            and record.debit_origin_id.id
        )

        invoice_number = ""
        debit_note_number = ""
        credit_note_number = ""
        affected_invoice = ""
        transaction_type = "RET"

        if is_debit_note:
            transaction_type = "02 Registro"
            debit_note_number = defaults["reference_number"]
            affected_invoice = record.debit_origin_id.reference_number or ""

        elif record.move_type == "in_invoice":
            transaction_type = "01 Registro"
            invoice_number = defaults["reference_number"]
        
        elif record.move_type == "in_refund":
            transaction_type = "03 Registro"
            credit_note_number = defaults["reference_number"]

            if record.reversed_entry_id:
                affected_invoice = record.reversed_entry_id.reference_number

        data = {
            "amount_base": c(
                record.amount_total_iva
                - record.amount_tax_iva
                - record.vat_exempt_amount_iva
            ),
            "amount_total": c(record.amount_total_iva),
            "vat_exempt_amount": c(record.vat_exempt_amount_iva),
            "total_purchase": c(record.amount_total_purchase),
            "move_type": record.move_type,
            "invoice_number": invoice_number,
            "debit_note_number": debit_note_number,
            "credit_note_number": credit_note_number,
            "transaction_type": transaction_type,
            "affected_invoice": affected_invoice,
        }

        data["number_withholding"] = (
            record.withholding_number
            if record.sequence_withholding_iva
            else _("To be defined")
        )

        data["company_street"] = (
            " ".join([self.env.company.street or "", self.env.company.street2 or ""])
            .upper()
            .strip()
        )

        data["amounts"] = [
            QueryDict(
                {
                    name: c(value) if name != "aliquot" else value
                    for name, value in detail.items()
                }
            )
            for detail in record.get_vat_withholding_detail()
        ]

        return data

    def validate_record(self, record):
        super().validate_record(record)
        if not record.withholding_iva:
            raise UserError(_("This invoice has no withholding tax"))


class TaxWithholdingISLRReport(models.AbstractModel):
    _name = "report.tsc_withholdings_seniat.template_tax_withholding_islr"
    _description = "Tax Withholding ISLR Report"
    _inherit = "report.tsc_withholdings_seniat.mixin"

    def extract_data(self, record, defaults):
        c = self.convert_currency(record)

        data = {
            "amount_base": c(
                record.amount_total_islr
                - record.amount_tax_islr
                - record.subtracting
                - record.vat_exempt_amount_islr
            ),
            "amount_total": c(record.amount_total_islr),
            "amount_withholding": c(-record.withholding_opp_islr),
            "total_purchase": c(record.amount_total_purchase),
            "percentage": record.withholding_percentage_islr,
            "subtracting": c(record.subtracting),
            "total_withheld": c(-record.total_withheld),
            "code": record.withholding_code_islr,
        }

        if record.sequence_withholding_islr:
            date = record.date or record.invoice_date
            data["number_withholding"] = (
                f"{date:%Y%m}{record.sequence_withholding_islr:>08}"
            )
        else:
            data["number_withholding"] = _("To be defined")

        return data

    def validate_record(self, record):
        super().validate_record(record)

        if not record.withholding_code_islr:
            raise ValidationError(_("Withholding requires the Withholding Code"))

        if not record.withholding_islr:
            raise UserError(_("This invoice has no withholding tax"))
