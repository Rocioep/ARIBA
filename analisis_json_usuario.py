#!/usr/bin/env python3
"""
🔍 ANÁLISIS DE JSON USUARIO - ALFAMINE MONITOR
Análisis inteligente de datos de aprendizaje específicos del usuario

Analiza los JSON reales del usuario para:
- Identificar selectores exitosos
- Detectar problemas en el flujo
- Generar recomendaciones específicas
- Optimizar la configuración

Autor: Sistema Alfamine  
Versión: 2.0
Fecha: 2025-06-11
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path

# =====================================
# 🎯 CLASE PRINCIPAL
# =====================================

class AnalisisJsonUsuario:
    """Analizador inteligente de JSON de aprendizaje del usuario"""
    
    def __init__(self, data_dir: str = "data/learning"):
        """
        Inicializa el analizador
        
        Args:
            data_dir: Directorio con archivos JSON de aprendizaje
        """
        self.data_dir = Path(data_dir)
        self.resultados = {}
        self.recomendaciones = []
        self.problemas_detectados = []
        self.selectores_exitosos = {}
        
    def analizar_json_completo(self, archivo_json: str = None) -> Dict[str, Any]:
        """
        Análisis completo de JSON de aprendizaje
        
        Args:
            archivo_json: Archivo específico a analizar (opcional)
            
        Returns:
            Resultados completos del análisis
        """
        print("🔍 INICIANDO ANÁLISIS DE JSON USUARIO")
        print("=" * 50)
        
        # 1. Cargar datos
        datos = self._cargar_datos_json(archivo_json)
        if not datos:
            return {"error": "No se pudieron cargar datos JSON"}
            
        # 2. Análisis por categorías
        self._analizar_login_exitoso(datos)
        self._analizar_aplicacion_correcta(datos)
        self._analizar_elementos_capturados(datos)
        self._analizar_selectores_funcionales(datos)
        self._detectar_problemas_principales(datos)
        
        # 3. Generar recomendaciones específicas
        self._generar_recomendaciones_usuario()
        
        # 4. Crear plan de acción
        plan_accion = self._crear_plan_accion()
        
        # 5. Compilar resultados
        resultado_final = {
            "timestamp": datetime.now().isoformat(),
            "archivo_analizado": archivo_json or "múltiples",
            "resumen": self._generar_resumen(),
            "login_status": self.resultados.get("login", {}),
            "aplicacion_status": self.resultados.get("aplicacion", {}),
            "selectores_exitosos": self.selectores_exitosos,
            "problemas_detectados": self.problemas_detectados,
            "recomendaciones": self.recomendaciones,
            "plan_accion": plan_accion,
            "siguientes_pasos": self._definir_siguientes_pasos()
        }
        
        # 6. Mostrar resultados
        self._mostrar_resultados(resultado_final)
        
        # 7. Guardar análisis
        self._guardar_analisis(resultado_final)
        
        return resultado_final
    
    def _cargar_datos_json(self, archivo_especifico: str = None) -> Dict[str, Any]:
        """Carga datos JSON del usuario"""
        datos = {}
        
        if archivo_especifico and os.path.exists(archivo_especifico):
            # Archivo específico
            with open(archivo_especifico, 'r', encoding='utf-8') as f:
                datos[archivo_especifico] = json.load(f)
        else:
            # Buscar archivos en directorio
            archivos_encontrados = []
            
            # Buscar en directorio actual
            for archivo in os.listdir('.'):
                if archivo.endswith('.json') and 'learning' in archivo:
                    archivos_encontrados.append(archivo)
            
            # Buscar en data/learning si existe
            if self.data_dir.exists():
                for archivo in self.data_dir.glob('*.json'):
                    archivos_encontrados.append(str(archivo))
            
            # Cargar archivos encontrados
            for archivo in archivos_encontrados[:5]:  # Limitar a 5 archivos
                try:
                    with open(archivo, 'r', encoding='utf-8') as f:
                        datos[archivo] = json.load(f)
                except Exception as e:
                    print(f"⚠️  Error cargando {archivo}: {e}")
        
        print(f"📁 Archivos JSON cargados: {len(datos)}")
        return datos
    
    def _analizar_login_exitoso(self, datos: Dict[str, Any]):
        """Analiza el éxito del proceso de login"""
        login_exitoso = False
        selectores_login = {}
        
        for archivo, contenido in datos.items():
            if "successful_selectors" in contenido:
                selectores = contenido["successful_selectors"]
                if "login" in selectores:
                    login_exitoso = True
                    selectores_login = selectores["login"]
                    break
        
        self.resultados["login"] = {
            "exitoso": login_exitoso,
            "selectores": selectores_login
        }
        
        if login_exitoso:
            print("✅ LOGIN: Funcionando correctamente")
            self.selectores_exitosos.update(selectores_login)
        else:
            print("❌ LOGIN: Problemas detectados")
            self.problemas_detectados.append("Login no funcional")
    
    def _analizar_aplicacion_correcta(self, datos: Dict[str, Any]):
        """Analiza si está en la aplicación correcta de Ariba"""
        aplicacion_actual = None
        url_detectada = None
        es_correcta = False
        
        for archivo, contenido in datos.items():
            if "elements_captured" in contenido:
                for elemento in contenido["elements_captured"]:
                    if "url" in elemento:
                        url_detectada = elemento["url"]
                        
                    # Buscar texto de aplicación
                    if "buttons" in elemento:
                        for button in elemento["buttons"]:
                            texto = button.get("text", "")
                            if "Ariba" in texto:
                                aplicacion_actual = texto
                                break
        
        # Verificar si es la aplicación correcta
        if aplicacion_actual:
            if "Sourcing" in aplicacion_actual:
                es_correcta = True
                print("✅ APLICACIÓN: Ariba Sourcing (Correcto)")
            elif "Proposals" in aplicacion_actual:
                es_correcta = False
                print("❌ APLICACIÓN: Proposals & Questionnaires (Incorrecto)")
                self.problemas_detectados.append({
                    "tipo": "aplicacion_incorrecta",
                    "actual": aplicacion_actual,
                    "correcta": "Ariba Sourcing",
                    "criticidad": "ALTA"
                })
        
        self.resultados["aplicacion"] = {
            "actual": aplicacion_actual,
            "url": url_detectada,
            "es_correcta": es_correcta
        }
    
    def _analizar_elementos_capturados(self, datos: Dict[str, Any]):
        """Analiza elementos capturados en cada paso"""
        elementos_totales = 0
        pasos_capturados = []
        
        for archivo, contenido in datos.items():
            if "elements_captured" in contenido:
                for captura in contenido["elements_captured"]:
                    paso = captura.get("step_name", "desconocido")
                    pasos_capturados.append(paso)
                    
                    # Contar elementos
                    for tipo in ["buttons", "divs_clickable", "inputs", "selects", "links"]:
                        if tipo in captura:
                            elementos_totales += len(captura[tipo])
        
        self.resultados["elementos"] = {
            "total_capturados": elementos_totales,
            "pasos": pasos_capturados,
            "diversidad": len(set(pasos_capturados))
        }
        
        print(f"📊 ELEMENTOS: {elementos_totales} capturados en {len(pasos_capturados)} pasos")
    
    def _analizar_selectores_funcionales(self, datos: Dict[str, Any]):
        """Identifica selectores que funcionaron"""
        selectores_funcionales = {}
        
        for archivo, contenido in datos.items():
            if "successful_selectors" in contenido:
                selectores = contenido["successful_selectors"]
                
                # Procesar cada categoría
                for categoria, lista_selectores in selectores.items():
                    if isinstance(lista_selectores, dict):
                        for subcategoria, sel_list in lista_selectores.items():
                            if isinstance(sel_list, list) and sel_list:
                                clave = f"{categoria}_{subcategoria}"
                                selectores_funcionales[clave] = sel_list[0]  # Primer selector que funcionó
                    elif isinstance(lista_selectores, (int, str)):
                        selectores_funcionales[categoria] = lista_selectores
        
        self.selectores_exitosos.update(selectores_funcionales)
        print(f"🎯 SELECTORES: {len(selectores_funcionales)} funcionando")
    
    def _detectar_problemas_principales(self, datos: Dict[str, Any]):
        """Detecta los problemas principales basados en datos reales"""
        
        # Problema 1: Aplicación incorrecta (ya detectado)
        if not self.resultados.get("aplicacion", {}).get("es_correcta", False):
            self.problemas_detectados.append({
                "problema": "🚨 APLICACIÓN INCORRECTA",
                "descripcion": "Está en 'Proposals & Questionnaires' en lugar de 'Sourcing'",
                "impacto": "CRÍTICO - No encontrará licitaciones",
                "solucion": "Cambiar URL o configurar navegación a Sourcing"
            })
        
        # Problema 2: Dropdown limitado
        dropdown_funcional = False
        for archivo, contenido in datos.items():
            if "dropdown_strategy" in contenido.get("successful_selectors", {}):
                dropdown_funcional = True
                break
        
        if dropdown_funcional:
            self.problemas_detectados.append({
                "problema": "⚠️  DROPDOWN LIMITADO", 
                "descripcion": "Solo se abre el dropdown, no navega dentro",
                "impacto": "MEDIO - Sistema incompleto",
                "solucion": "Implementar navegación completa en dropdown"
            })
        
        # Problema 3: Falta navegación post-dropdown
        elementos_post_dropdown = 0
        for archivo, contenido in datos.items():
            if "elements_captured" in contenido:
                for captura in contenido["elements_captured"]:
                    if captura.get("step_name") == "dropdown_opened":
                        for tipo in ["buttons", "divs_clickable", "links"]:
                            elementos_post_dropdown += len(captura.get(tipo, []))
        
        if elementos_post_dropdown < 5:
            self.problemas_detectados.append({
                "problema": "📋 NAVEGACIÓN INCOMPLETA",
                "descripcion": f"Solo {elementos_post_dropdown} elementos después de abrir dropdown",
                "impacto": "MEDIO - No navega a licitaciones",
                "solucion": "Capturar más elementos de navegación"
            })
    
    def _generar_recomendaciones_usuario(self):
        """Genera recomendaciones específicas basadas en el análisis"""
        
        # Recomendación 1: Corregir aplicación
        if not self.resultados.get("aplicacion", {}).get("es_correcta", False):
            self.recomendaciones.append({
                "prioridad": "🔥 CRÍTICA",
                "accion": "Cambiar a aplicación Sourcing",
                "implementacion": [
                    "Modificar URL base en config.json",
                    "Cambiar de '/Sourcing.aw/' a '/Buyer/'",
                    "O navegar manualmente a Sourcing después del login"
                ],
                "codigo_sugerido": """
