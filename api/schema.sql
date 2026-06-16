-- PsicoaTrading CRM — Schema MySQL
-- Base de datos: psicoatrading_crm

CREATE DATABASE IF NOT EXISTS psicoatrading_crm
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE psicoatrading_crm;

-- ============================================
-- 1. PSICÓLOGOS (usuarios del panel clínico)
-- ============================================
CREATE TABLE IF NOT EXISTS psychologists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    specialty VARCHAR(200) DEFAULT 'Psicología del Trading',
    role ENUM('admin', 'psychologist') DEFAULT 'psychologist',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================
-- 2. LEADS (visitantes que completan el test)
-- ============================================
CREATE TABLE IF NOT EXISTS leads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL,
    phone VARCHAR(50),
    country VARCHAR(100),
    trading_experience VARCHAR(50),
    source VARCHAR(100) DEFAULT 'web_test',
    status ENUM('new', 'contacted', 'in_process', 'converted', 'lost') DEFAULT 'new',
    assigned_psychologist_id INT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_psychologist_id) REFERENCES psychologists(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================
-- 3. TEST RESULTS (resultados de los tests)
-- ============================================
CREATE TABLE IF NOT EXISTS test_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT NOT NULL,
    test_type ENUM('A', 'B') NOT NULL COMMENT 'A=Perfil Psicológico Trader, B=Auditoría Plan Trading',
    profile_name VARCHAR(200) NOT NULL,
    profile_code VARCHAR(50) NOT NULL,
    total_score DECIMAL(5,2),
    answers_json JSON,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================
-- 4. DIMENSION SCORES (puntuaciones por dimensión)
-- ============================================
CREATE TABLE IF NOT EXISTS dimension_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    test_result_id INT NOT NULL,
    dimension_name VARCHAR(100) NOT NULL,
    dimension_code VARCHAR(50) NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    max_score DECIMAL(5,2) NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (test_result_id) REFERENCES test_results(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================
-- 5. EMAIL QUEUE (cola de emails automáticos)
-- ============================================
CREATE TABLE IF NOT EXISTS email_queue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT NOT NULL,
    email_type VARCHAR(50) NOT NULL COMMENT 'welcome, deep_dive, social_proof, free_resource, last_call',
    sequence_number INT NOT NULL COMMENT '1-5',
    subject VARCHAR(500),
    body_html TEXT,
    status ENUM('pending', 'sent', 'failed') DEFAULT 'pending',
    scheduled_at DATETIME NOT NULL,
    sent_at DATETIME,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================
-- 6. SESSIONS (sesiones agendadas)
-- ============================================
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT NOT NULL,
    psychologist_id INT,
    session_type ENUM('diagnostic', 'follow_up', 'advisory') DEFAULT 'diagnostic',
    status ENUM('scheduled', 'completed', 'cancelled', 'no_show') DEFAULT 'scheduled',
    scheduled_at DATETIME,
    duration_minutes INT DEFAULT 45,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
    FOREIGN KEY (psychologist_id) REFERENCES psychologists(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================
-- 7. CLINICAL NOTES (notas clínicas)
-- ============================================
CREATE TABLE IF NOT EXISTS clinical_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT NOT NULL,
    psychologist_id INT NOT NULL,
    session_id INT,
    note_type ENUM('initial_assessment', 'progress', 'intervention', 'discharge') DEFAULT 'progress',
    content TEXT NOT NULL,
    is_private BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
    FOREIGN KEY (psychologist_id) REFERENCES psychologists(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================
-- SEED: Admin por defecto
-- ============================================
-- Password: PsicoaTrading2025! (bcrypt hash)
INSERT INTO psychologists (name, email, password_hash, specialty, role)
VALUES (
    'Admin PsicoaTrading',
    'admin@psicoatrading.com',
    '$2b$12$LJ3m4ys3GZxkGJXQfVhOeOYHWEVPH0VQ1y5AzQRnMKn8Y8y9S6Iri',
    'Psicología del Trading',
    'admin'
) ON DUPLICATE KEY UPDATE name = name;
