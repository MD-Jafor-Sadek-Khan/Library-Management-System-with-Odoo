{
    "name": "Library Management",
    "summary": "Manage library catalog and book lending.",
    "author": "Rahat",
    "license": "LGPL-3",

    "version": "1.0.0",
    "category": "Services/Library",
    "depends": ["base"],
    "data": [
        "security/library_security.xml",
        "security/ir.model.access.csv",
        "views/book_view.xml",
        "views/library_menu.xml",
        "views/book_category_view.xml",
        "views/book_list_template.xml",
        "reports/library_book_report.xml",
        "reports/library_publisher_report.xml",
        ],
    "demo": [
        "data/res.partner.csv",
        "data/library.book.csv",
        "data/book_demo.xml",
    ],
    "application": True,
}
