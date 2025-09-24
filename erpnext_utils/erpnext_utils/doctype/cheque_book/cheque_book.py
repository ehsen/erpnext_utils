# Copyright (c) 2025, SpotLedger and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class ChequeBook(Document):
	def validate(self):
		if self.start_series >= self.end_series:
			frappe.throw("Start Series must be less than End Series")
		
		if not self.current_series:
			self.current_series = self.start_series
		
		if self.current_series < self.start_series or self.current_series > self.end_series:
			frappe.throw("Current Series must be between Start Series and End Series")
	
	def get_next_cheque_number(self):
		"""Get the next available cheque number"""
		if self.current_series > self.end_series:
			frappe.throw(f"No more cheques available in this cheque book. Last cheque number: {self.end_series}")
		
		next_number = self.current_series
		self.current_series += 1
		self.save()
		return next_number
