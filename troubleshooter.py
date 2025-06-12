# troubleshooter.py
"""
TROUBLESHOOTER ALFAMINE MONITOR
Diagnóstico y resolución automática de problemas comunes
"""

import sys
import json
import subprocess
import importlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from rich.prompt import Confirm, Prompt
from rich.tree import Tree
from loguru import logger

console = Console()

class Problem:
    """Clase para representar un problema y su solución"""
    def __init__(self, name: str, description: str, severity: str, 
                 check_func, fix_func=None, fix_description: str = ""):
        self.name = name
        self.description = description
        self.severity = severity  # 'critical', 'warning', 'info'
        self.check_func = check_func
        self.fix_func = fix_func
        self.fix_description = fix_description
        self.status = 'unchecked'  # 'unchecked', 'ok', 'problem', 'fixed'
        self.details = ""

class AlfamineTroubleshooter:
    """Diagnóstico y resolución automática de problemas"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.problems: List[Problem] = []
        self.results: Dict[str, str] = {}
        
        # Configurar logging para troubleshooting
        logger.add(
            "data/logs/troubleshoot_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="DEBUG"
        )
        
        self.setup_problem_definitions()
    
    def setup_problem_definitions(self):
        """Definir todos los problemas conocidos y sus soluciones"""
        
        # PROBLEMAS CRÍTICOS
        self.problems.extend([
            Problem(
                "python_version",
                "Versión de Python incompatible", 
                "critical",
                self.check_python_version,
                self.fix_python_version,
                "Instalar Python 3.8 o superior"
            ),
            Problem(
                "missing_dependencies",
                "Dependencias de Python faltantes",
                "critical", 
                self.check_dependencies,
                self.fix_dependencies,
                "Instalar dependencias faltantes"
            ),
            Problem(
                "corrupted_config",
                "Archivo de configuración corrupto",
                "critical",
                self.check_config_integrity,
                self.fix_corrupted_config,
                "Regenerar archivo de configuración"
            ),
            Problem(
                "missing_main_files",
                "Archivos principales del sistema faltantes",
                "critical",
                self.check_main_files,
                self.fix_missing_files,
                "Restaurar archivos desde backup o reinstalar"
            )
        ])
        
        # PROBLEMAS DE ADVERTENCIA
        self.problems.extend([
            Problem(
                "outdated_selectors",
                "Selectores de scraping desactualizados",
                "warning",
                self.check_selector_freshness,
                self.fix_outdated_selectors,
                "Actualizar selectores con sesión de aprendizaje"
            ),
            Problem(
                "disk_space_low",
                "Espacio en disco insuficiente",
                "warning",
                self.check_disk_space,
                self.fix_disk_space,
                "Limpiar archivos antiguos"
            ),
            Problem(
                "large_log_files",
                "Archivos de log muy grandes",
                "warning",
                self.check_log_sizes,
                self.fix_large_logs,
                "Rotar y comprimir logs antiguos"
            ),
            Problem(
                "firefox_outdated",
                "Firefox o geckodriver desactualizado",
                "warning",
                self.check_firefox_version,
                self.fix_firefox_issues,
                "Actualizar Firefox y geckodriver"
            )
        ])
        
        # PROBLEMAS INFORMATIVOS
        self.problems.extend([
            Problem(
                "no_learning_data",
                "Sin datos de aprendizaje",
                "info",
                self.check_learning_data,
                self.fix_no_learning_data,
                "Ejecutar sesión de aprendizaje"
            ),
            Problem(
                "no_recent_runs",
                "Sin ejecuciones recientes",
                "info", 
                self.check_recent_activity,
                None,
                "Sistema no usado recientemente"
            ),
            Problem(
                "scheduler_not_running",
                "Scheduler de automatización inactivo",
                "info",
                self.check_scheduler_status,
                self.fix_scheduler,
                "Iniciar scheduler de automatización"
            )
        ])
    
    def run_diagnosis(self) -> Dict:
        """Ejecutar diagnóstico completo"""
        console.print("🔍 [bold blue]DIAGNÓSTICO COMPLETO DEL SISTEMA[/bold blue]")
        console.print("Analizando posibles problemas...\n")
        
        results = {
            'critical': [],
            'warning': [],
            'info': [],
            'total_problems': 0,
            'fixable_problems': 0
        }
        
        with Progress() as progress:
            task = progress.add_task("Ejecutando diagnóstico...", total=len(self.problems))
            
            for problem in self.problems:
                progress.update(task, description=f"Verificando: {problem.name}")
                
                try:
                    # Ejecutar verificación
                    is_problem, details = problem.check_func()
                    
                    if is_problem:
                        problem.status = 'problem'
                        problem.details = details
                        results[problem.severity].append(problem)
                        results['total_problems'] += 1
                        
                        if problem.fix_func:
                            results['fixable_problems'] += 1
                    else:
                        problem.status = 'ok'
                        problem.details = details or "OK"
                
                except Exception as e:
                    problem.status = 'problem'
                    problem.details = f"Error verificando: {e}"
                    results[problem.severity].append(problem)
                    results['total_problems'] += 1
                
                progress.advance(task)
        
        return results
    
    def display_diagnosis_results(self, results: Dict):
        """Mostrar resultados del diagnóstico"""
        
        # Panel de resumen
        summary_text = f"""
