// Copyright (c) 2024, SpotLedger and Contributors
// License: MIT. See license.txt

frappe.ui.form.on('Gate Entry', {
	refresh: function(frm) {
		// Add custom buttons
		if (frm.doc.docstatus === 1 && frm.doc.gate_entry_type === 'Inward') {
			frm.add_custom_button(__('Create Purchase Order'), function() {
				frappe.call({
					method: 'erpnext_utils.erpnext_utils.doctype.gate_entry.gate_entry.make_purchase_order_from_gate_entry',
					args: {
						source_name: frm.doc.name
					},
					callback: function(r) {
						if (r.exc) return;
						
						var doclist = frappe.model.sync(r.message);
						frappe.set_route('Form', 'Purchase Order', doclist[0].name);
					}
				});
			}, __('Create'));
		}

		// Add button to get items from Material Request
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__('Get Items from Material Request'), function() {
				show_material_request_dialog(frm);
			}, __('Get Items'));
		}

		// Add button to verify Gate Entry Item references
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Verify References'), function() {
				frappe.call({
					method: 'erpnext_utils.erpnext_utils.doctype.gate_entry.gate_entry.verify_gate_entry_item_references',
					args: {
						gate_entry_name: frm.doc.name
					},
					callback: function(r) {
						if (r.exc) return;
						
						var result = r.message;
						var msg = __('<h4>Gate Entry: {0}</h4>', [result.gate_entry]);
						
						// Purchase Orders
						msg += __('<h5>Purchase Orders</h5>');
						msg += __('Total Items: {0} | With Gate Entry Item: {1} | Without: {2}<br>', 
							[result.purchase_orders.total_items, result.purchase_orders.items_with_gate_entry_item, result.purchase_orders.items_without_gate_entry_item]);
						
						if (result.purchase_orders.details.length > 0) {
							result.purchase_orders.details.forEach(function(item) {
								msg += __('&nbsp;&nbsp;PO: {0} | Item: {1} | Gate Entry Item: {2}<br>', 
									[item.parent_doc, item.item_code, item.gate_entry_item || 'MISSING']);
							});
						}
						
						// Purchase Receipts
						msg += __('<h5>Purchase Receipts</h5>');
						msg += __('Total Items: {0} | With Gate Entry Item: {1} | Without: {2}<br>', 
							[result.purchase_receipts.total_items, result.purchase_receipts.items_with_gate_entry_item, result.purchase_receipts.items_without_gate_entry_item]);
						
						if (result.purchase_receipts.details.length > 0) {
							result.purchase_receipts.details.forEach(function(item) {
								msg += __('&nbsp;&nbsp;PR: {0} | Item: {1} | Gate Entry Item: {2}<br>', 
									[item.parent_doc, item.item_code, item.gate_entry_item || 'MISSING']);
							});
						}
						
						// Purchase Invoices
						msg += __('<h5>Purchase Invoices</h5>');
						msg += __('Total Items: {0} | With Gate Entry Item: {1} | Without: {2}<br>', 
							[result.purchase_invoices.total_items, result.purchase_invoices.items_with_gate_entry_item, result.purchase_invoices.items_without_gate_entry_item]);
						
						if (result.purchase_invoices.details.length > 0) {
							result.purchase_invoices.details.forEach(function(item) {
								msg += __('&nbsp;&nbsp;PI: {0} | Item: {1} | Gate Entry Item: {2}<br>', 
									[item.parent_doc, item.item_code, item.gate_entry_item || 'MISSING']);
							});
						}
						
						frappe.msgprint({
							title: __('Gate Entry Item References Verification'),
							message: msg,
							indicator: (result.purchase_orders.items_without_gate_entry_item > 0 || 
									   result.purchase_receipts.items_without_gate_entry_item > 0 || 
									   result.purchase_invoices.items_without_gate_entry_item > 0) ? 'red' : 'green'
						});
					}
				});
			}, __('Tools'));
		}
	},

	gate_entry_type: function(frm) {
		// Clear party fields when type changes
		if (frm.doc.gate_entry_type === 'Inward') {
			frm.set_value('customer', '');
			frm.set_value('customer_name', '');
		} else if (frm.doc.gate_entry_type === 'Outward') {
			frm.set_value('supplier', '');
			frm.set_value('supplier_name', '');
		}
	},

	supplier: function(frm) {
		if (frm.doc.supplier) {
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Supplier',
					name: frm.doc.supplier,
					fieldname: 'supplier_name'
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('supplier_name', r.message.supplier_name);
					}
				}
			});
		}
	},

	customer: function(frm) {
		if (frm.doc.customer) {
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Customer',
					name: frm.doc.customer,
					fieldname: 'customer_name'
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('customer_name', r.message.customer_name);
					}
				}
			});
		}
	},

	calculate_totals: function(frm) {
		var total_qty = 0;
		var total_amount = 0;

		$.each(frm.doc.items || [], function(i, item) {
			total_qty += flt(item.qty);
			total_amount += flt(item.amount);
		});

		frm.set_value('total_qty', total_qty);
		frm.set_value('total_amount', total_amount);
	}
});

