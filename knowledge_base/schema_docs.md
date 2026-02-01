# Database Schema Documentation

## Table Relationships Overview

```
users (1) ──────┬─── (M) subscriptions ─── (1) plans
                │
                ├─── (M) transactions
                │
                ├─── (M) usage_events
                │
                ├─── (M) support_tickets
                │
                ├─── (M) customer_health
                │
                ├─── (M) campaign_attribution ─── (M) campaigns
                │
                └─── (M) experiment_assignments ─── (M) experiments
```

---

## Core Tables

### users
**Purpose**: Master customer table containing account-level information.

**Key Columns**:
- `user_id` (PK): Unique identifier for each customer account
- `email`: Primary contact email, unique per user
- `company_name`: Organization name (B2B context)
- `industry`: Vertical/sector (Tech, Healthcare, Finance, Retail, etc.)
- `company_size`: Firmographic segmentation (Startup, SMB, Mid-Market, Enterprise)
- `signup_date`: Account creation date (important for cohort analysis)
- `country`: Geographic location (for regional analysis)
- `status`: Current account status
  - 'active': Has active subscription or recent activity
  - 'churned': Cancelled subscription, no longer customer
  - 'trial': Currently in trial period

**Common Joins**:
- Join to `subscriptions` for revenue analysis
- Join to `usage_events` for engagement tracking
- Join to `customer_health` for churn prediction

**Business Context**: This is the source of truth for customer demographics. Use for segmentation analysis.

---

### subscriptions
**Purpose**: Tracks subscription lifecycle including plans, billing, and cancellations.

**Key Columns**:
- `subscription_id` (PK): Unique subscription instance
- `user_id` (FK): Links to customer
- `plan_id` (FK): Links to plan details
- `status`: Subscription state
  - 'active': Currently paying/using
  - 'cancelled': User terminated
  - 'paused': Temporarily suspended
  - 'trial': Free trial period
- `start_date`: Subscription began (activation date)
- `end_date`: NULL for active subscriptions, populated on cancellation
- `billing_cycle`: Payment frequency
  - 'monthly': Charged monthly
  - 'annual': Charged yearly (typically discounted)
  - 'quarterly': Charged every 3 months
- `amount`: Subscription value in dollars
- `trial_end_date`: When trial expires (NULL if direct paid)
- `cancellation_reason`: Why user churned
  - 'price': Too expensive
  - 'features': Missing functionality
  - 'support': Poor customer service
  - 'competition': Switched to competitor
  - 'other': Unspecified

**Common Joins**:
- Join to `users` for customer context
- Join to `plans` for plan tier details
- Join to `transactions` for payment history

**Important Notes**:
- A user can have multiple subscriptions over time (downgrades, upgrades, reactivations)
- For MRR, only include status = 'active'
- Normalize annual amounts by dividing by 12

**Business Context**: Central table for revenue metrics (MRR, ARR, churn). Track status changes for customer lifecycle analysis.

---

### plans
**Purpose**: Master data for subscription plan configurations.

**Key Columns**:
- `plan_id` (PK): Unique plan identifier
- `plan_name`: Human-readable name
  - 'Free': Self-serve tier (limited features)
  - 'Starter': Entry-level paid (for individuals/small teams)
  - 'Professional': Mid-tier (for growing businesses)
  - 'Enterprise': Top-tier (for large organizations)
- `plan_tier`: Categorical grouping
  - 'free', 'basic', 'premium', 'enterprise'
- `monthly_price`: Price if billed monthly
- `annual_price`: Price if billed annually (typically 10-20% discount)
- `max_users`: Seat limit for the plan
- `max_projects`: Resource limit
- `features`: JSON array of included features
- `is_active`: Whether plan is still offered (for legacy plans)

**Common Joins**:
- Join to `subscriptions` to analyze plan distribution

**Business Context**: Reference table for pricing analysis and plan performance. Use to identify upgrade paths.

---

## Transaction Tables

### transactions
**Purpose**: Records all payment events (charges, refunds, failures).

**Key Columns**:
- `transaction_id` (PK): Unique payment event
- `user_id` (FK): Customer who made payment
- `subscription_id` (FK): Related subscription (NULL for one-time charges)
- `amount`: Payment value
- `transaction_type`: Nature of transaction
  - 'charge': Regular payment
  - 'refund': Money returned to customer
  - 'credit': Applied balance/discount
