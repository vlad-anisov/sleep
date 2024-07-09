from odoo import models, fields


class MailMessage(models.Model):
    _inherit = "mail.message"

    body = fields.Html(sanitize=False)
