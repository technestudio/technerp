from odoo import models, fields, api, _

class FiscalTransmissionQueue(models.Model):
    _name = 'fiscal.transmission.queue'
    _description = 'Cola de Transmisión Fiscal'
    _order = 'create_date desc'
    
    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    move_id = fields.Many2one('account.move', string='Fiscal Document', required=True, ondelete='cascade')
    document_type = fields.Selection([
        ('invoice', 'Factura'),
        ('credit_note', 'Nota de Crédito'),
        ('debit_note', 'Nota de Débito'),
        ('annulment', 'Anulación')
    ], string='Document Type', required=True)
    
    payload = fields.Text(string='Payload (JSON/XML)')
    payload_hash = fields.Char(string='Payload Hash')
    
    state = fields.Selection([
        ('pending', 'Pending'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='pending', tracking=True)
    
    attempt_count = fields.Integer(string='Attempts', default=0)
    max_attempts = fields.Integer(string='Max Attempts', default=3)
    last_attempt_at = fields.Datetime(string='Last Attempt At')
    next_attempt_at = fields.Datetime(string='Next Attempt At')
    
    response_ids = fields.One2many('fiscal.transmission.response', 'queue_id', string='Responses')
    error_message = fields.Text(string='Last Error Message')
    company_id = fields.Many2one('res.company', string='Company', related='move_id.company_id', store=True)

    @api.depends('move_id')
    def _compute_name(self):
        for record in self:
            record.name = f"TX-{record.move_id.fiscal_document_number or record.move_id.name}"

    @api.model
    def create_from_move(self, move):
        doc_type = 'invoice'
        if move.move_type == 'out_refund':
            doc_type = 'credit_note'
        
        # Obtenemos el payload usando el adapter genérico
        client = self.env['fiscal.seniat.client']
        payload = client.build_invoice_payload(move)
        
        return self.create({
            'move_id': move.id,
            'document_type': doc_type,
            'payload': payload,
            'state': 'pending'
        })
        
    def action_transmit(self):
        client = self.env['fiscal.seniat.client']
        for record in self.filtered(lambda r: r.state in ('pending', 'failed') and r.attempt_count < r.max_attempts):
            record.state = 'sending'
            record.attempt_count += 1
            record.last_attempt_at = fields.Datetime.now()
            try:
                success, response_data, error = client.send_payload(record.payload)
                if success:
                    record.state = 'accepted'
                    record.move_id.fiscal_transmission_state = 'accepted'
                    record.move_id.fiscal_status = 'transmitted'
                    self.env['fiscal.transmission.response'].create({
                        'queue_id': record.id,
                        'response_code': '200',
                        'response_message': 'Success',
                        'accepted': True,
                        'raw_response': str(response_data)
                    })
                else:
                    record.state = 'rejected'
                    record.move_id.fiscal_transmission_state = 'rejected'
                    record.error_message = error
                    self.env['fiscal.transmission.response'].create({
                        'queue_id': record.id,
                        'response_code': '500',
                        'response_message': error,
                        'accepted': False,
                        'raw_response': str(response_data)
                    })
            except Exception as e:
                record.state = 'failed'
                record.error_message = str(e)
                
    @api.model
    def _cron_process_transmission_queue(self):
        records = self.search([
            ('state', 'in', ['pending', 'failed']),
            ('attempt_count', '<', 3)
        ], limit=50)
        records.action_transmit()
