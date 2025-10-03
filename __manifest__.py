{
    "name": "Hospital Management",
    "version": "1.0",
    "depends": ["base","mail"],
    "author": "Ton Nom",
    "category": "Healthcare",
    "description": "Gestion complète d'hôpital avec facturation simple",
    "installable": True,
    "application": True,
    "auto_install": False,
'data': [
    'security/security.xml',
    'security/ir.model.access.csv',

    'data/patient_sequence.xml',
    'data/doctor_sequence.xml',
'data/invoice_sequence.xml',

    'report/report.xml',
    'report/report_patient_card.xml',
'report/report_invoice_template.xml',


    'views/patient_views.xml',
    'views/doctor_views.xml',
    'views/invoice_views.xml',


],


}