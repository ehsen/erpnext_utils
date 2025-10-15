# Copyright (c) 2025, SpotLedger and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today
from erpnext_utils.erpnext_utils.controllers.voucher_controller import (validate_accounts_child_table, validate_accounting_equation, 
create_gl_entries)


class BankReceiptVoucher(Document):
	pass

	def validate(self):
		validate_accounts_child_table(self)
		validate_accounting_equation(self)
		self.total_payment = sum(flt(row.amount or 0) for row in self.accounts)

		# gl_bank_account is automatically fetched from voucher_account.account via fetch_from
		# No need to set it manually
		
		# Validate cheque details if instrument type is Cheque
		if self.instrument_type == "Cheque":
			if not self.cheque_number:
				frappe.throw("Cheque Number is mandatory when Instrument Type is Cheque")
			if not self.cheque_date:
				frappe.throw("Cheque Date is mandatory when Instrument Type is Cheque")
			if not self.bank:
				frappe.throw("Bank is mandatory when Instrument Type is Cheque")
			if not self.party_type:
				frappe.throw("Party Type is mandatory when Instrument Type is Cheque")
			if not self.received_from:
				frappe.throw("Received From (Party) is mandatory when Instrument Type is Cheque")
			
			# For receipts, we don't need to validate cheque book as we're receiving cheques
			# Just validate that the cheque number is not already received
			self.validate_received_cheque()

	def on_submit(self):
		# Create cheque record if instrument type is Cheque
		if self.instrument_type == "Cheque":
			self.create_cheque_record()
			
			# Check if it's a post dated cheque
			if self.cheque_date > today():
				# Create post dated cheque GL entries using gl_bank_account
				from erpnext_utils.erpnext_utils.controllers.voucher_controller import create_post_dated_cheque_gl_entries
				create_post_dated_cheque_gl_entries(self.posting_date, self.accounts, self.company, 
					"Bank Receipt", self.gl_bank_account, "Bank Receipt Voucher", self.name,
					self.cheque_date, self.cheque_number)
			else:
				# Create normal GL entries for current date cheques using gl_bank_account
				create_gl_entries(self.posting_date, self.accounts, self.company, "Bank Receipt",
						self.gl_bank_account, "Bank Receipt Voucher", self.name)
		else:
			# Create normal GL entries for non-cheque instruments using gl_bank_account
			create_gl_entries(self.posting_date, self.accounts, self.company, "Bank Receipt",
					self.gl_bank_account, "Bank Receipt Voucher", self.name)

	def create_cheque_record(self):
		"""Create cheque record for cheque receipts"""
		cheque_doc = frappe.new_doc("Cheque")
		cheque_doc.cheque_number = self.cheque_number
		cheque_doc.cheque_date = self.cheque_date
		cheque_doc.party_type = self.party_type

		cheque_doc.party = self.received_from
		cheque_doc.status = "Unpresented"
		cheque_doc.cheque_type = "Received"
		cheque_doc.amount = self.total_payment
		cheque_doc.bank = self.bank  # Bank from which cheque is received
		
		# For receipts, we don't set bank_account field - only bank field is used
		# This distinguishes received cheques from issued cheques
		
		cheque_doc.insert()

	def validate_received_cheque(self):
		"""Validate received cheque number"""
		if not self.cheque_number:
			return
		
		# Check if this cheque number is already received from the same party and bank
		existing_cheque = frappe.db.exists("Cheque", {
			"cheque_number": self.cheque_number,
			"party_type": self.party_type,
			"party": self.received_from,
			"bank": self.bank,
			"status": ["!=", "Cancelled"]
		})
		
		if existing_cheque:
			frappe.throw(f"Cheque number '{self.cheque_number}' from {self.party_type} '{self.received_from}' drawn on {self.bank} has already been received")
		
		# Additional validation: Check if cheque date is not too far in the past
		from frappe.utils import add_days
		if self.cheque_date < add_days(today(), -365):  # Not older than 1 year
			frappe.throw(f"Cheque date '{self.cheque_date}' is too old. Cheques older than 1 year are not accepted")
