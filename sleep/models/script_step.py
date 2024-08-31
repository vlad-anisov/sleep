from odoo import models, fields, _
from email_validator import validate_email, EmailNotValidError
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
from datetime import timedelta

STATE_TYPES = [
    ("not_running", "Not running"),
    ("pre_processing", "Pre processing"),
    ("waiting", "Waiting"),
    ("post_processing", "Post processing"),
    ("done", "Done"),
    ("failed", "Failed"),
]
TYPES = [
    ("nothing", "Nothing"),
    ("next_step_name", "Next step name"),
    ("email", "Email"),
    ("time", "Time"),
    ("article", "Article"),
    ("mood", "Mood"),
    ("ritual_line", "Ritual line"),
    ("ritual", "Ritual"),
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
    type = fields.Selection(TYPES, string="Type", required=True, default="next_step_name")

    def send_message(self, message):
        if not message and self.type == "nothing":
            return
        chat_id = self.env.user.sleepy_chat_id.with_user(self.env.ref("sleep.sleepy"))
        skip_notify_thread_by_web_push = self.env.context.get("skip_notify_thread_by_web_push", True)
        message_id = chat_id.with_context(skip_notify_thread_by_web_push=skip_notify_thread_by_web_push).message_post(
            body=message, message_type="comment", subtype_xmlid="mail.mt_comment", body_is_html=True
        )
        self.message_id = message_id

    def run(self):
        if self.state in ("not_running", "done", "failed"):
            self.state = "pre_processing"

        if self.state == "pre_processing":
            self.pre_processing()
            if self.type != "nothing":
                return

        if self.state == "waiting":
            self.waiting()

        if self.state == "post_processing":
            self.post_processing()

    def pre_processing(self):
        if self.type == "next_step_name":
            buttons = ""
            for step_id in self.next_step_ids:
                buttons += f"""
                    <div class="row px-3">
                        <button class="btn btn-primary" style="border-radius: 20px;"
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
                    </div><br/>"""
            message = f"{self.message}<br/>{buttons}"[:-5]
        elif self.type == "mood":
            buttons = ""
            for mood in ("👍", "👌", "👎"):
                buttons += f"""
                    <div class="row px-3">
                        <button class="btn btn-primary" style="border-radius: 20px;"
                        onclick="
                            let el = document.getElementsByClassName('o-mail-Composer-input')[0];
                            el.focus();
                            el.value = '';
                            el.dispatchEvent(new window.KeyboardEvent('keydown', {{ key: 'Backspace' }}));
                            el.dispatchEvent(new window.KeyboardEvent('keyup', {{ key: 'Backspace' }}));
                            el.dispatchEvent(new window.InputEvent('input'));
                            el.dispatchEvent(new window.InputEvent('change'));
                            for (const char of '{mood}') {{
                                el.value += char;
                                el.dispatchEvent(new window.KeyboardEvent('keydown', {{key: char}}));
                                el.dispatchEvent(new window.KeyboardEvent('keyup', {{key: char}}));
                                el.dispatchEvent(new window.InputEvent('input'));
                                el.dispatchEvent(new window.InputEvent('change'));
                            }};
                            el.dispatchEvent(new window.KeyboardEvent('keydown', {{ key: 'Enter' }}));
                            ">
                            {mood}
                        </button>
                    </div><br/>"""
            message = f"{self.message}<br/>{buttons}"[:-5]
        elif self.type == "time":
            timepicker = f"""
                <div class="row px-3">
                    <input type="time" id="timepicker" value="23:15" onfocus="(e) => e.currentTarget.showPicker()"/>
                </div>
            """
            button = f"""
                <div class="row px-3">
                    <button class="btn btn-primary" style="border-radius: 20px;"
                    onclick="
                        let el = document.getElementsByClassName('o-mail-Composer-input')[0];
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
                        el.dispatchEvent(new window.KeyboardEvent('keydown', {{ key: 'Enter' }}));
                        ">
                        Set
                    </button>
                </div>
            """
            message = f"{self.message}<br/>{timepicker}<br/>{button}"
        elif self.type == "article":
            # Adds access to new article for user
            self.script_id.sudo().article_id.user_ids += self.env.user
            # Adds next script to current script
            self.script_id.next_script_id = self.script_id.main_script_id.next_script_id
            # Adds link to read the article
            button = f"""
                <div class="row px-3">
                    <a class="btn btn-primary" style="border-radius: 20px;" href="/web#id={self.script_id.article_id.id}&model=article&view_type=form">Read</a>
                </div>
            """
            message = f"{self.message}<br/>{button}"
        elif self.type == "ritual":
            button = f"""
                <div class="row px-3">
                    <a class="btn btn-primary" style="border-radius: 20px;" href="/web#id={self.env.user.ritual_id.id}&model=ritual&view_type=form">Go</a>
                </div>
            """
            message = f"{self.message}<br/>{button}"
        elif self.type == "ritual_line":
            new_ritual_line_id = self.script_id.sudo().ritual_line_id
            ritual_line_id = self.env["ritual.line"].search(
                [("name", "=", new_ritual_line_id.name), ("is_base", "=", True), ("create_uid", "=", self.env.user.id)]
            )
            if not ritual_line_id:
                ritual_line_id = new_ritual_line_id.copy()
            if self.name == "Давай 👌":
                self.env.user.ritual_id.line_ids += ritual_line_id
            self.type = "nothing"
            message = self.message
        else:
            message = self.message
        self.send_message(message)
        self.state = "waiting"

    def waiting(self):
        if self.user_answer:
            if self.type == "next_step_name":
                if not self.next_step_ids.filtered(lambda s: s.name == self.user_answer):
                    self.send_message("Unknown answer")
            elif self.type == "email":
                try:
                    emailinfo = validate_email(self.user_answer, check_deliverability=False)
                    self.user_answer = emailinfo.normalized
                    self.env.user.email = self.user_answer
                except EmailNotValidError as e:
                    self.send_message("Invalid email")
            elif self.type == "time":
                hour, minute = self.user_answer.split(":")
                time = (fields.Datetime.now().replace(hour=int(hour), minute=int(minute)) - timedelta(hours=1))
                self.user_answer = time.strftime("%H:%M")
                self.env.user.time = self.user_answer
                self.script_id.next_script_id = self.script_id.main_script_id.next_script_id
        elif self.type != "nothing":
            self.send_message("Please provide an answer")
        self.state = "post_processing"
        if self.type not in ("article", "ritual"):
            self.message_id.body = self.message

    def post_processing(self):
        next_step_id = self.next_step_ids[:1]
        if self.code:
            safe_eval(self.code, {"self": self, "UserError": UserError}, mode="exec", nocopy=True)
        if self.type == "next_step_name":
            next_step_id = self.next_step_ids.filtered(lambda s: s.name == self.user_answer)[:1]
        self.state = "done"
        if next_step_id:
            next_step_id.run()
        elif self.env.user.test_script_count < 1 and self.script_id.next_script_id:
            self.env.user.test_script_count += 1
            self.script_id.next_script_id.run()
        else:
            self.env.user.test_script_count = 0
