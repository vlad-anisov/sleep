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
            'background_color': '#141e36',
            'theme_color': '#141e36',
            'prefer_related_applications': False,
            # "description": "Eva: Healthy sleep in 30 days",
            # "screenshots": [{
            #     "src": "/sleep/static/img/screenshot.png",
            #     "sizes": "367x794",
            #     "type": "image/png",
            # }],
        }
        icon_sizes = ['192x192', '512x512']
        manifest['icons'] = [{
            'src': '/sleep/static/img/odoo-icon-%s.webp' % size,
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

    def _icon_path(self):
        return 'sleep/static/img/odoo-icon-192x192.webp'

