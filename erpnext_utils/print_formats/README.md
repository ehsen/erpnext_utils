# Print Format Templates

This directory contains HTML templates for print formats. These templates are included in the print format fixtures using Frappe's `{% include %}` directive.

## Files

- **cash_payment_voucher.html** - A5 Landscape format for Cash Payment Vouchers
- **delivery_challan.html** - A5 Landscape format for Delivery Challans

## How It Works

The print formats in `fixtures/print_format.json` reference these HTML files using:

```jinja2
{% include 'erpnext_utils/print_formats/cash_payment_voucher.html' %}
```

This allows you to edit the HTML templates directly without modifying the JSON fixture files.

## Editing Print Format Templates

1. **Edit the HTML file** in this directory using your preferred editor:
   ```bash
   nano cash_payment_voucher.html
   # or
   code delivery_challan.html
   ```

2. **Deploy the changes** to ERPNext:
   ```bash
   cd /home/frappe/frappe-bench
   bench migrate erpnext_utils
   ```

3. **Test** the print format in ERPNext by printing a document

That's it! The changes take effect after deploying.

## Tips

- Use **Jinja2 templating** for dynamic content: `{{ doc.field_name }}`
- Frappe functions available: `frappe.utils.format_date()`, `frappe.utils.money_in_words()`, `frappe.get_list()`, etc.
- Keep **CSS inline** for print compatibility
- Test in different browsers for consistent output
- Use **fixed positioning** for headers/footers if needed

## Example: Adding a new field

In `cash_payment_voucher.html`, add this line in the appropriate section:

```html
<div><strong>Reference:</strong> {{ doc.reference_no or 'N/A' }}</div>
```

Then deploy with `bench migrate erpnext_utils`.

## Document Reference

- [Frappe Print Formats](https://frappeframework.com/docs/v14/user/guides/customization/print-formats)
- [Jinja2 Template Documentation](https://jinja.palletsprojects.com/)

## Current Print Formats

### Cash Payment Voucher - Half Page
- **DocType**: Cash Payment Voucher
- **Size**: A5 Landscape
- **File**: `cash_payment_voucher.html`
- **Purpose**: Print vouchers on half-cut A4 pages

### Delivery Challan - Simple Format
- **DocType**: Delivery Note
- **Size**: A5 Landscape
- **File**: `delivery_challan.html`
- **Purpose**: Print delivery notes on half-cut A4 pages
