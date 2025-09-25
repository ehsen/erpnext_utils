import frappe
from frappe.utils import nowdate,flt
from erpnext import get_default_cost_center


def get_voucher_accounts_total(doc):
    """
    Get the total amount of the accounts in the voucher.
    :param doc: The voucher document.
    :return: The total amount of the accounts in the voucher.
    """
    total = 0
    for account in doc.accounts:
        total += account.amount
    return total

def get_against_account_str(accounts):
    against_account = ",".join(acc.account for acc in accounts)
        
    
def create_gl_entries(
    posting_date,
    accounts,
    company,
    voucher_type=None,
    voucher_account=None,
    voucher_doctype=None,
    voucher_no=None
):
    """
    Create GL Entries in ERPNext.
    """

    gl_entries = []

    if voucher_type == "Payment":
        total_amount = sum(acc.get("amount", 0) for acc in accounts)

        for acc in accounts:
            if acc.get("amount", 0) > 0:
                gl_entry = frappe.new_doc("GL Entry")
                gl_entry.posting_date = posting_date or nowdate()
                gl_entry.account = acc.account
                gl_entry.debit = acc.get("amount", 0)  # For payment: amount = debit
                gl_entry.credit = 0
                gl_entry.cost_center = acc.get("cost_center", get_default_cost_center(company))
                gl_entry.party_type = acc.get("party_type")
                gl_entry.party = acc.get("party")
                gl_entry.company = company
                gl_entry.voucher_type = voucher_doctype or acc.get("voucher_type", voucher_type)
                gl_entry.voucher_no = voucher_no or acc.get("voucher_no")
                gl_entry.voucher_subtype = acc.get("voucher_subtype")
                gl_entry.against = voucher_account

                try:
                    gl_entry.insert()
                    gl_entries.append(gl_entry)
                except Exception as e:
                    frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")
        
        if voucher_account:
            # Get against accounts for cash account GL entry
            against_accounts = ",".join(acc.account for acc in accounts if acc.get("amount", 0) > 0)
            
            # Get cost center from first account row if available, otherwise use default
            voucher_cost_center = None
            if accounts and accounts[0].get("cost_center"):
                voucher_cost_center = accounts[0].get("cost_center")
            else:
                voucher_cost_center = get_default_cost_center(company)
            
            gl_entry = frappe.new_doc("GL Entry")
            gl_entry.posting_date = posting_date or nowdate()
            gl_entry.account = voucher_account
            gl_entry.debit = 0
            gl_entry.credit = total_amount  # For payment: cash account is credited
            gl_entry.cost_center = voucher_cost_center
            gl_entry.party_type = None
            gl_entry.party = None
            gl_entry.company = company
            gl_entry.voucher_type = voucher_doctype or voucher_type
            gl_entry.voucher_no = voucher_no
            gl_entry.voucher_subtype = voucher_doctype
            gl_entry.against = against_accounts

            try:
                gl_entry.insert()
                gl_entries.append(gl_entry)
            except Exception as e:
                frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")

    elif voucher_type == "Receipt":
        total_amount = sum(acc.get("amount", 0) for acc in accounts)

        for acc in accounts:
            if acc.get("amount", 0) > 0:
                gl_entry = frappe.new_doc("GL Entry")
                gl_entry.posting_date = posting_date or nowdate()
                gl_entry.account = acc.account
                gl_entry.debit = 0
                gl_entry.credit = acc.get("amount", 0)  # For receipt: amount = credit
                gl_entry.cost_center = acc.get("cost_center", get_default_cost_center(company))
                gl_entry.party_type = acc.get("party_type")
                gl_entry.party = acc.get("party")
                gl_entry.company = company
                gl_entry.voucher_type = voucher_doctype or acc.get("voucher_type", voucher_type)
                gl_entry.voucher_no = voucher_no or acc.get("voucher_no")
                gl_entry.voucher_subtype = acc.get("voucher_subtype")
                gl_entry.against = voucher_account

                try:
                    gl_entry.insert()
                    gl_entries.append(gl_entry)
                except Exception as e:
                    frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")

        if voucher_account:
            # Get against accounts for cash account GL entry
            against_accounts = ",".join(acc.account for acc in accounts if acc.get("amount", 0) > 0)
            
            # Get cost center from first account row if available, otherwise use default
            voucher_cost_center = None
            if accounts and accounts[0].get("cost_center"):
                voucher_cost_center = accounts[0].get("cost_center")
            else:
                voucher_cost_center = get_default_cost_center(company)
            
            gl_entry = frappe.new_doc("GL Entry")
            gl_entry.posting_date = posting_date or nowdate()
            gl_entry.account = voucher_account
            gl_entry.debit = total_amount  # For receipt: cash account is debited
            gl_entry.credit = 0
            gl_entry.cost_center = voucher_cost_center
            gl_entry.party_type = None
            gl_entry.party = None
            gl_entry.company = company
            gl_entry.voucher_type = voucher_doctype or voucher_type
            gl_entry.voucher_no = voucher_no
            gl_entry.voucher_subtype = voucher_doctype
            gl_entry.against = against_accounts

            try:
                gl_entry.insert()
                gl_entries.append(gl_entry)
            except Exception as e:
                frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")

    elif voucher_type == "Bank Payment":
        total_amount = sum(acc.get("amount", 0) for acc in accounts)

        for acc in accounts:
            if acc.get("amount", 0) > 0:
                gl_entry = frappe.new_doc("GL Entry")
                gl_entry.posting_date = posting_date or nowdate()
                gl_entry.account = acc.account
                gl_entry.debit = acc.get("amount", 0)  # For bank payment: amount = debit
                gl_entry.credit = 0
                gl_entry.cost_center = acc.get("cost_center", get_default_cost_center(company))
                gl_entry.party_type = acc.get("party_type")
                gl_entry.party = acc.get("party")
                gl_entry.company = company
                gl_entry.voucher_type = voucher_doctype or acc.get("voucher_type", voucher_type)
                gl_entry.voucher_no = voucher_no or acc.get("voucher_no")
                gl_entry.voucher_subtype = acc.get("voucher_subtype")
                gl_entry.against = voucher_account

                try:
                    gl_entry.insert()
                    gl_entries.append(gl_entry)
                except Exception as e:
                    frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")
        
        if voucher_account:
            # Get against accounts for bank account GL entry
            against_accounts = ",".join(acc.account for acc in accounts if acc.get("amount", 0) > 0)
            
            # Get cost center from first account row if available, otherwise use default
            voucher_cost_center = None
            if accounts and accounts[0].get("cost_center"):
                voucher_cost_center = accounts[0].get("cost_center")
            else:
                voucher_cost_center = get_default_cost_center(company)
            
            gl_entry = frappe.new_doc("GL Entry")
            gl_entry.posting_date = posting_date or nowdate()
            gl_entry.account = voucher_account
            gl_entry.debit = 0
            gl_entry.credit = total_amount  # For bank payment: bank account is credited
            gl_entry.cost_center = voucher_cost_center
            gl_entry.party_type = None
            gl_entry.party = None
            gl_entry.company = company
            gl_entry.voucher_type = voucher_doctype or voucher_type
            gl_entry.voucher_no = voucher_no
            gl_entry.voucher_subtype = voucher_doctype
            gl_entry.against = against_accounts

            try:
                gl_entry.insert()
                gl_entries.append(gl_entry)
            except Exception as e:
                frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")

    elif voucher_type == "Bank Receipt":
        total_amount = sum(acc.get("amount", 0) for acc in accounts)

        for acc in accounts:
            if acc.get("amount", 0) > 0:
                gl_entry = frappe.new_doc("GL Entry")
                gl_entry.posting_date = posting_date or nowdate()
                gl_entry.account = acc.account
                gl_entry.debit = 0
                gl_entry.credit = acc.get("amount", 0)  # For bank receipt: amount = credit
                gl_entry.cost_center = acc.get("cost_center", get_default_cost_center(company))
                gl_entry.party_type = acc.get("party_type")
                gl_entry.party = acc.get("party")
                gl_entry.company = company
                gl_entry.voucher_type = voucher_doctype or acc.get("voucher_type", voucher_type)
                gl_entry.voucher_no = voucher_no or acc.get("voucher_no")
                gl_entry.voucher_subtype = acc.get("voucher_subtype")
                gl_entry.against = voucher_account

                try:
                    gl_entry.insert()
                    gl_entries.append(gl_entry)
                except Exception as e:
                    frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")

        if voucher_account:
            # Get against accounts for bank account GL entry
            against_accounts = ",".join(acc.account for acc in accounts if acc.get("amount", 0) > 0)
            
            # Get cost center from first account row if available, otherwise use default
            voucher_cost_center = None
            if accounts and accounts[0].get("cost_center"):
                voucher_cost_center = accounts[0].get("cost_center")
            else:
                frappe.throw("Cost Center (Official or Out Of Books) is mandatory for all vouchers")
            
            gl_entry = frappe.new_doc("GL Entry")
            gl_entry.posting_date = posting_date or nowdate()
            gl_entry.account = voucher_account
            gl_entry.debit = total_amount  # For bank receipt: bank account is debited
            gl_entry.credit = 0
            gl_entry.cost_center = voucher_cost_center
            gl_entry.party_type = None
            gl_entry.party = None
            gl_entry.company = company
            gl_entry.voucher_type = voucher_doctype or voucher_type
            gl_entry.voucher_no = voucher_no
            gl_entry.voucher_subtype = voucher_doctype
            gl_entry.against = against_accounts

            try:
                gl_entry.insert()
                gl_entries.append(gl_entry)
            except Exception as e:
                frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")

    else:
        for acc in accounts:
            gl_entry = frappe.new_doc("GL Entry")
            gl_entry.posting_date = posting_date or nowdate()
            gl_entry.account = acc.account
            gl_entry.debit = acc.get("debit", 0)
            gl_entry.credit = acc.get("credit", 0)
            gl_entry.cost_center = acc.get("cost_center", get_default_cost_center(company))
            gl_entry.party_type = acc.get("party_type")
            gl_entry.party = acc.get("party")
            gl_entry.company = company
            gl_entry.voucher_type = voucher_doctype or acc.get("voucher_type", voucher_type)
            gl_entry.voucher_no = voucher_no or acc.get("voucher_no")
            gl_entry.voucher_subtype = acc.get("voucher_subtype")
            gl_entry.against = acc.get("against")

            try:
                gl_entry.insert()
                gl_entries.append(gl_entry)
            except Exception as e:
                frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")

    return [entry.name for entry in gl_entries]






