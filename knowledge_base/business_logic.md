# Business Logic & Query Guidelines

## Critical Query Rules

### 1. Revenue Calculations

**Always Normalize to Monthly**
- Monthly subscriptions: use amount as-is
- Annual subscriptions: divide by 12
- Quarterly subscriptions: divide by 3
- Never mix time periods without normalization

**Standard MRR Formula**
```sql
SUM(CASE 
    WHEN billing_cycle = 'monthly' THEN amount
    WHEN billing_cycle = 'annual' THEN amount / 12.0
    WHEN billing_cycle = 'quarterly' THEN amount / 3.0
END)
```

**Only Count Active**
- Revenue queries MUST filter `status = 'active'`
- Exclude `status = 'trial'` from MRR/ARR
- Exclude `status = 'cancelled'` unless analyzing churn

### 2. Customer Counting

**Active Customer Definition**
```sql
WHERE status = 'active' 
AND (end_date IS NULL OR end_date > date('now'))
```

**Prevent Double-Counting**
- Always use `COUNT(DISTINCT user_id)`
- Never count `subscription_id` for customer totals
- Be careful with multi-table joins that can inflate counts

### 3. Transaction Rules

**Revenue Recognition**
```sql
WHERE status = 'success' 
AND transaction_type = 'charge'
```

**Exclude**
- Failed transactions (`status = 'failed'`)
- Pending transactions (`status = 'pending'`)
- Refunds should SUBTRACT: `CASE WHEN transaction_type = 'refund' THEN -amount ELSE amount END`

### 4. Date Handling

**Current Month**
```sql
WHERE date_column >= date('now', 'start of month')
AND date_column < date('now', 'start of month', '+1 month')
```

**Last 30 Days**
```sql
WHERE date_column >= date('now', '-30 days')
```

**Last Quarter**
```sql
WHERE date_column >= date('now', '-3 months')
```

**Year-to-Date**
```sql
WHERE strftime('%Y', date_column) = strftime('%Y', 'now')
```

**NEVER use BETWEEN for dates** - it can include wrong boundaries
**Use >= and <** for precise date ranges

### 5. Churn Calculations

**Monthly Churn Rate**
```sql
Customers Lost in Month / Customers at Start of Month * 100
```

**Important**
- Only count PAYING customers (exclude free/trial)
- Customer must have been active at period start
- Look at `end_date` for cancellations, not `status` change

**Churn Query Pattern**
```sql
SELECT 
    COUNT(DISTINCT CASE 
        WHEN status = 'cancelled' 
        AND end_date >= [start_of_period]
        AND end_date < [end_of_period]
    THEN user_id END) * 100.0 / 
    COUNT(DISTINCT CASE 
        WHEN start_date < [start_of_period]
        AND status IN ('active', 'cancelled')
    THEN user_id END) as churn_rate
FROM subscriptions
```

### 6. Join Best Practices

**User Context**
- Almost always join to `users` table for segmentation
- Use LEFT JOIN when user data might be missing
- Use INNER JOIN when you only want matched records

**Common Join Pattern**
```sql
FROM users u
JOIN subscriptions s ON u.user_id = s.user_id
JOIN plans p ON s.plan_id = p.plan_id
WHERE s.status = 'active'
```

**Multi-Table Joins**
- Join order: users → subscriptions → plans (logical hierarchy)
- Always specify which table each column comes from (u.user_id vs s.user_id)
- Be careful of Cartesian products with many-to-many relationships

### 7. Aggregation Rules

**Group By Requirements**
- Include all non-aggregated columns in GROUP BY
- SQLite is lenient but best practice: `GROUP BY u.user_id, u.email, u.company_name`

**Window Functions for Rankings**
```sql
ROW_NUMBER() OVER (PARTITION BY category ORDER BY value DESC) as rank
```

**Percentiles**
```sql
NTILE(4) OVER (ORDER BY amount) as quartile
```

