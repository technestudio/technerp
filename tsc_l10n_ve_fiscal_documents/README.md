# Manual de Uso: Inalterabilidad de Facturación

## Introducción
Este módulo blinda los documentos contables (`account.move`) para garantizar su inalterabilidad, tal como exige la Providencia SNAT/2024/000121.

## ¿Cómo funciona?
1. **Emisión**: Al momento de confirmar (Publicar) una factura, nota de débito o nota de crédito, el sistema entra en modo "Bloqueo Fiscal".
2. **Generación del Hash (Blockchain)**: El sistema calcula matemáticamente un Hash SHA-256 único para la factura, encadenándolo con el Hash de la factura inmediatamente anterior. Esto previene que se altere el orden o se eliminen facturas intermedias.
3. **Restricciones de Modificación**:
   - Una vez publicada, el botón "Restablecer a Borrador" queda inhabilitado.
   - El botón "Cancelar" requerirá un proceso de anulación formal (Nota de Crédito) según dicte la normativa, bloqueando la cancelación directa.
   - **Eliminación bloqueada**: Odoo impedirá físicamente eliminar el registro de la base de datos, garantizando la conservación de los datos.

## Consulta
Los usuarios podrán ver en la vista de la factura una nueva pestaña "Datos Fiscales" que muestra el código Hash SHA-256 generado y el estado de la cadena.
