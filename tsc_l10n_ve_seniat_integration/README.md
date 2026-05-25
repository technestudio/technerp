# Manual de Uso: Integración y Transmisión SENIAT

## Introducción
Encargado de encolar y transmitir los documentos fiscales emitidos hacia el Proveedor Autorizado (PAC) o directamente a la API del SENIAT.

## Uso del Sistema de Colas
El proceso es 100% automático y asíncrono para no bloquear la operación de los cajeros o facturadores.
1. Al emitirse una factura, ésta pasa automáticamente a la **Cola de Transmisión** con estado *Pendiente*.
2. Un proceso programado (Cron Job) llamado **"SENIAT: Procesar Cola de Transmisión Fiscal"** se ejecuta cada 10 minutos. Toma todos los documentos pendientes y los envía al endpoint configurado.
3. **Manejo de Errores**: Si falla la conexión a internet o el servidor del PAC está caído, el estado cambia a *Fallido* y el sistema reintentará el envío en la próxima ejecución del Cron.

## Supervisión
Para revisar qué documentos no han podido transmitirse:
- Ve al menú *Cumplimiento Fiscal > Cola de Transmisión*.
- Podrás ver el estado en tiempo real (Pendiente, Enviado, Rechazado, Fallido).
- Los administradores tienen un botón para **Forzar Transmisión** de forma manual en caso de ser necesario.
