-- Phase 2: Roadmap Service - Independent Schema
-- Creates independent database schema for Roadmap microservice

CREATE SCHEMA IF NOT EXISTS aivery_roadmap;

-- Roadmaps table
CREATE TABLE IF NOT EXISTS aivery_roadmap.roadmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    diagnostic_id VARCHAR(255),
    blueprint_id VARCHAR(255),
    title VARCHAR(255),
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    phases JSONB,
    timeline JSONB,
    resources JSONB,
    estimated_duration VARCHAR(100),
    priority VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- Indexes
CREATE INDEX idx_roadmap_user_id ON aivery_roadmap.roadmaps(user_id);
CREATE INDEX idx_roadmap_diagnostic_id ON aivery_roadmap.roadmaps(diagnostic_id);
CREATE INDEX idx_roadmap_blueprint_id ON aivery_roadmap.roadmaps(blueprint_id);
CREATE INDEX idx_roadmap_status ON aivery_roadmap.roadmaps(status);
CREATE INDEX idx_roadmap_created_at ON aivery_roadmap.roadmaps(created_at);

-- Milestones table
CREATE TABLE IF NOT EXISTS aivery_roadmap.milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id UUID NOT NULL REFERENCES aivery_roadmap.roadmaps(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    phase VARCHAR(100),
    target_date DATE,
    status VARCHAR(50) DEFAULT 'planned',
    deliverables JSONB,
    dependencies JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_milestone_roadmap_id ON aivery_roadmap.milestones(roadmap_id);
CREATE INDEX idx_milestone_status ON aivery_roadmap.milestones(status);
CREATE INDEX idx_milestone_target_date ON aivery_roadmap.milestones(target_date);

-- Tasks table
CREATE TABLE IF NOT EXISTS aivery_roadmap.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    milestone_id UUID NOT NULL REFERENCES aivery_roadmap.milestones(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assignee VARCHAR(255),
    status VARCHAR(50) DEFAULT 'todo',
    priority VARCHAR(50),
    due_date DATE,
    estimated_hours DECIMAL(10, 2),
    actual_hours DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_task_milestone_id ON aivery_roadmap.tasks(milestone_id);
CREATE INDEX idx_task_status ON aivery_roadmap.tasks(status);
CREATE INDEX idx_task_assignee ON aivery_roadmap.tasks(assignee);
CREATE INDEX idx_task_due_date ON aivery_roadmap.tasks(due_date);

-- Roadmap sharing table
CREATE TABLE IF NOT EXISTS aivery_roadmap.roadmap_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id UUID NOT NULL REFERENCES aivery_roadmap.roadmaps(id) ON DELETE CASCADE,
    shared_with_user_id VARCHAR(255),
    share_token VARCHAR(255) UNIQUE,
    permission VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_roadmap_share_roadmap_id ON aivery_roadmap.roadmap_shares(roadmap_id);
CREATE INDEX idx_roadmap_share_token ON aivery_roadmap.roadmap_shares(share_token);

-- Audit log
CREATE TABLE IF NOT EXISTS aivery_roadmap.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id UUID,
    user_id VARCHAR(255),
    action VARCHAR(100),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_audit_roadmap_id ON aivery_roadmap.audit_logs(roadmap_id);
CREATE INDEX idx_audit_user_id ON aivery_roadmap.audit_logs(user_id);
CREATE INDEX idx_audit_created_at ON aivery_roadmap.audit_logs(created_at);
