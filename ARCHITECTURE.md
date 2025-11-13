# Architecture & Flow Diagrams: Cheque Record Creation for Payment Entry

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ERPNext System                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ erpnext_utils App                                             │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │                                                               │   │
│  │  ┌───────────────────────────────────────────────────────┐   │   │
│  │  │ overrides/payment_entry.py                            │   │   │
│  │  ├───────────────────────────────────────────────────────┤   │   │
│  │  │ • validate_cheque_details()                           │   │   │
│  │  │ • validate_and_fetch_cheque_book()                    │   │   │
│  │  │ • on_submit_cheque_creation()                         │   │   │
│  │  │ • create_cheque_record()                              │   │   │
│  │  └───────────────────────────────────────────────────────┘   │   │
│  │                         ↕                                      │   │
│  │  ┌───────────────────────────────────────────────────────┐   │   │
│  │  │ hooks.py (doc_events)                                 │   │   │
│  │  ├───────────────────────────────────────────────────────┤   │   │
│  │  │ "Payment Entry": {                                    │   │   │
│  │  │   "validate": validate_cheque_details                 │   │   │
│  │  │   "on_submit": on_submit_cheque_creation             │   │   │
│  │  │ }                                                      │   │   │
│  │  └───────────────────────────────────────────────────────┘   │   │
│  │                                                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ ERPNext Core Doctypes (Used)                                 │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │ • Payment Entry (modified via hooks)                         │   │
│  │ • Cheque (created automatically)                             │   │
│  │ • Cheque Book (validated against)                            │   │
│  │ • Bank Account (referenced)                                  │   │
│  │ • Mode of Payment (detected)                                 │   │
│  │ • GL Entry (created for accounting)                          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Payment Entry Validation Flow

```
                        ┌─────────────────────┐
                        │  Payment Entry      │
                        │   (Draft/New)       │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │    Save Action      │
                        │   (triggers hooks)  │
                        └──────────┬──────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │ validate_cheque_details()    │
                    │ Hook: doc_events validate    │
                    └──────────┬───────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
        ┌─────────────────────┐  ┌─────────────────────┐
        │ Payment Type = Pay? │  │ Mode = Cheque?      │
        └─────────┬───────────┘  └────────┬────────────┘
                  │                       │
        NO: Exit  │ YES         YES: Continue
                  │                       │
                  └───────────┬───────────┘
                              │
                              ▼
                    ┌──────────────────────────────┐
                    │ Validate Required Fields     │
                    ├──────────────────────────────┤
                    │ ✓ Reference No (cheque #)   │
                    │ ✓ Reference Date            │
                    │ ✓ Party Type                │
                    │ ✓ Party                     │
                    │ ✓ Bank Account              │
                    └──────────┬───────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
              FAIL: │ YES             NO: │
              Error │                     ▼
                    │         ┌─────────────────────┐
                    │         │  validate_and_fetch │
                    │         │  _cheque_book()     │
                    │         └─────────┬───────────┘
                    │                   │
                    │      ┌────────────┴────────────┐
                    │      │                         │
                    │      ▼                         ▼
                    │  ┌─────────────┐    ┌──────────────────┐
                    │  │ Valid Bank  │    │ Cheque Book      │
                    │  │ Account?    │    │ Contains No?     │
                    │  └─────┬───────┘    └────────┬─────────┘
                    │        │                     │
                    │   FAIL:│ YES              FAIL│ YES
                    │   Error│                     │
                    │        │                     │
                    │        └────────┬────────────┘
                    │                 │
                    │                 ▼
                    │         ┌─────────────────────┐
                    │         │ Duplicate Check:    │
                    │         │ Cheque # Already    │
                    │         │ Used in Book?       │
                    │         └────────┬────────────┘
                    │                  │
                    │          FAIL: │ YES
                    │          Error │
                    │                 │
                    └─────────┬────────┘
                              │
                              ▼
                    ┌──────────────────────────────┐
                    │   Validation Passed ✓        │
                    │ Store: cheque_book_name      │
                    └──────────┬───────────────────┘
                               │
                               ▼
                    ┌──────────────────────────────┐
                    │   Payment Entry Saved        │
                    └──────────────────────────────┘
```

## Payment Entry Submission Flow

