# Copyright (c) 2025, SpotLedger and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class ChequeBook(Document):
	def validate(self):
		# Validate that series fields contain only numeric values
		self.validate_numeric_fields()
		
		# Convert to integers for comparison
		start_series = int(self.start_series)
		end_series = int(self.end_series)
		current_series = int(self.current_series) if self.current_series else None
		
		if start_series >= end_series:
			frappe.throw("Start Series must be less than End Series")
		
		if not self.current_series:
			self.current_series = self.start_series
			current_series = int(self.current_series)
		
		if current_series < start_series or current_series > end_series:
			frappe.throw("Current Series must be between Start Series and End Series")
	
	def validate_numeric_fields(self):
		"""Validate that series fields contain only numeric values"""
		try:
			int(self.start_series)
			int(self.end_series)
			if self.current_series:
				int(self.current_series)
		except (ValueError, TypeError):
			frappe.throw("Series fields must contain only numeric values")
	
	def get_next_cheque_number(self):
		"""Get the next available cheque number"""
		current_series = int(self.current_series)
		end_series = int(self.end_series)
		
		if current_series > end_series:
			frappe.throw(f"No more cheques available in this cheque book. Last cheque number: {self.end_series}")
		
		next_number = current_series
		self.current_series = str(current_series + 1)
		self.save()
		return next_number