- `status`: Payment outcome
  - 'success': Processed successfully
  - 'failed': Declined/rejected
  - 'pending': Awaiting confirmation
- `payment_method`: How customer paid
  - 'credit_card', 'paypal', 'wire_transfer'
- `transaction_date`: When payment occurred
- `failure_reason`: Why payment failed (for failed status)

**Common Joins**:
- Join to `users` for customer payment behavior
- Join to `subscriptions` for subscription revenue

**Important Notes**:
- Only status = 'success' counts toward revenue
- Refunds should subtract from revenue totals
- Failed payments may indicate churn risk

**Business Context**: Source of truth for actual cash flow. Use for revenue recognition and payment health.

---

## Engagement Tables

### usage_events
**Purpose**: Captures product usage behavior for engagement analysis.

**Key Columns**:
- `event_id` (PK): Unique event occurrence
- `user_id` (FK): User who performed action
- `event_type`: Category of activity
  - 'login': User authentication
  - 'feature_use': Interacted with product feature
  - 'export': Downloaded/exported data
  - 'api_call': Programmatic access
- `feature_name`: Specific feature used
  - 'dashboard', 'reports', 'integrations', 'analytics', 'settings'
- `event_date`: Date of action (for daily aggregation)
- `event_timestamp`: Exact time (for session analysis)
- `session_id`: Groups events within single usage session
- `metadata`: Additional context (JSON format)

**Common Joins**:
- Join to `users` for user-level engagement metrics
- Self-join for funnel analysis

**Business Context**: Track product stickiness and feature adoption. Use to identify power users vs. at-risk users.

---

### support_tickets
**Purpose**: Customer service interactions and issue resolution tracking.

**Key Columns**:
- `ticket_id` (PK): Unique support case
- `user_id` (FK): Customer who opened ticket
- `subject`: Brief issue description
- `category`: Issue classification
  - 'bug': Technical problem
  - 'feature_request': Enhancement request
  - 'billing': Payment/invoice issue
  - 'general': Other inquiries
- `priority`: Urgency level
  - 'low', 'medium', 'high', 'critical'
- `status`: Ticket state
  - 'open', 'in_progress', 'resolved', 'closed'
- `created_date`: When ticket was opened
- `resolved_date`: When issue was solved
- `assigned_to`: Support agent name
- `satisfaction_score`: Customer rating (1-5)
- `resolution_time_hours`: Time to resolve

**Common Joins**:
- Join to `users` for support load analysis
- Join to `customer_health` for health score correlation

**Business Context**: High ticket volume or low satisfaction may predict churn. Track by customer segment.

---

### customer_health
**Purpose**: Aggregated health scoring for proactive churn prevention.

**Key Columns**:
- `health_id` (PK): Unique score record
- `user_id` (FK): Customer being scored
- `score_date`: Date score was calculated
- `health_score`: Overall health (0-100)
  - 0-30: Critical risk
  - 31-50: High risk
  - 51-70: Medium risk
  - 71-85: Healthy
  - 86-100: Excellent
- `engagement_score`: Product usage component (0-100)
- `support_score`: CS satisfaction component (0-100)
- `payment_score`: Billing reliability component (0-100)
- `churn_risk`: Categorical risk level
  - 'low', 'medium', 'high'

**Common Joins**:
- Join to `users` for risk segmentation
- Time-series analysis for trend detection

**Business Context**: Proactive churn prevention. Trigger CS outreach when health_score < 50.

---

## Marketing Tables

### campaigns
**Purpose**: Marketing campaign master data.

**Key Columns**:
- `campaign_id` (PK): Unique campaign identifier
- `campaign_name`: Descriptive name
- `channel`: Marketing channel
  - 'email': Email marketing
  - 'social': Social media ads
  - 'paid_search': Google Ads, etc.
  - 'content': Blog, SEO
  - 'referral': Word-of-mouth/affiliate
- `start_date`, `end_date`: Campaign duration
- `budget`: Total spend allocated
- `target_segment`: Intended audience
- `status`: Campaign state
  - 'active', 'completed', 'paused'

**Common Joins**:
- Join to `campaign_attribution` for performance analysis

**Business Context**: Track marketing spend efficiency and channel ROI.

---

### campaign_attribution
**Purpose**: Links users to the campaigns that acquired them.

