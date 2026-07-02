"""Email templates con diseño PsicoaTrading — marca oscura + turquesa."""


def get_base_template(content: str) -> str:
    """Wrapper HTML con diseño de marca PsicoaTrading."""
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="margin:0;padding:0;background-color:#f4f4f4;font-family:'Segoe UI',Arial,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;padding:20px 0;">
            <tr><td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background-color:#0B1426;padding:24px 32px;text-align:center;">
                            <h1 style="color:#2DD4BF;margin:0;font-size:24px;letter-spacing:1px;">PsicoaTrading</h1>
                            <p style="color:#94A3B8;margin:4px 0 0;font-size:13px;">Psicología Aplicada al Trading</p>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding:32px;color:#1E293B;font-size:15px;line-height:1.6;">
                            {content}
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background-color:#F8FAFC;padding:20px 32px;text-align:center;border-top:1px solid #E2E8F0;">
                            <p style="color:#64748B;font-size:12px;margin:0;">
                                © 2026 PsicoaTrading · <a href="https://psicoatrading.online" style="color:#2DD4BF;text-decoration:none;">psicoatrading.online</a>
                            </p>
                            <p style="color:#94A3B8;font-size:11px;margin:8px 0 0;">
                                Instagram: <a href="https://instagram.com/psicoatrading" style="color:#2DD4BF;text-decoration:none;">@psicoatrading</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td></tr>
        </table>
    </body>
    </html>
    """


# ============================================================
# EMAILS DE CONTACTO
# ============================================================

def template_contacto_autorespuesta(nombre: str) -> dict:
    """Email automático al usuario cuando envía formulario de contacto."""
    content = f"""
        <h2 style="color:#0B1426;margin:0 0 16px;">Hola {nombre},</h2>
        <p>Recibimos tu solicitud. Un psicólogo especializado en trading revisará tu caso y te contactará en las próximas <strong>24 horas hábiles</strong>.</p>
        <p>Mientras tanto, si aún no lo has hecho, te invitamos a realizar nuestro <strong>test psicológico gratuito</strong>. En solo 4 minutos descubrirás tu perfil como trader:</p>
        <p style="text-align:center;margin:24px 0;">
            <a href="https://psicoatrading.online/#tests" style="display:inline-block;background-color:#2DD4BF;color:#0B1426;padding:12px 32px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:15px;">Hacer el test gratuito →</a>
        </p>
        <p>Si tienes alguna pregunta urgente, puedes responder directamente a este email.</p>
        <p style="margin-top:24px;">Un saludo,<br><strong>Equipo PsicoaTrading</strong></p>
    """
    return {
        "subject": "Recibimos tu solicitud — PsicoaTrading",
        "html": get_base_template(content)
    }


def template_contacto_notificacion_admin(nombre: str, email: str, pais: str, experiencia: str, whatsapp: str, mensaje: str = "") -> dict:
    """Notificación al admin cuando llega un nuevo contacto."""
    content = f"""
        <h2 style="color:#0B1426;margin:0 0 16px;">📬 Nuevo contacto recibido</h2>
        <table style="width:100%;border-collapse:collapse;">
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;width:130px;">Nombre:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;">{nombre}</td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;">Email:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;">{email}</td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;">WhatsApp:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;">{whatsapp or 'No proporcionado'}</td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;">País:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;">{pais}</td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;">Experiencia:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;">{experiencia}</td></tr>
            <tr><td style="padding:8px;font-weight:bold;vertical-align:top;">Mensaje:</td><td style="padding:8px;">{mensaje or 'Sin mensaje'}</td></tr>
        </table>
        <p style="margin-top:20px;">
            <a href="https://app.psicoatrading.online" style="display:inline-block;background-color:#2DD4BF;color:#0B1426;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:bold;">Ver en la app clínica →</a>
        </p>
    """
    return {
        "subject": f"📬 Nuevo contacto: {nombre} ({pais})",
        "html": get_base_template(content)
    }


# ============================================================
# SECUENCIA DE 5 EMAILS POST-TEST
# ============================================================

def template_test_email_1_bienvenida(nombre: str, test_tipo: str, perfil: str, dimensiones: dict) -> dict:
    """Email 1 — Inmediato: Bienvenida + resumen de perfil."""

    test_nombre = "Perfil Psicológico del Trader" if test_tipo == "A" else "Auditoría de Plan de Trading"

    # Construir resumen de dimensiones (los valores llegan como porcentaje 0-100)
    dimensiones_html = ""
    for dimension, puntaje in dimensiones.items():
        porcentaje = min(int(round(float(puntaje))), 100)
        color = "#22C55E" if porcentaje >= 70 else "#F59E0B" if porcentaje >= 40 else "#EF4444"
        dimensiones_html += f"""
            <div style="margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="font-size:13px;color:#475569;">{dimension}</span>
                    <span style="font-size:13px;font-weight:bold;color:{color};">{porcentaje}%</span>
                </div>
                <div style="background-color:#E2E8F0;border-radius:4px;height:8px;overflow:hidden;">
                    <div style="background-color:{color};height:100%;width:{porcentaje}%;border-radius:4px;"></div>
                </div>
            </div>
        """

    content = f"""
        <h2 style="color:#0B1426;margin:0 0 16px;">Hola {nombre},</h2>
        <p>Gracias por completar el <strong>{test_nombre}</strong>. Aquí tienes un resumen de tu evaluación:</p>

        <div style="background-color:#F0FDFA;border:1px solid #99F6E4;border-radius:8px;padding:20px;margin:20px 0;">
            <h3 style="color:#0B1426;margin:0 0 8px;">Tu perfil: {perfil}</h3>
            {dimensiones_html}
        </div>

        <p>Este resultado refleja tu estado psicológico actual frente al trading. No es una etiqueta permanente — es un punto de partida para tu desarrollo.</p>

        <p><strong>¿Qué sigue?</strong> En los próximos días te enviaremos contenido personalizado basado en tu perfil para ayudarte a fortalecer las áreas que más lo necesitan.</p>

        <p>Si quieres acelerar tu proceso, puedes agendar una <strong>sesión de valoración gratuita</strong> con uno de nuestros psicólogos especializados:</p>

        <p style="text-align:center;margin:24px 0;">
            <a href="https://psicoatrading.online/#contacto" style="display:inline-block;background-color:#2DD4BF;color:#0B1426;padding:12px 32px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:15px;">Agendar sesión gratuita →</a>
        </p>

        <p style="margin-top:24px;">Un saludo,<br><strong>Equipo PsicoaTrading</strong></p>
    """
    return {
        "subject": f"Tu resultado: {perfil} — PsicoaTrading",
        "html": get_base_template(content)
    }


def template_test_email_2_desafio(nombre: str, perfil: str, desafio_principal: str) -> dict:
    """Email 2 — Día 2: Profundización en el desafío principal."""

    # Contenido personalizado por desafío
    contenidos = {
        "control_emocional": {
            "titulo": "Control Emocional en el Trading",
            "parrafo1": "Tu evaluación reveló que el control emocional es un área de oportunidad importante. Esto es más común de lo que piensas — el 78% de los traders reportan que las emociones afectan negativamente su operativa.",
            "consejo": "Antes de cada sesión de trading, toma 2 minutos para hacer una pausa consciente. Cierra los ojos, respira profundamente 5 veces, y pregúntate: '¿Estoy operando desde la calma o desde la reactividad?' Si la respuesta es reactividad, no operes hasta que te sientas centrado.",
            "tecnica": "Técnica del Semáforo Emocional: Verde = operar con normalidad. Amarillo = reducir tamaño de posición a la mitad. Rojo = no operar. Evalúa tu color emocional antes de cada operación."
        },
        "disciplina": {
            "titulo": "Disciplina y Consistencia",
            "parrafo1": "La disciplina apareció como un área clave en tu perfil. La buena noticia: la disciplina no es un rasgo innato, es una habilidad que se entrena. Los traders más exitosos no tienen más fuerza de voluntad — tienen mejores sistemas.",
            "consejo": "Crea una checklist pre-trading de 5 puntos que debes cumplir antes de ejecutar cualquier operación. Si no cumples los 5, no ejecutas. Sin excepciones. Esto elimina la decisión emocional.",
            "tecnica": "Regla de los 3 strikes: Si rompes tu plan 3 veces en una sesión, cierras la plataforma por el resto del día. Sin negociación interna."
        },
        "gestion_riesgo": {
            "titulo": "Gestión del Riesgo",
            "parrafo1": "Tu perfil muestra que la gestión de riesgo necesita fortalecerse. Este es probablemente el factor más determinante entre los traders que sobreviven a largo plazo y los que no.",
            "consejo": "Establece una pérdida máxima diaria del 2% de tu cuenta. Cuando la alcances, paras. No hay 'recuperar lo perdido' — eso es la trampa psicológica que destruye cuentas.",
            "tecnica": "Antes de cada operación, calcula exactamente cuánto estás dispuesto a perder en esa operación (en dinero, no en pips). Si esa cifra te genera ansiedad, reduce el tamaño."
        },
        "default": {
            "titulo": "Tu Desarrollo como Trader",
            "parrafo1": "Tu evaluación mostró áreas específicas donde puedes crecer significativamente como trader. El primer paso siempre es la conciencia — y ese paso ya lo diste al completar el test.",
            "consejo": "Empieza un diario de trading emocional. Antes de cada sesión escribe: estado emocional (1-10), horas de sueño, nivel de estrés. Después de cada sesión: ¿seguí mi plan? ¿Qué emoción dominó? Esto crea el autoconocimiento que transforma tu operativa.",
            "tecnica": "Protocolo de pausa: entre que identificas una señal de entrada y ejecutas la operación, cuenta hasta 10. Si después de 10 segundos sigues convencido, ejecuta. Si dudas, no entres."
        },
    }

    data = contenidos.get(desafio_principal, contenidos["default"])

    content = f"""
        <h2 style="color:#0B1426;margin:0 0 16px;">Hola {nombre},</h2>
        <p>Ayer completaste tu evaluación y tu perfil fue: <strong>{perfil}</strong>. Hoy queremos profundizar en un área clave que detectamos: <strong>{data['titulo']}</strong>.</p>

        <p>{data['parrafo1']}</p>

        <div style="background-color:#FFF7ED;border-left:4px solid #F59E0B;padding:16px 20px;margin:20px 0;border-radius:0 8px 8px 0;">
            <h3 style="color:#92400E;margin:0 0 8px;font-size:14px;">💡 CONSEJO PRÁCTICO</h3>
            <p style="margin:0;color:#78350F;">{data['consejo']}</p>
        </div>

        <div style="background-color:#F0FDFA;border-left:4px solid #2DD4BF;padding:16px 20px;margin:20px 0;border-radius:0 8px 8px 0;">
            <h3 style="color:#0F766E;margin:0 0 8px;font-size:14px;">🛠 TÉCNICA PARA APLICAR HOY</h3>
            <p style="margin:0;color:#134E4A;">{data['tecnica']}</p>
        </div>

        <p>Estas técnicas son un primer paso. En una sesión de valoración podemos diseñar un programa personalizado basado en tu perfil específico.</p>

        <p style="margin-top:24px;">Un saludo,<br><strong>Equipo PsicoaTrading</strong></p>
    """
    return {
        "subject": f"Tu desafío principal: {data['titulo']} — PsicoaTrading",
        "html": get_base_template(content)
    }


def template_test_email_3_social_proof(nombre: str) -> dict:
    """Email 3 — Día 5: Caso de éxito / social proof."""
    content = f"""
        <h2 style="color:#0B1426;margin:0 0 16px;">Hola {nombre},</h2>
        <p>Queremos compartir contigo la historia de un trader que estuvo exactamente donde tú estás ahora.</p>

        <div style="background-color:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:24px;margin:20px 0;">
            <p style="font-style:italic;color:#475569;margin:0 0 12px;">"Llevaba 3 años haciendo trading y no entendía por qué repetía los mismos errores. Sabía la teoría, tenía una estrategia probada, pero cuando llegaba el momento de ejecutar, mis emociones tomaban el control. Después de trabajar con PsicoaTrading durante 8 semanas, finalmente entendí que mi problema no era técnico — era psicológico. Hoy opero con un plan y lo cumplo. Mis resultados cambiaron porque mi mentalidad cambió primero."</p>
            <p style="color:#0B1426;font-weight:bold;margin:0;">— Trader de futuros, 34 años, Colombia</p>
        </div>

        <p>El 90% de los traders que fracasan tienen un problema en común: <strong>no es falta de conocimiento técnico, es falta de gestión psicológica</strong>.</p>

        <p>La diferencia entre un trader que pierde y uno que es consistente rara vez está en la estrategia. Está en la capacidad de ejecutar esa estrategia bajo presión, sin que el miedo, la avaricia o la frustración saboteen las decisiones.</p>

        <p><strong>¿Te identificas?</strong> Una sesión de valoración gratuita de 45 minutos puede ser el primer paso para cambiar tu operativa:</p>

        <p style="text-align:center;margin:24px 0;">
            <a href="https://psicoatrading.online/#contacto" style="display:inline-block;background-color:#2DD4BF;color:#0B1426;padding:12px 32px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:15px;">Agendar mi sesión gratuita →</a>
        </p>

        <p style="margin-top:24px;">Un saludo,<br><strong>Equipo PsicoaTrading</strong></p>
    """
    return {
        "subject": "De repetir errores a operar con consistencia — PsicoaTrading",
        "html": get_base_template(content)
    }


def template_test_email_4_recurso(nombre: str) -> dict:
    """Email 4 — Día 7: Recurso gratuito."""
    content = f"""
        <h2 style="color:#0B1426;margin:0 0 16px;">Hola {nombre},</h2>
        <p>Hoy queremos dejarte un ejercicio concreto que puedes aplicar en tu próxima sesión de trading. Es una técnica que usamos con nuestros clientes y que produce resultados medibles desde la primera semana.</p>

        <div style="background-color:#0B1426;border-radius:8px;padding:24px;margin:20px 0;color:#F1F5F9;">
            <h3 style="color:#2DD4BF;margin:0 0 16px;">📋 Protocolo Pre-Trading de 5 Minutos</h3>

            <p style="margin:0 0 12px;"><strong style="color:#2DD4BF;">Minuto 1 — Escaneo corporal:</strong> Cierra los ojos. ¿Dónde sientes tensión? Mandíbula, hombros, estómago. Suelta esa tensión conscientemente.</p>

            <p style="margin:0 0 12px;"><strong style="color:#2DD4BF;">Minuto 2 — Check emocional:</strong> ¿Cómo me siento? Califica del 1 al 10: ansiedad, entusiasmo, frustración. Si alguna está por encima de 7, no operes.</p>

            <p style="margin:0 0 12px;"><strong style="color:#2DD4BF;">Minuto 3 — Revisión del plan:</strong> Lee tu plan de trading en voz alta. ¿Qué vas a buscar hoy? ¿Cuál es tu pérdida máxima? Si no tienes respuesta clara, no operes.</p>

            <p style="margin:0 0 12px;"><strong style="color:#2DD4BF;">Minuto 4 — Compromiso:</strong> Escribe en una nota: "Hoy voy a _______ y no voy a _______." Sé específico.</p>

            <p style="margin:0;"><strong style="color:#2DD4BF;">Minuto 5 — Respiración:</strong> 5 respiraciones profundas. Inhala 4 segundos, sostén 4 segundos, exhala 6 segundos. Ahora sí, abre tu plataforma.</p>
        </div>

        <p>Este protocolo parece simple, pero cambia completamente la forma en que enfrentas el mercado. <strong>Imprímelo y ponlo al lado de tu pantalla.</strong></p>

        <p>Si quieres un programa completo de entrenamiento psicológico diseñado para tu perfil específico, estamos aquí para ayudarte.</p>

        <p style="text-align:center;margin:24px 0;">
            <a href="https://psicoatrading.online/#contacto" style="display:inline-block;background-color:#2DD4BF;color:#0B1426;padding:12px 32px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:15px;">Hablar con un psicólogo →</a>
        </p>

        <p style="margin-top:24px;">Un saludo,<br><strong>Equipo PsicoaTrading</strong></p>
    """
    return {
        "subject": "Protocolo Pre-Trading de 5 minutos (descárgalo) — PsicoaTrading",
        "html": get_base_template(content)
    }


def template_test_email_5_ultima_invitacion(nombre: str, perfil: str) -> dict:
    """Email 5 — Día 10: Última invitación a agendar sesión."""
    content = f"""
        <h2 style="color:#0B1426;margin:0 0 16px;">Hola {nombre},</h2>
        <p>Han pasado 10 días desde que completaste tu evaluación y tu resultado fue: <strong>{perfil}</strong>.</p>

        <p>En estos días te compartimos consejos, técnicas y un protocolo práctico. Pero hay algo que ningún email puede hacer: <strong>un diagnóstico personalizado con un profesional que entiende tanto la psicología como el trading.</strong></p>

        <div style="background-color:#FEF2F2;border:1px solid #FECACA;border-radius:8px;padding:20px;margin:20px 0;">
            <h3 style="color:#991B1B;margin:0 0 8px;">La realidad es esta:</h3>
            <p style="color:#7F1D1D;margin:0;">El 90% de los traders pierden dinero. No porque no sepan qué hacer, sino porque no pueden controlar lo que sienten mientras lo hacen. Cada día que operas sin gestión psicológica es un día que refuerzas los patrones que te hacen perder.</p>
        </div>

        <p>Nuestra sesión de valoración es <strong>gratuita, dura 45 minutos, y es 100% online</strong>. No hay compromiso ni venta agresiva. Un psicólogo especializado analizará tu caso y te dirá exactamente en qué necesitas trabajar.</p>

        <p style="text-align:center;margin:24px 0;">
            <a href="https://psicoatrading.online/#contacto" style="display:inline-block;background-color:#EF4444;color:#ffffff;padding:14px 36px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:16px;">Quiero mi sesión gratuita →</a>
        </p>

        <p style="color:#64748B;font-size:13px;">Este es el último email de nuestra serie de bienvenida. Si en algún momento quieres retomar el contacto, siempre puedes escribirnos a admin@psicoatrading.online o visitarnos en <a href="https://psicoatrading.online" style="color:#2DD4BF;">psicoatrading.online</a>.</p>

        <p style="margin-top:24px;">Un saludo,<br><strong>Equipo PsicoaTrading</strong></p>
    """
    return {
        "subject": f"Última invitación: sesión gratuita para tu perfil ({perfil}) — PsicoaTrading",
        "html": get_base_template(content)
    }


def template_test_notificacion_admin(nombre: str, email: str, pais: str, test_tipo: str, perfil: str) -> dict:
    """Notificación al admin cuando alguien completa un test."""
    test_nombre = "Test A — Perfil Psicológico" if test_tipo == "A" else "Test B — Auditoría Plan de Trading"
    content = f"""
        <h2 style="color:#0B1426;margin:0 0 16px;">🧠 Nuevo test completado</h2>
        <table style="width:100%;border-collapse:collapse;">
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;width:130px;">Test:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;">{test_nombre}</td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;">Perfil:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;"><strong>{perfil}</strong></td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;">Nombre:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;">{nombre}</td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;">Email:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;">{email}</td></tr>
            <tr><td style="padding:8px;font-weight:bold;">País:</td><td style="padding:8px;">{pais}</td></tr>
        </table>
        <p style="margin-top:20px;">
            <a href="https://app.psicoatrading.online" style="display:inline-block;background-color:#2DD4BF;color:#0B1426;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:bold;">Ver en la app clínica →</a>
        </p>
    """
    return {
        "subject": f"🧠 Nuevo test: {nombre} → {perfil} ({pais})",
        "html": get_base_template(content)
    }

def template_pago_confirmacion(nombre: str, plan_nombre: str, precio_usd: float, username: str, temp_password: str = None) -> dict:
    acceso_html = ""
    if temp_password:
        acceso_html = f"""
        <div style="background-color:#F0FDFA;border:1px solid #99F6E4;border-radius:8px;padding:20px;margin:20px 0;">
            <h3 style="color:#0B1426;margin:0 0 12px;">🔐 Tus datos de acceso al portal</h3>
            <table style="width:100%;">
                <tr><td style="padding:4px 0;font-weight:bold;color:#475569;">Usuario:</td><td style="color:#0B1426;">{username}</td></tr>
                <tr><td style="padding:4px 0;font-weight:bold;color:#475569;">Contraseña temporal:</td><td style="color:#0B1426;font-family:monospace;font-size:16px;">{temp_password}</td></tr>
            </table>
            <p style="color:#64748B;font-size:12px;margin:12px 0 0;">Te recomendamos cambiar tu contraseña después del primer ingreso.</p>
        </div>
        """
    
    content = f"""
        <h2 style="color:#0B1426;margin:0 0 16px;">¡Pago confirmado, {nombre}!</h2>
        <p>Tu plan <strong>{plan_nombre}</strong> ha sido activado exitosamente.</p>
        
        <div style="background-color:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:16px;margin:16px 0;">
            <table style="width:100%;">
                <tr><td style="padding:4px 0;color:#64748B;">Plan:</td><td style="color:#0B1426;font-weight:bold;">{plan_nombre}</td></tr>
                <tr><td style="padding:4px 0;color:#64748B;">Monto:</td><td style="color:#0B1426;font-weight:bold;">USD ${precio_usd:,.0f}</td></tr>
                <tr><td style="padding:4px 0;color:#64748B;">Estado:</td><td style="color:#16A34A;font-weight:bold;">✓ Aprobado</td></tr>
            </table>
        </div>
        
        {acceso_html}
        
        <p style="text-align:center;margin:24px 0;">
            <a href="https://psicoatrading.online/app/" style="display:inline-block;background-color:#2DD4BF;color:#0B1426;padding:14px 36px;border-radius:8px;text-decoration:none;font-weight:bold;font-size:16px;">Acceder al portal →</a>
        </p>
        
        <p>Si tienes alguna pregunta, responde a este email o escríbenos por WhatsApp.</p>
        <p style="margin-top:24px;">Bienvenido/a al programa,<br><strong>Equipo PsicoaTrading</strong></p>
    """
    return {
        "subject": f"✅ Pago confirmado — {plan_nombre} — PsicoaTrading",
        "html": get_base_template(content)
    }

def template_pago_notificacion_admin(nombre: str, email: str, plan_nombre: str, precio_usd: float, pais: str, reference: str) -> dict:
    content = f"""
        <h2 style="color:#0B1426;margin:0 0 16px;">💰 Nuevo pago recibido</h2>
        <table style="width:100%;border-collapse:collapse;">
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;">Cliente:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;">{nombre}</td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;">Email:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;">{email}</td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;">País:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;">{pais}</td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;">Plan:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;"><strong>{plan_nombre}</strong></td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #E2E8F0;font-weight:bold;">Monto:</td><td style="padding:8px;border-bottom:1px solid #E2E8F0;">USD ${precio_usd:,.0f}</td></tr>
            <tr><td style="padding:8px;font-weight:bold;">Referencia:</td><td style="padding:8px;">{reference}</td></tr>
        </table>
        <p style="margin-top:20px;">
            <a href="https://psicoatrading.online/app/" style="display:inline-block;background-color:#2DD4BF;color:#0B1426;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:bold;">Ver en la app →</a>
        </p>
    """
    return {
        "subject": f"💰 Nuevo pago: {nombre} → {plan_nombre} (USD ${precio_usd:,.0f})",
        "html": get_base_template(content)
    }
