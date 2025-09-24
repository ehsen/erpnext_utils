frappe.ui.form.on('Cash Payment Voucher', {
    setup: function(frm) {
        // Restrict account field to cash accounts only
        frm.set_query('voucher_account', function() {
            return {
                filters: {
                    account_type: 'Cash',
                    is_group: 0,
                    company:frm.doc.company
                }
            };
        });
    },

    onload: function(frm) {
        // Set default only for new vouchers
        if (frm.is_new() && !frm.doc.account) {
            frappe.db.get_value('Voucher Settings', 'Voucher Settings', 'default_cash_payment_account')
                .then(r => {
                    if (r && r.message && r.message.default_cash_payment_account) {
                        frm.set_value('voucher_account', r.message.default_cash_payment_account);
                    }
                });
        }
    }
});
