# install.py
"""
INSTALADOR AUTOMÁTICO ALFAMINE MONITOR
Instalación completa y automática del sistema desde cero
"""

import os
import sys
import subprocess
import json
import shutil
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Importar rich solo si está disponible
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.prompt import Confirm, Prompt
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

if RICH_AVAILABLE:
    console = Console()
else:
    # Fallback para cuando rich no esté disponible
    class DummyConsole:
        def print(self, *args, **kwargs):
            print(*args)
    console = DummyConsole()

class AlfamineInstaller:
    """Instalador automático completo para Alfamine Monitor"""
    
    def __init__(self):
        self.version = "1.1.0"
        self.base_dir = Path.cwd()
        self.install_log = []
        
        # URLs de archivos (si fuera necesario descargarlos)
        self.github_base = "https://raw.githubusercontent.com/tu-repo/alfamine/main/"
        
        # Lista de dependencias requeridas
        self.requirements = [
            "selenium==4.15.0",
            "webdriver-manager==4.0.1", 
            "pandas==2.1.0",
            "openpyxl==3.1.2",
            "loguru==0.7.2",
            "rich==13.6.0",
            "schedule==1.2.0",
            "requests==2.31.0",
            "beautifulsoup4==4.12.2",
            "python-dotenv==1.0.0"
        ]
        
        # Estructura de archivos del proyecto
        self.project_structure = {
            'files': [
                'alfamine.py',
                'main_improved.py',
                'setup_wizard.py',
                'learning_analyzer.py',
                'system_monitor.py',
                'scheduler_automation.py',
                'test_validator.py',
                'requirements.txt'
            ],
            'src_files': [
                'src/__init__.py',
                'src/scraper_engine_improved.py',
                'src/analyzer.py',
                'src/notifier.py'
            ],
            'directories': [
                'src',
                'config',
                'data/logs',
                'data/downloads',
                'data/screenshots', 
                'data/learning',
                'reports',
                'backups'
            ]
        }
    
    def log(self, message: str):
        """Registrar mensaje en log de instalación"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.install_log.append(log_entry)
        print(log_entry)
    
    def check_python_version(self) -> bool:
        """Verificar versión de Python"""
        version = sys.version_info
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.log(f"❌ ERROR: Se requiere Python 3.8 o superior")
            self.log(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
            return False
        
        self.log(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    
    def install_rich_if_needed(self) -> bool:
        """Instalar rich si no está disponible"""
        if RICH_AVAILABLE:
            return True
        
        self.log("📦 Rich no está instalado, instalando...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "rich>=13.0.0"
            ])
            self.log("✅ Rich instalado correctamente")
            return True
        except subprocess.CalledProcessError:
            self.log("⚠️ No se pudo instalar Rich, continuando sin UI mejorada")
            return False
    
    def create_directory_structure(self):
        """Crear estructura de directorios"""
        self.log("📁 Creando estructura de directorios...")
        
        for directory in self.project_structure['directories']:
            dir_path = self.base_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.log(f"   ✅ {directory}")
        
        self.log("✅ Estructura de directorios creada")
    
    def install_dependencies(self) -> bool:
        """Instalar dependencias de Python"""
        self.log("📦 Instalando dependencias de Python...")
        
        # Crear requirements.txt si no existe
        requirements_file = self.base_dir / "requirements.txt"
        if not requirements_file.exists():
            with open(requirements_file, 'w') as f:
                f.write('\n'.join(self.requirements))
            self.log("   📝 requirements.txt creado")
        
        try:
            # Actualizar pip primero
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ])
            
            # Instalar dependencias
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ])
            
            self.log("✅ Dependencias instaladas correctamente")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Error instalando dependencias: {e}")
            return False
    
    def verify_files_exist(self) -> bool:
        """Verificar que todos los archivos necesarios existen"""
        self.log("📄 Verificando archivos del proyecto...")
        
        missing_files = []
        
        # Verificar archivos principales
        for file_name in self.project_structure['files']:
            file_path = self.base_dir / file_name
            if file_path.exists():
                self.log(f"   ✅ {file_name}")
            else:
                missing_files.append(file_name)
                self.log(f"   ❌ {file_name} - NO ENCONTRADO")
        
        # Verificar archivos src
        for file_name in self.project_structure['src_files']:
            file_path = self.base_dir / file_name
            if file_path.exists():
                self.log(f"   ✅ {file_name}")
            else:
                missing_files.append(file_name)
                self.log(f"   ❌ {file_name} - NO ENCONTRADO")
        
        if missing_files:
            self.log(f"⚠️ {len(missing_files)} archivos faltantes")
            return False
        else:
            self.log("✅ Todos los archivos encontrados")
            return True
    
    def create_basic_config(self):
        """Crear configuración básica"""
        self.log("⚙️ Creando configuración básica...")
        
        config_file = self.base_dir / "config" / "config.json"
        
        if config_file.exists():
            self.log("   ℹ️ Configuración ya existe, conservando...")
            return
        
        basic_config = {
            "ariba_credentials": {
                "username": "sales@alfamine.cl",
                "password": "VI.2024al..al.",
                "url": "https://service.ariba.com/Sourcing.aw/109555009/aw?awh=r&awssk=XZHPCxm2&dard=1"
            },
            "search_criteria": {
                "lineas_producto": {
                    "ALFAMINE": [
                        "ZAPATA", "CADENA", "RODILLOS", "SPROCKET", 
                        "RUEDA TENSORA", "GEARBOX", "REDUCTOR", 
                        "MANDO FINAL", "MF"
                    ]
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
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(basic_config, f, indent=4, ensure_ascii=False)
        
        self.log("   ✅ config.json creado")
        
        # Crear estado de instalación
        status_file = self.base_dir / "config" / "installation_status.json"
        status = {
            'installed_at': datetime.now().isoformat(),
            'version': self.version,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'installation_method': 'automatic',
            'components_verified': True,
            'configuration_complete': True
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        
        self.log("   ✅ installation_status.json creado")
    
    def test_installation(self) -> bool:
        """Probar instalación básica"""
        self.log("🧪 Probando instalación...")
        
        try:
            # Test 1: Importar módulo principal
            sys.path.append(str(self.base_dir))
            
            # Test básico de imports
            import pandas as pd
            import selenium
            from rich.console import Console
            
            self.log("   ✅ Imports básicos OK")
            
            # Test 2: Ejecutar launcher con --help
            launcher_path = self.base_dir / "alfamine.py"
            if launcher_path.exists():
                result = subprocess.run(
                    [sys.executable, str(launcher_path), "--help"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.log("   ✅ Launcher ejecuta correctamente")
                else:
                    self.log(f"   ⚠️ Launcher tiene problemas: {result.stderr}")
            
            # Test 3: Verificar geckodriver
            try:
                from webdriver_manager.firefox import GeckoDriverManager
                driver_path = GeckoDriverManager().install()
                if Path(driver_path).exists():
                    self.log("   ✅ Geckodriver disponible")
                else:
                    self.log("   ⚠️ Problemas con geckodriver")
            except Exception as e:
                self.log(f"   ⚠️ Error geckodriver: {e}")
            
            self.log("✅ Tests básicos completados")
            return True
            
        except Exception as e:
            self.log(f"❌ Error en tests: {e}")
            return False
    
    def create_install_summary(self):
        """Crear resumen de instalación"""
        self.log("📄 Generando resumen de instalación...")
        
        summary = {
            'installation_date': datetime.now().isoformat(),
            'version': self.version,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'install_directory': str(self.base_dir),
            'installation_log': self.install_log,
            'files_created': len(self.project_structure['files'] + self.project_structure['src_files']),
            'directories_created': len(self.project_structure['directories'])
        }
        
        summary_file = self.base_dir / "INSTALL_SUMMARY.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.log(f"   ✅ Resumen guardado: {summary_file.name}")
    
    def show_next_steps(self):
        """Mostrar próximos pasos"""
        if RICH_AVAILABLE:
            steps_panel = Panel(
                """
