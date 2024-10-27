from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for article_id in env["article"].search([]):
        article_id.first_color = article_id.color
