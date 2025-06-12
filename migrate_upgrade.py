# migrate_upgrade.py
"""
HERRAMIENTA DE MIGRACIÓN Y ACTUALIZACIÓN ALFAMINE
Migra sistemas existentes y actualiza a nuevas versiones
"""

import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from rich.prompt import Confirm, Prompt
from loguru import logger

console = Console()

class AlfamineMigrator:
    """Herramienta de migración y actualización"""
    
    def __init__(self):
        self.current_version = "1.1.0"
        self.base_dir = Path.cwd()
        self.backup_dir = self.base_dir / "migration_backups" / f"backup_{datetime.now():%Y%m%d_%H%M%S}"
        
        # Mapeo de versiones y sus cambios
        self.version_changes = {
            "1.0.0": {
                "description": "Versión inicial básica",
                "files": ["main.py", "ariba_scraper_v2.2.py"],
                "config_structure": "simple"
            },
            "1.1.0": {
                "description": "Sistema mejorado con aprendizaje",
                "files": ["alfamine.py", "main_improved.py", "src/scraper_engine_improved.py"],
                "config_structure": "advanced",
                "new_features": ["learning_system", "automation", "monitoring"]
            }
        }
        
        # Archivos críticos a preservar durante migración
        self.preserve_files = [
            "config/config.json",
            "data/learning/*.json",
            "reports/*.xlsx",
            "data/logs/*.log"
        ]
    
    def detect_current_installation(self) -> Dict:
        """Detectar instalación actual"""
        console.print("🔍 [yellow]Detectando instalación actual...[/yellow]")
        
        detection = {
            'version': 'unknown',
            'type': 'unknown',
            'files_found': [],
            'config_exists': False,
            'data_exists': False,
            'needs_migration': False
        }
        
        # Detectar archivos de versiones anteriores
        legacy_files = {
            'main.py': '1.0.0',
            'ariba_scraper_v2.2.py': '1.0.0',
            'alfamine.py': '1.1.0',
            'main_improved.py': '1.1.0'
        }
        
        for file_name, version in legacy_files.items():
            file_path = self.base_dir / file_name
            if file_path.exists():
                detection['files_found'].append(file_name)
                if version > detection['version'] or detection['version'] == 'unknown':
                    detection['version'] = version
        
        # Verificar configuración
        config_path = self.base_dir / "config" / "config.json"
        if config_path.exists():
            detection['config_exists'] = True
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Determinar estructura de config
                if 'search_criteria' in config_data and 'scraping' in config_data:
                    detection['type'] = 'advanced'
                else:
                    detection['type'] = 'basic'
            except:
                detection['type'] = 'corrupted'
        
        # Verificar datos existentes
        data_dir = self.base_dir / "data"
        if data_dir.exists() and any(data_dir.iterdir()):
            detection['data_exists'] = True
        
        # Determinar si necesita migración
        if detection['version'] != self.current_version:
            detection['needs_migration'] = True
        
        return detection
    
    def display_detection_results(self, detection: Dict):
        """Mostrar resultados de detección"""
        # Panel de estado actual
        status_text = f"""
[bold cyan]Versión Detectada:[/bold cyan] {detection['version']}
[bold cyan]Tipo de Instalación:[/bold cyan] {detection['type']}
[bold cyan]Configuración:[/bold cyan] {'✅ Existe' if detection['config_exists'] else '❌ No encontrada'}
[bold cyan]Datos Existentes:[/bold cyan] {'✅ Existen' if detection['data_exists'] else '❌ No encontrados'}
[bold cyan]Migración Requerida:[/bold cyan] {'✅ Sí' if detection['needs_migration'] else '❌ No'}
        """
        
        status_panel = Panel(status_text, title="📊 Estado de la Instalación", border_style="blue")
        console.print(status_panel)
        
        # Tabla de archivos encontrados
        if detection['files_found']:
            files_table = Table(title="📁 Archivos Encontrados")
            files_table.add_column("Archivo", style="cyan")
            files_table.add_column("Versión", style="green")
            files_table.add_column("Estado", style="yellow")
            
            for file_name in detection['files_found']:
                version = next((v for f, v in [('main.py', '1.0.0'), ('ariba_scraper_v2.2.py', '1.0.0'), 
                                             ('alfamine.py', '1.1.0'), ('main_improved.py', '1.1.0')] if f == file_name), 'unknown')
                status = "🔄 Migrar" if version != self.current_version else "✅ Actual"
                files_table.add_row(file_name, version, status)
            
            console.print(files_table)
    
    def create_backup(self, detection: Dict) -> bool:
        """Crear backup completo antes de migración"""
        console.print("📦 [yellow]Creando backup completo...[/yellow]")
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup de archivos principales
            files_to_backup = detection['files_found'] + ['requirements.txt']
            for file_name in files_to_backup:
                file_path = self.base_dir / file_name
                if file_path.exists():
                    shutil.copy2(file_path, self.backup_dir)
            
            # Backup de directorios importantes
            dirs_to_backup = ['config', 'data', 'reports', 'src']
            for dir_name in dirs_to_backup:
                dir_path = self.base_dir / dir_name
                if dir_path.exists():
                    backup_dest = self.backup_dir / dir_name
                    shutil.copytree(dir_path, backup_dest, ignore_errors=True)
            
            # Crear manifiesto del backup
            manifest = {
                'backup_date': datetime.now().isoformat(),
                'original_version': detection['version'],
                'target_version': self.current_version,
                'files_backed_up': files_to_backup,
                'directories_backed_up': dirs_to_backup,
                'migration_type': f"{detection['version']} -> {self.current_version}"
            }
            
            with open(self.backup_dir / "backup_manifest.json", 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            console.print(f"✅ [green]Backup creado en: {self.backup_dir}[/green]")
            return True
            
        except Exception as e:
            console.print(f"❌ [red]Error creando backup: {e}[/red]")
            return False
    
    def migrate_config_structure(self, detection: Dict) -> bool:
        """Migrar estructura de configuración"""
        console.print("⚙️ [yellow]Migrando configuración...[/yellow]")
        
        config_path = self.base_dir / "config" / "config.json"
        
        if not config_path.exists():
            console.print("ℹ️ No hay configuración existente, creando nueva...")
            return self.create_new_config()
        
        try:
            # Leer configuración actual
            with open(config_path, 'r', encoding='utf-8') as f:
                old_config = json.load(f)
            
            # Migrar según versión detectada
            if detection['version'] == '1.0.0':
                new_config = self.migrate_from_v1_0_0(old_config)
            else:
                new_config = old_config  # Ya es compatible
            
            # Añadir nuevas secciones si no existen
            new_config = self.ensure_config_completeness(new_config)
            
            # Guardar configuración migrada
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=4, ensure_ascii=False)
            
            console.print("✅ [green]Configuración migrada exitosamente[/green]")
            return True
            
        except Exception as e:
            console.print(f"❌ [red]Error migrando configuración: {e}[/red]")
            return False
    
    def migrate_from_v1_0_0(self, old_config: Dict) -> Dict:
        """Migrar desde versión 1.0.0"""
        console.print("🔄 Migrando desde v1.0.0...")
        
        # Crear nueva estructura
        new_config = {
            "ariba_credentials": old_config.get('ariba_credentials', {
                "username": "sales@alfamine.cl",
                "password": "VI.2024al..al.",
                "url": "https://service.ariba.com/Sourcing.aw/109555009/aw?awh=r&awssk=XZHPCxm2&dard=1"
            }),
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
                "headless": old_config.get('headless', False),
                "timeout": old_config.get('timeout', 30),
                "max_retries": old_config.get('max_retries', 3)
            },
            "notifications": {
                "gmail_enabled": old_config.get('gmail_enabled', False),
                "recipients": old_config.get('recipients', ["sales@alfamine.cl"])
            }
        }
        
        # Preservar keywords personalizadas si existen
        if 'keywords' in old_config:
            # Migrar keywords antiguas a nueva estructura
            old_keywords = old_config['keywords']
            if isinstance(old_keywords, list):
                # Distribuir keywords en categorías apropiadas
                for keyword in old_keywords:
                    keyword_upper = keyword.upper()
                    if any(prod in keyword_upper for prod in ['ZAPATA', 'CADENA', 'RODILLO', 'SPROCKET']):
                        new_config['search_criteria']['lineas_producto']['ALFAMINE'].append(keyword_upper)
                    elif any(pern in keyword_upper for pern in ['PERNO', 'TUERCA', 'BOLT']):
                        new_config['search_criteria']['perneria']['keywords'].append(keyword_upper)
                    elif any(marca in keyword_upper for marca in ['CAT', 'KOMATSU']):
                        new_config['search_criteria']['marcas'].append(keyword_upper)
        
        return new_config
    
    def ensure_config_completeness(self, config: Dict) -> Dict:
        """Asegurar que la configuración esté completa"""
        # Secciones requeridas en v1.1.0
        required_sections = {
            'ariba_credentials': {
                "username": "sales@alfamine.cl",
                "password": "VI.2024al..al.",
                "url": "https://service.ariba.com/Sourcing.aw/109555009/aw?awh=r&awssk=XZHPCxm2&dard=1"
            },
            'search_criteria': {
                "lineas_producto": {"ALFAMINE": ["ZAPATA", "CADENA", "RODILLOS", "SPROCKET"]},
                "perneria": {"keywords": ["PERNO", "TUERCA"], "prefijos": ["AL00"]},
                "marcas": ["CAT", "KOMATSU"]
            },
            'scraping': {
                "browser_type": "firefox",
                "headless": False,
                "timeout": 30,
                "max_retries": 3
            },
            'notifications': {
                "gmail_enabled": False,
                "recipients": ["sales@alfamine.cl"]
            }
        }
        
        for section, default_values in required_sections.items():
            if section not in config:
                config[section] = default_values
            else:
                # Asegurar subsecciones
                for key, value in default_values.items():
                    if key not in config[section]:
                        config[section][key] = value
        
        return config
    
    def create_new_config(self) -> bool:
        """Crear nueva configuración desde cero"""
        config_dir = self.base_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        new_config = {
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
        
        config_path = config_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=4, ensure_ascii=False)
        
        return True
    
    def migrate_learning_data(self) -> bool:
        """Migrar datos de aprendizaje existentes"""
        console.print("🎓 [yellow]Migrando datos de aprendizaje...[/yellow]")
        
        learning_dir = self.base_dir / "data" / "learning"
        if not learning_dir.exists():
            console.print("ℹ️ No hay datos de aprendizaje existentes")
            return True
        
        try:
            # Validar archivos de aprendizaje existentes
            valid_files = 0
            total_files = 0
            
            for json_file in learning_dir.glob("*.json"):
                total_files += 1
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Verificar estructura básica
                    if isinstance(data, dict):
                        valid_files += 1
                except:
                    # Mover archivo corrupto a backup
                    corrupted_file = json_file.with_suffix('.corrupted')
                    json_file.rename(corrupted_file)
                    console.print(f"⚠️ Archivo corrupto movido: {json_file.name}")
            
            console.print(f"✅ [green]{valid_files}/{total_files} archivos de aprendizaje válidos[/green]")
            return True
            
        except Exception as e:
            console.print(f"❌ [red]Error migrando datos de aprendizaje: {e}[/red]")
            return False
    
    def update_file_structure(self, detection: Dict) -> bool:
        """Actualizar estructura de archivos"""
        console.print("📁 [yellow]Actualizando estructura de archivos...[/yellow]")
        
        # Crear directorios necesarios para v1.1.0
        required_dirs = [
            "src", "config", "data/logs", "data/downloads", 
            "data/screenshots", "data/learning", "reports", "backups"
        ]
        
        for dir_path in required_dirs:
            full_path = self.base_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
        
        # Renombrar archivos obsoletos
        if detection['version'] == '1.0.0':
            old_files = {
                'main.py': 'main_legacy.py',
                'ariba_scraper_v2.2.py': 'scraper_legacy.py'
            }
            
            for old_name, new_name in old_files.items():
                old_path = self.base_dir / old_name
                if old_path.exists():
                    new_path = self.base_dir / new_name
                    old_path.rename(new_path)
                    console.print(f"📦 Renombrado: {old_name} -> {new_name}")
        
        console.print("✅ [green]Estructura de archivos actualizada[/green]")
        return True
    
    def run_migration(self) -> bool:
        """Ejecutar migración completa"""
        console.print("🔄 [bold blue]INICIANDO MIGRACIÓN ALFAMINE[/bold blue]")
        
        # 1. Detectar instalación actual
        detection = self.detect_current_installation()
        self.display_detection_results(detection)
        
        if not detection['needs_migration']:
            console.print("✅ [green]Sistema ya está actualizado, no se requiere migración[/green]")
            return True
        
        # 2. Confirmar migración
        if not Confirm.ask(f"\n¿Proceder con migración de {detection['version']} a {self.current_version}?"):
            console.print("⏹️ Migración cancelada")
            return False
        
        # 3. Crear backup
        if not self.create_backup(detection):
            console.print("❌ Error creando backup, migración abortada")
            return False
        
        # 4. Migrar componentes
        with Progress() as progress:
            task = progress.add_task("Migrando sistema...", total=4)
            
            # Migrar configuración
            progress.update(task, description="⚙️ Migrando configuración...")
            if not self.migrate_config_structure(detection):
                return False
            progress.advance(task)
            
            # Migrar datos de aprendizaje
            progress.update(task, description="🎓 Migrando datos de aprendizaje...")
            self.migrate_learning_data()
            progress.advance(task)
            
            # Actualizar estructura
            progress.update(task, description="📁 Actualizando estructura...")
            self.update_file_structure(detection)
            progress.advance(task)
            
            # Validar migración
            progress.update(task, description="🧪 Validando migración...")
            self.validate_migration()
            progress.advance(task)
        
        console.print("🎉 [bold green]Migración completada exitosamente[/bold green]")
        return True
    
    def validate_migration(self) -> bool:
        """Validar que la migración fue exitosa"""
        try:
            # Verificar archivos críticos
            critical_files = [
                "config/config.json",
                "alfamine.py",
                "main_improved.py"
            ]
            
            for file_path in critical_files:
                if not (self.base_dir / file_path).exists():
                    console.print(f"⚠️ Archivo crítico faltante: {file_path}")
                    return False
            
            # Verificar estructura de config
            config_path = self.base_dir / "config" / "config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            required_sections = ['ariba_credentials', 'search_criteria', 'scraping', 'notifications']
            for section in required_sections:
                if section not in config:
                    console.print(f"⚠️ Sección de config faltante: {section}")
                    return False
            
            return True
            
        except Exception as e:
            console.print(f"❌ Error validando migración: {e}")
            return False
    
    def rollback_migration(self) -> bool:
        """Revertir migración usando backup"""
        console.print("🔄 [yellow]Iniciando rollback de migración...[/yellow]")
        
        if not self.backup_dir.exists():
            console.print("❌ No se encontró backup para rollback")
            return False
        
        try:
            # Restaurar archivos desde backup
            for item in self.backup_dir.iterdir():
                if item.name == "backup_manifest.json":
                    continue
                
                dest_path = self.base_dir / item.name
                
                if item.is_dir():
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.copytree(item, dest_path)
                else:
                    shutil.copy2(item, dest_path)
            
            console.print("✅ [green]Rollback completado exitosamente[/green]")
            return True
            
        except Exception as e:
            console.print(f"❌ [red]Error en rollback: {e}[/red]")
            return False


def main():
    """Función principal"""
    migrator = AlfamineMigrator()
    
    console.print("🔄 [bold blue]HERRAMIENTA DE MIGRACIÓN ALFAMINE MONITOR[/bold blue]")
    console.print("Migra sistemas existentes a la última versión\n")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "rollback":
            return 0 if migrator.rollback_migration() else 1
        elif sys.argv[1] == "detect":
            detection = migrator.detect_current_installation()
            migrator.display_detection_results(detection)
            return 0
    
    try:
        success = migrator.run_migration()
        
        if success:
            console.print("\n🎉 [bold green]¡Migración completada exitosamente![/bold green]")
            console.print("\n📋 [bold yellow]Próximos pasos:[/bold yellow]")
            console.print("1. Ejecutar: python test_validator.py full")
            console.print("2. Verificar: python alfamine.py --status")
            console.print("3. Probar: python alfamine.py --quick")
        else:
            console.print("\n❌ [red]Migración falló[/red]")
            console.print("💡 Puedes revertir con: python migrate_upgrade.py rollback")
            return 1
    
    except KeyboardInterrupt:
        console.print("\n⏹️ [yellow]Migración interrumpida[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n❌ [red]Error en migración: {e}[/red]")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)