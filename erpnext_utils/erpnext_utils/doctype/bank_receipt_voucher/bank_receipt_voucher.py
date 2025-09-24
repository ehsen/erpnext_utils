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

	def on_submit(self):
		# Create cheque record if instrument type is Cheque
		if self.instrument_type == "Cheque":
			self.create_cheque_record()
			
			# Check if it's a post dated cheque
			if self.cheque_date > today():
				# Create post dated cheque GL entries
				from erpnext_utils.erpnext_utils.controllers.voucher_controller import create_post_dated_cheque_gl_entries
				create_post_dated_cheque_gl_entries(self.posting_date, self.accounts, self.company, 
					"Bank Receipt", self.voucher_account, "Bank Receipt Voucher", self.name,
					self.cheque_date, self.cheque_number)
			else:
				# Create normal GL entries for current date cheques
				create_gl_entries(self.posting_date, self.accounts, self.company, "Bank Receipt",
						self.voucher_account, "Bank Receipt Voucher", self.name)
		else:
			# Create normal GL entries for non-cheque instruments
			create_gl_entries(self.posting_date, self.accounts, self.company, "Bank Receipt",
					self.voucher_account, "Bank Receipt Voucher", self.name)

	def create_cheque_record(self):
		"""Create cheque record for cheque receipts"""
		cheque_doc = frappe.new_doc("Cheque")
		cheque_doc.cheque_number = self.cheque_number
		cheque_doc.cheque_date = self.cheque_date
		cheque_doc.bank_account = self.voucher_account
		cheque_doc.party_type = self.party_type
		cheque_doc.party = self.party
		cheque_doc.status = "Unpresented"
		cheque_doc.amount = self.total_payment
		
		# Try to find and link the cheque book
		cheque_book = frappe.db.get_value("Cheque Book", 
			{"bank_account": self.voucher_account, "is_active": 1}, "name")
		if cheque_book:
			cheque_doc.cheque_book = cheque_book
		
		cheque_doc.insert()
