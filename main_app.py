import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import re
from io import BytesIO
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import os
import tempfile

# Desactivar warnings de SSL para desarrollo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración de la página con layout más ancho
st.set_page_config(
    page_title="Sistema de Ubicación de Contactos de Empleados",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado MEJORADO
st.markdown("""
    <style>
    /* Reducir márgenes principales al mínimo */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
    }
    
    /* Botones más compactos */
    .stButton button {
        width: 100%;
        margin: 0.1rem 0 !important;
        padding: 0.25rem 0.5rem !important;
    }
    
    /* Inputs más compactos */
    .stTextInput input {
        padding: 0.25rem 0.5rem !important;
        margin: 0.1rem 0 !important;
        font-size: 12px !important;
    }
    
    /* Dataframes más compactos */
    .dataframe {
        width: 100% !important;
        margin: 0.25rem 0 !important;
        font-size: 1px !important;
    }
    
    /* Reducir espacio entre elementos */
    .element-container {
        padding: 0.1rem 0 !important;
        margin: 0.1rem 0 !important;
    }
    
    /* Ajustar el ancho máximo del contenido principal */
    .main .block-container {
        max-width: 99vw !important;
    }
    
    /* Botones de acción personalizados MEJORADOS */
    .action-btn {
        border: none !important;
        padding: 12px 20px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        width: 100% !important;
        font-size: 14px !important;
        font-weight: bold !important;
        text-decoration: none !important;
        display: inline-block !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        margin: 0.2rem 0 !important;
    }
    
    .action-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    .whatsapp-btn {
        background: linear-gradient(135deg, #25D366, #128C7E) !important;
        color: white !important;
    }
    
    .email-btn {
        background: linear-gradient(135deg, #EA4335, #D14836) !important;
        color: white !important;
    }
    
    .disabled-btn {
        background-color: #f0f0f0 !important;
        color: #999 !important;
        cursor: not-allowed !important;
    }
    
    /* Mejoras para las tarjetas de contacto */
    .contact-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #007bff;
        border: 1px solid #e0e0e0;
    }
    
    /* Animaciones suaves */
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Contenedor con scroll para la lista de empleados */
    .employee-list-container {
        max-height: 60vh;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background: #fafafa;
    }
    
    /* Footer fijo */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: black;
        color: white;
        text-align: center;
        padding: 0.5rem;
        font-size: 14px;
        font-weight: bold;
        z-index: 1000;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    
    /* Espacio para el footer */
    .main .block-container {
        padding-bottom: 3rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Footer fijo
st.markdown(
    '<div class="footer">Software desarrollado por GNN</div>',
    unsafe_allow_html=True
)

# Configuración
PASSWORD = "admin2021*+"
TEMP_DIR = "temp_archivos"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Cache para mejorar rendimiento
@st.cache_data(ttl=3600)
def cargar_archivo(uploaded_file, header_row=0):
    """Carga un archivo Excel optimizado"""
    try:
        if uploaded_file is not None:
            df = pd.read_excel(
                uploaded_file, 
                header=header_row, 
                engine='openpyxl',
                dtype=str
            )
            
            # Limpiar nombres de columnas
            df.columns = clean_column_names(df.columns)
            
            # Eliminar filas completamente vacías
            df = df.dropna(how='all')
            
            return df
    except Exception as e:
        st.error(f"❌ Error al cargar archivo: {str(e)}")
    return None

@st.cache_data
def cargar_archivo_desde_ruta(file_path, header_row=0):
    """Carga archivo desde ruta"""
    try:
        if file_path and os.path.exists(file_path):
            df = pd.read_excel(
                file_path, 
                header=header_row, 
                engine='openpyxl',
                dtype=str
            )
            
            df.columns = clean_column_names(df.columns)
            df = df.dropna(how='all')
            
            return df
    except Exception as e:
        st.error(f"❌ Error al cargar archivo desde {file_path}: {str(e)}")
    return None

def clean_column_names(columns):
    """Limpia nombres de columnas de forma eficiente"""
    cleaned = []
    for col in columns:
        if pd.isna(col):
            cleaned.append('columna_desconocida')
            continue
            
        col_str = str(col).strip().lower()
        col_str = re.sub(r'[^\w\s]', '', col_str)
        col_str = re.sub(r'\s+', '_', col_str)
        cleaned.append(col_str or 'columna_sin_nombre')
    
    return cleaned

def encontrar_columna_clave(df, posibles_nombres):
    """Encuentra columnas clave optimizado"""
    if df is None or df.empty:
        return None
        
    for nombre in posibles_nombres:
        for col in df.columns:
            if nombre in col:
                return col
    return None

def guardar_archivo_temporal(uploaded_file, tipo_archivo):
    """Guarda archivo temporalmente"""
    if uploaded_file is not None:
        # Limpiar archivos anteriores del mismo tipo
        for archivo in os.listdir(TEMP_DIR):
            if archivo.startswith(tipo_archivo):
                try:
                    os.remove(os.path.join(TEMP_DIR, archivo))
                except:
                    pass
        
        # Guardar nuevo archivo
        file_path = os.path.join(TEMP_DIR, f"{tipo_archivo}_{uploaded_file.name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        return file_path
    return None

def cargar_archivo_temporal(tipo_archivo):
    """Carga archivo temporal"""
    for archivo in os.listdir(TEMP_DIR):
        if archivo.startswith(tipo_archivo):
            return os.path.join(TEMP_DIR, archivo)
    return None

def archivos_temporales_existen():
    """Verifica si existen archivos temporales"""
    tipos = ['ubicacion', 'correo', 'telefono']
    return all(cargar_archivo_temporal(tipo) is not None for tipo in tipos)

def limpiar_archivos_temporales():
    """Limpia archivos temporales"""
    for archivo in os.listdir(TEMP_DIR):
        try:
            os.remove(os.path.join(TEMP_DIR, archivo))
        except:
            pass

def es_director(puesto):
    """Verifica si es director (excluyendo subdirector)"""
    if pd.isna(puesto) or puesto == '':
        return False
    
    puesto_str = str(puesto).lower().strip()
    return 'director' in puesto_str and 'subdirector' not in puesto_str

def limpiar_telefono(numero):
    """Limpia número de teléfono"""
    if pd.isna(numero) or numero == '':
        return ''
    
    numero_str = str(numero)
    numero_limpio = re.sub(r'\D', '', numero_str)
    return numero_limpio

def crear_url_whatsapp(numero):
    """Crea URL de WhatsApp"""
    if not numero or numero == '':
        return None
    
    numero_limpio = re.sub(r'\D', '', str(numero))
    
    if numero_limpio.startswith('52') and len(numero_limpio) == 12:
        numero_final = numero_limpio
    elif len(numero_limpio) == 10:
        numero_final = '52' + numero_limpio
    else:
        return None
    
    return f"https://wa.me/{numero_final}"

def crear_url_correo(correo):
    """Crea URL de correo"""
    if not correo or correo == '':
        return None
    return f"mailto:{correo}"

def procesar_datos(_df_ubicacion, _df_correo, _df_telefono, _progress_bar=None):
    """Procesa y combina los datos de los tres archivos optimizado"""
    try:
        # Validación inicial
        if any(df is None or df.empty for df in [_df_ubicacion, _df_correo, _df_telefono]):
            return None, "❌ Uno o más archivos están vacíos"
        
        if _progress_bar:
            _progress_bar.progress(0.1, text="🔍 Buscando columnas...")
        
        # Listas de posibles nombres para cada campo
        posibles_nombres = ['nombre', 'name', 'nombres', 'empleado']
        col_nombre_ubi = encontrar_columna_clave(_df_ubicacion, posibles_nombres)
        col_nombre_correo = encontrar_columna_clave(_df_correo, posibles_nombres)
        col_nombre_telefono = encontrar_columna_clave(_df_telefono, posibles_nombres)
        
        # Validar columnas esenciales
        if not all([col_nombre_ubi, col_nombre_correo, col_nombre_telefono]):
            return None, "❌ No se encontraron todas las columnas de nombre necesarias"
        
        if _progress_bar:
            _progress_bar.progress(0.3, text="🧹 Limpiando datos...")
        
        # Limpiar y preparar datos
        df_ubicacion = _df_ubicacion.copy()
        df_correo = _df_correo.copy()
        df_telefono = _df_telefono.copy()
        
        # Limpiar nombres y estandarizar
        for df, col_nombre in [(df_ubicacion, col_nombre_ubi), 
                              (df_correo, col_nombre_correo), 
                              (df_telefono, col_nombre_telefono)]:
            df[col_nombre] = df[col_nombre].astype(str).str.strip().str.upper()
            df.dropna(subset=[col_nombre], inplace=True)
            df = df[df[col_nombre] != '']
            df = df[~df[col_nombre].str.upper().isin(['NAN', 'NONE', 'NULL'])]
        
        if _progress_bar:
            _progress_bar.progress(0.5, text="🔗 Combinando datos...")
        
        # Encontrar columnas adicionales
        col_puesto = encontrar_columna_clave(df_ubicacion, ['puesto', 'cargo', 'position'])
        col_departamento = encontrar_columna_clave(df_ubicacion, ['departamento', 'area', 'department'])
        col_correo_data = encontrar_columna_clave(df_correo, ['correo', 'email', 'mail'])
        col_telefono_data = encontrar_columna_clave(df_telefono, ['telefono', 'tel', 'phone', 'celular'])
        
        # Crear diccionarios para unión eficiente
        datos_ubicacion = {}
        for _, row in df_ubicacion.iterrows():
            nombre = row[col_nombre_ubi]
            datos_ubicacion[nombre] = {
                'puesto': row.get(col_puesto, '') if col_puesto else '',
                'departamento': row.get(col_departamento, '') if col_departamento else ''
            }
        
        # Diccionarios para correos y teléfonos
        correos_dict = {}
        for _, row in df_correo.iterrows():
            nombre = row[col_nombre_correo]
            if col_correo_data and pd.notna(row.get(col_correo_data)):
                correos_dict[nombre] = row[col_correo_data]
        
        telefonos_dict = {}
        for _, row in df_telefono.iterrows():
            nombre = row[col_nombre_telefono]
            if col_telefono_data and pd.notna(row.get(col_telefono_data)):
                telefonos_dict[nombre] = limpiar_telefono(row[col_telefono_data])
        
        # Combinar datos
        datos_combinados = []
        for nombre in df_ubicacion[col_nombre_ubi].unique():
            if nombre in correos_dict or nombre in telefonos_dict:
                datos_ubi = datos_ubicacion.get(nombre, {})
                datos_combinados.append({
                    'nombre': nombre,
                    'departamento': datos_ubi.get('departamento', ''),
                    'puesto': datos_ubi.get('puesto', ''),
                    'correo': correos_dict.get(nombre, ''),
                    'telefono': telefonos_dict.get(nombre, '')
                })
        
        df_combinado = pd.DataFrame(datos_combinados)
        
        if _progress_bar:
            _progress_bar.progress(0.8, text="⚙️ Aplicando filtros...")
        
        # Filtrar directores
        if 'puesto' in df_combinado.columns:
            df_combinado = df_combinado[~df_combinado['puesto'].apply(es_director)]
        
        # Ordenar columnas
        column_order = ['nombre', 'departamento', 'puesto', 'correo', 'telefono']
        existing_columns = [col for col in column_order if col in df_combinado.columns]
        df_combinado = df_combinado[existing_columns]
        
        if _progress_bar:
            _progress_bar.progress(1.0, text="✅ Procesamiento completado")
            time.sleep(0.5)
        
        return df_combinado, None  # Sin error
        
    except Exception as e:
        return None, f"❌ Error al procesar los datos: {str(e)}"

def cargar_datos_desde_temporales():
    """Carga y procesa los datos desde los archivos temporales"""
    progress_bar = st.progress(0, text="📥 Cargando archivos temporales...")
    
    try:
        progress_bar.progress(0.2, text="📁 Cargando archivo de ubicación...")
        ruta_ubicacion = cargar_archivo_temporal('ubicacion')
        df_ubicacion = cargar_archivo_desde_ruta(ruta_ubicacion, 1) if ruta_ubicacion else None
        
        progress_bar.progress(0.4, text="📁 Cargando archivo de correo...")
        ruta_correo = cargar_archivo_temporal('correo')
        df_correo = cargar_archivo_desde_ruta(ruta_correo, 0) if ruta_correo else None
        
        progress_bar.progress(0.6, text="📁 Cargando archivo de teléfono...")
        ruta_telefono = cargar_archivo_temporal('telefono')
        df_telefono = cargar_archivo_desde_ruta(ruta_telefono, 0) if ruta_telefono else None
        
        if all(df is not None and not df.empty for df in [df_ubicacion, df_correo, df_telefono]):
            df_combinado, error = procesar_datos(df_ubicacion, df_correo, df_telefono, progress_bar)
            
            if error:
                st.error(error)
                return None, None
                
            if df_combinado is not None and not df_combinado.empty:
                info_origen = {
                    'origen_ubicacion': f"Archivo: {os.path.basename(ruta_ubicacion).replace('ubicacion_', '')}",
                    'origen_correo': f"Archivo: {os.path.basename(ruta_correo).replace('correo_', '')}",
                    'origen_telefono': f"Archivo: {os.path.basename(ruta_telefono).replace('telefono_', '')}",
                    'fecha_actualizacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                return df_combinado, info_origen
        
        st.error("❌ No se pudieron cargar todos los archivos")
        return None, None
        
    except Exception as e:
        st.error(f"❌ Error al cargar datos temporales: {str(e)}")
        return None, None
    finally:
        time.sleep(0.5)
        progress_bar.empty()

def mostrar_tarjeta_contacto(contacto):
    """Muestra tarjeta de contacto mejorada"""
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="contact-card">', unsafe_allow_html=True)
        st.write(f"### 👤 {contacto['nombre']}")
        
        info_cols = st.columns(2)
        with info_cols[0]:
            if contacto.get('puesto'):
                st.write(f"**💼 Puesto:** {contacto['puesto']}")
            if contacto.get('departamento'):
                st.write(f"**🏢 Departamento:** {contacto['departamento']}")
        
        with info_cols[1]:
            telefono = contacto.get('telefono', '')
            correo = contacto.get('correo', '')
            
            if telefono:
                st.write(f"**📞 Teléfono:** {telefono}")
            else:
                st.warning("**📞 Teléfono:** No disponible")
            
            if correo:
                st.write(f"**📧 Correo:** {correo}")
            else:
                st.warning("**📧 Correo:** No disponible")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.write("### 📱 Acciones Rápidas")
        
        # Botón WhatsApp
        if telefono:
            url_whatsapp = crear_url_whatsapp(telefono)
            if url_whatsapp:
                st.markdown(
                    f'<a href="{url_whatsapp}" target="_blank" style="text-decoration: none;">'
                    f'<button class="action-btn whatsapp-btn">📱 Abrir WhatsApp</button>'
                    f'</a>',
                    unsafe_allow_html=True
                )
            else:
                st.button("📱 WhatsApp", disabled=True, use_container_width=True, help="Número de teléfono no válido")
        else:
            st.button("📱 WhatsApp", disabled=True, use_container_width=True, help="No hay número de teléfono")
        
        # Botón Correo
        if correo:
            url_correo = crear_url_correo(correo)
            if url_correo:
                st.markdown(
                    f'<a href="{url_correo}" target="_blank" style="text-decoration: none;">'
                    f'<button class="action-btn email-btn">📧 Enviar Correo</button>'
                    f'</a>',
                    unsafe_allow_html=True
                )
            else:
                st.button("📧 Correo", disabled=True, use_container_width=True, help="Correo no válido")
        else:
            st.button("📧 Correo", disabled=True, use_container_width=True, help="No hay correo electrónico")
    
    st.markdown('</div>', unsafe_allow_html=True)

def buscar_empleados_avanzado(df, termino_busqueda):
    """Búsqueda avanzada en todas las columnas"""
    if not termino_busqueda.strip() or df.empty:
        return df
    
    termino = termino_busqueda.upper().strip()
    termino_palabras = termino.split()
    
    def contiene_palabras(fila):
        texto_busqueda = ' '.join(str(val) for val in fila.values if pd.notna(val)).upper()
        return all(palabra in texto_busqueda for palabra in termino_palabras)
    
    return df[df.apply(contiene_palabras, axis=1)]

def mostrar_seccion_administrador():
    """Sección de administrador - solo para cambiar archivos"""
    if 'password_admin_verified' not in st.session_state:
        st.session_state.password_admin_verified = False
    
    if not st.session_state.password_admin_verified:
        st.write("### 👨‍💼 Panel de Administrador")
        with st.form("admin_login"):
            password = st.text_input("Contraseña:", type="password", key="admin_password")
            if st.form_submit_button("🔓 Acceder", use_container_width=True):
                if password == PASSWORD:
                    st.session_state.password_admin_verified = True
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta")
        return False
    
    # Header de administrador
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success("🔓 Sesión de administrador activa")
    with col2:
        if st.button("🚪 Cerrar Sesión", use_container_width=True, key="logout_admin"):
            st.session_state.password_admin_verified = False
            st.rerun()
    
    # Carga de archivos
    with st.expander("📁 Gestión de Archivos", expanded=True):
        st.info("💡 Sube los tres archivos necesarios para actualizar los datos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            archivo_ubicacion = st.file_uploader(
                "📋 Ubicación (Excel)",
                type=['xlsx', 'xls'],
                key="admin_ubicacion",
                help="Encabezados en fila 2: Nombre, Puesto, Departamento"
            )
            if archivo_ubicacion:
                guardar_archivo_temporal(archivo_ubicacion, 'ubicacion')
                st.success(f"✅ {archivo_ubicacion.name}")
        
        with col2:
            archivo_correo = st.file_uploader(
                "📧 Correos (Excel)",
                type=['xlsx', 'xls'],
                key="admin_correo",
                help="Encabezados en fila 1: Nombre, Correo"
            )
            if archivo_correo:
                guardar_archivo_temporal(archivo_correo, 'correo')
                st.success(f"✅ {archivo_correo.name}")
                
        with col3:
            archivo_telefono = st.file_uploader(
                "📞 Teléfonos (Excel)",
                type=['xlsx', 'xls'],
                key="admin_telefono",
                help="Encabezados en fila 1: Nombre, Teléfono"
            )
            if archivo_telefono:
                guardar_archivo_temporal(archivo_telefono, 'telefono')
                st.success(f"✅ {archivo_telefono.name}")
    
    # Botones de acción
    archivos_listos = archivos_temporales_existen()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Actualizar Datos", type="primary", use_container_width=True, 
                    disabled=not archivos_listos, key="process_admin"):
            with st.spinner("Procesando archivos..."):
                df_combinado, info_origen = cargar_datos_desde_temporales()
                
            if df_combinado is not None and not df_combinado.empty:
                st.session_state.df_combinado = df_combinado
                st.session_state.info_origen = info_origen
                st.session_state.datos_cargados = True
                st.success(f"✅ Datos actualizados - {len(df_combinado)} empleados cargados")
                st.rerun()
            else:
                st.error("❌ No se pudieron procesar los archivos")
    
    with col2:
        if st.button("🔄 Limpiar Cache", use_container_width=True, key="clear_cache"):
            st.cache_data.clear()
            st.success("✅ Cache limpiado")
    
    with col3:
        if st.button("🗑️ Limpiar Todo", use_container_width=True, key="clear_all"):
            limpiar_archivos_temporales()
            st.cache_data.clear()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("✅ Sistema limpiado completamente")
            st.rerun()
    
    # Información del sistema
    if st.session_state.get('info_origen'):
        with st.expander("📊 Información del Sistema", expanded=False):
            info = st.session_state.info_origen
            st.write(f"**📋 Ubicación:** {info['origen_ubicacion']}")
            st.write(f"**📧 Correo:** {info['origen_correo']}")
            st.write(f"**📞 Teléfono:** {info['origen_telefono']}")
            st.write(f"**🕐 Actualización:** {info['fecha_actualizacion']}")
            
            if st.session_state.get('df_combinado') is not None:
                st.write(f"**👥 Empleados cargados:** {len(st.session_state.df_combinado)}")
    
    return True

def main():
    """Función principal de la aplicación"""
    # Inicializar estado
    if 'datos_cargados' not in st.session_state:
        st.session_state.datos_cargados = False
    if 'df_combinado' not in st.session_state:
        st.session_state.df_combinado = None
    if 'info_origen' not in st.session_state:
        st.session_state.info_origen = None
    if 'contacto_seleccionado' not in st.session_state:
        st.session_state.contacto_seleccionado = None
    if 'termino_busqueda' not in st.session_state:
        st.session_state.termino_busqueda = ""

    # CARGA AUTOMÁTICA AL INICIO - Mejorada
    if not st.session_state.datos_cargados and archivos_temporales_existen():
        with st.spinner("🔄 Cargando datos del sistema..."):
            df_combinado, info_origen = cargar_datos_desde_temporales()
            if df_combinado is not None and not df_combinado.empty:
                st.session_state.df_combinado = df_combinado
                st.session_state.info_origen = info_origen
                st.session_state.datos_cargados = True

    # Interfaz principal
    st.title("🔍 Sistema de Ubicación de Contactos")
    
    # Estado del sistema (solo mostrar cuando hay problemas)
    if archivos_temporales_existen() and not st.session_state.datos_cargados:
        st.warning("⚠️ Archivos encontrados pero hubo un error al procesarlos")
    elif not archivos_temporales_existen():
        st.info("📝 Use el panel de administrador para cargar archivos iniciales")
    
    if st.session_state.datos_cargados and st.session_state.df_combinado is not None and not st.session_state.df_combinado.empty:
        df = st.session_state.df_combinado
        
        # Búsqueda con estado persistente - CORREGIDO
        col1, col2 = st.columns([3, 1])
        with col1:
            # Usar on_change para manejar mejor el estado
            def actualizar_busqueda():
                st.session_state.termino_busqueda = st.session_state.busqueda_input_value
                st.session_state.contacto_seleccionado = None
            
            termino_busqueda = st.text_input(
                "🔎 Buscar empleado por nombre, puesto o departamento",
                placeholder="Ej: JUAN PEREZ o VENTAS o GERENTE",
                key="busqueda_input_value",
                value=st.session_state.termino_busqueda,
                on_change=actualizar_busqueda
            )
        with col2:
            st.write("")
            st.write("")
            if st.button("🔄 Limpiar Búsqueda", use_container_width=True, key="clear_search"):
                # Limpiar tanto el término de búsqueda como el contacto seleccionado
                st.session_state.termino_busqueda = ""
                st.session_state.contacto_seleccionado = None
                st.rerun()
        
        # Procesar búsqueda
        if st.session_state.termino_busqueda:
            resultados = buscar_empleados_avanzado(df, st.session_state.termino_busqueda)
        else:
            resultados = df
        
        if len(resultados) > 0:
            if st.session_state.termino_busqueda:
                # st.success(f"📊 {len(resultados)} empleado(s) encontrado(s) para: '{st.session_state.termino_busqueda}'")
                pass
            
            # Mostrar contacto seleccionado si existe
            if st.session_state.contacto_seleccionado is not None:
                st.write("---")
                mostrar_tarjeta_contacto(st.session_state.contacto_seleccionado)
                st.write("---")
            
            # Tabla de resultados con selección directa EN CONTENEDOR CON SCROLL
            st.write("###  Lista de Empleados")
            st.info("💡 Haz clic en 'Seleccionar' para ver los detalles de contacto de cualquier empleado")
            
            # Contenedor con scroll para la lista de empleados
            st.markdown('<div class="employee-list-container">', unsafe_allow_html=True)
            
            # Crear tabla con botones de selección
            for idx, (_, row) in enumerate(resultados.iterrows()):
                contacto = row.to_dict()
                
                # Usar columnas para cada fila con mejor diseño
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{contacto['nombre']}**")
                with col2:
                    if contacto.get('puesto'):
                        st.write(f"_{contacto['puesto']}_")
                    else:
                        st.write("_Sin puesto_")
                with col3:
                    if contacto.get('departamento'):
                        st.write(f"`{contacto['departamento']}`")
                    else:
                        st.write("`Sin departamento`")
                with col4:
                    if st.button("Seleccionar", key=f"select_{idx}", use_container_width=True):
                        st.session_state.contacto_seleccionado = contacto
                        st.rerun()
                
                # Línea separadora entre empleados (excepto el último)
                if idx < len(resultados) - 1:
                    st.markdown("---")
            
            st.markdown('</div>', unsafe_allow_html=True)  # Cerrar contenedor con scroll
            
            # Exportar resultados (fuera del contenedor de scroll)
            st.write("---")
            csv_data = resultados.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Exportar Resultados (CSV)",
                data=csv_data,
                file_name=f"empleados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                key="export_results",
                use_container_width=True
            )
        else:
            st.warning("❌ No se encontraron empleados")
    
    # Panel de administrador (solo para cambios)
    st.markdown("---")
    with st.expander("🔧 Administrar Archivos (Solo para actualizaciones)", expanded=False):
        mostrar_seccion_administrador()
    
    # Estado del sistema en sidebar
    with st.sidebar:
        st.markdown("### 📊 Estado del Sistema")
        if st.session_state.datos_cargados and st.session_state.df_combinado is not None:
            st.success(f"✅ {len(st.session_state.df_combinado)} empleados")
            if st.session_state.info_origen:
                st.caption(f"Última actualización: {st.session_state.info_origen['fecha_actualizacion']}")
        elif archivos_temporales_existen():
            st.warning("⚠️ Archivos listos")
        else:
            st.info("📝 Sin archivos")
        
        # Información rápida
        st.markdown("---")
        st.markdown("### 💡 Uso Rápido")
        st.markdown("""
        1. **Buscar**: Escribe nombre, puesto o departamento
        2. **Seleccionar**: Haz clic en 'Seleccionar' de cualquier empleado
        3. **Contactar**: Usa WhatsApp o Correo desde la tarjeta
        4. **Limpiar**: Botón 'Limpiar Búsqueda' para empezar de nuevo
        """)

if __name__ == "__main__":
    main()