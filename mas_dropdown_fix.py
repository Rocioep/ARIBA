# mas_dropdown_fix.py
"""
FIX ESPECÍFICO para el dropdown "MÁS..." donde está Corporación Nacional del Cobre
Basado en la imagen 2 que muestra el dropdown correcto
"""

import time
import json
from pathlib import Path
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger

class MasDropdownFix:
    """Fix específico para el dropdown MÁS... y flujo completo"""
    
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        
        # SELECTORES ESPECÍFICOS para dropdown "MÁS..."
        self.mas_dropdown_selectors = [
            # Por texto específico "MÁS..." o "MAS"
            "//button[contains(text(), 'MÁS')]",
            "//button[contains(text(), 'MAS')]", 
            "//button[contains(text(), 'Más')]",
            "//button[contains(text(), 'más')]",
            "//*[contains(text(), 'MÁS')]//following-sibling::*[contains(@class, 'arrow')]",
            "//*[contains(text(), 'MÁS')]//parent::button",
            
            # Por estructura HTML que muestra dropdown con "ANTOFAGASTA MINERALS"
            "//button[contains(text(), 'ANTOFAGASTA MINERALS')]//following-sibling::button",
            "//div[contains(text(), 'ANTOFAGASTA MINERALS')]//following-sibling::button",
            "//span[contains(text(), 'ANTOFAGASTA MINERALS')]//following-sibling::button",
            
            # Por posición relativa a "ANTOFAGASTA MINERALS"  
            "//button[contains(text(), 'ANTOFAGASTA MINERALS')]//parent::div//button[position()>1]",
            "//div[contains(text(), 'ANTOFAGASTA MINERALS')]//parent::div//button[last()]",
            
            # Por clases típicas de dropdown con flecha
            "//button[contains(@class, 'dropdown') and contains(@aria-label, 'más')]",
            "//button[contains(@class, 'menu') and contains(text(), 'MÁS')]",
            "//button[@aria-haspopup='true' and contains(text(), 'MÁS')]",
            
            # Por estructura específica de SAP Ariba
            "//div[contains(@class, 'fd-user-menu')]//button[position()=2]",
            "//div[contains(@class, 'fd-user-menu')]//button[contains(@class, 'fd-button--menu')]",
            
            # Selectores genéricos por posición (última opción)
            "(//button[contains(@class, 'fd-') and @aria-haspopup='true'])[last()]",
            "(//button[@aria-expanded='false'])[last()]"
        ]
        
        # SELECTORES para opciones de Corporación del Cobre en el dropdown MÁS
        self.codelco_option_selectors = [
            # Texto exacto de la imagen
            "//*[contains(text(), 'Corporación Nacional del Cobre (Ambiente Productivo)')]",
            "//*[contains(text(), 'Corporación Nacional del Cobre')]",
            
            # En elementos de lista del dropdown
            "//li[contains(text(), 'Corporación Nacional del Cobre')]",
            "//div[@role='option' and contains(text(), 'Corporación Nacional del Cobre')]",
            "//a[contains(text(), 'Corporación Nacional del Cobre')]",
            
            # Por posición en el dropdown MÁS (segunda opción basada en imagen)
            "//ul[contains(@class, 'dropdown-menu')]//li[2]",
            "//div[contains(@class, 'dropdown-menu')]//div[2]",
            "(//li[@role='option'])[2]",
            "(//div[@role='option'])[2]",
            
            # Combinando texto parcial
            "//*[contains(text(), 'Corporación') and contains(text(), 'Cobre') and contains(text(), 'Ambiente')]",
            "//*[contains(text(), 'Nacional del Cobre')]"
        ]
        
        # SELECTORES para estado "abiertas" (siguiente paso)
        self.estado_abiertas_selectors = [
            "//select[contains(@name, 'estado')]//option[contains(text(), 'abiertas')]",
            "//select[contains(@name, 'status')]//option[contains(text(), 'open')]",
            "//button[contains(text(), 'Estado:')]",
            "//div[contains(text(), 'Estado:')]//following-sibling::select",
            "//*[contains(text(), 'Estado:')]//following-sibling::*//option[contains(text(), 'abiertas')]",
            "//select//option[contains(text(), 'Abiertas')]",
            "//select//option[contains(text(), 'ABIERTAS')]"
        ]
        
        # SELECTORES para "exportar todas las filas"
        self.export_selectors = [
            "//button[contains(text(), 'Exportar todas las filas')]",
            "//*[contains(text(), 'Exportar todas las filas')]",
            "//li[contains(text(), 'Exportar todas las filas')]",
            "//a[contains(text(), 'Exportar todas las filas')]",
            "//button[contains(@title, 'Exportar todas')]",
            "//*[contains(text(), 'Export all rows')]",
            "//button[contains(@class, 'export')]",
            "//button[contains(@aria-label, 'Exportar todas')]"
        ]
    
    def debug_current_page(self, step_name):
        """Debug completo de la página actual"""
        try:
            logger.info(f"🔍 DEBUG {step_name}")
            
            debug_info = {
                'timestamp': datetime.now().isoformat(),
                'step': step_name,
                'url': self.driver.current_url,
                'page_title': self.driver.title,
                'visible_buttons': [],
                'visible_text': [],
                'dropdowns_found': []
            }
            
            # 1. Buscar todos los botones visibles
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for i, btn in enumerate(buttons):
                try:
                    if btn.is_displayed():
                        text = btn.text.strip()
                        debug_info['visible_buttons'].append({
                            'index': i,
                            'text': text,
                            'class': btn.get_attribute('class'),
                            'aria_haspopup': btn.get_attribute('aria-haspopup'),
                            'aria_expanded': btn.get_attribute('aria-expanded')
                        })
                        
                        # Log botones que contengan "MÁS" o sean dropdown
                        if any(keyword in text.upper() for keyword in ['MÁS', 'MAS', 'MORE']) or btn.get_attribute('aria-haspopup'):
                            logger.info(f"   🎯 BOTÓN CANDIDATO: '{text}' | Class: {btn.get_attribute('class')} | HasPopup: {btn.get_attribute('aria-haspopup')}")
                except:
                    continue
            
            # 2. Buscar texto específico relacionado con empresas
            page_text = self.driver.page_source
            companies = ['ANTOFAGASTA MINERALS', 'Corporación Nacional del Cobre', 'Sierra Gorda SCM']
            
            for company in companies:
                if company in page_text:
                    logger.info(f"   ✅ EMPRESA ENCONTRADA: {company}")
                    debug_info['visible_text'].append(company)
                else:
                    logger.info(f"   ❌ EMPRESA NO ENCONTRADA: {company}")
            
            # 3. Screenshot para análisis visual
            screenshot_path = f"data/screenshots/debug_{step_name}_{int(time.time())}.png"
            Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
            self.driver.save_screenshot(screenshot_path)
            debug_info['screenshot'] = screenshot_path
            
            # 4. Guardar debug
            debug_file = Path("data/learning") / f"debug_{step_name}_{int(time.time())}.json"
            debug_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(debug_file, 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"📊 Debug guardado: {debug_file.name}")
            logger.info(f"📊 Botones visibles: {len(debug_info['visible_buttons'])}")
            
            return debug_info
            
        except Exception as e:
            logger.error(f"❌ Error en debug: {e}")
            return {}
    
    def find_and_click_mas_dropdown(self):
        """Buscar y hacer click en el dropdown MÁS..."""
        logger.info("🎯 Buscando dropdown 'MÁS...'")
        
        # Debug estado actual
        self.debug_current_page("before_mas_dropdown")
        
        for i, selector in enumerate(self.mas_dropdown_selectors, 1):
            try:
                logger.info(f"🔍 Probando selector MÁS {i}/{len(self.mas_dropdown_selectors)}: {selector[:60]}...")
                
                elements = self.driver.find_elements(By.XPATH, selector)
                logger.info(f"   📋 Encontrados: {len(elements)} elementos")
                
                for j, element in enumerate(elements):
                    try:
                        if element.is_displayed() and element.is_enabled():
                            text = element.text.strip()
                            logger.info(f"   📍 Elemento {j+1}: '{text}' | Tag: {element.tag_name}")
                            
                            # Verificar que realmente sea el dropdown MÁS
                            if self.is_mas_dropdown_candidate(element, text):
                                logger.info(f"   ✅ CANDIDATO VÁLIDO: '{text}'")
                                
                                # Scroll y click
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                time.sleep(1)
                                
                                # Intentar click
                                success = self.try_click_element(element, f"MÁS dropdown {i}-{j}")
                                if success:
                                    logger.info(f"   🎉 ¡Dropdown MÁS abierto!")
                                    time.sleep(3)  # Esperar que aparezca el menú
                                    
                                    # Verificar que se abrió
                                    if self.verify_mas_dropdown_opened():
                                        logger.info(f"   ✅ Verificación exitosa: dropdown MÁS abierto")
                                        self.debug_current_page("after_mas_dropdown_opened")
                                        return True
                                    else:
                                        logger.warning(f"   ⚠️ Click ejecutado pero dropdown no se abrió")
                        else:
                            logger.debug(f"   ❌ Elemento {j+1}: No clickeable")
                    except Exception as e:
                        logger.debug(f"   ❌ Error elemento {j+1}: {str(e)[:30]}...")
                        continue
                        
            except Exception as e:
                logger.debug(f"❌ Selector {i} falló: {str(e)[:50]}...")
                continue
        
        logger.error("❌ No se pudo encontrar dropdown MÁS")
        return False
    
    def is_mas_dropdown_candidate(self, element, text):
        """Verificar si un elemento es candidato válido para dropdown MÁS"""
        # Criterios para identificar el dropdown MÁS
        criteria_met = 0
        
        # 1. Contiene texto MÁS
        if any(keyword in text.upper() for keyword in ['MÁS', 'MAS', 'MORE']):
            criteria_met += 3
        
        # 2. Es un botón con aria-haspopup
        if element.tag_name == 'button' and element.get_attribute('aria-haspopup'):
            criteria_met += 2
        
        # 3. Tiene clases relacionadas con dropdown
        class_attr = element.get_attribute('class') or ''
        if any(keyword in class_attr.lower() for keyword in ['dropdown', 'menu', 'select']):
            criteria_met += 2
        
        # 4. Está cerca de texto "ANTOFAGASTA MINERALS"
        try:
            page_source = self.driver.page_source
            if 'ANTOFAGASTA MINERALS' in page_source:
                criteria_met += 1
        except:
            pass
        
        return criteria_met >= 2
    
    def verify_mas_dropdown_opened(self):
        """Verificar que el dropdown MÁS se abrió correctamente"""
        try:
            # Buscar opciones específicas que aparecen en el dropdown MÁS
            expected_options = [
                'Corporación Nacional del Cobre',
                'Sierra Gorda SCM',
                'Antofagasta Minerals'
            ]
            
            page_source = self.driver.page_source
            found_options = sum(1 for option in expected_options if option in page_source)
            
            # Si encontramos al menos 2 de las 3 opciones, el dropdown está abierto
            success = found_options >= 2
            
            if success:
                logger.info(f"✅ Dropdown MÁS verificado: {found_options}/3 opciones encontradas")
            else:
                logger.warning(f"⚠️ Solo {found_options}/3 opciones encontradas")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error verificando dropdown MÁS: {e}")
            return False
    
    def select_corporacion_codelco(self):
        """Seleccionar Corporación Nacional del Cobre del dropdown MÁS"""
        logger.info("🏢 Seleccionando Corporación Nacional del Cobre...")
        
        for i, selector in enumerate(self.codelco_option_selectors, 1):
            try:
                logger.info(f"🔍 Probando selector Codelco {i}: {selector[:60]}...")
                
                elements = self.driver.find_elements(By.XPATH, selector)
                logger.info(f"   📋 Encontrados: {len(elements)} elementos")
                
                for j, element in enumerate(elements):
                    try:
                        if element.is_displayed():
                            text = element.text.strip()
                            logger.info(f"   📍 Elemento {j+1}: '{text}'")
                            
                            # Verificar que realmente sea Codelco
                            if self.is_codelco_option(text):
                                logger.info(f"   ✅ OPCIÓN CODELCO VÁLIDA: '{text}'")
                                
                                # Click
                                success = self.try_click_element(element, f"Codelco {i}-{j}")
                                if success:
                                    logger.info(f"   🎉 ¡Corporación del Cobre seleccionada!")
                                    time.sleep(5)  # Esperar que se procese
                                    
                                    # Verificar éxito
                                    if self.verify_codelco_selected():
                                        logger.info(f"   ✅ Selección verificada exitosamente")
                                        return True
                                    else:
                                        logger.warning(f"   ⚠️ Click ejecutado pero no se verificó selección")
                    except Exception as e:
                        logger.debug(f"   ❌ Error elemento {j+1}: {str(e)[:30]}...")
                        continue
                        
            except Exception as e:
                logger.debug(f"❌ Selector {i} falló: {str(e)[:50]}...")
                continue
        
        logger.error("❌ No se pudo seleccionar Corporación del Cobre")
        return False
    
    def is_codelco_option(self, text):
        """Verificar si el texto corresponde a opción de Codelco"""
        text_lower = text.lower()
        return (
            ('corporación' in text_lower and 'cobre' in text_lower) or
            'codelco' in text_lower or
            ('nacional del cobre' in text_lower)
        )
    
    def verify_codelco_selected(self):
        """Verificar que Corporación del Cobre fue seleccionada"""
        try:
            time.sleep(3)
            
            # Indicadores de éxito
            page_source = self.driver.page_source.lower()
            indicators = [
                'corporación nacional del cobre' in page_source,
                'codelco' in page_source,
                'ambiente productivo' in page_source
            ]
            
            return any(indicators)
            
        except Exception as e:
            logger.error(f"❌ Error verificando selección Codelco: {e}")
            return False
    
    def select_estado_abiertas(self):
        """Seleccionar estado 'abiertas'"""
        logger.info("📋 Seleccionando estado 'abiertas'...")
        
        self.debug_current_page("before_estado_abiertas")
        
        for i, selector in enumerate(self.estado_abiertas_selectors, 1):
            try:
                logger.info(f"🔍 Probando selector estado {i}: {selector[:60]}...")
                
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    try:
                        if element.is_displayed():
                            success = self.try_click_element(element, f"Estado {i}")
                            if success:
                                logger.info(f"   ✅ Estado 'abiertas' seleccionado")
                                time.sleep(3)
                                return True
                    except:
                        continue
                        
            except Exception as e:
                logger.debug(f"❌ Selector estado {i} falló: {e}")
                continue
        
        logger.warning("⚠️ No se pudo seleccionar estado 'abiertas' automáticamente")
        return False
    
    def export_all_rows(self):
        """Exportar todas las filas"""
        logger.info("📥 Exportando todas las filas...")
        
        self.debug_current_page("before_export")
        
        # Primero buscar menú de exportación
        export_menu_selectors = [
            "//button[contains(@class, 'menu')]",
            "//button[contains(@title, 'menu')]",
            "//button[text()='⋮']",
            "//button[text()='☰']"
        ]
        
        # Intentar abrir menú de exportación
        menu_opened = False
        for selector in export_menu_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed():
                        self.try_click_element(element, "Export menu")
                        time.sleep(2)
                        menu_opened = True
                        break
                if menu_opened:
                    break
            except:
                continue
        
        # Buscar opción "Exportar todas las filas"
        for i, selector in enumerate(self.export_selectors, 1):
            try:
                logger.info(f"🔍 Probando selector export {i}: {selector[:60]}...")
                
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    try:
                        if element.is_displayed():
                            text = element.text.strip()
                            if 'exportar' in text.lower() or 'export' in text.lower():
                                success = self.try_click_element(element, f"Export {i}")
                                if success:
                                    logger.info(f"   ✅ Exportación iniciada")
                                    return True
                    except:
                        continue
                        
            except Exception as e:
                logger.debug(f"❌ Selector export {i} falló: {e}")
                continue
        
        logger.warning("⚠️ No se pudo exportar automáticamente")
        return False
    
    def try_click_element(self, element, description):
        """Intentar múltiples métodos de click"""
        methods = [
            ("Click normal", lambda: element.click()),
            ("JavaScript click", lambda: self.driver.execute_script("arguments[0].click();", element)),
            ("ActionChains", lambda: self.driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", element))
        ]
        
        for method_name, method_func in methods:
            try:
                method_func()
                logger.debug(f"      ✅ {method_name} exitoso para {description}")
                return True
            except Exception as e:
                logger.debug(f"      ❌ {method_name} falló: {str(e)[:30]}...")
                continue
        
        return False
    
    def run_complete_flow(self, include_export=True):
        """Ejecutar flujo completo"""
        logger.info("🚀 INICIANDO FLUJO COMPLETO - Dropdown MÁS...")
        
        steps_completed = []
        
        # Paso 1: Abrir dropdown MÁS
        if self.find_and_click_mas_dropdown():
            steps_completed.append("mas_dropdown_opened")
            logger.info("✅ Paso 1 completado: Dropdown MÁS abierto")
            
            # Paso 2: Seleccionar Corporación del Cobre
            if self.select_corporacion_codelco():
                steps_completed.append("codelco_selected")
                logger.info("✅ Paso 2 completado: Corporación del Cobre seleccionada")
                
                if include_export:
                    # Paso 3: Estado abiertas (opcional)
                    if self.select_estado_abiertas():
                        steps_completed.append("estado_abiertas")
                        logger.info("✅ Paso 3 completado: Estado 'abiertas' seleccionado")
                    
                    # Paso 4: Exportar (opcional)
                    if self.export_all_rows():
                        steps_completed.append("export_completed")
                        logger.info("✅ Paso 4 completado: Exportación iniciada")
            else:
                logger.error("❌ Falló Paso 2: No se pudo seleccionar Corporación del Cobre")
        else:
            logger.error("❌ Falló Paso 1: No se pudo abrir dropdown MÁS")
        
        # Guardar resultados
        results = {
            'timestamp': datetime.now().isoformat(),
            'flow_type': 'complete' if include_export else 'partial',
            'steps_completed': steps_completed,
            'success': len(steps_completed) >= 2,  # Al menos dropdown + codelco
            'total_steps': len(steps_completed)
        }
        
        results_file = Path("data/learning") / f"mas_flow_results_{int(time.time())}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📊 Resultados guardados: {results_file.name}")
        logger.info(f"🎯 Flujo completado: {len(steps_completed)} pasos exitosos")
        
        return results


# Función para integrar en el scraper principal
def integrate_mas_dropdown_fix(scraper_instance):
    """Integrar el fix del dropdown MÁS en el scraper principal"""
    
    mas_fix = MasDropdownFix(scraper_instance.driver, scraper_instance.wait)
    
    def select_corporation_mas_fixed(include_full_flow=False):
        """Método mejorado que usa el dropdown MÁS correcto"""
        logger.info("🏢 SELECCIÓN CORPORACIÓN - DROPDOWN MÁS (VERSIÓN CORREGIDA)")
        
        return mas_fix.run_complete_flow(include_export=include_full_flow)
    
    # Reemplazar método en el scraper
    scraper_instance.select_corporation_mas = select_corporation_mas_fixed
    
    return scraper_instance