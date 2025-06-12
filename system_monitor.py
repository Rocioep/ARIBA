# system_monitor.py
"""
MONITOR DE SISTEMA ALFAMINE
Monitoreo de archivos, estadísticas y mantenimiento automático
"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.layout import Layout
from rich.live import Live
import time

console = Console()

class AlfamineSystemMonitor:
    """Monitor de sistema para Alfamine"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.data_dir = self.base_dir / "data"
        self.reports_dir = self.base_dir / "reports"
        
        self.stats = {
            'downloads': {},
            'learning_sessions': {},
            'reports': {},
            'logs': {},
            'disk_usage': {}
        }
    
    def run_system_check(self) -> Dict:
        """Ejecutar verificación completa del sistema"""
        console.print("🔍 [bold blue]VERIFICACIÓN COMPLETA DEL SISTEMA[/bold blue]")
        
        checks = {
            'directories': self.check_directories(),
            'configuration': self.check_configuration(),
            'downloads': self.analyze_downloads(),
            'learning_data': self.analyze_learning_data(),
            'reports': self.analyze_reports(),
            'disk_usage': self.check_disk_usage(),
            'logs': self.analyze_logs()
        }
        
        self.display_system_overview(checks)
        return checks
    
    def check_directories(self) -> Dict:
        """Verificar estructura de directorios"""
        required_dirs = [
            'config', 'data', 'data/logs', 'data/downloads', 
            'data/screenshots', 'data/learning', 'reports', 'src'
        ]
        
        dir_status = {}
        for dir_path in required_dirs:
            path = self.base_dir / dir_path
            dir_status[dir_path] = {
                'exists': path.exists(),
                'is_dir': path.is_dir() if path.exists() else False,
                'size_mb': self.get_directory_size(path) if path.exists() else 0,
                'file_count': len(list(path.rglob('*'))) if path.exists() else 0
            }
        
        return dir_status
    
    def check_configuration(self) -> Dict:
        """Verificar archivos de configuración"""
        config_files = {
            'config/config.json': 'Configuración principal',
            'config/optimized_selectors.json': 'Selectores optimizados',
            'config/installation_status.json': 'Estado de instalación'
        }
        
        config_status = {}
        for file_path, description in config_files.items():
            path = self.base_dir / file_path
            
            status = {
                'exists': path.exists(),
                'description': description,
                'size_bytes': path.stat().st_size if path.exists() else 0,
                'modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat() if path.exists() else None
            }
            
            # Validar contenido JSON
            if path.exists() and path.suffix == '.json':
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    status['valid_json'] = True
                    status['keys_count'] = len(data) if isinstance(data, dict) else 0
                except Exception as e:
                    status['valid_json'] = False
                    status['error'] = str(e)
            
            config_status[file_path] = status
        
        return config_status
    
    def analyze_downloads(self) -> Dict:
        """Analizar archivos descargados"""
        downloads_dir = self.data_dir / "downloads"
        
        if not downloads_dir.exists():
            return {'total_files': 0, 'total_size_mb': 0}
        
        files = list(downloads_dir.glob("*"))
        
        analysis = {
            'total_files': len(files),
            'total_size_mb': sum(f.stat().st_size for f in files if f.is_file()) / (1024 * 1024),
            'by_extension': {},
            'by_date': {},
            'recent_files': []
        }
        
        # Análisis por extensión
        for file in files:
            if file.is_file():
                ext = file.suffix.lower()
                if ext not in analysis['by_extension']:
                    analysis['by_extension'][ext] = {'count': 0, 'size_mb': 0}
                
                analysis['by_extension'][ext]['count'] += 1
                analysis['by_extension'][ext]['size_mb'] += file.stat().st_size / (1024 * 1024)
        
        # Archivos recientes (última semana)
        week_ago = datetime.now() - timedelta(days=7)
        for file in files:
            if file.is_file():
                modified = datetime.fromtimestamp(file.stat().st_mtime)
                if modified > week_ago:
                    analysis['recent_files'].append({
                        'name': file.name,
                        'size_mb': file.stat().st_size / (1024 * 1024),
                        'modified': modified.isoformat()
                    })
        
        # Ordenar archivos recientes por fecha
        analysis['recent_files'].sort(key=lambda x: x['modified'], reverse=True)
        
        return analysis
    
    def analyze_learning_data(self) -> Dict:
        """Analizar datos de aprendizaje"""
        learning_dir = self.data_dir / "learning"
        
        if not learning_dir.exists():
            return {'total_sessions': 0}
        
        files = list(learning_dir.glob("*.json"))
        
        analysis = {
            'total_sessions': len(files),
            'session_types': {},
            'success_rate': {},
            'recent_sessions': []
        }
        
        successful_sessions = 0
        
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Determinar tipo de sesión
                session_type = 'unknown'
                if 'step_by_step' in file.name:
                    session_type = 'step_by_step'
                elif 'corporation_selection' in file.name:
                    session_type = 'corporation_selection'
                elif 'elements_' in file.name:
                    session_type = 'elements_capture'
                
                if session_type not in analysis['session_types']:
                    analysis['session_types'][session_type] = 0
                analysis['session_types'][session_type] += 1
                
                # Verificar éxito
                success_indicators = [
                    data.get('success', False),
                    data.get('total_steps', 0) > 0,
                    len(data.get('successful_selectors', {})) > 0
                ]
                
                if any(success_indicators):
                    successful_sessions += 1
                
                # Sesiones recientes
                modified = datetime.fromtimestamp(file.stat().st_mtime)
                if modified > datetime.now() - timedelta(days=7):
                    analysis['recent_sessions'].append({
                        'file': file.name,
                        'type': session_type,
                        'modified': modified.isoformat(),
                        'success': any(success_indicators)
                    })
                
            except Exception as e:
                continue
        
        analysis['success_rate'] = {
            'successful': successful_sessions,
            'total': len(files),
            'percentage': (successful_sessions / len(files) * 100) if files else 0
        }
        
        return analysis
    
    def analyze_reports(self) -> Dict:
        """Analizar reportes generados"""
        if not self.reports_dir.exists():
            return {'total_reports': 0}
        
        reports = list(self.reports_dir.glob("*.xlsx"))
        
        analysis = {
            'total_reports': len(reports),
            'total_size_mb': sum(r.stat().st_size for r in reports) / (1024 * 1024),
            'recent_reports': []
        }
        
        # Reportes recientes
        for report in reports:
            modified = datetime.fromtimestamp(report.stat().st_mtime)
            if modified > datetime.now() - timedelta(days=30):
                analysis['recent_reports'].append({
                    'name': report.name,
                    'size_mb': report.stat().st_size / (1024 * 1024),
                    'modified': modified.isoformat()
                })
        
        analysis['recent_reports'].sort(key=lambda x: x['modified'], reverse=True)
        
        return analysis
    
    def analyze_logs(self) -> Dict:
        """Analizar archivos de log"""
        logs_dir = self.data_dir / "logs"
        
        if not logs_dir.exists():
            return {'total_logs': 0}
        
        log_files = list(logs_dir.glob("*.log"))
        
        analysis = {
            'total_logs': len(log_files),
            'total_size_mb': sum(f.stat().st_size for f in log_files) / (1024 * 1024),
            'recent_logs': []
        }
        
        # Logs recientes
        for log_file in log_files:
            modified = datetime.fromtimestamp(log_file.stat().st_mtime)
            if modified > datetime.now() - timedelta(days=7):
                analysis['recent_logs'].append({
                    'name': log_file.name,
                    'size_mb': log_file.stat().st_size / (1024 * 1024),
                    'modified': modified.isoformat()
                })
        
        return analysis
    
    def check_disk_usage(self) -> Dict:
        """Verificar uso de disco"""
        usage = {}
        
        for directory in ['data', 'reports', 'config']:
            dir_path = self.base_dir / directory
            if dir_path.exists():
                usage[directory] = self.get_directory_size(dir_path)
        
        return usage
    
    def get_directory_size(self, path: Path) -> float:
        """Obtener tamaño de directorio en MB"""
        try:
            total_size = sum(
                file.stat().st_size 
                for file in path.rglob('*') 
                if file.is_file()
            )
            return total_size / (1024 * 1024)  # Convertir a MB
        except Exception:
            return 0.0
    
    def display_system_overview(self, checks: Dict):
        """Mostrar resumen del sistema"""
        
        # Tabla de estado general
        status_table = Table(title="📊 Estado General del Sistema")
        status_table.add_column("Componente", style="cyan")
        status_table.add_column("Estado", style="green")
        status_table.add_column("Detalles", style="yellow")
        
        # Directorios
        dirs_ok = sum(1 for d in checks['directories'].values() if d['exists'])
        total_dirs = len(checks['directories'])
        status_table.add_row(
            "Directorios",
            "✅ OK" if dirs_ok == total_dirs else f"⚠️ {dirs_ok}/{total_dirs}",
            f"{dirs_ok} de {total_dirs} directorios"
        )
        
        # Configuración
        configs_ok = sum(1 for c in checks['configuration'].values() if c['exists'])
        total_configs = len(checks['configuration'])
        status_table.add_row(
            "Configuración",
            "✅ OK" if configs_ok >= 1 else "❌ Falta",
            f"{configs_ok} archivos de configuración"
        )
        
        # Descargas
        downloads = checks['downloads']
        status_table.add_row(
            "Descargas",
            "✅ OK" if downloads['total_files'] > 0 else "ℹ️ Vacío",
            f"{downloads['total_files']} archivos ({downloads['total_size_mb']:.1f} MB)"
        )
        
        # Aprendizaje
        learning = checks['learning_data']
        status_table.add_row(
            "Datos de Aprendizaje",
            "✅ OK" if learning['total_sessions'] > 0 else "ℹ️ Sin datos",
            f"{learning['total_sessions']} sesiones ({learning.get('success_rate', {}).get('percentage', 0):.1f}% éxito)"
        )
        
        # Reportes
        reports = checks['reports']
        status_table.add_row(
            "Reportes",
            "✅ OK" if reports['total_reports'] > 0 else "ℹ️ Sin reportes",
            f"{reports['total_reports']} reportes ({reports['total_size_mb']:.1f} MB)"
        )
        
        console.print(status_table)
        
        # Tabla de uso de disco
        if checks['disk_usage']:
            disk_table = Table(title="💾 Uso de Disco")
            disk_table.add_column("Directorio", style="cyan")
            disk_table.add_column("Tamaño (MB)", style="green")
            
            total_size = 0
            for directory, size_mb in checks['disk_usage'].items():
                disk_table.add_row(directory, f"{size_mb:.1f}")
                total_size += size_mb
            
            disk_table.add_row("[bold]TOTAL[/bold]", f"[bold]{total_size:.1f}[/bold]")
            console.print(disk_table)
    
    def cleanup_old_files(self, days_old: int = 30) -> Dict:
        """Limpiar archivos antiguos"""
        console.print(f"🧹 [yellow]Limpiando archivos anteriores a {days_old} días...[/yellow]")
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleanup_stats = {
            'files_removed': 0,
            'space_freed_mb': 0,
            'directories_cleaned': []
        }
        
        # Directorios a limpiar
        cleanup_dirs = [
            self.data_dir / "screenshots",
            self.data_dir / "logs",
            self.data_dir / "downloads"  # Solo si hay muchos archivos
        ]
        
        for dir_path in cleanup_dirs:
            if not dir_path.exists():
                continue
            
            files_removed = 0
            space_freed = 0
            
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if modified < cutoff_date:
                        # Verificar que no sea un archivo crítico
                        if not self.is_critical_file(file_path):
                            try:
                                size = file_path.stat().st_size
                                file_path.unlink()
                                files_removed += 1
                                space_freed += size
                            except Exception as e:
                                console.print(f"⚠️ Error eliminando {file_path.name}: {e}")
            
            if files_removed > 0:
                cleanup_stats['directories_cleaned'].append({
                    'directory': str(dir_path.relative_to(self.base_dir)),
                    'files_removed': files_removed,
                    'space_freed_mb': space_freed / (1024 * 1024)
                })
                
                cleanup_stats['files_removed'] += files_removed
                cleanup_stats['space_freed_mb'] += space_freed / (1024 * 1024)
        
        if cleanup_stats['files_removed'] > 0:
            console.print(f"✅ Limpieza completada:")
            console.print(f"   📁 {cleanup_stats['files_removed']} archivos eliminados")
            console.print(f"   💾 {cleanup_stats['space_freed_mb']:.1f} MB liberados")
        else:
            console.print("ℹ️ No se encontraron archivos antiguos para eliminar")
        
        return cleanup_stats
    
    def is_critical_file(self, file_path: Path) -> bool:
        """Verificar si un archivo es crítico y no debe eliminarse"""
        critical_patterns = [
            'config.json',
            'optimized_selectors.json',
            'installation_status.json'
        ]
        
        return any(pattern in file_path.name for pattern in critical_patterns)
    
    def create_backup(self) -> Optional[Path]:
        """Crear backup del sistema"""
        console.print("📦 [yellow]Creando backup del sistema...[/yellow]")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path("backups") / f"alfamine_backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Backup de configuración
            config_backup = backup_dir / "config"
            if (self.base_dir / "config").exists():
                shutil.copytree(self.base_dir / "config", config_backup)
            
            # Backup de datos de aprendizaje
            learning_backup = backup_dir / "learning"
            if (self.data_dir / "learning").exists():
                shutil.copytree(self.data_dir / "learning", learning_backup)
            
            # Backup de reportes recientes (últimos 30 días)
            if self.reports_dir.exists():
                reports_backup = backup_dir / "reports"
                reports_backup.mkdir(exist_ok=True)
                
                cutoff = datetime.now() - timedelta(days=30)
                for report in self.reports_dir.glob("*.xlsx"):
                    modified = datetime.fromtimestamp(report.stat().st_mtime)
                    if modified > cutoff:
                        shutil.copy2(report, reports_backup)
            
            # Crear manifiesto del backup
            manifest = {
                'created_at': datetime.now().isoformat(),
                'version': '1.1.0',
                'backup_type': 'full_system',
                'contents': {
                    'config': (config_backup).exists(),
                    'learning_data': (learning_backup).exists(),
                    'recent_reports': len(list((backup_dir / "reports").glob("*"))) if (backup_dir / "reports").exists() else 0
                }
            }
            
            with open(backup_dir / "manifest.json", 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            console.print(f"✅ Backup creado: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            console.print(f"❌ Error creando backup: {e}")
            return None
    
    def watch_downloads(self, duration_minutes: int = 10):
        """Monitorear descargas en tiempo real"""
        console.print(f"👁️ [cyan]Monitoreando descargas por {duration_minutes} minutos...[/cyan]")
        
        downloads_dir = self.data_dir / "downloads"
        downloads_dir.mkdir(exist_ok=True)
        
        initial_files = set(downloads_dir.glob("*"))
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        with Live(console=console, refresh_per_second=1) as live:
            while time.time() < end_time:
                current_files = set(downloads_dir.glob("*"))
                new_files = current_files - initial_files
                
                # Crear tabla de estado
                status_table = Table(title=f"📥 Monitor de Descargas - {datetime.now():%H:%M:%S}")
                status_table.add_column("Métrica", style="cyan")
                status_table.add_column("Valor", style="green")
                
                remaining_time = int(end_time - time.time())
                
                status_table.add_row("Tiempo restante", f"{remaining_time // 60}:{remaining_time % 60:02d}")
                status_table.add_row("Archivos iniciales", str(len(initial_files)))
                status_table.add_row("Archivos actuales", str(len(current_files)))
                status_table.add_row("Nuevos archivos", str(len(new_files)))
                
                if new_files:
                    status_table.add_row("Último archivo", list(new_files)[-1].name)
                
                live.update(status_table)
                time.sleep(1)
        
        final_files = set(downloads_dir.glob("*"))
        new_downloads = final_files - initial_files
        
        if new_downloads:
            console.print(f"🎉 [green]{len(new_downloads)} nuevos archivos detectados:[/green]")
            for file in new_downloads:
                size_mb = file.stat().st_size / (1024 * 1024)
                console.print(f"   📄 {file.name} ({size_mb:.1f} MB)")
        else:
            console.print("ℹ️ No se detectaron nuevas descargas")


def main():
    """Función principal del monitor"""
    monitor = AlfamineSystemMonitor()
    
    console.print("🖥️ [bold blue]MONITOR DE SISTEMA ALFAMINE[/bold blue]")
    
    while True:
        console.print("\n📋 [bold]Opciones disponibles:[/bold]")
        console.print("1. 🔍 Verificación completa del sistema")
        console.print("2. 📊 Ver estadísticas detalladas")
        console.print("3. 🧹 Limpiar archivos antiguos")
        console.print("4. 📦 Crear backup del sistema")
        console.print("5. 👁️ Monitorear descargas en tiempo real")
        console.print("6. 🚪 Salir")
        
        from rich.prompt import Prompt
        choice = Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "4", "5", "6"])
        
        if choice == "1":
            monitor.run_system_check()
        elif choice == "2":
            checks = monitor.run_system_check()
            # Mostrar estadísticas adicionales aquí
        elif choice == "3":
            days = int(Prompt.ask("Días de antigüedad para limpieza", default="30"))
            monitor.cleanup_old_files(days)
        elif choice == "4":
            monitor.create_backup()
        elif choice == "5":
            minutes = int(Prompt.ask("Minutos de monitoreo", default="10"))
            monitor.watch_downloads(minutes)
        elif choice == "6":
            console.print("👋 [blue]¡Hasta luego![/blue]")
            break


if __name__ == "__main__":
    main()