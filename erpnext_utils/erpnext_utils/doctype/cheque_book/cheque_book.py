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
		"""Get the next available cheque number as a string.

		Preserves formatting (e.g. leading zeros) to match the cheque number
		series width defined by the configured range.
		"""
		# Determine the target width based on the configured range bounds
		width = max(len(str(self.start_series or "")), len(str(self.end_series or "")))

		# Work with integers for bounds checking, but preserve string formatting for return
		current_series_str = str(self.current_series)
		current_series_int = int(current_series_str)
		end_series_int = int(self.end_series)
		
		if current_series_int > end_series_int:
			frappe.throw(
				f"No more cheques available in this cheque book. Last cheque number: {self.end_series}"
			)
		
		# Return the current cheque number as a zero-padded string (if width known)
		next_number_str = (
			str(current_series_int).zfill(width) if width else current_series_str
		)

		# Increment and persist the next current_series, preserving width
		self.current_series = (
			str(current_series_int + 1).zfill(width)
			if width
			else str(current_series_int + 1)
		)
		self.save()
		return next_number_str
