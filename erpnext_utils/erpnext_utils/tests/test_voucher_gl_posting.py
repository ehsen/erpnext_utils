"""
Regression tests for one-sided GL postings from the voucher doctypes.

Bug (ETPL issues log item 4, 6 Oct 2026): create_gl_entries swallowed every GL
Entry validation error, so a voucher whose account line was rejected still
reached docstatus 1 with only the bank/cash leg posted, leaving the trial
balance out of balance.

Rule under test: a voucher posts all of its GL lines or none of them, ERPNext's
own validation error reaches the user, and total debit always equals total
credit.
"""

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import flt, today

from erpnext_utils.erpnext_utils.controllers import voucher_controller

VOUCHER_DOCTYPES = [
	"Bank Payment Voucher",
	"Cash Payment Voucher",
	"Bank Receipt Voucher",
	"Cash Receipt Voucher",
]


class TestVoucherGLPosting(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.db.get_value("Company", {}, "name")
		cls.abbr = frappe.db.get_value("Company", cls.company, "abbr")
		cls.cost_center = frappe.db.get_value("Company", cls.company, "cost_center")

		assets = frappe.db.get_value(
			"Account", {"company": cls.company, "root_type": "Asset", "is_group": 1, "account_type": ""}, "name"
		)
		bank_parent = frappe.db.get_value(
			"Account", {"company": cls.company, "account_type": "Bank", "is_group": 1}, "name"
		)
		expenses = frappe.db.get_value("Account", {"company": cls.company, "root_type": "Expense", "is_group": 1}, "name")

		cls.bank_gl = cls._account("GLT Bank", bank_parent, "Asset", "Bank")
		cls.cash_gl = cls._account("GLT Cash", assets, "Asset", "Cash")
		# ETPL's 110701: an asset account wrongly typed Payable (needs a party on every line)
		cls.payable_asset = cls._account("GLT Loan to Directors", assets, "Asset", "Payable")
		# ETPL's 520146: an expense account with a type, which rejects a party
		cls.typed_expense = cls._account("GLT Fuel Expense", expenses, "Expense", "Expense Account")
		cls.plain_expense = cls._account("GLT Legal Expense", expenses, "Expense")

		if not frappe.db.exists("Bank", "GLT Bank"):
			frappe.get_doc(doctype="Bank", bank_name="GLT Bank").insert()
		cls.bank_account = frappe.get_doc(
			doctype="Bank Account",
			account_name="GLT Bank Account",
			bank="GLT Bank",
			account=cls.bank_gl,
			company=cls.company,
			is_company_account=1,
		).insert().name
		if not frappe.db.exists("Mode of Payment", "IBFT"):
			frappe.get_doc(doctype="Mode of Payment", mode_of_payment="IBFT", type="Bank").insert()
		cls.supplier = frappe.get_doc(
			doctype="Supplier",
			supplier_name="GLT Supplier",
			supplier_group=frappe.db.get_value("Supplier Group", {"is_group": 0}) or "All Supplier Groups",
		).insert().name

	@classmethod
	def tearDownClass(cls):
		frappe.db.rollback()
		super().tearDownClass()

	@classmethod
	def _account(cls, name, parent, root_type, account_type=""):
		return frappe.get_doc(
			doctype="Account",
			account_name=name,
			parent_account=parent,
			company=cls.company,
			root_type=root_type,
			account_type=account_type,
			is_group=0,
		).insert().name

	def setUp(self):
		super().setUp()
		frappe.db.savepoint("glt_test")
		self.addCleanup(frappe.db.rollback, save_point="glt_test")

	# helpers

	def row(self, account, amount, party_type=None, party=None):
		return {
			"account": account,
			"amount": amount,
			"cost_center": self.cost_center,
			"party_type": party_type,
			"party": party,
		}

	def make_voucher(self, doctype, rows):
		doc = {
			"doctype": doctype,
			"posting_date": today(),
			"company": self.company,
			"cost_center": self.cost_center,
			"remarks": "GL posting regression test",
			"accounts": rows,
		}
		if doctype.startswith("Bank"):
			doc.update(voucher_account=self.bank_account, instrument_type="IBFT")
		else:
			doc.update(voucher_account=self.cash_gl)
		voucher = frappe.get_doc(doc).insert()
		# the request-level rollback target: the saved draft
		frappe.db.savepoint("glt_draft")
		return voucher

	def gl(self, voucher):
		return frappe.get_all(
			"GL Entry",
			filters={"voucher_type": voucher.doctype, "voucher_no": voucher.name, "is_cancelled": 0},
			fields=["account", "debit", "credit"],
		)

	def assert_not_submitted_and_unposted(self, voucher):
		# No GL rows may exist the moment the error is raised: the posting rolls itself back.
		self.assertEqual(self.gl(voucher), [])
		# Frappe rolls the whole request back on an error, which returns the voucher to Draft.
		frappe.db.rollback(save_point="glt_draft")
		self.assertEqual(frappe.db.get_value(voucher.doctype, voucher.name, "docstatus"), 0)
		self.assertEqual(self.gl(voucher), [])

	def assert_balanced(self, voucher, expected_rows):
		entries = self.gl(voucher)
		self.assertEqual(len(entries), expected_rows)
		self.assertEqual(sum(flt(e.debit) for e in entries), sum(flt(e.credit) for e in entries))

	# the four voucher doctypes

	def test_control_posts_both_legs(self):
		for doctype in VOUCHER_DOCTYPES:
			with self.subTest(doctype=doctype):
				voucher = self.make_voucher(doctype, [self.row(self.plain_expense, 5000)])
				voucher.submit()
				self.assertEqual(voucher.docstatus, 1)
				self.assert_balanced(voucher, 2)

	def test_case_a_missing_party_on_payable_account_blocks_submit(self):
		for doctype in VOUCHER_DOCTYPES:
			with self.subTest(doctype=doctype):
				voucher = self.make_voucher(doctype, [self.row(self.payable_asset, 2_000_000)])
				with self.assertRaisesRegex(frappe.ValidationError, "Supplier is required against Payable account"):
					voucher.submit()
				self.assert_not_submitted_and_unposted(voucher)

	def test_case_b_party_on_non_party_account_blocks_submit(self):
		for doctype in VOUCHER_DOCTYPES:
			with self.subTest(doctype=doctype):
				voucher = self.make_voucher(
					doctype, [self.row(self.typed_expense, 23_000, "Supplier", self.supplier)]
				)
				with self.assertRaisesRegex(
					frappe.ValidationError, "Party Type and Party can only be set for Receivable / Payable"
				):
					voucher.submit()
				self.assert_not_submitted_and_unposted(voucher)

	def test_failure_on_later_line_leaves_no_gl_rows(self):
		# Row 1 is valid and posts before row 2 fails; nothing may remain, bank leg included.
		for doctype in VOUCHER_DOCTYPES:
			with self.subTest(doctype=doctype):
				voucher = self.make_voucher(
					doctype,
					[self.row(self.plain_expense, 1000), self.row(self.payable_asset, 2000)],
				)
				with self.assertRaises(frappe.ValidationError):
					voucher.submit()
				self.assert_not_submitted_and_unposted(voucher)

	def test_valid_multi_line_voucher_posts_every_line(self):
		for doctype in VOUCHER_DOCTYPES:
			with self.subTest(doctype=doctype):
				voucher = self.make_voucher(
					doctype,
					[
						self.row(self.plain_expense, 1000),
						self.row(self.typed_expense, 2000),
						self.row(self.payable_asset, 3000, "Supplier", self.supplier),
					],
				)
				voucher.submit()
				self.assert_balanced(voucher, 4)

	def test_unbalanced_posting_is_rejected_and_rolled_back(self):
		# Simulate a failure that does not raise: the bank leg is silently not written.
		real_post = voucher_controller.post_gl_entry

		def drop_bank_leg(gl_entry, gl_entries):
			if gl_entry.account == self.bank_gl:
				return
			real_post(gl_entry, gl_entries)

		voucher = self.make_voucher("Bank Payment Voucher", [self.row(self.plain_expense, 5000)])
		with patch.object(voucher_controller, "post_gl_entry", drop_bank_leg):
			with self.assertRaisesRegex(frappe.ValidationError, "out of balance"):
				voucher.submit()
		self.assert_not_submitted_and_unposted(voucher)

	# post-dated cheque path

	def pdc_accounts(self, *rows):
		return [frappe._dict(r) for r in rows]

	def post_dated(self, voucher, voucher_type, accounts):
		return voucher_controller.create_post_dated_cheque_gl_entries(
			today(),
			accounts,
			self.company,
			voucher_type,
			None,
			voucher.doctype,
			voucher.name,
			today(),
			"000123",
		)

	def test_post_dated_cheque_failure_leaves_no_gl_rows(self):
		rows = [self.row(self.plain_expense, 1000), self.row(self.payable_asset, 2000)]
		voucher = self.make_voucher("Bank Payment Voucher", rows)
		with patch.object(voucher_controller, "get_post_dated_cheque_account", return_value=self.bank_gl):
			with self.assertRaisesRegex(frappe.ValidationError, "Supplier is required against Payable account"):
				self.post_dated(voucher, "Bank Payment", [frappe._dict(r) for r in rows])
		self.assertEqual(self.gl(voucher), [])

	def test_post_dated_cheque_valid_posts_balanced(self):
		rows = [self.row(self.plain_expense, 1000)]
		voucher = self.make_voucher("Bank Payment Voucher", rows)
		with patch.object(voucher_controller, "get_post_dated_cheque_account", return_value=self.bank_gl):
			names = self.post_dated(voucher, "Bank Payment", [frappe._dict(r) for r in rows])
		self.assertEqual(len(names), 2)
		self.assert_balanced(voucher, 2)

	def test_unset_post_dated_cheque_account_is_an_error_not_a_skipped_leg(self):
		with patch("frappe.db.get_single_value", return_value=None):
			with self.assertRaisesRegex(frappe.ValidationError, "Default Post Dated Cheque Account"):
				voucher_controller.get_post_dated_cheque_account()
