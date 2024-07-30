from odoo import models, fields


class PageAbout(models.Model):
    _name = "page.about"

    name = fields.Char(string="Name", default="About")