**Key Columns**:
- `attribution_id` (PK): Unique attribution record
- `user_id` (FK): Customer acquired
- `campaign_id` (FK): Campaign that drove acquisition
- `attribution_date`: When attribution occurred
- `touchpoint_type`: Attribution model
  - 'first_touch': First interaction
  - 'last_touch': Final interaction before conversion
  - 'multi_touch': Distributed credit

**Common Joins**:
- Join `campaigns` and `users` to analyze CAC by channel
- Join to `transactions` for LTV:CAC ratio

**Business Context**: Essential for marketing ROI analysis. Track which channels drive high-value customers.

---

## Experimentation Tables

### experiments
**Purpose**: A/B test and feature flag configuration.

**Key Columns**:
- `experiment_id` (PK): Unique test identifier
- `experiment_name`: Descriptive test name
- `feature_name`: Feature being tested
- `start_date`, `end_date`: Test duration
- `variant_a_name`: Control group label
- `variant_b_name`: Treatment group label
- `status`: Test state
  - 'active', 'completed', 'paused'

**Common Joins**:
- Join to `experiment_assignments` for results

**Business Context**: Track product experiments for data-driven decisions.

---

### experiment_assignments
**Purpose**: User assignment to experiment variants and conversion tracking.

**Key Columns**:
- `assignment_id` (PK): Unique assignment
- `user_id` (FK): Assigned user
- `experiment_id` (FK): Which experiment
- `variant`: 'A' (control) or 'B' (treatment)
- `assigned_date`: When user entered test
- `converted`: Whether user converted (Boolean)
- `conversion_date`: When conversion occurred

**Common Joins**:
- Join to `experiments` and `users` for conversion analysis
- Aggregate by variant for statistical significance

**Business Context**: Measure feature impact on key metrics (conversion, engagement, retention).

---

## Important Query Patterns

### Active Subscribers
```sql
SELECT * FROM users u
JOIN subscriptions s ON u.user_id = s.user_id
WHERE s.status = 'active'
  AND u.status = 'active'
```

### Customer Cohorts
```sql
SELECT 
    strftime('%Y-%m', signup_date) as cohort,
    COUNT(*) as cohort_size
FROM users
GROUP BY cohort
```

### Multi-Table Revenue Analysis
```sql
SELECT 
    u.industry,
    p.plan_tier,
    COUNT(DISTINCT u.user_id) as customers,
    SUM(s.amount) as total_arr
FROM users u
JOIN subscriptions s ON u.user_id = s.user_id
JOIN plans p ON s.plan_id = p.plan_id
WHERE s.status = 'active'
GROUP BY u.industry, p.plan_tier
```

### Engagement + Revenue
```sql
SELECT 
    u.user_id,
    COUNT(DISTINCT ue.event_date) as active_days,
    SUM(t.amount) as ltv
FROM users u
LEFT JOIN usage_events ue ON u.user_id = ue.user_id
LEFT JOIN transactions t ON u.user_id = t.user_id
WHERE t.status = 'success'
GROUP BY u.user_id
```

---

## Data Types and Formats

### Date Handling
- All dates stored as DATE type (YYYY-MM-DD)
- Timestamps stored as TIMESTAMP (YYYY-MM-DD HH:MM:SS)
- Use `strftime()` for date formatting in SQLite
- Current date: `date('now')`
- Date arithmetic: `date('now', '-30 days')`

### Currency
- All amounts in USD unless specified in `currency` column
- Stored as DECIMAL(10,2) for precision
- No currency conversion in database

### Text Fields
- Status fields use lowercase snake_case
- NULL vs. empty string: NULL indicates missing data, empty string is valid but blank
- JSON fields stored as TEXT, parse with json_extract()

---

## Common Pitfalls

1. **Double-counting revenue**: Don't sum transactions AND subscriptions
2. **Including trials in MRR**: Filter status = 'active', not 'trial'
3. **Forgetting to exclude refunds**: transaction_type = 'refund' should subtract
4. **Incorrect date comparisons**: Use >= and < for date ranges, not BETWEEN
5. **Missing JOINs**: Always join users for segmentation context
6. **Averaging percentages**: Weight averages by cohort size
7. **Time zone issues**: All timestamps are UTC

---

## Index Strategy

**Optimized for**:
- User-centric queries (most tables indexed on user_id)
- Time-series analysis (date columns indexed)
- Status filtering (subscription status, ticket status)

**Query Performance Tips**:
- Always filter on indexed columns first
- Use EXPLAIN QUERY PLAN to verify index usage
- Avoid SELECT * in production queries
- Limit result sets with TOP or LIMIT
