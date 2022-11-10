from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    enable_whatsapp = fields.Boolean("Whatsapp Button")

    phone = fields.Char(
        "Whatsapp Number",
    )

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    enable_whatsapp = fields.Boolean(related='website_id.enable_whatsapp', readonly=False)
    
    phone = fields.Char(related='website_id.phone', readonly=False)