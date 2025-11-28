🔍 Sistema de Ubicación de Contactos de Empleados
Aplicación profesional en Streamlit para búsqueda, localización y contacto rápido de empleados

Este sistema permite gestionar, unificar y consultar información de empleados proveniente de tres archivos independientes:

Ubicación (Nombre / Puesto / Departamento)

Correos electrónicos

Teléfonos

La aplicación integra estos datos, filtra inconsistencias, evita duplicados y permite contactar de forma inmediata vía WhatsApp o Correo, todo desde una interfaz web optimizada.

🚀 Características Principales
🔎 Búsqueda avanzada

Búsqueda por nombre, departamento, puesto, o cualquier palabra relacionada.

Soporta búsquedas múltiples: "JUAN PEREZ ventas gerente"

Resultados instantáneos con selector individual.

👤 Tarjetas de contacto

Cada empleado muestra:

Nombre

Puesto

Departamento

Teléfono

Correo

Botones rápidos:

📱 WhatsApp Directo (wa.me)

📧 Correo (mailto:)

🗂️ Gestión de archivos (modo administrador)

Sección protegida con contraseña (admin2021*+) que permite:

Cargar archivos de Ubicación / Correos / Teléfonos

Procesar y combinar datos

Limpiar caché

Reset completo del sistema

🔁 Carga automática

Si existen archivos previos en el directorio temporal, el sistema carga los datos automáticamente al iniciar.

⚙️ Aplicación estructurada con SOLID

El código implementa todos los principios SOLID:

SRP: Clases con responsabilidad única

OCP: Procesadores extensibles

LSP: Intercambio de manejadores sin romper el sistema

ISP: Interfaces específicas

DIP: Dependencias abstraídas y desacopladas

📁 Requisitos del Sistema
Archivos necesarios

Se requieren 3 archivos, en formato Excel o CSV:

Tipo	Encabezado esperado	Contenido mínimo
Ubicación	fila 2 (header=1)	Nombre, Puesto, Departamento
Correo	fila 1 (header=0)	Nombre, Correo
Teléfono	fila 1 (header=0)	Nombre, Teléfono
Libros y librerías utilizadas

Python 3.x

Streamlit

Pandas

Requests

OpenPyXL

urllib3

🛠️ Instalación
1️⃣ Clonar repositorio
git clone https://github.com/tu-repositorio/sistema-contactos-empleados.git
cd sistema-contactos-empleados

2️⃣ Crear entorno virtual (opcional)
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows

3️⃣ Instalar dependencias
pip install -r requirements.txt

4️⃣ Ejecutar la aplicación
streamlit run app.py

🧩 Estructura del Código

El proyecto está organizado en componentes claros, siguiendo SOLID:

EmployeeContactSystem
│
├── ConfigManager          # Configuración y directorios temporales
├── UIManager              # Estilos y configuración de interfaz
├── FileHandler            # Manejo de archivos temporales
├── FileDataProcessor      # Procesamiento de archivos Excel/CSV
├── ColumnCleaner          # Limpieza de encabezados
├── Contact Providers      # Ubicación / correo / teléfono
├── DataMerger             # Integración de datos entre proveedores
├── Searcher               # Búsqueda avanzada
├── PositionValidator      # Reglas para excluir directores
└── WhatsApp/Email URL     # Generadores de enlaces de contacto

🧪 Validaciones y Seguridad
✔️ Validaciones aplicadas

Limpieza completa de nombres y columnas

Filtrado de “directores” (excluye director pero no subdirector)

Normalización de teléfonos

Eliminación de valores nulos / vacíos

Verificación de encabezados y compatibilidad entre archivos

🔐 Seguridad

Modo administrador protegido por contraseña

Directorio temporal interno

Limpieza de archivos previa ante carga nueva

🖥️ Uso del Sistema
👨‍💼 Para los usuarios:

Escribir nombre / puesto / departamento

Seleccionar el empleado deseado

Usar las opciones:

📱 WhatsApp

📧 Correo

⚙️ Para administradores:

Abrir el panel “Administrar archivos”

Ingresar contraseña

Subir los 3 archivos

Presionar Actualizar Datos

📦 Exportar Resultados

La aplicación permite descargar resultados filtrados en CSV para reportes externos.

📌 Notas Importantes

El sistema solo integra empleados con:

Ubicación + (Correo o Teléfono)

Si un nombre aparece en ubicación pero no en correo ni teléfono → se descarta

El sistema se optimizó para organizaciones grandes (miles de empleados)

👨‍💻 Autor

Software desarrollado por GNN
Interfaz y motor de búsqueda optimizados para uso empresarial.