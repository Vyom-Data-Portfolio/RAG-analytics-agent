# SQLite-Specific Syntax Rules

**CRITICAL: This database uses SQLite, NOT PostgreSQL or MySQL.**

## Date Functions
SQLite uses different date functions than other databases:

### Month/Year Extraction
```sql
-- Get year-month: strftime('%Y-%m', date_column)
-- Get year: strftime('%Y', date_column)
-- Get month: strftime('%m', date_column)
```

### Date Arithmetic
```sql
-- Last 6 months: date('now', '-6 months')
-- Last year: date('now', '-1 year')
-- Yesterday: date('now', '-1 day')
```

### Monthly Grouping
```sql
GROUP BY strftime('%Y-%m', start_date)
ORDER BY strftime('%Y-%m', start_date)
```

## Common Mistakes to Avoid
❌ DATE_TRUNC() - PostgreSQL only
❌ INTERVAL - PostgreSQL only
❌ generate_series() - PostgreSQL only
❌ NOW() - Use datetime('now') or date('now')

## SQLite Date Examples
```sql
-- MRR by month for last 6 months
SELECT 
  strftime('%Y-%m', start_date) as month,
  SUM(amount) as mrr
FROM subscriptions
WHERE start_date >= date('now', '-6 months')
  AND status = 'active'
GROUP BY strftime('%Y-%m', start_date)
ORDER BY month;

-- Quarterly revenue
SELECT 
  CASE 
    WHEN CAST(strftime('%m', start_date) AS INTEGER) IN (1,2,3) THEN 'Q1'
    WHEN CAST(strftime('%m', start_date) AS INTEGER) IN (4,5,6) THEN 'Q2'
    WHEN CAST(strftime('%m', start_date) AS INTEGER) IN (7,8,9) THEN 'Q3'
    ELSE 'Q4'
  END as quarter,
  SUM(amount) as revenue
FROM subscriptions
GROUP BY quarter;
```