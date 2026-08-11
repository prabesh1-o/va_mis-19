{
    "name": "mis_attendance",
    "version": '19.0.1.0.0',
    "summary": """Integrating Biometric Device (Model: ZKteco uFace 202)
                     With HR Attendance (Face + Thumb) and MIS""",
    "description": """This module integrates Odoo with the
    biometric device(Model: ZKteco uFace 202),odoo16,odoo,hr,attendance""",
    "category": "Generic Modules/Human Resources",
    "author": "Vitruvian Analytica",
    "company": "Vitruvian Analytica",
    "website": "https://github.com/Dhakal-Silas/vamis",
    "depends": ["base_setup", "hr_attendance", "va_mis"],
    "data": [
        "security/ir.model.access.csv",
        "security/attendance_security.xml",
        "views/zk_machine_view.xml",
        "views/zk_machine_attendance_view.xml",
        "data/download_data.xml",
        "views/attendance_self_checkin_views.xml",
        "views/attendance_views.xml",
        "views/attendance_late_views.xml",
        
    ],
    "images": ["static/description/banner.png"],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True,
}
