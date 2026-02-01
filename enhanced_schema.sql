-- ENHANCED SAAS ANALYTICS SCHEMA
-- Designed for RAG demonstrations with realistic business scenarios

-- Core Entity: Users
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    email TEXT NOT NULL,
    company_name TEXT,
    industry TEXT,  -- Tech, Healthcare, Finance, Retail, etc.
    company_size TEXT,  -- Startup, SMB, Mid-Market, Enterprise
    signup_date DATE NOT NULL,
    country TEXT,
    status TEXT,  -- active, churned, trial
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subscriptions (1:Many with Users)
CREATE TABLE subscriptions (
    subscription_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    plan_id INTEGER NOT NULL,
    status TEXT NOT NULL,  -- active, cancelled, paused, trial
    start_date DATE NOT NULL,
    end_date DATE,
    billing_cycle TEXT,  -- monthly, annual, quarterly
    amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    trial_end_date DATE,
    cancellation_reason TEXT,  -- price, features, support, competition, other
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Subscription Plans (Master data)
CREATE TABLE plans (
    plan_id INTEGER PRIMARY KEY,
    plan_name TEXT NOT NULL,  -- Free, Starter, Professional, Enterprise
    plan_tier TEXT NOT NULL,  -- free, basic, premium, enterprise
    monthly_price DECIMAL(10,2) NOT NULL,
    annual_price DECIMAL(10,2) NOT NULL,
    max_users INTEGER,
    max_projects INTEGER,
    features TEXT,  -- JSON array of features
    is_active BOOLEAN DEFAULT 1
);

-- Transactions (Payment history)
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    subscription_id INTEGER,
    amount DECIMAL(10,2) NOT NULL,
    transaction_type TEXT,  -- charge, refund, credit
    status TEXT,  -- success, failed, pending
    payment_method TEXT,  -- credit_card, paypal, wire_transfer
    transaction_date DATE NOT NULL,
    currency TEXT DEFAULT 'USD',
    stripe_charge_id TEXT,
    failure_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
);

-- Product Usage (NEW - enables behavioral analytics)
CREATE TABLE usage_events (
    event_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,  -- login, feature_use, export, api_call
    feature_name TEXT,  -- dashboard, reports, integrations, etc.
    event_date DATE NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    session_id TEXT,
    metadata TEXT,  -- JSON for additional context
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Support Tickets (NEW - enables CS analytics)
CREATE TABLE support_tickets (
    ticket_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    category TEXT,  -- bug, feature_request, billing, general
    priority TEXT,  -- low, medium, high, critical
    status TEXT,  -- open, in_progress, resolved, closed
    created_date DATE NOT NULL,
    resolved_date DATE,
    assigned_to TEXT,  -- support agent name
    satisfaction_score INTEGER,  -- 1-5 rating
    resolution_time_hours DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Customer Health Score (NEW - enables churn prediction)
CREATE TABLE customer_health (
    health_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    score_date DATE NOT NULL,
    health_score INTEGER,  -- 0-100
    engagement_score INTEGER,  -- 0-100 based on usage
    support_score INTEGER,  -- 0-100 based on ticket satisfaction
    payment_score INTEGER,  -- 0-100 based on payment reliability
    churn_risk TEXT,  -- low, medium, high
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Marketing Campaigns (NEW - enables attribution analytics)
CREATE TABLE campaigns (
    campaign_id INTEGER PRIMARY KEY,
    campaign_name TEXT NOT NULL,
    channel TEXT,  -- email, social, paid_search, content, referral
    start_date DATE NOT NULL,
    end_date DATE,
    budget DECIMAL(10,2),
    target_segment TEXT,  -- enterprise, smb, specific industry
    status TEXT  -- active, completed, paused
);

-- Campaign Attribution (Links users to campaigns)
CREATE TABLE campaign_attribution (
    attribution_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    campaign_id INTEGER NOT NULL,
    attribution_date DATE NOT NULL,
    touchpoint_type TEXT,  -- first_touch, last_touch, multi_touch
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- Feature Flags / A/B Tests (NEW - enables experimentation analytics)
CREATE TABLE experiments (
    experiment_id INTEGER PRIMARY KEY,
    experiment_name TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    variant_a_name TEXT,  -- control
    variant_b_name TEXT,  -- treatment
    status TEXT  -- active, completed, paused
);

CREATE TABLE experiment_assignments (
    assignment_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    experiment_id INTEGER NOT NULL,
    variant TEXT,  -- A or B
    assigned_date DATE NOT NULL,
    converted BOOLEAN DEFAULT 0,
    conversion_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);

-- Indexes for common joins and queries
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_usage_events_user_id ON usage_events(user_id);
CREATE INDEX idx_usage_events_date ON usage_events(event_date);
CREATE INDEX idx_support_tickets_user_id ON support_tickets(user_id);
CREATE INDEX idx_customer_health_user_id ON customer_health(user_id);
CREATE INDEX idx_campaign_attribution_user_id ON campaign_attribution(user_id);
CREATE INDEX idx_experiment_assignments_user_id ON experiment_assignments(user_id);
