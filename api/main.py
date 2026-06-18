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
# MAIN
# ============================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
