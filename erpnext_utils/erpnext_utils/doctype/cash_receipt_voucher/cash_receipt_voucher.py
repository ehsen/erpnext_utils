# Copyright (c) 2025, SpotLedger and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext_utils.erpnext_utils.controllers.voucher_controller import (validate_accounts_child_table, validate_accounting_equation, 
create_gl_entries)


class CashReceiptVoucher(Document):
	pass

	def validate(self):
		validate_accounts_child_table(self)
		validate_accounting_equation(self)
		self.total_payment = sum(flt(row.amount or 0) for row in self.accounts)

	def on_submit(self):
		create_gl_entries(self.posting_date,self.accounts,self.company,"Receipt",
					self.voucher_account,"Cash Receipt Voucher",self.name)
