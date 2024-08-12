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
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/res_users_data.xml",
        "data/ir_actions_server_data.xml",
        "views/script_step_views.xml",
        "views/menuitems.xml",
        "views/page_sleepy_chat_views.xml",
        "views/page_about_views.xml",
        "views/article_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sleep/static/src/js/sleep.js",
            "sleep/static/src/xml/sleep.xml",
            "sleep/static/src/css/sleep.scss",
            "sleep/static/src/css/sleep.css",
        ],
    },
    "application": True,
}
