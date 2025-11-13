# Quick Start Guide: Cheque Payments in Payment Entry

## Overview
This guide shows how to create cheque payments in ERPNext Payment Entry with automatic cheque record creation.

## Prerequisites
- ERPNext system is installed
- erpnext_utils app is installed and activated
- Bank Account is set up with active Cheque Book
- Cheque mode of payment is configured
- Vendor/Supplier is created

## Step-by-Step Workflow

### Step 1: Create Payment Entry
1. Go to **Accounting** → **Payment Entry**
2. Click **+ New**
3. Set **Payment Type** to **"Pay"** (for outgoing cheque payments)

### Step 2: Fill Basic Details
1. **Posting Date**: Select the date of payment
2. **Company**: Select your company
3. **Mode of Payment**: Select **"Cheque"** (or any mode containing "Cheque" in the name)
4. **Party Type**: Select **"Supplier"**
5. **Party**: Select the vendor to whom cheque is issued

### Step 3: Fill Banking Details
1. **Company Bank Account** (bank_account): Select the bank account from which cheque will be issued
2. **Paid From**: This will auto-populate from the bank account
3. **Paid To**: Will auto-populate based on party

### Step 4: Fill Cheque Details
1. **Reference No**: Enter the **Cheque Number** (e.g., "CHQ12345")
   - Must be a valid number in the active cheque book
   - Cannot be duplicate
2. **Reference Date**: Enter the **Cheque Date**
   - Date when cheque is issued
3. **Amount**: Enter the payment amount

### Step 5: Add Payment References (Optional)
1. Click **"Get Outstanding Invoices"** to fetch unpaid invoices
2. Select invoices to allocate the cheque payment against
3. Confirm allocated amounts

### Step 6: Save & Validate
1. Click **Save**
2. System will validate:
   - ✅ Cheque number is provided
   - ✅ Cheque date is provided
   - ✅ Party information is complete
   - ✅ Bank account exists and is active
   - ✅ Cheque number exists in active cheque book
   - ✅ Cheque number is not already used
3. If any validation fails, error message will appear

### Step 7: Submit Payment Entry
1. Click **Submit** button
2. System will:
   - ✅ Create GL entries for the payment
   - ✅ Automatically create a **Cheque Record**
   - ✅ Link cheque to the cheque book
   - ✅ Set cheque status to "Unpresented"
3. Payment Entry is now submitted

### Step 8: Verify Cheque Record
1. After submission, a Cheque record is automatically created
2. To verify:
   - Go to **Accounting** → **Cheque**
   - Search for your cheque number
   - Verify all details match:
     - Cheque Number
     - Cheque Date
     - Party (Vendor)
     - Amount
     - Status: "Unpresented"
     - Type: "Issued"
     - Cheque Book link

## Common Validation Errors & Solutions

### Error: "Cheque Number (Reference No) is mandatory"
**Solution**: Fill in the Reference No field with the cheque number

### Error: "Cheque Date (Reference Date) is mandatory"
**Solution**: Fill in the Reference Date field with the cheque date

### Error: "Bank Account 'X' not found or not a company account"
**Solution**: 
- Verify the Bank Account exists
- Ensure it's marked as "Company Account" in Bank Account settings

### Error: "No active cheque book found for Bank Account 'X'"
**Solution**:
- Ensure a Cheque Book exists for the selected bank account
- Verify the cheque book is marked as "Active" (is_active = 1)
- Ensure the cheque number falls within the cheque book's range

### Error: "Cheque number 'X' is already used"
**Solution**: Use a different, unused cheque number from the cheque book

## What Happens Automatically

When you submit a cheque Payment Entry, the system automatically:

1. **Creates Cheque Record** with:
   - Cheque number (from Reference No)
   - Cheque date (from Reference Date)
   - Vendor information
   - Payment amount
   - Status: "Unpresented"
   - Type: "Issued"
   - Linked to cheque book

2. **Creates GL Entries** for:
   - Bank account (credit)
   - Vendor payable account (debit)
   - Associated invoice accounts

3. **Updates Outstanding Amounts** on referenced invoices

## Important Notes

### ✅ What Gets Created
- One Cheque Record per Payment Entry
- GL Entries for accounting
- Links between Payment Entry → Cheque → Cheque Book

### ❌ What's NOT Automatic (Yet)
- Post-dated cheque GL entries (future feature)
- Cheque status updates on clearing (future feature)
- Cheque cancellation on Payment Entry cancellation (future feature)

### 📌 Key Points
- Only "Pay" type payments create cheque records
- "Receive" and "Internal Transfer" payments are NOT affected
- Cheque detection is based on Mode of Payment name
- Each cheque number can only be used once per cheque book
- Cheque status starts as "Unpresented" and must be tracked manually

## Example Scenario

**Company**: ABC Corp  
**Vendor**: XYZ Suppliers  
**Amount**: 50,000 INR  
**Cheque Number**: CHQ001234  
**Date**: 2025-03-15  
**Bank Account**: ABC Corp - ICICI Bank Main

### Payment Entry Form
```
Payment Type: Pay
Posting Date: 2025-03-15
Company: ABC Corp
Mode of Payment: Cheque
Party Type: Supplier
Party: XYZ Suppliers

Paid From: 1001 - Bank Account (ICICI)
Paid To: 2001 - Creditors Account
Paid Amount: 50,000

Reference No: CHQ001234
Reference Date: 2025-03-15
Company Bank Account: ABC Corp - ICICI Bank Main
```

### After Submission
✅ Payment Entry: PE-2025-00001 (Submitted)  
✅ Cheque Record: Created automatically  
   - Number: CHQ001234
   - Status: Unpresented
   - Amount: 50,000
   - Bank: ICICI Bank Main
   - Cheque Book: ICICI-2025-Q1

## Troubleshooting

### Cheque record not created after submission?
- Check if Payment Type is "Pay"
- Check if Mode of Payment contains "Cheque"
- Check browser console for error messages
- Review cheque validation errors

### Can't save Payment Entry?
- Ensure all required fields are filled
- Verify cheque number is in the correct format
- Check if cheque number already exists
- Verify bank account is active

### Can't find the cheque record?
- Wait a moment (system might still be processing)
- Go to **Accounting** → **Cheque**
- Search by cheque number
- Filter by cheque date or vendor

## Next Steps

1. **Track Cheque Status**: Monitor when cheques are presented and cleared
2. **Bank Reconciliation**: Match cheque records with bank statements
3. **Generate Reports**: Create reports on cheque payments and status
4. **Set Up Post-Dated Cheques**: For future-dated payments (when feature is available)

## Support

For issues or feature requests:
- Check the `CHEQUE_IMPLEMENTATION.md` for detailed documentation
- Review error messages carefully - they suggest solutions
- Contact system administrator if system-level configuration is needed

---

**Happy Cheque Processing!** 🏦