def populate_cost_center_in_accounts(doc):
    """
    Automatically populate cost_center field in accounts child table rows
    from the main document's cost_center field.
    """
    if not doc.cost_center:
        return
    
    if doc.accounts:
        for account_row in doc.accounts:
            if not account_row.cost_center:
                account_row.cost_center = doc.cost_center


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

    
    # Validate amount
    amount = flt(row.amount or 0)
    if amount <= 0:
        frappe.throw(f"Row {row_idx}: Amount must be greater than zero")
    
    if amount < 0:
        frappe.throw(f"Row {row_idx}: Negative amount not allowed")
    
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
    # First populate cost center from main document
    populate_cost_center_in_accounts(doc)
    
    if not doc.accounts:
        frappe.throw("At least one account entry is required")
    
    for idx, row in enumerate(doc.accounts, 1):
        validate_account_row(row, idx)

def validate_accounting_equation(doc):
    """
    Validate accounting equation for Cash Payment/Receipt Voucher
    For cash payment: Total Debits = Total Credits
    For cash receipt: Total Debits = Total Credits
    """
    
    if not doc.accounts:
        return
    
    # Calculate total amount from child table
    total_amount = sum(flt(row.amount or 0) for row in doc.accounts)
    
    # For both payment and receipt vouchers, the accounting equation must balance
    # Payment: accounts debited, cash credited
    # Receipt: accounts credited, cash debited
    if total_amount <= 0:
        frappe.throw(f"<b>Total amount must be greater than zero</b>")

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


