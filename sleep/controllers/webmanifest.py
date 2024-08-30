from odoo.addons.web.controllers.webmanifest import WebManifest as MainWebManifest
from odoo import http
from odoo.http import request
import json
from odoo.tools import ustr


class WebManifest(MainWebManifest):

    @http.route('/web/manifest.webmanifest', type='http', auth='public', methods=['GET'])
    def webmanifest(self):
        web_app_name = request.env['ir.config_parameter'].sudo().get_param('web.web_app_name', 'Odoo')
        manifest = {
            'name': web_app_name,
            'scope': '/web',
            'start_url': '/web',
            'display': 'standalone',
            'background_color': '#01a2ff',
            'theme_color': '#01a2ff',
            'prefer_related_applications': False,
        }
        icon_sizes = ['192x192', '512x512']
        manifest['icons'] = [{
            'src': '/sleep/static/img/odoo-icon-%s.png' % size,
            'sizes': size,
            'type': 'image/png',
            "purpose": "maskable",
        } for size in icon_sizes]
        manifest['shortcuts'] = self._get_shortcuts()
        body = json.dumps(manifest, default=ustr)
        response = request.make_response(body, [
            ('Content-Type', 'application/manifest+json'),
        ])
        return response

