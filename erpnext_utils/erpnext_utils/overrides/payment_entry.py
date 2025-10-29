import frappe
from frappe.utils import flt, today


def validate_cheque_details(doc, method=None):
	"""Validate cheque details if mode of payment is Cheque"""
	try:
		# Only validate for payment type "Pay" (outgoing payments)
		if doc.payment_type != "Pay":
			return
		
		mode_of_payment = frappe.db.get_value("Mode of Payment", doc.mode_of_payment, "name") if doc.mode_of_payment else None
		
		if not mode_of_payment:
			return
		
		# Check if this is a cheque payment by checking if the mode of payment name contains "Cheque"
		mode_name = mode_of_payment.lower() if isinstance(mode_of_payment, str) else ""
		is_cheque = "cheque" in mode_name or "check" in mode_name
		
		if not is_cheque:
			return
		
		# Validate cheque-specific fields
		if not doc.reference_no:
			frappe.throw("Cheque Number (Reference No) is mandatory for Cheque payments")
		
		if not doc.reference_date:
			frappe.throw("Cheque Date (Reference Date) is mandatory for Cheque payments")
		
		if not doc.party_type:
			frappe.throw("Party Type is mandatory for Cheque payments")
		
		if not doc.party:
			frappe.throw("Party is mandatory for Cheque payments")
		
		# Validate and fetch correct cheque book
		validate_and_fetch_cheque_book(doc)
		
	except Exception as e:
		raise


def validate_and_fetch_cheque_book(doc):
	"""Validate cheque number and fetch the correct cheque book"""
	if not doc.reference_no or not doc.paid_from:
		return
	
	# Fetch Bank Account using the GL Account (paid_from)
	bank_account_doc = frappe.db.get_value(
		"Bank Account",
		{"account": doc.paid_from, "is_company_account": 1},
		["name"],
		as_dict=True
	)
	if not bank_account_doc:
		frappe.throw(f"Bank Account for GL Account '{doc.paid_from}' not found or not a company account")
	
	bank_account = bank_account_doc.name
	
	# Find cheque book that matches the Bank Account and contains the cheque number
	cheque_book = frappe.db.get_value(
		"Cheque Book",
		{
			"bank_account": bank_account,
			"is_active": 1,
			"start_series": ["<=", doc.reference_no],
			"end_series": [">=", doc.reference_no]
		},
		["name", "start_series", "end_series", "current_series"],
		as_dict=True
	)
	
	if not cheque_book:
		error_msg = f"No active cheque book found for Bank Account '{bank_account}' containing cheque number '{doc.reference_no}'"
		frappe.throw(error_msg)
	
	# Check if cheque number is already used
	existing_cheque = frappe.db.exists(
		"Cheque",
		{
			"cheque_number": doc.reference_no,
			"cheque_book": cheque_book.name
		}
	)
	
	if existing_cheque:
		error_msg = f"Cheque number '{doc.reference_no}' is already used in cheque book '{cheque_book.name}'"
		frappe.throw(error_msg)
	
	# Store the cheque book name for later use
	doc.cheque_book_name = cheque_book.name
	doc.bank_account_name = bank_account


def on_submit_cheque_creation(doc, method=None):
	"""Create cheque record on submission of Payment Entry"""
	try:
		# Only for payment type "Pay" (outgoing payments)
		if doc.payment_type != "Pay":
			return
		
		mode_of_payment = frappe.db.get_value("Mode of Payment", doc.mode_of_payment, "name") if doc.mode_of_payment else None
		if not mode_of_payment:
			return
		
		# Check if this is a cheque payment
		mode_name = mode_of_payment.lower() if isinstance(mode_of_payment, str) else ""
		is_cheque = "cheque" in mode_name or "check" in mode_name
		
		if not is_cheque:
			return
		
		# Create cheque record
		create_cheque_record(doc)
		
	except Exception as e:
		raise


def create_cheque_record(doc):
	"""Create cheque record for cheque payments"""
	try:
		cheque_doc = frappe.new_doc("Cheque")
		
		# Fetch Bank Account using the GL Account (paid_from)
		bank_account_doc = frappe.db.get_value(
			"Bank Account",
			{"account": doc.paid_from, "is_company_account": 1},
			["name"],
			as_dict=True
		)
		if not bank_account_doc:
			frappe.throw(f"Bank Account for GL Account '{doc.paid_from}' not found or not a company account")
		
		# Map fields from Payment Entry to Cheque
		cheque_doc.cheque_number = doc.reference_no
		cheque_doc.cheque_date = doc.reference_date
		cheque_doc.party_type = doc.party_type
		cheque_doc.party = doc.party
		cheque_doc.status = "Unpresented"
		cheque_doc.cheque_type = "Issued"
		cheque_doc.amount = doc.paid_amount
		cheque_doc.bank_account = bank_account_doc.name
		
		# Validate cheque number is provided
		if not doc.reference_no:
			frappe.throw("Cheque Number is required to create cheque record")
		
		# Fetch cheque book using bank_account GL Account and cheque_number range
		cheque_book = frappe.db.get_value(
			"Cheque Book",
			{
				"bank_account": bank_account_doc.name,
				"is_active": 1,
				"start_series": ["<=", doc.reference_no],
				"end_series": [">=", doc.reference_no]
			},
			["name", "start_series", "end_series"],
			as_dict=True
		)
		
		if cheque_book:
			cheque_doc.cheque_book = cheque_book.name
		else:
			frappe.throw(
				f"No active cheque book found for Bank Account '{bank_account_doc.name}' "
				f"containing cheque number '{doc.reference_no}'"
			)
		
		# The bank_account field will be automatically fetched from cheque_book.bank_account
		# due to the fetch_from configuration in the Cheque DocType
		cheque_doc.insert()
		
	except Exception as e:
		error_msg = f"Error creating cheque record for Payment Entry {doc.name}: {str(e)}"
		raise
