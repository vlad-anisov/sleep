from odoo import models, fields, _
from email_validator import validate_email, EmailNotValidError
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

STATE_TYPES = [
    ("not_running", "Not running"),
    ("pre_processing", "Pre processing"),
    ("waiting", "Waiting"),
    ("post_processing", "Post processing"),
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
    code = fields.Text(string="Code")
    user_answer = fields.Char(string="User answer")
    user_answer_type = fields.Selection(USER_ANSWER_TYPES, string="User answer type", required=True, default="next_step_name")

    # def get_channel(self):
    #     sleepy_id = self.env.ref("sleep.sleepy")
        # channel_ids = self.env["discuss.channel"].search(
        #     [("channel_partner_ids", "=", [self.env.user.partner_id.id])]
        # )
        # channel_id = self.env["discuss.channel"].search(
        #     [("id", "in", channel_ids.ids), ("channel_partner_ids", "=", [sleepy_id.partner_id.id])]
        # ).filtered(lambda c: len(c.channel_partner_ids) == 2)[:1]
        # return self.env.user.sleepy_chat_id.with_user(sleepy_id)

    def send_message(self, message):
        chat_id = self.env.user.sleepy_chat_id.with_user(self.env.ref("sleep.sleepy"))
        self.message_id = chat_id.with_context(skip_notify_thread_by_web_push=True).message_post(
            body=message, message_type="comment", subtype_xmlid="mail.mt_comment", body_is_html=True
        )

    def run(self):
        if self.state in ("not_running", "done", "failed"):
            self.state = "pre_processing"

        if self.state == "pre_processing":
            self.pre_processing()
            if self.user_answer_type != "nothing":
                return

        if self.state == "waiting":
            self.waiting()

        if self.state == "post_processing":
            self.post_processing()

    def pre_processing(self):
        if self.user_answer_type == "next_step_name":
            buttons = ""
            for step_id in self.next_step_ids:
                buttons += f"""
                    <div class="row px-3">
                        <button class="btn btn-primary" 
                        onclick="
                            let el = document.getElementsByClassName('o-mail-Composer-input')[0];
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
                            el.dispatchEvent(new window.KeyboardEvent('keydown', {{ key: 'Enter' }}));
                            ">
                            {step_id.name}
                        </button>
                    </div>
                """
            message = f"{self.message}<br/>{buttons}"
        elif self.user_answer_type == "time":
            timepicker = f"""
                <div class="row px-3">
                    <input type="time" id="timepicker" value="00:00"/>
                </div>
            """
            button = f"""
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
                        let timepicker = document.getElementById('timepicker');
                        for (const char of timepicker.value) {{
                            el.value += char;
                            el.dispatchEvent(new window.KeyboardEvent('keydown', {{key: char}}));
                            el.dispatchEvent(new window.KeyboardEvent('keyup', {{key: char}}));
                            el.dispatchEvent(new window.InputEvent('input'));
                            el.dispatchEvent(new window.InputEvent('change'));
                        }};
                        setTimeout(function() {{
                            el.dispatchEvent(new window.KeyboardEvent('keydown', {{key: 'Enter', which: 13, bubbles: true}}));
                        }}, 0);">
                        Set
                    </button>
                </div>
            """
            message = f"{self.message}<br/>{timepicker}<br/>{button}"
        elif self.user_answer_type in ("email", "nothing"):
            message = self.message
        self.send_message(message)
        self.state = "waiting"

    def waiting(self):
        if self.user_answer:
            if self.user_answer_type == "next_step_name":
                if not self.next_step_ids.filtered(lambda s: s.name == self.user_answer):
                    self.send_message(_("Unknown answer"))
            elif self.user_answer_type == "email":
                try:
                    emailinfo = validate_email(self.user_answer, check_deliverability=False)
                    self.user_answer = emailinfo.normalized
                except EmailNotValidError as e:
                    self.send_message(_("Invalid email"))
            elif self.user_answer_type == "time":
                pass
        elif self.user_answer_type != "nothing":
            self.send_message(_("Please provide an answer"))
        self.state = "post_processing"
        self.message_id.body = self.message

    def post_processing(self):
        next_step_id = self.next_step_ids[:1]
        if self.code:
            safe_eval(self.code, {"self": self, "UserError": UserError}, mode="exec", nocopy=True)
        if self.user_answer_type == "next_step_name":
            next_step_id = self.next_step_ids.filtered(lambda s: s.name == self.user_answer)[:1]
        self.state = "done"
        next_step_id.run()
