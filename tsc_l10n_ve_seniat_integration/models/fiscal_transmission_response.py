from odoo import models, fields

class FiscalTransmissionResponse(models.Model):
    _name = 'fiscal.transmission.response'
    _description = 'Respuesta de Transmisión Fiscal'
    
    queue_id = fields.Many2one('fiscal.transmission.queue', string='Transmission', required=True, ondelete='cascade')
    response_code = fields.Char(string='Response Code')
    response_message = fields.Text(string='Response Message')
    response_payload = fields.Text(string='Response Payload')
    seniat_tracking_number = fields.Char(string='SENIAT Tracking Number')
    accepted = fields.Boolean(string='Accepted')
    received_at = fields.Datetime(string='Received At', default=fields.Datetime.now)
    raw_response = fields.Text(string='Raw Response')