[bold red]🚨 Problemas Críticos: {len(results['critical'])}[/bold red]
[bold yellow]⚠️ Advertencias: {len(results['warning'])}[/bold yellow] 
[bold blue]ℹ️ Informativos: {len(results['info'])}[/bold blue]
[bold green]🔧 Problemas Reparables: {results['fixable_problems']}/{results['total_problems']}[/bold green]
        """
        
        if results['total_problems'] == 0:
            summary_panel = Panel(summary_text + "\n[bold green]✅ Sistema funcionando correctamente[/bold green]", 
                                title="📊 Resumen del Diagnóstico", border_style="green")
        elif len(results['critical']) > 0:
            summary_panel = Panel(summary_text + "\n[bold red]❌ Atención inmediata requerida[/bold red]",
                                title="📊 Resumen del Diagnóstico", border_style="red")
        else:
            summary_panel = Panel(summary_text + "\n[bold yellow]⚠️ Algunos problemas detectados[/bold yellow]",
                                title="📊 Resumen del Diagnóstico", border_style="yellow")
        
        console.print(summary_panel)
        
        # Detalles por categoría
        for severity, color, emoji in [('critical', 'red', '🚨'), ('warning', 'yellow', '⚠️'), ('info', 'blue', 'ℹ️')]:
            if results[severity]:
                console.print(f"\n{emoji} [bold {color}]PROBLEMAS {severity.upper()}:[/bold {color}]")
                
                problems_table = Table()
                problems_table.add_column("Problema", style="cyan")
                problems_table.add_column("Descripción", style="white")
                problems_table.add_column("Estado", style=color)
                problems_table.add_column("Acción", style="green")
                
                for problem in results[severity]:
                    action = problem.fix_description if problem.fix_func else "No reparable automáticamente"
                    problems_table.add_row(
                        problem.name,
                        problem.description,
                        problem.details[:50] + "..." if len(problem.details) > 50 else problem.details,
                        action
                    )
                
                console.print(problems_table)
    
    def auto_fix_problems(self, results: Dict) -> int:
        """Reparar automáticamente problemas que tengan solución"""
        fixable_problems = []
        
        for severity in ['critical', 'warning', 'info']:
            for problem in results[severity]:
                if problem.fix_func:
                    fixable_problems.append(problem)
        
        if not fixable_problems:
            console.print("ℹ️ [blue]No hay problemas reparables automáticamente[/blue]")
            return 0
        
        console.print(f"\n🔧 [bold green]Reparando {len(fixable_problems)} problemas automáticamente...[/bold green]")
        
        fixed_count = 0
        
        with Progress() as progress:
            task = progress.add_task("Reparando problemas...", total=len(fixable_problems))
            
            for problem in fixable_problems:
                progress.update(task, description=f"Reparando: {problem.name}")
                
                try:
                    success = problem.fix_func()
                    if success:
                        problem.status = 'fixed'
                        fixed_count += 1
                        logger.info(f"✅ Problema reparado: {problem.name}")
                    else:
                        logger.error(f"❌ No se pudo reparar: {problem.name}")
                except Exception as e:
                    logger.error(f"💥 Error reparando {problem.name}: {e}")
                
                progress.advance(task)
        
        console.print(f"✅ [bold green]{fixed_count}/{len(fixable_problems)} problemas reparados[/bold green]")
        return fixed_count
    
    # VERIFICACIONES DE PROBLEMAS
    
    def check_python_version(self) -> Tuple[bool, str]:
        """Verificar versión de Python"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            return True, f"Python {version.major}.{version.minor} < 3.8 requerido"
        return False, f"Python {version.major}.{version.minor}.{version.micro}"
    
    def check_dependencies(self) -> Tuple[bool, str]:
        """Verificar dependencias faltantes"""
        required = ['selenium', 'pandas', 'rich', 'loguru', 'webdriver_manager']
        missing = []
        
        for package in required:
            try:
                importlib.import_module(package.replace('-', '_'))
            except ImportError:
                missing.append(package)
        
        if missing:
            return True, f"Faltan: {', '.join(missing)}"
        return False, f"Todas las dependencias instaladas"
    
    def check_config_integrity(self) -> Tuple[bool, str]:
        """Verificar integridad de configuración"""
        config_path = self.base_dir / "config" / "config.json"
        
        if not config_path.exists():
            return True, "Archivo config.json no existe"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            required_sections = ['ariba_credentials', 'search_criteria']
            missing_sections = [s for s in required_sections if s not in config]
            
            if missing_sections:
                return True, f"Secciones faltantes: {', '.join(missing_sections)}"
            
            return False, "Configuración válida"
            
        except json.JSONDecodeError:
            return True, "JSON corrupto"
        except Exception as e:
            return True, f"Error leyendo config: {e}"
    
    def check_main_files(self) -> Tuple[bool, str]:
        """Verificar archivos principales"""
        required_files = [
            "alfamine.py",
            "main_improved.py", 
            "src/scraper_engine_improved.py",
            "src/analyzer.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.base_dir / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            return True, f"Archivos faltantes: {', '.join(missing_files)}"
        return False, "Todos los archivos principales presentes"
    
    def check_selector_freshness(self) -> Tuple[bool, str]:
        """Verificar frescura de selectores"""
        learning_dir = self.base_dir / "data" / "learning"
        
        if not learning_dir.exists():
            return True, "Sin datos de aprendizaje"
        
        json_files = list(learning_dir.glob("*.json"))
        if not json_files:
            return True, "Sin sesiones de aprendizaje"
        
        # Verificar fecha de la sesión más reciente
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        days_old = (datetime.now().timestamp() - latest_file.stat().st_mtime) / 86400
        
        if days_old > 30:
            return True, f"Última sesión hace {days_old:.0f} días"
        return False, f"Última sesión hace {days_old:.0f} días"
    
    def check_disk_space(self) -> Tuple[bool, str]:
        """Verificar espacio en disco"""
        try:
            import shutil
            free_space = shutil.disk_usage(self.base_dir).free / (1024 * 1024 * 1024)  # GB
            
            if free_space < 1:  # Menos de 1GB
                return True, f"Solo {free_space:.1f}GB libres"
            return False, f"{free_space:.1f}GB libres"
        except Exception as e:
            return True, f"Error verificando espacio: {e}"
    
    def check_log_sizes(self) -> Tuple[bool, str]:
        """Verificar tamaño de logs"""
        logs_dir = self.base_dir / "data" / "logs"
        
        if not logs_dir.exists():
            return False, "Sin logs"
        
        total_size = sum(f.stat().st_size for f in logs_dir.glob("*.log")) / (1024 * 1024)  # MB
        
        if total_size > 100:  # Más de 100MB
            return True, f"Logs ocupan {total_size:.1f}MB"
        return False, f"Logs: {total_size:.1f}MB"
    
    def check_firefox_version(self) -> Tuple[bool, str]:
        """Verificar versión de Firefox y geckodriver"""
        try:
            from webdriver_manager.firefox import GeckoDriverManager
            driver_path = GeckoDriverManager().install()
            
            if not Path(driver_path).exists():
                return True, "Geckodriver no disponible"
            
            return False, "Firefox/geckodriver disponibles"
        except Exception as e:
            return True, f"Error verificando Firefox: {e}"
    
    def check_learning_data(self) -> Tuple[bool, str]:
        """Verificar datos de aprendizaje"""
        learning_dir = self.base_dir / "data" / "learning"
        
        if not learning_dir.exists():
            return True, "Directorio de aprendizaje no existe"
        
        json_files = list(learning_dir.glob("*.json"))
        if len(json_files) == 0:
            return True, "Sin sesiones de aprendizaje"
        
        return False, f"{len(json_files)} sesiones de aprendizaje"
    
    def check_recent_activity(self) -> Tuple[bool, str]:
        """Verificar actividad reciente"""
        downloads_dir = self.base_dir / "data" / "downloads"
        
        if not downloads_dir.exists():
            return True, "Sin actividad reciente"
        
        files = list(downloads_dir.glob("*"))
        if not files:
            return True, "Sin descargas recientes"
        
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        days_old = (datetime.now().timestamp() - latest_file.stat().st_mtime) / 86400
        
        if days_old > 7:
            return True, f"Última actividad hace {days_old:.0f} días"
        return False, f"Última actividad hace {days_old:.1f} días"
    
    def check_scheduler_status(self) -> Tuple[bool, str]:
        """Verificar estado del scheduler"""
        # Por ahora simplemente verificar si existe la configuración
        config_path = self.base_dir / "config" / "scheduler_config.json"
        
        if not config_path.exists():
            return True, "Scheduler no configurado"
        
        return False, "Scheduler configurado"
    
    # FUNCIONES DE REPARACIÓN
    
    def fix_python_version(self) -> bool:
        """Reparar problema de versión Python"""
        console.print("⚠️ [yellow]Versión de Python requerida: 3.8 o superior[/yellow]")
        console.print("💡 Instala Python desde: https://python.org/downloads/")
        return False  # No se puede reparar automáticamente
    
    def fix_dependencies(self) -> bool:
        """Reparar dependencias faltantes"""
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            return True
        except Exception as e:
            console.print(f"❌ Error instalando dependencias: {e}")
            return False
    
    def fix_corrupted_config(self) -> bool:
        """Reparar configuración corrupta"""
        try:
            # Crear backup de config corrupta
            config_path = self.base_dir / "config" / "config.json"
            if config_path.exists():
                backup_path = config_path.with_suffix('.corrupted')
                config_path.rename(backup_path)
            
            # Crear nueva configuración
            from setup_wizard import AlfamineSetupWizard
            wizard = AlfamineSetupWizard()
            wizard.create_basic_config()
            
            return True
        except Exception as e:
            console.print(f"❌ Error reparando config: {e}")
            return False
    
    def fix_missing_files(self) -> bool:
        """Intentar restaurar archivos faltantes"""
        console.print("⚠️ [yellow]Archivos principales faltantes[/yellow]")
        console.print("💡 Ejecuta: python install.py para reinstalar")
        return False  # Requiere reinstalación manual
    
    def fix_outdated_selectors(self) -> bool:
        """Sugerir actualización de selectores"""
        console.print("💡 [yellow]Ejecuta una sesión de aprendizaje para actualizar selectores:[/yellow]")
        console.print("   python alfamine.py --tool main --args --mode learning")
        return False  # Requiere acción manual
    
    def fix_disk_space(self) -> bool:
        """Limpiar espacio en disco"""
        try:
            from system_monitor import AlfamineSystemMonitor
            monitor = AlfamineSystemMonitor()
            cleanup_stats = monitor.cleanup_old_files(30)
            
            return cleanup_stats['files_removed'] > 0
        except Exception as e:
            console.print(f"❌ Error limpiando espacio: {e}")
            return False
    
    def fix_large_logs(self) -> bool:
        """Limpiar logs grandes"""
        try:
            logs_dir = self.base_dir / "data" / "logs"
            if not logs_dir.exists():
                return True
            
            # Eliminar logs más antiguos de 30 días
            import time
            cutoff = time.time() - (30 * 86400)
            
            removed_count = 0
            for log_file in logs_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff:
                    log_file.unlink()
                    removed_count += 1
            
            return removed_count > 0
        except Exception as e:
            console.print(f"❌ Error limpiando logs: {e}")
            return False
    
    def fix_firefox_issues(self) -> bool:
        """Intentar reparar problemas de Firefox"""
        try:
            from webdriver_manager.firefox import GeckoDriverManager
            # Forzar descarga de nueva versión
            GeckoDriverManager().install()
            return True
        except Exception as e:
            console.print(f"❌ Error actualizando geckodriver: {e}")
            return False
    
    def fix_no_learning_data(self) -> bool:
        """Crear directorio de aprendizaje"""
        try:
            learning_dir = self.base_dir / "data" / "learning"
            learning_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            console.print(f"❌ Error creando directorio: {e}")
            return False
    
    def fix_scheduler(self) -> bool:
        """Configurar scheduler básico"""
        try:
            config_dir = self.base_dir / "config"
            config_dir.mkdir(exist_ok=True)
            
            scheduler_config = {
                'last_updated': datetime.now().isoformat(),
                'tasks': {}
            }
            
            with open(config_dir / "scheduler_config.json", 'w') as f:
                json.dump(scheduler_config, f, indent=2)
            
            return True
        except Exception as e:
            console.print(f"❌ Error configurando scheduler: {e}")
            return False
    
    def create_troubleshoot_report(self, results: Dict) -> Path:
        """Crear reporte de troubleshooting"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'platform': sys.platform,
                'working_directory': str(self.base_dir)
            },
            'diagnosis_summary': {
                'total_problems': results['total_problems'],
                'critical_problems': len(results['critical']),
                'warning_problems': len(results['warning']),
                'info_problems': len(results['info']),
                'fixable_problems': results['fixable_problems']
            },
            'problems_detail': []
        }
        
        for severity in ['critical', 'warning', 'info']:
            for problem in results[severity]:
                report_data['problems_detail'].append({
                    'name': problem.name,
                    'description': problem.description,
                    'severity': problem.severity,
                    'status': problem.status,
                    'details': problem.details,
                    'fixable': problem.fix_func is not None,
                    'fix_description': problem.fix_description
                })
        
        # Guardar reporte
        report_file = Path("reports") / f"troubleshoot_report_{datetime.now():%Y%m%d_%H%M%S}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        console.print(f"📄 [bold green]Reporte de troubleshooting guardado: {report_file.name}[/bold green]")
        return report_file


def main():
    """Función principal del troubleshooter"""
    troubleshooter = AlfamineTroubleshooter()
    
    console.print("🛠️ [bold blue]TROUBLESHOOTER ALFAMINE MONITOR[/bold blue]")
    console.print("Diagnóstico y resolución automática de problemas\n")
    
    try:
        # Ejecutar diagnóstico
        results = troubleshooter.run_diagnosis()
        
        # Mostrar resultados
        troubleshooter.display_diagnosis_results(results)
        
        # Ofrecer reparación automática
        if results['fixable_problems'] > 0:
            if Confirm.ask(f"\n¿Intentar reparar automáticamente {results['fixable_problems']} problemas?"):
                fixed_count = troubleshooter.auto_fix_problems(results)
                
                if fixed_count > 0:
                    console.print(f"\n✅ [bold green]{fixed_count} problemas reparados exitosamente[/bold green]")
                    
                    # Re-ejecutar diagnóstico para verificar
                    if Confirm.ask("¿Ejecutar nuevo diagnóstico para verificar reparaciones?"):
                        console.print("\n🔄 Re-ejecutando diagnóstico...")
                        new_results = troubleshooter.run_diagnosis()
                        troubleshooter.display_diagnosis_results(new_results)
        
        # Crear reporte
        troubleshooter.create_troubleshoot_report(results)
        
        # Sugerencias finales
        if results['total_problems'] > 0:
            console.print("\n💡 [bold yellow]Sugerencias adicionales:[/bold yellow]")
            if len(results['critical']) > 0:
                console.print("   🚨 Problemas críticos requieren atención inmediata")
                console.print("   📞 Considera ejecutar: python install.py para reinstalación")
            console.print("   📚 Consulta la documentación: README_SISTEMA_COMPLETO.md")
            console.print("   🧪 Ejecuta validación: python test_validator.py full")
        else:
            console.print("\n🎉 [bold green]¡Sistema funcionando perfectamente![/bold green]")
    
    except KeyboardInterrupt:
        console.print("\n⏹️ [yellow]Troubleshooting interrumpido[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n❌ [red]Error en troubleshooting: {e}[/red]")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)