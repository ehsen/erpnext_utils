# Comprehensive Logging Guide: Payment Entry Cheque Override

## Overview

This document describes the comprehensive logging system implemented for the Payment Entry cheque record creation feature. All major workflow steps, validations, and decisions are logged for debugging and monitoring purposes.

## Log Categories & Prefixes

The logging system uses categorized prefixes to help identify and filter log messages:

| Prefix | Purpose | Logged By | Log Level |
|--------|---------|-----------|-----------|
| `[Cheque Validation]` | Field and requirement validation | `validate_cheque_details()` | INFO/ERROR |
| `[Cheque Book Validation]` | Cheque book lookup and validation | `validate_and_fetch_cheque_book()` | INFO/ERROR |
| `[Cheque Creation]` | Cheque record creation workflow | `on_submit_cheque_creation()` | INFO |
| `[Cheque Record Creation]` | Actual cheque document creation | `create_cheque_record()` | INFO/ERROR |

## Logging Levels Used

- **INFO**: Normal operational flow, successful validations, key milestones
- **DEBUG**: Detailed field values, intermediate data
- **WARNING**: Fallback operations, optional missing data
- **ERROR**: Validation failures, business logic violations, exceptions

## Log Flow During Validation (Save)

### When Payment Entry is Saved with Cheque Payment

```
1. validate_cheque_details() ENTRY
   ├─ [Cheque Validation] validate_cheque_details called for doc PE-2025-00001
   │
   ├─ Check Payment Type
   │  └─ [Cheque Validation] Processing Payment Entry PE-2025-00001 with Payment Type 'Pay'
   │
   ├─ Retrieve Mode of Payment
   │  └─ [Cheque Validation] Mode of Payment retrieved: 'Cheque' for PE-2025-00001
   │
   ├─ Detect Cheque Payment
   │  └─ [Cheque Validation] Mode of Payment 'Cheque' - Is Cheque Payment: True
   │  └─ [Cheque Validation] ✓ Cheque payment detected for PE-2025-00001
   │
   ├─ Validate Fields
   │  ├─ [Cheque Validation] Validating required cheque fields for PE-2025-00001
   │  ├─ [Cheque Validation] ✓ Cheque Number present: CHQ001234
   │  ├─ [Cheque Validation] ✓ Cheque Date present: 2025-03-15
   │  ├─ [Cheque Validation] ✓ Party Type present: Supplier
   │  ├─ [Cheque Validation] ✓ Party present: XYZ Suppliers
   │  └─ [Cheque Validation] All required fields validated for PE-2025-00001
   │
   └─ Validate & Fetch Cheque Book
      └─ validate_and_fetch_cheque_book() ENTRY
         ├─ [Cheque Book Validation] Starting for Payment Entry PE-2025-00001
         ├─ [Cheque Book Validation] Validating bank account: 'ICICI-Main' for PE-2025-00001
         ├─ [Cheque Book Validation] ✓ Bank Account 'ICICI-Main' validated. Account: 1001-Bank
         ├─ [Cheque Book Validation] Searching for cheque book containing cheque #CHQ001234
         ├─ [Cheque Book Validation] ✓ Cheque book found: 'CB-ICICI-2025-Q1' (Range: CHQ000001-CHQ009999, Current: CHQ001233)
         ├─ [Cheque Book Validation] Checking for duplicate cheque #CHQ001234 in cheque book 'CB-ICICI-2025-Q1'
         ├─ [Cheque Book Validation] ✓ Cheque #CHQ001234 is unique - not previously used
         ├─ [Cheque Book Validation] ✓ Stored cheque_book_name: 'CB-ICICI-2025-Q1', bank_account_name: 'ICICI-Main'
         └─ [Cheque Book Validation] ✓ Cheque book validation completed successfully for PE-2025-00001

2. [Cheque Validation] ✓ Cheque validation completed successfully for PE-2025-00001

RESULT: Payment Entry Saved Successfully ✓
```

