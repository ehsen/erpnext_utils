# Copyright (c) 2024, SpotLedger and Contributors
# License: MIT. See license.txt

from frappe import _


def get_data():
	return {
		"fieldname": "gate_entry",
		"non_standard_fieldnames": {
			"Journal Entry": "reference_name",
			"Payment Entry": "reference_name",
			"Payment Request": "reference_name",
			"Auto Repeat": "reference_document",
		},
		"internal_links": {
			"Material Request": ["items", "material_request"],
		},
		"transactions": [
			{"label": _("Related"), "items": ["Purchase Order", "Purchase Receipt", "Purchase Invoice"]},
			{"label": _("Reference"), "items": ["Material Request"]},
		],
	}
