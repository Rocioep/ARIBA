# src/scraper_engine.py
"""
ALFAMINE SCRAPER ENGINE v1.0
Motor de scraping robusto con múltiples estrategias para elementos difíciles
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

class AribaScraperEngine:
    """Motor de scraping robusto para Ariba con múltiples estrategias"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.driver: Optional[webdriver.Firefox] = None
        self.wait: Optional[WebDriverWait] = None
        
        # Estrategias para elementos problemáticos
        self.dropdown_strategies = [
            self._strategy_known_selectors,
            self._strategy_intelligent_search,
            self._strategy_brute_force,
            self._strategy_javascript_injection
        ]
        
        # Contadores y estado
        self.screenshots_count = 0
        self.retry_count = 0
        self.max_retries = self.config.get('scraping', {}).get('max_retries', 3)
        
        # Selectores conocidos (basados en experiencia anterior)
        self.known_selectors = {
            'login': {
                'username': [
                    "//input[@name='UserName']",  # ✅ Sabemos que funciona
                    "//input[@placeholder='Nombre de usuario']",
                    "//input[@type='text']"
                ],
                'password': [
                    "//input[@name='Password']",  # ✅ Sabemos que funciona
                    "//input[@placeholder='Contraseña']",
                    "//input[@type='password']"
                ],
                'submit': [
                    "//input[@type='submit']",  # ✅ Sabemos que funciona
                    "//button[contains(text(), 'Inicio de sesión')]",
                    "//button[@type='submit']"
                ]
            },
            'dropdown_cliente': [
                # Selectores específicos de Ariba
                "//div[contains(@class, 'fd-product-menu')]//button",
                "//button[contains(@class, 'fd-product-menu__control')]",
                "//div[@class='fd-product-menu']//button[@class='fd-product-menu__control']",
                
                # Selectores por contenido
                "//button[contains(text(), 'Todos los clientes')]",
                "//button[contains(text(), 'cliente')]",
                "//button[contains(text(), 'Cliente')]",
                
                # Selectores genéricos de dropdown
                "//button[contains(@class, 'dropdown')]",
                "//div[contains(@class, 'dropdown')]//button",
                "//select[contains(@name, 'customer')]",
                
                # Selectores por posición (último recurso)
                "(//button)[1]",
                "(//button)[2]",
                "(//button)[3]"
            ],
            'codelco_options': [
                "//*[contains(text(), 'Corporación Nacional del Cobre')]",
                "//*[contains(text(), 'CODELCO')]",
                "//*[contains(text(), 'Codelco')]",
                "//*[contains(text(), 'Corporación del Cobre')]",
                "//li[contains(text(), 'CODELCO')]",
                "//option[contains(text(), 'CODELCO')]"
            ],
            'export_menu': [
                "//button[contains(@class, 'menu')]",
                "//button[contains(@title, 'menu')]",
                "//*[contains(@class, 'export')]",
                "//button[text()='⋮']",
                "//button[text()='☰']",
                "//*[contains(@class, 'action-menu')]"
            ],
            'export_all_rows': [
                "//*[contains(text(), 'Exportar todas las filas')]",
                "//*[contains(text(), 'Export all rows')]",
                "//*[contains(text(), 'todas las filas')]",
                "//li[contains(text(), 'Exportar todas')]"
            ]
        }
    
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
            
            # Configuraciones de estabilidad
            options.set_preference("browser.cache.disk.enable", False)
            options.set_preference("browser.cache.memory.enable", False)
            options.set_preference("browser.cache.offline.enable", False)
            
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
    
    def robust_element_interaction(self, selectors_list: List[str], action: str, 
                                 value: str = None, timeout: int = 30, 
                                 step_name: str = "") -> bool:
        """Interacción robusta con elementos usando múltiples selectores"""
        
        logger.info(f"🎯 {step_name}")
        
        # Screenshot ANTES
        self.take_screenshot(f"before_{step_name.lower().replace(' ', '_')}")
        
        for i, selector in enumerate(selectors_list):
            try:
                logger.debug(f"   Probando selector {i+1}/{len(selectors_list)}: {selector[:60]}...")
                
                # Esperar elemento
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                
                # Verificar visibilidad
                if not element.is_displayed():
                    logger.debug(f"   ⚠️ Elemento presente pero no visible")
                    continue
                
                # Scroll al elemento
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(1)
                
                # Ejecutar acción
                if action == "click":
                    success = self._try_multiple_click_methods(element, selector)
                    if success:
                        logger.info(f"   ✅ Click exitoso con selector {i+1}")
                        self.take_screenshot(f"after_{step_name.lower().replace(' ', '_')}_success")
                        return True
                
                elif action == "write" and value:
                    element.clear()
                    time.sleep(0.5)
                    element.send_keys(value)
                    
                    # Verificar que se escribió correctamente
                    if element.get_attribute("value") == value:
                        logger.info(f"   ✅ Texto escrito exitosamente con selector {i+1}")
                        self.take_screenshot(f"after_{step_name.lower().replace(' ', '_')}_success")
                        return True
                
                elif action == "find":
                    logger.info(f"   ✅ Elemento encontrado con selector {i+1}")
                    return True
                
            except TimeoutException:
                logger.debug(f"   ⏱️ Timeout en selector {i+1}")
                continue
            except Exception as e:
                logger.debug(f"   ❌ Error en selector {i+1}: {str(e)[:50]}...")
                continue
        
        # Si llegamos aquí, todos los selectores fallaron
        logger.error(f"❌ Todos los selectores fallaron para: {step_name}")
        self.take_screenshot(f"after_{step_name.lower().replace(' ', '_')}_failed")
        return False
    
    def _try_multiple_click_methods(self, element, selector: str) -> bool:
        """Intentar múltiples métodos de click"""
        methods = [
            ("Click normal", lambda: element.click()),
            ("Click JavaScript", lambda: self.driver.execute_script("arguments[0].click();", element)),
            ("ActionChains", lambda: ActionChains(self.driver).move_to_element(element).click().perform()),
            ("ActionChains con offset", lambda: ActionChains(self.driver).move_to_element_with_offset(element, 5, 5).click().perform())
        ]
        
        for method_name, method_func in methods:
            try:
                # Asegurar que el elemento sea clickeable
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, selector)))
                method_func()
                logger.debug(f"      ✅ {method_name} exitoso")
                return True
            except Exception as e:
                logger.debug(f"      ⚠️ {method_name} falló: {str(e)[:30]}...")
                continue
        
        return False
    
    def login_to_ariba(self) -> bool:
        """Login robusto a Ariba"""
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
                if not self.robust_element_interaction(
                    self.known_selectors['login']['username'],
                    "write",
                    username,
                    step_name="Ingresar usuario"
                ):
                    raise Exception("No se pudo ingresar usuario")
                
                time.sleep(2)
                
                # Ingresar contraseña
                password = self.config['ariba_credentials']['password']
                if not self.robust_element_interaction(
                    self.known_selectors['login']['password'],
                    "write",
                    password,
                    step_name="Ingresar contraseña"
                ):
                    raise Exception("No se pudo ingresar contraseña")
                
                time.sleep(2)
                
                # Click submit
                if not self.robust_element_interaction(
                    self.known_selectors['login']['submit'],
                    "click",
                    step_name="Click login"
                ):
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
    
    def _strategy_known_selectors(self) -> bool:
        """Estrategia 1: Usar selectores conocidos del dropdown cliente"""
        logger.info("🎯 Estrategia 1: Selectores conocidos")
        
        return self.robust_element_interaction(
            self.known_selectors['dropdown_cliente'],
            "click",
            step_name="Abrir dropdown cliente (selectores conocidos)"
        )
    
    def _strategy_intelligent_search(self) -> bool:
        """Estrategia 2: Búsqueda inteligente de elementos"""
        logger.info("🎯 Estrategia 2: Búsqueda inteligente")
        
        try:
            # Buscar todos los botones visibles
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            
            candidate_buttons = []
            
            for button in buttons:
                try:
                    if not button.is_displayed():
                        continue
                    
                    # Analizar atributos del botón
                    class_attr = button.get_attribute("class") or ""
                    text_content = button.text.strip().lower()
                    id_attr = button.get_attribute("id") or ""
                    
                    # Criterios de identificación de dropdown cliente
                    score = 0
                    reasons = []
                    
                    # Indicadores positivos
                    if "menu" in class_attr.lower():
                        score += 3
                        reasons.append("clase contiene 'menu'")
                    
                    if "dropdown" in class_attr.lower():
                        score += 3
                        reasons.append("clase contiene 'dropdown'")
                    
                    if "control" in class_attr.lower():
                        score += 2
                        reasons.append("clase contiene 'control'")
                    
                    if "cliente" in text_content or "client" in text_content:
                        score += 4
                        reasons.append("texto relacionado con cliente")
                    
                    if "todos" in text_content:
                        score += 2
                        reasons.append("texto contiene 'todos'")
                    
                    # Verificar si tiene arrow/chevron (indicador de dropdown)
                    button_html = button.get_attribute("outerHTML")
                    if any(indicator in button_html.lower() for indicator in ["arrow", "chevron", "▼", "⌄"]):
                        score += 2
                        reasons.append("tiene indicador de dropdown")
                    
                    if score >= 3:  # Umbral mínimo
                        candidate_buttons.append({
                            'element': button,
                            'score': score,
                            'reasons': reasons,
                            'text': text_content[:30],
                            'class': class_attr[:50]
                        })
                
                except Exception as e:
                    continue
            
            # Ordenar candidatos por score
            candidate_buttons.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"🔍 {len(candidate_buttons)} candidatos encontrados")
            
            # Intentar click en los mejores candidatos
            for i, candidate in enumerate(candidate_buttons[:3]):  # Top 3
                try:
                    logger.info(f"   Probando candidato {i+1}: '{candidate['text']}' (score: {candidate['score']})")
                    logger.debug(f"     Razones: {', '.join(candidate['reasons'])}")
                    
                    # Scroll y click
                    element = candidate['element']
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(1)
                    
                    if self._try_multiple_click_methods(element, f"candidato_{i+1}"):
                        logger.info(f"   ✅ Dropdown abierto con candidato {i+1}")
                        time.sleep(3)  # Esperar que aparezca el menú
                        
                        # Verificar si se abrió un menú
                        menus = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'menu') or contains(@class, 'dropdown')]")
                        visible_menus = [m for m in menus if m.is_displayed()]
                        
                        if visible_menus:
                            logger.info(f"   ✅ Menú visible detectado")
                            return True
                
                except Exception as e:
                    logger.debug(f"   ❌ Error con candidato {i+1}: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda inteligente: {e}")
            return False
    
    def _strategy_brute_force(self) -> bool:
        """Estrategia 3: Fuerza bruta controlada"""
        logger.info("🎯 Estrategia 3: Fuerza bruta controlada")
        
        try:
            # Obtener estado inicial
            initial_url = self.driver.current_url
            initial_page_source_length = len(self.driver.page_source)
            
            # Obtener elementos clickeables
            clickeable_elements = []
            
            for tag in ["button", "div", "span", "a"]:
                elements = self.driver.find_elements(By.TAG_NAME, tag)
                for element in elements:
                    try:
                        if element.is_displayed() and element.is_enabled():
                            clickeable_elements.append(element)
                    except:
                        continue
            
            logger.info(f"🔍 {len(clickeable_elements)} elementos clickeables encontrados")
            
            # Limitar para evitar loops infinitos
            max_elements = min(30, len(clickeable_elements))
            
            for i, element in enumerate(clickeable_elements[:max_elements]):
                try:
                    logger.debug(f"   Probando elemento {i+1}/{max_elements}")
                    
                    # Intentar click
                    try:
                        element.click()
                    except:
                        try:
                            self.driver.execute_script("arguments[0].click();", element)
                        except:
                            continue
                    
                    time.sleep(2)
                    
                    # Verificar cambios
                    current_url = self.driver.current_url
                    current_page_length = len(self.driver.page_source)
                    
                    # Buscar menús que mencionen Codelco
                    codelco_menus = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Codelco') or contains(text(), 'Corporación')]")
                    visible_codelco_menus = [m for m in codelco_menus if m.is_displayed()]
                    
                    if visible_codelco_menus:
                        logger.info(f"   ✅ Menú con Codelco encontrado con elemento {i+1}")
                        return True
                    
                    # Si la página cambió significativamente, puede que hayamos abierto algo
                    if abs(current_page_length - initial_page_source_length) > 1000:
                        # Verificar si hay nuevos menús visibles
                        new_menus = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'menu') or contains(@class, 'dropdown')]")
                        visible_new_menus = [m for m in new_menus if m.is_displayed()]
                        
                        if visible_new_menus:
                            logger.info(f"   ✅ Nuevo menú detectado con elemento {i+1}")
                            return True
                
                except Exception as e:
                    continue
            
            logger.warning("⚠️ Fuerza bruta no encontró dropdown")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error en fuerza bruta: {e}")
            return False
    
    def _strategy_javascript_injection(self) -> bool:
        """Estrategia 4: Inyección de JavaScript"""
        logger.info("🎯 Estrategia 4: JavaScript injection")
        
        try:
            # Script para buscar y activar dropdowns
            js_script = """
            // Buscar elementos que parezcan dropdowns de cliente
            var elementos = document.querySelectorAll('*');
            var candidatos = [];
            
            for (var i = 0; i < elementos.length; i++) {
                var el = elementos[i];
                var clase = el.className || '';
                var texto = el.textContent || '';
                var id = el.id || '';
                
                // Criterios de identificación
                var score = 0;
                
                if (clase.toLowerCase().includes('menu')) score += 3;
                if (clase.toLowerCase().includes('dropdown')) score += 3;
                if (clase.toLowerCase().includes('control')) score += 2;
                if (texto.toLowerCase().includes('cliente')) score += 4;
                if (texto.toLowerCase().includes('client')) score += 4;
                if (texto.toLowerCase().includes('todos')) score += 2;
                
                if (score >= 3) {
                    candidatos.push({element: el, score: score, text: texto.substring(0, 30)});
                }
            }
            
            // Ordenar por score
            candidatos.sort(function(a, b) { return b.score - a.score; });
            
            // Intentar click en los mejores candidatos
            for (var j = 0; j < Math.min(5, candidatos.length); j++) {
                try {
                    var candidato = candidatos[j];
                    candidato.element.scrollIntoView({block: 'center'});
                    
                    // Simular diferentes tipos de eventos
                    var eventos = ['click', 'mousedown', 'mouseup'];
                    for (var k = 0; k < eventos.length; k++) {
                        var evento = new MouseEvent(eventos[k], {
                            view: window,
                            bubbles: true,
                            cancelable: true
                        });
                        candidato.element.dispatchEvent(evento);
                    }
                    
                    // Esperar un poco
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    
                    // Verificar si apareció menú con Codelco
                    var codelcoElements = document.querySelectorAll('*');
                    for (var l = 0; l < codelcoElements.length; l++) {
                        var texto = codelcoElements[l].textContent || '';
                        if ((texto.includes('Codelco') || texto.includes('Corporación')) && 
                            codelcoElements[l].offsetParent !== null) {
                            return {success: true, candidato: j, text: candidato.text};
                        }
                    }
                    
                } catch(e) {
                    continue;
                }
            }
            
            return {success: false, candidatos: candidatos.length};
            """
            
            # Ejecutar script
            result = self.driver.execute_script(js_script)
            
            if result and result.get('success'):
                logger.info(f"   ✅ JavaScript encontró dropdown: {result.get('text', 'N/A')}")
                time.sleep(3)  # Esperar que se complete la acción
                return True
            else:
                logger.warning(f"   ⚠️ JavaScript no encontró dropdown (candidatos: {result.get('candidatos', 0)})")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error en JavaScript injection: {e}")
            return False
    
    def select_cliente_codelco(self) -> bool:
        """Seleccionar Corporación del Cobre del dropdown abierto"""
        logger.info("🏢 Seleccionando Corporación del Cobre...")
        
        # Intentar con selectores conocidos
        if self.robust_element_interaction(
            self.known_selectors['codelco_options'],
            "click",
            step_name="Seleccionar Codelco"
        ):
            logger.info("✅ Codelco seleccionado con selectores conocidos")
            time.sleep(8)  # Esperar refresh
            return True
        
        # Fallback: buscar con JavaScript
        try:
            logger.info("🔍 Buscando Codelco con JavaScript...")
            
            js_codelco = """
            var elementos = document.querySelectorAll('*');
            for (var i = 0; i < elementos.length; i++) {
                var texto = elementos[i].textContent || '';
                if ((texto.includes('Codelco') || texto.includes('Corporación Nacional del Cobre') || 
                     texto.includes('Corporación del Cobre')) && elementos[i].offsetParent !== null) {
                    elementos[i].scrollIntoView({block: 'center'});
                    elementos[i].click();
                    return {success: true, text: texto.substring(0, 50)};
                }
            }
            return {success: false};
            """
            
            result = self.driver.execute_script(js_codelco)
            
            if result and result.get('success'):
                logger.info(f"✅ Codelco seleccionado con JavaScript: {result.get('text')}")
                time.sleep(8)
                return True
            
        except Exception as e:
            logger.error(f"❌ Error JavaScript Codelco: {e}")
        
        logger.error("❌ No se pudo seleccionar Codelco")
        return False
    
    def select_cliente_autonomous(self) -> bool:
        """Seleccionar cliente usando múltiples estrategias autónomas"""
        logger.info("🏢 Seleccionando cliente Corporación del Cobre (autónomo)...")
        
        # Probar cada estrategia para abrir dropdown
        for i, strategy in enumerate(self.dropdown_strategies, 1):
            try:
                logger.info(f"🎯 Probando estrategia {i}: {strategy.__name__}")
                
                if strategy():
                    # Si se abrió el dropdown, buscar Codelco
                    time.sleep(3)
                    self.take_screenshot(f"dropdown_opened_strategy_{i}")
                    
                    if self.select_cliente_codelco():
                        logger.info(f"✅ Cliente seleccionado con estrategia {i}")
                        return True
                    else:
                        logger.warning(f"⚠️ Dropdown abierto con estrategia {i} pero no se pudo seleccionar Codelco")
                
            except Exception as e:
                logger.error(f"❌ Estrategia {i} falló: {e}")
                continue
        
        logger.error("❌ Todas las estrategias de selección de cliente fallaron")
        return False
    
    def export_all_rows(self) -> Optional[Path]:
        """Exportar todas las filas"""
        logger.info("📥 Iniciando exportación de todas las filas...")
        
        # 1. Abrir menú de exportación
        if not self.robust_element_interaction(
            self.known_selectors['export_menu'],
            "click",
            step_name="Abrir menú de exportación"
        ):
            logger.error("❌ No se pudo abrir menú de exportación")
            return None
        
        time.sleep(3)
        
        # 2. Click en "Exportar todas las filas"
        if not self.robust_element_interaction(
            self.known_selectors['export_all_rows'],
            "click",
            step_name="Click Exportar todas las filas"
        ):
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
    
    def run_complete_scraping(self) -> Optional[Path]:
        """Ejecutar proceso completo de scraping"""
        logger.info("🚀 Iniciando proceso completo de scraping")
        
        try:
            # 1. Setup navegador
            if not self.setup_firefox():
                return None
            
            try:
                # 2. Login
                if not self.login_to_ariba():
                    logger.error("❌ Login falló")
                    return None
                
                # 3. Seleccionar cliente (Corporación del Cobre)
                if not self.select_cliente_autonomous():
                    logger.warning("⚠️ Selección de cliente falló, continuando...")
                    # No retornamos None aquí porque puede que ya esté en la página correcta
                
                # 4. Exportar datos
                downloaded_file = self.export_all_rows()
                
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
    
    def run_manual_assisted_scraping(self) -> Optional[Path]:
        """Scraping con asistencia manual para pasos críticos"""
        logger.info("🤝 Iniciando scraping con asistencia manual")
        
        try:
            # 1. Setup navegador (visible)
            config_backup = self.config.get('scraping', {}).copy()
            self.config.setdefault('scraping', {})['headless'] = False  # Forzar modo visible
            
            if not self.setup_firefox():
                return None
            
            try:
                # 2. Login automático
                if not self.login_to_ariba():
                    logger.error("❌ Login automático falló")
                    return None
                
                # 3. Asistencia manual para cliente
                logger.info("🖱️ ASISTENCIA MANUAL REQUERIDA:")
                logger.info("   1. Busca el DROPDOWN que dice 'Todos los clientes'")
                logger.info("   2. Haz CLICK en la FLECHA del dropdown")
                logger.info("   3. Selecciona 'Corporación Nacional del Cobre'")
                logger.info("   4. Espera a que se actualice la página")
                
                input("👆 Presiona ENTER cuando hayas completado la selección de cliente...")
                
                # 4. Intentar exportación automática
                logger.info("🤖 Continuando con exportación automática...")
                time.sleep(3)
                
                downloaded_file = self.export_all_rows()
                
                if not downloaded_file:
                    # Fallback manual para exportación
                    logger.info("🖱️ ASISTENCIA MANUAL PARA EXPORTACIÓN:")
                    logger.info("   1. Busca el botón de MENÚ (3 puntos ⋮ o 3 líneas ☰)")
                    logger.info("   2. Haz CLICK en el menú")
                    logger.info("   3. Selecciona 'Exportar todas las filas'")
                    
                    input("👆 Presiona ENTER cuando hayas iniciado la exportación...")
                    
                    # Esperar descarga manual
                    downloaded_file = self.wait_for_download(180)  # 3 minutos
                
                if downloaded_file:
                    logger.info(f"✅ Scraping asistido completado: {downloaded_file}")
                    return downloaded_file
                else:
                    logger.error("❌ No se detectó descarga")
                    return None
                    
            finally:
                # Restaurar configuración
                if config_backup:
                    self.config['scraping'] = config_backup
                
                # Preguntar antes de cerrar
                input("👆 Presiona ENTER para cerrar el navegador...")
                if self.driver:
                    self.driver.quit()
                
        except Exception as e:
            logger.error(f"❌ Error en scraping asistido: {e}")
            if self.driver:
                input("👆 Presiona ENTER para cerrar el navegador...")
                self.driver.quit()
            return None
    
    def capture_page_elements_for_learning(self, step_name: str) -> Dict:
        """Capturar elementos de página para aprendizaje de selectores"""
        try:
            logger.info(f"🎓 Capturando elementos para aprendizaje: {step_name}")
            
            elements_data = {
                'timestamp': datetime.now().isoformat(),
                'step_name': step_name,
                'url': self.driver.current_url,
                'buttons': [],
                'divs_clickable': [],
                'inputs': [],
                'selects': [],
                'links': []
            }
            
            # Capturar botones
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for i, btn in enumerate(buttons[:20]):  # Limitar para evitar datos excesivos
                try:
                    elements_data['buttons'].append({
                        'index': i,
                        'text': btn.text.strip()[:50],
                        'class': btn.get_attribute("class"),
                        'id': btn.get_attribute("id"),
                        'visible': btn.is_displayed(),
                        'enabled': btn.is_enabled(),
                        'xpath': f"(//button)[{i+1}]"
                    })
                except:
                    continue
            
            # Capturar divs clickeables
            divs = self.driver.find_elements(By.TAG_NAME, "div")
            for i, div in enumerate(divs[:30]):
                try:
                    class_attr = div.get_attribute("class") or ""
                    if any(keyword in class_attr.lower() for keyword in ['menu', 'dropdown', 'control', 'button']):
                        elements_data['divs_clickable'].append({
                            'index': i,
                            'text': div.text.strip()[:30],
                            'class': class_attr,
                            'id': div.get_attribute("id"),
                            'visible': div.is_displayed()
                        })
                except:
                    continue
            
            # Guardar datos de aprendizaje
            learning_file = Path("data/learning") / f"elements_{step_name}_{int(time.time())}.json"
            learning_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(learning_file, 'w', encoding='utf-8') as f:
                json.dump(elements_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Datos de aprendizaje guardados: {learning_file.name}")
            
            return elements_data
            
        except Exception as e:
            logger.error(f"❌ Error capturando elementos: {e}")
            return {}
    
    def run_learning_mode(self) -> Dict:
        """Ejecutar modo de aprendizaje para mejorar selectores"""
        logger.info("🎓 Iniciando modo de aprendizaje")
        
        learning_results = {
            'session_id': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'successful_selectors': {},
            'failed_steps': [],
            'elements_captured': []
        }
        
        try:
            # Setup navegador visible
            self.config.setdefault('scraping', {})['headless'] = False
            
            if not self.setup_firefox():
                return learning_results
            
            try:
                # 1. Login (sabemos que funciona)
                if self.login_to_ariba():
                    learning_results['successful_selectors']['login'] = self.known_selectors['login']
                    
                    # 2. Capturar elementos después del login
                    elements_after_login = self.capture_page_elements_for_learning("after_login")
                    learning_results['elements_captured'].append(elements_after_login)
                    
                    # 3. Intentar encontrar dropdown cliente
                    logger.info("🎯 Buscando dropdown cliente...")
                    dropdown_found = False
                    
                    for i, strategy in enumerate(self.dropdown_strategies, 1):
                        logger.info(f"📝 Probando estrategia {i} para aprendizaje...")
                        
                        if strategy():
                            dropdown_found = True
                            learning_results['successful_selectors']['dropdown_strategy'] = i
                            
                            # Capturar elementos con dropdown abierto
                            elements_dropdown_open = self.capture_page_elements_for_learning("dropdown_opened")
                            learning_results['elements_captured'].append(elements_dropdown_open)
                            
                            break
                    
                    if not dropdown_found:
                        learning_results['failed_steps'].append("dropdown_cliente")
                        
                        # Modo manual para aprendizaje
                        logger.info("🖱️ MODO APRENDIZAJE MANUAL:")
                        logger.info("   Haz click MANUALMENTE en el dropdown cliente")
                        
                        input("👆 Presiona ENTER después del click manual...")
                        
                        # Capturar elementos después del click manual
                        elements_manual = self.capture_page_elements_for_learning("after_manual_click")
                        learning_results['elements_captured'].append(elements_manual)
                
                else:
                    learning_results['failed_steps'].append("login")
                
                # Guardar resultados de aprendizaje
                learning_file = Path("data/learning") / f"learning_session_{learning_results['session_id']}.json"
                learning_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(learning_file, 'w', encoding='utf-8') as f:
                    json.dump(learning_results, f, indent=2, ensure_ascii=False, default=str)
                
                logger.info(f"🎓 Sesión de aprendizaje completada: {learning_file.name}")
                
            finally:
                input("👆 Presiona ENTER para cerrar navegador...")
                if self.driver:
                    self.driver.quit()
                
        except Exception as e:
            logger.error(f"❌ Error en modo aprendizaje: {e}")
            learning_results['error'] = str(e)
        
        return learning_results
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🔒 Driver cerrado")
            except:
                pass