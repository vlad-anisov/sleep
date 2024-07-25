from odoo import models, fields, _

STEP_TYPES = [
    ("send_message", "Send message"),
    ("process_answer", "Process answer"),
    ("run_code", "Run code"),
]

STATE_TYPES = [
    ("pending", "Pending"),
    ("started", "Started"),
    ("wait_dependencies", "Wait Dependencies"),
    ("done", "Done"),
    ("failed", "Failed"),
]


class ScriptStep(models.Model):
    _name = "script.step"

    name = fields.Char(string="Name")
    script_id = fields.Many2one("script", string="Script")
    sequence = fields.Integer(string="Sequence")
    type = fields.Selection(STEP_TYPES, string="Type", required=True)
    state = fields.Selection(STATE_TYPES, string="State", required=True, default="pending")
    is_running = fields.Boolean(string="Running")
    next_step_ids = fields.Many2many(
        "script.step",
        "previous_step_next_step_rel",
        "previous_step_id",
        "next_step_id",
        string="Next steps"
    )
    message = fields.Html(string="Message")
    code = fields.Char(string="Code")

    def get_channel(self):
        sleepy_id = self.env.ref("sleep.sleepy")
        partner_ids = self.env.user.partner_id + sleepy_id.partner_id
        channel_id = self.env["discuss.channel"].search(
            [("channel_partner_ids", "=", partner_ids.ids)], order="id desc", limit=1)
        channel_id = channel_id.browse(3).with_user(sleepy_id)
        return channel_id

    def send_message(self, message):
        channel_id = self.get_channel()
        channel_id.message_post(
            body=message, message_type="comment", subtype_xmlid="mail.mt_comment", body_is_html=True
        )

    def run(self, **kwargs):
        self.ensure_one()
        self.is_running = True
        next_step_id = self.env["script.step"]

        if self.name:


        if self.type == "send_message":
            next_step_id = self.next_step_ids[:1]
            if next_step_id.type == "send_message":
                message = self.message
            else:
                buttons = ""
                for step_id in next_step_id.next_step_ids:
                    buttons += f"""
                        <button class="btn btn-primary" 
                        onclick="
                            let el = [...document.getElementsByTagName('textarea')].filter((el) => {{return el.className.indexOf('o-mail-Composer-input')}})[0];
                            el.focus();
                            el.value = '';
                            el.dispatchEvent(new window.KeyboardEvent('keydown', {{ key: 'Backspace' }}));
                            el.dispatchEvent(new window.KeyboardEvent('keyup', {{ key: 'Backspace' }}));
                            el.dispatchEvent(new window.InputEvent('input'));
                            el.dispatchEvent(new window.InputEvent('change'));
                            for (const char of '{step_id.name}') {{
                                el.value += char;
                                el.dispatchEvent(new window.KeyboardEvent('keydown', {{key: char}}));
                                el.dispatchEvent(new window.KeyboardEvent('keyup', {{key: char}}));
                                el.dispatchEvent(new window.InputEvent('input'));
                                el.dispatchEvent(new window.InputEvent('change'));
                            }};
                            setTimeout(function() {{
                                document.getElementsByClassName('o-mail-Composer-send')[0].click();
                            }}, 0);">
                            {step_id.name}
                        </button>
                    """
                message = f"{self.message}<br/>{buttons}"
            self.send_message(message)
        elif self.type == "process_answer":
            user_answer = kwargs.get("user_answer")
            if not user_answer:
                return
            next_step_id = self.next_step_ids.filtered(lambda s: s.name == user_answer)[:1]
            if user_answer and not next_step_id:
                self.send_message(_("Unknown answer"))
                return
        elif self.type == "run_code":
            pass

        self.is_running = False
        if next_step_id:
            next_step_id.run()
        else:
            self.env.user.script_id = False

