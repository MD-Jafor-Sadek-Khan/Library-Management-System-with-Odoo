{
    "name": "Library Members",
    "description": "Manage members borrowing books.",
    "author": "Rahat",
    "license": "LGPL-3",
    "depends": ["base","library_app", "mail"],
    "application": False,
    "data": [
        "security/library_security.xml",
        "security/ir.model.access.csv",
        "views/book_view.xml",
        "views/member_view.xml",
        "views/library_menu.xml",
        "views/book_list_template.xml",
        "data/sequence_view.xml",

    ],
}
