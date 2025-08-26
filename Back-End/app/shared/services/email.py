import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from pathlib import Path
from app.config.settings import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio para envío de emails"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.use_tls = True  # Por defecto usar TLS
        self.from_email = settings.SMTP_USER  # Usar el mismo usuario como remitente
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[Path]] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None
    ) -> bool:
        """Enviar email"""
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Agregar cuerpo del mensaje
            if body:
                text_part = MIMEText(body, 'plain', 'utf-8')
                msg.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Agregar archivos adjuntos
            if attachments:
                for attachment_path in attachments:
                    if attachment_path.exists():
                        with open(attachment_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {attachment_path.name}'
                        )
                        msg.attach(part)
            
            # Enviar email
            all_recipients = to_emails.copy()
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                server.send_message(msg, to_addrs=all_recipients)
            
            logger.info(f"Email enviado exitosamente a: {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar email: {str(e)}")
            return False
    
    async def send_notification_email(
        self,
        to_email: str,
        template_name: str,
        context: dict
    ) -> bool:
        """Enviar email de notificación usando plantilla"""
        templates = {
            'caso_nuevo': {
                'subject': 'Nuevo caso asignado - {codigo_caso}',
                'body': '''Estimado/a {nombre_usuario},

Se le ha asignado un nuevo caso:

Código: {codigo_caso}
Paciente: {nombre_paciente}
Tipo de prueba: {tipo_prueba}
Prioridad: {prioridad}

Por favor, ingrese al sistema para revisar los detalles.

Saludos,
Sistema PathSys'''
            },
            'caso_completado': {
                'subject': 'Caso completado - {codigo_caso}',
                'body': '''Estimado/a {nombre_usuario},

El caso {codigo_caso} ha sido completado y está listo para firma.

Paciente: {nombre_paciente}
Completado por: {completado_por}
Fecha: {fecha_completado}

Saludos,
Sistema PathSys'''
            },
            'resultado_firmado': {
                'subject': 'Resultado firmado - {codigo_caso}',
                'body': '''Estimado/a {nombre_usuario},

El resultado del caso {codigo_caso} ha sido firmado digitalmente.

Paciente: {nombre_paciente}
Firmado por: {firmado_por}
Fecha: {fecha_firma}

El resultado está disponible para entrega.

Saludos,
Sistema PathSys'''
            },
            'password_reset': {
                'subject': 'Restablecimiento de contraseña - PathSys',
                'body': '''Estimado/a {nombre_usuario},

Ha solicitado restablecer su contraseña.

Su nueva contraseña temporal es: {nueva_password}

Por favor, cambie esta contraseña al iniciar sesión.

Saludos,
Sistema PathSys'''
            }
        }
        
        if template_name not in templates:
            logger.error(f"Plantilla de email no encontrada: {template_name}")
            return False
        
        template = templates[template_name]
        subject = template['subject'].format(**context)
        body = template['body'].format(**context)
        
        return await self.send_email([to_email], subject, body)
    
    def is_configured(self) -> bool:
        """Verificar si el servicio de email está configurado"""
        return bool(
            self.smtp_server and 
            self.smtp_port and 
            self.from_email
        )

# Instancia global del servicio
email_service = EmailService()