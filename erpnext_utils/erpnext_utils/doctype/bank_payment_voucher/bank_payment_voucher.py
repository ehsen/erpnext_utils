# Copyright (c) 2025, SpotLedger and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today
from erpnext_utils.erpnext_utils.controllers.voucher_controller import (validate_accounts_child_table, validate_accounting_equation, 
create_gl_entries)


class BankPaymentVoucher(Document):
	pass

	def validate(self):
		validate_accounts_child_table(self)
		validate_accounting_equation(self)
		self.total_payment = sum(flt(row.amount or 0) for row in self.accounts)

		# Set gl_bank_account to voucher_account since both should be Account records
		if self.voucher_account and not self.gl_bank_account:
			self.gl_bank_account = self.voucher_account
		
		# Validate cheque details if instrument type is Cheque
		if self.instrument_type == "Cheque":
			if not self.cheque_number:
				frappe.throw("Cheque Number is mandatory when Instrument Type is Cheque")
			if not self.cheque_date:
				frappe.throw("Cheque Date is mandatory when Instrument Type is Cheque")
			if not self.party_type:
				frappe.throw("Party Type is mandatory when Instrument Type is Cheque")
			if not self.party:
				frappe.throw("Issued To (Party) is mandatory when Instrument Type is Cheque")
			
			# Validate and fetch correct cheque book
			self.validate_and_fetch_cheque_book()

	def on_submit(self):
		# Create cheque record if instrument type is Cheque
		if self.instrument_type == "Cheque":
			self.create_cheque_record()
			
			# Check if it's a post dated cheque
			if self.cheque_date > today():
				# Create post dated cheque GL entries using gl_bank_account
				from erpnext_utils.erpnext_utils.controllers.voucher_controller import create_post_dated_cheque_gl_entries,get_post_dated_cheque_account
				
				create_post_dated_cheque_gl_entries(self.posting_date, self.accounts, self.company, 
					"Bank Payment", get_post_dated_cheque_account(), "Bank Payment Voucher", self.name,
					self.cheque_date, self.cheque_number)
			else:
				# Create normal GL entries for current date cheques using gl_bank_account
				create_gl_entries(self.posting_date, self.accounts, self.company, "Bank Payment",
						self.gl_bank_account, "Bank Payment Voucher", self.name)
		else:
			# Create normal GL entries for non-cheque instruments using gl_bank_account
			create_gl_entries(self.posting_date, self.accounts, self.company, "Bank Payment",
					self.gl_bank_account, "Bank Payment Voucher", self.name)

	def create_cheque_record(self):
		"""Create cheque record for cheque payments"""
		cheque_doc = frappe.new_doc("Cheque")
		cheque_doc.cheque_number = self.cheque_number
		cheque_doc.cheque_date = self.cheque_date
		cheque_doc.party_type = self.party_type
		cheque_doc.party = self.party
		cheque_doc.status = "Unpresented"
		cheque_doc.cheque_type = "Issued"
		cheque_doc.amount = self.total_payment
		
		# Use the validated cheque book
		if hasattr(self, 'cheque_book_name') and self.cheque_book_name:
			cheque_doc.cheque_book = self.cheque_book_name
		else:
			# Fallback: Try to find and link the cheque book using the Bank Account directly
			if self.voucher_account:
				cheque_book = frappe.db.get_value("Cheque Book",
					{"bank_account": self.voucher_account, "is_active": 1}, "name")
				if cheque_book:
					cheque_doc.cheque_book = cheque_book
		
		# The bank_account field will be automatically fetched from cheque_book.bank_account
		# due to the fetch_from configuration in the Cheque DocType
		cheque_doc.insert()

	def validate_and_fetch_cheque_book(self):
		"""Validate cheque number and fetch the correct cheque book"""
		if not self.cheque_number or not self.voucher_account:
			return
		
		# voucher_account is the Bank Account name, not Account name
		# We need to find the Bank Account record directly
		bank_account = self.voucher_account

		# Verify the Bank Account exists and is a company account
		bank_account_doc = frappe.db.get_value("Bank Account",
			{"name": bank_account, "is_company_account": 1}, 
			["name", "account"], as_dict=True)

		if not bank_account_doc:
			frappe.throw(f"Bank Account '{bank_account}' not found or not a company account")

		# Find cheque book that matches the Bank Account and contains the cheque number
		cheque_book = frappe.db.get_value("Cheque Book",
			{
				"bank_account": bank_account,
				"is_active": 1,
				"start_series": ["<=", self.cheque_number],
				"end_series": [">=", self.cheque_number]
			},
			["name", "start_series", "end_series", "current_series"],
			as_dict=True
		)
		
		if not cheque_book:
			frappe.throw(f"No active cheque book found for Bank Account '{bank_account}' containing cheque number '{self.cheque_number}'")
		
		# Check if cheque number is already used
		existing_cheque = frappe.db.exists("Cheque", {
			"cheque_number": self.cheque_number,
			"cheque_book": cheque_book.name
		})
		
		if existing_cheque:
			frappe.throw(f"Cheque number '{self.cheque_number}' is already used in cheque book '{cheque_book.name}'")
		
		# Store the cheque book name for later use
		self.cheque_book_name = cheque_book.name
		# Also store the bank account for reference
		self.bank_account_name = bank_account
