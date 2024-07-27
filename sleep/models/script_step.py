from odoo import models, fields, _
from odoo.tools import html2plaintext, email_normalize
from email_validator import validate_email, EmailNotValidError

STATE_TYPES = [
    ("not_running", "Not running"),
    ("running", "Running"),
    ("waiting", "Waiting"),
    ("done", "Done"),
    ("failed", "Failed"),
]

USER_ANSWER_TYPES = [
    ("nothing", "Nothing"),
    ("next_step_name", "Next step name"),
    ("email", "Email"),
    ("time", "Time"),
]


class ScriptStep(models.Model):
    _name = "script.step"

    name = fields.Char(string="Name")
    script_id = fields.Many2one("script", string="Script")
    sequence = fields.Integer(string="Sequence")
    state = fields.Selection(STATE_TYPES, string="State", required=True, default="not_running")
    next_step_ids = fields.Many2many(
        "script.step",
        "previous_step_next_step_rel",
        "previous_step_id",
        "next_step_id",
        string="Next steps"
    )
    message = fields.Html(string="Message")
    message_id = fields.Many2one("mail.message", string="Message")
    code = fields.Char(string="Code")
    user_answer = fields.Char(string="User answer")
    user_answer_type = fields.Selection(USER_ANSWER_TYPES, string="User answer type", required=True, default="next_step_name")

    def get_channel(self):
        sleepy_id = self.env.ref("sleep.sleepy")
        partner_ids = self.env.user.partner_id + sleepy_id.partner_id
        channel_id = self.env["discuss.channel"].search(
            [("channel_partner_ids", "=", partner_ids.ids)], order="id desc", limit=1)
        channel_id = channel_id.browse(3).with_user(sleepy_id)
        return channel_id

    def send_message(self, message):
        channel_id = self.get_channel()
        self.message_id = channel_id.message_post(
            body=message, message_type="comment", subtype_xmlid="mail.mt_comment", body_is_html=True
        )

    def run(self):
        self.ensure_one()

        if self.state in ("not_running", "done", "failed"):
            self.state = "running"

        if self.state == "running":
            if self.user_answer_type == "next_step_name":
                buttons = ""
                for step_id in self.next_step_ids:
                    buttons += f"""
                        <div class="row px-3">
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
                        </div>
                    """
                message = f"{self.message}<br/>{buttons}"
            elif self.user_answer_type == "email":
                message = self.message
            elif self.user_answer_type == "time":
                buttons = ""
                for step_id in self.next_step_ids:
                    buttons += f"""
                        <div class="row px-3">
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
                        </div>
                    """
                message = f"{self.message}<br/>{buttons}"
            elif self.user_answer_type == "nothing":
                message = self.message
            else:
                message = self.message
            self.send_message(message)
            self.state = "waiting"
            if self.user_answer_type != "nothing":
                return

        if self.state == "waiting":
            if self.user_answer_type == "nothing":
                self.state = "done"
                self.next_step_ids[:1].run()
            elif self.user_answer:
                if self.user_answer_type == "next_step_name":
                    if not self.next_step_ids:
                        self.state = "done"
                    next_step_id = self.next_step_ids.filtered(lambda s: s.name == self.user_answer)[:1]
                    if next_step_id:
                        self.state = "done"
                        self.message_id.body = self.message
                        next_step_id.run()
                    else:
                        self.send_message(_("Unknown answer"))
                elif self.user_answer_type == "email":
                    try:
                        emailinfo = validate_email(self.user_answer, check_deliverability=False)
                        email = emailinfo.normalized
                        self.env.user.email = email
                        self.state = "done"
                        self.next_step_ids[:1].run()
                    except EmailNotValidError as e:
                        self.send_message(_("Invalid email"))
                elif self.user_answer_type == "time":
                    pass
            else:
                self.send_message(_("Please provide an answer"))
