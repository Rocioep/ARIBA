"""
🚀 ALFAMINE MONITOR - Paquete Principal
Sistema avanzado de monitoreo de licitaciones Ariba

Autor: Sistema Alfamine
Versión: 2.0
Fecha: 2025-06-11
"""

# =====================================
# 📦 IMPORTACIONES PRINCIPALES
# =====================================

# Versión del paquete
__version__ = "2.0.0"
__author__ = "Sistema Alfamine"
__description__ = "Sistema avanzado de monitoreo de licitaciones Ariba"

# =====================================
# 🔧 IMPORTACIONES DE MÓDULOS CORE
# =====================================

try:
    # Motor principal de scraping
    from .scraper_engine_improved import ScraperEngine
    
    # Sistema de análisis
    from .analyzer import Analyzer
    
    # Sistema de notificaciones  
    from .notifier import Notifier
    
    # ✅ Imports exitosos
    _imports_successful = True
    
except ImportError as e:
    # ⚠️ Fallback a versiones legacy si las nuevas fallan
    print(f"⚠️  Advertencia: No se pudo importar módulo mejorado: {e}")
    print("🔄 Cargando versión de respaldo...")
    
    try:
        # Intentar cargar versiones legacy
        from .scraper_engine import ScraperEngine
        from .analyzer import Analyzer  
        from .notifier import Notifier
        _imports_successful = True
        
    except ImportError as fallback_error:
        print(f"❌ Error crítico: {fallback_error}")
        _imports_successful = False

# =====================================
# 🎯 CONFIGURACIÓN GLOBAL
# =====================================

# Configuración por defecto
DEFAULT_CONFIG = {
    "browser": "firefox",
    "headless": False,
    "timeout": 30,
    "retry_attempts": 3,
    "screenshot_enabled": True,
    "learning_mode": True,
    "debug_level": "INFO"
}

# =====================================
# 🚀 FUNCIONES DE UTILIDAD
# =====================================

def get_version():
    """Retorna la versión actual del sistema"""
    return __version__

def check_system_status():
    """Verifica el estado del sistema"""
    status = {
        "version": __version__,
        "imports_successful": _imports_successful,
        "modules_available": []
    }
    
    # Verificar módulos disponibles
    modules_to_check = ["scraper_engine_improved", "analyzer", "notifier"]
    
    for module in modules_to_check:
        try:
            __import__(f"src.{module}")
            status["modules_available"].append(module)
        except ImportError:
            pass
    
    return status

def initialize_system(config=None):
    """
    Inicializa el sistema completo
    
    Args:
        config (dict): Configuración personalizada
        
    Returns:
        dict: Componentes inicializados
    """
    if not _imports_successful:
        raise ImportError("❌ No se pudieron cargar los módulos necesarios")
    
    # Usar configuración por defecto si no se proporciona
    if config is None:
        config = DEFAULT_CONFIG.copy()
    
    # Inicializar componentes
    components = {}
    
    try:
        components["scraper"] = ScraperEngine(config)
        components["analyzer"] = Analyzer(config)
        components["notifier"] = Notifier(config)
        
        print("✅ Sistema inicializado exitosamente")
        
    except Exception as e:
        print(f"❌ Error al inicializar sistema: {e}")
        raise
    
    return components

# =====================================
# 📋 EXPORTS PÚBLICOS
# =====================================

# Lo que se exporta cuando se hace "from src import *"
__all__ = [
    # Clases principales
    "ScraperEngine",
    "Analyzer", 
    "Notifier",
    
    # Funciones utiles
    "get_version",
    "check_system_status",
    "initialize_system",
    
    # Configuraciones
    "DEFAULT_CONFIG",
    
    # Metadatos
    "__version__",
    "__author__",
    "__description__"
]

# =====================================
# 🔍 DIAGNÓSTICO INICIAL
# =====================================

# Ejecutar diagnóstico al importar (solo si no es importación silenciosa)
import sys
if not any(arg in sys.argv for arg in ['--quiet', '-q', '--silent']):
    try:
        status = check_system_status()
        if status["imports_successful"]:
            print(f"🚀 Alfamine Monitor v{status['version']} - Listo")
            print(f"📦 Módulos disponibles: {', '.join(status['modules_available'])}")
        else:
            print("⚠️  Alfamine Monitor - Modo de compatibilidad")
    except:
        # Silenciar errores de diagnóstico
        pass