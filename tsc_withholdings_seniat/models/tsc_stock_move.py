# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TscStockMove(models.Model):
    
    _inherit = 'stock.move'
    
    def _adjust_unit_price(self, precio):
        for record in self:
            product_line_uom = record.product_uom
            product_storage_uom = record.product_id.uom_id

            # Verificar si las unidades de medida son distintas
            if product_line_uom != product_storage_uom:
                # Verificar si alguna de las unidades es de tipo "unidad de medida de referencia"
                if product_line_uom.uom_type == 'reference' or product_storage_uom.uom_type == 'reference':
                    # Una conversión

                    # De acuerdo a la unidad de medida de la línea de movimiento se ajusta el precio
                    if product_line_uom.uom_type == 'reference':
                        factor_inv = product_storage_uom.factor_inv
                        uom_type = product_storage_uom.uom_type

                        if uom_type == 'bigger':
                            precio = precio / factor_inv
                        elif uom_type == 'smaller':
                            precio = precio * factor_inv

                    # De acuerdo a la unidad de medida de almacenamiento se ajusta el precio
                    elif product_storage_uom.uom_type == 'reference':
                        factor_inv = product_line_uom.factor_inv
                        uom_type = product_line_uom.uom_type

                        if uom_type == 'bigger':
                            precio = precio * factor_inv
                        elif uom_type == 'smaller':
                            precio = precio / factor_inv

                else:
                    # Doble conversión
                    # Convertimos el precio a la unidad de medida de almacenamiento
                    factor_inv_storage = product_storage_uom.factor_inv
                    precio = precio / factor_inv_storage if product_storage_uom.uom_type == 'bigger' else precio * factor_inv_storage

                    # Convertimos el precio a la unidad de medida de la línea de movimiento
                    factor_inv_line = product_line_uom.factor_inv
                    precio = precio / factor_inv_line if product_line_uom.uom_type == 'smaller' else precio * factor_inv_line

            return precio



    