# En config.json:
"ariba_base_url": "https://service.ariba.com/Buyer.aw/109555009/aw?awh=r"

# O en scraper_engine_improved.py:
def navegar_a_sourcing(self):
    sourcing_url = "https://service.ariba.com/Buyer.aw/109555009/aw?awh=r"
    self.driver.get(sourcing_url)
                """
            })
        
        # Recomendación 2: Mejorar selectores dropdown
        self.recomendaciones.append({
            "prioridad": "🎯 ALTA",
            "accion": "Optimizar selectores de dropdown",
            "implementacion": [
                "Usar selectores más específicos basados en tu JSON",
                "Implementar navegación completa en menús",
                "Agregar timeouts adaptativos"
            ],
            "codigo_sugerido": f"""
# Selectores optimizados basados en tu JSON:
DROPDOWN_SELECTORS = [
    "//div[@class='fd-user-menu__control']",      # Menú usuario (correcto)
    "//div[contains(@class, 'fd-user-menu')]//button",
    "//div[@class='fd-popover__control']"         # Basado en tu JSON
]
            """
        })
        
        # Recomendación 3: Implementar sistema completo
        self.recomendaciones.append({
            "prioridad": "📈 MEDIA",
            "accion": "Implementar sistema de monitoreo completo",
            "implementacion": [
                "Usar scraper_engine_improved.py",
                "Configurar automatización 24/7", 
                "Implementar sistema de alertas"
            ],
            "beneficios": [
                "Monitoreo automático continuo",
                "Detección proactiva de licitaciones",
                "Notificaciones en tiempo real"
            ]
        })
    
    def _crear_plan_accion(self) -> List[Dict[str, Any]]:
        """Crea plan de acción específico para el usuario"""
        return [
            {
                "paso": 1,
                "titulo": "🚨 CORRECCIÓN INMEDIATA",
                "tiempo": "5 minutos",
                "acciones": [
                    "Cambiar URL para ir a Ariba Sourcing",
                    "Probar selector de dropdown corregido", 
                    "Verificar navegación post-login"
                ],
                "archivos_modificar": ["config.json", "scraper_engine.py"]
            },
            {
                "paso": 2, 
                "titulo": "🔧 OPTIMIZACIÓN",
                "tiempo": "30 minutos",
                "acciones": [
                    "Implementar selectores mejorados",
                    "Agregar captura de elementos completa",
                    "Configurar timeouts adaptativos"
                ],
                "archivos_modificar": ["scraper_engine_improved.py"]
            },
            {
                "paso": 3,
                "titulo": "🚀 AUTOMATIZACIÓN",
                "tiempo": "1 hora", 
                "acciones": [
                    "Configurar scheduler_automation.py",
                    "Implementar sistema de monitoreo 24/7",
                    "Configurar alertas y notificaciones"
                ],
                "archivos_nuevos": ["scheduler_automation.py", "system_monitor.py"]
            }
        ]
    
    def _generar_resumen(self) -> Dict[str, Any]:
        """Genera resumen ejecutivo del análisis"""
        return {
            "estado_general": "⚠️  PARCIALMENTE FUNCIONAL" if self.problemas_detectados else "✅ FUNCIONAL",
            "login": "✅ Funcionando" if self.resultados.get("login", {}).get("exitoso") else "❌ Con problemas",
            "aplicacion": "✅ Correcta" if self.resultados.get("aplicacion", {}).get("es_correcta") else "❌ Incorrecta",
            "problemas_criticos": len([p for p in self.problemas_detectados if "CRÍTICO" in str(p)]),
            "problemas_medios": len([p for p in self.problemas_detectados if "MEDIO" in str(p)]),
            "selectores_funcionales": len(self.selectores_exitosos),
            "tiempo_implementacion": "2 horas" if len(self.problemas_detectados) > 2 else "30 minutos"
        }
    
    def _definir_siguientes_pasos(self) -> List[str]:
        """Define los siguientes pasos inmediatos"""
        pasos = []
        
        if not self.resultados.get("aplicacion", {}).get("es_correcta", False):
            pasos.append("🔥 URGENTE: Cambiar a aplicación Ariba Sourcing")
        
        if len(self.selectores_exitosos) < 3:
            pasos.append("🎯 Optimizar selectores con datos del JSON analizado")
        
        pasos.extend([
            "📋 Implementar captura completa de elementos",
            "🤖 Configurar automatización 24/7",
            "📧 Configurar sistema de alertas",
            "🧪 Realizar pruebas de monitoreo completo"
        ])
        
        return pasos[:5]  # Limitar a 5 pasos
    
    def _mostrar_resultados(self, resultados: Dict[str, Any]):
        """Muestra resultados del análisis en consola"""
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DEL ANÁLISIS")
        print("=" * 60)
        
        # Resumen
        resumen = resultados["resumen"]
        print(f"\n🎯 ESTADO GENERAL: {resumen['estado_general']}")
        print(f"   • Login: {resumen['login']}")
        print(f"   • Aplicación: {resumen['aplicacion']}")
        print(f"   • Problemas críticos: {resumen['problemas_criticos']}")
        print(f"   • Selectores funcionales: {resumen['selectores_funcionales']}")
        
        # Problemas detectados
        if self.problemas_detectados:
            print(f"\n🚨 PROBLEMAS DETECTADOS ({len(self.problemas_detectados)}):")
            for i, problema in enumerate(self.problemas_detectados[:3], 1):
                if isinstance(problema, dict):
                    print(f"   {i}. {problema.get('problema', 'Sin título')}")
                    print(f"      {problema.get('descripcion', 'Sin descripción')}")
                else:
                    print(f"   {i}. {problema}")
        
        # Recomendaciones
        if self.recomendaciones:
            print(f"\n💡 RECOMENDACIONES ({len(self.recomendaciones)}):")
            for i, rec in enumerate(self.recomendaciones[:3], 1):
                print(f"   {i}. {rec['prioridad']} - {rec['accion']}")
        
        # Siguientes pasos
        print(f"\n🚀 SIGUIENTES PASOS:")
        for i, paso in enumerate(resultados["siguientes_pasos"][:3], 1):
            print(f"   {i}. {paso}")
        
        print("\n" + "=" * 60)
    
    def _guardar_analisis(self, resultados: Dict[str, Any]):
        """Guarda análisis en archivo JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_salida = f"analisis_usuario_{timestamp}.json"
        
        try:
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Análisis guardado: {archivo_salida}")
            
        except Exception as e:
            print(f"⚠️  Error guardando análisis: {e}")

