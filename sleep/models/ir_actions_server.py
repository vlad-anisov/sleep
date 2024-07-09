from odoo import models


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    def start_first_communication(self):
        pass