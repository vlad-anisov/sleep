from odoo import models, fields


class PageSleepyChat(models.Model):
    _name = "page.sleepy.chat"

    name = fields.Char(string="Name", default=" ")
