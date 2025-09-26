# Copyright (c) 2024, SpotLedger and Contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate


class GateEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from erpnext_utils.erpnext_utils.doctype.gate_entry_item.gate_entry_item import GateEntryItem

		amended_from: DF.Link | None
		company: DF.Link
		contact_number: DF.Data | None
		customer: DF.Link | None
		customer_name: DF.Data | None
		driver_name: DF.Data | None
		gate_entry_date: DF.Date
		gate_entry_type: DF.Literal["Inward", "Outward"]
		items: DF.Table[GateEntryItem]
		naming_series: DF.Literal["GE-.YYYY.-"]
		purpose: DF.Text | None
		remarks: DF.Text | None
		status: DF.Data | None
		supplier: DF.Link | None
		supplier_name: DF.Data | None
		title: DF.Data
		total_amount: DF.Currency
		total_qty: DF.Float
		vehicle_number: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.validate_dates()
		self.validate_items()
		self.calculate_totals()
		self.set_party_name()

	def validate_dates(self):
		if self.gate_entry_date and getdate(self.gate_entry_date) > getdate():
			frappe.throw(_("Gate Entry Date cannot be in the future"))

	def validate_items(self):
		if not self.items:
			frappe.throw(_("Please add at least one item"))

		for item in self.items:
			if not item.qty or item.qty <= 0:
				frappe.throw(_("Quantity must be greater than 0 for item {0}").format(item.item_code))

	def calculate_totals(self):
		total_qty = 0
		total_amount = 0

		for item in self.items:
			total_qty += flt(item.qty)
			total_amount += flt(item.amount)

		self.total_qty = total_qty
		self.total_amount = total_amount

	def set_party_name(self):
		if self.gate_entry_type == "Inward" and self.supplier:
			self.supplier_name = frappe.db.get_value("Supplier", self.supplier, "supplier_name")
		elif self.gate_entry_type == "Outward" and self.customer:
			self.customer_name = frappe.db.get_value("Customer", self.customer, "customer_name")

	def on_submit(self):
		self.status = "Submitted"
		self.update_material_request_status()

	def on_cancel(self):
		self.status = "Cancelled"
		self.update_material_request_status()

	def update_material_request_status(self):
		"""Update status of linked Material Requests"""
		material_requests = set()
		for item in self.items:
			if item.material_request:
				material_requests.add(item.material_request)

		for mr in material_requests:
			# Update Material Request status based on Gate Entry status
			if self.status == "Submitted":
				frappe.db.set_value("Material Request", mr, "status", "Partially Ordered")
			elif self.status == "Cancelled":
				frappe.db.set_value("Material Request", mr, "status", "Pending")


@frappe.whitelist()
def make_purchase_order_from_gate_entry(source_name, target_doc=None):
	"""Create Purchase Order from Gate Entry"""
	def postprocess(source, target_doc):
		target_doc.supplier = source.supplier
		target_doc.supplier_name = source.supplier_name
		target_doc.company = source.company
		target_doc.transaction_date = source.gate_entry_date

	def select_item(d):
		return d.material_request and d.material_request_item

	doclist = get_mapped_doc(
		"Gate Entry",
		source_name,
		{
			"Gate Entry": {
				"doctype": "Purchase Order",
				"validation": {"docstatus": ["=", 1]},
			},
			"Gate Entry Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "gate_entry_item"],
					["parent", "gate_entry"],
					["uom", "stock_uom"],
					["uom", "uom"],
				],
				"condition": select_item,
			},
		},
		target_doc,
		postprocess,
	)

	# Debug: Print the mapped items to verify gate_entry_item is set
	if doclist and hasattr(doclist, 'items'):
		for item in doclist.items:
			frappe.logger().info(f"PO Item {item.item_code}: gate_entry={item.gate_entry}, gate_entry_item={item.gate_entry_item}")

	return doclist


@frappe.whitelist()
def get_gate_entry_dashboard_data(name):
	"""Get dashboard data for Gate Entry"""
	doc = frappe.get_doc("Gate Entry", name)
	
	# Get linked Purchase Orders
	purchase_orders = frappe.get_all(
		"Purchase Order Item",
		filters={"gate_entry": name},
		fields=["parent"],
		distinct=True
	)
	
	# Get linked Purchase Receipts
	purchase_receipts = frappe.get_all(
		"Purchase Receipt Item",
		filters={"gate_entry": name},
		fields=["parent"],
		distinct=True
	)
	
	# Get linked Purchase Invoices
	purchase_invoices = frappe.get_all(
		"Purchase Invoice Item",
		filters={"gate_entry": name},
		fields=["parent"],
		distinct=True
	)

	return {
		"purchase_orders": [po.parent for po in purchase_orders],
		"purchase_receipts": [pr.parent for pr in purchase_receipts],
		"purchase_invoices": [pi.parent for pi in purchase_invoices],
	}


@frappe.whitelist()
def get_material_requests_for_gate_entry():
	"""Get Material Requests that can be used for Gate Entry"""
	# Get Material Requests with Purchase type and pending/partially ordered status
	material_requests = frappe.get_all(
		"Material Request",
		filters={
			"material_request_type": "Purchase",
			"status": ["in", ["Pending", "Partially Ordered"]],
			"docstatus": 1
		},
		fields=["name", "title", "transaction_date", "schedule_date", "status"],
		order_by="transaction_date desc"
	)
	
	return material_requests