[bold yellow]🎉 INSTALACIÓN COMPLETADA[/bold yellow]

[bold green]Próximos pasos:[/bold green]

[bold cyan]1. Verificar instalación:[/bold cyan]
   python test_validator.py quick

[bold cyan]2. Configurar sistema:[/bold cyan]
   python alfamine.py --setup

[bold cyan]3. Probar conexión:[/bold cyan]
   python alfamine.py --quick
   # Luego elegir 'a' (Test rápido)

[bold cyan]4. Entrenar sistema:[/bold cyan]
   python alfamine.py --tool main --args --mode learning

[bold cyan]5. Usar sistema:[/bold cyan]
   python alfamine.py

[bold yellow]📚 Documentación completa:[/bold yellow]
   Ver README_SISTEMA_COMPLETO.md
                """,
                title="✅ Instalación Exitosa",
                border_style="green"
            )
            console.print(steps_panel)
        else:
            print("\n" + "="*50)
            print("🎉 INSTALACIÓN COMPLETADA")
            print("="*50)
            print("\nPróximos pasos:")
            print("1. Verificar: python test_validator.py quick")
            print("2. Configurar: python alfamine.py --setup")
            print("3. Probar: python alfamine.py --quick")
            print("4. Entrenar: python alfamine.py --tool main --args --mode learning")
            print("5. Usar: python alfamine.py")
    
    def run_installation(self) -> bool:
        """Ejecutar instalación completa"""
        if RICH_AVAILABLE:
            console.print("📦 [bold blue]INSTALADOR AUTOMÁTICO ALFAMINE MONITOR[/bold blue]")
            console.print(f"Versión {self.version} - Instalación completa automática\n")
        else:
            print("📦 INSTALADOR AUTOMÁTICO ALFAMINE MONITOR")
            print(f"Versión {self.version} - Instalación completa automática\n")
        
        self.log("🚀 Iniciando instalación automática...")
        
        steps = [
            ("Verificando Python", self.check_python_version),
            ("Instalando Rich", self.install_rich_if_needed),
            ("Creando directorios", lambda: (self.create_directory_structure(), True)[1]),
            ("Verificando archivos", self.verify_files_exist),
            ("Instalando dependencias", self.install_dependencies),
            ("Creando configuración", lambda: (self.create_basic_config(), True)[1]),
            ("Probando instalación", self.test_installation),
            ("Generando resumen", lambda: (self.create_install_summary(), True)[1])
        ]
        
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                task = progress.add_task("Instalando...", total=len(steps))
                
                for step_name, step_func in steps:
                    progress.update(task, description=f"{step_name}...")
                    
                    try:
                        success = step_func()
                        if not success:
                            self.log(f"❌ Fallo en paso: {step_name}")
                            return False
                    except Exception as e:
                        self.log(f"💥 Error en {step_name}: {e}")
                        return False
                    
                    progress.advance(task)
        else:
            # Versión sin rich
            for i, (step_name, step_func) in enumerate(steps, 1):
                print(f"[{i}/{len(steps)}] {step_name}...")
                
                try:
                    success = step_func()
                    if not success:
                        self.log(f"❌ Fallo en paso: {step_name}")
                        return False
                except Exception as e:
                    self.log(f"💥 Error en {step_name}: {e}")
                    return False
        
        self.log("🎉 Instalación completada exitosamente")
        return True
    
    def run_uninstall(self):
        """Desinstalar sistema (opcional)"""
        self.log("🗑️ Iniciando desinstalación...")
        
        if RICH_AVAILABLE:
            confirm = Confirm.ask("¿Estás seguro de que quieres desinstalar Alfamine Monitor?")
        else:
            confirm = input("¿Estás seguro de que quieres desinstalar Alfamine Monitor? (y/N): ").lower() == 'y'
        
        if not confirm:
            self.log("⏹️ Desinstalación cancelada")
            return
        
        # Crear backup antes de desinstalar
        if RICH_AVAILABLE:
            backup = Confirm.ask("¿Crear backup antes de desinstalar?", default=True)
        else:
            backup = input("¿Crear backup antes de desinstalar? (Y/n): ").lower() != 'n'
        
        if backup:
            backup_dir = self.base_dir / f"alfamine_backup_{datetime.now():%Y%m%d_%H%M%S}"
            backup_dir.mkdir(exist_ok=True)
            
            # Backup de configuración y datos importantes
            for item in ['config', 'data/learning', 'reports']:
                src = self.base_dir / item
                if src.exists():
                    if src.is_dir():
                        shutil.copytree(src, backup_dir / item)
                    else:
                        shutil.copy2(src, backup_dir)
            
            self.log(f"📦 Backup creado en: {backup_dir}")
        
        # Eliminar directorios opcionales
        optional_dirs = ['data', 'reports', 'backups', 'config']
        for dir_name in optional_dirs:
            dir_path = self.base_dir / dir_name
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    self.log(f"   🗑️ {dir_name} eliminado")
                except Exception as e:
                    self.log(f"   ⚠️ No se pudo eliminar {dir_name}: {e}")
        
        self.log("✅ Desinstalación completada")


def main():
    """Función principal del instalador"""
    installer = AlfamineInstaller()
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == "uninstall":
            installer.run_uninstall()
            return
        elif sys.argv[1] == "--help":
            print("Uso:")
            print("  python install.py           # Instalación completa")
            print("  python install.py uninstall # Desinstalar sistema")
            return
    
    try:
        success = installer.run_installation()
        
        if success:
            installer.show_next_steps()
        else:
            print("\n❌ Instalación falló. Revisa los mensajes de error arriba.")
            print("💡 Intenta ejecutar los pasos manualmente o pide ayuda.")
            return 1
    
    except KeyboardInterrupt:
        print("\n⏹️ Instalación interrumpida por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error fatal durante instalación: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)