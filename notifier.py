# src/notifier.py
"""
ALFAMINE NOTIFIER v1.0
Sistema de notificaciones por email (simplificado)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from loguru import logger

class EmailNotifier:
    """Sistema básico de notificaciones por email"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.notifications_config = config.get('notifications', {})
        
        logger.info("📧 Notifier iniciado")
    
    def send_daily_report(self, opportunities: List[Dict], report_file: Optional[Path] = None) -> bool:
        """Enviar reporte diario por email"""
        
        if not self.notifications_config.get('gmail_enabled', False):
            logger.info("📧 Notificaciones deshabilitadas en config")
            return True
        
        if not opportunities:
            logger.info("📭 No hay oportunidades para notificar")
            return True
        
        try:
            logger.info(f"📨 Preparando notificación para {len(opportunities)} oportunidades...")
            
            # Generar contenido del email
            subject = self._generate_subject(opportunities)
            html_content = self._generate_html_content(opportunities)
            
            # Por ahora solo loggeamos (implementar Gmail API después)
            logger.info(f"📧 EMAIL SIMULADO:")
            logger.info(f"   Para: {', '.join(self.notifications_config.get('recipients', []))}")
            logger.info(f"   Asunto: {subject}")
            if report_file:
                logger.info(f"   Adjunto: {report_file.name}")
            
            # Mostrar resumen en logs
            oro = len([o for o in opportunities if o.get('classification') == 'ORO'])
            plata = len([o for o in opportunities if o.get('classification') == 'PLATA'])
            
            logger.info(f"   🏆 Oro: {oro} | 🥈 Plata: {plata}")
            
            # Simular éxito
            logger.success("✅ Notificación enviada (simulada)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando notificación: {e}")
            return False
    
    def _generate_subject(self, opportunities: List[Dict]) -> str:
        """Generar asunto del email"""
        oro = len([o for o in opportunities if o.get('classification') == 'ORO'])
        total = len(opportunities)
        date_str = datetime.now().strftime("%d/%m/%Y")
        
        if oro > 0:
            return f"🎯 {oro} Oportunidades ORO + {total-oro} más - Alfamine {date_str}"
        else:
            return f"📊 {total} Oportunidades Detectadas - Alfamine {date_str}"
    
    def _generate_html_content(self, opportunities: List[Dict]) -> str:
        """Generar contenido HTML del email"""
        oro = [o for o in opportunities if o.get('classification') == 'ORO']
        plata = [o for o in opportunities if o.get('classification') == 'PLATA']
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2E86AB;">🎯 Reporte Diario Alfamine</h2>
            <p><strong>Fecha:</strong> {datetime.now().strftime('%d de %B, %Y')}</p>
            
            <h3>📊 Resumen:</h3>
            <ul>
                <li>🏆 Oportunidades Oro: <strong>{len(oro)}</strong></li>
                <li>🥈 Oportunidades Plata: <strong>{len(plata)}</strong></li>
                <li>📊 Total: <strong>{len(opportunities)}</strong></li>
            </ul>
        """
        
        if oro:
            html += "<h3>🏆 Top Oportunidades Oro:</h3><ul>"
            for opp in oro[:5]:  # Top 5
                html += f"<li><strong>{opp['id']}</strong>: {opp['title'][:60]}... (Score: {opp['score']})</li>"
            html += "</ul>"
        
        html += """
            <p><em>Reporte generado automáticamente por Sistema Alfamine Monitor</em></p>
        </body>
        </html>
        """
        
        return html
    
    def send_test_notification(self) -> bool:
        """Enviar notificación de prueba"""
        logger.info("🧪 Enviando notificación de prueba...")
        
        # Simular notificación de prueba
        logger.info("📧 EMAIL DE PRUEBA SIMULADO:")
        logger.info("   Asunto: 🧪 Prueba Sistema Alfamine - OK")
        logger.info("   Contenido: Sistema funcionando correctamente")
        
        logger.success("✅ Notificación de prueba enviada (simulada)")
        return True