## Log Flow During Submission

### When Payment Entry is Submitted (Cheque Payment)

```
1. on_submit_cheque_creation() ENTRY
   ├─ [Cheque Creation] on_submit_cheque_creation called for PE-2025-00001
   ├─ [Cheque Creation] Payment Entry PE-2025-00001 is type 'Pay'
   ├─ [Cheque Creation] Mode of Payment: 'Cheque' - Is Cheque: True
   ├─ [Cheque Creation] ✓ Cheque payment confirmed for PE-2025-00001
   │
   └─ create_cheque_record() ENTRY
      ├─ [Cheque Record Creation] Starting cheque record creation for Payment Entry PE-2025-00001
      ├─ [Cheque Record Creation] Creating new Cheque document for PE-2025-00001
      ├─ [Cheque Record Creation] Mapping fields:
      │  ├─ cheque_number: CHQ001234
      │  ├─ cheque_date: 2025-03-15
      │  ├─ party_type: Supplier
      │  ├─ party: XYZ Suppliers
      │  └─ amount: 50000
      ├─ [Cheque Record Creation] ✓ Fields mapped successfully
      ├─ [Cheque Record Creation] Using validated cheque_book_name: 'CB-ICICI-2025-Q1'
      ├─ [Cheque Record Creation] Inserting cheque document with details:
      │  ├─ cheque_number: CHQ001234
      │  ├─ cheque_date: 2025-03-15
      │  ├─ party: XYZ Suppliers (Supplier)
      │  ├─ amount: 50000
      │  ├─ cheque_book: CB-ICICI-2025-Q1
      │  ├─ status: Unpresented
      │  └─ type: Issued
      ├─ [Cheque Record Creation] ✓ Cheque record created successfully: CHQ-00001 (Cheque #CHQ001234, Amount: 50000)
      └─ [Cheque Record Creation] ✓ Cheque linked to Payment Entry PE-2025-00001

2. [Cheque Creation] ✓ Cheque creation completed for PE-2025-00001

RESULT: Payment Entry Submitted + Cheque Created Successfully ✓
```

## Error Scenarios & Logs

### Scenario 1: Missing Cheque Number

```
[Cheque Validation] validate_cheque_details called for doc PE-2025-00002
[Cheque Validation] Processing Payment Entry PE-2025-00002 with Payment Type 'Pay'
[Cheque Validation] Mode of Payment retrieved: 'Cheque' for PE-2025-00002
[Cheque Validation] Mode of Payment 'Cheque' - Is Cheque Payment: True
[Cheque Validation] ✓ Cheque payment detected for PE-2025-00002
[Cheque Validation] Validating required cheque fields for PE-2025-00002
[Cheque Validation] ✗ Missing Cheque Number for PE-2025-00002
→ frappe.throw("Cheque Number (Reference No) is mandatory for Cheque payments")

RESULT: Validation Failed ✗
```

### Scenario 2: Invalid Bank Account

```
[Cheque Book Validation] Starting for Payment Entry PE-2025-00003
[Cheque Book Validation] Validating bank account: 'HDFC-Invalid' for PE-2025-00003
[Cheque Book Validation] ✗ Bank Account 'HDFC-Invalid' not found or not a company account for PE-2025-00003
→ frappe.throw("Bank Account 'HDFC-Invalid' not found or not a company account")

RESULT: Validation Failed ✗
```

### Scenario 3: Duplicate Cheque Number

```
[Cheque Book Validation] Checking for duplicate cheque #CHQ001200 in cheque book 'CB-ICICI-2025-Q1'
[Cheque Book Validation] ✗ Cheque number 'CHQ001200' is already used in cheque book 'CB-ICICI-2025-Q1'. 
    Existing cheque: CHQ-00015 for PE-2025-00002

RESULT: Validation Failed ✗
```

### Scenario 4: Non-Cheque Payment (No Logs)

