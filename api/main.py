"""
PsicoaTrading — API Backend
FastAPI + MySQL + SendGrid
CRM Clínico con embudo de ventas automatizado
"""
import os
import json
from datetime import datetime, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Boolean, DateTime,
    JSON, Enum as SAEnum, ForeignKey, func, DECIMAL
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
    specialty = Column(String(200), default="Psicología del Trading")
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


class CourseModule(Base):
    __tablename__ = "courses_modules"
    id            = Column(Integer, primary_key=True, index=True)
    module_number = Column(Integer, nullable=False, unique=True)  # 1-7
    title         = Column(String(200), nullable=False)
    content_md    = Column(Text)
    is_sequential = Column(Boolean, default=True)  # True: 1,2,3,7 | False: 4,5,6
    unlocks_diary_question_id = Column(Integer, nullable=True)  # FK lógico a diario (sin constraint por ahora)
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


# ============================================
# SCHEMAS (Pydantic)
# ============================================
class TestResultSubmit(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    country: Optional[str] = None
    trading_experience: Optional[str] = None
    test_type: str
    profile_name: str
    profile_code: str
    total_score: float
    answers: Optional[dict] = None
    dimensions: List[dict]


class ContactSubmit(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    country: Optional[str] = None


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
            raise HTTPException(status_code=401, detail="Token inválido")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


# ============================================
# EMAIL SEQUENCES
# ============================================
EMAIL_SEQUENCES = [
    {"type": "welcome", "seq": 1, "delay_hours": 0,
     "subject": "Tu perfil psicológico de trader está listo 🧠",
     "template": "Hola {name}, gracias por completar el test. Tu perfil es: {profile}. En los próximos días te enviaremos contenido personalizado para mejorar tu psicología de trading."},
    {"type": "deep_dive", "seq": 2, "delay_hours": 48,
     "subject": "Tu principal desafío como trader (y cómo superarlo)",
     "template": "Hola {name}, basados en tu perfil ({profile}), tu principal desafío es el control emocional durante las operaciones. Aquí te explicamos cómo trabajamos este aspecto..."},
    {"type": "social_proof", "seq": 3, "delay_hours": 120,
     "subject": "Cómo Juan pasó de perder 3 fondeos a ser consistente",
     "template": "Hola {name}, queremos compartirte el caso de un trader que tenía un perfil similar al tuyo..."},
    {"type": "free_resource", "seq": 4, "delay_hours": 168,
     "subject": "Regalo: Guía de autoregulación emocional para traders 📖",
     "template": "Hola {name}, como parte de nuestro compromiso con tu desarrollo, te compartimos nuestra guía gratuita de autoregulación emocional..."},
    {"type": "last_call", "seq": 5, "delay_hours": 240,
     "subject": "Tu sesión diagnóstico gratuita te espera (últimos cupos)",
     "template": "Hola {name}, hace 10 días completaste tu test y tu perfil reveló áreas importantes de trabajo. ¿Ya agendaste tu sesión diagnóstico gratuita? Los cupos son limitados..."},
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
    scheduler.start()
    print("✅ PsicoaTrading API running — email scheduler active")
    yield
    scheduler.shutdown()


# ============================================
# APP
# ============================================
app = FastAPI(
    title="PsicoaTrading API",
    description="CRM Clínico — Psicología aplicada al Trading",
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
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# ENDPOINTS PÚBLICOS
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
            source="web_test"
        )
        db.add(lead)
        db.flush()
    else:
        lead.name = data.name
        if data.phone:
            lead.phone = data.phone
        if data.country:
            lead.country = data.country

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
        ds = DimensionScore(
            test_result_id=test_result.id,
            dimension_name=dim.get("name", ""),
            dimension_code=dim.get("code", ""),
            score=dim.get("score", 0),
            max_score=dim.get("max_score", 100),
            percentage=dim.get("percentage", 0)
        )
        db.add(ds)

    db.commit()

    # Schedule email sequence
    schedule_email_sequence(db, lead.id, lead.name, data.profile_name)

    return {
        "success": True,
        "lead_id": lead.id,
        "test_result_id": test_result.id,
        "message": "Resultado guardado. Revisa tu email para más información."
    }


@app.post("/api/contact")
def submit_contact(data: ContactSubmit, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.email == data.email).first()
    if not lead:
        lead = Lead(
            name=data.name,
            email=data.email,
            phone=data.phone,
            source="contact_form",
            notes=data.message
        )
        db.add(lead)
    else:
        lead.notes = (lead.notes or "") + f"\n\n[Contacto {datetime.utcnow().strftime('%Y-%m-%d')}]: {data.message}"

    db.commit()
    return {"success": True, "message": "Mensaje recibido. Te contactaremos pronto."}


# ============================================
# ENDPOINTS AUTENTICADOS
# ============================================
@app.post("/api/auth/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # 1. Psicólogos y admins
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
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    if db.query(Client).filter(Client.email == data.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
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


@app.get("/api/dashboard/stats")
def dashboard_stats(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    total_leads = db.query(func.count(Lead.id)).scalar()
    new_leads = db.query(func.count(Lead.id)).filter(Lead.status == "new").scalar()
    converted = db.query(func.count(Lead.id)).filter(Lead.status == "converted").scalar()
    total_tests = db.query(func.count(TestResult.id)).scalar()
    pending_emails = db.query(func.count(EmailQueue.id)).filter(EmailQueue.status == "pending").scalar()
    sent_emails = db.query(func.count(EmailQueue.id)).filter(EmailQueue.status == "sent").scalar()
    upcoming_sessions = db.query(func.count(SessionModel.id)).filter(
        SessionModel.status == "scheduled",
        SessionModel.scheduled_at >= datetime.utcnow()
    ).scalar()

    # Leads last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_leads = db.query(func.count(Lead.id)).filter(Lead.created_at >= week_ago).scalar()

    return {
        "total_leads": total_leads,
        "new_leads": new_leads,
        "converted": converted,
        "conversion_rate": round((converted / total_leads * 100), 1) if total_leads > 0 else 0,
        "total_tests": total_tests,
        "pending_emails": pending_emails,
        "sent_emails": sent_emails,
        "upcoming_sessions": upcoming_sessions,
        "recent_leads_7d": recent_leads
    }


@app.get("/api/leads")
def list_leads(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    payload: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status)
    if search:
        query = query.filter(
            (Lead.name.ilike(f"%{search}%")) | (Lead.email.ilike(f"%{search}%"))
        )
    total = query.count()
    leads = query.order_by(Lead.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "leads": [
            {
                "id": l.id, "name": l.name, "email": l.email, "phone": l.phone,
                "country": l.country, "status": l.status, "source": l.source,
                "trading_experience": l.trading_experience,
                "created_at": l.created_at.isoformat() if l.created_at else None
            }
            for l in leads
        ]
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


@app.post("/api/clinical-notes")
def create_clinical_note(data: ClinicalNoteCreate, payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    psych = db.query(Psychologist).filter(Psychologist.email == payload["sub"]).first()
    if not psych:
        raise HTTPException(status_code=403, detail="Psicólogo no encontrado")

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
        raise HTTPException(status_code=403, detail="Psicólogo no encontrado")

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
    payload: dict = Depends(verify_token),
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
# ADMIN - GESTIÓN DE USUARIOS
# ============================================
def require_admin(payload: dict = Depends(verify_token)):
    """Guard: solo permite acceso a usuarios con rol admin."""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acceso solo para administradores")
    return payload


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
        raise HTTPException(status_code=400, detail=f"Rol inválido. Use: {', '.join(VALID_ROLES)}")

    # Email único en ambas tablas
    if db.query(Psychologist).filter(Psychologist.email == data.email).first() or \
       db.query(Client).filter(Client.email == data.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

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
        raise HTTPException(status_code=400, detail="Tipo de usuario inválido")

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar rol si se envía
    if data.role is not None:
        if data.role not in VALID_ROLES:
            raise HTTPException(status_code=400, detail=f"Rol inválido. Use: {', '.join(VALID_ROLES)}")
        # Restricción: no cambiar tipo de tabla (un psicólogo no puede pasar a cliente y viceversa)
        if user_type == "psychologist" and data.role == "cliente":
            raise HTTPException(status_code=400, detail="Un psicólogo/admin no puede cambiar a rol cliente")
        if user_type == "client" and data.role in ("admin", "psychologist"):
            raise HTTPException(status_code=400, detail="Un cliente no puede cambiar a rol admin/psychologist")
        user.role = data.role

    # Email único si cambia
    if data.email is not None and data.email != user.email:
        if db.query(Psychologist).filter(Psychologist.email == data.email).first() or \
           db.query(Client).filter(Client.email == data.email).first():
            raise HTTPException(status_code=400, detail="El email ya está registrado")
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
    """Reglas de progresión MIXTA del curso."""
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
    """Devuelve (correctas_necesarias, total) — 80%."""
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
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    # Calcular módulos completados para validar acceso
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
        raise HTTPException(status_code=403, detail="Este módulo está bloqueado")

    # Marcar in_progress si está disponible y aún no se completó
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
                # correct_option NO se envía al cliente
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
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

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
        raise HTTPException(status_code=403, detail="Este módulo está bloqueado")

    if p and p.attempts >= MAX_QUIZ_ATTEMPTS:
        raise HTTPException(status_code=403,
                            detail="Alcanzaste el límite de 3 intentos. Contacta a tu psicólogo.")

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
                             payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    # Solo psicólogos/admins
    if payload.get("role") not in ("admin", "psychologist"):
        raise HTTPException(status_code=403, detail="Acceso solo para el equipo clínico")

    clients_q = db.query(Client)
    if client_id is not None:
        clients_q = clients_q.filter(Client.id == client_id)
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
# MAIN
# ============================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
