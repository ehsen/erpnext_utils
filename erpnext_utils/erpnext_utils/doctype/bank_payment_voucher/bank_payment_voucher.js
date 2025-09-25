frappe.ui.form.on('Bank Payment Voucher', {
    setup: function(frm) {
        // Restrict account field to bank accounts only
        frm.set_query('voucher_account', function() {
            return {
                filters: {
                    is_company_account: 1,
                    company: frm.doc.company
                }
            };
        });
    },

    onload: function(frm) {
        // Set default only for new vouchers
        if (frm.is_new() && !frm.doc.voucher_account) {
            frappe.db.get_value('Voucher Settings', 'Voucher Settings', 'default_bank_payment_account')
                .then(r => {
                    if (r && r.message && r.message.default_bank_payment_account) {
                        frm.set_value('voucher_account', r.message.default_bank_payment_account);
                    }
                });
        }
    },

    cost_center: function(frm) {
        // Auto-populate cost_center in all accounts child table rows
        if (frm.doc.cost_center && frm.doc.accounts) {
            frm.doc.accounts.forEach(function(row) {
                frappe.model.set_value(row.doctype, row.name, 'cost_center', frm.doc.cost_center);
            });
            frm.refresh_field('accounts');
        }
    }
});

// Handle accounts child table events
frappe.ui.form.on('Voucher Account', {
    accounts_add: function(frm, cdt, cdn) {
        // Auto-populate cost_center when new row is added
        if (frm.doc.cost_center) {
            frappe.model.set_value(cdt, cdn, 'cost_center', frm.doc.cost_center);
        }
    }
});