```
                  ┌──────────────────────┐
                  │ Payment Entry        │
                  │  (Saved/Valid)       │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Submit Action        │
                  │ (triggers on_submit) │
                  └──────────┬───────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ on_submit_cheque_creation()  │
              │ Hook: doc_events on_submit   │
              └──────────┬───────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
  ┌─────────────────────┐  ┌─────────────────────┐
  │ Payment Type = Pay? │  │ Mode = Cheque?      │
  └─────────┬───────────┘  └────────┬────────────┘
            │                       │
  NO: Exit  │ YES         YES: Continue
            │                       │
            └───────────┬───────────┘
                        │
                        ▼
          ┌──────────────────────────────┐
          │  create_cheque_record()      │
          └──────────┬───────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
    ┌──────────┐        ┌───────────────────┐
    │ Create   │        │ Set Cheque Fields │
    │ Cheque   │        ├───────────────────┤
    │ Document │        │ cheque_number:    │
    │          │        │   ref_no          │
    │          │        │ cheque_date:      │
    │          │        │   ref_date        │
    │          │        │ party_type/party  │
    │          │        │ amount:           │
    │          │        │   paid_amount     │
    │          │        │ status:           │
    │          │        │   "Unpresented"   │
    │          │        │ cheque_type:      │
    │          │        │   "Issued"        │
    └──────────┘        └───────────────────┘
        │                     │
        └──────────┬──────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Link to Cheque Book  │
        │ (cheque_book_name)   │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Insert Cheque Doc    │
        │ to Database          │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Payment Entry        │
        │ Submitted ✓          │
        │ Cheque Created ✓     │
        └──────────────────────┘
```

## Data Model: Payment Entry to Cheque Mapping

```
┌──────────────────────────────┐
│    Payment Entry (Source)    │
├──────────────────────────────┤
│ payment_type: "Pay"          │
│ mode_of_payment: "Cheque"    │
│ reference_no: "CHQ123456"    │────┐
│ reference_date: 2025-03-15   │    │
│ party_type: "Supplier"       │    │
│ party: "Vendor Name"         │    │
│ bank_account: "ACC-001"      │    │
│ paid_amount: 50000           │    │
│ company: "ABC Corp"          │    │
│                              │    │
│ (Internal fields added)      │    │
│ cheque_book_name: "CHQ-2025" │    │
│ bank_account_name: "ACC-001" │    │
└──────────────────────────────┘    │
                                     │
                                     │ Maps to
                                     │
                                     ▼
┌──────────────────────────────┐
│    Cheque (Target)           │
├──────────────────────────────┤
│ cheque_number: "CHQ123456"   │
│ cheque_date: 2025-03-15      │
│ party_type: "Supplier"       │
│ party: "Vendor Name"         │
│ amount: 50000                │
│ cheque_book: "CHQ-2025"      │
│ status: "Unpresented"        │
│ cheque_type: "Issued"        │
│ bank_account: (fetched from  │
│               cheque_book)   │
│ company: "ABC Corp"          │
│                              │
│ (Auto-populated fields)      │
│ owner: (current user)        │
│ creation: (timestamp)        │
└──────────────────────────────┘
```

## Database Relationships

```
┌──────────────────────┐         ┌─────────────────────┐
│  Payment Entry       │         │  Cheque             │
├──────────────────────┤         ├─────────────────────┤
│ name (PK)            │ ◄────── │ name (PK)           │
│ reference_no         │  Cheque │ cheque_number       │
│ reference_date       │  Created│ cheque_date         │
│ party_type           │  By     │ party_type          │
│ party                │         │ party               │
│ bank_account         │         │ bank_account (FK)   │
│ paid_amount          │         │ cheque_book (FK)    │
│ company (FK)         │         │ status              │
│ ...                  │         │ cheque_type         │
└──────────────────────┘         │ amount              │
            │                    │ company (FK)        │
            │                    └─────────────────────┘
            │                              │
            │ References                   │ Links to
            │                              ▼
            │                    ┌─────────────────────┐
            │                    │  Cheque Book        │
            │                    ├─────────────────────┤
            │                    │ name (PK)           │
            │                    │ bank_account (FK)   │
            │                    │ start_series        │
            │                    │ end_series          │
            │                    │ is_active           │
            │                    │ company (FK)        │
            │                    └─────────────────────┘
            │                              │
            ▼                              ▼
    ┌───────────────────┐        ┌─────────────────────┐
    │  Bank Account     │        │  Company            │
    ├───────────────────┤        ├─────────────────────┤
    │ name (PK)         │        │ name (PK)           │
    │ account (FK)      │        │ default_currency    │
    │ bank (FK)         │        │ ...                 │
    │ is_company_account│        └─────────────────────┘
    │ company (FK)      │────────────┘
    └───────────────────┘
```

## Function Call Hierarchy

