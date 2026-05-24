# -*- coding: utf-8 -*-

import csv
import io
import re
from base64 import b64encode
from functools import partial
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from lxml import etree
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

if TYPE_CHECKING:
    from typing import Callable

MISSING_VALUE = _("To define")


def _parse_float(
    number: float,
    ignore_zeros: bool = False,
    positive: bool = False,
    convert: "Callable | None" = None,
) -> str:
    if convert:
        number = convert(number)

    if positive:
        number = abs(number)

    number = round(number, 2)
    text = f"{number:.2f}"

    if ignore_zeros:
        return text.rstrip("0").rstrip(".")

    return text


def clean_string(string: str):
    text = "0"
    if isinstance(string, str):
        text = re.sub(r"[^a-zA-Z0-9]+", "", string).upper() or text
    return text


class TaxWithholdingsExportMixin(models.AbstractModel):
    _name = "tsc.tax.withholdings.export.mixin"
    _description = _("Mixin to export tax withholdings")

    def get_last_10_years(self):
        current_year = fields.Date.today().year
        years = range(current_year, current_year - 10, -1)
        return [(str(year),) * 2 for year in years]

    month = fields.Selection(
        selection=[
            ("01", _("January")),
            ("02", _("February")),
            ("03", _("March")),
            ("04", _("April")),
            ("05", _("May")),
            ("06", _("Juny")),
            ("07", _("July")),
            ("08", _("August")),
            ("09", _("September")),
            ("10", _("October")),
            ("11", _("November")),
            ("12", _("December")),
        ],
        string=_("Month"),
        required=True,
        default=lambda _: f"{fields.Date.today().month:02d}",
        help=_("Year of the declaration period"),
    )
    year = fields.Selection(
        selection=get_last_10_years,
        string=_("Year"),
        required=True,
        default=lambda _: str(fields.Date.today().year),
        help=_("Month of the declaration period"),
    )
    invoice_ids = fields.One2many(
        comodel_name="account.move",
        string=_("Invoices"),
        compute="_compute_invoice_ids",
    )

    @api.depends_context("default_invoice_ids")
    def _compute_invoice_ids(self):
        self.invoice_ids = self.env["account.move"].browse(
            self.env.context.get("default_invoice_ids")
        )

    def check_invoice_ids(self):
        if not self.env.company.vat:
            raise ValidationError(_("You must define the company VAT"))

        for invoice in self.invoice_ids:
            if invoice.state != "posted":
                raise ValidationError(_("You can only export posted invoices"))

            if not invoice.retained_subject_vat:
                raise ValidationError(
                    _("You must define the VAT of the retained subject")
                )

            if invoice.withholding_iva < 0.0 or invoice.withholding_islr < 0.0:
                if not invoice.invoice_control_number:
                    raise ValidationError(
                        _("You must define the invoice control number")
                    )

                if not invoice.reference_number:
                    raise ValidationError(
                        _("You must define the invoice reference number")
                    )

                if invoice.withholding_islr < 0.0 and not invoice.line_ids.filtered(
                    lambda line: (
                        not line.tax_line_id
                        and line.tsc_cod_retencion_islr
                        and line.tax_ids.filtered(
                            lambda tax: tax.withholding_type == "islr"
                        )
                    )
                ):
                    raise ValidationError(
                        _("You must define the ISLR withholding concept code")
                    )

    def action_export(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        name = self.get_filename()
        attachment_id = self.env["ir.attachment"].create(
            {
                "name": name,
                "store_fname": name,
                "datas": b64encode(self.generate_file()),
            }
        )
        download_url = f"/web/content/{attachment_id.id}?download=true"
        return {
            "type": "ir.actions.act_url",
            "url": urljoin(base_url, download_url),
            "target": "self",
        }

    @property
    def period(self) -> str:
        self.ensure_one()
        return f"{self.year}{self.month}"

    def get_filename(self) -> str:
        raise NotImplementedError("You must implement this method in your subclass")

    def generate_file(self) -> bytes:
        raise NotImplementedError("You must implement this method in your subclass")


class TaxWithholdingsIVAExport(models.TransientModel):
    _name = "tsc.tax.withholdings.iva.export"
    _description = _("Export to txt IVA withholding taxes")
    _inherit = "tsc.tax.withholdings.export.mixin"

    fortnight = fields.Selection(
        selection=[
            ("P", _("First")),
            ("S", _("Second")),
        ],
        string=_("Fortnight"),
        required=True,
        default=lambda _: "P" if fields.Date.today().day <= 15 else "S",
        help=_("Fortnight of the declaration period"),
    )

    def get_filename(self):
        period = self.period
        return f"TXT_RetencionesIVA_{self.fortnight}Q{period}.TXT"

    def generate_file(self):
        self.check_invoice_ids()

        with io.StringIO() as csv_file:
            writer = csv.writer(csv_file, delimiter="\t")

            base_currency = self.env.ref("base.VES")

            for invoice in self.invoice_ids:
                date = (
                    invoice.tsc_tax_withholding_date
                    or invoice.invoice_date
                    or invoice.date
                )

                currency_conversion = (
                    partial(
                        invoice.currency_id._convert,
                        to_currency=base_currency,
                        company=invoice.company_id,
                        date=invoice.invoice_date or invoice.date,
                    )
                    if invoice.currency_id != base_currency
                    else None
                )

                parse_float = partial(
                    _parse_float,
                    positive=True,
                    convert=currency_conversion,
                )

                is_debit_note = (
                    invoice.move_type in {"in_invoice", "out_invoice"}
                    and invoice.debit_origin_id.id
                )

                doc_type = "01"

                if is_debit_note:
                    doc_type = "02"
                elif invoice.move_type == "in_refund":
                    doc_type = "03"

                affected_document_number = "0"

                if (
                    invoice.move_type == "in_refund"
                    and invoice.reversed_entry_id
                    and invoice.reversed_entry_id.reference_number
                ):
                    affected_document_number = clean_string(
                        invoice.reversed_entry_id.reference_number
                    )
                elif is_debit_note:
                    affected_document_number = clean_string(
                        invoice.debit_origin_id.reference_number
                    )

                writer.writerow(
                    [
                        # RIF del Agente de Retención
                        clean_string(invoice.withholding_agent_vat),
                        # Periodo Impositivo
                        self.period,
                        # Fecha de Factura
                        date.strftime("%Y-%m-%d") if date else MISSING_VALUE,
                        # Tipo de Operación
                        "C",
                        # Tipo de documento
                        doc_type,
                        # RIF de Proveedor
                        clean_string(invoice.retained_subject_vat),
                        # Número de documento
                        (
                            invoice.reference_number
                            if invoice.reference_number
                            else MISSING_VALUE
                        ),
                        # Número de control
                        (
                            invoice.invoice_control_number
                            if invoice.invoice_control_number
                            else MISSING_VALUE
                        ),
                        # Monto total del documento
                        parse_float(invoice.amount_total_purchase),
                        # Base imponible
                        parse_float(
                            invoice.amount_total_iva
                            - invoice.amount_tax_iva
                            - invoice.vat_exempt_amount_iva
                        ),
                        # Monto de IVA retenido
                        parse_float(invoice.withholding_opp_iva),
                        # Número de documento afectado
                        affected_document_number,
                        # Numero del documento afectado
                        (
                            invoice.withholding_number
                            if invoice.sequence_withholding_iva
                            else MISSING_VALUE
                        ),
                        # Monto exento de IVA
                        parse_float(invoice.vat_exempt_amount_iva),
                        # Alícuota
                        _parse_float(
                            invoice.aliquot_iva,
                            positive=True,
                        ),
                        # Número de expediente
                        "0",
                    ]
                )
            return csv_file.getvalue().encode("utf-8")


class TaxWithholdingsISLRExport(models.TransientModel):
    _name = "tsc.tax.withholdings.islr.export"
    _description = _("Export to xml ISLR withholding taxes")
    _inherit = "tsc.tax.withholdings.export.mixin"

    def get_filename(self):
        return f"XML_relacionRetencionesISLR_{self.period}.xml"

    def generate_file(self):
        self.check_invoice_ids()

        tree = etree.Element(
            "RelacionRetencionesISLR",
            {
                "Periodo": self.period,
                "RifAgente": clean_string(self.env.company.vat),
            },
        )

        base_currency = self.env.ref("base.VES")

        for invoice in self.invoice_ids:
            date = (
                invoice.tsc_tax_withholding_date or invoice.invoice_date or invoice.date
            )

            detail = etree.SubElement(tree, "DetalleRetencion")
            etree.SubElement(detail, "RifRetenido").text = clean_string(
                invoice.retained_subject_vat
            )
            etree.SubElement(detail, "NumeroFactura").text = clean_string(
                invoice.reference_number
            )
            etree.SubElement(detail, "NumeroControl").text = clean_string(
                invoice.invoice_control_number
            )
            etree.SubElement(detail, "FechaOperacion").text = (
                date.strftime("%d/%m/%Y") if date else MISSING_VALUE
            )

            concept = "0"
            amount = "0.00"
            percentage = "0.00"

            if invoice.withholding_islr:
                concept = (
                    invoice.line_ids.filtered(
                        lambda line: (
                            not line.tax_line_id
                            and line.tsc_cod_retencion_islr
                            and line.tax_ids.filtered(
                                lambda tax: tax.withholding_type == "islr"
                            )
                        )
                    )
                    .sorted(key="amount_currency", reverse=True)[0]
                    .tsc_cod_retencion_islr
                )

                currency_conversion = (
                    partial(
                        invoice.currency_id._convert,
                        to_currency=base_currency,
                        company=invoice.company_id,
                        date=invoice.invoice_date or invoice.date,
                    )
                    if invoice.currency_id != base_currency
                    else None
                )

                amount = _parse_float(
                    (
                        invoice.amount_total_islr
                        - invoice.amount_tax_islr
                        - invoice.subtracting
                        - invoice.vat_exempt_amount_islr
                    ),
                    convert=currency_conversion,
                )
                percentage = _parse_float(invoice.withholding_percentage_islr)

            etree.SubElement(detail, "CodigoConcepto").text = concept
            etree.SubElement(detail, "MontoOperacion").text = amount
            etree.SubElement(detail, "PorcentajeRetencion").text = percentage

        return etree.tostring(
            tree, pretty_print=True, xml_declaration=True, encoding="ISO-8859-1"
        )
