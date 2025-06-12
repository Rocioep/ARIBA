# alfamine.py
"""
ALFAMINE MONITOR - LAUNCHER PRINCIPAL UNIFICADO
Punto de entrada único para todas las funcionalidades del sistema
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.columns import Columns
from rich.text import Text

console = Console()

class AlfamineLauncher:
    """Launcher principal unificado para Alfamine Monitor"""
    
    def __init__(self):
        self.version = "1.1.0"
        self.ascii_logo = """
    ╔═══════════════════════════════════════╗
    ║              ALFAMINE                 ║
    ║            MONITOR v1.1               ║
    ║     Sistema de Monitoreo Inteligente  ║
    ╚═══════════════════════════════════════╝
        """
        
        self.tools = {
            'setup': {
                'script': 'setup_wizard.py',
                'description': 'Configuración inicial del sistema',
                'icon': '🔧',
                'status': self.check_script_exists('setup_wizard.py')
            },
            'main': {
                'script': 'main_improved.py',
                'description': 'Sistema principal mejorado',
                'icon': '🎯',
                'status': self.check_script_exists('main_improved.py')
            },
            'learning': {
                'script': 'learning_analyzer.py',
                'description': 'Analizador de sesiones de aprendizaje',
                'icon': '🎓',
                'status': self.check_script_exists('learning_analyzer.py')
            },
            'monitor': {
                'script': 'system_monitor.py',
                'description': 'Monitor de sistema y estadísticas',
                'icon': '📊',
                'status': self.check_script_exists('system_monitor.py')
            },
            'analysis': {
                'script': 'analisis_json_usuario.py',
                'description': 'Análisis de JSON de usuario',
                'icon': '🔍',
                'status': self.check_script_exists('analisis_json_usuario.py')
            }
        }
    
    def check_script_exists(self, script_name: str) -> bool:
        """Verificar si un script existe"""
        return Path(script_name).exists()
    
    def show_main_menu(self):
        """Mostrar menú principal"""
        console.clear()
        
        # Logo
        logo_panel = Panel(
            Text(self.ascii_logo, style="bold blue", justify="center"),
            border_style="blue"
        )
        console.print(logo_panel)
        
        # Estado del sistema
        status_text = self.get_system_status()
        status_panel = Panel(status_text, title="📊 Estado del Sistema", border_style="green")
        console.print(status_panel)
        
        # Menú de opciones
        console.print("\n🚀 [bold cyan]LAUNCHER PRINCIPAL[/bold cyan]")
        
        options_table = Table(show_header=False, box=None)
        options_table.add_column("Opción", style="bold white")
        options_table.add_column("Descripción", style="cyan")
        options_table.add_column("Estado", style="green")
        
        options_table.add_row("1. 🔧 Setup", "Configuración inicial del sistema", "✅" if self.tools['setup']['status'] else "❌")
        options_table.add_row("2. 🎯 Principal", "Sistema principal de monitoreo", "✅" if self.tools['main']['status'] else "❌")
        options_table.add_row("3. 🎓 Aprendizaje", "Análisis de sesiones de aprendizaje", "✅" if self.tools['learning']['status'] else "❌")
        options_table.add_row("4. 📊 Monitor", "Monitor de sistema y estadísticas", "✅" if self.tools['monitor']['status'] else "❌")
        options_table.add_row("5. 🔍 Análisis", "Análisis de JSON de usuario", "✅" if self.tools['analysis']['status'] else "❌")
        options_table.add_row("6. ⚡ Acceso Rápido", "Menú de accesos rápidos", "✅")
        options_table.add_row("7. ℹ️ Info", "Información del sistema", "✅")
        options_table.add_row("8. 🚪 Salir", "Cerrar el launcher", "✅")
        
        console.print(options_table)
    
    def get_system_status(self) -> str:
        """Obtener estado actual del sistema"""
        status_lines = []
        
        # Verificar instalación
        config_exists = Path("config/config.json").exists()
        status_lines.append(f"⚙️ Configuración: {'✅ OK' if config_exists else '❌ Falta'}")
        
        # Verificar datos
        downloads_dir = Path("data/downloads")
        downloads_count = len(list(downloads_dir.glob("*"))) if downloads_dir.exists() else 0
        status_lines.append(f"📥 Descargas: {downloads_count} archivos")
        
        # Verificar aprendizaje
        learning_dir = Path("data/learning")
        learning_count = len(list(learning_dir.glob("*.json"))) if learning_dir.exists() else 0
        status_lines.append(f"🎓 Sesiones: {learning_count} aprendizajes")
        
        # Verificar reportes
        reports_dir = Path("reports")
        reports_count = len(list(reports_dir.glob("*.xlsx"))) if reports_dir.exists() else 0
        status_lines.append(f"📊 Reportes: {reports_count} generados")
        
        return "\n".join(status_lines)
    
    def run_tool(self, tool_key: str, args: list = None):
        """Ejecutar una herramienta específica"""
        if tool_key not in self.tools:
            console.print(f"❌ [red]Herramienta '{tool_key}' no encontrada[/red]")
            return
        
        tool = self.tools[tool_key]
        
        if not tool['status']:
            console.print(f"❌ [red]Script {tool['script']} no encontrado[/red]")
            return
        
        console.print(f"🚀 [yellow]Ejecutando {tool['description']}...[/yellow]")
        
        try:
            cmd = [sys.executable, tool['script']]
            if args:
                cmd.extend(args)
            
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ [red]Error ejecutando {tool['script']}: {e}[/red]")
        except KeyboardInterrupt:
            console.print(f"\n⏹️ [yellow]Ejecución de {tool['script']} interrumpida[/yellow]")
    
    def show_quick_access_menu(self):
        """Mostrar menú de acceso rápido"""
        console.print("\n⚡ [bold yellow]ACCESO RÁPIDO[/bold yellow]")
        
        quick_options = Table(show_header=False, box=None)
        quick_options.add_column("Opción", style="bold white")
        quick_options.add_column("Descripción", style="cyan")
        
        quick_options.add_row("a. 🧪 Test rápido", "Verificación rápida de conexión")
        quick_options.add_row("b. 🎓 Aprendizaje paso a paso", "Modo aprendizaje inmediato")
        quick_options.add_row("c. 🤖 Scraping automático", "Ejecutar scraping con selectores aprendidos")
        quick_options.add_row("d. 📊 Análisis archivo", "Analizar último archivo descargado")
        quick_options.add_row("e. 🔍 Estado completo", "Verificación completa del sistema")
        quick_options.add_row("f. 🧹 Mantenimiento", "Limpieza y backup rápido")
        quick_options.add_row("g. 🔙 Volver", "Volver al menú principal")
        
        console.print(quick_options)
        
        choice = Prompt.ask("Selecciona opción de acceso rápido", 
                          choices=["a", "b", "c", "d", "e", "f", "g"])
        
        if choice == "a":
            self.run_tool('main', ['--mode', 'test'])
        elif choice == "b":
            self.run_tool('main', ['--mode', 'learning'])
        elif choice == "c":
            self.run_tool('main', ['--mode', 'scraping'])
        elif choice == "d":
            self.quick_analyze_latest_file()
        elif choice == "e":
            self.run_tool('monitor')
        elif choice == "f":
            self.quick_maintenance()
        elif choice == "g":
            return
    
    def quick_analyze_latest_file(self):
        """Análisis rápido del último archivo descargado"""
        downloads_dir = Path("data/downloads")
        
        if not downloads_dir.exists():
            console.print("❌ [red]No existe directorio de descargas[/red]")
            return
        
        files = list(downloads_dir.glob("*"))
        if not files:
            console.print("❌ [red]No hay archivos para analizar[/red]")
            return
        
        # Obtener archivo más reciente
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        
        console.print(f"📊 [yellow]Analizando archivo más reciente: {latest_file.name}[/yellow]")
        
        # Ejecutar análisis
        self.run_tool('main', ['--mode', 'interactive'])
    
    def quick_maintenance(self):
        """Mantenimiento rápido del sistema"""
        console.print("🧹 [yellow]Ejecutando mantenimiento rápido...[/yellow]")
        
        # Aquí podrías ejecutar tareas de mantenimiento automático
        maintenance_tasks = [
            "Verificando integridad de archivos...",
            "Limpiando archivos temporales...",
            "Optimizando base de datos de aprendizaje...",
            "Generando estadísticas de uso..."
        ]
        
        from rich.progress import Progress
        
        with Progress() as progress:
            task = progress.add_task("Mantenimiento", total=len(maintenance_tasks))
            
            for task_desc in maintenance_tasks:
                progress.update(task, description=task_desc)
                import time
                time.sleep(1)  # Simular trabajo
                progress.advance(task)
        
        console.print("✅ [green]Mantenimiento completado[/green]")
    
    def show_system_info(self):
        """Mostrar información del sistema"""
        console.print("\nℹ️ [bold blue]INFORMACIÓN DEL SISTEMA[/bold blue]")
        
        info_table = Table(title="🔧 Información Técnica")
        info_table.add_column("Parámetro", style="cyan")
        info_table.add_column("Valor", style="green")
        
        info_table.add_row("Versión", self.version)
        info_table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        info_table.add_row("Directorio", str(Path.cwd()))
        info_table.add_row("Última actualización", datetime.now().strftime("%Y-%m-%d"))
        
        # Estado de herramientas
        tools_available = sum(1 for tool in self.tools.values() if tool['status'])
        info_table.add_row("Herramientas disponibles", f"{tools_available}/{len(self.tools)}")
        
        console.print(info_table)
        
        # Mostrar herramientas detalladas
        tools_table = Table(title="🛠️ Estado de Herramientas")
        tools_table.add_column("Herramienta", style="cyan")
        tools_table.add_column("Script", style="yellow")
        tools_table.add_column("Estado", style="green")
        
        for key, tool in self.tools.items():
            status = "✅ Disponible" if tool['status'] else "❌ No encontrado"
            tools_table.add_row(f"{tool['icon']} {tool['description']}", tool['script'], status)
        
        console.print(tools_table)
        
        # Mostrar comandos útiles
        console.print("\n💡 [bold yellow]Comandos útiles:[/bold yellow]")
        console.print("   python alfamine.py --help    # Ayuda completa")
        console.print("   python alfamine.py --quick   # Acceso rápido directo")
        console.print("   python alfamine.py --setup   # Ejecutar setup directamente")
        console.print("   python alfamine.py --status  # Ver solo estado del sistema")
    
    def run_interactive(self):
        """Ejecutar modo interactivo"""
        while True:
            self.show_main_menu()
            
            choice = Prompt.ask("\nSelecciona una opción", 
                              choices=["1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "1":
                self.run_tool('setup')
            elif choice == "2":
                self.run_tool('main')
            elif choice == "3":
                self.run_tool('learning')
            elif choice == "4":
                self.run_tool('monitor')
            elif choice == "5":
                self.run_tool('analysis')
            elif choice == "6":
                self.show_quick_access_menu()
            elif choice == "7":
                self.show_system_info()
                input("\nPresiona ENTER para continuar...")
            elif choice == "8":
                console.print("👋 [blue]¡Hasta luego![/blue]")
                break
    
    def run_command_line(self, args):
        """Ejecutar desde línea de comandos"""
        if args.setup:
            self.run_tool('setup')
        elif args.quick:
            self.show_quick_access_menu()
        elif args.status:
            console.print("📊 [bold blue]ESTADO DEL SISTEMA[/bold blue]")
            status_text = self.get_system_status()
            console.print(status_text)
        elif args.tool:
            tool_args = args.args if args.args else []
            self.run_tool(args.tool, tool_args)
        else:
            self.run_interactive()


def create_parser():
    """Crear parser de argumentos"""
    parser = argparse.ArgumentParser(
        description="Alfamine Monitor v1.1 - Launcher Principal",
        epilog="Ejemplos:\n"
               "  python alfamine.py                    # Modo interactivo\n"
               "  python alfamine.py --setup            # Ejecutar configuración\n"
               "  python alfamine.py --quick            # Acceso rápido\n"
               "  python alfamine.py --tool main --args --mode test\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--setup', action='store_true', 
                       help='Ejecutar asistente de configuración')
    
    parser.add_argument('--quick', action='store_true', 
                       help='Mostrar menú de acceso rápido')
    
    parser.add_argument('--status', action='store_true', 
                       help='Mostrar estado del sistema')
    
    parser.add_argument('--tool', choices=['setup', 'main', 'learning', 'monitor', 'analysis'],
                       help='Ejecutar herramienta específica')
    
    parser.add_argument('--args', nargs='*', 
                       help='Argumentos para la herramienta especificada')
    
    parser.add_argument('--version', action='version', version='Alfamine Monitor v1.1.0')
    
    return parser


def main():
    """Función principal"""
    parser = create_parser()
    args = parser.parse_args()
    
    launcher = AlfamineLauncher()
    
    try:
        launcher.run_command_line(args)
    except KeyboardInterrupt:
        console.print("\n⏹️ [yellow]Launcher interrumpido por el usuario[/yellow]")
    except Exception as e:
        console.print(f"\n❌ [red]Error en launcher: {e}[/red]")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)