# extraer_links_real.py
"""
Extrae los LINKS REALES de Excel (no solo el texto)
"""

import openpyxl
from pathlib import Path

def extraer_hyperlinks_reales():
    """Extraer hipervínculos reales de Excel"""
    
    # Buscar archivo data.xlsx o data(4).xlsx
    archivos = list(Path.cwd().glob("data*.xlsx")) + list(Path.cwd().glob("data*.xls"))
    
    if not archivos:
        print("❌ No se encontró archivo data.xlsx")
        return
    
    # Usar el más reciente
    archivo = max(archivos, key=lambda x: x.stat().st_mtime)
    print(f"📖 Procesando: {archivo.name}")
    
    try:
        # Abrir Excel con openpyxl
        workbook = openpyxl.load_workbook(archivo)
        sheet = workbook.active
        
        links_encontrados = []
        
        print("🔍 Buscando links desde fila 3...")
        
        # Desde fila 3 hacia abajo
        for row in range(3, sheet.max_row + 1):
            cell = sheet[f'A{row}']
            
            # ¡AQUÍ ESTÁ LA CLAVE!
            if cell.hyperlink:
                url_real = cell.hyperlink.target
                texto = str(cell.value) if cell.value else ""
                
                print(f"✅ Fila {row}: {texto[:50]}...")
                print(f"   Link: {url_real}")
                
                links_encontrados.append({
                    'fila': row,
                    'texto': texto,
                    'url': url_real
                })
        
        workbook.close()
        
        print(f"\n🎉 TOTAL: {len(links_encontrados)} links extraídos")
        
        # Guardar en archivo de texto
        with open('links_extraidos.txt', 'w', encoding='utf-8') as f:
            f.write("LINKS EXTRAÍDOS DE EXCEL\n")
            f.write("=" * 50 + "\n\n")
            
            for link in links_encontrados:
                f.write(f"Fila {link['fila']}:\n")
                f.write(f"Texto: {link['texto']}\n")
                f.write(f"URL: {link['url']}\n")
                f.write("-" * 30 + "\n")
        
        print("💾 Links guardados en: links_extraidos.txt")
        return links_encontrados
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    extraer_hyperlinks_reales()