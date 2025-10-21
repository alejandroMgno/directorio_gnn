Sistema de Directorio con Streamlit 

Descripción

Este proyecto es un sistema de directorio desarrollado con Streamlit que permite gestionar y visualizar información organizada, como ubicaciones, usuarios, contactos u otros datos relacionados.

Requisitos

Python 3.7 o superior instalado en el servidor.

Streamlit instalado (pip install streamlit).

Dependencias adicionales, por ejemplo, para manejar archivos Excel u otros formatos (openpyxl, polars):

pip install openpyxl polars


Puerto TCP 8501 abierto en el firewall de Windows.

Instalación

Copiar o clonar el proyecto en el servidor.
git clone https://github.com/alejandroMgno/directorio_gnn.git

Instalar las dependencias con:

pip install -r requirements.txt

(o instalar manualmente según necesidad)

Abrir el puerto 8501 en el firewall para permitir conexiones entrantes:

netsh advfirewall firewall add rule name="Streamlit 8501" dir=in action=allow protocol=TCP localport=8501 profile=domain,private,public

Uso

Para iniciar el sistema, ejecutar:

python -m streamlit run main_app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true


Accede desde cualquier navegador en la red local usando la IP del servidor, por ejemplo:

http://10.10.8.200:8501

Funcionalidades principales

Visualización de directorios y estructuras jerárquicas.

Gestión de datos vía carga de archivos (por ejemplo, Excel).

Filtros y búsquedas en la información.

Interfaz sencilla e interactiva gracias a Streamlit.

Mantenimiento y recomendaciones

Para mantener el sistema activo, configura su ejecución automática con un servicio Windows o tarea programada.

Protege la aplicación con controles de acceso si contiene información sensible.

Monitorea logs y estado del sistema regularmente.

Solución de problemas comunes

Módulo Streamlit no instalado:

pip install streamlit


Dependencia ‘openpyxl’ faltante para archivos Excel:

pip install openpyxl


Problemas de acceso remoto: verifica que el firewall permita el puerto 8501 y que el servidor esté escuchando (usar netstat).

Contacto

Para soporte o consultas:
Nombre: Jose Alejandro Rubio Mendoza
Correo: jarubio@gasnaturalindustrial.com.mx