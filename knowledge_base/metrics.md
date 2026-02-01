# Business Metrics Documentation

## Revenue Metrics

### Monthly Recurring Revenue (MRR)
**Definition**: The predictable revenue generated from active subscriptions normalized to a monthly value.

**Calculation Logic**:
- Sum all active subscription amounts where billing_cycle = 'monthly'
- For annual subscriptions: divide amount by 12
- For quarterly subscriptions: divide amount by 3
- Only include subscriptions with status = 'active'
- Exclude trials (status != 'trial')

**SQL Pattern**:
```sql
SELECT 
    SUM(CASE 
        WHEN billing_cycle = 'monthly' THEN amount
        WHEN billing_cycle = 'annual' THEN amount / 12.0
        WHEN billing_cycle = 'quarterly' THEN amount / 3.0
    END) as mrr
FROM subscriptions
WHERE status = 'active'
```

**Business Context**: MRR is the single most important metric for SaaS businesses. It represents predictable, recurring revenue.

---

### Annual Recurring Revenue (ARR)
**Definition**: MRR multiplied by 12, representing annualized recurring revenue.

**Calculation Logic**:
- ARR = MRR × 12
- Only includes active subscriptions

**SQL Pattern**:
```sql
SELECT (MRR * 12) as arr FROM (
    -- MRR calculation here
)
```

**Business Context**: ARR is used for long-term planning and valuation. Public SaaS companies report ARR.

---

### Average Revenue Per User (ARPU)
**Definition**: Average monthly revenue generated per active user.

**Calculation Logic**:
- ARPU = Total MRR / Number of Active Users
- Active users = users with status = 'active' OR have active subscription

**SQL Pattern**:
```sql
SELECT 
    SUM(mrr) / COUNT(DISTINCT user_id) as arpu
FROM subscriptions
WHERE status = 'active'
```

**Business Context**: ARPU trends indicate pricing power and upsell effectiveness.

---

## Customer Metrics

### Customer Churn Rate
**Definition**: Percentage of customers who cancelled their subscription in a given period.

**Calculation Logic**:
- Monthly Churn = (Customers Lost in Month) / (Customers at Start of Month)
- Only count paying customers (exclude free/trial)
- Time period: typically measured monthly

**SQL Pattern**:
```sql
SELECT 
    COUNT(DISTINCT CASE WHEN status = 'cancelled' 
          AND end_date >= '2024-01-01' 
          AND end_date < '2024-02-01' THEN user_id END) * 1.0 / 
    COUNT(DISTINCT CASE WHEN start_date < '2024-01-01' 
          AND status IN ('active', 'cancelled') THEN user_id END) as churn_rate
FROM subscriptions
```

**Business Context**: Churn rate is inversely correlated with business health. Below 5% monthly is good for SaaS.

---

### Customer Lifetime Value (LTV)
**Definition**: Predicted total revenue from a customer over their entire relationship.

**Calculation Logic**:
- Simple LTV = ARPU / Churn Rate
- Advanced LTV = (ARPU × Gross Margin) / Churn Rate
- Time horizon: typically 3-5 years

**SQL Pattern**:
```sql
SELECT 
    AVG(total_revenue) as ltv
FROM (
    SELECT 
        user_id,
        SUM(amount) as total_revenue
    FROM transactions
    WHERE status = 'success'
    GROUP BY user_id
)
```

**Business Context**: LTV must exceed Customer Acquisition Cost (CAC) for sustainable growth. Target LTV:CAC ratio of 3:1.

---

### Net Revenue Retention (NRR)
**Definition**: Revenue retained from existing customers, including upgrades and downgrades but excluding new customers.

**Calculation Logic**:
- NRR = (Starting MRR + Expansion - Contraction - Churn) / Starting MRR
- Expansion = upgrades from existing customers
- Contraction = downgrades
- Churn = cancellations

**SQL Pattern**:
```sql
SELECT 
    ((starting_mrr + expansion - contraction - churned_mrr) / starting_mrr * 100) as nrr
FROM (
    -- Complex subquery tracking cohort revenue changes
)
```

**Business Context**: NRR > 100% means you're growing revenue from existing customers alone. Best-in-class is 120%+.

