from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for step_id in env["script.step"].search([]):
        step_id.type = step_id.user_answer_type
