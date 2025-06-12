# main.py
"""
ALFAMINE MONITOR v1.0 - SISTEMA PRINCIPAL
Monitoreo inteligente de licitaciones Ariba para Alfamine
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Agregar directorio actual al path de Python
sys.path.append(str(Path(__file__).parent))

# Rich para UI bonita
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from rich.prompt import Prompt, Confirm

# Loguru para logging profesional
from loguru import logger

# Nuestros módulos con imports corregidos
try:
    from src.scraper_engine import AribaScraperEngine
    from src.analyzer import OpportunityAnalyzer
    from src.notifier import EmailNotifier
except ImportError as e:
    # Fallback si no funciona la importación normal
    import importlib.util
    
    # Cargar scraper_engine
    scraper_spec = importlib.util.spec_from_file_location("scraper_engine", "src/scraper_engine.py")
    scraper_module = importlib.util.module_from_spec(scraper_spec)
    scraper_spec.loader.exec_module(scraper_module)
    AribaScraperEngine = scraper_module.AribaScraperEngine
    
    # Cargar analyzer
    analyzer_spec = importlib.util.spec_from_file_location("analyzer", "src/analyzer.py")
    analyzer_module = importlib.util.module_from_spec(analyzer_spec)
    analyzer_spec.loader.exec_module(analyzer_module)
    OpportunityAnalyzer = analyzer_module.OpportunityAnalyzer
    
    # Cargar notifier
    notifier_spec = importlib.util.spec_from_file_location("notifier", "src/notifier.py")
    notifier_module = importlib.util.module_from_spec(notifier_spec)
    notifier_spec.loader.exec_module(notifier_module)
    EmailNotifier = notifier_module.EmailNotifier

console = Console()

class AlfamineMonitor:
    """Clase principal del sistema Alfamine Monitor"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.config = None
        self.scraper = None
        self.analyzer = None
        self.notifier = None
        
        # Setup inicial
        self.setup_logging()
        self.load_configuration()
        self.display_banner()
    
    def setup_logging(self):
        """Configurar sistema de logging profesional"""
        # Remover logger por defecto
        logger.remove()
        
        # Log a archivo con rotación
        log_file = Path("data/logs") / f"alfamine_{datetime.now():%Y%m%d}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
        
        # Log a consola (solo INFO y superior)
        logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{message}</cyan>",
            level="INFO"
        )
        
        logger.info("🚀 Sistema de logging iniciado")
    
    def load_configuration(self):
        """Cargar configuración desde config.json"""
        try:
            config_path = Path("config/config.json")
            
            if not config_path.exists():
                console.print("❌ [red]No se encontró config/config.json[/red]")
                console.print("💡 [yellow]Crea el archivo con tus credenciales de Ariba[/yellow]")
                
                # Crear config básico si no existe
                self.create_basic_config()
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            logger.info("✅ Configuración cargada exitosamente")
            
            # Validar configuración crítica
            required_keys = ['ariba_credentials']
            for key in required_keys:
                if key not in self.config:
                    raise ValueError(f"Falta configuración requerida: {key}")
            
            logger.info("✅ Configuración validada")
            
        except Exception as e:
            logger.error(f"❌ Error cargando configuración: {e}")
            console.print(f"❌ [red]Error en configuración: {e}[/red]")
            self.create_basic_config()
    
    def create_basic_config(self):
        """Crear configuración básica si no existe"""
        try:
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            
            basic_config = {
                "ariba_credentials": {
                    "username": "sales@alfamine.cl",
                    "password": "VI.2024al..al.",
                    "url": "https://service.ariba.com/Sourcing.aw/109555009/aw?awh=r&awssk=XZHPCxm2&dard=1"
                },
                "search_criteria": {
                    "lineas_producto": {
                        "ALFAMINE": ["ZAPATA", "CADENA", "RODILLOS", "SPROCKET"]
                    },
                    "perneria": {
                        "keywords": ["PERNO", "TUERCA", "BOLT"],
                        "prefijos": ["AL00"]
                    },
                    "marcas": ["CAT", "KOMATSU"]
                },
                "scraping": {
                    "browser_type": "firefox",
                    "headless": False,
                    "timeout": 30,
                    "max_retries": 3
                },
                "notifications": {
                    "gmail_enabled": False,
                    "recipients": ["sales@alfamine.cl"]
                }
            }
            
            with open("config/config.json", 'w', encoding='utf-8') as f:
                json.dump(basic_config, f, indent=4, ensure_ascii=False)
            
            self.config = basic_config
            console.print("✅ [green]Configuración básica creada en config/config.json[/green]")
            logger.info("✅ Configuración básica creada")
            
        except Exception as e:
            logger.error(f"❌ Error creando configuración básica: {e}")
            console.print(f"❌ [red]Error creando configuración: {e}[/red]")
            sys.exit(1)
    
    def display_banner(self):
        """Mostrar banner inicial del sistema"""
        banner_text = f"""
[bold blue]🎯 ALFAMINE MONITOR v{self.version}[/bold blue]
[dim]Sistema Inteligente de Monitoreo de Licitaciones[/dim]

[green]✅ Usuario:[/green] {self.config['ariba_credentials']['username']}
[green]✅ Keywords:[/green] {self.count_keywords()} configuradas
[green]✅ Logs:[/green] data/logs/
[green]✅ Reportes:[/green] reports/
        """
        
        panel = Panel(banner_text, title="🚀 Sistema Iniciado", border_style="blue")
        console.print(panel)
    
    def count_keywords(self):
        """Contar total de keywords configuradas"""
        try:
            search_criteria = self.config.get('search_criteria', {})
            total = 0
            
            # Contar líneas de producto
            lineas = search_criteria.get('lineas_producto', {})
            for productos in lineas.values():
                total += len(productos)
            
            # Contar pernería
            perneria = search_criteria.get('perneria', {})
            total += len(perneria.get('keywords', []))
            total += len(perneria.get('prefijos', []))
            
            # Contar marcas
            total += len(search_criteria.get('marcas', []))
            
            return total
            
        except Exception:
            return 0
    
    def initialize_components(self):
        """Inicializar componentes del sistema"""
        try:
            logger.info("🔧 Inicializando componentes...")
            
            # Scraper engine
            self.scraper = AribaScraperEngine(self.config)
            logger.info("✅ Scraper engine iniciado")
            
            # Analyzer
            self.analyzer = OpportunityAnalyzer(self.config)
            logger.info("✅ Analyzer iniciado")
            
            # Notifier (si está habilitado)
            if self.config.get('notifications', {}).get('gmail_enabled', False):
                self.notifier = EmailNotifier(self.config)
                logger.info("✅ Email notifier iniciado")
            else:
                logger.info("📧 Email notifier deshabilitado")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando componentes: {e}")
            console.print(f"❌ [red]Error inicializando componentes: {e}[/red]")
            return False
    
    def run_test_mode(self):
        """Ejecutar en modo de prueba"""
        console.print("🧪 [yellow]Modo de prueba activado[/yellow]")
        
        try:
            if not self.initialize_components():
                return False
            
            # Test de configuración
            console.print("⚙️ Verificando configuración...")
            console.print("✅ [green]Configuración OK[/green]")
            
            # Test de conexión
            console.print("🔍 Probando conexión a Ariba...")
            if self.scraper.test_connection():
                console.print("✅ [green]Conexión exitosa[/green]")
            else:
                console.print("❌ [red]Error de conexión[/red]")
                return False
            
            console.print("🎉 [green]Modo de prueba completado exitosamente[/green]")
            return True
            
        except Exception as e:
            console.print(f"❌ [red]Error en modo de prueba: {e}[/red]")
            logger.error(f"❌ Error en modo de prueba: {e}")
            return False
    
    def run_interactive_mode(self):
        """Ejecutar en modo interactivo"""
        console.print("🎮 [cyan]Modo interactivo activado[/cyan]")
        
        while True:
            console.print("\n📋 [bold]Opciones disponibles:[/bold]")
            console.print("1. 🧪 Modo de prueba")
            console.print("2. 🤝 Modo colaborativo (captura)")
            console.print("3. ⚙️ Ver configuración")
            console.print("4. 🚪 Salir")
            
            choice = Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "4"])
            
            if choice == "1":
                self.run_test_mode()
            elif choice == "2":
                self.run_collaborative_mode()
            elif choice == "3":
                self.display_configuration()
            elif choice == "4":
                console.print("👋 [blue]¡Hasta luego![/blue]")
                break
    
    def run_collaborative_mode(self):
        """Modo colaborativo para captura de selectores"""
        console.print("🤝 [yellow]Modo colaborativo activado[/yellow]")
        console.print("📝 En este modo TÚ ejecutas manualmente y el sistema aprende")
        
        if not self.initialize_components():
            return False
        
        try:
            # Ejecutar captura colaborativa
            learning_results = self.scraper.run_learning_mode()
            
            console.print("🎓 [green]Sesión de aprendizaje completada[/green]")
            console.print(f"✅ Selectores exitosos: {len(learning_results.get('successful_selectors', {}))}")
            console.print(f"⚠️ Pasos fallidos: {len(learning_results.get('failed_steps', []))}")
            
            return True
            
        except Exception as e:
            console.print(f"❌ [red]Error en modo colaborativo: {e}[/red]")
            return False
    
    def display_configuration(self):
        """Mostrar configuración actual"""
        config_table = Table(title="⚙️ Configuración Actual")
        config_table.add_column("Parámetro", style="cyan")
        config_table.add_column("Valor", style="green")
        
        config_table.add_row("Usuario Ariba", self.config['ariba_credentials']['username'])
        config_table.add_row("Total Keywords", str(self.count_keywords()))
        config_table.add_row("Gmail Habilitado", str(self.config.get('notifications', {}).get('gmail_enabled', False)))
        config_table.add_row("Versión", self.version)
        
        console.print(config_table)


