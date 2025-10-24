# Print Format Management - Quick Start Guide

## Overview

Print format templates are now managed separately from the JSON fixtures. This allows you to:
- ✅ Edit HTML templates directly without modifying fixtures
- ✅ Keep templates organized and version-controlled
- ✅ Easily update fixtures from HTML files
- ✅ Add new formats without manual JSON editing

## Location

```
erpnext_utils/
├── print_formats/                    ← Edit HTML files here
│   ├── README.md                     ← Full documentation
│   ├── manage_formats.py            ← Management utility
│   ├── __init__.py
│   ├── cash_payment_voucher.html    ← Cash Payment Voucher template
│   └── delivery_challan.html        ← Delivery Challan template
├── fixtures/
│   └── print_format.json            ← Generated from HTML files
└── PRINT_FORMAT_SETUP.md            ← This file
```

## Common Tasks

### 1. Update a print format

Edit the HTML file:
```bash
cd /home/frappe/frappe-bench/apps/erpnext_utils/erpnext_utils/print_formats
nano cash_payment_voucher.html    # or your preferred editor
```

Then update the fixture:
```bash
cd /home/frappe/frappe-bench/apps/erpnext_utils
python3 -m erpnext_utils.print_formats.manage_formats --load
```

Deploy the changes:
```bash
cd /home/frappe/frappe-bench
bench migrate erpnext_utils
```

### 2. List all available templates

```bash
cd /home/frappe/frappe-bench/apps/erpnext_utils
python3 -m erpnext_utils.print_formats.manage_formats --list
```

### 3. Update a specific template

```bash
python3 -m erpnext_utils.print_formats.manage_formats --template cash_payment_voucher
```

### 4. Backup current fixture to HTML

```bash
python3 -m erpnext_utils.print_formats.manage_formats --export cash_payment_voucher
```

This creates a backup if the file exists: `cash_payment_voucher.html.bak`

### 5. Get help

```bash
python3 -m erpnext_utils.print_formats.manage_formats --help
```

## File Descriptions

### `cash_payment_voucher.html`
- **Purpose**: Print Cash Payment Vouchers on A5 landscape half-cut pages
- **Size**: A5 Landscape (148mm × 210mm)
- **Contains**: Header, voucher details, accounts table, signatures
- **Edit**: Safe to modify HTML structure and styles

### `delivery_challan.html`
- **Purpose**: Print Delivery Challans on A5 landscape half-cut pages  
- **Size**: A5 Landscape (148mm × 210mm)
- **Contains**: Header, items table with item code and name
- **Edit**: Safe to modify HTML structure and styles

## HTML Editing Tips

### Dynamic Fields (Jinja2 Template Syntax)

Access document fields:
```html
{{ doc.company }}
{{ doc.name }}
```

Format values:
```html
{{ "{:,.2f}".format(doc.amount or 0) }}
{{ frappe.utils.format_date(doc.posting_date, "dd-MM-yyyy") }}
{{ frappe.utils.money_in_words(doc.total or 0) }}
```

Loop through items:
```html
{% for item in doc.items %}
  <tr>
    <td>{{ item.item_code }}</td>
    <td>{{ item.qty }}</td>
  </tr>
{% endfor %}
```

### Example: Add a field to your template

Edit `cash_payment_voucher.html`:
```html
<!-- Add this in the Document Details section -->
<div style="margin-bottom: 10px;">
  <strong>Reference:</strong> {{ doc.reference_no or 'N/A' }}
</div>
```

Then sync with fixture:
```bash
python3 -m erpnext_utils.print_formats.manage_formats --load
```

## Workflow Diagram

```
┌─────────────────────┐
│  Edit HTML file     │
│ (cash_payment_     │
│  voucher.html)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Run manage_formats │
│  with --load flag   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│  Fixture JSON updated      │
│ (print_format.json)        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Deploy: bench migrate      │
│  erpnext_utils              │
└─────────────────────────────┘
```

## Troubleshooting

### Script not found
Make sure you're in the correct directory:
```bash
cd /home/frappe/frappe-bench/apps/erpnext_utils
```

### Permission denied
Add execute permission:
```bash
chmod +x erpnext_utils/print_formats/manage_formats.py
```

### Changes not showing in ERPNext
1. Run the migration:
   ```bash
   cd /home/frappe/frappe-bench
   bench migrate erpnext_utils
   ```

2. Clear browser cache (Ctrl+Shift+Delete in most browsers)

3. If still not showing, restart bench:
   ```bash
   bench restart
   ```

### HTML syntax error
Check your HTML file for unclosed tags and proper quote escaping:
```bash
# Validate HTML
python3 -c "import html.parser; html.parser.HTMLParser().feed(open('cash_payment_voucher.html').read())"
```

## Adding New Print Formats

1. Create a new HTML file in `print_formats/` directory:
   ```bash
   touch check_print.html
   ```

2. Edit `manage_formats.py` and add to the `templates` dictionary:
   ```python
   'check_print': {
       'html_file': 'check_print.html',
       'fixture_name': 'Check - Print Format',
       'doc_type': 'Check'
   }
   ```

3. Create your HTML template in `check_print.html`

4. Load it:
   ```bash
   python3 -m erpnext_utils.print_formats.manage_formats --template check_print
   ```

## Support & Documentation

- **Detailed docs**: See `print_formats/README.md`
- **Frappe template guide**: https://frappeframework.com/docs/v14/user/guides/customization/print-formats
- **Jinja2 documentation**: https://jinja.palletsprojects.com/

## Version Info

- **System**: ERPNext Print Formats
- **Module**: erpnext_utils
- **Last Updated**: 2025-01-27
- **Formats**: 2 (Cash Payment Voucher, Delivery Challan)
