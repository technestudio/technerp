from odoo import models, api

class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    @api.ondelete(at_uninstall=False)
    def _unlink_except_used_fiscal(self):
        # Logica opcional para prohibir borrado de secuencias ya consumidas
        pass
