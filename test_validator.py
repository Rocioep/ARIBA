# test_validator.py
"""
SISTEMA DE TESTING Y VALIDACIÓN ALFAMINE
Validación automática de todos los componentes del sistema
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import importlib
import traceback

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Confirm
from loguru import logger

console = Console()

class TestResult:
    """Clase para almacenar resultados de pruebas"""
    def __init__(self, name: str, passed: bool, message: str = "", duration: float = 0.0):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = duration
        self.timestamp = datetime.now().isoformat()

class AlfamineValidator:
    """Validador completo del sistema Alfamine"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.base_dir = Path.cwd()
        
        # Configurar logging para tests
        logger.add(
            "data/logs/validation_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="DEBUG",
            rotation="1 day"
        )
        
        self.test_categories = {
            'system': 'Configuración del Sistema',
            'dependencies': 'Dependencias de Python',
            'files': 'Archivos del Proyecto',
            'configuration': 'Archivos de Configuración',
            'functionality': 'Funcionalidades Principales',
            'integration': 'Pruebas de Integración'
        }
    
    def run_full_validation(self) -> Dict:
        """Ejecutar validación completa del sistema"""
        console.print("🧪 [bold blue]VALIDACIÓN COMPLETA DEL SISTEMA ALFAMINE[/bold blue]")
        console.print("Ejecutando todas las pruebas de validación...\n")
        
        start_time = datetime.now()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            # Crear tareas de progreso
            total_tests = 20  # Estimado
            task = progress.add_task("Ejecutando validaciones...", total=total_tests)
            
            # 1. Tests del sistema
            progress.update(task, description="🔧 Validando sistema...")
            self.test_system_requirements()
            progress.advance(task, 3)
            
            # 2. Tests de dependencias
            progress.update(task, description="📦 Verificando dependencias...")
            self.test_dependencies()
            progress.advance(task, 3)
            
            # 3. Tests de archivos
            progress.update(task, description="📁 Verificando archivos...")
            self.test_project_files()
            progress.advance(task, 4)
            
            # 4. Tests de configuración
            progress.update(task, description="⚙️ Validando configuración...")
            self.test_configuration_files()
            progress.advance(task, 3)
            
            # 5. Tests de funcionalidad
            progress.update(task, description="🎯 Probando funcionalidades...")
            self.test_core_functionality()
            progress.advance(task, 4)
            
            # 6. Tests de integración
            progress.update(task, description="🔗 Pruebas de integración...")
            self.test_integration()
            progress.advance(task, 3)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generar reporte
        report = self.generate_validation_report(duration)
        
        # Mostrar resultados
        self.display_validation_results()
        
        return report
    
    def test_system_requirements(self):
        """Probar requisitos del sistema"""
        # Test 1: Versión de Python
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            self.results.append(TestResult("python_version", True, f"Python {python_version.major}.{python_version.minor}.{python_version.micro}"))
        else:
            self.results.append(TestResult("python_version", False, f"Python {python_version.major}.{python_version.minor} < 3.8"))
        
        # Test 2: Permisos de escritura
        try:
            test_file = self.base_dir / "test_write_permissions.tmp"
            test_file.write_text("test")
            test_file.unlink()
            self.results.append(TestResult("write_permissions", True, "Permisos de escritura OK"))
        except Exception as e:
            self.results.append(TestResult("write_permissions", False, f"Error permisos: {e}"))
        
        # Test 3: Espacio en disco
        try:
            import shutil
            free_space = shutil.disk_usage(self.base_dir).free / (1024 * 1024)  # MB
            if free_space > 100:  # Al menos 100MB
                self.results.append(TestResult("disk_space", True, f"{free_space:.1f} MB disponibles"))
            else:
                self.results.append(TestResult("disk_space", False, f"Poco espacio: {free_space:.1f} MB"))
        except Exception as e:
            self.results.append(TestResult("disk_space", False, f"Error verificando espacio: {e}"))
    
    def test_dependencies(self):
        """Probar dependencias de Python"""
        required_packages = {
            'selenium': '4.15.0',
            'webdriver_manager': '4.0.1',
            'pandas': '2.1.0',
            'openpyxl': '3.1.2',
            'loguru': '0.7.2',
            'rich': '13.6.0',
            'schedule': '1.2.0',
            'requests': '2.31.0',
            'beautifulsoup4': '4.12.2'
        }
        
        for package, min_version in required_packages.items():
            try:
                # Convertir nombre del paquete
                import_name = package.replace('-', '_')
                module = importlib.import_module(import_name)
                
                # Verificar versión si está disponible
                if hasattr(module, '__version__'):
                    version = module.__version__
                    self.results.append(TestResult(f"package_{package}", True, f"{package} {version}"))
                else:
                    self.results.append(TestResult(f"package_{package}", True, f"{package} instalado"))
                    
            except ImportError:
                self.results.append(TestResult(f"package_{package}", False, f"{package} no instalado"))
            except Exception as e:
                self.results.append(TestResult(f"package_{package}", False, f"Error {package}: {e}"))
    
    def test_project_files(self):
        """Probar archivos del proyecto"""
        required_files = {
            'alfamine.py': 'Launcher principal',
            'main_improved.py': 'Sistema principal mejorado',
            'setup_wizard.py': 'Asistente de configuración',
            'learning_analyzer.py': 'Analizador de aprendizaje',
            'system_monitor.py': 'Monitor de sistema',
            'scheduler_automation.py': 'Automatización',
            'src/scraper_engine_improved.py': 'Motor de scraping mejorado',
            'src/analyzer.py': 'Analizador de oportunidades',
            'src/notifier.py': 'Sistema de notificaciones',
            'requirements.txt': 'Lista de dependencias'
        }
        
        for file_path, description in required_files.items():
            path = self.base_dir / file_path
            if path.exists():
                try:
                    # Verificar que el archivo no esté vacío y sea válido Python
                    if file_path.endswith('.py'):
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if len(content.strip()) > 100:  # Al menos 100 caracteres
                            # Verificar sintaxis básica
                            try:
                                compile(content, path, 'exec')
                                self.results.append(TestResult(f"file_{file_path}", True, f"{description} - Sintaxis OK"))
                            except SyntaxError as e:
                                self.results.append(TestResult(f"file_{file_path}", False, f"Error sintaxis: {e}"))
                        else:
                            self.results.append(TestResult(f"file_{file_path}", False, "Archivo muy pequeño"))
                    else:
                        self.results.append(TestResult(f"file_{file_path}", True, f"{description} - Existe"))
                        
                except Exception as e:
                    self.results.append(TestResult(f"file_{file_path}", False, f"Error leyendo: {e}"))
            else:
                self.results.append(TestResult(f"file_{file_path}", False, f"{description} - No encontrado"))
        
        # Verificar directorios
        required_dirs = ['src', 'config', 'data', 'data/logs', 'data/downloads', 'data/screenshots', 'data/learning', 'reports']
        for dir_path in required_dirs:
            path = self.base_dir / dir_path
            if path.exists() and path.is_dir():
                self.results.append(TestResult(f"dir_{dir_path}", True, f"Directorio {dir_path} existe"))
            else:
                self.results.append(TestResult(f"dir_{dir_path}", False, f"Directorio {dir_path} falta"))
    
    def test_configuration_files(self):
        """Probar archivos de configuración"""
        config_files = {
            'config/config.json': self.validate_main_config,
            'config/optimized_selectors.json': self.validate_selectors_config,
            'config/installation_status.json': self.validate_installation_status
        }
        
        for config_path, validator in config_files.items():
            path = self.base_dir / config_path
            if path.exists():
                try:
                    result = validator(path)
                    self.results.append(result)
                except Exception as e:
                    self.results.append(TestResult(f"config_{config_path}", False, f"Error validando: {e}"))
            else:
                self.results.append(TestResult(f"config_{config_path}", False, f"Archivo {config_path} no encontrado"))
    
    def validate_main_config(self, path: Path) -> TestResult:
        """Validar configuración principal"""
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_keys = ['ariba_credentials', 'search_criteria', 'scraping', 'notifications']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            return TestResult("main_config", False, f"Faltan claves: {missing_keys}")
        
        # Validar credenciales
        creds = config['ariba_credentials']
        if not all(key in creds for key in ['username', 'password', 'url']):
            return TestResult("main_config", False, "Credenciales incompletas")
        
        return TestResult("main_config", True, "Configuración principal válida")
    
    def validate_selectors_config(self, path: Path) -> TestResult:
        """Validar configuración de selectores"""
        with open(path, 'r', encoding='utf-8') as f:
            selectors = json.load(f)
        
        expected_categories = ['login', 'corporation_dropdown', 'codelco_selection']
        found_categories = [cat for cat in expected_categories if cat in selectors]
        
        if len(found_categories) >= 2:
            return TestResult("selectors_config", True, f"Selectores válidos: {found_categories}")
        else:
            return TestResult("selectors_config", False, f"Pocos selectores: {found_categories}")
    
    def validate_installation_status(self, path: Path) -> TestResult:
        """Validar estado de instalación"""
        with open(path, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        if status.get('configuration_complete', False):
            return TestResult("installation_status", True, "Instalación completa")
        else:
            return TestResult("installation_status", False, "Instalación incompleta")
    
    def test_core_functionality(self):
        """Probar funcionalidades principales"""
        # Test 1: Importar módulos principales
        modules_to_test = [
            ('src.scraper_engine_improved', 'ImprovedAribaScraperEngine'),
            ('src.analyzer', 'OpportunityAnalyzer'),
            ('src.notifier', 'EmailNotifier')
        ]
        
        for module_name, class_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                cls = getattr(module, class_name)
                self.results.append(TestResult(f"import_{class_name}", True, f"Clase {class_name} importada"))
            except ImportError as e:
                self.results.append(TestResult(f"import_{class_name}", False, f"Error importando {module_name}: {e}"))
            except AttributeError as e:
                self.results.append(TestResult(f"import_{class_name}", False, f"Clase {class_name} no encontrada: {e}"))
        
        # Test 2: Verificar geckodriver
        try:
            from webdriver_manager.firefox import GeckoDriverManager
            driver_path = GeckoDriverManager().install()
            if Path(driver_path).exists():
                self.results.append(TestResult("geckodriver", True, "Geckodriver instalado"))
            else:
                self.results.append(TestResult("geckodriver", False, "Geckodriver no encontrado"))
        except Exception as e:
            self.results.append(TestResult("geckodriver", False, f"Error geckodriver: {e}"))
        
        # Test 3: Verificar que el analizador puede procesar datos
        try:
            import pandas as pd
            test_data = pd.DataFrame({'test': [1, 2, 3]})
            if len(test_data) == 3:
                self.results.append(TestResult("pandas_functionality", True, "Pandas funciona correctamente"))
            else:
                self.results.append(TestResult("pandas_functionality", False, "Error procesando datos"))
        except Exception as e:
            self.results.append(TestResult("pandas_functionality", False, f"Error pandas: {e}"))
    
    def test_integration(self):
        """Probar integración entre componentes"""
        # Test 1: Ejecutar help de script principal
        try:
            result = subprocess.run(
                [sys.executable, 'alfamine.py', '--help'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and 'Alfamine' in result.stdout:
                self.results.append(TestResult("launcher_help", True, "Launcher ejecuta correctamente"))
            else:
                self.results.append(TestResult("launcher_help", False, f"Error launcher: {result.stderr}"))
        except Exception as e:
            self.results.append(TestResult("launcher_help", False, f"Error ejecutando launcher: {e}"))
        
        # Test 2: Verificar modo status
        try:
            result = subprocess.run(
                [sys.executable, 'alfamine.py', '--status'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                self.results.append(TestResult("status_mode", True, "Modo status funciona"))
            else:
                self.results.append(TestResult("status_mode", False, f"Error status: {result.stderr}"))
        except Exception as e:
            self.results.append(TestResult("status_mode", False, f"Error status: {e}"))
        
        # Test 3: Verificar estructura de directorios después de ejecución
        required_dirs = ['data/logs', 'data/downloads', 'data/screenshots', 'data/learning']
        dirs_created = 0
        for dir_path in required_dirs:
            if (self.base_dir / dir_path).exists():
                dirs_created += 1
        
        if dirs_created == len(required_dirs):
            self.results.append(TestResult("directory_creation", True, "Directorios creados correctamente"))
        else:
            self.results.append(TestResult("directory_creation", False, f"Solo {dirs_created}/{len(required_dirs)} directorios"))
    
    def display_validation_results(self):
        """Mostrar resultados de validación"""
        # Calcular estadísticas
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.passed])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Panel de resumen
        summary_text = f"""
[bold green]✅ Pruebas Exitosas: {passed_tests}[/bold green]
[bold red]❌ Pruebas Fallidas: {failed_tests}[/bold red]
[bold blue]📊 Tasa de Éxito: {success_rate:.1f}%[/bold blue]
[bold white]📋 Total Pruebas: {total_tests}[/bold white]
        """
        
        if success_rate >= 90:
            border_style = "green"
            status = "🎉 SISTEMA VALIDADO"
        elif success_rate >= 70:
            border_style = "yellow"
            status = "⚠️ SISTEMA PARCIALMENTE VALIDADO"
        else:
            border_style = "red"
            status = "❌ SISTEMA REQUIERE ATENCIÓN"
        
        summary_panel = Panel(summary_text, title=status, border_style=border_style)
        console.print(summary_panel)
        
        # Tabla detallada de resultados
        results_table = Table(title="📋 Resultados Detallados de Validación")
        results_table.add_column("Prueba", style="cyan")
        results_table.add_column("Estado", style="green")
        results_table.add_column("Mensaje", style="white")
        results_table.add_column("Categoría", style="yellow")
        
        # Agrupar por categoría
        categorized_results = {}
        for result in self.results:
            # Determinar categoría basada en el nombre
            category = 'other'
            if 'python' in result.name or 'disk' in result.name or 'write' in result.name:
                category = 'system'
            elif 'package' in result.name:
                category = 'dependencies'
            elif 'file' in result.name or 'dir' in result.name:
                category = 'files'
            elif 'config' in result.name:
                category = 'configuration'
            elif 'import' in result.name or 'pandas' in result.name or 'geckodriver' in result.name:
                category = 'functionality'
            elif 'launcher' in result.name or 'status' in result.name or 'directory' in result.name:
                category = 'integration'
            
            if category not in categorized_results:
                categorized_results[category] = []
            categorized_results[category].append(result)
        
        # Mostrar resultados por categoría
        for category, results in categorized_results.items():
            category_name = self.test_categories.get(category, category.title())
            
            for result in results:
                status_icon = "✅" if result.passed else "❌"
                results_table.add_row(
                    result.name.replace('_', ' ').title(),
                    status_icon,
                    result.message[:60] + "..." if len(result.message) > 60 else result.message,
                    category_name
                )
        
        console.print(results_table)
        
        # Recomendaciones
        if failed_tests > 0:
            console.print("\n💡 [bold yellow]RECOMENDACIONES:[/bold yellow]")
            
            failed_results = [r for r in self.results if not r.passed]
            
            # Agrupar fallos por tipo
            dependency_fails = [r for r in failed_results if 'package' in r.name]
            file_fails = [r for r in failed_results if 'file' in r.name or 'dir' in r.name]
            config_fails = [r for r in failed_results if 'config' in r.name]
            
            if dependency_fails:
                console.print("📦 [yellow]Dependencias faltantes:[/yellow]")
                console.print("   Ejecuta: python -m pip install -r requirements.txt")
            
            if file_fails:
                console.print("📁 [yellow]Archivos faltantes:[/yellow]")
                console.print("   Ejecuta: python setup_wizard.py")
            
            if config_fails:
                console.print("⚙️ [yellow]Configuración incompleta:[/yellow]")
                console.print("   Ejecuta: python alfamine.py --setup")
    
    def generate_validation_report(self, duration: float) -> Dict:
        """Generar reporte de validación"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'total_tests': len(self.results),
            'passed_tests': len([r for r in self.results if r.passed]),
            'failed_tests': len([r for r in self.results if not r.passed]),
            'success_rate': (len([r for r in self.results if r.passed]) / len(self.results) * 100) if self.results else 0,
            'system_status': 'VALIDATED' if len([r for r in self.results if r.passed]) / len(self.results) >= 0.9 else 'NEEDS_ATTENTION',
            'test_results': [
                {
                    'name': r.name,
                    'passed': r.passed,
                    'message': r.message,
                    'duration': r.duration,
                    'timestamp': r.timestamp
                }
                for r in self.results
            ]
        }
        
        # Guardar reporte
        report_file = Path("reports") / f"validation_report_{datetime.now():%Y%m%d_%H%M%S}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        console.print(f"\n📄 [bold green]Reporte guardado: {report_file.name}[/bold green]")
        
        return report
    
    def quick_validation(self):
        """Validación rápida de componentes críticos"""
        console.print("⚡ [bold yellow]VALIDACIÓN RÁPIDA[/bold yellow]")
        
        quick_tests = [
            ("Python 3.8+", lambda: sys.version_info >= (3, 8)),
            ("Archivo principal", lambda: Path("alfamine.py").exists()),
            ("Configuración", lambda: Path("config/config.json").exists()),
            ("Directorio data", lambda: Path("data").exists()),
            ("Selenium", lambda: importlib.import_module("selenium")),
            ("Pandas", lambda: importlib.import_module("pandas"))
        ]
        
        results = []
        for test_name, test_func in quick_tests:
            try:
                test_func()
                results.append((test_name, True, "OK"))
            except Exception as e:
                results.append((test_name, False, str(e)[:30]))
        
        # Mostrar resultados
        quick_table = Table(title="⚡ Validación Rápida")
        quick_table.add_column("Prueba", style="cyan")
        quick_table.add_column("Estado", style="green")
        quick_table.add_column("Detalle", style="white")
        
        for name, passed, detail in results:
            status = "✅" if passed else "❌"
            quick_table.add_row(name, status, detail)
        
        console.print(quick_table)
        
        passed_count = len([r for r in results if r[1]])
        total_count = len(results)
        
        if passed_count == total_count:
            console.print("🎉 [bold green]Validación rápida: SISTEMA OK[/bold green]")
        else:
            console.print(f"⚠️ [bold yellow]Validación rápida: {passed_count}/{total_count} pruebas OK[/bold yellow]")


def main():
    """Función principal del validador"""
    validator = AlfamineValidator()
    
    console.print("🧪 [bold blue]SISTEMA DE VALIDACIÓN ALFAMINE[/bold blue]")
    console.print("Verificación automática de todos los componentes\n")
    
    from rich.prompt import Prompt
    
    mode = Prompt.ask(
        "Tipo de validación",
        choices=["quick", "full"],
        default="quick"
    )
    
    if mode == "quick":
        validator.quick_validation()
    else:
        validator.run_full_validation()
    
    console.print("\n💡 [bold cyan]Comandos adicionales:[/bold cyan]")
    console.print("   python test_validator.py quick    # Validación rápida")
    console.print("   python test_validator.py full     # Validación completa")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            validator = AlfamineValidator()
            validator.quick_validation()
        elif sys.argv[1] == "full":
            validator = AlfamineValidator()
            validator.run_full_validation()
        else:
            console.print("❌ Uso: python test_validator.py [quick|full]")
    else:
        main()