"""
Enhanced Synthetic Data Generator for RAG Analytics Agent
Generates realistic SaaS data for all 10 tables with proper relationships
"""

import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker
import json

fake = Faker()
Faker.seed(None)  # Change 42 to None
random.seed(None)  # Change 42 to None

class SaaSDataGenerator:
    """Generates realistic SaaS analytics data"""
    
    def __init__(self, db_path="saas_analytics.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Configuration
        self.num_users = 1000
        self.num_campaigns = 20
        self.num_experiments = 5
        
        # Reference data
        self.industries = ['Tech', 'Healthcare', 'Finance', 'Retail', 'Education', 'Manufacturing']
        self.company_sizes = ['Startup', 'SMB', 'Mid-Market', 'Enterprise']
        self.countries = ['US', 'UK', 'Canada', 'Germany', 'France', 'Australia']
        self.plan_tiers = ['free', 'basic', 'premium', 'enterprise']
        self.channels = ['email', 'social', 'paid_search', 'content', 'referral']
        self.features = ['dashboard', 'reports', 'integrations', 'analytics', 'api', 'settings']
        
        print(f"🔨 Creating database: {db_path}")
        
    def create_schema(self):
        """Create all tables"""
        print("📋 Creating schema...")
        
        # Drop existing tables
        tables = ['experiment_assignments', 'experiments', 'campaign_attribution', 
                  'campaigns', 'customer_health', 'support_tickets', 'usage_events',
                  'transactions', 'subscriptions', 'plans', 'users']
        
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
        
        # Users table
        self.cursor.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                company_name TEXT,
                industry TEXT,
                company_size TEXT,
                signup_date DATE NOT NULL,
                country TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Plans table
        self.cursor.execute("""
            CREATE TABLE plans (
                plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_name TEXT NOT NULL,
                plan_tier TEXT NOT NULL,
                monthly_price DECIMAL(10,2) NOT NULL,
                annual_price DECIMAL(10,2) NOT NULL,
                max_users INTEGER,
                max_projects INTEGER,
                features TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Subscriptions table
        self.cursor.execute("""
            CREATE TABLE subscriptions (
                subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                billing_cycle TEXT,
                amount DECIMAL(10,2) NOT NULL,
                currency TEXT DEFAULT 'USD',
                trial_end_date DATE,
                cancellation_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (plan_id) REFERENCES plans(plan_id)
            )
        """)
        
        # Transactions table
        self.cursor.execute("""
            CREATE TABLE transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subscription_id INTEGER,
                amount DECIMAL(10,2) NOT NULL,
                transaction_type TEXT,
                status TEXT,
                payment_method TEXT,
                transaction_date DATE NOT NULL,
                currency TEXT DEFAULT 'USD',
                stripe_charge_id TEXT,
                failure_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
            )
        """)
        
        # Usage events table
        self.cursor.execute("""
            CREATE TABLE usage_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                feature_name TEXT,
                event_date DATE NOT NULL,
                event_timestamp TIMESTAMP NOT NULL,
                session_id TEXT,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Support tickets table
        self.cursor.execute("""
            CREATE TABLE support_tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                category TEXT,
                priority TEXT,
                status TEXT,
                created_date DATE NOT NULL,
                resolved_date DATE,
                assigned_to TEXT,
                satisfaction_score INTEGER,
                resolution_time_hours DECIMAL(10,2),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Customer health table
        self.cursor.execute("""
            CREATE TABLE customer_health (
                health_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                score_date DATE NOT NULL,
                health_score INTEGER,
                engagement_score INTEGER,
                support_score INTEGER,
                payment_score INTEGER,
                churn_risk TEXT,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Campaigns table
        self.cursor.execute("""
            CREATE TABLE campaigns (
                campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_name TEXT NOT NULL,
                channel TEXT,
                start_date DATE NOT NULL,
                end_date DATE,
                budget DECIMAL(10,2),
                target_segment TEXT,
                status TEXT
            )
        """)
        
        # Campaign attribution table
        self.cursor.execute("""
            CREATE TABLE campaign_attribution (
                attribution_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                campaign_id INTEGER NOT NULL,
                attribution_date DATE NOT NULL,
                touchpoint_type TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
            )
        """)
        
        # Experiments table
        self.cursor.execute("""
            CREATE TABLE experiments (
                experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_name TEXT NOT NULL,
                feature_name TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                variant_a_name TEXT,
                variant_b_name TEXT,
                status TEXT
            )
        """)
        
        # Experiment assignments table
        self.cursor.execute("""
            CREATE TABLE experiment_assignments (
                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                experiment_id INTEGER NOT NULL,
                variant TEXT,
                assigned_date DATE NOT NULL,
                converted BOOLEAN DEFAULT 0,
                conversion_date DATE,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
            )
        """)
        
        self.conn.commit()
        print("✅ Schema created")
    
    def generate_plans(self):
        """Generate subscription plans"""
        print("📦 Generating plans...")
        
        plans = [
            ('Free', 'free', 0, 0, 1, 3, json.dumps(['dashboard']), 1),
            ('Starter', 'basic', 29, 290, 5, 10, json.dumps(['dashboard', 'reports']), 1),
            ('Professional', 'premium', 99, 990, 20, 50, json.dumps(['dashboard', 'reports', 'integrations', 'analytics']), 1),
            ('Enterprise', 'enterprise', 299, 2990, 100, 500, json.dumps(['dashboard', 'reports', 'integrations', 'analytics', 'api', 'priority_support']), 1),
        ]
        
        self.cursor.executemany("""
            INSERT INTO plans (plan_name, plan_tier, monthly_price, annual_price, 
                             max_users, max_projects, features, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, plans)
        
        self.conn.commit()
        print(f"  ✅ Created {len(plans)} plans")
    
    def generate_campaigns(self):
        """Generate marketing campaigns"""
        print("📢 Generating campaigns...")
        
        campaigns = []
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(self.num_campaigns):
            start_date = base_date + timedelta(days=random.randint(0, 300))
            channel = random.choice(self.channels)
            
            campaign = (
                f"{channel.title()} Campaign Q{random.randint(1,4)} 2024",
                channel,
                start_date.date(),
                (start_date + timedelta(days=random.randint(30, 90))).date(),
                random.randint(5000, 50000),
                random.choice(self.company_sizes),
                random.choice(['active', 'completed'])
            )
            campaigns.append(campaign)
        
        self.cursor.executemany("""
            INSERT INTO campaigns (campaign_name, channel, start_date, end_date, 
                                 budget, target_segment, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, campaigns)
        
        self.conn.commit()
        print(f"  ✅ Created {len(campaigns)} campaigns")
    
    def generate_experiments(self):
        """Generate A/B test experiments"""
        print("🧪 Generating experiments...")
        
        experiments = [
            ('New Dashboard Layout', 'dashboard', '2024-01-15', '2024-02-15', 'Control', 'New Layout', 'completed'),
            ('Onboarding Flow V2', 'onboarding', '2024-02-01', '2024-03-01', 'Old Flow', 'New Flow', 'completed'),
            ('Pricing Page Redesign', 'pricing', '2024-03-01', None, 'Current', 'Redesign', 'active'),
            ('Email Notification Timing', 'notifications', '2024-01-20', '2024-02-20', 'Morning', 'Evening', 'completed'),
            ('Mobile App Navigation', 'mobile_nav', '2024-02-15', None, 'Bottom Nav', 'Side Menu', 'active'),
        ]
        
        self.cursor.executemany("""
            INSERT INTO experiments (experiment_name, feature_name, start_date, end_date,
                                   variant_a_name, variant_b_name, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, experiments)
        
        self.conn.commit()
        print(f"  ✅ Created {len(experiments)} experiments")
    
    def generate_users(self):
        """Generate user accounts"""
        print(f"👥 Generating {self.num_users} users...")
        
        users = []
        base_date = datetime.now() - timedelta(days=730)  # 2 years ago
        
        for i in range(self.num_users):
            signup_date = base_date + timedelta(days=random.randint(0, 700))
            
            # 70% active, 25% churned, 5% trial
            status = random.choices(
                ['active', 'churned', 'trial'],
                weights=[70, 25, 5]
            )[0]
            
            user = (
                fake.unique.email(),
                fake.company(),
                random.choice(self.industries),
                random.choice(self.company_sizes),
                signup_date.date(),
                random.choice(self.countries),
                status
            )
            users.append(user)
        
        self.cursor.executemany("""
            INSERT INTO users (email, company_name, industry, company_size, 
                             signup_date, country, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, users)
        
        self.conn.commit()
        print(f"  ✅ Created {len(users)} users")
    
    def generate_subscriptions(self):
        """Generate subscriptions for users"""
        print("💳 Generating subscriptions...")
        
        self.cursor.execute("SELECT user_id, signup_date, status FROM users")
        users = self.cursor.fetchall()
        
        subscriptions = []
        
        for user_id, signup_date, status in users:
            # Skip 10% of users (free tier only)
            if random.random() < 0.1:
                continue
            
            # Choose plan based on company size (stored in users table)
            self.cursor.execute("""
                SELECT company_size FROM users WHERE user_id = ?
            """, (user_id,))
            company_size = self.cursor.fetchone()[0]
            
            if company_size == 'Enterprise':
                plan_id = 4
            elif company_size == 'Mid-Market':
                plan_id = random.choice([3, 4])
            elif company_size == 'SMB':
                plan_id = random.choice([2, 3])
            else:  # Startup
                plan_id = random.choice([1, 2])
            
            # Get plan details
            self.cursor.execute("""
                SELECT monthly_price, annual_price FROM plans WHERE plan_id = ?
            """, (plan_id,))
            monthly_price, annual_price = self.cursor.fetchone()
            
            # Billing cycle
            billing_cycle = random.choices(
                ['monthly', 'annual', 'quarterly'],
                weights=[50, 40, 10]
            )[0]
            
            if billing_cycle == 'monthly':
                amount = monthly_price
            elif billing_cycle == 'annual':
                amount = annual_price
            else:  # quarterly
                amount = monthly_price * 3 * 0.95  # 5% discount
            
            # Subscription dates
            start_date = datetime.strptime(signup_date, '%Y-%m-%d')
            
            if status == 'trial':
                sub_status = 'trial'
                trial_end = start_date + timedelta(days=14)
                end_date = None
            elif status == 'churned':
                sub_status = 'cancelled'
                trial_end = None
                # Churned sometime in the past 6 months
                end_date = start_date + timedelta(days=random.randint(30, 365))
                cancellation_reason = random.choice([
                    'price', 'features', 'support', 'competition', 'other'
                ])
            else:  # active
                sub_status = 'active'
                trial_end = None
                end_date = None
                cancellation_reason = None
            
            subscription = (
                user_id,
                plan_id,
                sub_status,
                start_date.date(),
                end_date.date() if end_date else None,
                billing_cycle,
                amount,
                'USD',
                trial_end.date() if trial_end else None,
                cancellation_reason if status == 'churned' else None
            )
            subscriptions.append(subscription)
        
        self.cursor.executemany("""
            INSERT INTO subscriptions (user_id, plan_id, status, start_date, end_date,
                                     billing_cycle, amount, currency, trial_end_date,
                                     cancellation_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, subscriptions)
        
        self.conn.commit()
        print(f"  ✅ Created {len(subscriptions)} subscriptions")
    
    def generate_transactions(self):
        """Generate payment transactions"""
        print("💰 Generating transactions...")
        
        self.cursor.execute("""
            SELECT s.subscription_id, s.user_id, s.start_date, s.amount, s.billing_cycle, s.status
            FROM subscriptions s
            WHERE s.status IN ('active', 'cancelled')
        """)
        subscriptions = self.cursor.fetchall()
        
        transactions = []
        
        for sub_id, user_id, start_date, amount, billing_cycle, status in subscriptions:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            
            # Generate transactions from start until now (or cancellation)
            current_date = start
            end_date = datetime.now()
            
            # Determine billing interval
            if billing_cycle == 'monthly':
                interval = 30
            elif billing_cycle == 'annual':
                interval = 365
            else:  # quarterly
                interval = 90
            
            while current_date < end_date:
                # 95% success rate
                trans_status = 'success' if random.random() < 0.95 else 'failed'
                
                transaction = (
                    user_id,
                    sub_id,
                    amount,
                    'charge',
                    trans_status,
                    random.choice(['credit_card', 'paypal', 'wire_transfer']),
                    current_date.date(),
                    'USD',
                    f"ch_{fake.uuid4()[:24]}",
                    'insufficient_funds' if trans_status == 'failed' else None
                )
                transactions.append(transaction)
                
                current_date += timedelta(days=interval)
                
                # Stop if subscription was cancelled
                if status == 'cancelled' and random.random() < 0.3:
                    break
        
        self.cursor.executemany("""
            INSERT INTO transactions (user_id, subscription_id, amount, transaction_type,
                                    status, payment_method, transaction_date, currency,
                                    stripe_charge_id, failure_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, transactions)
        
        self.conn.commit()
        print(f"  ✅ Created {len(transactions)} transactions")
    
    def generate_usage_events(self):
        """Generate product usage events"""
        print("📊 Generating usage events...")
        
        self.cursor.execute("SELECT user_id, signup_date, status FROM users")
        users = self.cursor.fetchall()
        
        events = []
        event_types = ['login', 'feature_use', 'export', 'api_call']
        
        for user_id, signup_date, status in users:
            if status == 'trial':
                num_events = random.randint(5, 20)
            elif status == 'churned':
                num_events = random.randint(10, 50)
            else:  # active
                num_events = random.randint(50, 200)
            
            start = datetime.strptime(signup_date, '%Y-%m-%d')
            
            for _ in range(num_events):
                event_date = start + timedelta(days=random.randint(0, 365))
                
                event = (
                    user_id,
                    random.choice(event_types),
                    random.choice(self.features) if random.random() < 0.7 else None,
                    event_date.date(),
                    event_date,
                    fake.uuid4()[:8]
                )
                events.append(event)
        
        self.cursor.executemany("""
            INSERT INTO usage_events (user_id, event_type, feature_name, event_date,
                                    event_timestamp, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, events)
        
        self.conn.commit()
        print(f"  ✅ Created {len(events)} usage events")
    
    def generate_support_tickets(self):
        """Generate support tickets"""
        print("🎫 Generating support tickets...")
        
        self.cursor.execute("SELECT user_id, signup_date FROM users WHERE status IN ('active', 'churned')")
        users = self.cursor.fetchall()
        
        tickets = []
        categories = ['bug', 'feature_request', 'billing', 'general']
        priorities = ['low', 'medium', 'high', 'critical']
        statuses = ['open', 'in_progress', 'resolved', 'closed']
        
        # 30% of users have tickets
        for user_id, signup_date in random.sample(users, int(len(users) * 0.3)):
            num_tickets = random.randint(1, 5)
            
            for _ in range(num_tickets):
                created = datetime.strptime(signup_date, '%Y-%m-%d') + timedelta(days=random.randint(1, 365))
                status = random.choice(statuses)
                
                if status in ['resolved', 'closed']:
                    resolved = created + timedelta(hours=random.randint(1, 72))
                    resolution_hours = (resolved - created).total_seconds() / 3600
                    satisfaction = random.randint(3, 5)
                else:
                    resolved = None
                    resolution_hours = None
                    satisfaction = None
                
                ticket = (
                    user_id,
                    fake.sentence(nb_words=6),
                    random.choice(categories),
                    random.choice(priorities),
                    status,
                    created.date(),
                    resolved.date() if resolved else None,
                    fake.name(),
                    satisfaction,
                    resolution_hours
                )
                tickets.append(ticket)
        
        self.cursor.executemany("""
            INSERT INTO support_tickets (user_id, subject, category, priority, status,
                                        created_date, resolved_date, assigned_to,
                                        satisfaction_score, resolution_time_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tickets)
        
        self.conn.commit()
        print(f"  ✅ Created {len(tickets)} support tickets")
    
    def generate_customer_health(self):
        """Generate customer health scores"""
        print("❤️  Generating customer health scores...")
        
        self.cursor.execute("SELECT user_id FROM users WHERE status = 'active'")
        active_users = [row[0] for row in self.cursor.fetchall()]
        
        health_records = []
        
        for user_id in active_users:
            # Generate monthly health scores for past 6 months
            for months_ago in range(6):
                score_date = datetime.now() - timedelta(days=30 * months_ago)
                
                engagement = random.randint(40, 100)
                support = random.randint(60, 100)
                payment = random.randint(80, 100)
                
                health_score = int((engagement * 0.4 + support * 0.2 + payment * 0.4))
                
                if health_score >= 80:
                    risk = 'low'
                elif health_score >= 60:
                    risk = 'medium'
                else:
                    risk = 'high'
                
                health_records.append((
                    user_id,
                    score_date.date(),
                    health_score,
                    engagement,
                    support,
                    payment,
                    risk
                ))
        
        self.cursor.executemany("""
            INSERT INTO customer_health (user_id, score_date, health_score,
                                        engagement_score, support_score, payment_score,
                                        churn_risk)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, health_records)
        
        self.conn.commit()
        print(f"  ✅ Created {len(health_records)} health records")
    
    def generate_campaign_attribution(self):
        """Generate campaign attribution"""
        print("🎯 Generating campaign attribution...")
        
        self.cursor.execute("SELECT user_id, signup_date FROM users")
        users = self.cursor.fetchall()
        
        self.cursor.execute("SELECT campaign_id, start_date FROM campaigns")
        campaigns = self.cursor.fetchall()
        
        attributions = []
        
        # Attribute 70% of users to campaigns
        for user_id, signup_date in random.sample(users, int(len(users) * 0.7)):
            # Find campaigns that were active before signup
            signup = datetime.strptime(signup_date, '%Y-%m-%d')
            valid_campaigns = [
                (cid, start) for cid, start in campaigns
                if datetime.strptime(start, '%Y-%m-%d') <= signup
            ]
            
            if valid_campaigns:
                campaign_id, _ = random.choice(valid_campaigns)
                
                attribution = (
                    user_id,
                    campaign_id,
                    signup_date,
                    random.choice(['first_touch', 'last_touch'])
                )
                attributions.append(attribution)
        
        self.cursor.executemany("""
            INSERT INTO campaign_attribution (user_id, campaign_id, attribution_date,
                                             touchpoint_type)
            VALUES (?, ?, ?, ?)
        """, attributions)
        
        self.conn.commit()
        print(f"  ✅ Created {len(attributions)} attributions")
    
    def generate_experiment_assignments(self):
        """Generate experiment assignments"""
        print("🧬 Generating experiment assignments...")
        
        self.cursor.execute("SELECT user_id, signup_date FROM users WHERE status = 'active'")
        users = self.cursor.fetchall()
        
        self.cursor.execute("SELECT experiment_id, start_date FROM experiments")
        experiments = self.cursor.fetchall()
        
        assignments = []
        
        for exp_id, start_date in experiments:
            # Assign 50% of eligible users to experiment
            exp_start = datetime.strptime(start_date, '%Y-%m-%d')
            eligible_users = [
                (uid, signup) for uid, signup in users
                if datetime.strptime(signup, '%Y-%m-%d') <= exp_start
            ]
            
            for user_id, _ in random.sample(eligible_users, int(len(eligible_users) * 0.5)):
                variant = random.choice(['A', 'B'])
                converted = random.random() < 0.15  # 15% conversion rate
                
                assignment = (
                    user_id,
                    exp_id,
                    variant,
                    start_date,
                    1 if converted else 0,
                    (exp_start + timedelta(days=random.randint(1, 30))).date() if converted else None
                )
                assignments.append(assignment)
        
        self.cursor.executemany("""
            INSERT INTO experiment_assignments (user_id, experiment_id, variant,
                                               assigned_date, converted, conversion_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, assignments)
        
        self.conn.commit()
        print(f"  ✅ Created {len(assignments)} assignments")
    
    def generate_all(self):
        """Generate all data"""
        print("\n" + "="*60)
        print("🚀 GENERATING SYNTHETIC SAAS DATA")
        print("="*60 + "\n")
        
        self.create_schema()
        self.generate_plans()
        self.generate_campaigns()
        self.generate_experiments()
        self.generate_users()
        self.generate_subscriptions()
        self.generate_transactions()
        self.generate_usage_events()
        self.generate_support_tickets()
        self.generate_customer_health()
        self.generate_campaign_attribution()
        self.generate_experiment_assignments()
        
        print("\n" + "="*60)
        print("✅ DATA GENERATION COMPLETE!")
        print("="*60)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print database summary"""
        print("\n📊 DATABASE SUMMARY:\n")
        
        tables = [
            'users', 'plans', 'subscriptions', 'transactions',
            'usage_events', 'support_tickets', 'customer_health',
            'campaigns', 'campaign_attribution', 'experiments', 'experiment_assignments'
        ]
        
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            print(f"  {table:25} {count:>8,} rows")
        
        print(f"\n💾 Database saved to: {self.db_path}")
        print("="*60 + "\n")
    
    def close(self):
        """Close database connection"""
        self.conn.close()


if __name__ == "__main__":
    try:
        # Check if faker is installed
        from faker import Faker
    except ImportError:
        print("❌ Error: 'faker' package not found")
        print("Install it with: pip install faker")
        exit(1)
    
    generator = SaaSDataGenerator()
    generator.generate_all()
    generator.close()
    
    print("🎉 Ready to query! Run: python agent_with_rag.py")
