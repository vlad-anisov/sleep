from odoo import models, fields


class PageAbout(models.Model):
    _name = "page.about"

    name = fields.Char(string="Name", default="About")

    def read(self, fields=None, load="_classic_read"):
        self.env["discuss.channel"].close_sleepy_chat()
        return super().read(fields, load)
