# Logging Quick Reference Card

## 🔍 Log Categories

```
[Cheque Validation]         → Field & requirement checks (validate_cheque_details)
[Cheque Book Validation]    → Cheque book lookups (validate_and_fetch_cheque_book)
[Cheque Creation]           → Submission workflow (on_submit_cheque_creation)
[Cheque Record Creation]    → Document creation (create_cheque_record)
```

## 📊 What Gets Logged

### ✅ On Save (Validation)
- Payment Entry name
- Payment type check
- Mode of payment detection
- Field validations (cheque #, date, party)
- Bank account validation
- Cheque book lookup
- Duplicate cheque check
- Success/failure results

### ✅ On Submit (Creation)
- Cheque record creation start
- Field mapping (reference_no → cheque_number, etc.)
- Cheque book linking
- Document insertion
- Success with new cheque ID
- Amount and details
- Exceptions and errors

## 🔗 Log Search Commands

### Quick SQL Queries

```sql
-- All cheque logs (last 10 entries)
SELECT * FROM `tabError Log` 
WHERE title LIKE '%Cheque%' 
ORDER BY creation DESC LIMIT 10;

-- Only validation logs
SELECT * FROM `tabError Log` 
WHERE title = 'Cheque Validation' 
ORDER BY creation DESC;

-- Only creation logs
SELECT * FROM `tabError Log` 
WHERE title LIKE '%Cheque Record Creation%' 
ORDER BY creation DESC;

-- Errors only
SELECT * FROM `tabError Log` 
WHERE title LIKE '%Cheque%' 
AND message LIKE '%✗%' 
ORDER BY creation DESC;

-- Last 24 hours
SELECT * FROM `tabError Log` 
WHERE title LIKE '%Cheque%' 
AND creation >= NOW() - INTERVAL 24 HOUR 
ORDER BY creation DESC;
```

### Python Console Commands

```python
# Get all cheque validation logs
frappe.db.get_list('Error Log', filters={
    'title': 'Cheque Validation'
}, order_by='creation desc', limit=10)

# Get logs for specific payment entry
frappe.db.sql("""
    SELECT * FROM `tabError Log`
    WHERE message LIKE '%PE-2025-00001%'
    ORDER BY creation DESC
""")

# Count cheque records created today
from datetime import date
frappe.db.count('Error Log', {
    'title': 'Cheque Record Creation',
    'message': ('like', '%successfully%'),
    'creation': ('>=', f'{date.today()} 00:00:00')
})

# Get all errors
frappe.db.sql("""
    SELECT message FROM `tabError Log`
    WHERE title LIKE '%Cheque%'
    AND message LIKE '%✗%'
    ORDER BY creation DESC
    LIMIT 20
""")
```

## 🎯 Common Log Messages

### Success Messages
```
✓ Cheque payment detected for PE-2025-00001
✓ Cheque Number present: CHQ001234
✓ Bank Account validated
✓ Cheque book found: 'CB-ICICI-2025-Q1'
✓ Cheque #CHQ001234 is unique
✓ Cheque record created successfully: CHQ-00001
```

### Error Messages
```
✗ Missing Cheque Number
✗ Missing Cheque Date
✗ Bank Account not found or not a company account
✗ No active cheque book found for Bank Account
✗ Cheque number already used in cheque book
✗ Error creating cheque record: [error details]
```

### Info Messages
```
Skipping validation for PE-2025-00002 - Payment Type is 'Receive'
Payment mode 'Bank Transfer' is not a cheque payment
No mode of payment found - skipping cheque validation
```

## 📈 Performance Indicators

```
[Timestamp] Action takes [duration]ms
[14:05:32.123] → [14:05:32.654] = 531ms (slow query!)
```

## 🐛 Debugging Workflow

**Step 1: Check if function is called**
```sql
SELECT * FROM `tabError Log` 
WHERE title LIKE 'Cheque%'
AND message LIKE '%PE-2025-00001%' LIMIT 5;
```

**Step 2: Identify where it failed**
```
Search for: ✗ symbol in messages
```

**Step 3: Get error details**
```sql
SELECT message FROM `tabError Log`
WHERE title LIKE '%Cheque%'
AND message LIKE '%✗%'
AND message LIKE '%PE-2025-00001%';
```

**Step 4: Check successful completions**
```sql
SELECT message FROM `tabError Log`
WHERE title LIKE '%Cheque%'
AND message LIKE '%successfully%'
AND message LIKE '%PE-2025-00001%';
```

## 🚨 Alert Triggers

Create alerts for:
1. **Error Rate High**: > 10% validation failures
2. **Missing Logs**: No logs for submitted payment entries
3. **Slow Operations**: Single operation > 1000ms
4. **Duplicate Cheques**: Multiple uses of same number

## 📋 Monitoring Checklist

- [ ] Check daily cheque validation stats
- [ ] Monitor error rate trend
- [ ] Review slow queries
- [ ] Clean up old logs (> 30 days)
- [ ] Verify cheque books are being linked
- [ ] Check for orphaned payment entries

## 🔐 Access Permissions

To view logs, user needs:
- `read` permission on Error Log
- Role: System Manager or Auditor (recommended)

## 💾 Log Retention

**Default**: 500 error log records  
**Cleanup**: Delete logs older than 30 days monthly  
**Archive**: Consider archiving old logs for audit trail

## 📞 Support Info

**For issues, check:**
1. Log messages for ✗ errors
2. Database queries work
3. Payment Entry fields are populated
4. Cheque book exists and is active

**When reporting issues, include:**
1. Payment Entry name
2. Timestamp from logs
3. Full error message
4. Cheque number being used

---

**Pro Tip**: Search logs for payment entry name (e.g., "PE-2025-00001") to get complete workflow trace!
