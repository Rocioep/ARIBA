# scheduler_automation.py
"""
AUTOMATIZACIÓN Y TAREAS PROGRAMADAS ALFAMINE
Sistema de tareas programadas para monitoreo automático
"""

import schedule
import time
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.prompt import Prompt, Confirm, IntPrompt
from loguru import logger

console = Console()

@dataclass
class ScheduledTask:
    """Clase para representar una tarea programada"""
    name: str
    description: str
    script: str
    args: List[str]
    schedule_type: str  # 'daily', 'weekly', 'hourly', 'interval'
    schedule_value: str  # '09:00', 'monday', '2', etc.
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    run_count: int = 0
    success_count: int = 0

class AlfamineScheduler:
    """Planificador de tareas para Alfamine"""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.scheduler_thread = None
        self.config_file = Path("config/scheduler_config.json")
        
        # Configurar logging para scheduler
        logger.add(
            "data/logs/scheduler_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO",
            rotation="1 day",
            retention="30 days"
        )
        
        self.load_configuration()
        self.setup_default_tasks()
    
    def setup_default_tasks(self):
        """Configurar tareas por defecto"""
        default_tasks = [
            ScheduledTask(
                name="scraping_diario",
                description="Scraping automático diario de licitaciones",
                script="main_improved.py",
                args=["--mode", "scraping"],
                schedule_type="daily",
                schedule_value="09:00"
            ),
            ScheduledTask(
                name="monitoreo_sistema",
                description="Verificación diaria del estado del sistema",
                script="system_monitor.py",
                args=[],
                schedule_type="daily", 
                schedule_value="08:00"
            ),
            ScheduledTask(
                name="analisis_aprendizaje",
                description="Análisis semanal de sesiones de aprendizaje",
                script="learning_analyzer.py",
                args=[],
                schedule_type="weekly",
                schedule_value="monday"
            ),
            ScheduledTask(
                name="backup_sistema",
                description="Backup semanal del sistema",
                script="system_monitor.py",
                args=["--backup"],
                schedule_type="weekly",
                schedule_value="sunday"
            ),
            ScheduledTask(
                name="limpieza_archivos",
                description="Limpieza mensual de archivos antiguos",
                script="system_monitor.py", 
                args=["--cleanup", "30"],
                schedule_type="weekly",
                schedule_value="saturday",
                enabled=False  # Deshabilitado por defecto
            )
        ]
        
        for task in default_tasks:
            if task.name not in self.tasks:
                self.tasks[task.name] = task
    
    def load_configuration(self):
        """Cargar configuración de tareas"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Cargar tareas guardadas
                for task_name, task_data in data.get('tasks', {}).items():
                    self.tasks[task_name] = ScheduledTask(**task_data)
                
                logger.info(f"✅ Configuración cargada: {len(self.tasks)} tareas")
                
            except Exception as e:
                logger.error(f"❌ Error cargando configuración: {e}")
                console.print(f"⚠️ [yellow]Error cargando configuración del scheduler: {e}[/yellow]")
    
    def save_configuration(self):
        """Guardar configuración de tareas"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'last_updated': datetime.now().isoformat(),
                'tasks': {}
            }
            
            # Convertir tareas a diccionario
            for task_name, task in self.tasks.items():
                data['tasks'][task_name] = {
                    'name': task.name,
                    'description': task.description,
                    'script': task.script,
                    'args': task.args,
                    'schedule_type': task.schedule_type,
                    'schedule_value': task.schedule_value,
                    'enabled': task.enabled,
                    'last_run': task.last_run,
                    'next_run': task.next_run,
                    'run_count': task.run_count,
                    'success_count': task.success_count
                }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info("💾 Configuración del scheduler guardada")
            
        except Exception as e:
            logger.error(f"❌ Error guardando configuración: {e}")
    
    def register_schedules(self):
        """Registrar todas las tareas en el scheduler"""
        schedule.clear()  # Limpiar tareas anteriores
        
        for task_name, task in self.tasks.items():
            if not task.enabled:
                continue
            
            # Crear función wrapper para cada tarea
            def run_task(t=task):
                return self.execute_task(t)
            
            # Programar según tipo
            if task.schedule_type == "daily":
                schedule.every().day.at(task.schedule_value).do(run_task)
            elif task.schedule_type == "weekly":
                if task.schedule_value.lower() == "monday":
                    schedule.every().monday.at("09:00").do(run_task)
                elif task.schedule_value.lower() == "tuesday":
                    schedule.every().tuesday.at("09:00").do(run_task)
                elif task.schedule_value.lower() == "wednesday":
                    schedule.every().wednesday.at("09:00").do(run_task)
                elif task.schedule_value.lower() == "thursday":
                    schedule.every().thursday.at("09:00").do(run_task)
                elif task.schedule_value.lower() == "friday":
                    schedule.every().friday.at("09:00").do(run_task)
                elif task.schedule_value.lower() == "saturday":
                    schedule.every().saturday.at("09:00").do(run_task)
                elif task.schedule_value.lower() == "sunday":
                    schedule.every().sunday.at("09:00").do(run_task)
            elif task.schedule_type == "hourly":
                schedule.every().hour.do(run_task)
            elif task.schedule_type == "interval":
                minutes = int(task.schedule_value)
                schedule.every(minutes).minutes.do(run_task)
            
            # Actualizar próxima ejecución
            next_run = schedule.jobs[-1].next_run if schedule.jobs else None
            task.next_run = next_run.isoformat() if next_run else None
        
        logger.info(f"📅 {len([t for t in self.tasks.values() if t.enabled])} tareas programadas")
    
    def execute_task(self, task: ScheduledTask) -> bool:
        """Ejecutar una tarea específica"""
        logger.info(f"🚀 Ejecutando tarea: {task.name}")
        
        try:
            # Actualizar estadísticas
            task.run_count += 1
            task.last_run = datetime.now().isoformat()
            
            # Ejecutar comando
            cmd = [sys.executable, task.script] + task.args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hora timeout
            )
            
            if result.returncode == 0:
                task.success_count += 1
                logger.success(f"✅ Tarea {task.name} completada exitosamente")
                return True
            else:
                logger.error(f"❌ Tarea {task.name} falló con código {result.returncode}")
                logger.error(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Tarea {task.name} excedió tiempo límite")
            return False
        except Exception as e:
            logger.error(f"💥 Error ejecutando tarea {task.name}: {e}")
            return False
        finally:
            # Guardar estadísticas
            self.save_configuration()
    
    def start_scheduler(self):
        """Iniciar el scheduler en segundo plano"""
        if self.running:
            console.print("⚠️ [yellow]El scheduler ya está ejecutándose[/yellow]")
            return
        
        self.register_schedules()
        self.running = True
        
        def scheduler_loop():
            logger.info("🔄 Scheduler iniciado")
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
            logger.info("⏹️ Scheduler detenido")
        
        self.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        console.print("✅ [green]Scheduler iniciado en segundo plano[/green]")
    
    def stop_scheduler(self):
        """Detener el scheduler"""
        if not self.running:
            console.print("ℹ️ [blue]El scheduler no está ejecutándose[/blue]")
            return
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        console.print("🛑 [yellow]Scheduler detenido[/yellow]")
    
    def show_status(self):
        """Mostrar estado del scheduler"""
        console.print("\n📅 [bold blue]ESTADO DEL SCHEDULER[/bold blue]")
        
        # Estado general
        status_table = Table(title="📊 Estado General")
        status_table.add_column("Métrica", style="cyan")
        status_table.add_column("Valor", style="green")
        
        total_tasks = len(self.tasks)
        enabled_tasks = len([t for t in self.tasks.values() if t.enabled])
        total_runs = sum(t.run_count for t in self.tasks.values())
        total_success = sum(t.success_count for t in self.tasks.values())
        
        status_table.add_row("Estado", "🟢 Ejecutándose" if self.running else "🔴 Detenido")
        status_table.add_row("Total Tareas", str(total_tasks))
        status_table.add_row("Tareas Habilitadas", str(enabled_tasks))
        status_table.add_row("Total Ejecuciones", str(total_runs))
        status_table.add_row("Ejecuciones Exitosas", str(total_success))
        status_table.add_row("Tasa de Éxito", f"{(total_success/total_runs*100):.1f}%" if total_runs > 0 else "N/A")
        
        console.print(status_table)
        
        # Tabla de tareas
        tasks_table = Table(title="📋 Tareas Programadas")
        tasks_table.add_column("Nombre", style="cyan")
        tasks_table.add_column("Descripción", style="white")
        tasks_table.add_column("Horario", style="yellow")
        tasks_table.add_column("Estado", style="green")
        tasks_table.add_column("Última Ejecución", style="blue")
        tasks_table.add_column("Éxitos/Total", style="magenta")
        
        for task in self.tasks.values():
            status = "✅ Habilitada" if task.enabled else "❌ Deshabilitada"
            schedule_info = f"{task.schedule_type}: {task.schedule_value}"
            last_run = task.last_run[:16] if task.last_run else "Nunca"
            success_rate = f"{task.success_count}/{task.run_count}"
            
            tasks_table.add_row(
                task.name,
                task.description[:40] + "..." if len(task.description) > 40 else task.description,
                schedule_info,
                status,
                last_run,
                success_rate
            )
        
        console.print(tasks_table)
        
        # Próximas ejecuciones
        if self.running:
            next_jobs = []
            for job in schedule.jobs:
                next_jobs.append({
                    'task': 'Tarea programada',
                    'next_run': job.next_run.strftime("%Y-%m-%d %H:%M:%S")
                })
            
            if next_jobs:
                console.print("\n⏰ [bold yellow]Próximas Ejecuciones:[/bold yellow]")
                for job in next_jobs[:5]:  # Mostrar próximas 5
                    console.print(f"   📅 {job['next_run']}")
    
    def configure_task(self, task_name: str = None):
        """Configurar una tarea específica"""
        if task_name and task_name in self.tasks:
            task = self.tasks[task_name]
        else:
            # Mostrar lista de tareas disponibles
            console.print("\n📋 [bold]Tareas disponibles:[/bold]")
            for i, (name, task) in enumerate(self.tasks.items(), 1):
                status = "✅" if task.enabled else "❌"
                console.print(f"  {i}. {status} {name}: {task.description}")
            
            choice = Prompt.ask("Selecciona número de tarea")
            task_names = list(self.tasks.keys())
            
            try:
                task_idx = int(choice) - 1
                if 0 <= task_idx < len(task_names):
                    task = self.tasks[task_names[task_idx]]
                else:
                    console.print("❌ [red]Número inválido[/red]")
                    return
            except ValueError:
                console.print("❌ [red]Entrada inválida[/red]")
                return
        
        # Configurar tarea
        console.print(f"\n⚙️ [bold yellow]Configurando: {task.name}[/bold yellow]")
        
        # Habilitar/deshabilitar
        task.enabled = Confirm.ask(f"¿Habilitar tarea?", default=task.enabled)
        
        if task.enabled:
            # Configurar horario
            console.print(f"Horario actual: {task.schedule_type} - {task.schedule_value}")
            
            if Confirm.ask("¿Cambiar horario?", default=False):
                schedule_type = Prompt.ask(
                    "Tipo de programación",
                    choices=["daily", "weekly", "hourly", "interval"],
                    default=task.schedule_type
                )
                
                if schedule_type == "daily":
                    schedule_value = Prompt.ask("Hora (HH:MM)", default=task.schedule_value)
                elif schedule_type == "weekly":
                    schedule_value = Prompt.ask(
                        "Día de la semana",
                        choices=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
                        default=task.schedule_value
                    )
                elif schedule_type == "hourly":
                    schedule_value = "hourly"
                elif schedule_type == "interval":
                    schedule_value = str(IntPrompt.ask("Intervalo en minutos", default=int(task.schedule_value)))
                
                task.schedule_type = schedule_type
                task.schedule_value = schedule_value
        
        # Guardar cambios
        self.save_configuration()
        
        # Reiniciar scheduler si está ejecutándose
        if self.running:
            console.print("🔄 [yellow]Reiniciando scheduler con nueva configuración...[/yellow]")
            self.stop_scheduler()
            time.sleep(1)
            self.start_scheduler()
        
        console.print("✅ [green]Tarea configurada exitosamente[/green]")
    
    def run_task_now(self, task_name: str = None):
        """Ejecutar una tarea inmediatamente"""
        if task_name and task_name in self.tasks:
            task = self.tasks[task_name]
        else:
            # Seleccionar tarea
            console.print("\n📋 [bold]Seleccionar tarea para ejecutar:[/bold]")
            for i, (name, task) in enumerate(self.tasks.items(), 1):
                console.print(f"  {i}. {name}: {task.description}")
            
            choice = Prompt.ask("Selecciona número de tarea")
            task_names = list(self.tasks.keys())
            
            try:
                task_idx = int(choice) - 1
                if 0 <= task_idx < len(task_names):
                    task = self.tasks[task_names[task_idx]]
                else:
                    console.print("❌ [red]Número inválido[/red]")
                    return
            except ValueError:
                console.print("❌ [red]Entrada inválida[/red]")
                return
        
        console.print(f"🚀 [yellow]Ejecutando {task.name} inmediatamente...[/yellow]")
        
        success = self.execute_task(task)
        
        if success:
            console.print("✅ [green]Tarea ejecutada exitosamente[/green]")
        else:
            console.print("❌ [red]Error ejecutando tarea[/red]")
            console.print("💡 Revisa los logs para más detalles")
    
    def create_custom_task(self):
        """Crear una tarea personalizada"""
        console.print("\n➕ [bold yellow]CREAR TAREA PERSONALIZADA[/bold yellow]")
        
        name = Prompt.ask("Nombre de la tarea")
        
        if name in self.tasks:
            console.print("❌ [red]Ya existe una tarea con ese nombre[/red]")
            return
        
        description = Prompt.ask("Descripción")
        script = Prompt.ask("Script a ejecutar")
        
        # Argumentos opcionales
        args_input = Prompt.ask("Argumentos (separados por espacios)", default="")
        args = args_input.split() if args_input.strip() else []
        
        # Programación
        schedule_type = Prompt.ask(
            "Tipo de programación",
            choices=["daily", "weekly", "hourly", "interval"]
        )
        
        if schedule_type == "daily":
            schedule_value = Prompt.ask("Hora (HH:MM)", default="09:00")
        elif schedule_type == "weekly":
            schedule_value = Prompt.ask(
                "Día de la semana",
                choices=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            )
        elif schedule_type == "hourly":
            schedule_value = "hourly"
        elif schedule_type == "interval":
            schedule_value = str(IntPrompt.ask("Intervalo en minutos"))
        
        # Crear tarea
        task = ScheduledTask(
            name=name,
            description=description,
            script=script,
            args=args,
            schedule_type=schedule_type,
            schedule_value=schedule_value,
            enabled=True
        )
        
        self.tasks[name] = task
        self.save_configuration()
        
        console.print("✅ [green]Tarea personalizada creada exitosamente[/green]")
        
        if self.running:
            if Confirm.ask("¿Reiniciar scheduler para aplicar cambios?", default=True):
                self.stop_scheduler()
                time.sleep(1)
                self.start_scheduler()


def main():
    """Función principal del scheduler"""
    scheduler = AlfamineScheduler()
    
    console.print("📅 [bold blue]SCHEDULER ALFAMINE[/bold blue]")
    console.print("Sistema de automatización y tareas programadas\n")
    
    while True:
        console.print("\n📋 [bold]Opciones disponibles:[/bold]")
        console.print("1. 🚀 Iniciar scheduler")
        console.print("2. 🛑 Detener scheduler")
        console.print("3. 📊 Ver estado")
        console.print("4. ⚙️ Configurar tarea")
        console.print("5. ▶️ Ejecutar tarea ahora")
        console.print("6. ➕ Crear tarea personalizada")
        console.print("7. 🔄 Reiniciar scheduler")
        console.print("8. 🚪 Salir")
        
        choice = Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
        
        if choice == "1":
            scheduler.start_scheduler()
        elif choice == "2":
            scheduler.stop_scheduler()
        elif choice == "3":
            scheduler.show_status()
        elif choice == "4":
            scheduler.configure_task()
        elif choice == "5":
            scheduler.run_task_now()
        elif choice == "6":
            scheduler.create_custom_task()
        elif choice == "7":
            scheduler.stop_scheduler()
            time.sleep(1)
            scheduler.start_scheduler()
        elif choice == "8":
            if scheduler.running:
                scheduler.stop_scheduler()
            console.print("👋 [blue]¡Hasta luego![/blue]")
            break


if __name__ == "__main__":
    main()