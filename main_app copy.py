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
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any

# Desactivar warnings de SSL para desarrollo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =============================================
# PRINCIPIO DE RESPONSABILIDAD ÚNICA (SRP)
# =============================================

class ConfigManager:
    """Gestiona la configuración de la aplicación - SRP"""
    
    def __init__(self):
        self.PASSWORD = "admin2021*+"
        self.TEMP_DIR = "temp_archivos"
        self._ensure_temp_dir()
    
    def _ensure_temp_dir(self):
        """Asegura que el directorio temporal exista"""
        if not os.path.exists(self.TEMP_DIR):
            os.makedirs(self.TEMP_DIR)

class UIManager:
    """Gestiona la interfaz de usuario y estilos - SRP"""
    
    @staticmethod
    def setup_page_config():
        """Configura la página de Streamlit"""
        st.set_page_config(
            page_title="Sistema de Ubicación de Contactos de Empleados",
            page_icon="",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
    
    @staticmethod
    def apply_custom_styles():
        """Aplica estilos CSS personalizados"""
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
    
    @staticmethod
    def display_footer():
        """Muestra el footer"""
        st.markdown(
            '<div class="footer">Software desarrollado por GNN</div>',
            unsafe_allow_html=True
        )

# =============================================
# PRINCIPIO ABIERTO/CERRADO (OCP)
# =============================================

class DataProcessor(ABC):
    """Interfaz base para procesadores de datos - OCP"""
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        pass

class ExcelDataProcessor(DataProcessor):
    """Procesador específico para datos de Excel - OCP"""
    
    def __init__(self, header_row: int = 0):
        self.header_row = header_row
    
    def process(self, uploaded_file) -> Optional[pd.DataFrame]:
        """Procesa archivos Excel"""
        try:
            if uploaded_file is not None:
                df = pd.read_excel(
                    uploaded_file, 
                    header=self.header_row, 
                    engine='openpyxl',
                    dtype=str
                )
                df.columns = ColumnCleaner.clean_column_names(df.columns)
                df = df.dropna(how='all')
                return df
        except Exception as e:
            st.error(f"❌ Error al procesar archivo: {str(e)}")
        return None

class ColumnCleaner:
    """Clase dedicada a la limpieza de columnas - SRP"""
    
    @staticmethod
    def clean_column_names(columns) -> List[str]:
        """Limpia nombres de columnas"""
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

# =============================================
# PRINCIPIO DE SUSTITUCIÓN DE LISKOV (LSP)
# =============================================

class FileHandler(ABC):
    """Interfaz base para manejo de archivos - LSP"""
    
    @abstractmethod
    def save(self, uploaded_file, file_type: str) -> Optional[str]:
        pass
    
    @abstractmethod
    def load(self, file_type: str) -> Optional[str]:
        pass

class TemporaryFileHandler(FileHandler):
    """Manejador de archivos temporales - LSP"""
    
    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir
    
    def save(self, uploaded_file, file_type: str) -> Optional[str]:
        """Guarda archivo temporalmente"""
        if uploaded_file is not None:
            # Limpiar archivos anteriores del mismo tipo
            for archivo in os.listdir(self.temp_dir):
                if archivo.startswith(file_type):
                    try:
                        os.remove(os.path.join(self.temp_dir, archivo))
                    except:
                        pass
            
            # Guardar nuevo archivo
            file_path = os.path.join(self.temp_dir, f"{file_type}_{uploaded_file.name}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            return file_path
        return None
    
    def load(self, file_type: str) -> Optional[str]:
        """Carga archivo temporal"""
        for archivo in os.listdir(self.temp_dir):
            if archivo.startswith(file_type):
                return os.path.join(self.temp_dir, archivo)
        return None
    
    def exists(self, file_types: List[str]) -> bool:
        """Verifica si existen archivos temporales"""
        return all(self.load(tipo) is not None for tipo in file_types)
    
    def cleanup(self):
        """Limpia archivos temporales"""
        for archivo in os.listdir(self.temp_dir):
            try:
                os.remove(os.path.join(self.temp_dir, archivo))
            except:
                pass

# =============================================
# PRINCIPIO DE SEGREGACIÓN DE INTERFACES (ISP)
# =============================================

class ContactInfoProvider(ABC):
    """Interfaz específica para proveedores de información de contacto - ISP"""
    
    @abstractmethod
    def get_contact_info(self, nombre: str) -> Dict[str, str]:
        pass

class URLGenerator(ABC):
    """Interfaz específica para generadores de URLs - ISP"""
    
    @abstractmethod
    def generate_url(self, data: str) -> Optional[str]:
        pass

class WhatsAppURLGenerator(URLGenerator):
    """Generador de URLs de WhatsApp - ISP"""
    
    def generate_url(self, numero: str) -> Optional[str]:
        """Genera URL de WhatsApp"""
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

class EmailURLGenerator(URLGenerator):
    """Generador de URLs de correo - ISP"""
    
    def generate_url(self, correo: str) -> Optional[str]:
        """Genera URL de correo"""
        if not correo or correo == '':
            return None
        return f"mailto:{correo}"

# =============================================
# PRINCIPIO DE INVERSIÓN DE DEPENDENCIAS (DIP)
# =============================================

class DataMerger:
    """Combina datos de diferentes fuentes - DIP"""
    
    def __init__(self, 
                 ubicacion_provider: ContactInfoProvider,
                 correo_provider: ContactInfoProvider,
                 telefono_provider: ContactInfoProvider):
        self.ubicacion_provider = ubicacion_provider
        self.correo_provider = correo_provider
        self.telefono_provider = telefono_provider
    
    def merge_data(self, nombres: List[str]) -> List[Dict[str, str]]:
        """Combina datos de diferentes proveedores"""
        datos_combinados = []
        
        for nombre in nombres:
            datos_ubi = self.ubicacion_provider.get_contact_info(nombre)
            datos_correo = self.correo_provider.get_contact_info(nombre)
            datos_telefono = self.telefono_provider.get_contact_info(nombre)
            
            if datos_correo.get('correo') or datos_telefono.get('telefono'):
                datos_combinados.append({
                    'nombre': nombre,
                    'departamento': datos_ubi.get('departamento', ''),
                    'puesto': datos_ubi.get('puesto', ''),
                    'correo': datos_correo.get('correo', ''),
                    'telefono': datos_telefono.get('telefono', '')
                })
        
        return datos_combinados

# =============================================
# IMPLEMENTACIONES CONCRETAS
# =============================================

class EmployeeDataProvider(ContactInfoProvider):
    """Proveedor de datos de empleados desde DataFrames"""
    
    def __init__(self, df: pd.DataFrame, nombre_column: str, data_columns: Dict[str, str]):
        self.df = df
        self.nombre_column = nombre_column
        self.data_columns = data_columns
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepara los datos para búsqueda eficiente"""
        self.df[self.nombre_column] = self.df[self.nombre_column].astype(str).str.strip().str.upper()
        self.df.dropna(subset=[self.nombre_column], inplace=True)
        self.df = self.df[self.df[self.nombre_column] != '']
        self.df = self.df[~self.df[self.nombre_column].str.upper().isin(['NAN', 'NONE', 'NULL'])]
    
    def get_contact_info(self, nombre: str) -> Dict[str, str]:
        """Obtiene información de contacto para un nombre específico"""
        result = {}
        row = self.df[self.df[self.nombre_column] == nombre]
        
        if not row.empty:
            for key, column in self.data_columns.items():
                if column and column in row.columns and not row[column].isna().all():
                    result[key] = row[column].iloc[0] if not pd.isna(row[column].iloc[0]) else ''
        
        return result
    
    def get_all_names(self) -> List[str]:
        """Obtiene todos los nombres únicos"""
        return self.df[self.nombre_column].unique().tolist()

class ColumnFinder:
    """Encuentra columnas en DataFrames - SRP"""
    
    @staticmethod
    def find_column(df: pd.DataFrame, posibles_nombres: List[str]) -> Optional[str]:
        """Encuentra una columna por posibles nombres"""
        if df is None or df.empty:
            return None
            
        for nombre in posibles_nombres:
            for col in df.columns:
                if nombre in col:
                    return col
        return None

class PhoneCleaner:
    """Limpia números de teléfono - SRP"""
    
    @staticmethod
    def clean_phone(numero: str) -> str:
        """Limpia número de teléfono"""
        if pd.isna(numero) or numero == '':
            return ''
        
        numero_str = str(numero)
        numero_limpio = re.sub(r'\D', '', numero_str)
        return numero_limpio

class PositionValidator:
    """Valida posiciones de empleados - SRP"""
    
    @staticmethod
    def is_director(puesto: str) -> bool:
        """Verifica si es director (excluyendo subdirector)"""
        if pd.isna(puesto) or puesto == '':
            return False
        
        puesto_str = str(puesto).lower().strip()
        return 'director' in puesto_str and 'subdirector' not in puesto_str

class EmployeeSearcher:
    """Realiza búsquedas de empleados - SRP"""
    
    @staticmethod
    def advanced_search(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
        """Búsqueda avanzada en todas las columnas"""
        if not search_term.strip() or df.empty:
            return pd.DataFrame()
        
        termino = search_term.upper().strip()
        termino_palabras = termino.split()
        
        def contains_words(row):
            texto_busqueda = ' '.join(str(val) for val in row.values if pd.notna(val)).upper()
            return all(palabra in texto_busqueda for palabra in termino_palabras)
        
        return df[df.apply(contains_words, axis=1)]

# =============================================
# CLASE PRINCIPAL DE LA APLICACIÓN
# =============================================

class EmployeeContactSystem:
    """Sistema principal de gestión de contactos de empleados"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.file_handler = TemporaryFileHandler(self.config.TEMP_DIR)
        self.ui_manager = UIManager()
        
        # Inicializar estado de la sesión
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Inicializa el estado de la sesión"""
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
        if 'mostrando_resultados' not in st.session_state:
            st.session_state.mostrando_resultados = False
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.ui_manager.setup_page_config()
        self.ui_manager.apply_custom_styles()
        self.ui_manager.display_footer()
    
    def load_data_from_temporales(self) -> Tuple[Optional[pd.DataFrame], Optional[Dict]]:
        """Carga y procesa datos desde archivos temporales"""
        progress_bar = st.progress(0, text="📥 Cargando archivos temporales...")
        
        try:
            # Cargar archivos
            progress_bar.progress(0.2, text="📁 Cargando archivo de ubicación...")
            df_ubicacion = self._load_dataframe('ubicacion', 1)
            
            progress_bar.progress(0.4, text="📁 Cargando archivo de correo...")
            df_correo = self._load_dataframe('correo', 0)
            
            progress_bar.progress(0.6, text="📁 Cargando archivo de teléfono...")
            df_telefono = self._load_dataframe('telefono', 0)
            
            if all(df is not None and not df.empty for df in [df_ubicacion, df_correo, df_telefono]):
                df_combinado = self._process_data(df_ubicacion, df_correo, df_telefono, progress_bar)
                
                if df_combinado is not None and not df_combinado.empty:
                    info_origen = self._create_source_info()
                    return df_combinado, info_origen
        
            st.error("❌ No se pudieron cargar todos los archivos")
            return None, None
            
        except Exception as e:
            st.error(f"❌ Error al cargar datos temporales: {str(e)}")
            return None, None
        finally:
            time.sleep(0.5)
            progress_bar.empty()
    
    def _load_dataframe(self, file_type: str, header_row: int) -> Optional[pd.DataFrame]:
        """Carga un DataFrame desde archivo temporal"""
        file_path = self.file_handler.load(file_type)
        if file_path:
            processor = ExcelDataProcessor(header_row)
            return processor.process(file_path)
        return None
    
    def _process_data(self, df_ubicacion, df_correo, df_telefono, progress_bar) -> Optional[pd.DataFrame]:
        """Procesa y combina los datos"""
        try:
            # Encontrar columnas
            col_nombre_ubi = ColumnFinder.find_column(df_ubicacion, ['nombre', 'name', 'nombres', 'empleado'])
            col_nombre_correo = ColumnFinder.find_column(df_correo, ['nombre', 'name', 'nombres', 'empleado'])
            col_nombre_telefono = ColumnFinder.find_column(df_telefono, ['nombre', 'name', 'nombres', 'empleado'])
            
            if not all([col_nombre_ubi, col_nombre_correo, col_nombre_telefono]):
                st.error("❌ No se encontraron todas las columnas de nombre necesarias")
                return None
            
            progress_bar.progress(0.5, text="🔗 Combinando datos...")
            
            # Crear proveedores de datos
            ubicacion_provider = EmployeeDataProvider(
                df_ubicacion, col_nombre_ubi,
                {
                    'puesto': ColumnFinder.find_column(df_ubicacion, ['puesto', 'cargo', 'position']),
                    'departamento': ColumnFinder.find_column(df_ubicacion, ['departamento', 'area', 'department'])
                }
            )
            
            correo_provider = EmployeeDataProvider(
                df_correo, col_nombre_correo,
                {'correo': ColumnFinder.find_column(df_correo, ['correo', 'email', 'mail'])}
            )
            
            telefono_provider = EmployeeDataProvider(
                df_telefono, col_nombre_telefono,
                {'telefono': ColumnFinder.find_column(df_telefono, ['telefono', 'tel', 'phone', 'celular'])}
            )
            
            # Combinar datos
            data_merger = DataMerger(ubicacion_provider, correo_provider, telefono_provider)
            datos_combinados = data_merger.merge_data(ubicacion_provider.get_all_names())
            
            df_combinado = pd.DataFrame(datos_combinados)
            
            # Filtrar directores
            if 'puesto' in df_combinado.columns:
                df_combinado = df_combinado[~df_combinado['puesto'].apply(PositionValidator.is_director)]
            
            progress_bar.progress(1.0, text="✅ Procesamiento completado")
            return df_combinado
            
        except Exception as e:
            st.error(f"❌ Error al procesar los datos: {str(e)}")
            return None
    
    def _create_source_info(self) -> Dict[str, str]:
        """Crea información de origen de los datos"""
        ubicacion_file = self.file_handler.load('ubicacion')
        correo_file = self.file_handler.load('correo')
        telefono_file = self.file_handler.load('telefono')
        
        return {
            'origen_ubicacion': f"Archivo: {os.path.basename(ubicacion_file).replace('ubicacion_', '')}" if ubicacion_file else "No disponible",
            'origen_correo': f"Archivo: {os.path.basename(correo_file).replace('correo_', '')}" if correo_file else "No disponible",
            'origen_telefono': f"Archivo: {os.path.basename(telefono_file).replace('telefono_', '')}" if telefono_file else "No disponible",
            'fecha_actualizacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def display_contact_card(self, contacto: Dict[str, str]):
        """Muestra tarjeta de contacto"""
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
            self._display_action_buttons(telefono, correo)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _display_action_buttons(self, telefono: str, correo: str):
        """Muestra botones de acción"""
        # Botón WhatsApp
        whatsapp_generator = WhatsAppURLGenerator()
        url_whatsapp = whatsapp_generator.generate_url(telefono) if telefono else None
        
        if url_whatsapp:
            st.markdown(
                f'<a href="{url_whatsapp}" target="_blank" style="text-decoration: none;">'
                f'<button class="action-btn whatsapp-btn">📱 Abrir WhatsApp</button>'
                f'</a>',
                unsafe_allow_html=True
            )
        else:
            st.button("📱 WhatsApp", disabled=True, use_container_width=True, 
                     help="No hay número de teléfono válido")
        
        # Botón Correo
        email_generator = EmailURLGenerator()
        url_correo = email_generator.generate_url(correo) if correo else None
        
        if url_correo:
            st.markdown(
                f'<a href="{url_correo}" target="_blank" style="text-decoration: none;">'
                f'<button class="action-btn email-btn">📧 Enviar Correo</button>'
                f'</a>',
                unsafe_allow_html=True
            )
        else:
            st.button("📧 Correo", disabled=True, use_container_width=True, 
                     help="No hay correo electrónico")
    
    def show_admin_section(self) -> bool:
        """Muestra la sección de administrador"""
        if 'password_admin_verified' not in st.session_state:
            st.session_state.password_admin_verified = False
        
        if not st.session_state.password_admin_verified:
            return self._show_admin_login()
        
        return self._show_admin_panel()
    
    def _show_admin_login(self) -> bool:
        """Muestra formulario de login de administrador"""
        st.write("### 👨‍💼 Panel de Administrador")
        with st.form("admin_login"):
            password = st.text_input("Contraseña:", type="password", key="admin_password")
            if st.form_submit_button("🔓 Acceder", use_container_width=True):
                if password == self.config.PASSWORD:
                    st.session_state.password_admin_verified = True
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta")
        return False
    
    def _show_admin_panel(self) -> bool:
        """Muestra panel de administrador"""
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
            self._show_file_upload_section()
        
        # Botones de acción
        self._show_admin_actions()
        
        # Información del sistema
        if st.session_state.get('info_origen'):
            self._show_system_info()
        
        return True
    
    def _show_file_upload_section(self):
        """Muestra sección de carga de archivos"""
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
                self.file_handler.save(archivo_ubicacion, 'ubicacion')
                st.success(f"✅ {archivo_ubicacion.name}")
        
        with col2:
            archivo_correo = st.file_uploader(
                "📧 Correos (Excel)",
                type=['xlsx', 'xls'],
                key="admin_correo",
                help="Encabezados en fila 1: Nombre, Correo"
            )
            if archivo_correo:
                self.file_handler.save(archivo_correo, 'correo')
                st.success(f"✅ {archivo_correo.name}")
                
        with col3:
            archivo_telefono = st.file_uploader(
                "📞 Teléfonos (Excel)",
                type=['xlsx', 'xls'],
                key="admin_telefono",
                help="Encabezados en fila 1: Nombre, Teléfono"
            )
            if archivo_telefono:
                self.file_handler.save(archivo_telefono, 'telefono')
                st.success(f"✅ {archivo_telefono.name}")
    
    def _show_admin_actions(self):
        """Muestra botones de acción del administrador"""
        archivos_listos = self.file_handler.exists(['ubicacion', 'correo', 'telefono'])
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Actualizar Datos", type="primary", use_container_width=True, 
                        disabled=not archivos_listos, key="process_admin"):
                self._update_data()
        
        with col2:
            if st.button("🔄 Limpiar Cache", use_container_width=True, key="clear_cache"):
                st.cache_data.clear()
                st.success("✅ Cache limpiado")
        
        with col3:
            if st.button("🗑️ Limpiar Todo", use_container_width=True, key="clear_all"):
                self._cleanup_system()
    
    def _update_data(self):
        """Actualiza los datos del sistema"""
        with st.spinner("Procesando archivos..."):
            df_combinado, info_origen = self.load_data_from_temporales()
            
        if df_combinado is not None and not df_combinado.empty:
            st.session_state.df_combinado = df_combinado
            st.session_state.info_origen = info_origen
            st.session_state.datos_cargados = True
            st.success(f"✅ Datos actualizados - {len(df_combinado)} empleados cargados")
            st.rerun()
        else:
            st.error("❌ No se pudieron procesar los archivos")
    
    def _cleanup_system(self):
        """Limpia todo el sistema"""
        self.file_handler.cleanup()
        st.cache_data.clear()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("✅ Sistema limpiado completamente")
        st.rerun()
    
    def _show_system_info(self):
        """Muestra información del sistema"""
        with st.expander("📊 Información del Sistema", expanded=False):
            info = st.session_state.info_origen
            st.write(f"**📋 Ubicación:** {info['origen_ubicacion']}")
            st.write(f"**📧 Correo:** {info['origen_correo']}")
            st.write(f"**📞 Teléfono:** {info['origen_telefono']}")
            st.write(f"**🕐 Actualización:** {info['fecha_actualizacion']}")
            
            if st.session_state.get('df_combinado') is not None:
                st.write(f"**👥 Empleados cargados:** {len(st.session_state.df_combinado)}")
    
    def show_search_interface(self, df: pd.DataFrame):
        """Muestra la interfaz de búsqueda"""
        # Búsqueda
        col1, col2 = st.columns([3, 1])
        with col1:
            def update_search():
                st.session_state.termino_busqueda = st.session_state.busqueda_input_value
                st.session_state.contacto_seleccionado = None
                st.session_state.mostrando_resultados = bool(st.session_state.busqueda_input_value.strip())
            
            termino_busqueda = st.text_input(
                "🔎 Buscar empleado por nombre, puesto, departamento, numero de telefono o correo",
                placeholder="Ej: JUAN PEREZ o VENTAS o GERENTE",
                key="busqueda_input_value",
                value=st.session_state.termino_busqueda,
                on_change=update_search
            )
        with col2:
            st.write("")
            st.write("")
            if st.button("🔄 Limpiar Búsqueda", use_container_width=True, key="clear_search"):
                st.session_state.termino_busqueda = ""
                st.session_state.contacto_seleccionado = None
                st.session_state.mostrando_resultados = False
                st.rerun()
        
        # Mostrar solo campo de búsqueda limpio al inicio
        if not st.session_state.mostrando_resultados and not st.session_state.termino_busqueda:
            # Solo muestra el campo de búsqueda, nada más
            return
        
        # Procesar búsqueda
        if st.session_state.termino_busqueda:
            resultados = EmployeeSearcher.advanced_search(df, st.session_state.termino_busqueda)
            
            if len(resultados) > 0:
                # Mostrar contacto seleccionado si existe
                if st.session_state.contacto_seleccionado is not None:
                    st.write("---")
                    self.display_contact_card(st.session_state.contacto_seleccionado)
                    st.write("---")
                
                # Mostrar resultados de búsqueda
                st.success(f"📊 {len(resultados)} empleado(s) encontrado(s) para: '{st.session_state.termino_busqueda}'")
                
                st.write("### Lista de Empleados")
                st.info("💡 Haz clic en 'Seleccionar' para ver los detalles de contacto completos")
                
                st.markdown('<div class="employee-list-container">', unsafe_allow_html=True)
                self._display_employee_table(resultados)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Exportar resultados
                st.write("---")
                self._export_results(resultados)
            else:
                st.warning(f"❌ No se encontraron empleados para: '{st.session_state.termino_busqueda}'")
                st.info("💡 Prueba con otros términos de búsqueda o verifica la ortografía")
    
    def _display_employee_table(self, resultados: pd.DataFrame):
        """Muestra la tabla de empleados"""
        for idx, (_, row) in enumerate(resultados.iterrows()):
            contacto = row.to_dict()
            
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
            
            if idx < len(resultados) - 1:
                st.markdown("---")
    
    def _export_results(self, resultados: pd.DataFrame):
        """Exporta resultados a CSV"""
        csv_data = resultados.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Exportar Resultados (CSV)",
            data=csv_data,
            file_name=f"empleados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            key="export_results",
            use_container_width=True
        )
    
    def show_sidebar(self):
        """Muestra la barra lateral"""
        with st.sidebar:
            st.markdown("### 📊 Estado del Sistema")
            if st.session_state.datos_cargados and st.session_state.df_combinado is not None:
                st.success(f"✅ {len(st.session_state.df_combinado)} empleados")
                if st.session_state.info_origen:
                    st.caption(f"Última actualización: {st.session_state.info_origen['fecha_actualizacion']}")
            elif self.file_handler.exists(['ubicacion', 'correo', 'telefono']):
                st.warning("⚠️ Archivos listos")
            else:
                st.info("📝 Sin archivos")
            
            st.markdown("---")
            st.markdown("### 💡 Uso Rápido")
            st.markdown("""
            1. **Buscar**: Escribe nombre, puesto o departamento
            2. **Seleccionar**: Haz clic en 'Seleccionar' de cualquier empleado
            3. **Contactar**: Usa WhatsApp o Correo desde la tarjeta
            4. **Limpiar**: Botón 'Limpiar Búsqueda' para empezar de nuevo
            """)
    
    def run(self):
        """Ejecuta la aplicación principal"""
        # Configuración inicial
        self.setup_ui()
        
        # CARGA AUTOMÁTICA AL INICIO
        if not st.session_state.datos_cargados and self.file_handler.exists(['ubicacion', 'correo', 'telefono']):
            with st.spinner("🔄 Cargando datos del sistema..."):
                df_combinado, info_origen = self.load_data_from_temporales()
                if df_combinado is not None and not df_combinado.empty:
                    st.session_state.df_combinado = df_combinado
                    st.session_state.info_origen = info_origen
                    st.session_state.datos_cargados = True
        
        # Interfaz principal
        st.title("🔍 Sistema de Ubicación de Empleados-GNI")
        
        # Estado del sistema
        if self.file_handler.exists(['ubicacion', 'correo', 'telefono']) and not st.session_state.datos_cargados:
            st.warning("⚠️ Archivos encontrados pero hubo un error al procesarlos")
        elif not self.file_handler.exists(['ubicacion', 'correo', 'telefono']):
            st.info("📝 Use el panel de administrador para cargar archivos iniciales")
        
        # Mostrar interfaz de búsqueda si los datos están cargados
        if st.session_state.datos_cargados and st.session_state.df_combinado is not None and not st.session_state.df_combinado.empty:
            self.show_search_interface(st.session_state.df_combinado)
        
        # Panel de administrador
        st.markdown("---")
        with st.expander("🔧 Administrar Archivos (Solo para actualizaciones)", expanded=False):
            self.show_admin_section()
        
        # Barra lateral
        self.show_sidebar()

# =============================================
# EJECUCIÓN PRINCIPAL
# =============================================

def main():
    """Función principal de la aplicación"""
    system = EmployeeContactSystem()
    system.run()

if __name__ == "__main__":
    main()