@frappe.whitelist()
def get_material_request_items(material_request):
	"""Get items from a specific Material Request"""
	if not material_request:
		return []
	
	# Get Material Request Items - for pending MRs, ordered_qty is 0, so we check if stock_qty > 0
	items = frappe.get_all(
		"Material Request Item",
		filters={
			"parent": material_request,
			"stock_qty": [">", 0]
		},
		fields=[
			"name",
			"item_code",
			"item_name",
			"description",
			"qty",
			"stock_qty",
			"ordered_qty",
			"uom",
			"warehouse",
			"rate"
		]
	)
	
	# Filter items where ordered_qty < stock_qty (meaning there are still items to be ordered)
	filtered_items = []
	for item in items:
		if flt(item.ordered_qty) < flt(item.stock_qty):
			filtered_items.append(item)
	
	return filtered_items


@frappe.whitelist()
def make_gate_entry_from_material_request(source_name, target_doc=None):
	"""Create Gate Entry from Material Request"""
	def postprocess(source, target_doc):
		target_doc.gate_entry_type = "Inward"
		target_doc.gate_entry_date = frappe.utils.today()
		target_doc.company = frappe.defaults.get_user_default("Company")

	def select_item(d):
		return d.ordered_qty < d.stock_qty

	doclist = get_mapped_doc(
		"Material Request",
		source_name,
		{
			"Material Request": {
				"doctype": "Gate Entry",
				"validation": {"docstatus": ["=", 1], "material_request_type": ["=", "Purchase"]},
			},
			"Material Request Item": {
				"doctype": "Gate Entry Item",
				"field_map": [
					["name", "material_request_item"],
					["parent", "material_request"],
					["qty", "qty"],
					["stock_qty", "qty"],
					["uom", "uom"],
					["rate", "rate"],
				],
				"postprocess": update_item,
				"condition": select_item,
			},
		},
		target_doc,
		postprocess,
	)

	return doclist


def update_item(source, target, source_parent):
	target.amount = target.qty * (target.rate or 0)


@frappe.whitelist()
def verify_gate_entry_item_references(gate_entry_name):
	"""Verify that all procurement documents have correct Gate Entry Item references"""
	# Get all Purchase Order Items that reference this Gate Entry
	po_items = frappe.get_all(
		"Purchase Order Item",
		filters={"gate_entry": gate_entry_name},
		fields=["name", "parent", "item_code", "gate_entry", "gate_entry_item", "material_request", "material_request_item"]
	)
	
	# Get all Purchase Receipt Items that reference this Gate Entry
	pr_items = frappe.get_all(
		"Purchase Receipt Item",
		filters={"gate_entry": gate_entry_name},
		fields=["name", "parent", "item_code", "gate_entry", "gate_entry_item", "purchase_order", "purchase_order_item"]
	)
	
	# Get all Purchase Invoice Items that reference this Gate Entry
	pi_items = frappe.get_all(
		"Purchase Invoice Item",
		filters={"gate_entry": gate_entry_name},
		fields=["name", "parent", "item_code", "gate_entry", "gate_entry_item", "purchase_receipt", "pr_detail"]
	)
	
	result = {
		"gate_entry": gate_entry_name,
		"purchase_orders": {
			"total_items": len(po_items),
			"items_with_gate_entry_item": 0,
			"items_without_gate_entry_item": 0,
			"details": []
		},
		"purchase_receipts": {
			"total_items": len(pr_items),
			"items_with_gate_entry_item": 0,
			"items_without_gate_entry_item": 0,
			"details": []
		},
		"purchase_invoices": {
			"total_items": len(pi_items),
			"items_with_gate_entry_item": 0,
			"items_without_gate_entry_item": 0,
			"details": []
		}
	}
	
	# Process Purchase Order Items
	for item in po_items:
		item_detail = {
			"item_name": item.name,
			"parent_doc": item.parent,
			"item_code": item.item_code,
			"gate_entry": item.gate_entry,
			"gate_entry_item": item.gate_entry_item,
			"material_request": item.material_request,
			"material_request_item": item.material_request_item
		}
		
		if item.gate_entry_item:
			result["purchase_orders"]["items_with_gate_entry_item"] += 1
		else:
			result["purchase_orders"]["items_without_gate_entry_item"] += 1
			
		result["purchase_orders"]["details"].append(item_detail)
	
	# Process Purchase Receipt Items
	for item in pr_items:
		item_detail = {
			"item_name": item.name,
			"parent_doc": item.parent,
			"item_code": item.item_code,
			"gate_entry": item.gate_entry,
			"gate_entry_item": item.gate_entry_item,
			"purchase_order": item.purchase_order,
			"purchase_order_item": item.purchase_order_item
		}
		
		if item.gate_entry_item:
			result["purchase_receipts"]["items_with_gate_entry_item"] += 1
		else:
			result["purchase_receipts"]["items_without_gate_entry_item"] += 1
			
		result["purchase_receipts"]["details"].append(item_detail)
	
	# Process Purchase Invoice Items
	for item in pi_items:
		item_detail = {
			"item_name": item.name,
			"parent_doc": item.parent,
			"item_code": item.item_code,
			"gate_entry": item.gate_entry,
			"gate_entry_item": item.gate_entry_item,
			"purchase_receipt": item.purchase_receipt,
			"pr_detail": item.pr_detail
		}
		
		if item.gate_entry_item:
			result["purchase_invoices"]["items_with_gate_entry_item"] += 1
		else:
			result["purchase_invoices"]["items_without_gate_entry_item"] += 1
			
		result["purchase_invoices"]["details"].append(item_detail)
	
	return result