---

## Engagement Metrics

### Daily Active Users (DAU)
**Definition**: Unique users who performed at least one meaningful action in the product on a given day.

**Calculation Logic**:
- Count distinct users with usage_events on specific date
- Exclude automated events (API calls without user sessions)
- Common event types: login, feature_use, export

**SQL Pattern**:
```sql
SELECT 
    event_date,
    COUNT(DISTINCT user_id) as dau
FROM usage_events
WHERE event_type IN ('login', 'feature_use', 'export')
    AND event_date = '2024-01-15'
GROUP BY event_date
```

**Business Context**: DAU tracks product stickiness. Compare to MAU for engagement depth.

---

### Feature Adoption Rate
**Definition**: Percentage of users who have used a specific feature at least once.

**Calculation Logic**:
- Adoption Rate = (Users Who Used Feature) / (Total Active Users) × 100
- Time period: typically 30 days or 90 days
- Must join with active users to get denominator

**SQL Pattern**:
```sql
SELECT 
    feature_name,
    COUNT(DISTINCT user_id) * 100.0 / (SELECT COUNT(DISTINCT user_id) FROM users WHERE status = 'active') as adoption_rate
FROM usage_events
WHERE feature_name IS NOT NULL
    AND event_date >= date('now', '-30 days')
GROUP BY feature_name
```

**Business Context**: Low adoption of premium features may indicate onboarding issues or poor feature-market fit.

---

## Support & Health Metrics

### Average Resolution Time
**Definition**: Mean time to resolve support tickets, measured in hours.

**Calculation Logic**:
- Resolution Time = resolved_date - created_date (in hours)
- Only include resolved/closed tickets
- Can segment by priority or category

**SQL Pattern**:
```sql
SELECT 
    AVG(resolution_time_hours) as avg_resolution_time,
    category
FROM support_tickets
WHERE status IN ('resolved', 'closed')
    AND resolution_time_hours IS NOT NULL
GROUP BY category
```

**Business Context**: Fast resolution correlates with customer satisfaction. Target < 24 hours for critical issues.

---

### Customer Health Score
**Definition**: Composite score (0-100) indicating likelihood of renewal/expansion.

**Calculation Logic**:
- Health Score = weighted average of:
  - Engagement Score (40%): product usage frequency
  - Support Score (20%): ticket satisfaction, resolution time
  - Payment Score (20%): payment reliability, no failed charges
  - Adoption Score (20%): feature usage breadth

**SQL Pattern**:
```sql
SELECT 
    user_id,
    (engagement_score * 0.4 + 
     support_score * 0.2 + 
     payment_score * 0.2 + 
     (SELECT COUNT(DISTINCT feature_name) * 10 FROM usage_events WHERE usage_events.user_id = customer_health.user_id) * 0.2) as health_score
FROM customer_health
```

**Business Context**: Health score < 50 indicates high churn risk. Trigger CS intervention at < 40.

---

## Conversion Metrics

### Trial-to-Paid Conversion Rate
**Definition**: Percentage of trial users who convert to paid subscriptions.

**Calculation Logic**:
- Conversion Rate = (Users Who Upgraded to Paid) / (Total Trial Users) × 100
- Track within 14 or 30 days of trial start
- Exclude users still in trial period

**SQL Pattern**:
```sql
SELECT 
    COUNT(DISTINCT CASE WHEN status IN ('active') 
          AND start_date > trial_end_date THEN user_id END) * 100.0 /
    COUNT(DISTINCT CASE WHEN trial_end_date IS NOT NULL THEN user_id END) as conversion_rate
FROM subscriptions
```

**Business Context**: Typical SaaS trial conversion rates range from 10-25%. Benchmark against industry.

---

### Upgrade Rate
**Definition**: Percentage of customers who upgraded to a higher plan tier.

**Calculation Logic**:
- Track plan changes where new plan_tier > old plan_tier
- Measure monthly or quarterly
- Join subscriptions with plans table

