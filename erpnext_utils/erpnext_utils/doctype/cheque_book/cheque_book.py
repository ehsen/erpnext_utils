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
		"""Get the next cheque number and increment current series"""
		if not self.current_series:
			frappe.throw("Current series is not set")
		
		# Store the current cheque number to return
		current_cheque_number = str(self.current_series)
		
		# Convert to integers for calculation
		current_int = int(self.current_series)
		end_int = int(self.end_series)
		
		# Check if we've reached the end of the series
		if current_int >= end_int:
			frappe.throw(f"Cheque series has reached the end. Current: {current_int}, End: {end_int}")
		
		# Increment current series for next call
		next_int = current_int + 1
		
		# Preserve original formatting by padding with zeros if needed
		original_length = len(str(self.start_series))
		self.current_series = str(next_int).zfill(original_length)
		
		# Save the document to persist the updated current_series
		self.save()
		
		return current_cheque_number
	