```
┌──────────────────────────────────────────────────────────────┐
│ Frappe Document Hooks (Automatic)                             │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  validate (During doc.save())                               │
│  └─> validate_cheque_details(doc, method)                   │
│      ├─> Check: payment_type == "Pay"                       │
│      ├─> Check: mode_of_payment contains "Cheque"           │
│      ├─> Validate fields:                                   │
│      │   ├─> reference_no                                   │
│      │   ├─> reference_date                                 │
│      │   ├─> party_type                                     │
│      │   └─> party                                          │
│      └─> validate_and_fetch_cheque_book(doc)                │
│          ├─> Check: bank_account exists                     │
│          ├─> Find: cheque_book by number range              │
│          ├─> Check: cheque_book is_active                   │
│          ├─> Check: cheque_number not duplicate             │
│          └─> Store: cheque_book_name in doc                 │
│                                                              │
│  on_submit (During doc.submit())                            │
│  └─> on_submit_cheque_creation(doc, method)                │
│      ├─> Check: payment_type == "Pay"                       │
│      ├─> Check: mode_of_payment contains "Cheque"           │
│      └─> create_cheque_record(doc)                          │
│          ├─> Create: new Cheque document                    │
│          ├─> Map: fields from Payment Entry                 │
│          ├─> Set: status = "Unpresented"                    │
│          ├─> Set: cheque_type = "Issued"                    │
│          ├─> Link: cheque_book reference                    │
│          └─> Insert: cheque_doc into database               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Validation Decision Tree

```
                            ┌─────────────────────────┐
                            │ Payment Entry Changed   │
                            └────────────┬────────────┘
                                         │
                                         ▼
                    ┌────────────────────────────────────┐
                    │ Is Payment Type = "Pay"?           │
                    └────┬──────────────────────────┬────┘
                    NO: │                           │ YES
                        │                           ▼
                        │                ┌─────────────────────────┐
                        │                │ Does Mode of Payment   │
                        │                │ contain "Cheque"?      │
                        │                └────┬──────────────┬────┘
                        │            NO: │     │            │ YES
                        │                │     │            ▼
                        │                │     │  ┌──────────────────────┐
                        │                │     │  │ Check Cheque Fields  │
                        │                │     │  │ • ref_no required    │
                        │                │     │  │ • ref_date required  │
                        │                │     │  │ • party_type req.    │
                        │                │     │  │ • party required     │
                        │                │     │  └───┬────────────┬────┘
                        │                │     │ FAIL:│ YES     NO:│
                        │                │     │Error │         ▼
                        │                │     │      │  ┌───────────────┐
                        │                │     │      │  │ Validate Bank │
                        │                │     │      │  │ Account       │
                        │                │     │      │  └───┬───────┬──┘
                        │                │     │      │ FAIL:│ YES  NO:│
                        │                │     │      │Error │        ▼
                        │                │     │      │      │ ┌───────────┐
                        │                │     │      │      │ │Find Cheque│
                        │                │     │      │      │ │Book by #  │
                        │                │     │      │      │ └───┬───┬──┘
                        │                │     │      │      │FAIL:│ Y │NO:
                        │                │     │      │      │Error│   │
                        │                │     │      │      │     │   ▼
                        │                │     │      │      │     │ ┌──────┐
                        │                │     │      │      │     │ │Check │
                        │                │     │      │      │     │ │Dupe? │
                        │                │     │      │      │     │ └──┬─┬┘
                        │                │     │      │      │     │FAIL││Y
                        │                │     │      │      │     │Err │
                        │                │     │      │      │     │    ▼
                        │                │     │      │      │     │  ┌────┐
                        │                └─────┴──────┴──────┴──────┴──> ✓OK │
                        │                                          │  └────┘
                        └──────────────────────────────────────────┘
```

## Error Handling Path

```
                    ┌──────────────────────┐
                    │  Validation Error    │
                    │  Encountered         │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
        ┌────────────────────┐  ┌──────────────────┐
        │ Error Type 1       │  │ Error Type 2     │
        │ Field Validation   │  │ Business Logic   │
        ├────────────────────┤  ├──────────────────┤
        │ • Missing field    │  │ • Invalid bank   │
        │ • Invalid format   │  │ • Cheque book    │
        │ • Wrong type       │  │   not found      │
        │                    │  │ • Duplicate      │
        │                    │  │   cheque number  │
        └────────┬───────────┘  └────────┬─────────┘
                 │                       │
                 ▼                       ▼
        ┌────────────────────┐  ┌──────────────────┐
        │ frappe.throw()     │  │ frappe.throw()   │
        │ with message       │  │ with message     │
        │ "Field is         │  │ "No active       │
        │  mandatory"        │  │  cheque book..." │
        └────────┬───────────┘  └────────┬─────────┘
                 │                       │
                 └───────────┬───────────┘
                             │
                             ▼
                    ┌──────────────────────┐
                    │ Payment Entry        │
                    │ Validation Failed    │
                    │ (Not saved/Drafted)  │
                    │                      │
                    │ User sees error      │
                    │ in UI & corrects     │
                    └──────────────────────┘
```

---

**These diagrams illustrate:**
1. System architecture and components
2. Complete validation flow with all decision points
3. Submission flow and cheque creation process
4. Data mapping between Payment Entry and Cheque
5. Database relationships and foreign keys
6. Function call hierarchy and dependencies
7. Error handling and validation logic

This modular, hook-based approach ensures clean integration with ERPNext without modifying core code.