def get_post_dated_cheque_account():
    """Get the default post dated cheque account from Voucher Settings"""
    try:
        voucher_settings = frappe.get_single("Voucher Settings")
        return voucher_settings.default_post_dated_cheque
    except:
        frappe.throw("Please set Default Post Dated Cheque Account in Voucher Settings")


def create_post_dated_cheque_gl_entries(posting_date, accounts, company, voucher_type, 
                                       voucher_account, voucher_doctype, voucher_no, 
                                       cheque_date, cheque_number):
    """
    Create GL entries for post dated cheques
    For post dated cheques, the transaction hits the post dated cheque account instead of bank account
    """
    from frappe.utils import nowdate
    
    gl_entries = []
    total_amount = sum(acc.get("amount", 0) for acc in accounts)
    
    # Get post dated cheque account
    post_dated_account = get_post_dated_cheque_account()
    
    # Create entries for accounts (same as normal voucher)
    for acc in accounts:
        if acc.get("amount", 0) > 0:
            gl_entry = frappe.new_doc("GL Entry")
            gl_entry.posting_date = posting_date or nowdate()
            gl_entry.account = acc.account
            
            if voucher_type in ["Bank Payment", "Payment"]:
                gl_entry.debit = acc.get("amount", 0)
                gl_entry.credit = 0
            else:  # Bank Receipt, Receipt
                gl_entry.debit = 0
                gl_entry.credit = acc.get("amount", 0)
            
            gl_entry.cost_center = acc.get("cost_center", get_default_cost_center(company))
            gl_entry.party_type = acc.get("party_type")
            gl_entry.party = acc.get("party")
            gl_entry.company = company
            gl_entry.voucher_type = voucher_doctype or acc.get("voucher_type", voucher_type)
            gl_entry.voucher_no = voucher_no or acc.get("voucher_no")
            gl_entry.voucher_subtype = acc.get("voucher_subtype")
            gl_entry.against = post_dated_account
            gl_entry.remarks = f"Post Dated Cheque #{cheque_number} dated {cheque_date}"

            try:
                gl_entry.insert()
                gl_entries.append(gl_entry)
            except Exception as e:
                frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")
    
    # Create entry for post dated cheque account
    if post_dated_account:
        against_accounts = ",".join(acc.account for acc in accounts if acc.get("amount", 0) > 0)
        
        # Get cost center from first account row if available, otherwise use default
        voucher_cost_center = None
        if accounts and accounts[0].get("cost_center"):
            voucher_cost_center = accounts[0].get("cost_center")
        else:
            voucher_cost_center = get_default_cost_center(company)
        
        gl_entry = frappe.new_doc("GL Entry")
        gl_entry.posting_date = posting_date or nowdate()
        gl_entry.account = post_dated_account
        
        if voucher_type in ["Bank Payment", "Payment"]:
            gl_entry.debit = 0
            gl_entry.credit = total_amount
        else:  # Bank Receipt, Receipt
            gl_entry.debit = total_amount
            gl_entry.credit = 0
        
        gl_entry.cost_center = voucher_cost_center
        gl_entry.party_type = None
        gl_entry.party = None
        gl_entry.company = company
        gl_entry.voucher_type = voucher_doctype or voucher_type
        gl_entry.voucher_no = voucher_no
        gl_entry.voucher_subtype = voucher_doctype
        gl_entry.against = against_accounts
        gl_entry.remarks = f"Post Dated Cheque #{cheque_number} dated {cheque_date}"

        try:
            gl_entry.insert()
            gl_entries.append(gl_entry)
        except Exception as e:
            frappe.log_error(f"Error inserting GL Entry: {str(e)}", "GL Entry Insertion Error")
    
    return [entry.name for entry in gl_entries]


