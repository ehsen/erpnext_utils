# Copyright (c) 2024, SpotLedger and Contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
	"""Override ERPNext's make_purchase_receipt to include Gate Entry references"""
	def update_item(obj, target, source_parent):
		target.qty = frappe.utils.flt(obj.qty) - frappe.utils.flt(obj.received_qty)
		target.stock_qty = (frappe.utils.flt(obj.qty) - frappe.utils.flt(obj.received_qty)) * frappe.utils.flt(obj.conversion_factor)
		target.amount = (frappe.utils.flt(obj.qty) - frappe.utils.flt(obj.received_qty)) * frappe.utils.flt(obj.rate)
		target.base_amount = (
			(frappe.utils.flt(obj.qty) - frappe.utils.flt(obj.received_qty)) * frappe.utils.flt(obj.rate) * frappe.utils.flt(source_parent.conversion_rate)
		)

	def set_missing_values(source, target):
		target.run_method("calculate_taxes_and_totals")

	doc = get_mapped_doc(
		"Purchase Order",
		source_name,
		{
			"Purchase Order": {
				"doctype": "Purchase Receipt",
				"field_map": {"supplier_warehouse": "supplier_warehouse"},
				"validation": {
					"docstatus": ["=", 1],
				},
			},
			"Purchase Order Item": {
				"doctype": "Purchase Receipt Item",
				"field_map": {
					"name": "purchase_order_item",
					"parent": "purchase_order",
					"bom": "bom",
					"material_request": "material_request",
					"material_request_item": "material_request_item",
					"sales_order": "sales_order",
					"sales_order_item": "sales_order_item",
					"wip_composite_asset": "wip_composite_asset",
					# Gate Entry references
					"gate_entry": "gate_entry",
					"gate_entry_item": "gate_entry_item",
				},
				"postprocess": update_item,
				"condition": lambda doc: abs(doc.received_qty) < abs(doc.qty)
				and doc.delivered_by_supplier != 1,
			},
			"Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "reset_value": True},
		},
		target_doc,
		set_missing_values,
	)

	return doc
