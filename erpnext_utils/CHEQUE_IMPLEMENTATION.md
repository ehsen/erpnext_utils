# Cheque Record Creation for Payment Entry

## Overview

This implementation adds automatic cheque record creation functionality to the ERPNext Payment Entry doctype, similar to the existing Bank Payment Voucher implementation. When a payment is made via cheque, a corresponding Cheque record is automatically created upon submission.

## Features

### 1. **Cheque Payment Detection**
- Automatically detects when a Payment Entry uses a cheque as the mode of payment
- Checks if the mode of payment contains "Cheque" or "Check" (case-insensitive)
- Only applies to "Pay" type payments (outgoing payments)

### 2. **Validation**
The system validates the following when a cheque payment is detected:
- **Cheque Number** (Reference No): Must be provided
- **Cheque Date** (Reference Date): Must be provided
- **Party Type**: Must be specified
- **Party**: The recipient/vendor must be specified
- **Bank Account**: Must be a valid company bank account

### 3. **Cheque Book Validation**
Before creating a cheque record, the system:
- Verifies that the bank account exists and is marked as a company account
- Finds an active cheque book containing the cheque number
- Ensures the cheque number hasn't already been used
- Stores the cheque book reference for later use

### 4. **Automatic Cheque Record Creation**
Upon submission of a Payment Entry with cheque payment:
- Creates a new Cheque document automatically
- Populates it with:
  - Cheque Number (from Reference No)
  - Cheque Date (from Reference Date)
  - Party Type and Party information
  - Payment Amount
  - Status: "Unpresented"
  - Type: "Issued"
  - Associated Cheque Book

## File Structure

### New Files
```
erpnext_utils/
├── erpnext_utils/
│   └── overrides/
│       └── payment_entry.py      # Cheque functionality for Payment Entry
```

### Modified Files
```
hooks.py                           # Added doc_events for Payment Entry
```

## Implementation Details

### payment_entry.py Functions

#### `validate_cheque_details(doc, method=None)`
- **Purpose**: Validates cheque details during Payment Entry validation
- **Trigger**: Called during the validate hook
- **Actions**:
  - Checks if payment type is "Pay"
  - Detects if mode of payment is a cheque payment
  - Validates mandatory cheque fields
  - Calls cheque book validation

#### `validate_and_fetch_cheque_book(doc)`
- **Purpose**: Validates and fetches the correct cheque book
- **Actions**:
  - Verifies bank account exists and is a company account
  - Finds active cheque book containing the cheque number
  - Checks if cheque number is already used
  - Stores cheque book reference in the document

#### `on_submit_cheque_creation(doc, method=None)`
- **Purpose**: Creates cheque record when Payment Entry is submitted
- **Trigger**: Called during the on_submit hook
- **Actions**:
  - Checks if payment type is "Pay"
  - Detects if mode of payment is a cheque payment
  - Calls cheque record creation

#### `create_cheque_record(doc)`
- **Purpose**: Creates and inserts the Cheque document
- **Actions**:
  - Creates new Cheque document
  - Maps all relevant fields from Payment Entry
  - Links to the validated cheque book
  - Inserts the cheque record into the system

## Usage

### For Users

1. **Create a Payment Entry**
   - Set Payment Type to "Pay"
   - Select a cheque-based Mode of Payment

2. **Fill Cheque Details**
   - Enter Cheque Number in "Reference No" field
   - Enter Cheque Date in "Reference Date" field
   - Ensure Bank Account is selected
   - Ensure Party Type and Party are specified

3. **Validation**
   - System validates cheque details on save
   - Ensures cheque number belongs to an active cheque book
   - Prevents duplicate cheque numbers

4. **Submit Payment Entry**
   - Upon submission, a Cheque record is automatically created
   - Cheque status is set to "Unpresented"
   - Cheque is linked to the appropriate cheque book

### Error Handling

The system provides clear error messages for:
- Missing cheque number
- Missing cheque date
- Missing party information
- Invalid bank account
- Non-existent cheque book
- Duplicate cheque numbers

## Integration with Bank Payment Voucher

This implementation follows the same pattern as the existing Bank Payment Voucher:
- Similar validation logic
- Same cheque record structure
- Consistent error messages
- Same handling of post-dated checks (extensible for future enhancement)

## Database Considerations

- **Cheque Records**: One Cheque record is created per Payment Entry with cheque payment
- **Uniqueness**: Cheque numbers are unique within a cheque book
- **Relationships**: Cheque records are linked to:
  - Payment Entry (via creation)
  - Cheque Book (automatic linking)
  - Party (Vendor/Supplier)
  - Bank Account

## Future Enhancements

Potential improvements for future versions:
1. **Post-Dated Cheques**: Handle post-dated cheque GL entries
2. **Cheque Status Tracking**: Update cheque status based on payment clearance
3. **Batch Cheque Processing**: Create multiple cheques from a Payment Entry
4. **Cheque Cancellation**: Handle cheque cancellation with Payment Entry cancellation
5. **Audit Trail**: Log cheque creation and status changes

## Testing

### Test Cases
1. Create Payment Entry with cheque payment → Cheque record created
2. Validate mandatory fields → Appropriate errors thrown
3. Duplicate cheque number → Error on validation
4. Invalid cheque book → Error on validation
5. Non-cheque payment → No cheque record created
6. "Receive" payment type → No cheque record created (ignores cheque payment mode)

## Dependencies

- ERPNext core (Payment Entry DocType)
- Cheque DocType
- Cheque Book DocType
- Bank Account DocType
- Mode of Payment DocType

## Notes

- This feature only applies to "Pay" type payments (outgoing)
- "Receive" and "Internal Transfer" payment types are not affected
- The feature is automatic and requires no additional configuration
- Cheque detection is based on Mode of Payment name containing "Cheque" or "Check"
