from odoo import fields, models


class MisNoteTemplate(models.Model):
    _name = "mis.note.template"
    _description = "MIS Note Template"

    name = fields.Char(string="Template Name", required=True)
    note = fields.Html(string="Terms & Conditions", required=True)
