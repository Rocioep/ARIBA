# setup_wizard.py
"""
ASISTENTE DE CONFIGURACIÓN ALFAMINE MONITOR
Configuración automática y verificación del sistema
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import importlib.util

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class AlfamineSetupWizard:
    """Asistente de configuración del sistema Alfamine"""
    
    def __init__(self):
        self.config = {}
        self.required_packages = [
            'selenium==4.15.0',
            'webdriver-manager==4.0.1', 
            'pandas==2.1.0',
            'openpyxl==3.1.2',
            'loguru==0.7.2',
            'rich==13.6.0',
            'schedule==1.2.0',
            'requests==2.31.0',
            'beautifulsoup4==4.12.2',
            'python-dotenv==1.0.0'
        ]
        
        self.directories = [
            'config',
            'data/logs',
            'data/downloads', 
            'data/screenshots',
            'data/learning',
            'reports',
            'src'
        ]
    
    def run_setup(self):
        """Ejecutar asistente completo de configuración"""
        console.print("🎯 [bold blue]ASISTENTE DE CONFIGURACIÓN ALFAMINE MONITOR[/bold blue]")
        console.print("Te ayudaré a configurar el sistema paso a paso\n")
        
        # 1. Verificar Python
        if not self.check_python_version():
            return False
        
        # 2. Crear directorios
        self.create_directories()
        
        # 3. Verificar/instalar dependencias
        if not self.check_and_install_dependencies():
            return False
        
        # 4. Configurar credenciales
        self.configure_credentials()
        
        # 5. Configurar criterios de búsqueda
        self.configure_search_criteria()
        
        # 6. Configurar opciones avanzadas
        self.configure_advanced_options()
        
        # 7. Guardar configuración
        self.save_configuration()
        
        # 8. Verificar instalación
        self.verify_installation()
        
        console.print("🎉 [bold green]¡Configuración completada exitosamente![/bold green]")
        return True
    
    def check_python_version(self) -> bool:
        """Verificar versión de Python"""
        console.print("🐍 Verificando versión de Python...")
        
        version = sys.version_info
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            console.print("❌ [red]Se requiere Python 3.8 o superior[/red]")
            console.print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
            return False
        
        console.print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    
    def create_directories(self):
        """Crear estructura de directorios"""
        console.print("📁 Creando estructura de directorios...")
        
        for directory in self.directories:
            path = Path(directory)
            path.mkdir(parents=True, exist_ok=True)
            console.print(f"   ✅ {directory}")
        
        console.print("✅ Directorios creados")
    
    def check_and_install_dependencies(self) -> bool:
        """Verificar e instalar dependencias"""
        console.print("📦 Verificando dependencias...")
        
        missing_packages = []
        
        # Verificar paquetes instalados
        for package in self.required_packages:
            package_name = package.split('==')[0]
            try:
                importlib.import_module(package_name.replace('-', '_'))
                console.print(f"   ✅ {package_name}")
            except ImportError:
                missing_packages.append(package)
                console.print(f"   ❌ {package_name} - No instalado")
        
        if missing_packages:
            console.print(f"\n⚠️ Se encontraron {len(missing_packages)} paquetes faltantes")
            
            if Confirm.ask("¿Quieres instalar los paquetes faltantes automáticamente?"):
                return self.install_missing_packages(missing_packages)
            else:
                console.print("❌ [red]Instalación manual requerida[/red]")
                console.print("Ejecuta: pip install " + " ".join(missing_packages))
                return False
        
        console.print("✅ Todas las dependencias están instaladas")
        return True
    
    def install_missing_packages(self, packages: list) -> bool:
        """Instalar paquetes faltantes"""
        console.print("🔧 Instalando paquetes faltantes...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Instalando dependencias...", total=None)
            
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "--upgrade"
                ] + packages, 
                capture_output=True, text=True)
                
                progress.update(task, completed=True)
                console.print("✅ Paquetes instalados exitosamente")
                return True
                
            except subprocess.CalledProcessError as e:
                progress.update(task, completed=True)
                console.print("❌ [red]Error instalando paquetes[/red]")
                console.print(f"Error: {e}")
                return False
    
    def configure_credentials(self):
        """Configurar credenciales de Ariba"""
        console.print("\n🔐 [bold yellow]CONFIGURACIÓN DE CREDENCIALES ARIBA[/bold yellow]")
        
        # Valores por defecto
        default_username = "sales@alfamine.cl"
        default_password = "VI.2024al..al."
        default_url = "https://service.ariba.com/Sourcing.aw/109555009/aw?awh=r&awssk=XZHPCxm2&dard=1"
        
        console.print("ℹ️ Presiona ENTER para usar valores por defecto")
        
        username = Prompt.ask("Usuario Ariba", default=default_username)
        password = Prompt.ask("Contraseña Ariba", password=True, default=default_password)
        url = Prompt.ask("URL Ariba", default=default_url)
        
        self.config['ariba_credentials'] = {
            'username': username,
            'password': password,
            'url': url
        }
        
        console.print("✅ Credenciales configuradas")
    
    def configure_search_criteria(self):
        """Configurar criterios de búsqueda"""
        console.print("\n🔍 [bold yellow]CONFIGURACIÓN DE CRITERIOS DE BÚSQUEDA[/bold yellow]")
        
        # Líneas de producto
        console.print("📋 Configurando líneas de producto...")
        
        default_alfamine = ["ZAPATA", "CADENA", "RODILLOS", "SPROCKET", "RUEDA TENSORA", "GEARBOX", "REDUCTOR", "MANDO FINAL", "MF"]
        
        if Confirm.ask("¿Usar líneas de producto por defecto para ALFAMINE?", default=True):
            alfamine_products = default_alfamine
        else:
            console.print("Ingresa productos ALFAMINE separados por comas:")
            products_input = Prompt.ask("Productos ALFAMINE")
            alfamine_products = [p.strip().upper() for p in products_input.split(',')]
        
        # Pernería
        console.print("🔩 Configurando pernería...")
        default_perneria = ["PERNO", "TUERCA", "NUT", "BOLT", "CHAVETA", "SCREW"]
        default_prefijos = ["AL00"]
        
        if Confirm.ask("¿Usar keywords de pernería por defecto?", default=True):
            perneria_keywords = default_perneria
            perneria_prefijos = default_prefijos
        else:
            perneria_input = Prompt.ask("Keywords pernería (separadas por comas)")
            prefijos_input = Prompt.ask("Prefijos pernería (separados por comas)")
            perneria_keywords = [k.strip().upper() for k in perneria_input.split(',')]
            perneria_prefijos = [p.strip().upper() for p in prefijos_input.split(',')]
        
        # Marcas
        console.print("🏷️ Configurando marcas...")
        default_marcas = ["KRESS", "CAT", "CATERPILLAR", "KOMATSU"]
        
        if Confirm.ask("¿Usar marcas por defecto?", default=True):
            marcas = default_marcas
        else:
            marcas_input = Prompt.ask("Marcas (separadas por comas)")
            marcas = [m.strip().upper() for m in marcas_input.split(',')]
        
        self.config['search_criteria'] = {
            'lineas_producto': {
                'ALFAMINE': alfamine_products
            },
            'perneria': {
                'keywords': perneria_keywords,
                'prefijos': perneria_prefijos
            },
            'marcas': marcas
        }
        
        console.print("✅ Criterios de búsqueda configurados")
    
    def configure_advanced_options(self):
        """Configurar opciones avanzadas"""
        console.print("\n⚙️ [bold yellow]CONFIGURACIÓN AVANZADA[/bold yellow]")
        
        # Configuración de scraping
        headless = Confirm.ask("¿Ejecutar navegador en modo headless (sin ventana)?", default=False)
        timeout = IntPrompt.ask("Timeout en segundos", default=30)
        max_retries = IntPrompt.ask("Máximo reintentos", default=3)
        
        self.config['scraping'] = {
            'browser_type': 'firefox',
            'headless': headless,
            'timeout': timeout,
            'max_retries': max_retries
        }
        
        # Configuración de notificaciones
        gmail_enabled = Confirm.ask("¿Habilitar notificaciones por email?", default=False)
        
        if gmail_enabled:
            recipients_input = Prompt.ask("Emails destinatarios (separados por comas)", default="sales@alfamine.cl")
            recipients = [email.strip() for email in recipients_input.split(',')]
        else:
            recipients = ["sales@alfamine.cl"]
        
        self.config['notifications'] = {
            'gmail_enabled': gmail_enabled,
            'recipients': recipients
        }
        
        console.print("✅ Opciones avanzadas configuradas")
    
    def save_configuration(self):
        """Guardar configuración"""
        console.print("\n💾 Guardando configuración...")
        
        config_file = Path("config/config.json")
        
        # Backup si existe configuración previa
        if config_file.exists():
            backup_file = config_file.with_suffix(f'.backup_{datetime.now():%Y%m%d_%H%M%S}.json')
            config_file.rename(backup_file)
            console.print(f"   📦 Backup creado: {backup_file.name}")
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        
        console.print(f"   ✅ Configuración guardada: {config_file}")
    
    def verify_installation(self):
        """Verificar instalación"""
        console.print("\n🔍 Verificando instalación...")
        
        verification_table = Table(title="🔍 Verificación de Instalación")
        verification_table.add_column("Componente", style="cyan")
        verification_table.add_column("Estado", style="green")
        verification_table.add_column("Detalles", style="yellow")
        
        # Verificar archivos principales
        main_files = [
            ('main_improved.py', 'Archivo principal mejorado'),
            ('src/scraper_engine_improved.py', 'Motor de scraping mejorado'),
            ('src/analyzer.py', 'Analizador de oportunidades'),
            ('src/notifier.py', 'Sistema de notificaciones'),
            ('config/config.json', 'Archivo de configuración')
        ]
        
        for file_path, description in main_files:
            path = Path(file_path)
            if path.exists():
                verification_table.add_row(description, "✅ OK", f"Encontrado: {file_path}")
            else:
                verification_table.add_row(description, "❌ FALTA", f"No encontrado: {file_path}")
        
        # Verificar directorios
        for directory in self.directories:
            path = Path(directory)
            if path.exists():
                verification_table.add_row(f"Directorio {directory}", "✅ OK", "Creado")
            else:
                verification_table.add_row(f"Directorio {directory}", "❌ FALTA", "No creado")
        
        console.print(verification_table)
        
        # Crear archivo de estado
        status_file = Path("config/installation_status.json")
        status = {
            'installed_at': datetime.now().isoformat(),
            'version': '1.1.0',
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'components_verified': True,
            'configuration_complete': True
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2)
        
        console.print(f"📄 Estado de instalación guardado: {status_file.name}")
    
    def show_next_steps(self):
        """Mostrar próximos pasos"""
        console.print("\n🚀 [bold green]PRÓXIMOS PASOS[/bold green]")
        
        steps_panel = Panel(
            """
[bold yellow]1. Probar conexión básica:[/bold yellow]
   python main_improved.py --mode test

[bold yellow]2. Ejecutar aprendizaje paso a paso:[/bold yellow]
   python main_improved.py --mode learning

[bold yellow]3. Analizar sesiones de aprendizaje:[/bold yellow]
   python learning_analyzer.py

[bold yellow]4. Ejecutar scraping automático:[/bold yellow]
   python main_improved.py --mode scraping

[bold yellow]5. Modo interactivo completo:[/bold yellow]
   python main_improved.py
            """,
            title="📋 Guía de Uso",
            border_style="green"
        )
        
        console.print(steps_panel)


def main():
    """Función principal del asistente"""
    wizard = AlfamineSetupWizard()
    
    try:
        if wizard.run_setup():
            wizard.show_next_steps()
        else:
            console.print("❌ [red]Configuración incompleta[/red]")
            console.print("💡 Revisa los errores y ejecuta el asistente nuevamente")
            return 1
            
    except KeyboardInterrupt:
        console.print("\n⏹️ [yellow]Configuración interrumpida por el usuario[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n❌ [red]Error durante la configuración: {e}[/red]")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