# =====================================
# 🔧 FUNCIONES DE UTILIDAD
# =====================================

def analizar_json_rapido(archivo: str = None) -> Dict[str, Any]:
    """Análisis rápido de JSON específico"""
    analizador = AnalisisJsonUsuario()
    return analizador.analizar_json_completo(archivo)

def mostrar_selectores_exitosos(archivo: str = None):
    """Muestra solo los selectores que funcionaron"""
    analizador = AnalisisJsonUsuario()
    datos = analizador._cargar_datos_json(archivo)
    
    print("🎯 SELECTORES EXITOSOS IDENTIFICADOS:")
    print("-" * 40)
    
    for archivo_name, contenido in datos.items():
        if "successful_selectors" in contenido:
            selectores = contenido["successful_selectors"]
            print(f"\n📁 {archivo_name}:")
            
            for categoria, valores in selectores.items():
                if isinstance(valores, dict):
                    for sub, lista in valores.items():
                        if isinstance(lista, list) and lista:
                            print(f"   • {categoria}_{sub}: {lista[0]}")
                else:
                    print(f"   • {categoria}: {valores}")

# =====================================
# 🚀 EJECUCIÓN PRINCIPAL
# =====================================

if __name__ == "__main__":
    print("🔍 ANÁLISIS DE JSON USUARIO - ALFAMINE MONITOR")
    print("=" * 50)
    
    # Verificar argumentos
    archivo_especifico = None
    if len(sys.argv) > 1:
        archivo_especifico = sys.argv[1]
        if not os.path.exists(archivo_especifico):
            print(f"❌ Archivo no encontrado: {archivo_especifico}")
            sys.exit(1)
    
    # Ejecutar análisis
    try:
        analizador = AnalisisJsonUsuario()
        resultados = analizador.analizar_json_completo(archivo_especifico)
        
        # Mostrar resumen final
        print(f"\n✅ Análisis completado")
        print(f"📊 {len(resultados.get('problemas_detectados', []))} problemas detectados")
        print(f"💡 {len(resultados.get('recomendaciones', []))} recomendaciones generadas")
        print(f"🎯 {len(resultados.get('selectores_exitosos', {}))} selectores funcionales")
        
    except Exception as e:
        print(f"❌ Error ejecutando análisis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)")