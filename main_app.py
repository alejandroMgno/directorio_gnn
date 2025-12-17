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
import hashlib

# Desactivar warnings de SSL para desarrollo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Script de redirección automática - AL INICIO
st.markdown("""
<style>
/* Esto es temporal para evitar flash de contenido */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>

<script>
// Función para ejecutar después de que la página cargue
function initializeRedirect() {
    // Redirección automática a /directorio si se accede sin él
    const currentPath = window.location.pathname;
    const basePath = '/directorio';

    if (currentPath === '/' || !currentPath.includes(basePath)) {
        // Construir nueva URL manteniendo parámetros
        const newPath = basePath + (currentPath === '/' ? '' : currentPath);
        const newUrl = window.location.origin + newPath + window.location.search + window.location.hash;
        
        // Solo redirigir si es necesario
        if (window.location.href !== newUrl) {
            window.history.replaceState(null, null, newPath);
            console.log('Redirigido automáticamente a:', newPath);
        }
    }

    // Interceptar clics en enlaces internos
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'A') {
            const href = e.target.getAttribute('href');
            if (href && href.startsWith('/') && !href.startsWith('/directorio/') && !href.startsWith('/static/')) {
                e.preventDefault();
                const newHref = '/directorio' + href;
                window.location.href = newHref;
            }
        }
    });
}

// Ejecutar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeRedirect);
} else {
    initializeRedirect();
}
</script>
""", unsafe_allow_html=True)

# Configuración de página (DEBE IR PRIMERO)
st.set_page_config(
    page_title="Directorio Corporativo GNI",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Directorio Corporativo v2.0 - Uso Interno"
    }
)

