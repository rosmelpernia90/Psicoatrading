"""
PsicoaTrading â€” API Backend
FastAPI + MySQL + SendGrid
CRM ClÃ­nico con embudo de ventas automatizado
"""
import os
import json
import re
import secrets
from datetime import datetime, timedelta, date as date_type
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Boolean, DateTime, Date,
    JSON, Enum as SAEnum, ForeignKey, func, DECIMAL, or_
)
from sqlalchemy.orm import sessionmaker, Session, declarative_base, relationship
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

# ============================================
# CONFIG
# ============================================
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "psicoatrading_crm")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
JWT_SECRET = os.getenv("JWT_SECRET", "psicoatrading-secret-key-change-this")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "hola@psicoatrading.com")
SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "PsicoaTrading")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://psicoatrading.online")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# ============================================
# MODELS
# ============================================
class Psychologist(Base):
    __tablename__ = "psychologists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    specialty = Column(String(200), default="PsicologÃ­a del Trading")
    role = Column(SAEnum("admin", "psychologist"), default="psychologist")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(50))
    country = Column(String(100))
    trading_experience = Column(String(50))
    source = Column(String(100), default="web_test")
    status = Column(SAEnum("new", "contacted", "in_process", "converted", "lost"), default="new")
    funnel_stage = Column("stage", String(40), default="nuevo")
    last_contact_at = Column(DateTime, nullable=True)
    whatsapp = Column(String(40), nullable=True)
    assigned_psychologist_id = Column(Integer, ForeignKey("psychologists.id"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    test_results = relationship("TestResult", backref="lead")
    clinical_notes = relationship("ClinicalNote", backref="lead")
    sessions = relationship("SessionModel", backref="lead")


class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    test_type = Column(SAEnum("A", "B"), nullable=False)
    profile_name = Column(String(200), nullable=False)
    profile_code = Column(String(50), nullable=False)
    total_score = Column(DECIMAL(5, 2))
    answers_json = Column(JSON)
    completed_at = Column(DateTime, default=datetime.utcnow)
    dimensions = relationship("DimensionScore", backref="test_result")


class DimensionScore(Base):
    __tablename__ = "dimension_scores"
    id = Column(Integer, primary_key=True, index=True)
    test_result_id = Column(Integer, ForeignKey("test_results.id"), nullable=False)
    dimension_name = Column(String(100), nullable=False)
    dimension_code = Column(String(50), nullable=False)
    score = Column(DECIMAL(5, 2), nullable=False)
    max_score = Column(DECIMAL(5, 2), nullable=False)
    percentage = Column(DECIMAL(5, 2), nullable=False)


class EmailQueue(Base):
    __tablename__ = "email_queue"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    email_type = Column(String(50), nullable=False)
    sequence_number = Column(Integer, nullable=False)
    subject = Column(String(500))
    body_html = Column(Text)
    status = Column(SAEnum("pending", "sent", "failed"), default="pending")
    scheduled_at = Column(DateTime, nullable=False)
    sent_at = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class SessionModel(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    psychologist_id = Column(Integer, ForeignKey("psychologists.id"))
    session_type = Column(SAEnum("diagnostic", "follow_up", "advisory"), default="diagnostic")
    status = Column(SAEnum("scheduled", "completed", "cancelled", "no_show"), default="scheduled")
    scheduled_at = Column(DateTime)
    duration_minutes = Column(Integer, default=45)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ClinicalNote(Base):
    __tablename__ = "clinical_notes"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    psychologist_id = Column(Integer, ForeignKey("psychologists.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    note_type = Column(SAEnum("initial_assessment", "progress", "intervention", "discharge"), default="progress")
    content = Column(Text, nullable=False)
    is_private = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Client(Base):
    __tablename__ = "clients"
    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name          = Column(String(200), nullable=False)
    country       = Column(String(100))
    role          = Column(String(20), nullable=False, default="cliente")
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdminSetupToken(Base):
    __tablename__ = "admin_setup_tokens"
    id              = Column(Integer, primary_key=True, index=True)
    psychologist_id = Column(Integer, ForeignKey("psychologists.id"), nullable=False)
    token           = Column(String(128), unique=True, nullable=False, index=True)
    expires_at      = Column(DateTime, nullable=False)
    used_at         = Column(DateTime, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)


class PsicologoPaciente(Base):
    __tablename__ = "psicologo_paciente"
    id                   = Column(Integer, primary_key=True, index=True)
    psicologo_id         = Column(Integer, ForeignKey("psychologists.id"), nullable=False)
    paciente_id          = Column(Integer, ForeignKey("clients.id"), nullable=False)
    assigned_at          = Column(DateTime, default=datetime.utcnow)
    assigned_by_admin_id = Column(Integer, ForeignKey("psychologists.id"), nullable=True)
    is_active            = Column(Boolean, default=True)
    ended_at             = Column(DateTime, nullable=True)
    end_reason           = Column(Text, nullable=True)
    # Nota: la columna generada `active_paciente` existe en la BD para el
    # UNIQUE de "un psicÃ³logo activo por paciente"; no se mapea aquÃ­.


class PsicologoProfile(Base):
    __tablename__ = "psicologos_profile"
    psychologist_id     = Column(Integer, ForeignKey("psychologists.id"), primary_key=True)
    bio                 = Column(Text, nullable=True)
    especialidad        = Column(String(255), nullable=True)
    idiomas             = Column(String(255), nullable=True)
    max_pacientes       = Column(Integer, default=20)
    tarjeta_profesional = Column(String(100), nullable=True)
    esta_disponible     = Column(Boolean, default=True)
    created_at          = Column(DateTime, default=datetime.utcnow)
    updated_at          = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CambioPsicologoRequest(Base):
    __tablename__ = "cambio_psicologo_requests"
    id                    = Column(Integer, primary_key=True, index=True)
    paciente_id           = Column(Integer, ForeignKey("clients.id"), nullable=False)
    current_psicologo_id  = Column(Integer, ForeignKey("psychologists.id"), nullable=True)
    reason_category       = Column(String(50), nullable=False)
    reason_text           = Column(Text, nullable=True)
    share_reason_with_new = Column(Boolean, default=False)
    status                = Column(SAEnum("pendiente", "aprobada", "rechazada"), default="pendiente")
    resolved_by_admin_id  = Column(Integer, ForeignKey("psychologists.id"), nullable=True)
    resolved_at           = Column(DateTime, nullable=True)
    admin_notes           = Column(Text, nullable=True)
    created_at            = Column(DateTime, default=datetime.utcnow)


class CourseModule(Base):
    __tablename__ = "courses_modules"
    id            = Column(Integer, primary_key=True, index=True)
    module_number = Column(Integer, nullable=False, unique=True)  # 1-7
    title         = Column(String(200), nullable=False)
    content_md    = Column(Text)
    is_sequential = Column(Boolean, default=True)  # True: 1,2,3,7 | False: 4,5,6
    unlocks_diary_question_id = Column(Integer, nullable=True)  # FK lÃ³gico a diario (sin constraint por ahora)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    quizzes       = relationship("CourseQuiz", backref="module", order_by="CourseQuiz.question_order")


class CourseQuiz(Base):
    __tablename__ = "courses_quizzes"
    id             = Column(Integer, primary_key=True, index=True)
    module_id      = Column(Integer, ForeignKey("courses_modules.id"), nullable=False)
    question       = Column(Text, nullable=False)
    option_a       = Column(String(500))
    option_b       = Column(String(500))
    option_c       = Column(String(500))
    option_d       = Column(String(500))
    correct_option = Column(String(1), nullable=False)  # 'a','b','c','d'
    question_order = Column(Integer, default=1)


class CourseProgress(Base):
    __tablename__ = "courses_progress"
    id           = Column(Integer, primary_key=True, index=True)
    client_id    = Column(Integer, ForeignKey("clients.id"), nullable=False)
    module_id    = Column(Integer, ForeignKey("courses_modules.id"), nullable=False)
    status       = Column(String(20), default="locked")  # locked|available|in_progress|completed
    quiz_score   = Column(Integer, nullable=True)
    attempts     = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DiaryQuestion(Base):
    __tablename__ = "diary_questions"
    id                    = Column(Integer, primary_key=True, index=True)
    question_text         = Column(Text, nullable=False)
    unlocked_by_module_id = Column(Integer, ForeignKey("courses_modules.id"), nullable=True)
    is_active             = Column(Boolean, default=True)
    display_order         = Column(Integer, default=0)


class DiaryEntry(Base):
    __tablename__ = "diary_entries"
    id               = Column(Integer, primary_key=True, index=True)
    client_id        = Column(Integer, ForeignKey("clients.id"), nullable=False)
    entry_date       = Column(Date, nullable=False)
    traded_today     = Column(Boolean, default=False)
    financial_result = Column(DECIMAL(12, 2), nullable=True)
    emotional_score  = Column(Integer, nullable=False)
    free_notes       = Column(Text, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    answers          = relationship("DiaryEntryAnswer", backref="entry", cascade="all, delete-orphan")


class DiaryEntryAnswer(Base):
    __tablename__ = "diary_entry_answers"
    id          = Column(Integer, primary_key=True, index=True)
    entry_id    = Column(Integer, ForeignKey("diary_entries.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("diary_questions.id"), nullable=False)
    answer_text = Column(Text)


class LeadSubmission(Base):
    """
    Una fila por cada interaccion del visitante con un formulario publico.
    Permite que un mismo lead acumule N submissions (contacto + tests + compras...)
    y diferenciar el origen exacto de cada lead.
    """
    __tablename__ = "lead_submissions"
    id                  = Column(Integer, primary_key=True, index=True)
    lead_id             = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    source              = Column(SAEnum(
        "formulario_contacto",
        "formulario_agendar_sesion",
        "test_a_perfil_psicologico",
        "test_b_plan_trading",
        "newsletter_suscripcion",
        "compra_plan_trader_consciente",
        "compra_plan_asesoria_personalizada",
        "compra_plan_transformacion_total",
    ), nullable=False)
    # Datos comunes a cualquier formulario
    whatsapp            = Column(String(30), nullable=True)
    pais                = Column(String(50), nullable=True)
    # Formulario de contacto / agendar
    experiencia_trading = Column(String(50), nullable=True)
    principal_desafio   = Column(Text, nullable=True)
    intent              = Column(String(40), nullable=True)   # "informacion" | "agendar"
    # Tests
    test_a_score        = Column(Integer, nullable=True)
    test_a_perfil       = Column(String(100), nullable=True)
    test_b_score        = Column(Integer, nullable=True)
    test_b_perfil       = Column(String(100), nullable=True)
    test_respuestas     = Column(JSON, nullable=True)
    # Pagos (preparado para Bold/Stripe)
    plan_comprado       = Column(String(50), nullable=True)
    monto_pagado        = Column(DECIMAL(10, 2), nullable=True)
    moneda              = Column(String(3), nullable=True)
    pasarela            = Column(String(20), nullable=True)
    transaccion_id      = Column(String(100), nullable=True)
    # Body completo del POST por trazabilidad
    raw_data            = Column(JSON, nullable=True)
    created_at          = Column(DateTime, default=datetime.utcnow)


# ============================================
# SCHEMAS (Pydantic)
# ============================================
class TestResultSubmit(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    country: Optional[str] = None
    trading_experience: Optional[str] = None
    main_market: Optional[str] = None
    test_type: str
    profile_name: str
    profile_code: str
    total_score: float
    max_score: Optional[float] = None
    percentile: Optional[float] = None
    risk_level: Optional[str] = None
    answers: Optional[dict] = None
    dimensions: List[dict]


class ContactSubmit(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: Optional[str] = None
    notes: Optional[str] = None
    country: Optional[str] = None
    trading_experience: Optional[str] = None
    source: Optional[str] = "contact_form"


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    country: Optional[str] = None


class SetPasswordRequest(BaseModel):
    token: str
    password: str


class PsicologoProfileIn(BaseModel):
    bio: Optional[str] = None
    especialidad: Optional[str] = None
    idiomas: Optional[str] = None
    max_pacientes: Optional[int] = None
    tarjeta_profesional: Optional[str] = None
    esta_disponible: Optional[bool] = None


class AsignacionIn(BaseModel):
    paciente_id: int
    psicologo_id: int
    notes: Optional[str] = None


class EndAsignacionIn(BaseModel):
    end_reason: Optional[str] = None


class CambioRequestIn(BaseModel):
    reason_category: str
    reason_text: Optional[str] = None
    share_reason_with_new: bool = False


class AprobarCambioIn(BaseModel):
    nuevo_psicologo_id: int
    admin_notes: Optional[str] = None


class RechazarCambioIn(BaseModel):
    admin_notes: Optional[str] = None


class AdminUserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # admin | psychologist | cliente
    country: Optional[str] = None


class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None  # opcional: solo si se quiere cambiar
    country: Optional[str] = None


class QuizAnswer(BaseModel):
    question_id: int
    answer: str  # 'a','b','c','d'


class CompleteModuleRequest(BaseModel):
    quiz_answers: List[QuizAnswer]


class DiaryAnswerIn(BaseModel):
    question_id: int
    answer_text: str


class DiaryEntryCreate(BaseModel):
    entry_date: Optional[str] = None        # YYYY-MM-DD, defaults to today
    traded_today: bool
    financial_result: Optional[float] = None
    emotional_score: int                    # 1-5
    free_notes: Optional[str] = None
    answers: Optional[List[DiaryAnswerIn]] = []


class DiaryEntryUpdate(BaseModel):
    traded_today: Optional[bool] = None
    financial_result: Optional[float] = None
    emotional_score: Optional[int] = None
    free_notes: Optional[str] = None
    answers: Optional[List[DiaryAnswerIn]] = None


class ClinicalNoteCreate(BaseModel):
    lead_id: int
    session_id: Optional[int] = None
    note_type: str = "progress"
    content: str


class SessionCreate(BaseModel):
    lead_id: int
    session_type: str = "diagnostic"
    scheduled_at: str
    duration_minutes: int = 45
    notes: Optional[str] = None


# ============================================
# SCHEMAS - formularios publicos (lead_submissions)
# ============================================
class FormContactSubmit(BaseModel):
    name: str
    email: EmailStr
    whatsapp: Optional[str] = None
    pais: Optional[str] = None
    experiencia_trading: Optional[str] = None
    principal_desafio: Optional[str] = None
    intent: Optional[str] = None   # "informacion" | "agendar"


class FormTestSubmit(BaseModel):
    name: str
    email: EmailStr
    pais: Optional[str] = None
    experiencia_trading: Optional[str] = None
    main_market: Optional[str] = None
    test_type: str                       # "A" | "B" - el endpoint que recibe valida
    score: int
    perfil: str
    profile_code: Optional[str] = None
    respuestas: Optional[dict] = None
    dimensions: Optional[List[dict]] = None
    max_score: Optional[float] = None
    percentile: Optional[float] = None


class FormNewsletterSubmit(BaseModel):
    email: EmailStr
    name: Optional[str] = None


# ============================================
# DEPENDENCIES
# ============================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token invÃ¡lido")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invÃ¡lido o expirado")


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def require_admin(payload: dict = Depends(verify_token)):
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acceso solo para administradores")
    return payload


def require_psychologist_or_admin(payload: dict = Depends(verify_token)):
    role = payload.get("role")
    if role not in ("admin", "psychologist"):
        raise HTTPException(status_code=403, detail="Acceso solo para el equipo clinico")
    return payload


# ============================================
# EMAIL SEQUENCES
# ============================================
EMAIL_SEQUENCES = [
    {"type": "welcome", "seq": 1, "delay_hours": 0,
     "subject": "Tu perfil psicolÃ³gico de trader estÃ¡ listo ðŸ§ ",
     "template": "Hola {name}, gracias por completar el test. Tu perfil es: {profile}. En los prÃ³ximos dÃ­as te enviaremos contenido personalizado para mejorar tu psicologÃ­a de trading."},
    {"type": "deep_dive", "seq": 2, "delay_hours": 48,
     "subject": "Tu principal desafÃ­o como trader (y cÃ³mo superarlo)",
     "template": "Hola {name}, basados en tu perfil ({profile}), tu principal desafÃ­o es el control emocional durante las operaciones. AquÃ­ te explicamos cÃ³mo trabajamos este aspecto..."},
    {"type": "social_proof", "seq": 3, "delay_hours": 120,
     "subject": "CÃ³mo Juan pasÃ³ de perder 3 fondeos a ser consistente",
     "template": "Hola {name}, queremos compartirte el caso de un trader que tenÃ­a un perfil similar al tuyo..."},
    {"type": "free_resource", "seq": 4, "delay_hours": 168,
     "subject": "Regalo: GuÃ­a de autoregulaciÃ³n emocional para traders ðŸ“–",
     "template": "Hola {name}, como parte de nuestro compromiso con tu desarrollo, te compartimos nuestra guÃ­a gratuita de autoregulaciÃ³n emocional..."},
    {"type": "last_call", "seq": 5, "delay_hours": 240,
     "subject": "Tu sesiÃ³n diagnÃ³stico gratuita te espera (Ãºltimos cupos)",
     "template": "Hola {name}, hace 10 dÃ­as completaste tu test y tu perfil revelÃ³ Ã¡reas importantes de trabajo. Â¿Ya agendaste tu sesiÃ³n diagnÃ³stico gratuita? Los cupos son limitados..."},
]


def schedule_email_sequence(db: Session, lead_id: int, lead_name: str, profile_name: str):
    now = datetime.utcnow()
    for seq in EMAIL_SEQUENCES:
        body = seq["template"].format(name=lead_name, profile=profile_name)
        email = EmailQueue(
            lead_id=lead_id,
            email_type=seq["type"],
            sequence_number=seq["seq"],
            subject=seq["subject"],
            body_html=body,
            status="pending",
            scheduled_at=now + timedelta(hours=seq["delay_hours"])
        )
        db.add(email)
    db.commit()


def send_diary_reminders():
    """Send email to clients with 3+ days without a diary entry (runs daily)."""
    if not SENDGRID_API_KEY:
        return
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        today = date_type.today()
        three_days_ago = today - timedelta(days=3)
        db = SessionLocal()
        clients = db.query(Client).filter(Client.is_active == True, Client.role == "cliente").all()
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        for client in clients:
            last = db.query(DiaryEntry)\
                .filter(DiaryEntry.client_id == client.id)\
                .order_by(DiaryEntry.entry_date.desc()).first()
            last_date = last.entry_date if last else (today - timedelta(days=100))
            if (today - last_date).days == 3:
                msg = Mail(
                    from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
                    to_emails=client.email,
                    subject="Tu diario de trading te espera ðŸ“–",
                    html_content=(
                        f"<p>Hola {client.name},</p>"
                        f"<p>Llevas 3 dÃ­as sin escribir en tu diario de trading. "
                        f"Tomarte 5 minutos para reflexionar sobre tus operaciones "
                        f"puede marcar una gran diferencia en tu desarrollo.</p>"
                        f"<p><a href='https://app.psicoatrading.online'>Escribir hoy â†’</a></p>"
                    )
                )
                try:
                    sg.send(msg)
                except Exception as e:
                    print(f"Diary reminder error for {client.email}: {e}")
        db.close()
    except Exception as e:
        print(f"Diary reminder scheduler error: {e}")


def send_pending_emails():
    """Called by APScheduler every 5 minutes"""
    if not SENDGRID_API_KEY:
        return
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        db = SessionLocal()
        pending = db.query(EmailQueue).filter(
            EmailQueue.status == "pending",
            EmailQueue.scheduled_at <= datetime.utcnow()
        ).limit(10).all()
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        for email_item in pending:
            lead = db.query(Lead).filter(Lead.id == email_item.lead_id).first()
            if not lead:
                email_item.status = "failed"
                email_item.error_message = "Lead not found"
                continue
            message = Mail(
                from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
                to_emails=lead.email,
                subject=email_item.subject,
                html_content=email_item.body_html
            )
            try:
                sg.send(message)
                email_item.status = "sent"
                email_item.sent_at = datetime.utcnow()
            except Exception as e:
                email_item.status = "failed"
                email_item.error_message = str(e)
        db.commit()
        db.close()
    except Exception as e:
        print(f"Email scheduler error: {e}")


# ============================================
# APP LIFESPAN
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_pending_emails, "interval", minutes=5)
    scheduler.add_job(send_diary_reminders, "interval", hours=24)
    scheduler.start()
    print("âœ… PsicoaTrading API running â€” email scheduler active")
    yield
    scheduler.shutdown()


# ============================================
# APP
# ============================================
app = FastAPI(
    title="PsicoaTrading API",
    description="CRM ClÃ­nico â€” PsicologÃ­a aplicada al Trading",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://psicoatrading.online",
        "https://app.psicoatrading.online",
        "https://psicoatrading.com",
        "https://app.psicoatrading.com",
        "http://psicoatrading.online",
        "http://app.psicoatrading.online",
        "http://psicoatrading.com",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5177",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# ENDPOINTS PÃšBLICOS
# ============================================
@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "PsicoaTrading API", "version": "1.0.0"}


@app.post("/api/test-results")
def submit_test_result(data: TestResultSubmit, db: Session = Depends(get_db)):
    # Create or find lead
    lead = db.query(Lead).filter(Lead.email == data.email).first()
    if not lead:
        lead = Lead(
            name=data.name,
            email=data.email,
            phone=data.phone,
            country=data.country,
            trading_experience=data.trading_experience,
            source="web_test",
            funnel_stage="test_completed",
        )
        db.add(lead)
        db.flush()
        print(f"[LEAD] Nuevo lead por test: {data.email} perfil={data.profile_name}")
    else:
        lead.name = data.name
        lead.funnel_stage = "test_completed"
        if data.phone: lead.phone = data.phone
        if data.country: lead.country = data.country
        if data.trading_experience: lead.trading_experience = data.trading_experience
        print(f"[LEAD] Test completado por lead existente: {data.email}")

    # Save test result
    test_result = TestResult(
        lead_id=lead.id,
        test_type=data.test_type,
        profile_name=data.profile_name,
        profile_code=data.profile_code,
        total_score=data.total_score,
        answers_json=data.answers
    )
    db.add(test_result)
    db.flush()

    # Save dimension scores
    for dim in data.dimensions:
        sc = float(dim.get("score", 0))
        mx = float(dim.get("max_score", dim.get("max", 100)) or 100)
        pct = dim.get("percentage") or (round(sc / mx * 100, 1) if mx else 0)
        ds = DimensionScore(
            test_result_id=test_result.id,
            dimension_name=dim.get("name", dim.get("dimension_code", "")),
            dimension_code=dim.get("code", dim.get("dimension_code", "")),
            score=sc,
            max_score=mx,
            percentage=pct
        )
        db.add(ds)

    # Registrar tambien en lead_submissions (origen exacto del lead)
    src_map = {"A": "test_a_perfil_psicologico", "B": "test_b_plan_trading"}
    sub_kwargs = {
        "lead_id": lead.id,
        "source": src_map.get(data.test_type, "test_a_perfil_psicologico"),
        "pais": data.country,
        "experiencia_trading": data.trading_experience,
        "test_respuestas": data.answers,
        "raw_data": data.model_dump() if hasattr(data, "model_dump") else None,
    }
    if data.test_type == "A":
        sub_kwargs["test_a_score"]  = int(data.total_score) if data.total_score else None
        sub_kwargs["test_a_perfil"] = data.profile_name
    else:
        sub_kwargs["test_b_score"]  = int(data.total_score) if data.total_score else None
        sub_kwargs["test_b_perfil"] = data.profile_name
    db.add(LeadSubmission(**sub_kwargs))

    db.commit()

    # Schedule email sequence
    schedule_email_sequence(db, lead.id, lead.name, data.profile_name)

    return {
        "success": True,
        "lead_id": lead.id,
        "test_result_id": test_result.id,
        "message": "Resultado guardado. Revisa tu email para mas informacion."
    }


@app.post("/api/contact")
def submit_contact(data: ContactSubmit, db: Session = Depends(get_db)):
    """Alias retro-compat: redirige al nuevo /api/forms/contact pero acepta el schema viejo."""
    wa = getattr(data, "phone", None)
    notes_text = data.notes or data.message
    payload = FormContactSubmit(
        name=data.name, email=data.email,
        whatsapp=wa, pais=data.country,
        experiencia_trading=data.trading_experience,
        principal_desafio=notes_text,
        intent=None,
    )
    return form_contact(payload, db)


# ============================================
# ENDPOINTS PUBLICOS - FORMULARIOS (lead_submissions)
# Cada formulario publico tiene su endpoint propio para registrar
# correctamente el origen del lead en lead_submissions.
# ============================================
def _get_or_create_lead(db: Session, *, name: str, email: str, whatsapp: Optional[str] = None,
                       country: Optional[str] = None, trading_experience: Optional[str] = None,
                       initial_source: str = "web_form",
                       initial_stage: str = "nuevo") -> "Lead":
    """Busca un lead por email; si no existe lo crea. Devuelve el lead persistido (con id)."""
    lead = db.query(Lead).filter(Lead.email == email).first()
    if not lead:
        lead = Lead(
            name=name, email=email,
            whatsapp=whatsapp, phone=whatsapp,   # `phone` queda como espejo por retro-compat
            country=country,
            trading_experience=trading_experience,
            source=initial_source,
            funnel_stage=initial_stage,
        )
        db.add(lead)
        db.flush()
        print(f"[LEAD] Nuevo lead capturado: {email} fuente={initial_source}")
    else:
        # Enriquecer campos vacios sin pisar lo existente
        if name and not lead.name: lead.name = name
        if whatsapp:
            if not lead.whatsapp: lead.whatsapp = whatsapp
            if not lead.phone:    lead.phone    = whatsapp
        if country and not lead.country: lead.country = country
        if trading_experience and not lead.trading_experience:
            lead.trading_experience = trading_experience
        lead.last_contact_at = datetime.utcnow()
    return lead


@app.post("/api/forms/contact")
def form_contact(data: FormContactSubmit, db: Session = Depends(get_db)):
    """Formulario publico de Contacto / Agendar Sesion. Distingue intencion via `intent`."""
    lead = _get_or_create_lead(
        db, name=data.name, email=data.email, whatsapp=data.whatsapp,
        country=data.pais, trading_experience=data.experiencia_trading,
        initial_source="formulario_contacto",
    )
    # Decidir el source segun el intent
    src = "formulario_agendar_sesion" if (data.intent == "agendar") else "formulario_contacto"
    sub = LeadSubmission(
        lead_id=lead.id, source=src,
        whatsapp=data.whatsapp, pais=data.pais,
        experiencia_trading=data.experiencia_trading,
        principal_desafio=data.principal_desafio,
        intent=data.intent,
        raw_data=data.model_dump(),
    )
    db.add(sub)
    db.commit()
    return {"success": True, "lead_id": lead.id, "submission_id": sub.id,
            "message": "Recibimos tu solicitud. Te contactaremos pronto."}


@app.post("/api/forms/test-a")
def form_test_a(data: FormTestSubmit, db: Session = Depends(get_db)):
    return _submit_test(db, data, expected_type="A",
                       source="test_a_perfil_psicologico")


@app.post("/api/forms/test-b")
def form_test_b(data: FormTestSubmit, db: Session = Depends(get_db)):
    return _submit_test(db, data, expected_type="B",
                       source="test_b_plan_trading")


def _submit_test(db: Session, data: FormTestSubmit, *, expected_type: str, source: str):
    if data.test_type.upper() != expected_type:
        raise HTTPException(status_code=400,
            detail=f"test_type debe ser '{expected_type}' en este endpoint")
    lead = _get_or_create_lead(
        db, name=data.name, email=data.email,
        country=data.pais, trading_experience=data.experiencia_trading,
        initial_source="web_test",
        initial_stage="test_completed",
    )
    if lead.funnel_stage in (None, "nuevo"):
        lead.funnel_stage = "test_completed"

    # Tambien creamos el TestResult clasico (mantiene compatibilidad con el panel actual)
    test_result = TestResult(
        lead_id=lead.id, test_type=expected_type,
        profile_name=data.perfil, profile_code=data.profile_code or "",
        total_score=data.score, answers_json=data.respuestas,
    )
    db.add(test_result)
    db.flush()
    for dim in (data.dimensions or []):
        sc = float(dim.get("score", 0))
        mx = float(dim.get("max_score", dim.get("max", 100)) or 100)
        pct = dim.get("percentage") or (round(sc / mx * 100, 1) if mx else 0)
        db.add(DimensionScore(
            test_result_id=test_result.id,
            dimension_name=dim.get("name", dim.get("dimension_code", "")),
            dimension_code=dim.get("code", dim.get("dimension_code", "")),
            score=sc, max_score=mx, percentage=pct,
        ))

    # Registrar tambien en lead_submissions
    sub_kwargs = {
        "lead_id": lead.id, "source": source,
        "pais": data.pais, "experiencia_trading": data.experiencia_trading,
        "test_respuestas": data.respuestas,
        "raw_data": data.model_dump(),
    }
    if expected_type == "A":
        sub_kwargs["test_a_score"]  = data.score
        sub_kwargs["test_a_perfil"] = data.perfil
    else:
        sub_kwargs["test_b_score"]  = data.score
        sub_kwargs["test_b_perfil"] = data.perfil
    sub = LeadSubmission(**sub_kwargs)
    db.add(sub)
    db.commit()

    # Disparar secuencia de emails (preserva el comportamiento actual)
    schedule_email_sequence(db, lead.id, lead.name, data.perfil)

    return {"success": True, "lead_id": lead.id, "submission_id": sub.id,
            "test_result_id": test_result.id,
            "message": "Resultado guardado. Revisa tu email para mas informacion."}


@app.post("/api/forms/newsletter")
def form_newsletter(data: FormNewsletterSubmit, db: Session = Depends(get_db)):
    lead = _get_or_create_lead(
        db, name=(data.name or "(suscriptor)"), email=data.email,
        initial_source="newsletter",
    )
    sub = LeadSubmission(
        lead_id=lead.id, source="newsletter_suscripcion",
        raw_data=data.model_dump(),
    )
    db.add(sub)
    db.commit()
    return {"success": True, "lead_id": lead.id, "submission_id": sub.id,
            "message": "Suscripcion confirmada."}


# ============================================
# ENDPOINTS AUTENTICADOS
# ============================================
@app.post("/api/auth/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # 1. PsicÃ³logos y admins
    psych = db.query(Psychologist).filter(Psychologist.email == data.email).first()
    if psych and pwd_context.verify(data.password, psych.password_hash):
        if not psych.is_active:
            raise HTTPException(status_code=403, detail="Cuenta desactivada")
        token = create_token({"sub": psych.email, "name": psych.name, "role": psych.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": psych.id, "name": psych.name, "email": psych.email, "role": psych.role}
        }

    # 2. Clientes
    client = db.query(Client).filter(Client.email == data.email).first()
    if client and pwd_context.verify(data.password, client.password_hash):
        if not client.is_active:
            raise HTTPException(status_code=403, detail="Cuenta desactivada")
        token = create_token({"sub": client.email, "name": client.name, "role": client.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": client.id, "name": client.name, "email": client.email, "role": client.role}
        }

    raise HTTPException(status_code=401, detail="Credenciales incorrectas")


@app.post("/api/auth/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(Psychologist).filter(Psychologist.email == data.email).first():
        raise HTTPException(status_code=400, detail="El email ya estÃ¡ registrado")
    if db.query(Client).filter(Client.email == data.email).first():
        raise HTTPException(status_code=400, detail="El email ya estÃ¡ registrado")
    client = Client(
        email=data.email,
        password_hash=pwd_context.hash(data.password),
        name=data.name,
        country=data.country,
        role="cliente"
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    token = create_token({"sub": client.email, "name": client.name, "role": client.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": client.id, "name": client.name, "email": client.email, "role": client.role}
    }


# ============================================
# SETUP / RECUPERACIÃ“N DE CONTRASEÃ‘A DEL ADMIN
# ============================================
ADMIN_EMAIL = "psicoatrading@gmail.com"
PASSWORD_UNSET = "!"  # placeholder: contraseÃ±a sin establecer

def validate_password_strength(pw: str):
    """MÃ­nimo 12 caracteres, mayÃºscula, minÃºscula, nÃºmero y sÃ­mbolo."""
    if len(pw) < 12:
        return "La contraseÃ±a debe tener al menos 12 caracteres"
    if not re.search(r"[A-Z]", pw):
        return "Debe incluir al menos una mayÃºscula"
    if not re.search(r"[a-z]", pw):
        return "Debe incluir al menos una minÃºscula"
    if not re.search(r"[0-9]", pw):
        return "Debe incluir al menos un nÃºmero"
    if not re.search(r"[^A-Za-z0-9]", pw):
        return "Debe incluir al menos un sÃ­mbolo"
    return None


def _generate_admin_setup_token(db: Session, admin: "Psychologist") -> str:
    """Crea y persiste un token de setup (24h) para un admin."""
    token = secrets.token_urlsafe(32)
    db.add(AdminSetupToken(
        psychologist_id=admin.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    ))
    db.commit()
    return token


@app.get("/api/auth/setup-status")
def setup_status(db: Session = Depends(get_db)):
    """Indica si el admin necesita configurar su contraseÃ±a."""
    admin = db.query(Psychologist).filter(Psychologist.role == "admin").first()
    needs = (admin is None) or (admin.password_hash in (None, "", PASSWORD_UNSET))
    return {"needs_setup": needs}


@app.post("/api/auth/setup-admin")
def setup_admin(db: Session = Depends(get_db)):
    """
    Setup inicial del admin (una sola vez). Crea psicoatrading@gmail.com si
    no existe y genera un link para establecer contraseÃ±a.
    Si el admin YA tiene contraseÃ±a usable â†’ 403 (no permitir reset pÃºblico).
    """
    admin = db.query(Psychologist).filter(Psychologist.role == "admin").first()
    if admin and admin.password_hash not in (None, "", PASSWORD_UNSET):
        raise HTTPException(status_code=403, detail="El administrador ya estÃ¡ configurado")

    if not admin:
        admin = Psychologist(
            name="Administrador", email=ADMIN_EMAIL, role="admin",
            password_hash=PASSWORD_UNSET, is_active=True,
        )
        db.add(admin); db.flush()

    token = _generate_admin_setup_token(db, admin)
    setup_url = f"{FRONTEND_URL}/app/setup-password.html?token={token}"

    if SENDGRID_API_KEY:
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            SendGridAPIClient(SENDGRID_API_KEY).send(Mail(
                from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
                to_emails=admin.email,
                subject="Configura tu contraseÃ±a de administrador Â· PsicoaTrading",
                html_content=f"<p>Para establecer tu contraseÃ±a de administrador, abre este enlace (vÃ¡lido 24h):</p><p><a href='{setup_url}'>{setup_url}</a></p>",
            ))
            return {"sent": True, "email": admin.email}
        except Exception as e:
            print(f"setup-admin email error: {e}")
    # Modo puente: sin proveedor de email configurado
    return {"sent": False, "setup_url": setup_url,
            "note": "Email no configurado. Usa este link (vÃ¡lido 24h) para establecer la contraseÃ±a."}


@app.post("/api/auth/set-password")
def set_password(data: SetPasswordRequest, db: Session = Depends(get_db)):
    """Establece la contraseÃ±a usando un token de setup vÃ¡lido."""
    rec = db.query(AdminSetupToken).filter(AdminSetupToken.token == data.token).first()
    if not rec:
        raise HTTPException(status_code=400, detail="Token invÃ¡lido")
    if rec.used_at is not None:
        raise HTTPException(status_code=400, detail="Este enlace ya fue usado")
    if rec.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="El enlace expirÃ³. Solicita uno nuevo.")

    err = validate_password_strength(data.password)
    if err:
        raise HTTPException(status_code=400, detail=err)

    admin = db.query(Psychologist).filter(Psychologist.id == rec.psychologist_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    admin.password_hash = pwd_context.hash(data.password)
    rec.used_at = datetime.utcnow()
    db.commit()
    return {"success": True, "email": admin.email}


@app.get("/api/dashboard/stats")
def dashboard_stats(payload: dict = Depends(require_admin), db: Session = Depends(get_db)):
    total_leads = db.query(func.count(Lead.id)).scalar() or 0
    new_leads = db.query(func.count(Lead.id)).filter(Lead.status == "new").scalar() or 0
    converted = db.query(func.count(Lead.id)).filter(Lead.status == "converted").scalar() or 0
    total_tests = db.query(func.count(TestResult.id)).scalar() or 0
    tests_a = db.query(func.count(TestResult.id)).filter(TestResult.test_type == "A").scalar() or 0
    tests_b = db.query(func.count(TestResult.id)).filter(TestResult.test_type == "B").scalar() or 0

    # Alertas clinicas: tests cuyo promedio de dimensiones esta en rangos de riesgo
    # danger (<=30%) -> requieren atencion; warning (31-50%) -> seguimiento
    test_avgs = db.query(
        DimensionScore.test_result_id,
        func.avg(DimensionScore.percentage).label("avg_pct")
    ).group_by(DimensionScore.test_result_id).all()
    alerts_danger = sum(1 for _, p in test_avgs if p is not None and float(p) <= 30)
    alerts_warning = sum(1 for _, p in test_avgs if p is not None and 30 < float(p) <= 50)

    # Percentil promedio (promedio global de percentages de dimensiones)
    avg_pct_raw = db.query(func.avg(DimensionScore.percentage)).scalar()
    avg_percentile = round(float(avg_pct_raw), 1) if avg_pct_raw is not None else 0

    # Sesiones agendadas futuras
    pending_sessions = db.query(func.count(SessionModel.id)).filter(
        SessionModel.status == "scheduled",
        SessionModel.scheduled_at >= datetime.utcnow()
    ).scalar() or 0

    # Emails
    pending_emails = db.query(func.count(EmailQueue.id)).filter(EmailQueue.status == "pending").scalar() or 0
    sent_emails = db.query(func.count(EmailQueue.id)).filter(EmailQueue.status == "sent").scalar() or 0

    # Leads ultimos 7 dias
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_leads = db.query(func.count(Lead.id)).filter(Lead.created_at >= week_ago).scalar() or 0

    # Distribucion por perfil (top 10)
    profile_rows = db.query(
        TestResult.profile_name,
        func.count(TestResult.id).label("count")
    ).group_by(TestResult.profile_name).order_by(func.count(TestResult.id).desc()).limit(10).all()
    profile_distribution = [{"name": name or "(sin perfil)", "count": count} for name, count in profile_rows]

    # Distribucion por etapa del funnel (columna BD: stage)
    funnel_rows = db.query(
        Lead.funnel_stage,
        func.count(Lead.id).label("count")
    ).group_by(Lead.funnel_stage).all()
    funnel_distribution = [{"stage": stage or "nuevo", "count": count} for stage, count in funnel_rows]

    return {
        # Metricas principales
        "total_leads": total_leads,
        "new_leads": new_leads,
        "converted": converted,
        "conversion_rate": round((converted / total_leads * 100), 1) if total_leads > 0 else 0,
        "total_tests": total_tests,
        "tests_a": tests_a,
        "tests_b": tests_b,
        "alerts_danger": alerts_danger,
        "alerts_warning": alerts_warning,
        "avg_percentile": avg_percentile,
        "pending_sessions": pending_sessions,
        "emails_sent": sent_emails,
        "emails_pending": pending_emails,
        "recent_leads_7d": recent_leads,
        # Distribuciones
        "profile_distribution": profile_distribution,
        "funnel_distribution": funnel_distribution,
        # Aliases retro-compat (por si algun consumidor viejo los lee)
        "pending_emails": pending_emails,
        "sent_emails": sent_emails,
        "upcoming_sessions": pending_sessions,
    }


@app.get("/api/leads")
def list_leads(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    source: Optional[str] = None,           # filtro por origen (lead_submissions.source)
    country: Optional[str] = None,          # filtro por pais
    funnel_stage: Optional[str] = None,     # filtro por etapa
    payload: dict = Depends(require_psychologist_or_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Lead)
    if status:       query = query.filter(Lead.status == status)
    if country:      query = query.filter(Lead.country == country)
    if funnel_stage: query = query.filter(Lead.funnel_stage == funnel_stage)
    if source:
        # Filtro por origen: lead que tenga al menos una submission con ese source
        query = query.filter(Lead.id.in_(
            db.query(LeadSubmission.lead_id).filter(LeadSubmission.source == source)
        ))
    if search:
        query = query.filter(
            (Lead.name.ilike(f"%{search}%")) | (Lead.email.ilike(f"%{search}%"))
        )
    total = query.count()
    leads = query.order_by(Lead.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    # Pre-cargar latest_source y submissions_count para evitar N+1
    lead_ids = [l.id for l in leads]
    submissions_meta = {}
    if lead_ids:
        # Cuenta por lead
        for lid, n in db.query(LeadSubmission.lead_id, func.count(LeadSubmission.id))\
                       .filter(LeadSubmission.lead_id.in_(lead_ids))\
                       .group_by(LeadSubmission.lead_id).all():
            submissions_meta.setdefault(lid, {})["count"] = n
        # Source mas reciente por lead (subquery: max(created_at))
        latest = db.query(LeadSubmission.lead_id, LeadSubmission.source, LeadSubmission.created_at)\
                   .filter(LeadSubmission.lead_id.in_(lead_ids))\
                   .order_by(LeadSubmission.lead_id, LeadSubmission.created_at.desc())\
                   .all()
        for lid, src, _ in latest:
            if "latest_source" not in submissions_meta.setdefault(lid, {}):
                submissions_meta[lid]["latest_source"] = src

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "leads": [
            {
                "id": l.id, "name": l.name, "email": l.email, "phone": l.phone,
                "whatsapp": l.whatsapp,
                "country": l.country, "status": l.status, "source": l.source,
                "funnel_stage": l.funnel_stage or "nuevo",
                "trading_experience": l.trading_experience,
                "tests_count": len(l.test_results),
                "submissions_count": submissions_meta.get(l.id, {}).get("count", 0),
                "latest_source": submissions_meta.get(l.id, {}).get("latest_source"),
                "created_at": l.created_at.isoformat() if l.created_at else None
            }
            for l in leads
        ]
    }


@app.get("/api/forms/sources")
def list_form_sources(payload: dict = Depends(require_psychologist_or_admin), db: Session = Depends(get_db)):
    """Lista los origenes (sources) disponibles para el dropdown del filtro."""
    rows = db.query(LeadSubmission.source, func.count(LeadSubmission.id))\
             .group_by(LeadSubmission.source).all()
    return {"sources": [{"value": s, "count": n} for s, n in rows]}


@app.get("/api/test-results-list")
def list_test_results(
    test_type: Optional[str] = None,        # 'A' | 'B'
    profile: Optional[str] = None,          # profile_name exacto
    country: Optional[str] = None,
    date_from: Optional[str] = None,        # ISO YYYY-MM-DD
    date_to: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    payload: dict = Depends(require_psychologist_or_admin),
    db: Session = Depends(get_db),
):
    """Lista completa de tests realizados con info del lead. Sirve a la seccion
    'Resultados de Tests' del panel admin + KPIs."""
    query = db.query(TestResult, Lead).join(Lead, Lead.id == TestResult.lead_id)
    if test_type:
        query = query.filter(TestResult.test_type == test_type.upper())
    if profile:
        query = query.filter(TestResult.profile_name == profile)
    if country:
        query = query.filter(Lead.country == country)
    if date_from:
        try: query = query.filter(TestResult.completed_at >= datetime.fromisoformat(date_from))
        except Exception: pass
    if date_to:
        try: query = query.filter(TestResult.completed_at <= datetime.fromisoformat(date_to + "T23:59:59"))
        except Exception: pass

    total = query.count()
    rows = query.order_by(TestResult.completed_at.desc()).limit(limit).all()

    # KPIs: globales (no filtrados por los params) para tener referencia estable
    g_total  = db.query(func.count(TestResult.id)).scalar() or 0
    g_test_a = db.query(func.count(TestResult.id)).filter(TestResult.test_type == "A").scalar() or 0
    g_test_b = db.query(func.count(TestResult.id)).filter(TestResult.test_type == "B").scalar() or 0
    # Top 3 perfiles mas comunes
    top_profiles_rows = db.query(TestResult.profile_name, func.count(TestResult.id).label("n"))\
                          .group_by(TestResult.profile_name)\
                          .order_by(func.count(TestResult.id).desc())\
                          .limit(3).all()
    top_profiles = [{"profile": p or "(sin perfil)", "count": n} for p, n in top_profiles_rows]
    # Perfiles disponibles para el dropdown
    profiles_all = [p for (p,) in db.query(TestResult.profile_name).distinct().all() if p]
    countries_all = [c for (c,) in db.query(Lead.country).distinct().all() if c]

    return {
        "total": total,
        "kpis": {
            "total_tests": g_total,
            "tests_a": g_test_a,
            "tests_b": g_test_b,
            "top_profiles": top_profiles,
        },
        "filters": {
            "profiles": sorted(profiles_all),
            "countries": sorted(countries_all),
        },
        "results": [
            {
                "id": t.id,
                "lead_id": t.lead_id,
                "lead_name": l.name,
                "lead_email": l.email,
                "lead_country": l.country,
                "test_type": t.test_type,
                "profile_name": t.profile_name,
                "profile_code": t.profile_code,
                "total_score": float(t.total_score) if t.total_score else 0,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                "dimensions": [
                    {"name": d.dimension_name, "code": d.dimension_code,
                     "score": float(d.score), "max_score": float(d.max_score),
                     "percentage": float(d.percentage)}
                    for d in t.dimensions
                ],
            } for t, l in rows
        ],
    }


@app.get("/api/leads/{lead_id}")
def get_lead(lead_id: int, payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    tests = db.query(TestResult).filter(TestResult.lead_id == lead_id).all()
    notes = db.query(ClinicalNote).filter(ClinicalNote.lead_id == lead_id).order_by(ClinicalNote.created_at.desc()).all()
    sessions_list = db.query(SessionModel).filter(SessionModel.lead_id == lead_id).order_by(SessionModel.scheduled_at.desc()).all()
    emails = db.query(EmailQueue).filter(EmailQueue.lead_id == lead_id).order_by(EmailQueue.sequence_number).all()

    return {
        "lead": {
            "id": lead.id, "name": lead.name, "email": lead.email, "phone": lead.phone,
            "country": lead.country, "status": lead.status, "source": lead.source,
            "trading_experience": lead.trading_experience, "notes": lead.notes,
            "created_at": lead.created_at.isoformat() if lead.created_at else None
        },
        "test_results": [
            {
                "id": t.id, "test_type": t.test_type, "profile_name": t.profile_name,
                "profile_code": t.profile_code, "total_score": float(t.total_score) if t.total_score else 0,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                "dimensions": [
                    {"name": d.dimension_name, "code": d.dimension_code,
                     "score": float(d.score), "max_score": float(d.max_score),
                     "percentage": float(d.percentage)}
                    for d in t.dimensions
                ]
            }
            for t in tests
        ],
        "clinical_notes": [
            {
                "id": n.id, "note_type": n.note_type, "content": n.content,
                "psychologist_id": n.psychologist_id,
                "created_at": n.created_at.isoformat() if n.created_at else None
            }
            for n in notes
        ],
        "sessions": [
            {
                "id": s.id, "session_type": s.session_type, "status": s.status,
                "scheduled_at": s.scheduled_at.isoformat() if s.scheduled_at else None,
                "duration_minutes": s.duration_minutes, "notes": s.notes
            }
            for s in sessions_list
        ],
        "emails": [
            {
                "id": e.id, "email_type": e.email_type, "sequence_number": e.sequence_number,
                "subject": e.subject, "status": e.status,
                "scheduled_at": e.scheduled_at.isoformat() if e.scheduled_at else None,
                "sent_at": e.sent_at.isoformat() if e.sent_at else None
            }
            for e in emails
        ]
    }


@app.get("/api/leads/{lead_id}/submissions")
def list_lead_submissions(lead_id: int, payload: dict = Depends(require_psychologist_or_admin),
                          db: Session = Depends(get_db)):
    """Historial cronologico (mas reciente arriba) de todas las interacciones del lead
    con formularios publicos: contacto/agendar, tests A/B, newsletter y compras (futuro)."""
    rows = (db.query(LeadSubmission)
              .filter(LeadSubmission.lead_id == lead_id)
              .order_by(LeadSubmission.created_at.desc())
              .all())
    return {
        "lead_id": lead_id,
        "total": len(rows),
        "submissions": [
            {
                "id": s.id,
                "source": s.source,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "whatsapp": s.whatsapp,
                "pais": s.pais,
                "experiencia_trading": s.experiencia_trading,
                "principal_desafio": s.principal_desafio,
                "intent": s.intent,
                "test_a_score": s.test_a_score, "test_a_perfil": s.test_a_perfil,
                "test_b_score": s.test_b_score, "test_b_perfil": s.test_b_perfil,
                "test_respuestas": s.test_respuestas,
                "plan_comprado": s.plan_comprado, "monto_pagado": float(s.monto_pagado) if s.monto_pagado else None,
                "moneda": s.moneda, "pasarela": s.pasarela, "transaccion_id": s.transaccion_id,
            } for s in rows
        ]
    }


@app.post("/api/clinical-notes")
def create_clinical_note(data: ClinicalNoteCreate, payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    psych = db.query(Psychologist).filter(Psychologist.email == payload["sub"]).first()
    if not psych:
        raise HTTPException(status_code=403, detail="PsicÃ³logo no encontrado")

    note = ClinicalNote(
        lead_id=data.lead_id,
        psychologist_id=psych.id,
        session_id=data.session_id,
        note_type=data.note_type,
        content=data.content
    )
    db.add(note)
    db.commit()
    return {"success": True, "note_id": note.id}


@app.post("/api/sessions")
def create_session(data: SessionCreate, payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    psych = db.query(Psychologist).filter(Psychologist.email == payload["sub"]).first()
    if not psych:
        raise HTTPException(status_code=403, detail="PsicÃ³logo no encontrado")

    session = SessionModel(
        lead_id=data.lead_id,
        psychologist_id=psych.id,
        session_type=data.session_type,
        scheduled_at=datetime.fromisoformat(data.scheduled_at),
        duration_minutes=data.duration_minutes,
        notes=data.notes
    )
    db.add(session)
    db.commit()
    return {"success": True, "session_id": session.id}


@app.get("/api/email-queue")
def get_email_queue(
    status: Optional[str] = None,
    payload: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(EmailQueue)
    if status:
        query = query.filter(EmailQueue.status == status)
    emails = query.order_by(EmailQueue.scheduled_at.desc()).limit(100).all()
    return {
        "emails": [
            {
                "id": e.id, "lead_id": e.lead_id, "email_type": e.email_type,
                "sequence_number": e.sequence_number, "subject": e.subject,
                "status": e.status,
                "scheduled_at": e.scheduled_at.isoformat() if e.scheduled_at else None,
                "sent_at": e.sent_at.isoformat() if e.sent_at else None,
                "error_message": e.error_message
            }
            for e in emails
        ]
    }


# ============================================
# ADMIN - GESTIÃ”N DE USUARIOS
# ============================================
def get_current_psychologist(payload: dict, db: Session):
    """Devuelve el registro Psychologist del token (admin o psychologist)."""
    psych = db.query(Psychologist).filter(Psychologist.email == payload["sub"]).first()
    if not psych:
        raise HTTPException(status_code=403, detail="Profesional no encontrado")
    return psych


def get_assigned_client_ids(db: Session, psicologo_id: int) -> set:
    """IDs de clientes actualmente asignados a un psicÃ³logo (is_active=TRUE)."""
    rows = db.query(PsicologoPaciente.paciente_id).filter(
        PsicologoPaciente.psicologo_id == psicologo_id,
        PsicologoPaciente.is_active == True,
    ).all()
    return {r[0] for r in rows}


def assert_can_access_client(payload: dict, client_id: int, db: Session):
    """
    REGLA CRÃTICA: admin ve todo; un psicÃ³logo SOLO puede acceder a un
    paciente asignado a Ã©l (validado contra psicologo_paciente en la BD,
    no contra el JWT). Cualquier otro caso â†’ 403.
    """
    role = payload.get("role")
    if role == "admin":
        return
    if role == "psychologist":
        psych = get_current_psychologist(payload, db)
        link = db.query(PsicologoPaciente).filter(
            PsicologoPaciente.psicologo_id == psych.id,
            PsicologoPaciente.paciente_id == client_id,
            PsicologoPaciente.is_active == True,
        ).first()
        if not link:
            raise HTTPException(status_code=403, detail="Este paciente no estÃ¡ asignado a ti")
        return
    raise HTTPException(status_code=403, detail="No autorizado")


# ============================================
# PSICÃ“LOGOS (perfil + carga)
# ============================================
def _psico_active_load(db: Session, psicologo_id: int) -> int:
    return db.query(func.count(PsicologoPaciente.id)).filter(
        PsicologoPaciente.psicologo_id == psicologo_id,
        PsicologoPaciente.is_active == True,
    ).scalar() or 0


def _psico_to_dict(db: Session, p: "Psychologist") -> dict:
    prof = db.query(PsicologoProfile).filter(PsicologoProfile.psychologist_id == p.id).first()
    load = _psico_active_load(db, p.id)
    max_p = prof.max_pacientes if prof and prof.max_pacientes is not None else 20
    return {
        "id": p.id, "name": p.name, "email": p.email, "is_active": bool(p.is_active),
        "bio": prof.bio if prof else None,
        "especialidad": prof.especialidad if prof else None,
        "idiomas": prof.idiomas if prof else None,
        "max_pacientes": max_p,
        "tarjeta_profesional": prof.tarjeta_profesional if prof else None,
        "esta_disponible": bool(prof.esta_disponible) if prof else True,
        "current_load": load,
        "slots_available": max(0, max_p - load),
    }


@app.get("/api/psicologos")
def list_psicologos(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """Admin ve todos; cliente ve solo el suyo asignado; psicÃ³logo se ve a sÃ­ mismo."""
    role = payload.get("role")
    if role == "admin":
        psicos = db.query(Psychologist).filter(Psychologist.role == "psychologist").all()
    elif role == "psychologist":
        psicos = [get_current_psychologist(payload, db)]
    elif role == "cliente":
        client = get_current_client(payload, db)
        link = db.query(PsicologoPaciente).filter(
            PsicologoPaciente.paciente_id == client.id,
            PsicologoPaciente.is_active == True,
        ).first()
        psicos = []
        if link:
            ps = db.query(Psychologist).filter(Psychologist.id == link.psicologo_id).first()
            if ps:
                psicos = [ps]
    else:
        raise HTTPException(status_code=403, detail="No autorizado")
    return {"psicologos": [_psico_to_dict(db, p) for p in psicos]}


@app.post("/api/psicologos/{psicologo_id}/profile")
def upsert_psicologo_profile(psicologo_id: int, data: PsicologoProfileIn,
                             payload: dict = Depends(require_admin), db: Session = Depends(get_db)):
    psico = db.query(Psychologist).filter(Psychologist.id == psicologo_id).first()
    if not psico:
        raise HTTPException(status_code=404, detail="PsicÃ³logo no encontrado")
    prof = db.query(PsicologoProfile).filter(PsicologoProfile.psychologist_id == psicologo_id).first()
    if not prof:
        prof = PsicologoProfile(psychologist_id=psicologo_id)
        db.add(prof)
    for field in ("bio", "especialidad", "idiomas", "max_pacientes", "tarjeta_profesional", "esta_disponible"):
        val = getattr(data, field)
        if val is not None:
            setattr(prof, field, val)
    db.commit()
    return {"success": True}


@app.get("/api/psicologos/{psicologo_id}/load")
def psicologo_load(psicologo_id: int, payload: dict = Depends(require_psychologist_or_admin),
                   db: Session = Depends(get_db)):
    # Un psicÃ³logo solo puede consultar su propia carga; admin cualquiera
    if payload.get("role") == "psychologist":
        me = get_current_psychologist(payload, db)
        if me.id != psicologo_id:
            raise HTTPException(status_code=403, detail="Solo puedes ver tu propia carga")
    psico = db.query(Psychologist).filter(Psychologist.id == psicologo_id).first()
    if not psico:
        raise HTTPException(status_code=404, detail="PsicÃ³logo no encontrado")
    return _psico_to_dict(db, psico)


# ============================================
# ASIGNACIONES CLIENTE â†” PSICÃ“LOGO (solo admin)
# ============================================
def _assignment_to_dict(db: Session, a: "PsicologoPaciente") -> dict:
    pac = db.query(Client).filter(Client.id == a.paciente_id).first()
    psi = db.query(Psychologist).filter(Psychologist.id == a.psicologo_id).first()
    return {
        "id": a.id,
        "paciente_id": a.paciente_id,
        "paciente_name": pac.name if pac else None,
        "paciente_email": pac.email if pac else None,
        "psicologo_id": a.psicologo_id,
        "psicologo_name": psi.name if psi else None,
        "is_active": bool(a.is_active),
        "assigned_at": a.assigned_at.isoformat() if a.assigned_at else None,
        "ended_at": a.ended_at.isoformat() if a.ended_at else None,
    }


@app.post("/api/asignaciones", status_code=201)
def crear_asignacion(data: AsignacionIn, payload: dict = Depends(require_admin), db: Session = Depends(get_db)):
    pac = db.query(Client).filter(Client.id == data.paciente_id).first()
    if not pac:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    psi = db.query(Psychologist).filter(Psychologist.id == data.psicologo_id,
                                        Psychologist.role == "psychologist").first()
    if not psi:
        raise HTTPException(status_code=404, detail="PsicÃ³logo no encontrado")
    # Regla: un psicÃ³logo activo por paciente a la vez
    existing = db.query(PsicologoPaciente).filter(
        PsicologoPaciente.paciente_id == data.paciente_id,
        PsicologoPaciente.is_active == True,
    ).first()
    if existing:
        raise HTTPException(status_code=409,
            detail="Este cliente ya tiene un psicÃ³logo activo. Finaliza la asignaciÃ³n actual primero o usa una solicitud de cambio.")
    admin = get_current_psychologist(payload, db)
    a = PsicologoPaciente(
        psicologo_id=data.psicologo_id, paciente_id=data.paciente_id,
        assigned_by_admin_id=admin.id, is_active=True, end_reason=data.notes,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    print(f"[AUDIT] AsignaciÃ³n creada: paciente={data.paciente_id} psicologo={data.psicologo_id} por admin={admin.id}")
    return {"success": True, "assignment_id": a.id}


@app.get("/api/asignaciones/active")
def asignaciones_activas(payload: dict = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(PsicologoPaciente).filter(PsicologoPaciente.is_active == True).all()
    return {"asignaciones": [_assignment_to_dict(db, a) for a in rows]}


@app.patch("/api/asignaciones/{assignment_id}/end")
def finalizar_asignacion(assignment_id: int, data: EndAsignacionIn,
                         payload: dict = Depends(require_admin), db: Session = Depends(get_db)):
    a = db.query(PsicologoPaciente).filter(PsicologoPaciente.id == assignment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="AsignaciÃ³n no encontrada")
    a.is_active = False
    a.ended_at = datetime.utcnow()
    if data.end_reason:
        a.end_reason = data.end_reason
    db.commit()
    print(f"[AUDIT] AsignaciÃ³n {assignment_id} finalizada por admin")
    return {"success": True}


# ============================================
# SOLICITUDES DE CAMBIO DE PSICÃ“LOGO
# ============================================
@app.post("/api/cambio-psicologo", status_code=201)
def solicitar_cambio(data: CambioRequestIn, payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    if payload.get("role") != "cliente":
        raise HTTPException(status_code=403, detail="Solo los clientes pueden solicitar cambio")
    client = get_current_client(payload, db)
    link = db.query(PsicologoPaciente).filter(
        PsicologoPaciente.paciente_id == client.id, PsicologoPaciente.is_active == True,
    ).first()
    if not link:
        raise HTTPException(status_code=400, detail="No tienes un psicÃ³logo asignado actualmente")
    # Evitar solicitudes duplicadas pendientes
    pend = db.query(CambioPsicologoRequest).filter(
        CambioPsicologoRequest.paciente_id == client.id,
        CambioPsicologoRequest.status == "pendiente",
    ).first()
    if pend:
        raise HTTPException(status_code=409, detail="Ya tienes una solicitud de cambio pendiente")
    req = CambioPsicologoRequest(
        paciente_id=client.id,
        current_psicologo_id=link.psicologo_id,
        reason_category=data.reason_category,
        reason_text=data.reason_text,
        share_reason_with_new=data.share_reason_with_new,
        status="pendiente",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    print(f"[AUDIT] Solicitud de cambio creada: paciente={client.id} req={req.id}")
    return {"success": True, "request_id": req.id}


@app.get("/api/mi-psicologo")
def mi_psicologo(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """El cliente obtiene los datos de su psicÃ³logo asignado y su asignaciÃ³n activa."""
    if payload.get("role") != "cliente":
        raise HTTPException(status_code=403, detail="Solo para clientes")
    client = get_current_client(payload, db)
    link = db.query(PsicologoPaciente).filter(
        PsicologoPaciente.paciente_id == client.id, PsicologoPaciente.is_active == True,
    ).first()
    if not link:
        return {"assigned": False}
    psico = db.query(Psychologist).filter(Psychologist.id == link.psicologo_id).first()
    prof = db.query(PsicologoProfile).filter(PsicologoProfile.psychologist_id == link.psicologo_id).first()
    return {
        "assigned": True,
        "assignment_id": link.id,
        "assigned_at": link.assigned_at.isoformat() if link.assigned_at else None,
        "psicologo_id": psico.id if psico else None,
        "psicologo_name": psico.name if psico else None,
        "especialidad": prof.especialidad if prof else None,
        "bio": prof.bio if prof else None,
        "idiomas": prof.idiomas if prof else None,
    }


@app.get("/api/mis-solicitudes")
def mis_solicitudes(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """El cliente ve sus propias solicitudes de cambio de psicÃ³logo."""
    if payload.get("role") != "cliente":
        raise HTTPException(status_code=403, detail="Solo para clientes")
    client = get_current_client(payload, db)
    rows = db.query(CambioPsicologoRequest).filter(
        CambioPsicologoRequest.paciente_id == client.id,
    ).order_by(CambioPsicologoRequest.created_at.desc()).all()
    return {"solicitudes": [
        {
            "id": r.id,
            "reason_category": r.reason_category,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in rows
    ]}


@app.get("/api/cambio-psicologo/pendientes")
def cambios_pendientes(payload: dict = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(CambioPsicologoRequest).filter(
        CambioPsicologoRequest.status == "pendiente",
    ).order_by(CambioPsicologoRequest.created_at.desc()).all()
    out = []
    for r in rows:
        pac = db.query(Client).filter(Client.id == r.paciente_id).first()
        cur = db.query(Psychologist).filter(Psychologist.id == r.current_psicologo_id).first()
        out.append({
            "id": r.id, "paciente_id": r.paciente_id,
            "paciente_name": pac.name if pac else None,
            "current_psicologo_id": r.current_psicologo_id,
            "current_psicologo_name": cur.name if cur else None,
            "reason_category": r.reason_category,
            "reason_text": r.reason_text if r.share_reason_with_new else None,
            "shared": bool(r.share_reason_with_new),
            "reason_text_admin": r.reason_text,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return {"solicitudes": out}


@app.post("/api/cambio-psicologo/{req_id}/aprobar")
def aprobar_cambio(req_id: int, data: AprobarCambioIn,
                   payload: dict = Depends(require_admin), db: Session = Depends(get_db)):
    req = db.query(CambioPsicologoRequest).filter(CambioPsicologoRequest.id == req_id).first()
    if not req or req.status != "pendiente":
        raise HTTPException(status_code=404, detail="Solicitud no encontrada o ya resuelta")
    nuevo = db.query(Psychologist).filter(Psychologist.id == data.nuevo_psicologo_id,
                                          Psychologist.role == "psychologist").first()
    if not nuevo:
        raise HTTPException(status_code=404, detail="Nuevo psicÃ³logo no encontrado")
    admin = get_current_psychologist(payload, db)
    # 1) Finalizar asignaciÃ³n activa actual del paciente
    actual = db.query(PsicologoPaciente).filter(
        PsicologoPaciente.paciente_id == req.paciente_id, PsicologoPaciente.is_active == True,
    ).first()
    if actual:
        actual.is_active = False
        actual.ended_at = datetime.utcnow()
        actual.end_reason = f"Cambio aprobado (solicitud #{req.id})"
        db.flush()  # liberar el UNIQUE de active_paciente antes de insertar
    # 2) Crear nueva asignaciÃ³n
    nueva = PsicologoPaciente(
        psicologo_id=nuevo.id, paciente_id=req.paciente_id,
        assigned_by_admin_id=admin.id, is_active=True,
    )
    db.add(nueva)
    # 3) Resolver la solicitud
    req.status = "aprobada"
    req.resolved_by_admin_id = admin.id
    req.resolved_at = datetime.utcnow()
    req.admin_notes = data.admin_notes
    db.commit()
    print(f"[AUDIT] Cambio aprobado req={req.id} paciente={req.paciente_id} nuevo_psico={nuevo.id} admin={admin.id}")
    return {"success": True}


@app.post("/api/cambio-psicologo/{req_id}/rechazar")
def rechazar_cambio(req_id: int, data: RechazarCambioIn,
                    payload: dict = Depends(require_admin), db: Session = Depends(get_db)):
    req = db.query(CambioPsicologoRequest).filter(CambioPsicologoRequest.id == req_id).first()
    if not req or req.status != "pendiente":
        raise HTTPException(status_code=404, detail="Solicitud no encontrada o ya resuelta")
    admin = get_current_psychologist(payload, db)
    req.status = "rechazada"
    req.resolved_by_admin_id = admin.id
    req.resolved_at = datetime.utcnow()
    req.admin_notes = data.admin_notes
    db.commit()
    print(f"[AUDIT] Cambio rechazado req={req.id} admin={admin.id}")
    return {"success": True}


VALID_ROLES = {"admin", "psychologist", "cliente"}


@app.get("/api/admin/users")
def admin_list_users(payload: dict = Depends(require_admin), db: Session = Depends(get_db)):
    psychs = db.query(Psychologist).all()
    clients = db.query(Client).all()

    users = []
    for p in psychs:
        users.append({
            "id": p.id,
            "user_type": "psychologist",
            "name": p.name,
            "email": p.email,
            "role": p.role,
            "is_active": bool(p.is_active),
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })
    for c in clients:
        users.append({
            "id": c.id,
            "user_type": "client",
            "name": c.name,
            "email": c.email,
            "role": c.role,
            "is_active": bool(c.is_active),
            "country": c.country,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    return {"total": len(users), "users": users}


@app.post("/api/admin/users", status_code=201)
def admin_create_user(data: AdminUserCreate, payload: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Rol invÃ¡lido. Use: {', '.join(VALID_ROLES)}")

    # Email Ãºnico en ambas tablas
    if db.query(Psychologist).filter(Psychologist.email == data.email).first() or \
       db.query(Client).filter(Client.email == data.email).first():
        raise HTTPException(status_code=400, detail="El email ya estÃ¡ registrado")

    if data.role in ("admin", "psychologist"):
        user = Psychologist(
            name=data.name,
            email=data.email,
            password_hash=pwd_context.hash(data.password),
            role=data.role,
            is_active=True,
        )
        user_type = "psychologist"
    else:  # cliente
        user = Client(
            name=data.name,
            email=data.email,
            password_hash=pwd_context.hash(data.password),
            country=data.country,
            role="cliente",
            is_active=True,
        )
        user_type = "client"

    db.add(user)
    db.commit()
    db.refresh(user)
    return {"success": True, "id": user.id, "user_type": user_type}


@app.put("/api/admin/users/{user_type}/{user_id}")
def admin_update_user(
    user_type: str,
    user_id: int,
    data: AdminUserUpdate,
    payload: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if user_type == "psychologist":
        user = db.query(Psychologist).filter(Psychologist.id == user_id).first()
    elif user_type == "client":
        user = db.query(Client).filter(Client.id == user_id).first()
    else:
        raise HTTPException(status_code=400, detail="Tipo de usuario invÃ¡lido")

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar rol si se envÃ­a
    if data.role is not None:
        if data.role not in VALID_ROLES:
            raise HTTPException(status_code=400, detail=f"Rol invÃ¡lido. Use: {', '.join(VALID_ROLES)}")
        # RestricciÃ³n: no cambiar tipo de tabla (un psicÃ³logo no puede pasar a cliente y viceversa)
        if user_type == "psychologist" and data.role == "cliente":
            raise HTTPException(status_code=400, detail="Un psicÃ³logo/admin no puede cambiar a rol cliente")
        if user_type == "client" and data.role in ("admin", "psychologist"):
            raise HTTPException(status_code=400, detail="Un cliente no puede cambiar a rol admin/psychologist")
        user.role = data.role

    # Email Ãºnico si cambia
    if data.email is not None and data.email != user.email:
        if db.query(Psychologist).filter(Psychologist.email == data.email).first() or \
           db.query(Client).filter(Client.email == data.email).first():
            raise HTTPException(status_code=400, detail="El email ya estÃ¡ registrado")
        user.email = data.email

    if data.name is not None:
        user.name = data.name
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password:
        user.password_hash = pwd_context.hash(data.password)
    if data.country is not None and user_type == "client":
        user.country = data.country

    db.commit()
    return {"success": True}


# ============================================
# CURSO "TRADER CONSCIENTE"
# ============================================
MAX_QUIZ_ATTEMPTS = 3


def get_current_client(payload: dict, db: Session) -> Client:
    """Obtiene el cliente autenticado a partir del token (rol cliente)."""
    if payload.get("role") != "cliente":
        raise HTTPException(status_code=403, detail="Acceso solo para clientes")
    client = db.query(Client).filter(Client.email == payload["sub"]).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client


def _is_module_available(module_number: int, completed: set) -> bool:
    """Reglas de progresiÃ³n MIXTA del curso."""
    if module_number == 1:
        return True
    if module_number == 2:
        return 1 in completed
    if module_number == 3:
        return 2 in completed
    if module_number in (4, 5, 6):
        return 3 in completed          # libres tras completar el 3
    if module_number == 7:
        return all(m in completed for m in (1, 2, 3, 4, 5, 6))
    return False


def _pass_mark(module_number: int) -> tuple:
    """Devuelve (correctas_necesarias, total) â€” 80%."""
    total = 10 if module_number == 7 else 5
    needed = 8 if module_number == 7 else 4
    return needed, total


@app.get("/api/course/modules")
def course_list_modules(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    client = get_current_client(payload, db)
    modules = db.query(CourseModule).order_by(CourseModule.module_number).all()
    progress_rows = db.query(CourseProgress).filter(CourseProgress.client_id == client.id).all()
    prog_by_module = {p.module_id: p for p in progress_rows}
    completed = {
        m.module_number for m in modules
        if prog_by_module.get(m.id) and prog_by_module[m.id].status == "completed"
    }

    result = []
    for m in modules:
        p = prog_by_module.get(m.id)
        if p and p.status == "completed":
            status = "completed"
        elif _is_module_available(m.module_number, completed):
            status = "in_progress" if (p and p.status == "in_progress") else "available"
        else:
            status = "locked"
        result.append({
            "id": m.id,
            "module_number": m.module_number,
            "title": m.title,
            "is_sequential": bool(m.is_sequential),
            "status": status,
            "quiz_score": p.quiz_score if p else None,
            "attempts": p.attempts if p else 0,
            "completed_at": p.completed_at.isoformat() if (p and p.completed_at) else None,
        })
    return {"modules": result}


@app.get("/api/course/modules/{module_id}")
def course_get_module(module_id: int, payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    client = get_current_client(payload, db)
    module = db.query(CourseModule).filter(CourseModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="MÃ³dulo no encontrado")

    # Calcular mÃ³dulos completados para validar acceso
    progress_rows = db.query(CourseProgress).filter(CourseProgress.client_id == client.id).all()
    prog_by_module = {p.module_id: p for p in progress_rows}
    all_modules = db.query(CourseModule).all()
    completed = {
        mm.module_number for mm in all_modules
        if prog_by_module.get(mm.id) and prog_by_module[mm.id].status == "completed"
    }

    p = prog_by_module.get(module.id)
    is_completed = p and p.status == "completed"
    if not (is_completed or _is_module_available(module.module_number, completed)):
        raise HTTPException(status_code=403, detail="Este mÃ³dulo estÃ¡ bloqueado")

    # Marcar in_progress si estÃ¡ disponible y aÃºn no se completÃ³
    if not is_completed:
        if not p:
            p = CourseProgress(client_id=client.id, module_id=module.id, status="in_progress")
            db.add(p)
        elif p.status != "completed":
            p.status = "in_progress"
        db.commit()

    quizzes = db.query(CourseQuiz).filter(CourseQuiz.module_id == module.id)\
        .order_by(CourseQuiz.question_order).all()

    return {
        "id": module.id,
        "module_number": module.module_number,
        "title": module.title,
        "content_md": module.content_md,
        "is_sequential": bool(module.is_sequential),
        "quiz": [
            {
                "id": q.id, "question": q.question, "order": q.question_order,
                "option_a": q.option_a, "option_b": q.option_b,
                "option_c": q.option_c, "option_d": q.option_d,
                # correct_option NO se envÃ­a al cliente
            }
            for q in quizzes
        ],
        "status": "completed" if is_completed else "in_progress",
        "attempts": p.attempts if p else 0,
        "max_attempts": MAX_QUIZ_ATTEMPTS,
    }


@app.post("/api/course/modules/{module_id}/complete")
def course_complete_module(module_id: int, data: CompleteModuleRequest,
                           payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    client = get_current_client(payload, db)
    module = db.query(CourseModule).filter(CourseModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="MÃ³dulo no encontrado")

    # Validar acceso
    progress_rows = db.query(CourseProgress).filter(CourseProgress.client_id == client.id).all()
    prog_by_module = {p.module_id: p for p in progress_rows}
    all_modules = db.query(CourseModule).all()
    completed_before = {
        mm.module_number for mm in all_modules
        if prog_by_module.get(mm.id) and prog_by_module[mm.id].status == "completed"
    }
    p = prog_by_module.get(module.id)

    if p and p.status == "completed":
        return {"passed": True, "score": p.quiz_score, "already_completed": True, "next_unlocked": []}

    if not _is_module_available(module.module_number, completed_before):
        raise HTTPException(status_code=403, detail="Este mÃ³dulo estÃ¡ bloqueado")

    if p and p.attempts >= MAX_QUIZ_ATTEMPTS:
        raise HTTPException(status_code=403,
                            detail="Alcanzaste el lÃ­mite de 3 intentos. Contacta a tu psicÃ³logo.")

    # Calcular score
    quizzes = db.query(CourseQuiz).filter(CourseQuiz.module_id == module.id).all()
    correct_by_id = {q.id: (q.correct_option or "").lower() for q in quizzes}
    answers_by_id = {a.question_id: (a.answer or "").lower() for a in data.quiz_answers}
    score = sum(1 for qid, correct in correct_by_id.items() if answers_by_id.get(qid) == correct)

    needed, total = _pass_mark(module.module_number)
    passed = score >= needed

    # Upsert progreso
    if not p:
        p = CourseProgress(client_id=client.id, module_id=module.id, status="in_progress", attempts=0)
        db.add(p)
        db.flush()
    p.attempts = (p.attempts or 0) + 1
    p.quiz_score = score

    next_unlocked = []
    diary_question_id = None
    if passed:
        p.status = "completed"
        p.completed_at = datetime.utcnow()
        diary_question_id = module.unlocks_diary_question_id
        # recomputar desbloqueos
        completed_after = set(completed_before) | {module.module_number}
        available_before = {m.module_number for m in all_modules
                            if _is_module_available(m.module_number, completed_before)}
        for m in all_modules:
            if m.module_number not in available_before and \
               _is_module_available(m.module_number, completed_after):
                next_unlocked.append(m.module_number)
    else:
        p.status = "in_progress"

    db.commit()

    return {
        "passed": passed,
        "score": score,
        "total": total,
        "needed": needed,
        "attempts": p.attempts,
        "attempts_left": max(0, MAX_QUIZ_ATTEMPTS - p.attempts),
        "next_unlocked": sorted(next_unlocked),
        "diary_question_id": diary_question_id,
    }


@app.get("/api/course/progress")
def course_progress_overview(client_id: Optional[int] = None,
                             payload: dict = Depends(require_psychologist_or_admin), db: Session = Depends(get_db)):
    clients_q = db.query(Client)
    if client_id is not None:
        # REGLA CRÃTICA: si pide un cliente puntual, validar acceso
        assert_can_access_client(payload, client_id, db)
        clients_q = clients_q.filter(Client.id == client_id)
    elif payload.get("role") == "psychologist":
        # Un psicÃ³logo (sin client_id) solo ve a SUS pacientes asignados
        psych = get_current_psychologist(payload, db)
        assigned = get_assigned_client_ids(db, psych.id)
        if not assigned:
            return {"progress": []}
        clients_q = clients_q.filter(Client.id.in_(assigned))
    clients = clients_q.all()

    total_modules = db.query(func.count(CourseModule.id)).scalar() or 0
    result = []
    for c in clients:
        rows = db.query(CourseProgress).filter(CourseProgress.client_id == c.id).all()
        completed = [r for r in rows if r.status == "completed"]
        last_activity = None
        if rows:
            dates = [r.updated_at for r in rows if r.updated_at]
            last_activity = max(dates).isoformat() if dates else None
        result.append({
            "client_id": c.id,
            "name": c.name,
            "email": c.email,
            "modules_completed": len(completed),
            "total_modules": total_modules,
            "quiz_scores": [
                {"module_id": r.module_id, "score": r.quiz_score, "attempts": r.attempts}
                for r in rows if r.quiz_score is not None
            ],
            "last_activity": last_activity,
        })
    return {"progress": result}


# ============================================
# DIARIO DE TRADING PSICOLÃ“GICO
# ============================================
def _entry_to_dict(entry: DiaryEntry, with_answers: bool = False) -> dict:
    d = {
        "id": entry.id,
        "entry_date": entry.entry_date.isoformat() if entry.entry_date else None,
        "traded_today": bool(entry.traded_today),
        "financial_result": float(entry.financial_result) if entry.financial_result is not None else None,
        "emotional_score": entry.emotional_score,
        "free_notes": entry.free_notes,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }
    if with_answers:
        d["answers"] = [
            {"question_id": a.question_id, "answer_text": a.answer_text}
            for a in entry.answers
        ]
    return d


@app.get("/api/diary/questions")
def diary_questions(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    client = get_current_client(payload, db)
    completed_module_ids = {
        p.module_id for p in db.query(CourseProgress)
        .filter(CourseProgress.client_id == client.id, CourseProgress.status == "completed")
    }
    qs = db.query(DiaryQuestion).filter(
        DiaryQuestion.is_active == True,
        or_(
            DiaryQuestion.unlocked_by_module_id == None,
            DiaryQuestion.unlocked_by_module_id.in_(completed_module_ids) if completed_module_ids else False
        )
    ).order_by(DiaryQuestion.display_order).all()
    return {"questions": [{"id": q.id, "question_text": q.question_text} for q in qs]}


@app.post("/api/diary/entries", status_code=201)
def diary_create_entry(data: DiaryEntryCreate, payload: dict = Depends(verify_token),
                       db: Session = Depends(get_db)):
    client = get_current_client(payload, db)
    if data.emotional_score < 1 or data.emotional_score > 5:
        raise HTTPException(status_code=400, detail="emotional_score debe ser entre 1 y 5")

    entry_date = date_type.fromisoformat(data.entry_date) if data.entry_date else date_type.today()

    existing = db.query(DiaryEntry).filter(
        DiaryEntry.client_id == client.id, DiaryEntry.entry_date == entry_date
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ya existe una entrada para esta fecha")

    entry = DiaryEntry(
        client_id=client.id,
        entry_date=entry_date,
        traded_today=data.traded_today,
        financial_result=data.financial_result,
        emotional_score=data.emotional_score,
        free_notes=data.free_notes,
    )
    db.add(entry)
    db.flush()

    for ans in (data.answers or []):
        db.add(DiaryEntryAnswer(entry_id=entry.id, question_id=ans.question_id,
                                answer_text=ans.answer_text))
    db.commit()
    db.refresh(entry)
    return {"success": True, "entry_id": entry.id}


@app.get("/api/diary/entries")
def diary_list_entries(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    payload: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    client = get_current_client(payload, db)
    q = db.query(DiaryEntry).filter(DiaryEntry.client_id == client.id)
    if from_date:
        q = q.filter(DiaryEntry.entry_date >= date_type.fromisoformat(from_date))
    if to_date:
        q = q.filter(DiaryEntry.entry_date <= date_type.fromisoformat(to_date))
    entries = q.order_by(DiaryEntry.entry_date.desc()).all()
    return {"entries": [_entry_to_dict(e) for e in entries]}


@app.get("/api/diary/entries/{entry_id}")
def diary_get_entry(entry_id: int, payload: dict = Depends(verify_token),
                    db: Session = Depends(get_db)):
    client = get_current_client(payload, db)
    entry = db.query(DiaryEntry).filter(
        DiaryEntry.id == entry_id, DiaryEntry.client_id == client.id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entrada no encontrada")
    return _entry_to_dict(entry, with_answers=True)


@app.patch("/api/diary/entries/{entry_id}")
def diary_update_entry(entry_id: int, data: DiaryEntryUpdate,
                       payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    client = get_current_client(payload, db)
    entry = db.query(DiaryEntry).filter(
        DiaryEntry.id == entry_id, DiaryEntry.client_id == client.id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entrada no encontrada")
    if entry.entry_date != date_type.today():
        raise HTTPException(status_code=403, detail="Solo puedes editar la entrada del dÃ­a de hoy")

    if data.traded_today is not None:
        entry.traded_today = data.traded_today
    if data.financial_result is not None:
        entry.financial_result = data.financial_result
    if data.emotional_score is not None:
        if data.emotional_score < 1 or data.emotional_score > 5:
            raise HTTPException(status_code=400, detail="emotional_score debe ser entre 1 y 5")
        entry.emotional_score = data.emotional_score
    if data.free_notes is not None:
        entry.free_notes = data.free_notes

    if data.answers is not None:
        db.query(DiaryEntryAnswer).filter(DiaryEntryAnswer.entry_id == entry.id).delete()
        for ans in data.answers:
            db.add(DiaryEntryAnswer(entry_id=entry.id, question_id=ans.question_id,
                                    answer_text=ans.answer_text))
    db.commit()
    return {"success": True}


@app.get("/api/diary/client/{client_id}")
def diary_psychologist_view(client_id: int, payload: dict = Depends(require_psychologist_or_admin),
                             db: Session = Depends(get_db)):
    # REGLA CRÃTICA: el psicÃ³logo solo ve pacientes asignados; admin ve todo
    assert_can_access_client(payload, client_id, db)
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    entries = db.query(DiaryEntry).filter(DiaryEntry.client_id == client_id)\
        .order_by(DiaryEntry.entry_date.desc()).all()
    return {
        "client": {"id": client.id, "name": client.name, "email": client.email},
        "entries": [_entry_to_dict(e, with_answers=True) for e in entries],
        "stats": {
            "total_entries": len(entries),
            "days_traded": sum(1 for e in entries if e.traded_today),
            "avg_emotional": round(sum(e.emotional_score for e in entries) / len(entries), 1) if entries else None,
            "total_financial": float(sum(e.financial_result or 0 for e in entries)),
        }
    }


# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
