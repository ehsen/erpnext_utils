import frappe
from frappe.model.naming import make_autoname


def create_voucher_name(self):
    #TODO This should be revemod. name should come from naming series
    if not self.company:
        frappe.throw("Please select a Company before saving.")

    company_abbr = frappe.db.get_value("Company", self.company, "abbr")
    if not company_abbr:
        frappe.throw(f"Abbreviation not found for Company {self.company}")

    fiscal_year = frappe.defaults.get_user_default("fiscal_year") or frappe.get_date().split("-")[0]
    year_suffix = fiscal_year[-2:]  # Get 'YY'

    # Pick prefix based on DocType name
    prefix_map = {
        "Cash Payment Voucher": "CP",
        "Bank Payment Voucher": "BP",
        "Bank Receipt Voucher": "BR",
        "Cash Receipt Voucher": "CR"
    }

    short_code = prefix_map.get(self.doctype, "XX")
    self.name = make_autoname(f"{short_code}-{company_abbr}-{year_suffix}-#####")


