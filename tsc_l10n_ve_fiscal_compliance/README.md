# Manual de Uso: Configuración y Cumplimiento Fiscal (Core)

## Introducción
Este es el módulo principal que habilita la capa de cumplimiento de la Providencia Administrativa SNAT/2024/000121 del SENIAT en Odoo. 

## Configuración Inicial
1. Ve a **Ajustes > Compañías**.
2. En la pestaña de configuración de la compañía, ingresa el **RIF del SENIAT** y define el **Ambiente Fiscal** (Pruebas o Producción).
3. **Versiones Homologadas**: Ve al menú *Cumplimiento Fiscal > Versiones del Sistema*. Aquí el Administrador debe registrar el Hash del código fuente autorizado por el SENIAT. Si el código en producción no coincide con este Hash, el sistema bloqueará la emisión de documentos para evitar sanciones.

## Gestión de Accesos (Roles)
El módulo instala nuevos perfiles de seguridad:
- **Fiscal Administrator**: Control total de configuraciones, registro de proveedores y reglas de validación.
- **Fiscal Manager**: Puede gestionar y forzar transmisiones a la cola.
- **Fiscal Auditor**: Perfil de **solo lectura**. Destinado a los fiscales del SENIAT para auditar el sistema sin riesgo de manipulación de datos.
- **Fiscal User**: Perfil básico operativo para consulta de documentos.
