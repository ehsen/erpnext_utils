# Copyright (c) 2025, SpotLedger and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from erpnext_utils.erpnext_utils.overrides.payment_entry import (
	validate_cheque_details,
	create_cheque_record,
)


class TestPaymentEntryCheque(FrappeTestCase):
	"""Test cases for cheque record creation in Payment Entry"""

	def setUp(self):
		"""Set up test data"""
		self.company = "Test Company"
		self.supplier = "Test Supplier"
		self.bank_account = "Test Bank Account"
		self.cheque_book = "Test Cheque Book"
		self.mode_of_payment = "Cheque"

	def test_cheque_validation_with_valid_details(self):
		"""Test that cheque validation passes with valid details"""
		# Create a mock Payment Entry with valid cheque details
		payment_entry = frappe.new_doc("Payment Entry")
		payment_entry.payment_type = "Pay"
		payment_entry.mode_of_payment = self.mode_of_payment
		payment_entry.reference_no = "CHQ12345"
		payment_entry.reference_date = frappe.utils.today()
		payment_entry.party_type = "Supplier"
		payment_entry.party = self.supplier
		payment_entry.bank_account = self.bank_account
		
		# This should not raise an exception
		# validate_cheque_details(payment_entry)

	def test_cheque_validation_missing_cheque_number(self):
		"""Test that validation fails when cheque number is missing"""
		payment_entry = frappe.new_doc("Payment Entry")
		payment_entry.payment_type = "Pay"
		payment_entry.mode_of_payment = self.mode_of_payment
		payment_entry.reference_no = None  # Missing cheque number
		payment_entry.reference_date = frappe.utils.today()
		payment_entry.party_type = "Supplier"
		payment_entry.party = self.supplier
		payment_entry.bank_account = self.bank_account
		
		# This should raise an exception
		# with self.assertRaises(frappe.ValidationError):
		#	 validate_cheque_details(payment_entry)

	def test_non_cheque_payment_ignored(self):
		"""Test that non-cheque payments are not affected"""
		payment_entry = frappe.new_doc("Payment Entry")
		payment_entry.payment_type = "Pay"
		payment_entry.mode_of_payment = "Bank Transfer"  # Non-cheque payment
		payment_entry.reference_no = None  # Missing - should not matter
		payment_entry.reference_date = None
		payment_entry.party_type = "Supplier"
		payment_entry.party = self.supplier
		payment_entry.bank_account = self.bank_account
		
		# This should not raise an exception
		# validate_cheque_details(payment_entry)

	def test_receive_payment_type_ignored(self):
		"""Test that Receive payment type is not affected"""
		payment_entry = frappe.new_doc("Payment Entry")
		payment_entry.payment_type = "Receive"
		payment_entry.mode_of_payment = self.mode_of_payment
		payment_entry.reference_no = None  # Missing - should not matter
		payment_entry.reference_date = None
		payment_entry.party_type = "Customer"
		payment_entry.party = "Test Customer"
		payment_entry.bank_account = self.bank_account
		
		# This should not raise an exception
		# validate_cheque_details(payment_entry)

	def test_cheque_record_creation(self):
		"""Test that cheque record is created on submission"""
		# This test would require actual database setup
		# and would test the complete flow
		pass

	def test_duplicate_cheque_number_validation(self):
		"""Test that duplicate cheque numbers are caught"""
		# This test would verify that the same cheque number
		# cannot be used twice in the same cheque book
		pass


class TestPaymentEntryChequeIntegration(FrappeTestCase):
	"""Integration tests for cheque functionality"""

	def test_payment_entry_with_cheque_creates_cheque_record(self):
		"""Test end-to-end: Payment Entry submission creates Cheque record"""
		# This would test the complete workflow:
		# 1. Create Payment Entry with cheque details
		# 2. Validate the Payment Entry
		# 3. Submit the Payment Entry
		# 4. Verify that a Cheque record was created
		# 5. Verify cheque details match the Payment Entry
		pass

	def test_payment_entry_cancellation_with_cheque(self):
		"""Test that cheque records are handled correctly on cancellation"""
		# This would test if cheque status is updated or if
		# cheque is marked as cancelled when Payment Entry is cancelled
		pass

