import frappe
from frappe.utils import nowdate,flt
from erpnext import get_default_cost_center


def get_voucher_accounts_total(doc,total_type="debit"):
    """
    Get the total of the accounts in the voucher.
    :param doc: The voucher document.
    :param total_type: The type of total to get.
    :return: The total of the accounts in the voucher.
    """
    total = 0
    for account in doc.accounts:
        if total_type == "debit":
            total += account.debit
        else:
            total += account.credit
    return total
    
def create_gl_entries(posting_date, accounts, company, voucher_type=None, voucher_account=None, 
                      voucher_doctype=None):
    """
    Create GL Entries in ERPNext.

    :param posting_date: Date for the GL Entries (e.g., '2024-12-07').
    :param accounts: List of account details (each dict with account, debit, credit, and cost_center if needed).
                     Example:
                     [
                         {"account": "Debtors - CO", "debit": 1000, "credit": 0},
                         {"account": "Sales - CO", "debit": 0, "credit": 1000},
                     ]
    :param company: Company for the GL Entries.
    :param voucher_type: Type of the voucher (e.g., 'Payment', 'Receipt', 'Journal Entry').
                         For Payment vouchers: All debits are individual entries, credit is one consolidated entry.
                         For Receipt vouchers: All credits are individual entries, debit is one consolidated entry.
    :param voucher_account: The main cash/bank account for the voucher (e.g., 'Cash - CO', 'Bank - CO').
                           This account will be credited for Payment vouchers and debited for Receipt vouchers.
    :return: List of GL Entry names or an error message.
    """
    
    

    # Prepare GL Entry details
    gl_entries = []
    
    if voucher_type == "Payment":
        # For Payment vouchers: individual debit entries + one consolidated credit entry
        total_debit = sum(acc.get("debit", 0) for acc in accounts)
        
        # Create individual debit entries
        for acc in accounts:
            if acc.get("debit", 0) > 0:
                gl_entry = frappe.new_doc("GL Entry")
                gl_entry.posting_date = posting_date or nowdate()
                gl_entry.account = acc.account
                gl_entry.debit = acc.get("debit", 0)
                gl_entry.credit = 0
                gl_entry.cost_center = acc.get("cost_center", get_default_cost_center(company))
                gl_entry.party_type = acc.get("party_type", None)
                gl_entry.party = acc.get("party", None)
                gl_entry.company = company
                gl_entry.voucher_type = acc.get("voucher_type", voucher_type)
                gl_entry.voucher_no = acc.get("voucher_no", None)
                gl_entry.voucher_subtype = acc.get("voucher_subtype", None)
                gl_entry.against = acc.get("against", None)
                
                try:
                    gl_entry.insert()
                    gl_entries.append(gl_entry)
                except Exception as e:
                    frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")
        
        # Create one consolidated credit entry for voucher_account
        if voucher_account:
            gl_entry = frappe.new_doc("GL Entry")
            gl_entry.posting_date = posting_date or nowdate()
            gl_entry.account = voucher_account
            gl_entry.debit = 0
            gl_entry.credit = total_debit
            gl_entry.cost_center = get_default_cost_center(company)
            gl_entry.party_type = None
            gl_entry.party = None
            gl_entry.company = company
            gl_entry.voucher_type = voucher_type
            gl_entry.voucher_no = None
            gl_entry.voucher_subtype = None
            gl_entry.against = None
            
            try:
                gl_entry.insert()
                gl_entries.append(gl_entry)
            except Exception as e:
                frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")
                
    elif voucher_type == "Receipt":
        # For Receipt vouchers: individual credit entries + one consolidated debit entry
        total_credit = sum(acc.get("credit", 0) for acc in accounts)
        
        # Create individual credit entries
        for acc in accounts:
            if acc.get("credit", 0) > 0:
                gl_entry = frappe.new_doc("GL Entry")
                gl_entry.posting_date = posting_date or nowdate()
                gl_entry.account = acc["account"]
                gl_entry.debit = 0
                gl_entry.credit = acc.get("credit", 0)
                gl_entry.cost_center = acc.get("cost_center", get_default_cost_center(company))
                gl_entry.party_type = acc.get("party_type", None)
                gl_entry.party = acc.get("party", None)
                gl_entry.company = company
                gl_entry.voucher_type = acc.get("voucher_type", voucher_type)
                gl_entry.voucher_no = acc.get("voucher_no", None)
                gl_entry.voucher_subtype = acc.get("voucher_subtype", None)
                gl_entry.against = acc.get("against", None)
                
                try:
                    gl_entry.insert()
                    gl_entries.append(gl_entry)
                except Exception as e:
                    frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")
        
        # Create one consolidated debit entry for voucher_account
        if voucher_account:
            gl_entry = frappe.new_doc("GL Entry")
            gl_entry.posting_date = posting_date or nowdate()
            gl_entry.account = voucher_account
            gl_entry.debit = total_credit
            gl_entry.credit = 0
            gl_entry.cost_center = get_default_cost_center(company)
            gl_entry.party_type = None
            gl_entry.party = None
            gl_entry.company = company
            gl_entry.voucher_type = voucher_type
            gl_entry.voucher_no = None
            gl_entry.voucher_subtype = None
            gl_entry.against = None
            
            try:
                gl_entry.insert()
                gl_entries.append(gl_entry)
            except Exception as e:
                frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")
                
    else:
        # Default behavior for other voucher types (Journal Entry, etc.)
        for acc in accounts:
            gl_entry = frappe.new_doc("GL Entry")
            gl_entry.posting_date = posting_date or nowdate()
            gl_entry.account = acc["account"]
            gl_entry.debit = acc.get("debit", 0)
            gl_entry.credit = acc.get("credit", 0)
            gl_entry.cost_center = acc.get("cost_center", get_default_cost_center(company))
            gl_entry.party_type = acc.get("party_type", None)
            gl_entry.party = acc.get("party", None)
            gl_entry.company = company
            gl_entry.voucher_type = acc.get("voucher_type", voucher_type)
            gl_entry.voucher_no = acc.get("voucher_no", None)
            gl_entry.voucher_subtype = acc.get("voucher_subtype", None)
            gl_entry.against = acc.get("against", None)

            # Insert GL Entry one by one (instead of bulk insert)
            try:
                gl_entry.insert()  # This will trigger validation and insert each entry individually
                gl_entries.append(gl_entry)
            except Exception as e:
                frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")

    # Return the list of names of successfully inserted entries
    return [entry.name for entry in gl_entries]




