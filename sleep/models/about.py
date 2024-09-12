from odoo import models, fields


class About(models.Model):
    _name = "about"

    name = fields.Char(string="Name", default="About")
