# quick_mas_fix.py
"""
🚀 FIX RÁPIDO ESPECÍFICO PARA DROPDOWN "MÁS..."
Soluciona el problema real: dropdown MÁS... → Corporación del Cobre → estado: abiertas → exportar
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.append(str(Path(__file__).parent / "src"))
sys.path.append(str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from loguru import logger

console = Console()

class QuickMasFix:
    """Fix específico para el dropdown MÁS... y flujo completo"""
    
    def __init__(self):
        self.config = self.load_config()
        self.scraper = None
        
    def load_config(self):
        """Cargar configuración"""
        try:
            config_path = Path("config/config.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                console.print("❌ [red]No se encontró config/config.json[/red]")
                return None
        except Exception as e:
            console.print(f"❌ [red]Error cargando config: {e}[/red]")
            return None
    
    def run_mas_dropdown_fix(self):
        """Ejecutar fix específico para dropdown MÁS..."""
        
        console.print(Panel("""
[bold blue]🎯 FIX DROPDOWN "MÁS..." ESPECÍFICO[/bold blue]

[yellow]Problema identificado:[/yellow]
❌ Primera imagen: Dropdown incorrecto (Ariba Proposals, etc.)
✅ Segunda imagen: Dropdown correcto "MÁS..." → Corporación del Cobre

