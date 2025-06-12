# main_improved.py
"""
ALFAMINE MONITOR v1.1 - SISTEMA PRINCIPAL MEJORADO
Con aprendizaje paso a paso basado en acciones reales del usuario
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
from rich.prompt import Prompt, Confirm

# Loguru para logging profesional
from loguru import logger

# Importar el motor mejorado
try:
    from src.scraper_engine_improved import ImprovedAribaScraperEngine
    from src.analyzer import OpportunityAnalyzer
    from src.notifier import EmailNotifier
except ImportError as e:
    logger.error(f"❌ Error importando módulos: {e}")
    sys.exit(1)

console = Console()

class ImprovedAlfamineMonitor:
    """Clase principal del sistema Alfamine Monitor MEJORADO"""
    
    def __init__(self):
        self.version = "1.1.0 - Learning Enhanced"
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
        logger.remove()
        
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
        
        logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{message}</cyan>",
            level="INFO"
        )
        
        logger.info("🚀 Sistema de logging iniciado - VERSIÓN MEJORADA")
    
    def load_configuration(self):
        """Cargar configuración desde config.json"""
        try:
            config_path = Path("config/config.json")
            
            if not config_path.exists():
                console.print("❌ [red]No se encontró config/config.json[/red]")
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
                        "ALFAMINE": ["ZAPATA", "CADENA", "RODILLOS", "SPROCKET", "RUEDA TENSORA", "GEARBOX", "REDUCTOR", "MANDO FINAL", "MF"]
                    },
                    "perneria": {
                        "keywords": ["PERNO", "TUERCA", "NUT", "BOLT", "CHAVETA", "SCREW"],
                        "prefijos": ["AL00"]
                    },
                    "marcas": ["KRESS", "CAT", "CATERPILLAR", "KOMATSU"]
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
[dim]Sistema Inteligente con Aprendizaje Mejorado[/dim]

[green]✅ Usuario:[/green] {self.config['ariba_credentials']['username']}
[green]✅ Keywords:[/green] {self.count_keywords()} configuradas
[yellow]🎓 Nuevo:[/yellow] Aprendizaje paso a paso
[yellow]🔧 Nuevo:[/yellow] Selectores mejorados de JSON
[green]✅ Logs:[/green] data/logs/ | [green]Reportes:[/green] reports/
        """
        
        panel = Panel(banner_text, title="🚀 Sistema Mejorado", border_style="blue")
        console.print(panel)
    
    def count_keywords(self):
        """Contar total de keywords configuradas"""
        try:
            search_criteria = self.config.get('search_criteria', {})
            total = 0
            
            lineas = search_criteria.get('lineas_producto', {})
            for productos in lineas.values():
                total += len(productos)
            
            perneria = search_criteria.get('perneria', {})
            total += len(perneria.get('keywords', []))
            total += len(perneria.get('prefijos', []))
            
            total += len(search_criteria.get('marcas', []))
            
            return total
            
        except Exception:
            return 0
    
    def initialize_components(self):
        """Inicializar componentes del sistema MEJORADO"""
        try:
            logger.info("🔧 Inicializando componentes mejorados...")
            
            # Scraper engine MEJORADO
            self.scraper = ImprovedAribaScraperEngine(self.config)
            logger.info("✅ Scraper engine MEJORADO iniciado")
            
            # Analyzer (sin cambios)
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
    
    def run_interactive_mode(self):
        """Ejecutar en modo interactivo MEJORADO"""
        console.print("🎮 [cyan]Modo interactivo MEJORADO activado[/cyan]")
        
        while True:
            console.print("\n📋 [bold]Opciones disponibles:[/bold]")
            console.print("1. 🧪 Modo de prueba básico")
            console.print("2. 🎓 Modo aprendizaje PASO A PASO [NUEVO]")
            console.print("3. 🤖 Scraping con selectores mejorados")
            console.print("4. 📊 Analizar archivo existente")
            console.print("5. ⚙️ Ver configuración")
            console.print("6. 📈 Ver estadísticas de aprendizaje")
            console.print("7. 🚪 Salir")
            
            choice = Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "4", "5", "6", "7"])
            
            if choice == "1":
                self.run_test_mode()
            elif choice == "2":
                self.run_step_by_step_learning()
            elif choice == "3":
                self.run_improved_scraping()
            elif choice == "4":
                self.analyze_existing_file()
            elif choice == "5":
                self.display_configuration()
            elif choice == "6":
                self.show_learning_stats()
            elif choice == "7":
                console.print("👋 [blue]¡Hasta luego![/blue]")
                break
    
    def run_test_mode(self):
        """Ejecutar en modo de prueba básico"""
        console.print("🧪 [yellow]Modo de prueba básico[/yellow]")
        
        try:
            if not self.initialize_components():
                return False
            
            console.print("⚙️ Verificando configuración...")
            console.print("✅ [green]Configuración OK[/green]")
            
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
    
    def run_step_by_step_learning(self):
        """Ejecutar modo de aprendizaje PASO A PASO"""
        console.print("🎓 [yellow]Modo aprendizaje PASO A PASO[/yellow]")
        console.print("📝 En este modo TÚ ejecutas paso a paso y el sistema aprende cada acción")
        
        if not self.initialize_components():
            return False
        
        try:
            # Confirmar que el usuario entiende el proceso
            console.print("\n📋 [bold]¿Cómo funciona?[/bold]")
            console.print("1. 🤖 El sistema hace LOGIN automáticamente")
            console.print("2. 🎯 TE GUÍA paso a paso para cada acción")
            console.print("3. 📸 CAPTURA cada estado antes y después de tus clicks")
            console.print("4. 🧠 APRENDE los selectores correctos de tus acciones")
            console.print("5. 💾 GUARDA todo para uso futuro")
            
            if not Confirm.ask("\n¿Quieres continuar con el aprendizaje paso a paso?"):
                return
            
            # Ejecutar aprendizaje paso a paso
            learning_results = self.scraper.run_step_by_step_learning()
            
            console.print("🎓 [green]Sesión de aprendizaje paso a paso completada[/green]")
            console.print(f"✅ Pasos completados: {learning_results.get('total_steps', 0)}")
            
            # Mostrar resumen de lo aprendido
            if learning_results.get('steps'):
                console.print("\n📊 [bold]Resumen de aprendizaje:[/bold]")
                for step in learning_results['steps']:
                    step_name = step.get('name', 'desconocido')
                    method = step.get('method', 'manual')
                    success = step.get('success', False) if 'success' in step else True
                    
                    status = "✅" if success else "❌"
                    console.print(f"  {status} Paso {step['step']}: {step_name} ({method})")
            
            return True
            
        except Exception as e:
            console.print(f"❌ [red]Error en aprendizaje paso a paso: {e}[/red]")
            return False
    
    def run_improved_scraping(self):
        """Ejecutar scraping con selectores mejorados"""
        console.print("🤖 [cyan]Scraping con selectores mejorados[/cyan]")
        console.print("🔧 Usando selectores aprendidos de sesiones anteriores")
        
        if not self.initialize_components():
            return False
        
        try:
            # Ejecutar scraping completo con selectores mejorados
            downloaded_file = self.scraper.run_complete_scraping_improved()
            
            if downloaded_file:
                console.print(f"✅ [green]Archivo descargado: {downloaded_file.name}[/green]")
                
                # Analizar archivo automáticamente
                if Confirm.ask("¿Quieres analizar el archivo descargado ahora?"):
                    opportunities = self.analyzer.analyze_file(downloaded_file)
                    
                    if opportunities:
                        report_file = self.analyzer.generate_report(opportunities)
                        if report_file:
                            console.print(f"📊 [green]Reporte generado: {report_file.name}[/green]")
                    
                    return True
            else:
                console.print("❌ [red]No se pudo descargar archivo[/red]")
                return False
                
        except Exception as e:
            console.print(f"❌ [red]Error en scraping mejorado: {e}[/red]")
            return False
    
    def analyze_existing_file(self):
        """Analizar un archivo existente"""
        console.print("📊 [cyan]Analizar archivo existente[/cyan]")
        
        # Buscar archivos en directorio de descargas
        downloads_dir = Path("data/downloads")
        if not downloads_dir.exists():
            console.print("❌ [red]No existe directorio de descargas[/red]")
            return
        
        files = list(downloads_dir.glob("*"))
        excel_files = [f for f in files if f.suffix.lower() in ['.xlsx', '.xls', '.csv', '.html']]
        
        if not excel_files:
            console.print("❌ [red]No se encontraron archivos para analizar[/red]")
            return
        
        # Mostrar archivos disponibles
        console.print("\n📁 [bold]Archivos disponibles:[/bold]")
        for i, file in enumerate(excel_files[:10], 1):  # Mostrar máximo 10
            size_mb = file.stat().st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            console.print(f"  {i}. {file.name} ({size_mb:.1f} MB, {modified})")
        
        if len(excel_files) > 10:
            console.print(f"  ... y {len(excel_files) - 10} archivos más")
        
        # Seleccionar archivo
        try:
            choice = int(Prompt.ask("Selecciona número de archivo", default="1"))
            if 1 <= choice <= len(excel_files):
                selected_file = excel_files[choice - 1]
                
                if not self.initialize_components():
                    return
                
                # Analizar archivo
                console.print(f"📊 Analizando: {selected_file.name}")
                opportunities = self.analyzer.analyze_file(selected_file)
                
                if opportunities:
                    # Generar reporte
                    report_file = self.analyzer.generate_report(opportunities)
                    if report_file:
                        console.print(f"✅ [green]Reporte generado: {report_file.name}[/green]")
                        
                        # Mostrar estadísticas rápidas
                        oro = len([o for o in opportunities if o['classification'] == 'ORO'])
                        plata = len([o for o in opportunities if o['classification'] == 'PLATA'])
                        console.print(f"🏆 Oro: {oro} | 🥈 Plata: {plata} | 📊 Total: {len(opportunities)}")
                else:
                    console.print("❌ [red]No se encontraron oportunidades[/red]")
            else:
                console.print("❌ [red]Número inválido[/red]")
                
        except ValueError:
            console.print("❌ [red]Entrada inválida[/red]")
    
    def display_configuration(self):
        """Mostrar configuración actual"""
        config_table = Table(title="⚙️ Configuración Actual")
        config_table.add_column("Parámetro", style="cyan")
        config_table.add_column("Valor", style="green")
        
        config_table.add_row("Versión", self.version)
        config_table.add_row("Usuario Ariba", self.config['ariba_credentials']['username'])
        config_table.add_row("Total Keywords", str(self.count_keywords()))
        config_table.add_row("Gmail Habilitado", str(self.config.get('notifications', {}).get('gmail_enabled', False)))
        
        # Mostrar estadísticas de aprendizaje
        learning_dir = Path("data/learning")
        if learning_dir.exists():
            learning_files = list(learning_dir.glob("*.json"))
            config_table.add_row("Sesiones de Aprendizaje", str(len(learning_files)))
        
        console.print(config_table)
    
    def show_learning_stats(self):
        """Mostrar estadísticas de aprendizaje"""
        console.print("📈 [cyan]Estadísticas de Aprendizaje[/cyan]")
        
        learning_dir = Path("data/learning")
        if not learning_dir.exists():
            console.print("❌ [red]No hay datos de aprendizaje disponibles[/red]")
            return
        
        learning_files = list(learning_dir.glob("*.json"))
        
        if not learning_files:
            console.print("❌ [red]No se encontraron archivos de aprendizaje[/red]")
            return
        
        # Tabla de estadísticas
        stats_table = Table(title="📊 Estadísticas de Aprendizaje")
        stats_table.add_column("Archivo", style="cyan")
        stats_table.add_column("Fecha", style="green")
        stats_table.add_column("Tipo", style="yellow")
        stats_table.add_column("Estado", style="blue")
        
        for file in sorted(learning_files, key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Determinar tipo de sesión
                if "step_by_step" in file.name:
                    session_type = "Paso a Paso"
                elif "elements_" in file.name:
                    session_type = "Elementos"
                elif "corporation_selection" in file.name:
                    session_type = "Corporación"
                else:
                    session_type = "General"
                
                # Determinar estado
                if data.get('error'):
                    status = "❌ Error"
                elif data.get('success') or data.get('total_steps', 0) > 0:
                    status = "✅ Exitoso"
                else:
                    status = "⚠️ Parcial"
                
                modified = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                
                stats_table.add_row(
                    file.name[:30],
                    modified,
                    session_type,
                    status
                )
                
            except Exception as e:
                stats_table.add_row(
                    file.name[:30],
                    "Error",
                    "Desconocido",
                    f"❌ {str(e)[:20]}"
                )
        
        console.print(stats_table)
        console.print(f"\n💾 Total archivos de aprendizaje: {len(learning_files)}")


def create_argument_parser():
    """Crear parser de argumentos mejorado"""
    parser = argparse.ArgumentParser(
        description="Alfamine Monitor v1.1 - Sistema de Monitoreo con Aprendizaje Mejorado",
        epilog="Ejemplo: python main_improved.py --mode learning"
    )
    
    parser.add_argument(
        "--mode",
        choices=["test", "interactive", "learning", "scraping"],
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
    """Función principal mejorada"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        # Crear instancia del monitor MEJORADO
        monitor = ImprovedAlfamineMonitor()
        
        # Ejecutar según modo
        if args.mode == "test":
            logger.info("🧪 Modo de prueba")
            monitor.run_test_mode()
        
        elif args.mode == "learning":
            logger.info("🎓 Modo aprendizaje paso a paso")
            monitor.run_step_by_step_learning()
        
        elif args.mode == "scraping":
            logger.info("🤖 Modo scraping mejorado")
            monitor.run_improved_scraping()
        
        elif args.mode == "interactive":
            logger.info("🎮 Modo interactivo mejorado")
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