**SQL Pattern**:
```sql
SELECT 
    COUNT(DISTINCT s2.user_id) * 100.0 / 
    COUNT(DISTINCT s1.user_id) as upgrade_rate
FROM subscriptions s1
LEFT JOIN subscriptions s2 
    ON s1.user_id = s2.user_id 
    AND s2.start_date > s1.end_date
    AND s2.plan_id IN (SELECT plan_id FROM plans WHERE monthly_price > 
        (SELECT monthly_price FROM plans WHERE plan_id = s1.plan_id))
```

**Business Context**: Upgrade rates indicate value realization. High upgrade = strong product-market fit.

---

## Campaign & Attribution Metrics

### Customer Acquisition Cost (CAC)
**Definition**: Average cost to acquire a new paying customer.

**Calculation Logic**:
- CAC = Total Marketing & Sales Spend / Number of New Customers
- Include campaign budgets from campaigns table
- Time period: typically monthly

**SQL Pattern**:
```sql
SELECT 
    SUM(budget) / COUNT(DISTINCT ca.user_id) as cac
FROM campaigns c
JOIN campaign_attribution ca ON c.campaign_id = ca.campaign_id
WHERE ca.attribution_date BETWEEN '2024-01-01' AND '2024-01-31'
```

**Business Context**: CAC must be < LTV/3 for sustainable growth. Track CAC payback period.

---

### Marketing Channel ROI
**Definition**: Return on investment for each marketing channel.

**Calculation Logic**:
- ROI = (Revenue from Channel - Channel Cost) / Channel Cost × 100
- Revenue = LTV of attributed customers
- Join campaigns, attribution, and transactions

**SQL Pattern**:
```sql
SELECT 
    c.channel,
    (SUM(t.amount) - SUM(c.budget)) / SUM(c.budget) * 100 as roi
FROM campaigns c
JOIN campaign_attribution ca ON c.campaign_id = ca.campaign_id
JOIN transactions t ON ca.user_id = t.user_id
WHERE t.status = 'success'
GROUP BY c.channel
```

**Business Context**: Identify high-ROI channels for budget reallocation. Typical SaaS ROI targets: 300%+.

---

## Time-Based Patterns

### Common Date Filters
- **This Month**: `WHERE strftime('%Y-%m', date_column) = strftime('%Y-%m', 'now')`
- **Last 30 Days**: `WHERE date_column >= date('now', '-30 days')`
- **Last Quarter**: `WHERE date_column >= date('now', '-3 months')`
- **Year-to-Date**: `WHERE strftime('%Y', date_column) = strftime('%Y', 'now')`
- **Month-over-Month**: Compare current month to previous month using LAG window function

### Cohort Analysis Pattern
Group users by signup month and track behavior over time:
```sql
SELECT 
    strftime('%Y-%m', u.signup_date) as cohort_month,
    strftime('%Y-%m', t.transaction_date) as transaction_month,
    COUNT(DISTINCT t.user_id) as active_users,
    SUM(t.amount) as revenue
FROM users u
JOIN transactions t ON u.user_id = t.user_id
GROUP BY cohort_month, transaction_month
ORDER BY cohort_month, transaction_month
```

---

## Business Rules

### Data Quality Rules
1. **Active subscriptions** must have start_date <= current_date and (end_date IS NULL OR end_date > current_date)
2. **MRR calculations** exclude free plans (plan_tier != 'free')
3. **Churn** only counts users who had paid subscriptions (not trials)
4. **Transaction success rate** = successful transactions / total transactions
5. **Revenue** only counts transactions with status = 'success'

### Common Exclusions
- Test accounts (email contains '@test.com' or '@example.com')
- Internal users (company_name = 'Our Company Name')
- Refunded transactions (transaction_type = 'refund' should subtract from revenue)
- Cancelled subscriptions (status = 'cancelled') don't count toward MRR

### Industry Benchmarks
- **SaaS Churn Rate**: 5-7% monthly (good), 3-5% (excellent)
- **NRR**: 90-100% (acceptable), 110%+ (excellent), 120%+ (best-in-class)
- **LTV:CAC Ratio**: 3:1 (minimum), 4:1+ (healthy)
- **CAC Payback**: 12 months (acceptable), 6 months (excellent)
- **Trial Conversion**: 10-15% (typical), 20%+ (excellent)
