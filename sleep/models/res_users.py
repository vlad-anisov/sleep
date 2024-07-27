from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    script_ids = fields.One2many("script", "user_id", string="Scripts")
