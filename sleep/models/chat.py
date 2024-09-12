from odoo import models, fields


class Chat(models.Model):
    _name = "chat"

    name = fields.Char(string="Name", default=" ")