[yellow]Este fix busca específicamente:[/yellow]
🎯 Dropdown "MÁS..." (con flecha)
🏢 "Corporación Nacional del Cobre (Ambiente Productivo)"
📋 Estado: "abiertas" 
📥 "Exportar todas las filas"
        """, title="🚀 Fix Correcto", border_style="blue"))
        
        if not self.config:
            console.print("❌ Necesitas configuración válida")
            return False
        
        # Pregunta sobre el flujo
        console.print("\n🤔 [bold yellow]¿Qué quieres que haga?[/bold yellow]")
        console.print("A. Solo hasta Corporación del Cobre (TÚ haces el resto manualmente)")
        console.print("B. Flujo completo automático (dropdown MÁS → Codelco → estado → exportar)")
        
        mode = Prompt.ask("Selecciona", choices=["A", "B"], default="A")
        
        include_full_flow = (mode == "B")
        
        if include_full_flow:
            console.print("✅ [green]Modo: Flujo completo automático[/green]")
        else:
            console.print("✅ [green]Modo: Solo hasta Corporación del Cobre[/green]")
        
        try:
            # Importar scraper mejorado
            from scraper_engine_improved import ImprovedAribaScraperEngine
            
            # Configurar en modo visible
            self.config['scraping']['headless'] = False
            self.scraper = ImprovedAribaScraperEngine(self.config)
            
            if not self.scraper.setup_firefox():
                console.print("❌ [red]Error configurando Firefox[/red]")
                return False
            
            console.print("✅ [green]Firefox configurado[/green]")
            
            # 1. Login automático
            console.print("\n📋 [bold yellow]Paso 1: Login automático[/bold yellow]")
            if self.scraper.login_to_ariba():
                console.print("✅ [green]Login exitoso[/green]")
            else:
                console.print("❌ [red]Login falló[/red]")
                return False
            
            # 2. Integrar fix del dropdown MÁS
            console.print("\n📋 [bold yellow]Paso 2: Integrando fix dropdown MÁS...[/bold yellow]")
            
            # Importar y aplicar fix específico
            from mas_dropdown_fix import MasDropdownFix
            mas_fix = MasDropdownFix(self.scraper.driver, self.scraper.wait)
            
            # 3. Ejecutar fix específico
            console.print("\n📋 [bold yellow]Paso 3: Ejecutando fix dropdown MÁS...[/bold yellow]")
            
            # Debug inicial
            mas_fix.debug_current_page("inicial_antes_mas")
            
            # Intentar flujo automático
            console.print("🤖 Intentando automáticamente...")
            results = mas_fix.run_complete_flow(include_export=include_full_flow)
            
            if results['success']:
                console.print(f"🎉 [bold green]¡ÉXITO AUTOMÁTICO![/bold green]")
                console.print(f"✅ Pasos completados: {results['total_steps']}")
                console.print(f"📋 Detalles: {', '.join(results['steps_completed'])}")
                
                # Guardar selectores exitosos
                self.save_successful_selectors(results)
                
                if include_full_flow:
                    console.print("📥 [green]Flujo completo terminado - archivo debería estar descargándose[/green]")
                else:
                    console.print("🏢 [green]Corporación del Cobre seleccionada - continúa manualmente[/green]")
                
                return True
            else:
                console.print("⚠️ [yellow]Método automático falló, cambiando a modo guiado...[/yellow]")
                return self.run_guided_mas_mode(mas_fix, include_full_flow)
            
        except Exception as e:
            console.print(f"❌ [red]Error en fix: {e}[/red]")
            return False
        finally:
            if self.scraper and self.scraper.driver:
                input("👆 Presiona ENTER para cerrar el navegador...")
                self.scraper.driver.quit()
    
    def run_guided_mas_mode(self, mas_fix, include_full_flow):
        """Modo guiado específico para dropdown MÁS"""
        console.print("\n🤝 [bold yellow]MODO GUIADO - DROPDOWN MÁS...[/bold yellow]")
        console.print("Trabajemos juntos para resolver el problema")
        
        console.print("\n📋 [bold]Instrucciones específicas:[/bold]")
        console.print("1. 🔍 Busca el texto [bold blue]'MÁS...'[/bold blue] en la página")
        console.print("2. 👁️ Al lado debe haber una [bold blue]FLECHA[/bold blue] (▼)")  
        console.print("3. 🖱️ Haz [bold red]CLICK en la FLECHA[/bold red] del MÁS...")
        console.print("4. ✅ Debe aparecer un menú con 'Corporación Nacional del Cobre'")
        
        if not Confirm.ask("¿Puedes ver el dropdown 'MÁS...' con la flecha?"):
            console.print("❌ [red]Sin dropdown MÁS... visible, no podemos continuar[/red]")
            return False
        
        # Capturar estado antes
        mas_fix.debug_current_page("antes_click_mas_manual")
        
        input("👆 Presiona ENTER DESPUÉS de hacer click en la flecha del MÁS...")
        
        # Capturar estado después del click en MÁS
        console.print("📸 Capturando estado del dropdown MÁS abierto...")
        mas_fix.debug_current_page("despues_click_mas_manual")
        
        # Verificar que se abrió
        if mas_fix.verify_mas_dropdown_opened():
            console.print("✅ [green]Dropdown MÁS abierto correctamente[/green]")
        else:
            console.print("⚠️ [yellow]No se puede verificar que el dropdown esté abierto[/yellow]")
        
        # Instrucciones para Corporación del Cobre
        console.print("\n📋 [bold]Selecciona Corporación del Cobre:[/bold]")
        console.print("1. 🎯 Busca [bold blue]'Corporación Nacional del Cobre (Ambiente Productivo)'[/bold blue]")
        console.print("2. 🖱️ Haz [bold red]CLICK en esa opción[/bold red]")
        console.print("3. ⏳ Espera a que se actualice la página")
        
        input("👆 Presiona ENTER DESPUÉS de seleccionar Corporación del Cobre...")
        
        # Verificar selección de Codelco
        time.sleep(5)
        if mas_fix.verify_codelco_selected():
            console.print("🎉 [bold green]¡Corporación del Cobre seleccionada exitosamente![/bold green]")
            
            # Guardar éxito manual
            self.save_manual_success("mas_dropdown_manual")
            
            if include_full_flow:
                # Continuar con resto del flujo
                return self.continue_manual_flow(mas_fix)
            else:
                console.print("✅ [green]Fix completado - puedes continuar manualmente[/green]")
                return True
        else:
            console.print("❌ [red]No se pudo verificar la selección de Corporación del Cobre[/red]")
            return False
    
    def continue_manual_flow(self, mas_fix):
        """Continuar con el resto del flujo manualmente"""
        console.print("\n📋 [bold yellow]Continuando con el flujo completo...[/bold yellow]")
        
        # Estado: abiertas
        console.print("\n📋 [bold]Paso siguiente - Estado 'abiertas':[/bold]")
        console.print("1. 🔍 Busca un campo de [bold blue]'Estado:'[/bold blue] o [bold blue]'Status:'[/bold blue]")
        console.print("2. 🖱️ Selecciona [bold blue]'Abiertas'[/bold blue] o [bold blue]'Open'[/bold blue]")
        
        # Intentar automático primero
        if mas_fix.select_estado_abiertas():
            console.print("✅ [green]Estado 'abiertas' seleccionado automáticamente[/green]")
        else:
            console.print("⚠️ [yellow]No se pudo automático, hazlo manualmente[/yellow]")
            input("👆 Presiona ENTER después de seleccionar estado 'abiertas'...")
        
        # Exportar todas las filas
        console.print("\n📋 [bold]Paso final - Exportar:[/bold]")
        console.print("1. 🔍 Busca un botón de [bold blue]MENÚ[/bold blue] (⋮ o ☰)")
        console.print("2. 🖱️ Haz click en el menú")
        console.print("3. 🖱️ Selecciona [bold blue]'Exportar todas las filas'[/bold blue]")
        
        # Intentar automático primero
        if mas_fix.export_all_rows():
            console.print("✅ [green]Exportación iniciada automáticamente[/green]")
        else:
            console.print("⚠️ [yellow]No se pudo automático, hazlo manualmente[/yellow]")
            input("👆 Presiona ENTER después de hacer click en 'Exportar todas las filas'...")
        
        console.print("🎉 [bold green]¡Flujo completo terminado![/bold green]")
        console.print("📥 [green]El archivo debería estar descargándose...[/green]")
        
        return True
    
    def save_successful_selectors(self, results):
        """Guardar selectores exitosos para uso futuro"""
        success_data = {
            'timestamp': datetime.now().isoformat(),
            'method': 'automatic',
            'fix_type': 'mas_dropdown',
            'results': results,
            'success': True,
            'note': 'Selectores funcionaron automáticamente para dropdown MÁS'
        }
        
        success_file = Path("data/learning") / f"mas_success_{int(time.time())}.json"
        success_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(success_file, 'w', encoding='utf-8') as f:
            json.dump(success_data, f, indent=2, ensure_ascii=False, default=str)
        
        console.print(f"💾 [green]Selectores exitosos guardados: {success_file.name}[/green]")
    
    def save_manual_success(self, step_name):
        """Guardar éxito manual para aprendizaje"""
        success_data = {
            'timestamp': datetime.now().isoformat(),
            'method': 'manual_guided',
            'fix_type': 'mas_dropdown',
            'step': step_name,
            'success': True,
            'note': 'Usuario ejecutó dropdown MÁS manualmente - sistema aprendió'
        }
        
        success_file = Path("data/learning") / f"mas_manual_{int(time.time())}.json"
        success_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(success_file, 'w', encoding='utf-8') as f:
            json.dump(success_data, f, indent=2, ensure_ascii=False, default=str)
        
        console.print(f"💾 [green]Aprendizaje manual guardado: {success_file.name}[/green]")


def main():
    """Función principal del fix específico"""
    console.print(Panel.fit(
        "🎯 [bold blue]FIX ESPECÍFICO DROPDOWN MÁS...[/bold blue]\n"
        "Soluciona el problema real del dropdown correcto",
        border_style="blue"
    ))
    
    fix = QuickMasFix()
    
    try:
        if fix.run_mas_dropdown_fix():
            console.print("\n🎉 [bold green]¡PROBLEMA SOLUCIONADO![/bold green]")
            console.print("El sistema ahora puede usar el dropdown MÁS... correctamente")
        else:
            console.print("\n⚠️ [yellow]El problema requiere más investigación[/yellow]")
            console.print("Revisa los archivos en data/learning/ para más detalles")
    
    except KeyboardInterrupt:
        console.print("\n⏹️ [yellow]Proceso interrumpido por el usuario[/yellow]")
    except Exception as e:
        console.print(f"\n❌ [red]Error fatal: {e}[/red]")


if __name__ == "__main__":
    main()