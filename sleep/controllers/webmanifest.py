from odoo.addons.web.controllers.webmanifest import WebManifest as MainWebManifest
from odoo.addons.mail.controllers.webmanifest import WebManifest as MailWebManifest
from odoo import http
from odoo.http import request
import json
from odoo.tools import ustr
from odoo.tools import file_open


class WebManifest(MainWebManifest):

    @http.route('/web/manifest.webmanifest', type='http', auth='public', methods=['GET'])
    def webmanifest(self):
        web_app_name = request.env['ir.config_parameter'].sudo().get_param('web.web_app_name', 'Odoo')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url', 'Odoo')
        manifest = {
            'name': web_app_name,
            "short_name": web_app_name,
            "scope": base_url,
            'start_url': '/web',
            'id': '/web',
            'display': 'standalone',
            'background_color': '#141e36',
            'theme_color': '#141e36',
            'prefer_related_applications': False,
            "description": web_app_name,
            "dir": "ltr",
            "lang": "ru",
            "orientation": "portrait",
            "handle_links": "preferred",
            # "screenshots": [{
            #     "src": "/sleep/static/img/screenshot.png",
            #     "sizes": "367x794",
            #     "type": "image/png",
            # }],
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

    def _icon_path(self):
        return 'sleep/static/img/odoo-icon-192x192.png'

    def _get_service_worker_content(self):
        body = super(MailWebManifest, self)._get_service_worker_content()

        # Add notification support to the service worker if user but no public
        if request.env.user.has_group('base.group_user'):
            with file_open('mail/static/src/service_worker.js') as f:
                body += f.read()

        with file_open('sleep/static/src/js/service_worker.js') as f:
            body += f.read()

        return body

