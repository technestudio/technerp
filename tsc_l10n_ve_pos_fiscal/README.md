# Manual de Uso: Punto de Venta Fiscal (POS)

## Introducción
Extiende las estrictas reglas de inalterabilidad fiscal hacia las terminales de Punto de Venta de Odoo.

## Operativa de Caja (Tickets)
- **Cálculo de Hash por Ticket**: Cada ticket (`pos.order`) validado por el cajero recibe un Hash SHA-256 y queda permanentemente bloqueado contra modificaciones en el backend.
- La experiencia del cajero es idéntica; todo el blindaje de seguridad ocurre en segundo plano de manera imperceptible.

## Cierre de Caja (Reporte Z)
- Al momento de realizar el "Cierre de Sesión" del POS (`pos.session`), el sistema consolida automáticamente el total de ventas gravadas, ventas exentas y los impuestos recaudados durante el turno.
- Estos totales se almacenan en un bloque resumen inalterable dentro de la sesión de caja, simulando el funcionamiento de una memoria fiscal de máquina registradora o un Reporte Z digital, vital para la inspección fiscal.
