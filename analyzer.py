# src/analyzer.py
"""
ALFAMINE ANALYZER v1.0
Analizador inteligente de licitaciones con sistema de scoring avanzado
"""

import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import chardet

from loguru import logger

class OpportunityAnalyzer:
    """Analizador de oportunidades de licitaciones para Alfamine"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.keywords_processed = self._process_keywords()
        
        logger.info(f"🎯 Analyzer iniciado con {len(self.keywords_processed['all'])} keywords")
    
    def _process_keywords(self) -> Dict:
        """Procesar keywords del config con scoring"""
        keywords = {
            'all': [],
            'by_category': {},
            'scoring': {}
        }
        
        try:
            search_criteria = self.config.get('search_criteria', {})
            
            # Procesar líneas de producto
            lineas_producto = search_criteria.get('lineas_producto', {})
            for marca, productos in lineas_producto.items():
                category_key = f'linea_{marca.lower()}'
                keywords['by_category'][category_key] = productos
                keywords['all'].extend(productos)
                
                # Scoring alto para productos core de cada línea
                base_score = 25 if marca == 'ALFAMINE' else 20
                for producto in productos:
                    keywords['scoring'][producto.upper()] = base_score
            
            # Procesar pernería
            perneria = search_criteria.get('perneria', {})
            perneria_items = perneria.get('keywords', []) + perneria.get('prefijos', [])
            keywords['by_category']['perneria'] = perneria_items
            keywords['all'].extend(perneria_items)
            
            # Scoring medio para pernería
            for item in perneria_items:
                keywords['scoring'][item.upper()] = 15
            
            # Procesar marcas
            marcas = search_criteria.get('marcas', [])
            keywords['by_category']['marcas'] = marcas
            keywords['all'].extend(marcas)
            
            # Scoring para marcas
            for marca in marcas:
                keywords['scoring'][marca.upper()] = 12
            
            # Eliminar duplicados
            keywords['all'] = list(set([k.upper() for k in keywords['all']]))
            
            logger.info(f"📊 Keywords procesadas: {len(keywords['all'])} totales")
            
            return keywords
            
        except Exception as e:
            logger.error(f"❌ Error procesando keywords: {e}")
            # Fallback básico
            return {
                'all': ['ZAPATA', 'CADENA', 'CAT', 'PERNO'],
                'by_category': {'basicas': ['ZAPATA', 'CADENA', 'CAT', 'PERNO']},
                'scoring': {'ZAPATA': 25, 'CADENA': 25, 'CAT': 12, 'PERNO': 15}
            }
    
    def detect_file_type(self, file_path: Path) -> str:
        """Detectar tipo de archivo descargado"""
        try:
            # Leer primeros bytes
            with open(file_path, 'rb') as f:
                first_bytes = f.read(1024)
            
            # Detectar HTML disfrazado
            if b'<html' in first_bytes.lower() or b'<table' in first_bytes.lower():
                logger.info(f"📄 Archivo detectado como HTML: {file_path.name}")
                return 'html'
            
            # Detectar Excel real
            if file_path.suffix.lower() in ['.xlsx', '.xls']:
                logger.info(f"📊 Archivo detectado como Excel: {file_path.name}")
                return 'excel'
            
            # Detectar CSV
            if file_path.suffix.lower() == '.csv':
                logger.info(f"📄 Archivo detectado como CSV: {file_path.name}")
                return 'csv'
            
            logger.warning(f"❓ Tipo de archivo no reconocido: {file_path.name}")
            return 'unknown'
            
        except Exception as e:
            logger.error(f"❌ Error detectando tipo de archivo: {e}")
            return 'unknown'
    
    def read_file_robust(self, file_path: Path) -> Optional[pd.DataFrame]:
        """Leer archivo de forma robusta según su tipo"""
        file_type = self.detect_file_type(file_path)
        
        if file_type == 'html':
            return self._read_html_file(file_path)
        elif file_type == 'excel':
            return self._read_excel_file(file_path)
        elif file_type == 'csv':
            return self._read_csv_file(file_path)
        else:
            # Intentar todos los métodos
            logger.info("🔄 Intentando múltiples métodos de lectura...")
            
            for method in [self._read_excel_file, self._read_html_file, self._read_csv_file]:
                try:
                    df = method(file_path)
                    if df is not None and not df.empty:
                        return df
                except:
                    continue
            
            logger.error("❌ No se pudo leer el archivo con ningún método")
            return None
    
    def _read_html_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """Leer archivo HTML que contiene tabla"""
        try:
            # Detectar encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                detected = chardet.detect(raw_data)
                encoding = detected.get('encoding', 'utf-8')
            
            logger.debug(f"📄 Leyendo HTML con encoding: {encoding}")
            
            # Intentar con pandas read_html
            try:
                df_list = pd.read_html(str(file_path), encoding=encoding)
                if df_list:
                    # Tomar la tabla más grande
                    main_df = max(df_list, key=len)
                    logger.success(f"✅ HTML leído con pandas: {main_df.shape}")
                    return self._clean_dataframe(main_df, file_path)
            except Exception as e:
                logger.debug(f"pandas read_html falló: {e}")
            
            # Fallback con BeautifulSoup (como en tu código original)
            from bs4 import BeautifulSoup
            
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            tables = soup.find_all('table')
            if not tables:
                logger.warning("❌ No se encontraron tablas en HTML")
                return None
            
            # Procesar la tabla más grande
            main_table = max(tables, key=lambda t: len(t.find_all('tr')))
            rows = main_table.find_all('tr')
            
            if not rows:
                return None
            
            # Extraer headers y datos
            header_row = rows[0]
            headers = [cell.get_text(strip=True) for cell in header_row.find_all(['th', 'td'])]
            
            data_rows = []
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                
                # Normalizar longitud
                if len(row_data) < len(headers):
                    row_data.extend([''] * (len(headers) - len(row_data)))
                elif len(row_data) > len(headers):
                    row_data = row_data[:len(headers)]
                
                if any(cell.strip() for cell in row_data):
                    data_rows.append(row_data)
            
            if headers and data_rows:
                df = pd.DataFrame(data_rows, columns=headers)
                logger.success(f"✅ HTML parseado con BeautifulSoup: {df.shape}")
                return self._clean_dataframe(df, file_path)
            
        except Exception as e:
            logger.error(f"❌ Error leyendo HTML: {e}")
        
        return None
    
    def _read_excel_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """Leer archivo Excel real"""
        engines = ['openpyxl', 'xlrd', None]
        
        for engine in engines:
            try:
                logger.debug(f"📊 Intentando leer Excel con engine: {engine}")
                
                if engine:
                    df = pd.read_excel(file_path, engine=engine)
                else:
                    df = pd.read_excel(file_path)
                
                if not df.empty:
                    logger.success(f"✅ Excel leído con {engine or 'default'}: {df.shape}")
                    return self._clean_dataframe(df, file_path)
                    
            except Exception as e:
                logger.debug(f"Engine {engine} falló: {e}")
                continue
        
        logger.error("❌ No se pudo leer Excel con ningún engine")
        return None
    
    def _read_csv_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """Leer archivo CSV"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        separators = [',', ';', '\t']
        
        for encoding in encodings:
            for sep in separators:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, sep=sep)
                    if not df.empty:
                        logger.success(f"✅ CSV leído con {encoding}/{sep}: {df.shape}")
                        return self._clean_dataframe(df, file_path)
                except:
                    continue
        
        logger.error("❌ No se pudo leer CSV")
        return None
    
    def _clean_dataframe(self, df: pd.DataFrame, file_path: Path) -> pd.DataFrame:
        """Limpiar y estructurar DataFrame (basado en tu código original)"""
        try:
            logger.info(f"🧹 Limpiando DataFrame de {len(df)} filas...")
            
            # Resetear índice
            df = df.reset_index(drop=True)
            
            # Buscar fila de headers (similar a tu código)
            header_row = None
            for i, row in df.iterrows():
                row_str = ' '.join(str(cell).lower() for cell in row if pd.notna(cell))
                if any(keyword in row_str for keyword in ['título', 'title', 'id', 'fecha', 'documento']):
                    header_row = i
                    break
            
            if header_row is not None and header_row > 0:
                logger.info(f"📋 Headers encontrados en fila {header_row}")
                # Usar esa fila como headers
                new_headers = df.iloc[header_row].fillna(f'Col_{i}' for i in range(len(df.columns)))
                df.columns = new_headers
                df = df.iloc[header_row + 1:].reset_index(drop=True)
            
            # Limpiar datos: remover filas de estado y vacías (como en tu código)
            df_clean = df[
                ~df.iloc[:, 0].astype(str).str.contains("Estado:", na=False) &
                df.iloc[:, 0].notna() &
                (df.iloc[:, 0].astype(str).str.strip() != '')
            ].copy()
            
            # Asegurar columnas básicas
            if len(df_clean.columns) >= 2:
                # Renombrar columnas de forma consistente
                col_mapping = {}
                for i, col in enumerate(df_clean.columns):
                    if i == 0:
                        col_mapping[col] = "Titulo"
                    elif i == 1:
                        col_mapping[col] = "ID"
                    elif i == 2:
                        col_mapping[col] = "Fecha_Cierre"
                    elif i == 3:
                        col_mapping[col] = "Tipo"
                    else:
                        col_mapping[col] = f"Col_{i}"
                
                df_clean = df_clean.rename(columns=col_mapping)
            
            # Remover filas donde ID está vacío
            if 'ID' in df_clean.columns:
                df_clean = df_clean.dropna(subset=["ID"])
                df_clean = df_clean[df_clean["ID"].astype(str).str.strip() != '']
            
            logger.success(f"✅ DataFrame limpiado: {len(df_clean)} filas válidas")
            
            # Mostrar muestra de datos (como en tu código)
            if not df_clean.empty:
                logger.info("📋 Muestra de datos:")
                for i, row in df_clean.head(3).iterrows():
                    titulo = row.get('Titulo', 'Sin título')
                    id_lic = row.get('ID', 'Sin ID')
                    logger.info(f"  {i+1}: {str(titulo)[:50]}... | ID: {id_lic}")
            
            return df_clean
            
        except Exception as e:
            logger.error(f"❌ Error limpiando DataFrame: {e}")
            return df
    
    def analyze_file(self, file_path: Path) -> List[Dict]:
        """Analizar archivo completo y retornar oportunidades"""
        logger.info(f"📊 Analizando archivo: {file_path.name}")
        
        # 1. Leer archivo
        df = self.read_file_robust(file_path)
        
        if df is None or df.empty:
            logger.error("❌ No se pudo leer el archivo o está vacío")
            return []
        
        # 2. Analizar cada fila
        opportunities = []
        
        for index, row in df.iterrows():
            opportunity = self._analyze_single_row(row, index, file_path)
            if opportunity and opportunity['score'] > 0:
                opportunities.append(opportunity)
        
        # 3. Clasificar y ordenar
        opportunities = self._classify_opportunities(opportunities)
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        logger.success(f"🎯 {len(opportunities)} oportunidades encontradas")
        
        # 4. Mostrar estadísticas
        self._show_analysis_stats(opportunities)
        
        return opportunities
    
    def _analyze_single_row(self, row: pd.Series, index: int, file_path: Path) -> Optional[Dict]:
        """Analizar una fila individual"""
        try:
            # Convertir toda la fila a texto
            row_text = " ".join([str(cell) for cell in row if pd.notna(cell)]).upper()
            
            if not row_text.strip():
                return None
            
            # Extraer información básica
            titulo = str(row.get('Titulo', row.iloc[0] if len(row) > 0 else 'Sin título'))
            licitacion_id = str(row.get('ID', row.iloc[1] if len(row) > 1 else f'ID_{index}'))
            fecha_cierre = row.get('Fecha_Cierre', '')
            
            # Análisis de keywords con scoring
            score = 0
            keywords_found = []
            categories_detected = []
            
            # Buscar cada keyword con su scoring
            for keyword, points in self.keywords_processed['scoring'].items():
                if keyword in row_text:
                    keywords_found.append(keyword)
                    score += points
            
            # Determinar categorías
            for category, keywords_list in self.keywords_processed['by_category'].items():
                if any(kw.upper() in row_text for kw in keywords_list):
                    categories_detected.append(category)
            
            # Solo retornar si hay keywords relevantes
            if not keywords_found:
                return None
            
            return {
                'index': index,
                'id': licitacion_id,
                'title': titulo,
                'fecha_cierre': str(fecha_cierre) if fecha_cierre else '',
                'keywords_found': keywords_found,
                'categories': categories_detected,
                'score': score,
                'raw_text': row_text[:200],  # Primeros 200 chars para referencia
                'source_file': file_path.name
            }
            
        except Exception as e:
            logger.debug(f"Error analizando fila {index}: {e}")
            return None
    
    def _classify_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Clasificar oportunidades por score"""
        for opp in opportunities:
            score = opp['score']
            
            if score >= 50:
                opp['classification'] = 'ORO'
                opp['priority'] = 1
            elif score >= 30:
                opp['classification'] = 'PLATA'
                opp['priority'] = 2
            elif score >= 15:
                opp['classification'] = 'BRONCE'
                opp['priority'] = 3
            else:
                opp['classification'] = 'SEGUIMIENTO'
                opp['priority'] = 4
        
        return opportunities
    
    def _show_analysis_stats(self, opportunities: List[Dict]):
        """Mostrar estadísticas del análisis"""
        if not opportunities:
            return
        
        stats = {
            'total': len(opportunities),
            'oro': len([o for o in opportunities if o['classification'] == 'ORO']),
            'plata': len([o for o in opportunities if o['classification'] == 'PLATA']),
            'bronce': len([o for o in opportunities if o['classification'] == 'BRONCE']),
            'seguimiento': len([o for o in opportunities if o['classification'] == 'SEGUIMIENTO'])
        }
        
        logger.info(f"📈 Estadísticas del análisis:")
        logger.info(f"   🏆 Oro: {stats['oro']} | 🥈 Plata: {stats['plata']} | 🥉 Bronce: {stats['bronce']} | 👁️ Seguimiento: {stats['seguimiento']}")
        
        # Top keywords encontradas
        all_keywords = []
        for opp in opportunities:
            all_keywords.extend(opp['keywords_found'])
        
        if all_keywords:
            from collections import Counter
            top_keywords = Counter(all_keywords).most_common(5)
            logger.info(f"🔑 Top keywords: {', '.join([f'{kw}({count})' for kw, count in top_keywords])}")
    
    def generate_report(self, opportunities: List[Dict]) -> Optional[Path]:
        """Generar reporte Excel con las oportunidades"""
        if not opportunities:
            logger.info("📭 No hay oportunidades para generar reporte")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = Path("reports") / f"Alfamine_Oportunidades_{timestamp}.xlsx"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"📊 Generando reporte: {report_file.name}")
            
            # Separar por clasificación
            oro = [o for o in opportunities if o['classification'] == 'ORO']
            plata = [o for o in opportunities if o['classification'] == 'PLATA']
            bronce = [o for o in opportunities if o['classification'] == 'BRONCE']
            seguimiento = [o for o in opportunities if o['classification'] == 'SEGUIMIENTO']
            
            # Crear Excel con múltiples hojas
            with pd.ExcelWriter(report_file, engine='openpyxl') as writer:
                
                # Hoja 1: Dashboard Ejecutivo
                dashboard = self._create_dashboard_data(opportunities)
                dashboard.to_excel(writer, sheet_name='Dashboard', index=False)
                
                # Hoja 2: Oportunidades Oro
                if oro:
                    oro_df = self._create_opportunities_dataframe(oro)
                    oro_df.to_excel(writer, sheet_name='Oportunidades_Oro', index=False)
                
                # Hoja 3: Oportunidades Plata
                if plata:
                    plata_df = self._create_opportunities_dataframe(plata)
                    plata_df.to_excel(writer, sheet_name='Oportunidades_Plata', index=False)
                
                # Hoja 4: Todas las Oportunidades
                todas_df = self._create_opportunities_dataframe(opportunities)
                todas_df.to_excel(writer, sheet_name='Todas_Oportunidades', index=False)
                
                # Hoja 5: Análisis por Categoría
                categorias_df = self._create_category_analysis(opportunities)
                if not categorias_df.empty:
                    categorias_df.to_excel(writer, sheet_name='Analisis_Categorias', index=False)
            
            logger.success(f"✅ Reporte generado: {report_file.name}")
            return report_file
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")
            return None
    
    def _create_dashboard_data(self, opportunities: List[Dict]) -> pd.DataFrame:
        """Crear datos del dashboard ejecutivo"""
        stats = {
            'oro': len([o for o in opportunities if o['classification'] == 'ORO']),
            'plata': len([o for o in opportunities if o['classification'] == 'PLATA']),
            'bronce': len([o for o in opportunities if o['classification'] == 'BRONCE']),
            'seguimiento': len([o for o in opportunities if o['classification'] == 'SEGUIMIENTO'])
        }
        
        dashboard_data = [
            {'Métrica': 'Total Oportunidades', 'Valor': len(opportunities)},
            {'Métrica': 'Oportunidades Oro', 'Valor': stats['oro']},
            {'Métrica': 'Oportunidades Plata', 'Valor': stats['plata']},
            {'Métrica': 'Oportunidades Bronce', 'Valor': stats['bronce']},
            {'Métrica': 'Score Promedio', 'Valor': f"{sum(o['score'] for o in opportunities) / len(opportunities):.1f}"},
            {'Métrica': 'Fecha Análisis', 'Valor': datetime.now().strftime('%Y-%m-%d %H:%M')},
            {'Métrica': 'Archivo Analizado', 'Valor': opportunities[0].get('source_file', 'N/A') if opportunities else 'N/A'}
        ]
        
        return pd.DataFrame(dashboard_data)
    
    def _create_opportunities_dataframe(self, opportunities: List[Dict]) -> pd.DataFrame:
        """Crear DataFrame de oportunidades"""
        data = []
        for opp in opportunities:
            data.append({
                'ID_Licitacion': opp['id'],
                'Titulo': opp['title'][:100],  # Limitar longitud
                'Score': opp['score'],
                'Clasificacion': opp['classification'],
                'Keywords_Encontradas': ', '.join(opp['keywords_found'][:5]),  # Top 5
                'Categorias': ', '.join(opp['categories']),
                'Fecha_Cierre': opp['fecha_cierre'],
                'Fila_Original': opp['index'] + 1
            })
        
        return pd.DataFrame(data)
    
    def _create_category_analysis(self, opportunities: List[Dict]) -> pd.DataFrame:
        """Crear análisis por categorías"""
        category_stats = {}
        
        for opp in opportunities:
            for category in opp['categories']:
                if category not in category_stats:
                    category_stats[category] = {
                        'count': 0,
                        'total_score': 0,
                        'avg_score': 0
                    }
                
                category_stats[category]['count'] += 1
                category_stats[category]['total_score'] += opp['score']
        
        # Calcular promedios
        for category, stats in category_stats.items():
            stats['avg_score'] = stats['total_score'] / stats['count']
        
        if not category_stats:
            return pd.DataFrame()
        
        data = []
        for category, stats in category_stats.items():
            data.append({
                'Categoria': category,
                'Cantidad_Oportunidades': stats['count'],
                'Score_Promedio': round(stats['avg_score'], 1),
                'Score_Total': stats['total_score']
            })
        
        df = pd.DataFrame(data)
        return df.sort_values('Score_Total', ascending=False)