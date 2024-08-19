from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    script_id = fields.Many2one("script", string="Script")
    sleepy_chat_id = fields.Many2one("discuss.channel", string="Sleepy Chat", required=True)
    ritual_id = fields.Many2one("ritual", string="Ritual", required=True)