def create_argument_parser():
    """Crear parser de argumentos"""
    parser = argparse.ArgumentParser(
        description="Alfamine Monitor v1.0 - Sistema de Monitoreo de Licitaciones",
        epilog="Ejemplo: python main.py --mode test"
    )
    
    parser.add_argument(
        "--mode",
        choices=["test", "interactive", "collaborative"],
        default="interactive",
        help="Modo de ejecución (default: interactive)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Output detallado"
    )
    
    return parser


def main():
    """Función principal"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        # Crear instancia del monitor
        monitor = AlfamineMonitor()
        
        # Ejecutar según modo
        if args.mode == "test":
            logger.info("🧪 Modo de prueba")
            monitor.run_test_mode()
        
        elif args.mode == "collaborative":
            logger.info("🤝 Modo colaborativo")
            monitor.run_collaborative_mode()
        
        elif args.mode == "interactive":
            logger.info("🎮 Modo interactivo")
            monitor.run_interactive_mode()
    
    except KeyboardInterrupt:
        console.print("\n⏹️ [yellow]Proceso interrumpido por el usuario[/yellow]")
        logger.info("⏹️ Proceso interrumpido por usuario")
    
    except Exception as e:
        console.print(f"\n💥 [red]Error fatal: {e}[/red]")
        logger.error(f"💥 Error fatal: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)