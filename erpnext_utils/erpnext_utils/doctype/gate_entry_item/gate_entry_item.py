# Copyright (c) 2024, SpotLedger and Contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GateEntryItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		description: DF.Text | None
		item_code: DF.Link
		item_name: DF.Data | None
		material_request: DF.Link | None
		material_request_item: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Float
		rate: DF.Currency
		remarks: DF.Text | None
		uom: DF.Link
		warehouse: DF.Link | None
	# end: auto-generated types

	def validate(self):
		self.validate_material_request()
		self.calculate_amount()

	def validate_material_request(self):
		"""Validate Material Request and Item linkage"""
		if self.material_request and self.material_request_item:
			# Check if the Material Request Item exists and matches
			mr_item = frappe.get_doc("Material Request Item", self.material_request_item)
			if mr_item.parent != self.material_request:
				frappe.throw(_("Material Request Item {0} does not belong to Material Request {1}").format(
					self.material_request_item, self.material_request
				))
			
			if mr_item.item_code != self.item_code:
				frappe.throw(_("Item Code {0} does not match Material Request Item {1}").format(
					self.item_code, self.material_request_item
				))

	def calculate_amount(self):
		"""Calculate amount based on qty and rate"""
		self.amount = self.qty * (self.rate or 0)
