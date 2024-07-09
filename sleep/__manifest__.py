{
    "name": "Sleep",
    "version": "17.0",
    "category": "",
    "summary": "Summary",
    "description": """ Description """,
    "depends": [
        "base",
        "muk_web_enterprise_theme",
        "queue_job",
        "knowledge",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/res_users_data.xml",
        "data/ir_actions_server_data.xml",
        "views/script_step_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sleep/static/src/js/sleep.js",
            # "sleep/static/src/xml/sleep.xml",
            "sleep/static/src/css/sleep.scss",
            "sleep/static/src/css/sleep.css",
        ],
    },
    "application": True,
}