### 8. NULL Handling

**NULL vs Zero**
- Revenue: NULL means no data, 0 means no revenue
- Use `COALESCE(column, 0)` to convert NULL to zero
- Use `IS NULL` or `IS NOT NULL` for checks, never `= NULL`

**LEFT JOIN NULL Checks**
```sql
LEFT JOIN table2 ON table1.id = table2.foreign_id
WHERE table2.id IS NULL  -- Finds non-matches
```

### 9. Data Quality Filters

**Exclude Test Data**
```sql
WHERE email NOT LIKE '%@test.com'
AND email NOT LIKE '%@example.com'
AND company_name != 'Test Company'
```

**Valid Subscriptions**
```sql
WHERE start_date <= date('now')
AND (end_date IS NULL OR end_date > start_date)
AND amount > 0
```

### 10. Performance Optimization

**Use Indexes**
- Filter on indexed columns first (user_id, date columns, status)
- Avoid functions on indexed columns: `WHERE date(created_at) = '2024-01-01'` is slow
- Better: `WHERE created_at >= '2024-01-01' AND created_at < '2024-01-02'`

**Limit Results**
- Always include `LIMIT` for exploratory queries
- Use `ORDER BY` with `LIMIT` to get "top N"

**Avoid SELECT ***
- Specify only needed columns
- Especially important for tables with JSON or TEXT columns

---

## Common Question Patterns

### "Show me revenue..."
- Default to MRR unless ARR or total specified
- Include time period (default: current month)
- Group by plan tier or segment if not specified

### "How many customers..."
- Count distinct user_id
- Default to active customers
- Add growth trend if "trend" or "over time" mentioned

### "What's our churn..."
- Calculate monthly churn unless otherwise specified
- Show churn rate as percentage
- Optionally break down by cancellation_reason

### "Top 10..." or "Best/Worst..."
- Use ORDER BY with LIMIT
- Clarify metric (revenue, count, rate, etc.)
- Include context columns (customer name, plan, etc.)

### "Compare..." or "Breakdown by..."
- Use GROUP BY for segmentation
- Common segments: plan tier, industry, company size, cohort
- Include totals for each segment

### "Trend" or "Over time"
- Use GROUP BY with date truncation (strftime)
- Default to monthly unless daily/weekly specified
- Order chronologically

---

## Metric Definitions Quick Reference

| Metric | Calculation | Key Filter |
|--------|-------------|-----------|
| MRR | Normalized monthly subscription value | status = 'active' |
| ARR | MRR × 12 | status = 'active' |
| ARPU | MRR / Active Users | status = 'active' |
| Churn Rate | Lost Customers / Starting Customers | Paying customers only |
| LTV | Average total revenue per customer | status = 'success' transactions |
| CAC | Marketing Spend / New Customers | Last 30-90 days |
| NRR | (Starting + Expansion - Churn) / Starting | Cohort-based |
| DAU | Distinct users with events | event_type filters |
| Conversion Rate | Converted / Total × 100 | Depends on funnel |

---

## Edge Cases & Gotchas

### Multiple Subscriptions
- A user can have sequential subscriptions (downgrade → upgrade)
- Only count current active subscription for MRR
- Historical subscriptions relevant for churn analysis

### Free Plans
- Exclude from MRR/ARR (plan_tier != 'free')
- Include in customer count if status = 'active'
- Relevant for conversion funnel analysis

### Annual Billing
- Billing cycle matters for MRR normalization
- Annual customers have lower churn but same MRR impact
- Consider cash flow vs. recognized revenue

### Trials
- Trial users are not paying customers
- Trial conversion is separate metric
- Exclude trials from MRR, include in activation metrics

### Failed Payments
- Don't count as revenue (status != 'success')
- May indicate churn risk
- Track failure_reason for dunning campaigns

### Timezone Considerations
- All timestamps are UTC
- Date comparisons use date(), not datetime
- Be consistent with date ranges

