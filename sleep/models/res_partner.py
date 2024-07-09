from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _compute_im_status(self):
        super()._compute_im_status()
        sleepy_id = self.env.ref("sleep.sleepy").partner_id
        if sleepy_id in self:
            sleepy_id.im_status = "bot"
