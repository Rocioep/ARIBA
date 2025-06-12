# sistema_iterativo_completo.py - VERSION ULTRA RAPIDA CORREGIDA
"""
⚡ SISTEMA ULTRA RÁPIDO CON LOGIN EN LINKS ESPECÍFICOS
- LOGIN EN CADA LICITACIÓN: No login inicial, sino en cada link específico
- DESCARGA: 10s máximo (vs 60s antes)
- DETECCIÓN: Cada 0.5s (vs 2s antes)  
- FALLBACK: Continúa sin archivo si no descarga
- TARGET: 5-8s por licitación = 30-45 min total
"""

import sys
import json
import time
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlparse
import re
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor
import threading

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.firefox.options import Options

# Rich para UI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, track
from rich.prompt import Confirm, Prompt

# Logging
from loguru import logger

console = Console()

class SistemaUltraRapido:
    """Sistema optimizado para máxima velocidad CON LOGIN EN LICITACIONES ESPECÍFICAS"""
    
    def __init__(self, config=None):
        self.config = config or self.load_default_config()
        self.driver = None
        self.wait = None
        
        # ⚡ CONFIGURACIÓN ULTRA RÁPIDA
        self.ultra_fast_timeout = 8       # Timeout general ultra reducido
        self.download_timeout = 10        # ✅ Máximo 10s para descarga (vs 60s)
        self.download_check_interval = 0.5 # ✅ Check cada 0.5s (vs 2s)
        self.page_delay = 0.5            # ✅ Delay mínimo
        self.max_retries = 1             # ✅ Solo 1 retry (vs 3)
        self.skip_threshold = 3          # ✅ Skip después de 3 errores consecutivos
        
        # 📊 CONTADORES DE VELOCIDAD
        self.consecutive_errors = 0
        self.skipped_downloads = 0
        self.successful_downloads = 0
        self.time_savings = 0
        self.login_success = False
        
        # 🔄 SISTEMA INCREMENTAL
        self.checkpoint_file = Path("data/checkpoint.json")
        self.processed_history = Path("data/processed_history.json")
        self.load_checkpoint()
        self.load_processed_history()
        
        # 🔑 CREDENCIALES (cargar inmediatamente)
        self.ariba_username = None
        self.ariba_password = None
        self.credentials_asked = False
        self.load_credentials_immediately()
        
        # Sistema de scoring (simplificado para velocidad)
        self.scoring_system = self.load_scoring_system()
        
        self.resultados_procesamiento = {
            'session_id': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'modo': 'ULTRA_RAPIDO',
            'login_en_licitaciones': True,  # ✅ NUEVO: Login en cada licitación específica
            'reautenticaciones': 0,
            'licitaciones_procesadas': [],
            'licitaciones_saltadas': [],
            'licitaciones_sin_descarga': [],
            'oportunidades_oro': [],
            'oportunidades_plata': [],
            'oportunidades_bronce': [],
            'descartadas': [],
            'errores': [],
            'archivos_eliminados': 0,
            'archivos_mantenidos': 0,
            'descargas_exitosas': 0,
            'descargas_fallidas': 0,
            'tiempo_ahorrado': 0
        }
        
        # Contadores
        self.total_licitaciones = 0
        self.procesadas = 0
        self.saltadas = 0
        self.exitosas = 0
        self.start_time = None
        
        logger.info("⚡ Sistema Ultra Rápido iniciado - Login en licitaciones específicas")
    
    def load_credentials_immediately(self):
        """Cargar credenciales INMEDIATAMENTE al inicializar"""
        try:
            ariba_creds = self.config.get('ariba_credentials', {})
            self.ariba_username = ariba_creds.get('username', 'sales@alfamine.cl')
            self.ariba_password = ariba_creds.get('password', 'VI.2024al..al.')
            self.credentials_asked = True
            
            console.print("🔑 [green]Credenciales precargadas desde config[/green]")
            console.print(f"   👤 Usuario: {self.ariba_username}")
            console.print(f"   🔒 Password: {'*' * len(self.ariba_password)}")
            
        except Exception as e:
            console.print(f"⚠️ [yellow]Error cargando credenciales: {e}[/yellow]")
            self.ariba_username = "sales@alfamine.cl"
            self.ariba_password = "VI.2024al..al."
            self.credentials_asked = True
    
    def load_scoring_system(self):
        """Sistema de scoring optimizado para velocidad"""
        try:
            search_criteria = self.config.get('search_criteria', {})
            
            # 🏆 KEYWORDS PLANAS (más rápido que categorías complejas)
            all_keywords = {}
            
            # Productos ALFAMINE
            lineas = search_criteria.get('lineas_producto', {})
            for categoria, data in lineas.items():
                if isinstance(data, dict) and 'keywords' in data:
                    score = data.get('score', 25)
                    for kw in data['keywords']:
                        all_keywords[kw.upper()] = score
                elif isinstance(data, list):
                    for kw in data:
                        all_keywords[kw.upper()] = 25
            
            # Pernería
            perneria = search_criteria.get('perneria', {})
            perneria_score = perneria.get('score', 15)
            for kw in perneria.get('keywords', []):
                all_keywords[kw.upper()] = perneria_score
            
            # Marcas
            marcas = search_criteria.get('marcas', [])
            if isinstance(marcas, list):
                for marca in marcas:
                    all_keywords[marca.upper()] = 12
            elif isinstance(marcas, dict):
                for tier, data in marcas.items():
                    score = data.get('score', 12)
                    for marca in data.get('brands', []):
                        all_keywords[marca.upper()] = score
            
            # Thresholds
            scoring_config = self.config.get('scoring', {})
            thresholds = scoring_config.get('classification_thresholds', {
                'ORO': 100, 'PLATA': 60, 'BRONCE': 30, 'DESCARTADO': 0
            })
            
            return {
                'keywords': all_keywords,  # Dict plano: keyword -> score
                'thresholds': thresholds
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Error cargando scoring: {e}")
            return {
                'keywords': {
                    'ZAPATA': 30, 'CADENA': 30, 'RODILLOS': 30, 'SPROCKET': 30, 'GEARBOX': 30,
                    'RUEDA TENSORA': 30, 'REDUCTOR': 30, 'MANDO FINAL': 30, 'MF': 30,
                    'PERNO': 15, 'TUERCA': 15, 'BOLT': 15, 'NUT': 15, 'SCREW': 15, 'CHAVETA': 15,
                    'CAT': 15, 'CATERPILLAR': 15, 'KOMATSU': 15, 'KRESS': 15
                },
                'thresholds': {'ORO': 100, 'PLATA': 60, 'BRONCE': 30, 'DESCARTADO': 0}
            }
    
    def load_checkpoint(self):
        """Cargar checkpoint"""
        try:
            if self.checkpoint_file.exists():
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    self.checkpoint = json.load(f)
                console.print(f"📂 [green]Checkpoint cargado: {self.checkpoint.get('last_processed', 0)} procesadas[/green]")
            else:
                self.checkpoint = {'last_processed': 0, 'completed': False}
        except Exception as e:
            self.checkpoint = {'last_processed': 0, 'completed': False}
    
    def save_checkpoint(self, current_index):
        """Guardar checkpoint"""
        try:
            self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
            self.checkpoint.update({
                'last_processed': current_index,
                'timestamp': datetime.now().isoformat(),
                'completed': False
            })
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(self.checkpoint, f, indent=2)
        except Exception as e:
            logger.warning(f"⚠️ Error guardando checkpoint: {e}")
    
    def load_processed_history(self):
        """Cargar historial"""
        try:
            if self.processed_history.exists():
                with open(self.processed_history, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            else:
                self.history = {}
        except Exception as e:
            self.history = {}
    
    def save_processed_history(self):
        """Guardar historial"""
        try:
            self.processed_history.parent.mkdir(parents=True, exist_ok=True)
            with open(self.processed_history, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, default=str)
        except Exception as e:
            pass

    def detect_login_page(self):
        """Detección de login mejorada"""
        try:
            # 1. Check por URL (más rápido)
            current_url = self.driver.current_url.lower()
            if any(keyword in current_url for keyword in ['login', 'signin', 'auth', 'logon']):
                logger.info("🔍 Login detectado por URL")
                return True
            
            # 2. Check por elementos clave
            login_indicators = [
                "//input[@type='password']",
                "//input[@name='Password']",
                "//input[@name='UserName']", 
                "//*[contains(text(), 'Inicio de sesión')]",
                "//*[contains(text(), 'Login')]"
            ]
            
            for indicator in login_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        logger.info("🔍 Login detectado por elemento")
                        return True
                except:
                    continue
            
            return False
                
        except Exception as e:
            logger.warning(f"⚠️ Error detectando login: {e}")
            return False

    def handle_login(self):
        """Manejar login con múltiples intentos"""
        try:
            console.print("🔑 [yellow]Iniciando proceso de login...[/yellow]")
            
            if not self.ariba_username or not self.ariba_password:
                console.print("❌ [red]No hay credenciales disponibles[/red]")
                return False
            
            max_login_attempts = 3
            
            for attempt in range(max_login_attempts):
                try:
                    console.print(f"🔑 [yellow]Intento de login {attempt + 1}/{max_login_attempts}[/yellow]")
                    
                    # Buscar campos con múltiples selectores
                    username_field = self.find_login_element([
                        "//input[@name='UserName']",
                        "//input[contains(@class, 'w-login-form-input-user')]",
                        "//input[@type='text' and contains(@placeholder, 'usuario')]",
                        "//input[@type='text']"
                    ])
                    
                    password_field = self.find_login_element([
                        "//input[@name='Password']",
                        "//input[contains(@class, 'w-psw')]",
                        "//input[@type='password']"
                    ])
                    
                    submit_button = self.find_login_element([
                        "//input[@type='submit']",
                        "//button[@type='submit']",
                        "//input[contains(@class, 'w-login-page-form-btn')]",
                        "//button[contains(text(), 'Inicio de sesión')]",
                        "//button[contains(text(), 'Login')]"
                    ])
                    
                    if not all([username_field, password_field, submit_button]):
                        console.print(f"❌ [red]Intento {attempt + 1}: No se encontraron todos los campos[/red]")
                        if attempt < max_login_attempts - 1:
                            time.sleep(2)
                            continue
                        else:
                            return False
                    
                    # Llenar formulario
                    console.print("📝 [cyan]Llenando formulario de login...[/cyan]")
                    
                    username_field.clear()
                    username_field.send_keys(self.ariba_username)
                    time.sleep(0.5)
                    
                    password_field.clear()
                    password_field.send_keys(self.ariba_password)
                    time.sleep(0.5)
                    
                    console.print("🚀 [cyan]Enviando credenciales...[/cyan]")
                    submit_button.click()
                    
                    # Esperar resultado
                    time.sleep(5)  # Tiempo para procesar login
                    
                    # Verificar si el login fue exitoso
                    if not self.detect_login_page():
                        console.print("✅ [green]LOGIN EXITOSO[/green]")
                        self.login_success = True
                        return True
                    else:
                        console.print(f"❌ [red]Intento {attempt + 1}: Aún en página de login[/red]")
                        if attempt < max_login_attempts - 1:
                            time.sleep(2)
                
                except Exception as e:
                    console.print(f"❌ [red]Error en intento {attempt + 1}: {e}[/red]")
                    if attempt < max_login_attempts - 1:
                        time.sleep(2)
            
            console.print("❌ [red]TODOS LOS INTENTOS DE LOGIN FALLARON[/red]")
            return False
                    
        except Exception as e:
            logger.error(f"❌ Error general en login: {e}")
            return False
    
    def find_login_element(self, selectors):
        """Encontrar elemento de login con múltiples selectores"""
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        return element
            except:
                continue
        return None

    def cargar_licitaciones_desde_json(self):
        """Cargar licitaciones con modo ultra rápido"""
        json_file = Path("licitaciones_para_procesar.json")
        
        if not json_file.exists():
            console.print("❌ [red]No se encontró licitaciones_para_procesar.json[/red]")
            return []
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                licitaciones = json.load(f)
            
            console.print(f"✅ [green]Cargadas {len(licitaciones)} licitaciones[/green]")
            
            # Para ultra velocidad, solo preguntar modo simple
            mode_choice = Prompt.ask(
                "Modo de procesamiento",
                choices=['incremental', 'continuar', 'completo'],
                default='incremental'
            )
            
            if mode_choice == 'incremental':
                # Filtrado simple para velocidad
                nuevas = [lic for lic in licitaciones if self.should_process_simple(lic)]
                console.print(f"🔄 [cyan]Modo INCREMENTAL: {len(nuevas)} para procesar[/cyan]")
                return nuevas
            elif mode_choice == 'continuar':
                last_index = self.checkpoint.get('last_processed', 0)
                return licitaciones[last_index:]
            else:
                return licitaciones
            
        except Exception as e:
            console.print(f"❌ [red]Error cargando JSON: {e}[/red]")
            return []
    
    def should_process_simple(self, licitacion_data):
        """Verificación simple para velocidad"""
        licitacion_id = licitacion_data.get('id', '')
        link = licitacion_data.get('link', '')
        
        # Hash simple
        content_hash = hashlib.md5(f"{licitacion_id}_{link}".encode()).hexdigest()
        
        # Si no está en historial o es muy antigua, procesar
        if content_hash not in self.history:
            return True
        
        last_processed = self.history[content_hash].get('last_processed')
        if last_processed:
            try:
                last_time = datetime.fromisoformat(last_processed)
                return datetime.now() - last_time > timedelta(hours=24)
            except:
                return True
        
        return True

    def setup_selenium_ultra_fast(self):
        """Selenium ultra optimizado"""
        try:
            options = Options()
            if self.config.get('scraping', {}).get('headless', False):
                options.add_argument('--headless')
            
            # ⚡ OPTIMIZACIONES DE VELOCIDAD
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-first-run')
            
            # Perfil optimizado
            profile = webdriver.FirefoxProfile()
            download_dir = str(Path.cwd() / "data" / "downloads")
            Path(download_dir).mkdir(parents=True, exist_ok=True)
            
            profile.set_preference("browser.download.folderList", 2)
            profile.set_preference("browser.download.dir", download_dir)
            profile.set_preference("browser.download.useDownloadDir", True)
            profile.set_preference("browser.download.manager.showWhenStarting", False)
            profile.set_preference("browser.download.manager.closeWhenDone", True)
            profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 
                                 "application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv")
            
            # ✅ TIMEOUTS BALANCEADOS (no muy agresivos)
            profile.set_preference("network.http.connection-timeout", 15)
            profile.set_preference("network.http.response.timeout", 15)
            profile.set_preference("dom.max_script_run_time", 15)
            
            options.profile = profile
            
            self.driver = webdriver.Firefox(options=options)
            self.wait = WebDriverWait(self.driver, self.ultra_fast_timeout)
            
            # ✅ TIMEOUTS GLOBALES BALANCEADOS
            self.driver.set_page_load_timeout(self.ultra_fast_timeout)
            self.driver.implicitly_wait(2)
            
            console.print("⚡ [green]Selenium optimizado para licitaciones específicas[/green]")
            return True
            
        except Exception as e:
            console.print(f"❌ [red]Error configurando Selenium: {e}[/red]")
            return False
    
    def process_single_licitacion_ultra_fast(self, licitacion_data, index):
        """Procesar licitación con velocidad máxima"""
        licitacion_start = time.time()
        
        try:
            licitacion_id = licitacion_data.get('id', f'Licitacion_{index}')
            titulo = licitacion_data.get('titulo', 'Sin título')
            link = licitacion_data.get('link')
            
            resultado = {
                'licitacion_id': licitacion_id,
                'titulo': titulo,
                'link': link,
                'index': index,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'oportunidades_encontradas': [],
                'classification': None,
                'score': 0,
                'error': None,
                'archivo_descargado': False,
                'tiempo_procesamiento': 0,
                'modo_procesamiento': 'SIN_ARCHIVO'
            }
            
            if not link:
                resultado['error'] = "No link válido"
                return resultado
            
            # 1. Navegar ultra rápido (CON LOGIN SI ES NECESARIO)
            if not self.navigate_ultra_fast(link):
                resultado['error'] = "No se pudo navegar"
                self.consecutive_errors += 1
                return resultado
            
            # 2. Intentar descarga ultra rápida (CON FALLBACK)
            downloaded_file = self.download_ultra_fast()
            
            if downloaded_file:
                # ✅ CON ARCHIVO: Análisis completo
                resultado['archivo_descargado'] = True
                resultado['modo_procesamiento'] = 'CON_ARCHIVO'
                oportunidades, score, classification = self.analyze_excel_ultra_fast(downloaded_file, licitacion_id)
                self.successful_downloads += 1
                self.resultados_procesamiento['descargas_exitosas'] += 1
            else:
                # ⚡ SIN ARCHIVO: Análisis básico del título/link
                console.print(f"   ⚡ [yellow]Sin descarga - análisis básico[/yellow]")
                oportunidades, score, classification = self.analyze_basic_content(titulo, link, licitacion_id)
                self.skipped_downloads += 1
                self.resultados_procesamiento['descargas_fallidas'] += 1
                self.resultados_procesamiento['licitaciones_sin_descarga'].append(licitacion_id)
                # ⚡ TIEMPO AHORRADO (no esperó 60s)
                self.time_savings += 50
                self.resultados_procesamiento['tiempo_ahorrado'] += 50
            
            resultado['oportunidades_encontradas'] = oportunidades
            resultado['score'] = score
            resultado['classification'] = classification
            resultado['success'] = True
            
            # 3. Clasificar resultado
            self.classify_result_ultra_fast(resultado, classification, score, downloaded_file)
            
            # 4. Actualizar historial
            content_hash = hashlib.md5(f"{licitacion_id}_{link}".encode()).hexdigest()
            self.history[content_hash] = {
                'licitacion_id': licitacion_id,
                'last_processed': datetime.now().isoformat(),
                'classification': classification,
                'score': score,
                'archivo_descargado': downloaded_file is not None
            }
            
            # 5. Reset error counter si fue exitoso
            self.consecutive_errors = 0
            
            resultado['tiempo_procesamiento'] = time.time() - licitacion_start
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error procesando {licitacion_data.get('id')}: {e}")
            resultado['error'] = str(e)
            resultado['tiempo_procesamiento'] = time.time() - licitacion_start
            self.consecutive_errors += 1
            return resultado
    
    def navigate_ultra_fast(self, link):
        """Navegación ultra rápida CON manejo de login en licitación específica"""
        try:
            # Skip si hay muchos errores consecutivos
            if self.consecutive_errors >= self.skip_threshold:
                logger.warning(f"⚠️ Skipping navegación - {self.consecutive_errors} errores consecutivos")
                return False
            
            # ✅ NAVEGAR AL LINK ESPECÍFICO DE LA LICITACIÓN
            console.print(f"🌐 [cyan]Navegando a licitación específica...[/cyan]")
            
            self.driver.set_page_load_timeout(self.ultra_fast_timeout)
            self.driver.get(link)
            
            time.sleep(self.page_delay)  # Mínimo delay
            
            # ✅ CHECK DE LOGIN EN ESTA LICITACIÓN ESPECÍFICA
            if self.detect_login_page():
                console.print("🔑 [yellow]Login necesario en esta licitación específica[/yellow]")
                if self.handle_login():
                    console.print("✅ [green]Login exitoso en licitación específica[/green]")
                    self.resultados_procesamiento['reautenticaciones'] += 1
                    time.sleep(1)  # Post-login delay mínimo
                else:
                    console.print("❌ [red]Login falló en licitación específica[/red]")
                    return False
            
            return True
            
        except TimeoutException:
            logger.warning(f"⚠️ Timeout navegando - continuando")
            return False
        except Exception as e:
            logger.error(f"❌ Error navegando: {e}")
            return False
    
    def download_ultra_fast(self):
        """Descarga ULTRA RÁPIDA con fallback agresivo"""
        try:
            download_start = time.time()
            
            # ⚡ SELECTORES MÁS COMUNES (solo los que funcionan)
            selectors = [
                "//*[contains(@title, 'Descargar contenido')]",
                "//button[contains(text(), 'Descargar contenido')]",
                "//button[@id='_wz4usd']",
                "//a[contains(text(), 'Descargar contenido')]"
            ]
            
            # Primer click ultra rápido
            clicked = False
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.click()
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                logger.warning("⚠️ No se encontró botón descarga - skip")
                return None
            
            time.sleep(0.5)  # Mínimo delay
            
            # Segundo click ultra rápido
            try:
                second_element = self.driver.find_element(By.XPATH, "//button[@id='_wz4usd']")
                if second_element.is_displayed():
                    second_element.click()
                    time.sleep(0.5)
            except:
                pass  # Continuar de cualquier manera
            
            # ⚡ ESPERA ULTRA RÁPIDA (máximo 10s)
            downloaded_file = self.wait_download_ultra_fast()
            
            download_time = time.time() - download_start
            logger.debug(f"⚡ Descarga intentada en {download_time:.1f}s")
            
            return downloaded_file
            
        except Exception as e:
            logger.warning(f"⚠️ Error descarga: {e}")
            return None
    
    def wait_download_ultra_fast(self):
        """Esperar descarga con timeout ULTRA reducido"""
        downloads_dir = Path(os.path.expanduser("~/Downloads"))
        local_downloads = Path("data/downloads")
        local_downloads.mkdir(parents=True, exist_ok=True)
        
        # Archivos existentes
        existing_system = set(downloads_dir.glob("*")) if downloads_dir.exists() else set()
        existing_local = set(local_downloads.glob("*"))
        
        start_time = time.time()
        
        # ⚡ LOOP ULTRA RÁPIDO (check cada 0.5s por máximo 10s)
        while time.time() - start_time < self.download_timeout:
            time.sleep(self.download_check_interval)  # 0.5s check
            
            # Check archivos nuevos
            current_system = set(downloads_dir.glob("*")) if downloads_dir.exists() else set()
            current_local = set(local_downloads.glob("*"))
            
            new_files = (current_system - existing_system).union(current_local - existing_local)
            
            for file_path in new_files:
                if self.is_ariba_file_ultra_fast(file_path):
                    # Mover a local si es necesario
                    if file_path.parent == downloads_dir:
                        try:
                            local_file = local_downloads / file_path.name
                            file_path.rename(local_file)
                            console.print(f"⚡ [green]Descarga detectada: {local_file.name}[/green]")
                            return local_file
                        except:
                            pass
                    
                    console.print(f"⚡ [green]Archivo detectado: {file_path.name}[/green]")
                    return file_path
        
        # ⚡ TIMEOUT = CONTINUAR SIN ARCHIVO
        logger.debug(f"⚡ Timeout descarga ({self.download_timeout}s) - continuando sin archivo")
        return None
    
    def is_ariba_file_ultra_fast(self, file_path):
        """Verificación ultra rápida de archivo Ariba"""
        if not file_path or not file_path.exists():
            return False
        
        try:
            name = file_path.name.lower()
            size = file_path.stat().st_size
            
            # ⚡ CHECKS ULTRA RÁPIDOS
            if size < 1000:  # Muy pequeño
                return False
            
            # Solo los patrones MÁS comunes
            quick_patterns = ['data', '.xls', '600103']
            return any(pattern in name for pattern in quick_patterns)
            
        except:
            return False
    
    def analyze_excel_ultra_fast(self, excel_path, licitacion_id):
        """Análisis de Excel ultra rápido"""
        try:
            # Leer archivo rápido
            try:
                df = pd.read_excel(excel_path, nrows=100)  # ⚡ Solo primeras 100 filas
            except:
                try:
                    df = pd.read_csv(excel_path, nrows=100)
                except:
                    return [], 0, 'DESCARTADO'
            
            if df.empty:
                return [], 0, 'DESCARTADO'
            
            # ⚡ ANÁLISIS ULTRA RÁPIDO con keywords planas
            total_score = 0
            oportunidades = []
            
            # Convertir todo el DataFrame a un string grande
            all_text = df.to_string().upper()
            
            # ⚡ BÚSQUEDA ULTRA RÁPIDA en texto completo
            keywords_found = []
            for keyword, score in self.scoring_system['keywords'].items():
                if keyword in all_text:
                    keywords_found.append(keyword)
                    total_score += score
            
            if keywords_found:
                oportunidades.append({
                    'licitacion_id': licitacion_id,
                    'keywords_found': keywords_found,
                    'score': total_score,
                    'method': 'ULTRA_FAST_EXCEL'
                })
            
            # Clasificar
            classification = self.classify_score_ultra_fast(total_score)
            
            return oportunidades, total_score, classification
            
        except Exception as e:
            logger.warning(f"⚠️ Error análisis Excel: {e}")
            return [], 0, 'ERROR'
    
    def analyze_basic_content(self, titulo, link, licitacion_id):
        """Análisis básico solo del título cuando no hay archivo"""
        try:
            # ⚡ ANÁLISIS SOLO DEL TÍTULO (ultra rápido)
            titulo_upper = titulo.upper() if titulo else ""
            link_upper = link.upper() if link else ""
            
            combined_text = f"{titulo_upper} {link_upper}"
            
            total_score = 0
            keywords_found = []
            
            # ⚡ BÚSQUEDA RÁPIDA en título/link
            for keyword, score in self.scoring_system['keywords'].items():
                if keyword in combined_text:
                    keywords_found.append(keyword)
                    total_score += score
            
            oportunidades = []
            if keywords_found:
                oportunidades.append({
                    'licitacion_id': licitacion_id,
                    'keywords_found': keywords_found,
                    'score': total_score,
                    'method': 'BASIC_TITLE_ANALYSIS'
                })
            
            # ⚡ PENALIZACIÓN por no tener archivo (reduce score 30%)
            total_score = int(total_score * 0.7)
            
            classification = self.classify_score_ultra_fast(total_score)
            
            return oportunidades, total_score, classification
            
        except Exception as e:
            logger.warning(f"⚠️ Error análisis básico: {e}")
            return [], 0, 'DESCARTADO'
    
    def classify_score_ultra_fast(self, score):
        """Clasificación ultra rápida"""
        thresholds = self.scoring_system['thresholds']
        
        if score >= thresholds.get('ORO', 100):
            return 'ORO'
        elif score >= thresholds.get('PLATA', 60):
            return 'PLATA'
        elif score >= thresholds.get('BRONCE', 30):
            return 'BRONCE'
        else:
            return 'DESCARTADO'
    
    def classify_result_ultra_fast(self, resultado, classification, score, downloaded_file):
        """Clasificar y gestionar resultado ultra rápido"""
        if classification == 'ORO':
            self.resultados_procesamiento['oportunidades_oro'].append(resultado)
            console.print(f"   🏆 [bold yellow]ORO: {score}pts[/bold yellow]")
            if downloaded_file:
                self.resultados_procesamiento['archivos_mantenidos'] += 1
        elif classification == 'PLATA':
            self.resultados_procesamiento['oportunidades_plata'].append(resultado)
            console.print(f"   🥈 [yellow]PLATA: {score}pts[/yellow]")
            if downloaded_file:
                self.resultados_procesamiento['archivos_mantenidos'] += 1
        elif classification == 'BRONCE':
            self.resultados_procesamiento['oportunidades_bronce'].append(resultado)
            console.print(f"   🥉 [dim yellow]BRONCE: {score}pts[/dim yellow]")
            # Eliminar archivos BRONCE para ahorrar espacio
            if downloaded_file and self.should_delete_file('BRONCE'):
                self.delete_file_ultra_fast(downloaded_file)
        else:
            self.resultados_procesamiento['descartadas'].append(resultado)
            console.print(f"   ❌ [dim]DESCARTADO: {score}pts[/dim]")
            # Eliminar archivos DESCARTADOS
            if downloaded_file and self.should_delete_file('DESCARTADO'):
                self.delete_file_ultra_fast(downloaded_file)
    
    def should_delete_file(self, classification):
        """Verificar si se debe eliminar archivo"""
        processing_config = self.config.get('processing', {})
        delete_immediately = processing_config.get('delete_immediately', ['DESCARTADO'])
        return classification in delete_immediately
    
    def delete_file_ultra_fast(self, file_path):
        """Eliminar archivo ultra rápido"""
        try:
            if file_path and Path(file_path).exists():
                Path(file_path).unlink()
                self.resultados_procesamiento['archivos_eliminados'] += 1
        except Exception as e:
            pass  # Ignorar errores de eliminación

    def calculate_ultra_metrics(self):
        """Calcular métricas ultra rápidas"""
        if self.start_time and self.procesadas > 0:
            elapsed = time.time() - self.start_time
            tiempo_promedio = elapsed / self.procesadas
            velocidad = self.procesadas / (elapsed / 3600)  # por hora
            
            return tiempo_promedio, velocidad, elapsed
        
        return 0, 0, 0

    def run_ultra_fast_processing(self):
        """Ejecutar procesamiento ultra rápido SIN LOGIN INICIAL"""
        try:
            console.print(Panel.fit(
                "⚡ [bold blue]SISTEMA ULTRA RÁPIDO - LOGIN EN LICITACIONES ESPECÍFICAS[/bold blue]\n"
                "🎯 Target: 5-8s por licitación | ⏱️ Descarga: máx 10s | 🚀 Total: 30-45min\n"
                "🔑 Login solo cuando sea necesario en cada licitación específica",
                border_style="blue"
            ))
            
            # 1. Cargar licitaciones
            licitaciones = self.cargar_licitaciones_desde_json()
            if not licitaciones:
                return False
            
            self.total_licitaciones = len(licitaciones)
            
            # 2. Setup selenium
            if not self.setup_selenium_ultra_fast():
                return False
            
            # ✅ 3. NO HACER LOGIN INICIAL - IR DIRECTO A PROCESAR LICITACIONES
            console.print("🚀 [green]Sin login inicial - procesando licitaciones específicas directamente[/green]")
            
            console.print(f"⚡ [green]Licitaciones a procesar: {self.total_licitaciones}[/green]")
            console.print(f"⚡ [cyan]Timeout descarga: {self.download_timeout}s (vs 60s normal)[/cyan]")
            console.print(f"⚡ [cyan]Check interval: {self.download_check_interval}s (vs 2s normal)[/cyan]")
            
            if not Confirm.ask(f"¿Ejecutar procesamiento ULTRA RÁPIDO?"):
                return False
            
            # 4. Procesamiento ultra rápido
            self.start_time = time.time()
            console.print("\n⚡ [bold cyan]PROCESAMIENTO ULTRA RÁPIDO INICIADO[/bold cyan]")
            
            with Progress() as progress:
                task = progress.add_task("Ultra procesando...", total=self.total_licitaciones)
                
                for i, licitacion in enumerate(licitaciones):
                    tiempo_promedio, velocidad, elapsed = self.calculate_ultra_metrics()
                    remaining = self.total_licitaciones - (i + 1)
                    eta_minutes = (remaining * tiempo_promedio) / 60 if tiempo_promedio > 0 else 0
                    
                    # ⚡ PROGRESO CON MÉTRICAS EN TIEMPO REAL
                    progress.update(task, completed=i+1,
                                  description=f"[{i+1}/{self.total_licitaciones}] "
                                            f"⚡{velocidad:.1f}/h | "
                                            f"📥{self.successful_downloads}✅ {self.skipped_downloads}⚡ | "
                                            f"ETA:{eta_minutes:.0f}min")
                    
                    # Procesar licitación
                    resultado = self.process_single_licitacion_ultra_fast(licitacion, i+1)
                    self.resultados_procesamiento['licitaciones_procesadas'].append(resultado)
                    
                    if resultado['success']:
                        self.exitosas += 1
                    else:
                        self.resultados_procesamiento['errores'].append({
                            'licitacion_id': licitacion.get('id'),
                            'error': resultado.get('error'),
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    self.procesadas += 1
                    
                    # Checkpoint cada 20 (vs 10 normal)
                    if (i + 1) % 20 == 0:
                        self.save_checkpoint(i + 1)
                    
                    # ⚡ SIN PAUSE (máxima velocidad)
            
            # 5. Finalizar
            self.save_checkpoint(self.total_licitaciones)
            self.save_processed_history()
            
            self.show_ultra_results()
            self.save_ultra_report()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error procesamiento ultra: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
    
    def show_ultra_results(self):
        """Mostrar resultados ultra rápidos"""
        console.print("\n⚡ [bold green]PROCESAMIENTO ULTRA RÁPIDO COMPLETADO[/bold green]")
        
        tiempo_promedio, velocidad, total_elapsed = self.calculate_ultra_metrics()
        
        # Tabla de velocidad
        speed_table = Table(title="⚡ Métricas de Velocidad Ultra")
        speed_table.add_column("Métrica", style="cyan")
        speed_table.add_column("Valor", style="green")
        speed_table.add_column("Comparación", style="yellow")
        
        speed_table.add_row("Tiempo total", f"{total_elapsed/60:.1f} min", f"vs ~{self.total_licitaciones*1/60:.0f}min normal")
        speed_table.add_row("Velocidad", f"{velocidad:.1f} lic/h", "vs ~30-60 lic/h normal")
        speed_table.add_row("Tiempo promedio", f"{tiempo_promedio:.1f}s", "vs ~30-60s normal")
        speed_table.add_row("Login en licitaciones", "✅ SÍ" if self.resultados_procesamiento['login_en_licitaciones'] else "❌ NO", "")
        speed_table.add_row("Re-autenticaciones", str(self.resultados_procesamiento['reautenticaciones']), "")
        
        console.print(speed_table)
        
        # Tabla de resultados
        results_table = Table(title="📊 Resultados de Procesamiento")
        results_table.add_column("Métrica", style="cyan")
        results_table.add_column("Cantidad", style="green")
        
        results_table.add_row("Total procesadas", str(self.procesadas))
        results_table.add_row("📥 Descargas exitosas", str(self.successful_downloads))
        results_table.add_row("⚡ Sin descarga (skip)", str(self.skipped_downloads))
        results_table.add_row("⏱️ Tiempo ahorrado", f"{self.time_savings/60:.1f} min")
        results_table.add_row("🏆 Oportunidades ORO", str(len(self.resultados_procesamiento['oportunidades_oro'])))
        results_table.add_row("🥈 Oportunidades PLATA", str(len(self.resultados_procesamiento['oportunidades_plata'])))
        results_table.add_row("🥉 Oportunidades BRONCE", str(len(self.resultados_procesamiento['oportunidades_bronce'])))
        results_table.add_row("❌ Descartadas", str(len(self.resultados_procesamiento['descartadas'])))
        
        console.print(results_table)
        
        # Mostrar ORO si hay
        if self.resultados_procesamiento['oportunidades_oro']:
            console.print("\n🏆 [bold yellow]OPORTUNIDADES ORO:[/bold yellow]")
            for oro in self.resultados_procesamiento['oportunidades_oro'][:3]:
                console.print(f"   💎 {oro['licitacion_id']}: {oro['titulo'][:40]}...")
                console.print(f"      🎯 Score: {oro['score']} | Archivo: {'✅' if oro['archivo_descargado'] else '⚡'}")
    
    def save_ultra_report(self):
        """Guardar reporte ultra optimizado"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            reports_dir = Path("reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Agregar métricas de velocidad al resultado
            tiempo_promedio, velocidad, total_elapsed = self.calculate_ultra_metrics()
            
            self.resultados_procesamiento.update({
                'metricas_velocidad': {
                    'tiempo_total_minutos': total_elapsed / 60,
                    'velocidad_licitaciones_por_hora': velocidad,
                    'tiempo_promedio_por_licitacion': tiempo_promedio,
                    'timeout_descarga_usado': self.download_timeout,
                    'check_interval_usado': self.download_check_interval,
                    'descargas_exitosas': self.successful_downloads,
                    'descargas_omitidas': self.skipped_downloads,
                    'tiempo_ahorrado_minutos': self.time_savings / 60
                }
            })
            
            # JSON completo
            report_file = reports_dir / f"procesamiento_ultra_rapido_{timestamp}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.resultados_procesamiento, f, indent=2, ensure_ascii=False, default=str)
            
            # Excel simplificado para velocidad
            excel_report = reports_dir / f"oportunidades_ultra_{timestamp}.xlsx"
            
            with pd.ExcelWriter(excel_report, engine='openpyxl') as writer:
                # Resumen de velocidad
                velocidad_data = {
                    'Métrica': [
                        'Tiempo total (min)', 'Velocidad (lic/h)', 'Tiempo promedio (s)',
                        'Login en licitaciones', 'Re-autenticaciones',
                        'Descargas exitosas', 'Descargas omitidas', 'Tiempo ahorrado (min)',
                        'ORO', 'PLATA', 'BRONCE', 'DESCARTADAS'
                    ],
                    'Valor': [
                        round(total_elapsed / 60, 1), round(velocidad, 1), round(tiempo_promedio, 1),
                        'SÍ' if self.resultados_procesamiento['login_en_licitaciones'] else 'NO',
                        self.resultados_procesamiento['reautenticaciones'],
                        self.successful_downloads, self.skipped_downloads, round(self.time_savings / 60, 1),
                        len(self.resultados_procesamiento['oportunidades_oro']),
                        len(self.resultados_procesamiento['oportunidades_plata']),
                        len(self.resultados_procesamiento['oportunidades_bronce']),
                        len(self.resultados_procesamiento['descartadas'])
                    ]
                }
                pd.DataFrame(velocidad_data).to_excel(writer, sheet_name='Resumen_Velocidad', index=False)
                
                # Solo ORO y PLATA (para velocidad)
                for categoria, data_list in [('ORO', self.resultados_procesamiento['oportunidades_oro']),
                                           ('PLATA', self.resultados_procesamiento['oportunidades_plata'])]:
                    if data_list:
                        simple_data = []
                        for opp in data_list:
                            simple_data.append({
                                'ID': opp['licitacion_id'],
                                'Titulo': opp['titulo'][:100],
                                'Score': opp['score'],
                                'Archivo': 'SÍ' if opp['archivo_descargado'] else 'NO',
                                'Modo': opp['modo_procesamiento'],
                                'Tiempo': round(opp['tiempo_procesamiento'], 1)
                            })
                        
                        if simple_data:
                            pd.DataFrame(simple_data).to_excel(writer, sheet_name=f'Oportunidades_{categoria}', index=False)
            
            console.print(f"⚡ [green]Reportes ultra guardados:[/green]")
            console.print(f"   📄 JSON: {report_file.name}")
            console.print(f"   📊 Excel: {excel_report.name}")
            
        except Exception as e:
            logger.error(f"❌ Error guardando reporte: {e}")

    def load_default_config(self):
        """Config por defecto COMPLETO basado en config.json original + mejoras"""
        return {
            'ariba_credentials': {
                'username': 'sales@alfamine.cl',
                'password': 'VI.2024al..al.',
                'url': 'https://service.ariba.com/Sourcing.aw/109555009/aw?awh=r&awssk=XZHPCxm2&dard=1'
            },
            'search_criteria': {
                'lineas_producto': {
                    'ALFAMINE_PREMIUM': {
                        'keywords': [
                            # ✅ ORIGINALES de tu config
                            'ZAPATA', 'CADENA', 'RODILLOS', 'SPROCKET', 
                            'RUEDA TENSORA', 'GEARBOX', 'REDUCTOR', 'MANDO FINAL', 'MF',
                            
                            # ✅ VARIACIONES EN INGLÉS (para más detección)
                            'TRACK SHOE', 'TRACK SHOES', 'SHOE', 'SHOES',
                            'CHAIN', 'CHAINS', 'TRACK CHAIN',
                            'ROLLER', 'ROLLERS', 'TRACK ROLLER', 'BOTTOM ROLLER',
                            'SPROCKETS', 'DRIVE SPROCKET',
                            'IDLER', 'FRONT IDLER', 'REAR IDLER',
                            'TRANSMISSION', 'FINAL DRIVE', 'DRIVE MOTOR',
                            'REDUCER', 'GEARBOX',
                            
                            # ✅ COMPONENTES ADICIONALES DE TREN DE RODAJE
                            'UNDERCARRIAGE', 'UC', 'TREN DE RODAJE',
                            'TRACK', 'TRACKS', 'ORUGA', 'ORUGAS',
                            'BOGGIE', 'BOGIE', 'TRUCK',
                            'BUSHING', 'BUSHINGS', 'CASQUILLO', 'CASQUILLOS',
                            'PIN', 'PINS', 'PASADOR', 'PASADORES', 'PIVOT PIN'
                        ],
                        'score': 30
                    },
                    'ALFAMINE_STANDARD': {
                        'keywords': [
                            # ✅ COMPONENTES HIDRÁULICOS Y MECÁNICOS
                            'HYDRAULIC MOTOR', 'MOTOR HIDRAULICO', 'SWING MOTOR', 'MOTOR DE GIRO',
                            'DIFFERENTIAL', 'DIFERENCIAL', 'PLANETARY', 'PLANETARIO',
                            'COUPLING', 'ACOPLAMIENTO', 'UNIVERSAL JOINT', 'CARDAN',
                            'SEAL', 'SEALS', 'SELLO', 'SELLOS', 'O-RING',
                            'BEARING', 'BEARINGS', 'RODAMIENTO', 'RODAMIENTOS', 'COJINETE'
                        ],
                        'score': 25
                    }
                },
                'perneria': {
                    'keywords': [
                        # ✅ ORIGINALES de tu config
                        'PERNO', 'TUERCA', 'NUT', 'BOLT', 'CHAVETA', 'SCREW',
                        
                        # ✅ VARIACIONES Y PLURALES
                        'PERNOS', 'TUERCAS', 'NUTS', 'BOLTS', 'CHAVETAS', 'SCREWS',
                        'TORNILLO', 'TORNILLOS', 'WASHER', 'WASHERS',
                        'ARANDELA', 'ARANDELAS', 'STUD', 'STUDS',
                        'ESPÁRRAGO', 'ESPARRAGOS', 'THREAD ROD',
                        
                        # ✅ TIPOS ESPECÍFICOS
                        'SOCKET HEAD', 'ALLEN', 'HEX BOLT', 'HEX BOLTS',
                        'FLANGE BOLT', 'FLANGE BOLTS', 'PERNO BRIDA',
                        'CAP SCREW', 'MACHINE SCREW', 'SET SCREW'
                    ],
                    'prefijos': ['AL00', 'AL01', 'AL02', 'AL03'],  # ✅ Original + extras
                    'score': 15
                },
                'marcas': {
                    'TIER_1': {
                        'brands': [
                            # ✅ ORIGINALES de tu config
                            'KRESS', 'CAT', 'CATERPILLAR', 'KOMATSU',
                            
                            # ✅ VARIACIONES
                            'CATERPILLAR INC', 'CAT®', 'KOMATSU LTD'
                        ],
                        'score': 15
                    },
                    'TIER_2': {
                        'brands': [
                            # ✅ MARCAS IMPORTANTES DE CONSTRUCCIÓN/MINERÍA
                            'VOLVO', 'LIEBHERR', 'HITACHI', 'JOHN DEERE', 'JCB', 'CASE',
                            'KOBELCO', 'KUBOTA', 'YANMAR', 'DOOSAN', 'HYUNDAI', 'SANY',
                            'NEW HOLLAND', 'BOBCAT', 'TEREX', 'MANITOU'
                        ],
                        'score': 12
                    },
                    'TIER_3': {
                        'brands': [
                            # ✅ MARCAS ASIÁTICAS
                            'XCMG', 'ZOOMLION', 'LIUGONG', 'SDLG', 'LONKING', 'XGMA',
                            'SHANTUI', 'CHANGLIN', 'SUNWARD', 'SHANDONG'
                        ],
                        'score': 8
                    }
                }
            },
            'scoring': {
                'classification_thresholds': {
                    'ORO': 100,      # ✅ Ajustado para nuevo sistema
                    'PLATA': 60,     # ✅ Más accesible  
                    'BRONCE': 30,    # ✅ Detecta más oportunidades
                    'DESCARTADO': 0
                }
            },
            'processing': {
                'keep_files': ['ORO', 'PLATA'],
                'delete_immediately': ['DESCARTADO'],
                'delete_after_report': ['BRONCE']
            },
            'scraping': {
                'browser_type': 'firefox',
                'headless': False,
                'timeout': 8,                    # ✅ Ultra rápido
                'download_timeout': 10,          # ✅ Máximo 10s
                'download_check_interval': 0.5,  # ✅ Check cada 0.5s
                'max_retries': 1                 # ✅ Solo 1 retry para velocidad
            }
        }


def main():
    """Función principal ultra rápida CON LOGIN EN LICITACIONES ESPECÍFICAS"""
    console.print(Panel.fit(
        "⚡ [bold blue]SISTEMA ULTRA RÁPIDO - LOGIN EN LICITACIONES ESPECÍFICAS[/bold blue]\n"
        "🎯 Objetivo: 5-8s por licitación | ⏱️ Descarga: 10s máx | 📊 Total: 30-45min\n"
        "🔑 Va directamente a cada licitación y hace login solo si es necesario\n"
        "🚀 Procesa CON o SIN archivo descargado | 📊 Usa links del Excel directamente",
        border_style="blue"
    ))
    
    # Cargar config ultra rápido
    config = None
    try:
        for config_path in [Path("config.json"), Path("config/config.json"), Path("../config/config.json")]:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                console.print(f"✅ [green]Config cargado desde {config_path}[/green]")
                break
    except Exception as e:
        console.print(f"⚠️ [yellow]Config error: {e} - usando default[/yellow]")
    
    console.print("\n⚡ [bold]CARACTERÍSTICAS ULTRA RÁPIDAS:[/bold]")
    console.print("   🔗 LINKS DIRECTOS: Usa los links del Excel directamente")
    console.print("   🔑 LOGIN INTELIGENTE: Solo hace login cuando lo detecta necesario")
    console.print("   🔥 DESCARGA: 10s máximo (vs 60s normal)")
    console.print("   ⚡ CHECK: cada 0.5s (vs 2s normal)")
    console.print("   🚀 FALLBACK: Continúa sin archivo si no descarga")
    console.print("   📊 ANÁLISIS: Completo con archivo, básico sin archivo")
    console.print("   🎯 VELOCIDAD: 5-8s por licitación vs 30-60s normal")
    
    if not Confirm.ask("\n¿Ejecutar sistema ULTRA RÁPIDO con login inteligente?"):
        return
    
    # Ejecutar ultra rápido
    sistema = SistemaUltraRapido(config)
    
    try:
        success = sistema.run_ultra_fast_processing()
        
        if success:
            console.print("\n⚡ [bold green]¡PROCESAMIENTO ULTRA RÁPIDO EXITOSO![/bold green]")
            console.print("🎯 Objetivo cumplido: máxima velocidad con login inteligente")
        else:
            console.print("\n⚠️ [yellow]Procesamiento incompleto[/yellow]")
    
    except KeyboardInterrupt:
        console.print("\n⏹️ [yellow]Interrumpido - guardando checkpoint...[/yellow]")
        sistema.save_checkpoint(sistema.procesadas)
    except Exception as e:
        console.print(f"\n❌ [red]Error: {e}[/red]")


if __name__ == "__main__":
    main()