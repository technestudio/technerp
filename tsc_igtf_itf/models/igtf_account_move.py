# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class TscAccountMove(models.Model):

    _inherit = 'account.move'

    tsc_total_igtf = fields.Monetary(string="Total IGTF",
                                     help="Total IGTF associated with the invoice.",
                                     required=True,
                                     readonly=True,
                                     store=True,
                                     copy=False,
                                     default=0.00,
                                     currency_field='currency_id',
                                     compute="tsc_compute_igtf_amounts")

    tsc_supplier_total_igtf = fields.Monetary(string="Negative Total IGTF for Suppliers",
                                     help="Total IGTF associated with the invoice (Suppliers Only).",
                                     required=False,
                                     readonly=True,
                                     store=True,
                                     copy=False,
                                     default=0.00,
                                     currency_field='currency_id',
                                     compute="tsc_compute_igtf_amounts")

    tsc_total_with_igtf = fields.Monetary(string="Total with IGTF",
                                     help="Total amount of the invoice including the IGTF, corresponds to the total amount of the payment received for the invoice.",
                                     required=True,
                                     readonly=True,
                                     store=True,
                                     copy=False,
                                     default=0.00,
                                     currency_field='currency_id',
                                     compute="tsc_compute_igtf_amounts")

    tsc_config_igtf_text = fields.Html(string="IGTF text from settings", 
                                       store=True, 
                                       default=lambda self: self.tsc_default_config_igtf_text())

    @api.depends('amount_residual')
    def tsc_compute_igtf_amounts(self):  
        for record in self:
            if record.state == 'posted' and record.is_invoice(include_receipts=True):
                tsc_reconciled_partials = record._get_all_reconciled_invoice_partials()
                record.tsc_total_igtf = 0.0
                for line in tsc_reconciled_partials:
                    tsc_payment = line["aml"].env['account.payment'].search([('move_id', '=', line["aml"].move_id.id)], limit=1)
                    if tsc_payment and tsc_payment.tsc_with_igtf:
                        record.tsc_total_igtf += (
                            line["amount"]
                            * tsc_payment.tsc_igtf_payment_journal.tsc_igtf_percentage 
                            / 100
                        )

                record.tsc_supplier_total_igtf = -record.tsc_total_igtf  
                record.tsc_total_with_igtf = record.tsc_total_igtf + record.amount_total   

    def tsc_default_config_igtf_text(self):
        return self.env['ir.config_parameter'].sudo().get_param('tsc_igtf_itf.tsc_igtf_text')   

    def _synchronize_business_models(self, changed_fields):
        moves_to_sync = self.filtered(lambda m: not m.journal_id.tsc_is_igtf_journal)
        if moves_to_sync:
            super(TscAccountMove, moves_to_sync)._synchronize_business_models(changed_fields)



class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def reverse_moves(self, is_modify=False):
        self.ensure_one()
        moves = self.move_ids

        # Create default values.
        default_values_list = []
        for move in moves:
            default_values_list.append(self._prepare_default_reversal(move))
            if move.journal_id.tsc_is_igtf_journal:
                payment = move.env['account.payment'].search([('move_id', '=', move.id)], limit=1)
                if payment:
                    payment.tsc_clean_igtf_fields()

        batches = [
            [self.env['account.move'], [], True],   # Moves to be cancelled by the reverses.
            [self.env['account.move'], [], False],  # Others.
        ]
        for move, default_vals in zip(moves, default_values_list):
            is_auto_post = default_vals.get('auto_post') != 'no'
            is_cancel_needed = not is_auto_post and (is_modify or self.move_type == 'entry')
            batch_index = 0 if is_cancel_needed else 1
            batches[batch_index][0] |= move
            batches[batch_index][1].append(default_vals)

        # Handle reverse method.
        moves_to_redirect = self.env['account.move']
        for moves, default_values_list, is_cancel_needed in batches:
            new_moves = moves._reverse_moves(default_values_list, cancel=is_cancel_needed)
            moves._message_log_batch(
                bodies={move.id: _('This entry has been %s', reverse._get_html_link(title=_("reversed"))) for move, reverse in zip(moves, new_moves)}
            )

            if is_modify:
                moves_vals_list = []
                for move in moves.with_context(include_business_fields=True):
                    data = move.copy_data({'date': self.date})[0]
                    data['line_ids'] = [line for line in data['line_ids'] if line[2]['display_type'] == 'product']
                    moves_vals_list.append(data)
                new_moves = self.env['account.move'].create(moves_vals_list)

            moves_to_redirect |= new_moves

        self.new_move_ids = moves_to_redirect

        # Create action.
        action = {
            'name': _('Reverse Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }
        if len(moves_to_redirect) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': moves_to_redirect.id,
                'context': {'default_move_type':  moves_to_redirect.move_type},
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', moves_to_redirect.ids)],
            })
            if len(set(moves_to_redirect.mapped('move_type'))) == 1:
                action['context'] = {'default_move_type':  moves_to_redirect.mapped('move_type').pop()}
        return action