# =============================================
# 1. CONFIGURACIÓN Y UI (VISUAL PROFESIONAL CORPORATIVO)
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
            page_title="Directorio Corporativo GNI",
            page_icon="🏢",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
    
    @staticmethod
    def apply_custom_styles():
        """Aplica estilos CSS personalizados profesional corporativo"""
        st.markdown("""
            <style>
            /* --- VARIABLES GLOBALES --- */
            :root {
                --primary-color: #1a3a5f;
                --secondary-color: #2c5282;
                --accent-color: #2563eb;
                --success-color: #059669;
                --warning-color: #d97706;
                --light-gray: #f8fafc;
                --medium-gray: #e2e8f0;
                --dark-gray: #475569;
                --card-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                --hover-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                --border-radius: 8px;
            }

            /* --- CONTENEDOR PRINCIPAL --- */
            .main .block-container {
                padding-top: 1rem !important;
                padding-bottom: 3rem !important;
                max-width: 1200px !important;
                margin: 0 auto !important;
            }

            /* --- HEADER CORPORATIVO --- */
            .header-container {
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                color: white;
                padding: 2rem;
                border-radius: var(--border-radius);
                margin-bottom: 2rem;
                box-shadow: var(--card-shadow);
                border-left: 4px solid var(--accent-color);
            }
            .header-title {
                font-size: 1.8rem;
                font-weight: 600;
                margin: 0;
                letter-spacing: -0.5px;
            }
            .header-subtitle {
                opacity: 0.9;
                font-size: 0.95rem;
                margin-top: 0.5rem;
                font-weight: 400;
            }

            /* --- INPUTS DE BÚSQUEDA --- */
            .stTextInput input {
                border-radius: 6px !important;
                border: 1px solid var(--medium-gray) !important;
                padding: 10px 14px !important;
                font-size: 14px !important;
                transition: all 0.2s ease;
                background-color: white;
            }
            .stTextInput input:focus {
                border-color: var(--accent-color) !important;
                box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1) !important;
                color: var(--dark-gray) !important;
            }

            /* --- FILTROS DE BÚSQUEDA --- */
            .filter-badge {
                display: inline-block;
                background: #e0f2fe;
                color: #0369a1;
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 13px;
                margin-right: 8px;
                margin-bottom: 8px;
                border: 1px solid #bae6fd;
            }
            
            .filter-container {
                background: white;
                border: 1px solid var(--medium-gray);
                border-radius: var(--border-radius);
                padding: 1rem;
                margin-bottom: 1.5rem;
                box-shadow: var(--card-shadow);
            }

            /* --- TARJETA DE CONTACTO DETALLADA --- */
            .contact-card-detail {
                background: white;
                border-radius: var(--border-radius);
                padding: 1.5rem;
                box-shadow: var(--card-shadow);
                border: 1px solid var(--medium-gray);
                margin-bottom: 1.5rem;
                transition: box-shadow 0.3s ease;
            }
            .contact-card-detail:hover {
                box-shadow: var(--hover-shadow);
            }
            
            .detail-header {
                font-size: 1.3rem;
                color: var(--primary-color);
                font-weight: 600;
                border-bottom: 1px solid var(--medium-gray);
                padding-bottom: 1rem;
                margin-bottom: 1.2rem;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .detail-row {
                display: flex;
                align-items: flex-start;
                margin-bottom: 0.8rem;
                font-size: 14px;
                color: var(--dark-gray);
            }
            .detail-label {
                min-width: 120px;
                font-weight: 500;
                color: var(--primary-color);
            }
            .detail-value {
                flex: 1;
                color: #374151;
            }

            /* --- LISTA DE EMPLEADOS --- */
            .employee-list-container {
                background: white;
                border-radius: var(--border-radius);
                box-shadow: var(--card-shadow);
                overflow: hidden;
                border: 1px solid var(--medium-gray);
            }

            .emp-name { 
                font-weight: 600; 
                color: var(--primary-color); 
                font-size: 14px; 
            }
            .emp-role { 
                color: var(--dark-gray); 
                font-size: 13px; 
                font-weight: 400; 
            }
            .emp-dept { 
                background: var(--light-gray); 
                color: var(--primary-color); 
                padding: 4px 10px; 
                border-radius: 4px; 
                font-size: 12px; 
                font-weight: 500;
                border: 1px solid var(--medium-gray);
            }
            .emp-location {
                background: #f0f9ff;
                color: #0369a1;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                border: 1px solid #bae6fd;
            }

            /* --- BOTONES DE ACCIÓN --- */
            .action-btn {
                display: block;
                width: 100%;
                padding: 10px;
                border-radius: 6px;
                text-align: center;
                text-decoration: none !important;
                font-weight: 500;
                font-size: 13px;
                transition: all 0.2s ease;
                border: none;
                cursor: pointer;
                margin-bottom: 8px;
            }
            .action-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            }
            .whatsapp-btn { 
                background: #25D366 !important; 
                color: white !important; 
            }
            .whatsapp-btn:hover { 
                background: #128C7E !important; 
            }
            .email-btn { 
                background: var(--accent-color) !important; 
                color: white !important; 
            }
            .email-btn:hover { 
                background: #1d4ed8 !important; 
            }
            
            /* --- FOOTER --- */
            .footer {
                margin-top: 3rem;
                padding-top: 1rem;
                border-top: 1px solid var(--medium-gray);
                text-align: center;
                font-size: 12px;
                color: var(--dark-gray);
            }
            
            /* Botones de Streamlit ajustados */
            .stButton button {
                border-radius: 6px !important;
                font-weight: 500 !important;
                font-size: 14px !important;
                border: 1px solid var(--medium-gray) !important;
            }

            /* --- BADGES --- */
            .status-badge {
                display: inline-block;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
                margin-right: 8px;
            }
            .status-online {
                background-color: #dcfce7;
                color: #166534;
            }
            .status-offline {
                background-color: #fee2e2;
                color: #991b1b;
            }

            /* --- EXPANDER ESTILO CORPORATIVO --- */
            .streamlit-expanderHeader {
                background-color: var(--light-gray) !important;
                border: 1px solid var(--medium-gray) !important;
                border-radius: var(--border-radius) !important;
                font-weight: 500 !important;
            }

            /* --- TABLAS --- */
            .dataframe {
                border: 1px solid var(--medium-gray) !important;
                border-radius: var(--border-radius) !important;
            }
            
            /* --- ICONOS MÁS DISCRETOS --- */
            .detail-icon {
                color: var(--accent-color);
                margin-right: 10px;
                font-size: 16px;
            }
            
            /* --- SEPARADORES --- */
            .divider {
                height: 1px;
                background: linear-gradient(90deg, transparent, var(--medium-gray), transparent);
                margin: 1.5rem 0;
            }
            
            /* --- PILLS DE FILTRO --- */
            .filter-pill {
                display: inline-flex;
                align-items: center;
                background: #e0f2fe;
                color: #0369a1;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 13px;
                margin-right: 8px;
                margin-bottom: 8px;
                border: 1px solid #bae6fd;
            }
            .filter-pill-remove {
                margin-left: 6px;
                cursor: pointer;
                font-weight: bold;
            }
            </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def display_header():
        """Muestra el header visual corporativo"""
        st.markdown("""
            <div class="header-container">
                <div class="header-title">Directorio Corporativo GNI</div>
                <div class="header-subtitle">Sistema Integral de Gestión de Contactos</div>
            </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def display_footer():
        """Muestra el footer corporativo"""
        st.markdown("""
            <div class="footer">
                <div>© 2025 Gas Natural Del Noroeste • Sistema Directorio v2.0 • Plataforma Empresarial</div>
                <div style="font-size: 11px; margin-top: 5px; color: #94a3b8;">Confidencial - Uso Interno</div>
            </div>
        """, unsafe_allow_html=True)

# =============================================
# 2. LÓGICA DE NEGOCIO (SOLID)
# =============================================

class DataProcessor(ABC):
    """Interfaz base para procesadores de datos - OCP"""
    @abstractmethod
    def process(self, data: Any) -> Any:
        pass

class FileDataProcessor(DataProcessor):
    """Procesador para archivos Excel y CSV - OCP"""
    def __init__(self, header_row: int = 0):
        self.header_row = header_row
    
    def process(self, file_input) -> Optional[pd.DataFrame]:
        try:
            if file_input is None: return None
            
            if hasattr(file_input, 'read'):
                file_extension = file_input.name.split('.')[-1].lower()
                file_content = file_input
            else:
                file_extension = file_input.split('.')[-1].lower()
                file_content = file_input
            
            if file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(file_content, header=self.header_row, engine='openpyxl', dtype=str)
            elif file_extension == 'csv':
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252']
                df = None
                for encoding in encodings:
                    try:
                        if hasattr(file_content, 'seek'): file_content.seek(0)
                        df = pd.read_csv(file_content, header=self.header_row, dtype=str, encoding=encoding)
                        break
                    except Exception: continue
                if df is None: return None
            else:
                return None
            
            df.columns = ColumnCleaner.clean_column_names(df.columns)
            df = df.dropna(how='all')
            return df
        except Exception:
            return None

class ColumnCleaner:
    @staticmethod
    def clean_column_names(columns) -> List[str]:
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

class FileHandler(ABC):
    @abstractmethod
    def save(self, uploaded_file, file_type: str) -> Optional[str]: pass
    @abstractmethod
    def load(self, file_type: str) -> Optional[str]: pass

class TemporaryFileHandler(FileHandler):
    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir
    
    def save(self, uploaded_file, file_type: str) -> Optional[str]:
        if uploaded_file is not None:
            for archivo in os.listdir(self.temp_dir):
                if archivo.startswith(file_type):
                    try: os.remove(os.path.join(self.temp_dir, archivo))
                    except: pass
            
            file_path = os.path.join(self.temp_dir, f"{file_type}_{uploaded_file.name}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            return file_path
        return None
    
    def load(self, file_type: str) -> Optional[str]:
        for archivo in os.listdir(self.temp_dir):
            if archivo.startswith(file_type):
                return os.path.join(self.temp_dir, archivo)
        return None
    
    def exists(self, file_types: List[str]) -> bool:
        return all(self.load(tipo) is not None for tipo in file_types)
    
    def cleanup(self):
        for archivo in os.listdir(self.temp_dir):
            try: os.remove(os.path.join(self.temp_dir, archivo))
            except: pass

class ContactInfoProvider(ABC):
    @abstractmethod
    def get_contact_info(self, nombre: str) -> Dict[str, str]: pass

class URLGenerator(ABC):
    @abstractmethod
    def generate_url(self, data: str) -> Optional[str]: pass

class WhatsAppURLGenerator(URLGenerator):
    def generate_url(self, numero: str) -> Optional[str]:
        if not numero or numero == '': return None
        numero_limpio = re.sub(r'\D', '', str(numero))
        if numero_limpio.startswith('52') and len(numero_limpio) == 12:
            numero_final = numero_limpio
        elif len(numero_limpio) == 10:
            numero_final = '52' + numero_limpio
        else:
            return None
        return f"https://wa.me/{numero_final}"

class EmailURLGenerator(URLGenerator):
    def generate_url(self, correo: str) -> Optional[str]:
        if not correo or correo == '': return None
        return f"mailto:{correo}"

class LocationExtractor:
    """Extrae ciudad y estado de una cadena de ubicación"""
    
    @staticmethod
    def extract_location(ubicacion_str: str) -> Tuple[str, str]:
        """Extrae ciudad y estado de una cadena. Ej: 'CIUDAD DE MEXICO CDMX' -> ('CIUDAD DE MEXICO', 'CDMX')"""
        if not ubicacion_str or pd.isna(ubicacion_str):
            return '', ''
        
        ubicacion = str(ubicacion_str).strip().upper()
        
        # Lista de estados comunes en México
        estados = [
            'AGUASCALIENTES', 'BAJA CALIFORNIA', 'BAJA CALIFORNIA SUR', 'CAMPECHE',
            'CHIAPAS', 'CHIHUAHUA', 'CDMX', 'CIUDAD DE MÉXICO', 'COAHUILA',
            'COLIMA', 'DURANGO', 'ESTADO DE MÉXICO', 'GUANAJUATO', 'GUERRERO',
            'HIDALGO', 'JALISCO', 'MICHOACÁN', 'MORELOS', 'NAYARIT', 'NUEVO LEÓN',
            'OAXACA', 'PUEBLA', 'QUERÉTARO', 'QUINTANA ROO', 'SAN LUIS POTOSÍ',
            'SINALOA', 'SONORA', 'TABASCO', 'TAMAULIPAS', 'TLAXCALA', 'VERACRUZ',
            'YUCATÁN', 'ZACATECAS'
        ]
        
        # Abreviaturas comunes
        abreviaturas = {
            'CDMX': 'CIUDAD DE MÉXICO',
            'DF': 'CIUDAD DE MÉXICO',
            'EDOMEX': 'ESTADO DE MÉXICO',
            'GTO': 'GUANAJUATO',
            'JAL': 'JALISCO',
            'NLE': 'NUEVO LEÓN',
            'QRO': 'QUERÉTARO',
            'BC': 'BAJA CALIFORNIA',
            'BCS': 'BAJA CALIFORNIA SUR',
            'SON': 'SONORA',
            'CHIH': 'CHIHUAHUA',
            'SIN': 'SINALOA',
            'VER': 'VERACRUZ',
            'TAB': 'TABASCO',
            'YUC': 'YUCATÁN',
            'QROO': 'QUINTANA ROO'
        }
        
        ciudad = ubicacion
        estado = ''
        
        # Buscar estados completos
        for est in estados:
            if est in ubicacion:
                estado = est
                ciudad = ubicacion.replace(est, '').strip()
                break
        
        # Si no se encontró estado completo, buscar abreviaturas
        if not estado:
            for abrev, est in abreviaturas.items():
                if abrev in ubicacion:
                    estado = est
                    ciudad = ubicacion.replace(abrev, '').strip()
                    break
        
        # Limpiar ciudad (remover comas, puntos, etc.)
        ciudad = re.sub(r'[,\.\-]+$', '', ciudad).strip()
        
        # Si la ciudad está vacía pero tenemos ubicación, usar toda la ubicación como ciudad
        if not ciudad and ubicacion:
            ciudad = ubicacion
        
        return ciudad, estado

class DataMerger:
    def __init__(self, ubicacion_provider, correo_provider, telefono_provider):
        self.ubicacion_provider = ubicacion_provider
        self.correo_provider = correo_provider
        self.telefono_provider = telefono_provider
    
    def merge_data(self, nombres: List[str]) -> List[Dict[str, str]]:
        datos_combinados = []
        for nombre in nombres:
            datos_ubi = self.ubicacion_provider.get_contact_info(nombre)
            datos_correo = self.correo_provider.get_contact_info(nombre)
            datos_telefono = self.telefono_provider.get_contact_info(nombre)
            
            tiene_ubicacion = bool(datos_ubi.get('departamento') or datos_ubi.get('puesto'))
            tiene_correo = bool(datos_correo.get('correo'))
            tiene_telefono = bool(datos_telefono.get('telefono'))
            
            if tiene_ubicacion and (tiene_correo or tiene_telefono):
                # Extraer ciudad y estado si están disponibles
                ubicacion_str = datos_ubi.get('ubicacion', '')
                ciudad, estado = LocationExtractor.extract_location(ubicacion_str)
                
                datos_combinados.append({
                    'nombre': nombre,
                    'departamento': datos_ubi.get('departamento', ''),
                    'puesto': datos_ubi.get('puesto', ''),
                    'ubicacion': ubicacion_str,
                    'ciudad': ciudad,
                    'estado': estado,
                    'correo': datos_correo.get('correo', ''),
                    'telefono': datos_telefono.get('telefono', ''),
                    'fuente_ubicacion': 'Sí' if tiene_ubicacion else 'No',
                    'fuente_correo': 'Sí' if tiene_correo else 'No',
                    'fuente_telefono': 'Sí' if tiene_telefono else 'No'
                })
        return datos_combinados

class EmployeeDataProvider(ContactInfoProvider):
    def __init__(self, df: pd.DataFrame, nombre_column: str, data_columns: Dict[str, str]):
        self.df = df
        self.nombre_column = nombre_column
        self.data_columns = data_columns
        self._prepare_data()
    
    def _prepare_data(self):
        if self.df is not None and not self.df.empty and self.nombre_column in self.df.columns:
            self.df[self.nombre_column] = self.df[self.nombre_column].astype(str).str.strip().str.upper()
            self.df.dropna(subset=[self.nombre_column], inplace=True)
            self.df = self.df[~self.df[self.nombre_column].isin(['', 'NAN', 'NONE', 'NULL'])]
    
    def get_contact_info(self, nombre: str) -> Dict[str, str]:
        result = {}
        if self.df is None or self.df.empty or self.nombre_column not in self.df.columns: return result
        row = self.df[self.df[self.nombre_column] == nombre]
        if not row.empty:
            for key, column in self.data_columns.items():
                if column and column in row.columns:
                    val = row[column].iloc[0]
                    result[key] = val if not pd.isna(val) else ''
        return result
    
    def get_all_names(self) -> List[str]:
        if self.df is None or self.df.empty: return []
        return self.df[self.nombre_column].unique().tolist()

class ColumnFinder:
    @staticmethod
    def find_column(df: pd.DataFrame, posibles_nombres: List[str]) -> Optional[str]:
        if df is None or df.empty: return None
        for nombre in posibles_nombres:
            for col in df.columns:
                if nombre in col: return col
        return None

class PositionValidator:
    @staticmethod
    def is_director(puesto: str) -> bool:
        if pd.isna(puesto) or puesto == '': return False
        puesto_str = str(puesto).lower().strip()
        return 'director' in puesto_str and 'subdirector' not in puesto_str

class EmployeeSearcher:
    @staticmethod
    def advanced_search(df: pd.DataFrame, search_term: str, ciudad: str = None, estado: str = None) -> pd.DataFrame:
        if not search_term.strip() and not ciudad and not estado:
            return pd.DataFrame()
        
        # Filtrar por término de búsqueda
        if search_term.strip():
            termino = search_term.upper().strip()
            termino_palabras = termino.split()
            def contains_words(row):
                texto = ' '.join(str(val) for val in row.values if pd.notna(val)).upper()
                return all(palabra in texto for palabra in termino_palabras)
            resultados = df[df.apply(contains_words, axis=1)]
        else:
            resultados = df.copy()
        
        # Filtrar por ciudad si se especifica
        if ciudad and 'ciudad' in resultados.columns:
            resultados = resultados[resultados['ciudad'].str.contains(ciudad.upper(), na=False)]
        
        # Filtrar por estado si se especifica
        if estado and 'estado' in resultados.columns:
            resultados = resultados[resultados['estado'].str.contains(estado.upper(), na=False)]
        
        return resultados

# =============================================
# 3. CLASE PRINCIPAL DE LA APLICACIÓN
# =============================================

class EmployeeContactSystem:
    """Sistema principal de gestión de contactos de empleados"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.file_handler = TemporaryFileHandler(self.config.TEMP_DIR)
        self.ui_manager = UIManager()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        if 'datos_cargados' not in st.session_state: st.session_state.datos_cargados = False
        if 'df_combinado' not in st.session_state: st.session_state.df_combinado = None
        if 'info_origen' not in st.session_state: st.session_state.info_origen = None
        if 'contacto_seleccionado' not in st.session_state: st.session_state.contacto_seleccionado = None
        if 'termino_busqueda' not in st.session_state: st.session_state.termino_busqueda = ""
        if 'mostrando_resultados' not in st.session_state: st.session_state.mostrando_resultados = False
        if 'last_contact_clicked' not in st.session_state: st.session_state.last_contact_clicked = None
        if 'filtro_ciudad' not in st.session_state: st.session_state.filtro_ciudad = ""
        if 'filtro_estado' not in st.session_state: st.session_state.filtro_estado = ""
        if 'filtros_activos' not in st.session_state: st.session_state.filtros_activos = False
    
    def setup_ui(self):
        self.ui_manager.setup_page_config()
        self.ui_manager.apply_custom_styles()
        self.ui_manager.display_footer()
    
    def load_data_from_temporales(self) -> Tuple[Optional[pd.DataFrame], Optional[Dict]]:
        # Simulación de carga (sin progress bar bloqueante)
        try:
            df_ubicacion = self._load_dataframe('ubicacion', 1)
            df_correo = self._load_dataframe('correo', 0)
            df_telefono = self._load_dataframe('telefono', 0)
            
            if all(df is not None and not df.empty for df in [df_ubicacion, df_correo, df_telefono]):
                df_combinado = self._process_data(df_ubicacion, df_correo, df_telefono)
                if df_combinado is not None and not df_combinado.empty:
                    info_origen = self._create_source_info()
                    return df_combinado, info_origen
            return None, None
        except Exception as e:
            st.error(f"Error al cargar datos: {str(e)}")
            return None, None
    
    def _load_dataframe(self, file_type: str, header_row: int) -> Optional[pd.DataFrame]:
        file_path = self.file_handler.load(file_type)
        if file_path:
            return FileDataProcessor(header_row).process(file_path)
        return None
    
    def _process_data(self, df_ubicacion, df_correo, df_telefono) -> Optional[pd.DataFrame]:
        try:
            col_nombre_ubi = ColumnFinder.find_column(df_ubicacion, ['nombre', 'name', 'nombres', 'empleado'])
            col_nombre_correo = ColumnFinder.find_column(df_correo, ['nombre', 'name', 'nombres', 'empleado'])
            col_nombre_telefono = ColumnFinder.find_column(df_telefono, ['nombre', 'name', 'nombres', 'empleado'])
            
            if not col_nombre_ubi: return None
            
            # Buscar columna de ubicación (ciudad/estado)
            col_ubicacion = ColumnFinder.find_column(df_ubicacion, [
                'ubicacion', 'ciudad', 'estado', 'location', 'city', 'state', 'ciudad_y_estado'
            ])
            
            ubicacion_provider = EmployeeDataProvider(
                df_ubicacion, col_nombre_ubi,
                {
                    'puesto': ColumnFinder.find_column(df_ubicacion, ['puesto', 'cargo', 'position']),
                    'departamento': ColumnFinder.find_column(df_ubicacion, ['departamento', 'area', 'department']),
                    'ubicacion': col_ubicacion  # Puede ser None si no existe
                }
            )
            correo_provider = EmployeeDataProvider(
                df_correo, col_nombre_correo if col_nombre_correo else col_nombre_ubi,
                {'correo': ColumnFinder.find_column(df_correo, ['correo', 'email', 'mail'])}
            )
            telefono_provider = EmployeeDataProvider(
                df_telefono, col_nombre_telefono if col_nombre_telefono else col_nombre_ubi,
                {'telefono': ColumnFinder.find_column(df_telefono, ['telefono', 'tel', 'phone', 'celular'])}
            )
            
            data_merger = DataMerger(ubicacion_provider, correo_provider, telefono_provider)
            datos = data_merger.merge_data(ubicacion_provider.get_all_names())
            df_combinado = pd.DataFrame(datos)
            
            if 'puesto' in df_combinado.columns:
                df_combinado = df_combinado[~df_combinado['puesto'].apply(PositionValidator.is_director)]
            
            return df_combinado
        except Exception as e:
            st.error(f"Error procesando datos: {str(e)}")
            return None
    
    def _create_source_info(self) -> Dict[str, str]:
        ubicacion = self.file_handler.load('ubicacion')
        return {
            'origen_ubicacion': os.path.basename(ubicacion) if ubicacion else "N/A",
            'fecha_actualizacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    # --- MÉTODOS VISUALES PROFESIONALES ---

    def display_contact_card(self, contacto: Dict[str, str]):
        """Muestra tarjeta de contacto con diseño profesional"""
        st.markdown(f"""
        <div class="contact-card-detail">
            <div class="detail-header">
                <span style="font-size: 20px;">👤</span> {contacto['nombre']}
            </div>
        """, unsafe_allow_html=True)

        col_info, col_actions = st.columns([2, 1])

        with col_info:
            puesto = contacto.get('puesto', 'No especificado')
            depto = contacto.get('departamento', 'General')
            ciudad = contacto.get('ciudad', 'No especificada')
            estado = contacto.get('estado', 'No especificado')
            telefono = contacto.get('telefono', 'No disponible')
            correo = contacto.get('correo', 'No disponible')

            st.markdown(f"""
                <div class="detail-row">
                    <span class="detail-label">Posición:</span>
                    <span class="detail-value">{puesto}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Departamento:</span>
                    <span class="detail-value">{depto}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Ubicación:</span>
                    <span class="detail-value">{ciudad}, {estado}</span>
                </div>
                <div class="divider"></div>
                <div class="detail-row">
                    <span class="detail-label">Teléfono:</span>
                    <span class="detail-value">{telefono}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Correo:</span>
                    <span class="detail-value">{correo}</span>
                </div>
            """, unsafe_allow_html=True)

        with col_actions:
            st.markdown("#### Contacto")
            self._display_action_buttons(contacto.get('telefono'), contacto.get('correo'))
        
        st.markdown("</div>", unsafe_allow_html=True)

    def _display_action_buttons(self, telefono: str, correo: str):
        whatsapp_generator = WhatsAppURLGenerator()
        url_whatsapp = whatsapp_generator.generate_url(telefono) if telefono else None
        
        email_generator = EmailURLGenerator()
        url_correo = email_generator.generate_url(correo) if correo else None

        if url_whatsapp:
            st.markdown(f'<a href="{url_whatsapp}" target="_blank" class="action-btn whatsapp-btn">WhatsApp</a>', unsafe_allow_html=True)
        else:
            st.button("WhatsApp", disabled=True, key="btn_wa_dis", use_container_width=True)

        if url_correo:
            st.markdown(f'<a href="{url_correo}" target="_blank" class="action-btn email-btn">Enviar Correo</a>', unsafe_allow_html=True)
        else:
            st.button("Correo", disabled=True, key="btn_em_dis", use_container_width=True)

    def show_search_interface(self, df: pd.DataFrame):
        # Mostrar filtros activos si existen
        self._show_active_filters()
        
        # Panel de búsqueda y filtros
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            def update_search():
                st.session_state.termino_busqueda = st.session_state.busqueda_input_value
                st.session_state.contacto_seleccionado = None
                st.session_state.mostrando_resultados = True
                st.session_state.filtros_activos = bool(
                    st.session_state.busqueda_input_value.strip() or 
                    st.session_state.ciudad_input_value or 
                    st.session_state.estado_input_value
                )
            
            st.text_input(
                "Buscar colaborador",
                placeholder="Nombre, posición o departamento...",
                key="busqueda_input_value",
                value=st.session_state.termino_busqueda,
                on_change=update_search
            )
        
        with col2:
            def update_ciudad():
                st.session_state.filtro_ciudad = st.session_state.ciudad_input_value
                st.session_state.contacto_seleccionado = None
                st.session_state.mostrando_resultados = True
                st.session_state.filtros_activos = True
            
            st.text_input(
                "Ciudad",
                placeholder="Filtrar por ciudad...",
                key="ciudad_input_value",
                value=st.session_state.filtro_ciudad,
                on_change=update_ciudad
            )
        
        with col3:
            def update_estado():
                st.session_state.filtro_estado = st.session_state.estado_input_value
                st.session_state.contacto_seleccionado = None
                st.session_state.mostrando_resultados = True
                st.session_state.filtros_activos = True
            
            st.text_input(
                "Estado",
                placeholder="Filtrar por estado...",
                key="estado_input_value",
                value=st.session_state.filtro_estado,
                on_change=update_estado
            )
        
        with col4:
            st.write("")
            st.write("")
            if st.button("Limpiar filtros", use_container_width=True, key="clear_filters"):
                st.session_state.termino_busqueda = ""
                st.session_state.filtro_ciudad = ""
                st.session_state.filtro_estado = ""
                st.session_state.contacto_seleccionado = None
                st.session_state.mostrando_resultados = False
                st.session_state.filtros_activos = False
                st.rerun()

        # Mostrar contacto seleccionado si existe
        if st.session_state.contacto_seleccionado is not None:
            self.display_contact_card(st.session_state.contacto_seleccionado)
            st.markdown("---")

        if not st.session_state.mostrando_resultados and not st.session_state.filtros_activos:
            # Mostrar estadísticas generales
            self._show_dashboard_stats(df)
            return

        # Realizar búsqueda con filtros
        if st.session_state.filtros_activos:
            resultados = EmployeeSearcher.advanced_search(
                df, 
                st.session_state.termino_busqueda,
                st.session_state.filtro_ciudad,
                st.session_state.filtro_estado
            )
            
            if len(resultados) > 0:
                if st.session_state.contacto_seleccionado is None:
                    st.markdown(f"**Resultados encontrados:** {len(resultados)} colaboradores")
                
                self._display_employee_table(resultados)
                
                st.markdown("---")
                self._export_results(resultados)
            else:
                st.warning("No se encontraron resultados con los filtros aplicados.")

    def _show_active_filters(self):
        """Muestra los filtros activos actualmente"""
        filters = []
        if st.session_state.termino_busqueda:
            filters.append(f"Texto: '{st.session_state.termino_busqueda}'")
        if st.session_state.filtro_ciudad:
            filters.append(f"Ciudad: '{st.session_state.filtro_ciudad}'")
        if st.session_state.filtro_estado:
            filters.append(f"Estado: '{st.session_state.filtro_estado}'")
        
        if filters:
            st.markdown('<div class="filter-container">', unsafe_allow_html=True)
            st.markdown("**Filtros aplicados:**")
            for filtro in filters:
                st.markdown(f'<span class="filter-badge">{filtro}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    def _show_dashboard_stats(self, df: pd.DataFrame):
        """Muestra estadísticas generales del directorio"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de colaboradores", len(df))
        
        with col2:
            if 'ciudad' in df.columns:
                ciudades_unicas = df['ciudad'].nunique()
                st.metric("Ciudades distintas", ciudades_unicas)
        
        with col3:
            if 'estado' in df.columns:
                estados_unicos = df['estado'].nunique()
                st.metric("Estados distintos", estados_unicos)
        
        with col4:
            if 'departamento' in df.columns:
                deptos_unicos = df['departamento'].nunique()
                st.metric("Departamentos", deptos_unicos)
        
        # Mostrar distribuciones
        if 'estado' in df.columns and not df['estado'].empty:
            st.markdown("---")
            st.subheader("Distribución por Estado")
            estado_counts = df['estado'].value_counts().head(15)
            st.bar_chart(estado_counts)
        
        if 'ciudad' in df.columns and not df['ciudad'].empty:
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Top 10 Ciudades")
                ciudad_counts = df['ciudad'].value_counts().head(10)
                st.dataframe(ciudad_counts, use_container_width=True)
            
            with col2:
                st.subheader("Top 10 Departamentos")
                if 'departamento' in df.columns:
                    depto_counts = df['departamento'].value_counts().head(10)
                    st.dataframe(depto_counts, use_container_width=True)

    def _generate_unique_key(self, contacto: Dict[str, str], idx: int) -> str:
        """Genera una clave única para el botón"""
        try:
            contacto_str = f"{contacto.get('nombre', '')}_{contacto.get('puesto', '')}_{contacto.get('departamento', '')}"
            hash_obj = hashlib.md5(contacto_str.encode())
            hash_hex = hash_obj.hexdigest()[:8]
            return f"select_btn_{idx}_{hash_hex}"
        except:
            return f"select_btn_{idx}_{int(time.time() * 1000)}"

    def _display_employee_table(self, resultados: pd.DataFrame):
        """Muestra la tabla de empleados con ubicación"""
        st.markdown("""
            <div style="display: flex; padding: 12px 20px; background: #f1f5f9; border-radius: 8px 8px 0 0; font-weight: 500; color: #475569; font-size: 13px;">
                <div style="flex: 2;">Colaborador</div>
                <div style="flex: 2;">Posición</div>
                <div style="flex: 1;">Departamento</div>
                <div style="flex: 1;">Ubicación</div>
                <div style="flex: 1; text-align: center;">Acción</div>
            </div>
            <div class="employee-list-container">
        """, unsafe_allow_html=True)

        for idx, (_, row) in enumerate(resultados.iterrows()):
            contacto = row.to_dict()
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
            
            with col1:
                st.markdown(f"<div style='padding: 10px 0;'><span class='emp-name'>{contacto['nombre']}</span></div>", unsafe_allow_html=True)
            with col2:
                puesto_safe = contacto.get('puesto', '') or '-'
                st.markdown(f"<div style='padding: 10px 0;'><span class='emp-role'>{puesto_safe}</span></div>", unsafe_allow_html=True)
            with col3:
                depto_safe = contacto.get('departamento', '') or '-'
                st.markdown(f"<div style='padding: 10px 0;'><span class='emp-dept'>{depto_safe}</span></div>", unsafe_allow_html=True)
            with col4:
                ciudad = contacto.get('ciudad', '') or '-'
                estado = contacto.get('estado', '') or ''
                ubicacion_text = f"{ciudad}"
                if estado and estado != '-':
                    ubicacion_text += f", {estado}"
                st.markdown(f"<div style='padding: 10px 0;'><span class='emp-location'>{ubicacion_text}</span></div>", unsafe_allow_html=True)
            with col5:
                button_key = self._generate_unique_key(contacto, idx)
                if st.button("Ver detalles", key=button_key, use_container_width=True):
                    st.session_state.contacto_seleccionado = contacto
                    st.rerun()

            st.markdown("<div style='border-bottom: 1px solid #f1f5f9;'></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    def _export_results(self, resultados: pd.DataFrame):
        """Exporta resultados excluyendo columnas de fuente"""
        if not resultados.empty:
            # Columnas a excluir del reporte
            columnas_a_excluir = ['fuente_ubicacion', 'fuente_correo', 'fuente_telefono']
            columnas_disponibles = [col for col in resultados.columns if col not in columnas_a_excluir]
            
            # Filtrar solo las columnas deseadas
            datos_exportar = resultados[columnas_disponibles].copy()
            
            # Renombrar columnas para mejor presentación
            nombre_columnas = {
                'nombre': 'Nombre',
                'puesto': 'Posición',
                'departamento': 'Departamento',
                'ciudad': 'Ciudad',
                'estado': 'Estado',
                'correo': 'Correo Electrónico',
                'telefono': 'Teléfono'
            }
            
            # Renombrar solo las columnas que existan
            datos_exportar = datos_exportar.rename(columns={
                k: v for k, v in nombre_columnas.items() 
                if k in datos_exportar.columns
            })
            
            csv_data = datos_exportar.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="Descargar reporte (CSV)",
                data=csv_data,
                file_name=f"directorio_empleados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    def show_admin_section(self):
        """Muestra la sección de administrador"""
        if 'password_admin_verified' not in st.session_state:
            st.session_state.password_admin_verified = False
        
        if not st.session_state.password_admin_verified:
            with st.form("admin_login"):
                st.markdown("### Acceso Administrativo")
                password = st.text_input("Credenciales de acceso:", type="password")
                if st.form_submit_button("Autenticar"):
                    if password == self.config.PASSWORD:
                        st.session_state.password_admin_verified = True
                        st.rerun()
                    else:
                        st.error("Credenciales inválidas")
        else:
            col1, col2 = st.columns([3, 1])
            with col1: 
                st.markdown("### Panel de Administración")
                st.caption("Modo administrativo activo")
            with col2:
                if st.button("Cerrar sesión", key="logout"):
                    st.session_state.password_admin_verified = False
                    st.rerun()
            
            st.markdown("---")
            st.markdown("#### Actualización de Datos")
            st.caption("Suba los archivos requeridos para actualizar la base de datos del directorio.")
            st.caption("**Nota:** El archivo de ubicación debe contener información de ciudad y estado.")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                u = st.file_uploader("Estructura organizacional", type=['xlsx','csv'], key="ubicacion_upload")
                if u: 
                    self.file_handler.save(u, 'ubicacion')
                    st.caption(f"Archivo cargado: {u.name}")
            with c2:
                c = st.file_uploader("Directorio de correos", type=['xlsx','csv'], key="correo_upload")
                if c: 
                    self.file_handler.save(c, 'correo')
                    st.caption(f"Archivo cargado: {c.name}")
            with c3:
                t = st.file_uploader("Contactos telefónicos", type=['xlsx','csv'], key="telefono_upload")
                if t: 
                    self.file_handler.save(t, 'telefono')
                    st.caption(f"Archivo cargado: {t.name}")
            
            st.markdown("---")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Procesar y actualizar datos", type="primary", use_container_width=True):
                    if self.file_handler.exists(['ubicacion', 'correo', 'telefono']):
                        with st.spinner("Procesando información..."):
                            df, info = self.load_data_from_temporales()
                            if df is not None:
                                st.session_state.df_combinado = df
                                st.session_state.info_origen = info
                                st.session_state.datos_cargados = True
                                st.session_state.contacto_seleccionado = None
                                st.session_state.termino_busqueda = ""
                                st.session_state.filtro_ciudad = ""
                                st.session_state.filtro_estado = ""
                                st.session_state.filtros_activos = False
                                st.success("Base de datos actualizada correctamente.")
                                time.sleep(1)
                                st.rerun()
                    else:
                        st.error("Se requieren los tres archivos para continuar.")
            
            with col_btn2:
                if st.button("Limpiar sistema", use_container_width=True):
                    self.file_handler.cleanup()
                    st.cache_data.clear()
                    for key in list(st.session_state.keys()): 
                        if key != 'datos_cargados':
                            del st.session_state[key]
                    st.session_state.datos_cargados = False
                    st.success("Sistema reiniciado")
                    st.rerun()

    def show_sidebar(self):
        with st.sidebar:
            st.markdown("### Estado del Sistema")
            
            if st.session_state.datos_cargados:
                st.markdown('<span class="status-badge status-online">Operativo</span>', unsafe_allow_html=True)
                if st.session_state.info_origen:
                    st.caption(f"**Última actualización:**")
                    st.caption(f"{st.session_state.info_origen['fecha_actualizacion']}")
            else:
                st.markdown('<span class="status-badge status-offline">Sin datos</span>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("#### Información")
            st.caption("""
            Este sistema permite la búsqueda y gestión de contactos corporativos.
            
            **Funcionalidades:**
            • Búsqueda por nombre, posición o departamento
            • Filtro por ciudad y estado
            • Contacto directo vía WhatsApp o correo
            • Exportación de resultados
            • Gestión administrativa de datos
            """)
            
            # Si hay datos, mostrar estadísticas rápidas
            if st.session_state.datos_cargados and st.session_state.df_combinado is not None:
                df = st.session_state.df_combinado
                st.markdown("---")
                st.markdown("#### Estadísticas")
                st.caption(f"**Colaboradores:** {len(df)}")
                
                if 'ciudad' in df.columns:
                    ciudades = df['ciudad'].nunique()
                    st.caption(f"**Ciudades:** {ciudades}")
                
                if 'estado' in df.columns:
                    estados = df['estado'].nunique()
                    st.caption(f"**Estados:** {estados}")
            
            st.markdown("---")
            st.caption("Versión 2.0 | Para uso interno")
            
            # Información de acceso
            st.markdown("---")
            st.markdown("#### Acceso Remoto")
            st.code("http://10.10.10.15:8501/directorio")

    def run(self):
        self.setup_ui()
        self.ui_manager.display_header()
        
        # Carga automática al inicio
        if not st.session_state.datos_cargados and self.file_handler.exists(['ubicacion', 'correo', 'telefono']):
            with st.spinner("Inicializando sistema..."):
                df_combinado, info_origen = self.load_data_from_temporales()
                if df_combinado is not None and not df_combinado.empty:
                    st.session_state.df_combinado = df_combinado
                    st.session_state.info_origen = info_origen
                    st.session_state.datos_cargados = True
        
        # Interfaz Principal
        if st.session_state.datos_cargados:
            self.show_search_interface(st.session_state.df_combinado)
        else:
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.markdown("""
                <div style="text-align: center; padding: 3rem 0;">
                    <div style="font-size: 1.2rem; color: #475569; margin-bottom: 1rem;">
                        Bienvenido al Sistema de Directorio Corporativo
                    </div>
                    <div style="color: #64748b; font-size: 0.95rem;">
                        El sistema requiere una carga inicial de datos por parte del administrador.
                    </div>
                    <div style="margin-top: 1rem; padding: 1rem; background: #f1f5f9; border-radius: 8px;">
                        <div style="font-size: 0.9rem; color: #475569; margin-bottom: 0.5rem;">
                            <strong>URL de acceso:</strong>
                        </div>
                        <div style="font-family: monospace; background: white; padding: 0.5rem; border-radius: 4px; border: 1px solid #e2e8f0;">
                            http://10.10.10.15:8501/directorio
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Panel Admin
        with st.expander("Administración del Sistema"):
            self.show_admin_section()
        
        self.show_sidebar()
        self.ui_manager.display_footer()

# =============================================
# EJECUCIÓN PRINCIPAL
# =============================================

if __name__ == "__main__":
    app = EmployeeContactSystem()
    app.run()