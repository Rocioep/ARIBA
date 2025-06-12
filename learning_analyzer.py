# learning_analyzer.py
"""
ANALIZADOR DE SESIONES DE APRENDIZAJE
Extrae selectores útiles de todas las sesiones de aprendizaje y genera selectores optimizados
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter, defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class LearningAnalyzer:
    """Analizador de sesiones de aprendizaje para extraer selectores óptimos"""
    
    def __init__(self):
        self.learning_dir = Path("data/learning")
        self.learning_data = []
        self.successful_selectors = {}
        self.failed_selectors = {}
        
    def load_all_sessions(self) -> int:
        """Cargar todas las sesiones de aprendizaje"""
        if not self.learning_dir.exists():
            console.print("❌ [red]No existe directorio de aprendizaje[/red]")
            return 0
        
        session_files = list(self.learning_dir.glob("*.json"))
        
        for file_path in session_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['file_name'] = file_path.name
                    data['file_path'] = str(file_path)
                    self.learning_data.append(data)
            except Exception as e:
                console.print(f"⚠️ Error cargando {file_path.name}: {e}")
        
        console.print(f"✅ Cargadas {len(self.learning_data)} sesiones de aprendizaje")
        return len(self.learning_data)
    
    def extract_successful_selectors(self) -> Dict:
        """Extraer selectores que funcionaron exitosamente"""
        successful = defaultdict(list)
        
        for session in self.learning_data:
            # Extraer de successful_selectors
            if 'successful_selectors' in session:
                for category, selectors in session['successful_selectors'].items():
                    if isinstance(selectors, dict):
                        for sub_category, selector_list in selectors.items():
                            if isinstance(selector_list, list):
                                successful[f"{category}_{sub_category}"].extend(selector_list)
            
            # Extraer de resultados de scraping
            if 'dropdown_result' in session and session['dropdown_result']:
                result = session['dropdown_result']
                if result.get('success') and result.get('selector_used'):
                    successful['dropdown_corporation'].append(result['selector_used'])
            
            if 'selection_result' in session and session['selection_result']:
                result = session['selection_result']
                if result.get('success') and result.get('selector_used'):
                    successful['codelco_selection'].append(result['selector_used'])
            
            # Extraer de análisis de elementos
            if 'steps' in session:
                for step in session['steps']:
                    if step.get('analysis') and step['analysis'].get('likely_clicked_element'):
                        element = step['analysis']['likely_clicked_element']
                        if element.get('element') and element['element'].get('xpath_sugerido'):
                            step_name = step.get('name', 'unknown')
                            successful[f"learned_{step_name}"].append(element['element']['xpath_sugerido'])
        
        # Limpiar duplicados
        for category, selectors in successful.items():
            successful[category] = list(set(selectors))
        
        self.successful_selectors = dict(successful)
        return self.successful_selectors
    
    def analyze_element_patterns(self) -> Dict:
        """Analizar patrones en elementos exitosos"""
        patterns = {
            'common_classes': Counter(),
            'common_attributes': Counter(),
            'xpath_patterns': Counter(),
            'element_types': Counter()
        }
        
        for session in self.learning_data:
            # Analizar elementos capturados
            if 'elements_captured' in session:
                for capture in session['elements_captured']:
                    # Analizar botones
                    for button in capture.get('all_buttons', []):
                        if button.get('visible') and button.get('enabled'):
                            # Clases comunes
                            class_attr = button.get('class', '')
                            if class_attr:
                                for cls in class_attr.split():
                                    patterns['common_classes'][cls] += 1
                            
                            # Tipos de elementos
                            patterns['element_types']['button'] += 1
                            
                            # Patrones de xpath
                            xpath = button.get('xpath', '')
                            if 'fd-' in xpath:
                                patterns['xpath_patterns']['fd-pattern'] += 1
                            if 'menu' in xpath.lower():
                                patterns['xpath_patterns']['menu-pattern'] += 1
        
        return patterns
    
    def generate_optimized_selectors(self) -> Dict:
        """Generar selectores optimizados basados en aprendizaje"""
        
        # Obtener selectores exitosos
        successful = self.extract_successful_selectors()
        patterns = self.analyze_element_patterns()
        
        # Generar selectores optimizados
        optimized = {
            'login': {
                'username': ["//input[@name='UserName']"],
                'password': ["//input[@name='Password']"],
                'submit': ["//input[@type='submit']"]
            }
        }
        
        # Dropdown de corporación optimizado
        corporation_selectors = []
        
        # Agregar selectores exitosos conocidos
        if 'dropdown_corporation' in successful:
            corporation_selectors.extend(successful['dropdown_corporation'])
        
        # Agregar selectores basados en patrones
        common_classes = patterns['common_classes']
        if 'fd-user-menu__control' in common_classes:
            corporation_selectors.append("//button[@class='fd-user-menu__control']")
            corporation_selectors.append("//button[contains(@class, 'fd-user-menu__control')]")
        
        if 'fd-user-menu' in [cls for cls in common_classes if 'user-menu' in cls]:
            corporation_selectors.append("//div[contains(@class, 'fd-user-menu')]//button")
        
        # Fallbacks basados en análisis
        corporation_selectors.extend([
            "(//button[contains(@class, 'fd-') and contains(@class, 'control')])[2]",
            "(//button[contains(@class, 'fd-')])[position()>1 and position()<4]",
            "//button[@aria-haspopup='true']",
            "//button[contains(@class, 'fd-product-menu__control')]"  # Último recurso
        ])
        
        optimized['corporation_dropdown'] = list(dict.fromkeys(corporation_selectors))  # Remover duplicados manteniendo orden
        
        # Selección de Codelco optimizada
        codelco_selectors = []
        if 'codelco_selection' in successful:
            codelco_selectors.extend(successful['codelco_selection'])
        
        codelco_selectors.extend([
            "//*[contains(text(), 'Corporación Nacional del Cobre')]",
            "//*[contains(text(), 'CODELCO')]",
            "//li[@role='option' and contains(text(), 'Corporación')]",
            "//div[contains(@class, 'fd-list__content') and contains(text(), 'Corporación')]"
        ])
        
        optimized['codelco_selection'] = list(dict.fromkeys(codelco_selectors))
        
        # Menú de exportación
        optimized['export_menu'] = [
            "//button[@title='Menú de acciones']",
            "//button[contains(@class, 'action-menu')]",
            "//button[contains(@aria-label, 'menu')]",
            "//button[text()='⋮']",
            "//button[text()='☰']",
            "(//button[contains(@class, 'menu')])[last()]"
        ]
        
        # Exportar todas las filas
        optimized['export_all_rows'] = [
            "//*[contains(text(), 'Exportar todas las filas')]",
            "//*[contains(text(), 'Export all rows')]",
            "//li[contains(text(), 'Exportar todas')]",
            "//*[@role='menuitem' and contains(text(), 'Exportar')]"
        ]
        
        return optimized
    
    def create_learning_report(self) -> Path:
        """Crear reporte detallado de aprendizaje"""
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'total_sessions': len(self.learning_data),
            'successful_selectors': self.successful_selectors,
            'optimized_selectors': self.generate_optimized_selectors(),
            'patterns_analysis': self.analyze_element_patterns(),
            'session_summary': []
        }
        
        # Resumen de sesiones
        for session in self.learning_data:
            summary = {
                'file_name': session.get('file_name'),
                'timestamp': session.get('timestamp', session.get('session_id', 'unknown')),
                'type': self._determine_session_type(session),
                'success_indicators': self._extract_success_indicators(session),
                'total_steps': session.get('total_steps', 0),
                'has_error': 'error' in session
            }
            report_data['session_summary'].append(summary)
        
        # Guardar reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path("reports") / f"learning_analysis_{timestamp}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        console.print(f"📊 Reporte de aprendizaje generado: {report_file.name}")
        return report_file
    
    def _determine_session_type(self, session: Dict) -> str:
        """Determinar tipo de sesión de aprendizaje"""
        file_name = session.get('file_name', '')
        
        if 'step_by_step' in file_name:
            return 'Paso a Paso'
        elif 'corporation_selection' in file_name:
            return 'Selección Corporación'
        elif 'elements_' in file_name:
            return 'Captura Elementos'
        elif 'learning_session' in file_name:
            return 'Sesión General'
        else:
            return 'Desconocido'
    
    def _extract_success_indicators(self, session: Dict) -> Dict:
        """Extraer indicadores de éxito de una sesión"""
        indicators = {
            'login_success': False,
            'dropdown_success': False,
            'corporation_success': False,
            'export_success': False
        }
        
        # Verificar login
        if session.get('successful_selectors', {}).get('login'):
            indicators['login_success'] = True
        
        # Verificar dropdown
        if session.get('dropdown_result', {}).get('success'):
            indicators['dropdown_success'] = True
        
        # Verificar corporación
        if session.get('selection_result', {}).get('success'):
            indicators['corporation_success'] = True
        
        # Verificar pasos completados
        if session.get('total_steps', 0) >= 4:
            indicators['export_success'] = True
        
        return indicators
    
    def display_analysis_summary(self):
        """Mostrar resumen visual del análisis"""
        
        console.print("\n📊 [bold blue]RESUMEN DE ANÁLISIS DE APRENDIZAJE[/bold blue]")
        
        # Tabla de sesiones
        sessions_table = Table(title="📁 Sesiones de Aprendizaje")
        sessions_table.add_column("Archivo", style="cyan")
        sessions_table.add_column("Tipo", style="yellow")
        sessions_table.add_column("Login", style="green")
        sessions_table.add_column("Dropdown", style="blue")
        sessions_table.add_column("Corporación", style="magenta")
        sessions_table.add_column("Pasos", style="white")
        
        for session in self.learning_data:
            indicators = self._extract_success_indicators(session)
            session_type = self._determine_session_type(session)
            
            sessions_table.add_row(
                session.get('file_name', 'unknown')[:20],
                session_type,
                "✅" if indicators['login_success'] else "❌",
                "✅" if indicators['dropdown_success'] else "❌", 
                "✅" if indicators['corporation_success'] else "❌",
                str(session.get('total_steps', 0))
            )
        
        console.print(sessions_table)
        
        # Selectores exitosos
        if self.successful_selectors:
            console.print("\n🎯 [bold green]SELECTORES EXITOSOS ENCONTRADOS[/bold green]")
            for category, selectors in self.successful_selectors.items():
                if selectors:
                    console.print(f"\n📌 {category}:")
                    for i, selector in enumerate(selectors[:3], 1):  # Mostrar top 3
                        console.print(f"  {i}. {selector}")
        
        # Patrones identificados
        patterns = self.analyze_element_patterns()
        console.print("\n🔍 [bold yellow]PATRONES IDENTIFICADOS[/bold yellow]")
        
        top_classes = patterns['common_classes'].most_common(5)
        if top_classes:
            console.print("🏷️ Clases CSS más comunes:")
            for cls, count in top_classes:
                console.print(f"  • {cls} ({count} veces)")
        
        # Recomendaciones
        optimized = self.generate_optimized_selectors()
        console.print("\n💡 [bold cyan]SELECTORES OPTIMIZADOS RECOMENDADOS[/bold cyan]")
        
        if 'corporation_dropdown' in optimized:
            console.print("🎯 Para dropdown de corporación:")
            for i, selector in enumerate(optimized['corporation_dropdown'][:3], 1):
                console.print(f"  {i}. {selector}")


def main():
    """Función principal del analizador"""
    console.print("🔍 [bold blue]ANALIZADOR DE SESIONES DE APRENDIZAJE[/bold blue]")
    console.print("Extrae selectores óptimos de todas las sesiones de aprendizaje\n")
    
    analyzer = LearningAnalyzer()
    
    # Cargar sesiones
    total_sessions = analyzer.load_all_sessions()
    
    if total_sessions == 0:
        console.print("❌ [red]No se encontraron sesiones de aprendizaje[/red]")
        console.print("💡 Ejecuta primero el modo de aprendizaje paso a paso")
        return
    
    # Analizar
    successful_selectors = analyzer.extract_successful_selectors()
    
    # Mostrar resumen
    analyzer.display_analysis_summary()
    
    # Generar reporte
    report_file = analyzer.create_learning_report()
    
    # Mostrar selectores optimizados
    optimized = analyzer.generate_optimized_selectors()
    
    console.print(f"\n📄 [bold green]REPORTE COMPLETO: {report_file.name}[/bold green]")
    
    # Crear archivo de selectores optimizados
    selectors_file = Path("config") / "optimized_selectors.json"
    with open(selectors_file, 'w', encoding='utf-8') as f:
        json.dump(optimized, f, indent=2, ensure_ascii=False)
    
    console.print(f"⚙️ [bold green]SELECTORES OPTIMIZADOS: {selectors_file.name}[/bold green]")
    
    console.print("\n🎉 [bold green]Análisis completado![/bold green]")
    console.print("💡 Usa los selectores optimizados en tu próximo scraping")


if __name__ == "__main__":
    main()