def validate_account_row(row, row_idx):
    """Validate individual account row 
    
    :param row: The row of the child table.
    :param row_idx: The index of the row.
    :return: None
    Note: Some validations are skipped because they are done by GL Entry validation.
    """
    
    # Account must exist and be valid
    if not row.account:
        frappe.throw(f"Row {row_idx}: Account is mandatory")

    
    # Validate debit amount
    debit = flt(row.debit or 0)
    if debit <= 0:
        frappe.throw(f"Row {row_idx}: Debit amount must be greater than zero")
    
    if debit < 0:
        frappe.throw(f"Row {row_idx}: Negative debit amount not allowed")
    
    # Party validation - negative space programming
    if row.party_type and not row.party:
        frappe.throw(f"Row {row_idx}: Party is mandatory when Party Type is specified")
    
    if row.party and not row.party_type:
        frappe.throw(f"Row {row_idx}: Party Type is mandatory when Party is specified")
    
    # Validate party exists
    if row.party_type and row.party:
        if not frappe.db.exists(row.party_type, row.party):
            frappe.throw(f"Row {row_idx}: {row.party_type} '{row.party}' does not exist")
    
   

def validate_accounts_child_table(doc):
    """Validate accounts child table rows"""
    if not doc.accounts:
        frappe.throw("At least one account entry is required")
    
    for idx, row in enumerate(doc.accounts, 1):
        validate_account_row(row, idx)

def validate_accounting_equation(doc):
    """
    Validate accounting equation for Cash Payment Voucher
    For cash payment: Total Debits = Total Credits
    """
    
    if not doc.accounts:
        return
    
    # Calculate total debits from child table
    total_debits = sum(flt(row.debit or 0) for row in doc.accounts)
    
    # For cash payment voucher, we need a cash/bank credit entry
    # This should either be in a separate field or implied
    total_credits = total_debits
    
    if total_debits != total_credits:
        frappe.throw(
            
            f"<b>Debits and Credits must equal in Voucher</b>"
        )

def create_single_gl_entry(doc, account, debit=0, credit=0, party_type=None, 
                          party=None, remarks="", against_account=""):
    """
    Create a single GL Entry.
    Focused function - validation already done at document level.
    """
    
    gl_entry = frappe.new_doc("GL Entry")
    gl_entry.posting_date = doc.posting_date or doc.transaction_date
    gl_entry.account = account
    gl_entry.debit = flt(debit)
    gl_entry.credit = flt(credit)
    gl_entry.company = doc.company
    gl_entry.voucher_type = doc.doctype
    gl_entry.voucher_no = doc.name
    gl_entry.remarks = remarks
    gl_entry.against = against_account
    
    # Set party details if provided
    if party_type and party:
        gl_entry.party_type = party_type
        gl_entry.party = party
    
    # Set cost center from document or get default
    gl_entry.cost_center = (doc.get('cost_center') or 
                           get_default_cost_center(doc.company))
    
    try:
        gl_entry.insert()
        return gl_entry.name
    except Exception as e:
        frappe.log_error(f"GL Entry creation failed: {str(e)}", "GL Entry Error")
        frappe.throw(f"Failed to create GL Entry for account {account}: {str(e)}")