---

## SQL Patterns to AVOID

❌ **Don't use SELECT * in production**
```sql
SELECT * FROM subscriptions  -- Bad
SELECT user_id, amount, status FROM subscriptions  -- Good
```

❌ **Don't mix revenue streams**
```sql
SUM(s.amount + t.amount)  -- Counts revenue twice!
```

❌ **Don't forget DISTINCT for counts**
```sql
COUNT(user_id)  -- Can double-count
COUNT(DISTINCT user_id)  -- Correct
```

❌ **Don't use BETWEEN for date ranges**
```sql
WHERE date BETWEEN '2024-01-01' AND '2024-01-31'  -- Includes wrong times
WHERE date >= '2024-01-01' AND date < '2024-02-01'  -- Correct
```

❌ **Don't compare NULL with =**
```sql
WHERE column = NULL  -- Always false
WHERE column IS NULL  -- Correct
```

---

## When to Use Each Table

| Question Type | Primary Table(s) | Join Requirements |
|---------------|------------------|-------------------|
| Revenue metrics | subscriptions | → plans (for tier) |
| Customer counts | users | → subscriptions (for status) |
| Actual cash flow | transactions | → users (for context) |
| Engagement | usage_events | → users (for segments) |
| Support analysis | support_tickets | → users (for context) |
| Churn prediction | customer_health | → users (for actions) |
| Marketing ROI | campaigns + attribution | → users + transactions |
| A/B testing | experiments + assignments | → users (for segments) |

---

## Query Validation Checklist

Before returning a query, verify:

✅ Filters for active records where appropriate
✅ Uses DISTINCT for user counts
✅ Normalizes billing cycles for revenue
✅ Excludes test/internal data
✅ Handles NULL values appropriately
✅ Uses indexed columns in WHERE clause
✅ Includes relevant time period filters
✅ Groups by all non-aggregated columns
✅ Orders results logically
✅ Limits results for large datasets

---

## Semantic Query Interpretation

### Revenue Questions
- "How much money..." → total revenue from transactions
- "What's our MRR/ARR..." → subscription-based recurring revenue
- "Revenue by..." → GROUP BY with SUM
- "Revenue trend..." → time series GROUP BY

### Customer Questions
- "How many customers..." → COUNT(DISTINCT user_id)
- "Which customers..." → SELECT with user details
- "Top customers..." → ORDER BY with LIMIT
- "Lost customers..." → WHERE status = 'cancelled'

### Comparison Questions
- "X vs Y" → GROUP BY with multiple segments
- "Highest/Lowest" → ORDER BY DESC/ASC with LIMIT
- "Better/Worse" → Include benchmark or comparison metric
- "Breakdown" → GROUP BY categorical column

### Time Questions
- "Last month/week/quarter" → Specific date range
- "This month/week/year" → Current period
- "Trend" → Monthly GROUP BY with ORDER BY date
- "Growth" → Calculate period-over-period change

---

## Natural Language to SQL Translation Examples

**"Who are our best customers?"**
→ Define "best" (highest revenue, longest tenure, most engaged?)
→ Default to highest MRR
→ Include customer details (name, email, company)
→ LIMIT to top 10-20

**"Why are customers churning?"**
→ GROUP BY cancellation_reason
→ Count churned customers per reason
→ Filter for recent period (last 3-6 months)
→ Include percentage breakdown

**"Is our product sticky?"**
→ Calculate DAU/MAU ratio
→ Track feature usage frequency
→ Measure session length/depth
→ Show retention cohorts

**"What's working in marketing?"**
→ Compare CAC by channel
→ Show ROI: (Revenue - Spend) / Spend
→ Identify highest-converting campaigns
→ Track LTV by acquisition channel

**"Should we worry about these customers?"**
→ Filter by health_score < 50
→ Include engagement, support, payment metrics
→ Show MRR at risk
→ Prioritize by account value
