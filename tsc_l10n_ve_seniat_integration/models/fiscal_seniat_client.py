from odoo import models, api
import json

class FiscalSeniatClient(models.AbstractModel):
    _name = 'fiscal.seniat.client'
    _description = 'Servicio Adapter de Integración SENIAT'

    @api.model
    def build_invoice_payload(self, move):
        """
        Método base abstracto para construir el payload. 
        Módulos hijos (como l10n_ve_edi_tfhka) sobrescribirán esto.
        """
        payload = {
            "document_id": move.id,
            "document_number": move.fiscal_document_number,
            "total": move.amount_total,
            # Añadir más mapeos base aquí
        }
        return json.dumps(payload)

    @api.model
    def send_payload(self, payload):
        """
        Simula o realiza el envío al PAC/SENIAT.
        Retorna (success, response_data, error_message)
        """
        # Por defecto, modo simulación/abstracto
        return True, {"status": "accepted", "control_number": "CTRL-001"}, None
