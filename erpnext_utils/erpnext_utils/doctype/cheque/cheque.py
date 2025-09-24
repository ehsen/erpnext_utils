# Copyright (c) 2025, SpotLedger and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class Cheque(Document):
	def validate(self):
		if self.party_type and not self.party:
			frappe.throw("Party is mandatory when Party Type is specified")
		
		if self.party and not self.party_type:
			frappe.throw("Party Type is mandatory when Party is specified")
		
		# Validate party exists
		if self.party_type and self.party:
			if not frappe.db.exists(self.party_type, self.party):
				frappe.throw(f"{self.party_type} '{self.party}' does not exist")
	
	def on_update(self):
		# Update status based on cheque date
		if self.cheque_date == today() and self.status == "Unpresented":
			# This is a current date cheque, no special handling needed
			pass
		elif self.cheque_date > today() and self.status == "Unpresented":
			# This is a post dated cheque
			pass