```
[Cheque Validation] Processing Payment Entry PE-2025-00004 with Payment Type 'Pay'
[Cheque Validation] Mode of Payment retrieved: 'Bank Transfer' for PE-2025-00004
[Cheque Validation] Mode of Payment 'Bank Transfer' - Is Cheque Payment: False
[Cheque Validation] Payment mode 'Bank Transfer' is not a cheque payment. Skipping validation.

RESULT: No Cheque Processing (Expected) ✓
```

### Scenario 5: Exception During Cheque Creation

```
[Cheque Record Creation] Starting cheque record creation for Payment Entry PE-2025-00005
[Cheque Record Creation] Creating new Cheque document for PE-2025-00005
[Cheque Record Creation] Mapping fields: [...]
[Cheque Record Creation] ✓ Fields mapped successfully
[Cheque Record Creation] Using validated cheque_book_name: 'CB-ICICI-2025-Q1'
[Cheque Record Creation] Inserting cheque document with details: [...]
[Cheque Record Creation] ✗ Error creating cheque record for Payment Entry PE-2025-00005: 
    Database constraint violation: party does not exist
→ Error logged to error log table

RESULT: Exception with Detailed Logging ✗
```

## Viewing Logs

### 1. Real-Time Logs (Console/Terminal)

```bash
# Watch live logs during payment entry operations
bench console
> frappe.logger().get_handler().records  # View recent records
```

### 2. Frappe Error Log

Navigate to: **Frappe > Settings > Logs** or **System > System Error**

Look for entries with titles:
- `Cheque Validation`
- `Cheque Book Validation`
- `Cheque Record Creation Error`

### 3. Database Log

Query the `Error Log` table:

```sql
SELECT * FROM `tabError Log` 
WHERE title LIKE '%Cheque%' 
ORDER BY creation DESC 
LIMIT 20;
```

### 4. File Logs (if configured)

Check `/home/frappe/frappe-bench/logs/` directory for:
- `frappe.log`
- `error.log`
- `bench.log`

### 5. Filter by Category

```python
# In Frappe Console
import frappe

# Get all cheque validation logs
logs = frappe.db.sql("""
    SELECT * FROM `tabError Log`
    WHERE title = 'Cheque Validation'
    AND creation >= NOW() - INTERVAL 1 HOUR
    ORDER BY creation DESC
""", as_dict=True)

for log in logs:
    print(f"{log.creation}: {log.message[:100]}...")
```

## Debug Mode - Enhanced Logging

To enable DEBUG level logging (shows field values):

### Option 1: Enable Debug Mode in Frappe

```python
# In Frappe Console
frappe.conf.debug = True
frappe.logger().setLevel('DEBUG')
```

### Option 2: Configure logging.conf

Edit `config/logging.conf`:

```ini
[logger_frappe]
level = DEBUG
```

Then restart Frappe:
```bash
bench restart
```

### Option 3: Runtime Configuration

Add to `payment_entry.py` at start:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Log Analysis Tips

### 1. Identify Performance Issues

Look for timestamp differences:

```
[Cheque Book Validation] Searching for cheque book... 14:05:32.123
[Cheque Book Validation] ✓ Cheque book found... 14:05:32.654  # 531ms - slower query
```

### 2. Track Cheque Number Reuse

Search logs for all uses of a specific cheque number:

```python
frappe.db.sql("""
    SELECT * FROM `tabError Log`
    WHERE message LIKE '%CHQ001234%'
    ORDER BY creation DESC
""")
```

### 3. Monitor Validation Failures

Count validation errors by type:

```python
import frappe
from collections import Counter

logs = frappe.db.sql("""
    SELECT message FROM `tabError Log`
    WHERE title = 'Cheque Validation'
    AND creation >= NOW() - INTERVAL 24 HOUR
""", as_list=True)

error_types = Counter([log[0].split('✗')[-1].strip() if '✗' in log[0] else 'Unknown' for log in logs])
print(error_types)
```

