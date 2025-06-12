# src/scraper_engine_improved.py
"""
MEJORAS AL SCRAPER ENGINE basadas en aprendizaje real del usuario
"""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager

from loguru import logger

class ImprovedAribaScraperEngine:
    """Motor de scraping mejorado con selectores aprendidos del usuario"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.driver: Optional[webdriver.Firefox] = None
        self.wait: Optional[WebDriverWait] = None
        
        # SELECTORES MEJORADOS basados en aprendizaje real
        self.learned_selectors = {
            'login': {
                'username': [
                    "//input[@name='UserName']",  # ✅ CONFIRMADO funciona
                    "//input[@placeholder='Nombre de usuario']",
                    "//input[@type='text']"
                ],
                'password': [
                    "//input[@name='Password']",  # ✅ CONFIRMADO funciona
                    "//input[@placeholder='Contraseña']", 
                    "//input[@type='password']"
                ],
                'submit': [
                    "//input[@type='submit']",  # ✅ CONFIRMADO funciona
                    "//button[contains(text(), 'Inicio de sesión')]",
                    "//button[@type='submit']"
                ]
            },
            
            # SELECTORES MEJORADOS para dropdown corporación
            'corporation_dropdown': [
                # Basados en elementos encontrados en JSON del usuario
                "//button[contains(@class, 'fd-user-menu__control')]",
                "//div[contains(@class, 'fd-user-menu')]//button",
                "(//button[contains(@class, 'fd-')])[2]",  # El segundo, no el primero
                "(//button[contains(@class, 'fd-')])[3]",  # Probar el tercero también
                
                # Selectores alternativos por posición
                "(//button[@class and contains(@class, 'fd-')])[position()>1]",
                
                # Por contenido (si tiene texto visible)
                "//button[contains(text(), 'cliente') or contains(text(), 'Cliente')]",
                "//button[contains(text(), 'corporación') or contains(text(), 'Corporación')]",
                
                # Por estructura específica de Ariba
                "//div[@class='fd-user-menu']//button[@type='button']",
                "//button[@aria-haspopup='true']",  # Dropdown con popup
                "//button[@aria-expanded='false']"  # Dropdown colapsado
            ],
            
            'codelco_options': [
                "//*[contains(text(), 'Corporación Nacional del Cobre')]",
                "//*[contains(text(), 'CODELCO')]", 
                "//*[contains(text(), 'Codelco')]",
                "//li[contains(text(), 'Corporación')]",
                "//option[contains(text(), 'Corporación')]",
                
                # Más específicos basados en estructura real
                "//li[@role='option' and contains(text(), 'Corporación')]",
                "//div[@class='fd-list__content' and contains(text(), 'Corporación')]"
            ],
            
            'export_menu': [
                # Menús de exportación más específicos
                "//button[@title='Menú de acciones']",
                "//button[contains(@class, 'action-menu')]",
                "//button[contains(@aria-label, 'menu')]",
                "//*[@data-testid='menu-button']",
                "//button[text()='⋮']",
                "//button[text()='☰']",
                "(//button[contains(@class, 'menu')])[last()]"  # El último menú
            ],
            
            'export_all_rows': [
                "//*[contains(text(), 'Exportar todas las filas')]",
                "//*[contains(text(), 'Export all rows')]", 
                "//li[contains(text(), 'Exportar todas')]",
                "//a[contains(text(), 'Exportar todas')]",
                "//*[@role='menuitem' and contains(text(), 'Exportar')]"
            ]
        }
        
        self.screenshots_count = 0
        
    def robust_element_interaction_improved(self, selectors_list: List[str], action: str, 
                                          value: str = None, timeout: int = 30, 
                                          step_name: str = "") -> Dict:
        """
        Interacción robusta MEJORADA que retorna información detallada del proceso
        """
        
        logger.info(f"🎯 {step_name}")
        result = {
            'success': False,
            'selector_used': None,
            'element_info': None,
            'error': None,
            'attempts': []
        }
        
        # Screenshot ANTES
        self.take_screenshot(f"before_{step_name.lower().replace(' ', '_')}")
        
        for i, selector in enumerate(selectors_list):
            attempt = {
                'selector': selector,
                'index': i + 1,
                'success': False,
                'error': None
            }
            
            try:
                logger.debug(f"   Probando selector {i+1}/{len(selectors_list)}: {selector[:60]}...")
                
                # Esperar elemento
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                
                # Capturar información del elemento ANTES de interactuar
                element_info = {
                    'tag': element.tag_name,
                    'text': element.text[:50],
                    'class': element.get_attribute("class"),
                    'id': element.get_attribute("id"),
                    'visible': element.is_displayed(),
                    'enabled': element.is_enabled(),
                    'location': element.location,
                    'size': element.size
                }
                
                if not element.is_displayed():
                    attempt['error'] = "Elemento presente pero no visible"
                    result['attempts'].append(attempt)
                    continue
                
                # Scroll al elemento
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(1)
                
                # Ejecutar acción
                if action == "click":
                    success = self._try_multiple_click_methods_improved(element, selector)
                    if success:
                        attempt['success'] = True
                        result['success'] = True
                        result['selector_used'] = selector
                        result['element_info'] = element_info
                        
                        logger.info(f"   ✅ Click exitoso con selector {i+1}")
                        self.take_screenshot(f"after_{step_name.lower().replace(' ', '_')}_success")
                        
                        result['attempts'].append(attempt)
                        return result
                
                elif action == "write" and value:
                    element.clear()
                    time.sleep(0.5)
                    element.send_keys(value)
                    
                    if element.get_attribute("value") == value:
                        attempt['success'] = True
                        result['success'] = True
                        result['selector_used'] = selector
                        result['element_info'] = element_info
                        
                        logger.info(f"   ✅ Texto escrito exitosamente con selector {i+1}")
                        self.take_screenshot(f"after_{step_name.lower().replace(' ', '_')}_success")
                        
                        result['attempts'].append(attempt)
                        return result
                
                elif action == "find":
                    attempt['success'] = True
                    result['success'] = True
                    result['selector_used'] = selector
                    result['element_info'] = element_info
                    
                    logger.info(f"   ✅ Elemento encontrado con selector {i+1}")
                    result['attempts'].append(attempt)
                    return result
                
            except TimeoutException:
                attempt['error'] = "Timeout"
                logger.debug(f"   ⏱️ Timeout en selector {i+1}")
            except Exception as e:
                attempt['error'] = str(e)[:100]
                logger.debug(f"   ❌ Error en selector {i+1}: {str(e)[:50]}...")
            
            result['attempts'].append(attempt)
        
        # Si llegamos aquí, todos los selectores fallaron
        result['error'] = f"Todos los {len(selectors_list)} selectores fallaron"
        logger.error(f"❌ Todos los selectores fallaron para: {step_name}")
        self.take_screenshot(f"after_{step_name.lower().replace(' ', '_')}_failed")
        
        return result
    
    def _try_multiple_click_methods_improved(self, element, selector: str) -> bool:
        """Métodos de click mejorados con más opciones"""
        methods = [
            ("Click normal", lambda: element.click()),
            ("JavaScript click", lambda: self.driver.execute_script("arguments[0].click();", element)),
            ("ActionChains move+click", lambda: ActionChains(self.driver).move_to_element(element).click().perform()),
            ("ActionChains offset", lambda: ActionChains(self.driver).move_to_element_with_offset(element, 5, 5).click().perform()),
            ("Submit (si es form)", lambda: element.submit() if element.tag_name in ['input', 'button'] else None),
            ("Space key", lambda: element.send_keys(" ") if element.tag_name == 'button' else None),
            ("Enter key", lambda: element.send_keys("\n") if element.tag_name == 'button' else None)
        ]
        
        for method_name, method_func in methods:
            try:
                if method_func is None:
                    continue
                    
                # Verificar clickeabilidad
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, selector)))
                method_func()
                logger.debug(f"      ✅ {method_name} exitoso")
                return True
            except Exception as e:
                logger.debug(f"      ⚠️ {method_name} falló: {str(e)[:30]}...")
                continue
        
        return False
    
    def select_corporation_improved(self) -> Dict:
        """Selección de corporación con seguimiento detallado"""
        logger.info("🏢 Seleccionando Corporación del Cobre (Método Mejorado)...")
        
        process_log = {
            'step': 'select_corporation',
            'timestamp': datetime.now().isoformat(),
            'dropdown_result': None,
            'selection_result': None,
            'success': False
        }
        
        # 1. Abrir dropdown corporación
        dropdown_result = self.robust_element_interaction_improved(
            self.learned_selectors['corporation_dropdown'],
            "click",
            step_name="Abrir dropdown corporación (selectores mejorados)"
        )
        
        process_log['dropdown_result'] = dropdown_result
        
        if dropdown_result['success']:
            logger.info(f"✅ Dropdown abierto con: {dropdown_result['selector_used']}")
            time.sleep(3)  # Esperar que aparezca el menú
            
            # 2. Seleccionar Codelco
            selection_result = self.robust_element_interaction_improved(
                self.learned_selectors['codelco_options'],
                "click", 
                step_name="Seleccionar Corporación del Cobre"
            )
            
            process_log['selection_result'] = selection_result
            
            if selection_result['success']:
                logger.info(f"✅ Corporación seleccionada con: {selection_result['selector_used']}")
                time.sleep(8)  # Esperar refresh de página
                process_log['success'] = True
            else:
                logger.error("❌ No se pudo seleccionar Corporación del Cobre")
        else:
            logger.error("❌ No se pudo abrir dropdown de corporación")
        
        # Guardar log del proceso
        log_file = Path("data/learning") / f"corporation_selection_{int(time.time())}.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(process_log, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📝 Log del proceso guardado: {log_file.name}")
        
        return process_log
    
    def run_step_by_step_learning(self) -> Dict:
        """
        Modo de aprendizaje PASO A PASO donde el usuario ejecuta acciones
        y el sistema las captura en tiempo real
        """
        logger.info("🎓 MODO APRENDIZAJE PASO A PASO")
        
        learning_session = {
            'session_id': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'steps': [],
            'successful_selectors': {},
            'total_steps': 0
        }
        
        try:
            # Setup navegador visible
            self.config.setdefault('scraping', {})['headless'] = False
            
            if not self.setup_firefox():
                return learning_session
            
            try:
                logger.info("🚀 Iniciando sesión de aprendizaje paso a paso...")
                
                # PASO 1: Login automático (sabemos que funciona)
                logger.info("\n📋 PASO 1: Login automático")
                if self.login_to_ariba():
                    learning_session['successful_selectors']['login'] = self.learned_selectors['login']
                    learning_session['steps'].append({
                        'step': 1,
                        'name': 'login',
                        'method': 'automatic',
                        'success': True,
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.info("✅ Login automático exitoso")
                else:
                    logger.error("❌ Login automático falló")
                    return learning_session
                
                # PASO 2: Captura colaborativa del dropdown
                logger.info("\n📋 PASO 2: Dropdown de Corporación")
                logger.info("🖱️  INSTRUCCIONES:")
                logger.info("   1. Busca en la página el DROPDOWN que dice 'Todos los clientes' o similar")
                logger.info("   2. Cuando lo encuentres, NO hagas click todavía")
                logger.info("   3. Presiona ENTER aquí para que capture el estado ANTES")
                
                input("👆 Presiona ENTER cuando hayas localizado el dropdown...")
                
                # Capturar estado ANTES del click
                before_elements = self.capture_page_elements_detailed("before_dropdown_click")
                
                logger.info("📸 Estado ANTES capturado")
                logger.info("🖱️  Ahora SÍ haz CLICK en el dropdown")
                
                input("👆 Presiona ENTER DESPUÉS de hacer click en el dropdown...")
                
                # Capturar estado DESPUÉS del click
                after_elements = self.capture_page_elements_detailed("after_dropdown_click")
                
                dropdown_step = {
                    'step': 2,
                    'name': 'dropdown_corporation',
                    'method': 'manual_guided',
                    'before_elements': before_elements,
                    'after_elements': after_elements,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Analizar diferencias para identificar el elemento clickeado
                dropdown_analysis = self.analyze_element_differences(before_elements, after_elements)
                dropdown_step['analysis'] = dropdown_analysis
                
                learning_session['steps'].append(dropdown_step)
                
                # PASO 3: Selección de Corporación
                logger.info("\n📋 PASO 3: Selección de Corporación del Cobre")
                logger.info("🖱️  INSTRUCCIONES:")
                logger.info("   1. Busca en el menú desplegado 'Corporación Nacional del Cobre' o 'CODELCO'")
                logger.info("   2. Cuando lo encuentres, NO hagas click todavía")
                
                input("👆 Presiona ENTER cuando hayas localizado la opción Corporación...")
                
                # Capturar antes de seleccionar corporación
                before_corp = self.capture_page_elements_detailed("before_corporation_select")
                
                logger.info("🖱️  Ahora SÍ haz CLICK en 'Corporación Nacional del Cobre'")
                
                input("👆 Presiona ENTER DESPUÉS de seleccionar la corporación...")
                
                time.sleep(8)  # Esperar que cargue la página
                
                # Capturar después de seleccionar
                after_corp = self.capture_page_elements_detailed("after_corporation_select") 
                
                corp_step = {
                    'step': 3,
                    'name': 'select_corporation',
                    'method': 'manual_guided',
                    'before_elements': before_corp,
                    'after_elements': after_corp,
                    'timestamp': datetime.now().isoformat()
                }
                
                corp_analysis = self.analyze_element_differences(before_corp, after_corp)
                corp_step['analysis'] = corp_analysis
                
                learning_session['steps'].append(corp_step)
                
                # PASO 4: Menú de exportación
                logger.info("\n📋 PASO 4: Menú de Exportación")
                logger.info("🖱️  INSTRUCCIONES:")
                logger.info("   1. Busca el botón de MENÚ (usualmente 3 puntos ⋮ o 3 líneas ☰)")
                logger.info("   2. Puede estar cerca de una tabla o lista de licitaciones")
                
                input("👆 Presiona ENTER cuando hayas localizado el menú...")
                
                before_menu = self.capture_page_elements_detailed("before_export_menu")
                
                logger.info("🖱️  Haz CLICK en el menú de acciones")
                
                input("👆 Presiona ENTER DESPUÉS de abrir el menú...")
                
                after_menu = self.capture_page_elements_detailed("after_export_menu")
                
                menu_step = {
                    'step': 4,
                    'name': 'export_menu',
                    'method': 'manual_guided',
                    'before_elements': before_menu,
                    'after_elements': after_menu,
                    'analysis': self.analyze_element_differences(before_menu, after_menu),
                    'timestamp': datetime.now().isoformat()
                }
                
                learning_session['steps'].append(menu_step)
                
                # PASO 5: Exportar todas las filas
                logger.info("\n📋 PASO 5: Exportar Todas las Filas")
                logger.info("🖱️  Busca y haz CLICK en 'Exportar todas las filas'")
                
                input("👆 Presiona ENTER DESPUÉS de hacer click en exportar...")
                
                export_step = {
                    'step': 5,
                    'name': 'export_all_rows',
                    'method': 'manual_execution',
                    'timestamp': datetime.now().isoformat()
                }
                
                learning_session['steps'].append(export_step)
                
                learning_session['total_steps'] = len(learning_session['steps'])
                
                logger.info("🎉 Sesión de aprendizaje paso a paso completada")
                
            finally:
                # Guardar sesión completa
                session_file = Path("data/learning") / f"step_by_step_session_{learning_session['session_id']}.json"
                session_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(session_file, 'w', encoding='utf-8') as f:
                    json.dump(learning_session, f, indent=2, ensure_ascii=False, default=str)
                
                logger.info(f"💾 Sesión completa guardada: {session_file.name}")
                
                input("👆 Presiona ENTER para cerrar el navegador...")
                if self.driver:
                    self.driver.quit()
                
        except Exception as e:
            logger.error(f"❌ Error en aprendizaje paso a paso: {e}")
            learning_session['error'] = str(e)
        
        return learning_session
    
    def capture_page_elements_detailed(self, step_name: str) -> Dict:
        """Captura DETALLADA de elementos para análisis de diferencias"""
        try:
            logger.debug(f"📸 Capturando elementos detallados: {step_name}")
            
            elements_data = {
                'timestamp': datetime.now().isoformat(),
                'step_name': step_name,
                'url': self.driver.current_url,
                'page_title': self.driver.title,
                'all_buttons': [],
                'all_clickable_divs': [],
                'all_links': [],
                'page_hash': hash(self.driver.page_source)  # Para detectar cambios
            }
            
            # Capturar TODOS los botones con detalles completos
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for i, btn in enumerate(buttons):
                try:
                    button_data = {
                        'index': i,
                        'text': btn.text.strip(),
                        'class': btn.get_attribute("class"),
                        'id': btn.get_attribute("id"),
                        'type': btn.get_attribute("type"),
                        'aria_label': btn.get_attribute("aria-label"),
                        'title': btn.get_attribute("title"),
                        'visible': btn.is_displayed(),
                        'enabled': btn.is_enabled(),
                        'location': btn.location,
                        'size': btn.size,
                        'xpath': f"(//button)[{i+1}]",
                        'outer_html': btn.get_attribute("outerHTML")[:200]  # Primeros 200 chars
                    }
                    elements_data['all_buttons'].append(button_data)
                except:
                    continue
            
            # Capturar divs clickeables
            divs = self.driver.find_elements(By.TAG_NAME, "div")
            for i, div in enumerate(divs[:50]):  # Limitar para evitar exceso
                try:
                    class_attr = div.get_attribute("class") or ""
                    if any(keyword in class_attr.lower() for keyword in ['menu', 'dropdown', 'control', 'button', 'clickable']):
                        div_data = {
                            'index': i,
                            'text': div.text.strip()[:50],
                            'class': class_attr,
                            'id': div.get_attribute("id"),
                            'role': div.get_attribute("role"),
                            'visible': div.is_displayed(),
                            'clickable': div.get_attribute("onclick") is not None,
                            'location': div.location,
                            'xpath': f"(//div[contains(@class, 'menu') or contains(@class, 'dropdown')])[{len(elements_data['all_clickable_divs'])+1}]"
                        }
                        elements_data['all_clickable_divs'].append(div_data)
                except:
                    continue
            
            # Tomar screenshot
            self.take_screenshot(f"detailed_{step_name}")
            
            return elements_data
            
        except Exception as e:
            logger.error(f"❌ Error en captura detallada: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def analyze_element_differences(self, before: Dict, after: Dict) -> Dict:
        """Analizar diferencias entre estados ANTES y DESPUÉS para identificar elementos clickeados"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'page_changed': False,
            'new_elements': [],
            'disappeared_elements': [],
            'likely_clicked_element': None,
            'new_menus_detected': False
        }
        
        try:
            # Verificar si la página cambió
            before_hash = before.get('page_hash')
            after_hash = after.get('page_hash')
            analysis['page_changed'] = before_hash != after_hash
            
            # Analizar botones nuevos o que cambiaron
            before_buttons = {btn['outer_html']: btn for btn in before.get('all_buttons', [])}
            after_buttons = {btn['outer_html']: btn for btn in after.get('all_buttons', [])}
            
            # Elementos que aparecieron
            new_button_htmls = set(after_buttons.keys()) - set(before_buttons.keys())
            for html in new_button_htmls:
                analysis['new_elements'].append({
                    'type': 'button',
                    'element': after_buttons[html]
                })
            
            # Detectar nuevos menús o dropdowns
            after_divs = after.get('all_clickable_divs', [])
            before_divs = before.get('all_clickable_divs', [])
            
            if len(after_divs) > len(before_divs):
                analysis['new_menus_detected'] = True
                # Los últimos elementos son probablemente los nuevos menús
                new_menus = after_divs[len(before_divs):]
                for menu in new_menus:
                    analysis['new_elements'].append({
                        'type': 'menu',
                        'element': menu
                    })
            
            # Sugerir el elemento más probable que fue clickeado
            # (esto es heurístico, pero útil para aprendizaje)
            if analysis['page_changed'] and analysis['new_elements']:
                # El primer botón que aparece después del click probablemente era el target
                analysis['likely_clicked_element'] = analysis['new_elements'][0]
            
            logger.debug(f"📊 Análisis: página cambió: {analysis['page_changed']}, nuevos elementos: {len(analysis['new_elements'])}")
            
        except Exception as e:
            analysis['error'] = str(e)
            logger.error(f"❌ Error analizando diferencias: {e}")
        
        return analysis
    
    def take_screenshot(self, name: str, description: str = "") -> Optional[Path]:
        """Tomar screenshot para debugging"""
        try:
            self.screenshots_count += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshots_count:02d}_{name}_{timestamp}.png"
            screenshot_path = Path("data/screenshots") / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.driver.save_screenshot(str(screenshot_path))
            
            if description:
                logger.debug(f"📸 Screenshot: {filename} - {description}")
            else:
                logger.debug(f"📸 Screenshot: {filename}")
            
            return screenshot_path
            
        except Exception as e:
            logger.warning(f"⚠️ Error tomando screenshot: {e}")
            return None
    
    def setup_firefox(self) -> bool:
        """Configurar Firefox optimizado para scraping"""
        try:
            logger.info("🔧 Configurando Firefox...")
            
            options = FirefoxOptions()
            
            # Configuración según modo
            scraping_config = self.config.get('scraping', {})
            if scraping_config.get('headless', False):
                options.add_argument("--headless")
                logger.info("👻 Modo headless activado")
            
            # Configurar descargas
            downloads_path = str(Path("data/downloads").absolute())
            Path(downloads_path).mkdir(parents=True, exist_ok=True)
            
            options.set_preference("browser.download.dir", downloads_path)
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.useDownloadDir", True)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", 
                                 "application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv,application/octet-stream,text/html")
            options.set_preference("browser.download.manager.showWhenStarting", False)
            
            # Anti-detección
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            
            # Inicializar driver
            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
            
            # Configurar timeouts
            timeout = scraping_config.get('timeout', 30)
            self.driver.set_page_load_timeout(timeout * 2)
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, timeout)
            
            logger.info("✅ Firefox configurado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando Firefox: {e}")
            return False
    
    def login_to_ariba(self) -> bool:
        """Login robusto a Ariba usando selectores confirmados"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"🔐 Intento de login {attempt + 1}/{max_attempts}")
                
                # Navegar a la URL
                ariba_url = self.config['ariba_credentials']['url']
                logger.info(f"🌐 Navegando a: {ariba_url}")
                self.driver.get(ariba_url)
                
                # Esperar carga completa
                WebDriverWait(self.driver, 60).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                self.take_screenshot("login_page_loaded", "Página de login cargada")
                
                # Ingresar usuario
                username = self.config['ariba_credentials']['username']
                username_result = self.robust_element_interaction_improved(
                    self.learned_selectors['login']['username'],
                    "write",
                    username,
                    step_name="Ingresar usuario"
                )
                
                if not username_result['success']:
                    raise Exception("No se pudo ingresar usuario")
                
                time.sleep(2)
                
                # Ingresar contraseña
                password = self.config['ariba_credentials']['password']
                password_result = self.robust_element_interaction_improved(
                    self.learned_selectors['login']['password'],
                    "write",
                    password,
                    step_name="Ingresar contraseña"
                )
                
                if not password_result['success']:
                    raise Exception("No se pudo ingresar contraseña")
                
                time.sleep(2)
                
                # Click submit
                submit_result = self.robust_element_interaction_improved(
                    self.learned_selectors['login']['submit'],
                    "click",
                    step_name="Click login"
                )
                
                if not submit_result['success']:
                    raise Exception("No se pudo hacer click en login")
                
                # Esperar resultado del login
                logger.info("⏳ Esperando resultado del login...")
                time.sleep(10)
                
                # Verificar login exitoso
                current_url = self.driver.current_url
                page_source = self.driver.page_source.lower()
                
                # Indicadores de login exitoso
                login_success_indicators = [
                    "login" not in current_url.lower(),
                    "signin" not in current_url.lower(),
                    "dashboard" in current_url.lower() or "sourcing" in current_url.lower(),
                    "bienvenido" in page_source or "welcome" in page_source
                ]
                
                if any(login_success_indicators):
                    logger.info("✅ Login exitoso")
                    self.take_screenshot("login_success", "Login completado exitosamente")
                    return True
                else:
                    logger.warning(f"⚠️ Login falló en intento {attempt + 1}")
                    self.take_screenshot(f"login_failed_attempt_{attempt + 1}")
                    
            except Exception as e:
                logger.error(f"❌ Error en intento de login {attempt + 1}: {e}")
                self.take_screenshot(f"login_error_attempt_{attempt + 1}")
                time.sleep(5)
        
        logger.error("❌ Login falló después de todos los intentos")
        return False
    
    def test_connection(self) -> bool:
        """Probar conexión básica a Ariba"""
        try:
            logger.info("🧪 Probando conexión a Ariba...")
            
            if not self.setup_firefox():
                return False
            
            try:
                # Solo probar navegación y carga de página
                ariba_url = self.config['ariba_credentials']['url']
                self.driver.get(ariba_url)
                
                # Esperar carga
                WebDriverWait(self.driver, 30).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                # Verificar que sea una página de Ariba
                page_source = self.driver.page_source.lower()
                ariba_indicators = ['ariba', 'sap', 'login', 'usuario', 'contraseña']
                
                if any(indicator in page_source for indicator in ariba_indicators):
                    logger.info("✅ Conexión a Ariba exitosa")
                    return True
                else:
                    logger.warning("⚠️ Página cargada pero no parece ser Ariba")
                    return False
                    
            finally:
                self.driver.quit()
                
        except Exception as e:
            logger.error(f"❌ Error probando conexión: {e}")
            if self.driver:
                self.driver.quit()
            return False
    
    def run_complete_scraping_improved(self) -> Optional[Path]:
        """Ejecutar proceso completo de scraping con selectores mejorados"""
        logger.info("🚀 Iniciando proceso completo de scraping MEJORADO")
        
        try:
            # 1. Setup navegador
            if not self.setup_firefox():
                return None
            
            try:
                # 2. Login
                if not self.login_to_ariba():
                    logger.error("❌ Login falló")
                    return None
                
                # 3. Seleccionar corporación con método mejorado
                corp_result = self.select_corporation_improved()
                
                if not corp_result['success']:
                    logger.warning("⚠️ Selección de corporación falló, intentando continuar...")
                    # No retornamos None aquí porque puede que ya esté en la página correcta
                
                # 4. Exportar datos con método mejorado
                downloaded_file = self.export_all_rows_improved()
                
                if downloaded_file:
                    logger.info(f"✅ Scraping completado exitosamente: {downloaded_file}")
                    return downloaded_file
                else:
                    logger.error("❌ No se pudo exportar datos")
                    return None
                    
            finally:
                # Limpiar recursos
                if self.driver:
                    self.driver.quit()
                    logger.info("🔒 Navegador cerrado")
                
        except Exception as e:
            logger.error(f"❌ Error en scraping completo: {e}")
            if self.driver:
                self.driver.quit()
            return None
    
    def export_all_rows_improved(self) -> Optional[Path]:
        """Exportar todas las filas con método mejorado"""
        logger.info("📥 Iniciando exportación de todas las filas (método mejorado)...")
        
        # 1. Abrir menú de exportación
        menu_result = self.robust_element_interaction_improved(
            self.learned_selectors['export_menu'],
            "click",
            step_name="Abrir menú de exportación"
        )
        
        if not menu_result['success']:
            logger.error("❌ No se pudo abrir menú de exportación")
            return None
        
        time.sleep(3)
        
        # 2. Click en "Exportar todas las filas"
        export_result = self.robust_element_interaction_improved(
            self.learned_selectors['export_all_rows'],
            "click",
            step_name="Click Exportar todas las filas"
        )
        
        if not export_result['success']:
            logger.error("❌ No se encontró opción 'Exportar todas las filas'")
            return None
        
        # 3. Esperar descarga
        logger.info("⏳ Esperando descarga del archivo...")
        downloaded_file = self.wait_for_download()
        
        if downloaded_file:
            logger.info(f"✅ Archivo descargado: {downloaded_file.name}")
            return downloaded_file
        else:
            logger.error("❌ No se detectó descarga")
            return None
    
    def wait_for_download(self, timeout_seconds: int = 120) -> Optional[Path]:
        """Esperar a que se complete la descarga"""
        downloads_dir = Path("data/downloads")
        
        # Obtener archivos existentes antes de la descarga
        existing_files = set(downloads_dir.glob("*")) if downloads_dir.exists() else set()
        
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            time.sleep(3)
            
            if not downloads_dir.exists():
                continue
            
            # Buscar archivos nuevos
            current_files = set(downloads_dir.glob("*"))
            new_files = current_files - existing_files
            
            for file_path in new_files:
                # Verificar que el archivo no esté siendo descargado (.part, .tmp, etc.)
                if any(ext in file_path.suffix.lower() for ext in ['.part', '.tmp', '.crdownload']):
                    continue
                
                # Verificar tamaño mínimo
                if file_path.stat().st_size > 1000:  # Al menos 1KB
                    # Esperar un poco más para asegurar que la descarga terminó
                    time.sleep(2)
                    return file_path
            
            # Log progreso cada 15 segundos
            elapsed = int(time.time() - start_time)
            if elapsed % 15 == 0:
                logger.info(f"⏳ Esperando descarga... {elapsed}s")
                self.take_screenshot(f"waiting_download_{elapsed}s")
        
        logger.error("❌ Timeout esperando descarga")
        return None
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🔒 Driver cerrado")
            except:
                pass