{
    "name": "Library Book Checkout",
    "description": "Members can borrow books from the library.",
    "author": "Rahat",
    "license": "LGPL-3",
    "depends": ["library_member","library_app", "mail", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/checkout_mass_message_wizard_view.xml",
        "views/library_menu.xml",
        "views/checkout_view.xml",
        "views/checkout_kanban_view.xml",
        "data/stage_data.xml",
        "data/sequence_view.xml",
        "report/checkout_report.xml",
    ],
    "assets": {
        "web.assets_backend": {
            "library_checkout/static/src/css/checkout.css",
            "library_checkout/static/src/js/checkout.js",
        }
    }
}