frappe.ui.form.on('Gate Entry Item', {
	items_remove: function(frm) {
		frm.calculate_totals();
	},

	qty: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = flt(row.qty) * flt(row.rate);
		frm.refresh_field('items');
		frm.calculate_totals();
	},

	rate: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = flt(row.qty) * flt(row.rate);
		frm.refresh_field('items');
		frm.calculate_totals();
	},

	item_code: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.item_code) {
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Item',
					name: row.item_code,
					fieldname: ['item_name', 'stock_uom', 'description']
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, 'item_name', r.message.item_name);
						frappe.model.set_value(cdt, cdn, 'uom', r.message.stock_uom);
						frappe.model.set_value(cdt, cdn, 'description', r.message.description);
						frm.refresh_field('items');
					}
				}
			});
		}
	}
});

function show_material_request_dialog(frm) {
	// Get Material Requests
	frappe.call({
		method: 'erpnext_utils.erpnext_utils.doctype.gate_entry.gate_entry.get_material_requests_for_gate_entry',
		callback: function(r) {
			if (r.exc) return;
			
			if (r.message && r.message.length > 0) {
				// Show dialog to select Material Request
				var dialog = new frappe.ui.Dialog({
					title: __('Select Material Request'),
					fields: [
						{
							label: __('Material Request'),
							fieldname: 'material_request',
							fieldtype: 'Link',
							options: 'Material Request',
							reqd: 1,
							get_query: function() {
								return {
									filters: {
										'material_request_type': 'Purchase',
										'status': ['in', ['Pending', 'Partially Ordered']],
										'docstatus': 1
									}
								};
							}
						}
					],
					primary_action_label: __('Get Items'),
					primary_action: function(values) {
						if (values.material_request) {
							get_items_from_material_request(frm, values.material_request);
							dialog.hide();
						}
					}
				});
				
				dialog.show();
			} else {
				frappe.msgprint(__('No Material Requests found with Purchase type and Pending/Partially Ordered status'));
			}
		}
	});
}

function get_items_from_material_request(frm, material_request) {
	frappe.call({
		method: 'erpnext_utils.erpnext_utils.doctype.gate_entry.gate_entry.get_material_request_items',
		args: {
			material_request: material_request
		},
		callback: function(r) {
			if (r.exc) return;
			
			if (r.message && r.message.length > 0) {
				// Clear existing items
				frm.clear_table('items');
				
				// Add items from Material Request
				r.message.forEach(function(item) {
					var row = frm.add_child('items');
					row.item_code = item.item_code;
					row.item_name = item.item_name;
					row.description = item.description;
					row.qty = item.stock_qty; // Use stock_qty as it's the actual requested quantity
					row.uom = item.uom;
					row.material_request = material_request;
					row.material_request_item = item.name;
					row.warehouse = item.warehouse;
					row.rate = item.rate || 0;
					row.amount = flt(row.qty) * flt(row.rate);
				});
				
				frm.refresh_field('items');
				frm.calculate_totals();
				frappe.msgprint(__('Items added from Material Request {0}', [material_request]));
			} else {
				frappe.msgprint(__('No items found in Material Request {0} or all items are already ordered', [material_request]));
			}
		}
	});
}