### 4. Track Successful Creations

Find all successfully created cheques:

```python
logs = frappe.db.sql("""
    SELECT message FROM `tabError Log`
    WHERE title = 'Cheque Record Creation'
    AND message LIKE '%successfully%'
    AND creation >= NOW() - INTERVAL 7 DAY
    ORDER BY creation DESC
""")
```

## Log Retention & Cleanup

### View Log Retention Settings

```python
frappe.get_single("System Settings").error_log_batch_size
# Default: 500 records
```

### Manual Cleanup (Old Logs)

```python
# Delete logs older than 30 days
import frappe
from datetime import datetime, timedelta

old_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')

frappe.db.sql(f"""
    DELETE FROM `tabError Log`
    WHERE title LIKE '%Cheque%'
    AND creation < '{old_date}'
""")
frappe.db.commit()
```

## Dashboard Query

Create a dashboard widget to monitor cheque operations:

```python
# In a Report or Dashboard Script
import frappe
from datetime import datetime, timedelta

today = datetime.now().strftime('%Y-%m-%d')

stats = {
    'Total Validations': frappe.db.count('Error Log', {
        'title': 'Cheque Validation',
        'creation': ('>=', f'{today} 00:00:00')
    }),
    'Validation Errors': frappe.db.count('Error Log', {
        'title': 'Cheque Validation',
        'message': ('like', '%✗%'),
        'creation': ('>=', f'{today} 00:00:00')
    }),
    'Cheques Created': frappe.db.count('Error Log', {
        'title': 'Cheque Record Creation',
        'message': ('like', '%successfully%'),
        'creation': ('>=', f'{today} 00:00:00')
    }),
    'Creation Errors': frappe.db.count('Error Log', {
        'title': 'Cheque Record Creation Error',
        'creation': ('>=', f'{today} 00:00:00')
    })
}

return stats
```

## Troubleshooting Using Logs

### Issue: Cheque not being created

**Check logs for:**
1. Is `on_submit_cheque_creation()` being called? → Check submission logs
2. Is payment type "Pay"? → Check "Payment Type is" log
3. Is mode of payment detected as cheque? → Check "Is Cheque" log
4. Did creation succeed? → Search for "successfully created"

**Example:**
```python
logs = frappe.db.sql("""
    SELECT message FROM `tabError Log`
    WHERE message LIKE '%CHQ001234%'
    ORDER BY creation DESC
    LIMIT 10
""")
```

### Issue: Validation failing unexpectedly

**Check logs for:**
1. Which field validation failed? → Look for ✗ symbol
2. What was the error message? → Read error log
3. When did it fail? → Check timestamp
4. Has this cheque been used before? → Search duplicate logs

### Issue: Performance degradation

**Check logs for:**
1. How long do cheque book searches take?
2. Are there repeated lookups?
3. Which queries are slowest?

```python
# Enable query logging
frappe.conf.db_query_count_limit = 500
frappe.conf.log_db_queries = True
```

## Best Practices

1. **Monitor Log Growth**: Set up alerts if error log exceeds threshold
2. **Regular Cleanup**: Archive/delete old logs monthly
3. **Alert on Errors**: Set up automated alerts for cheque validation failures
4. **Dashboard**: Create dashboard widget to view daily cheque statistics
5. **Audit Trail**: Use logs as audit trail for cheque operations
6. **Performance Tracking**: Monitor slow database queries

## Summary

The comprehensive logging system provides:

✅ **Full visibility** into cheque validation and creation workflow  
✅ **Easy debugging** with categorized, prefixed log messages  
✅ **Performance monitoring** with timestamp information  
✅ **Error tracking** with detailed error context  
✅ **Audit trail** for compliance and reporting  
✅ **Troubleshooting** capability with rich diagnostic information

Use these logs to monitor, debug, and optimize your cheque payment workflow!
