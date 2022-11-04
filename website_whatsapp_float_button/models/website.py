from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    enable_whatsapp = fields.Boolean("Whatsapp Button")

    phone = fields.Char(
        "Whatsapp Number",
    )
