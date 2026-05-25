from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for move in self:
            if move.fiscal_locked and move.fiscal_transmission_state == 'pending':
                self.env['fiscal.transmission.queue'].create_from_move(move)
        return res
