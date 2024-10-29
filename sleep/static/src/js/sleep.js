/** @odoo-module **/

// Removes actions in header of chat dialog
import {threadActionsRegistry} from "@mail/core/common/thread_actions";

const allowedThreadActions = new Set(["close"]);

for (const [actionName] of threadActionsRegistry.getEntries()) {
    if (!allowedThreadActions.has(actionName)) {
        threadActionsRegistry.remove(actionName);
    }
}

threadActionsRegistry.addEventListener("UPDATE", ({detail: {operation, key}}) => {
    if (operation === "add" && !allowedThreadActions.has(key)) {
        threadActionsRegistry.remove(key);
    }
});


// Removes actions in inout of chat dialog
import {messageActionsRegistry} from "@mail/core/common/message_actions";

const allowedMessageActions = new Set([]);
for (const [actionName] of messageActionsRegistry.getEntries()) {
    if (!allowedMessageActions.has(actionName)) {
        messageActionsRegistry.remove(actionName);
    }
}

messageActionsRegistry.addEventListener("UPDATE", ({detail: {operation, key}}) => {
    if (operation === "add" && !allowedMessageActions.has(key)) {
        messageActionsRegistry.remove(key);
    }
});


// ???
import {ChatWindowService} from "@mail/core/common/chat_window_service";
import {onWillRender, onWillDestroy, onMounted} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

patch(ChatWindowService.prototype, {
    // setup(...args) {
    //     super.setup(...args);
    //
    // },

    async _onClose(chatWindow, options) {
        if (this.ui.isSmall && !this.store.discuss.isActive) {
            // If we are in mobile and discuss is not open, it means the
            // chat window was opened from the messaging menu. In that
            // case it should be re-opened to simulate it was always
            // there in the background.
            document.querySelector(".o_menu_systray i[aria-label='Messages']")?.click();
            // ensure messaging menu is opened before chat window is closed
            await Promise.resolve();
        }
        await super._onClose(chatWindow, options);
    },
});


//
import {FormRenderer} from "@web/views/form/form_renderer";
import {loadJS} from "@web/core/assets";
import {useService} from "@web/core/utils/hooks";
import {session} from '@web/session';

patch(FormRenderer.prototype, {
    setup() {
        super.setup();
        this.threadService = useService("mail.thread");
        onWillRender(() => {
            if (this.props.record.model.config.resModel == "chat") {
                // let thread = this.mailStore.Thread.get({model: "discuss.channel", id: session.chat_id});
                // if (!thread)
                let thread = this.mailStore.Thread.insert({model: "discuss.channel", id: session.chat_id});
                this.threadService.open(thread)
            }
        });
        onWillDestroy(() => {
            const thread = this.mailStore.Thread.get({model: "discuss.channel", id: session.chat_id});
            const chatWindow = this.threadService.store.discuss.chatWindows.find((c) => c.thread?.eq(thread));
            if (chatWindow) {
                this.threadService.chatWindowService.close(chatWindow);
            }
        });
        onMounted(() => {
           $(".o-mail-Message-textContent").css('z-index', 1);
        });
    }
});


import {Composer} from "@mail/core/common/composer";

patch(Composer.prototype, {
    async sendMessage() {
        await super.sendMessage();
        await this.threadService.loadAround2(this.props.composer.thread);
    },
});


import {ThreadService} from "@mail/core/common/thread_service";
import { prettifyMessageContent } from "@mail/utils/common/format";
import { loadEmoji } from "@web/core/emoji_picker/emoji_picker";
import { browser } from "@web/core/browser/browser";

patch(ThreadService.prototype, {
    async loadAround2(thread) {
        let {messages} = await this.rpc(this.getFetchRoute(thread), {
            ...this.getFetchParams(thread)
        });
        let originalMessages = JSON.parse(JSON.stringify(messages));
        for (const message of messages) {
            if (this.user.userId === message.author.user.id) {
                break;
            } else {
                const index = originalMessages.findIndex(function (el) {
                    return el.id === message.id;
                });
                if (index !== -1) {
                    originalMessages.splice(index, 1);
                }
            }
        }
        thread.messages = this.store.Message.insert(originalMessages.reverse(), {html: true});
        thread.loadNewer = false;
        thread.loadOlder = true;
        this._enrichMessagesWithTransient(thread);
    },
    async loadAround3(thread) {
        let {messages} = await this.rpc(this.getFetchRoute(thread), {
            ...this.getFetchParams(thread)
        });
        thread.messages = this.store.Message.insert(messages.reverse(), {html: true});
        thread.loadNewer = false;
        thread.loadOlder = true;
        this._enrichMessagesWithTransient(thread);
    },

    async post(
        thread,
        body,
        {
            attachments = [],
            isNote = false,
            parentId,
            mentionedChannels = [],
            mentionedPartners = [],
            cannedResponseIds,
        } = {}
    ) {
        let tmpMsg;
        const params = await this.getMessagePostParams({
            attachments,
            body,
            cannedResponseIds,
            isNote,
            mentionedChannels,
            mentionedPartners,
            thread,
        });
        const tmpId = this.messageService.getNextTemporaryId();
        params.context = { ...this.user.context, ...params.context, temporary_id: tmpId };
        if (parentId) {
            params.post_data.parent_id = parentId;
        }
        if (thread.type === "chatter") {
            params.thread_id = thread.id;
            params.thread_model = thread.model;
        } else {
            const tmpData = {
                id: tmpId,
                attachments: attachments,
                res_id: thread.id,
                model: "discuss.channel",
            };
            tmpData.author = this.store.self;
            if (parentId) {
                tmpData.parentMessage = this.store.Message.get(parentId);
            }
            const prettyContent = await prettifyMessageContent(
                body,
                this.messageService.getMentionsFromText(body, {
                    mentionedChannels,
                    mentionedPartners,
                })
            );
            const { emojis } = await loadEmoji();
            const recentEmojis = JSON.parse(
                browser.localStorage.getItem("web.emoji.frequent") || "{}"
            );
            const emojisInContent =
                prettyContent.match(/\p{Emoji_Presentation}|\p{Emoji}\uFE0F/gu) ?? [];
            for (const codepoints of emojisInContent) {
                if (emojis.some((emoji) => emoji.codepoints === codepoints)) {
                    recentEmojis[codepoints] ??= 0;
                    recentEmojis[codepoints]++;
                }
            }
            browser.localStorage.setItem("web.emoji.frequent", JSON.stringify(recentEmojis));
            tmpMsg = this.store.Message.insert(
                {
                    ...tmpData,
                    body: prettyContent,
                    res_id: thread.id,
                    model: thread.model,
                    temporary_id: tmpId,
                },
                { html: true }
            );
            // thread.messages.push(tmpMsg);
            thread.seen_message_id = tmpMsg.id;
        }
        const data = await this.rpc(this.getMessagePostRoute(thread), params);
        tmpMsg?.delete();
        if (!data) {
            return;
        }
        if (data.id in this.store.Message.records) {
            data.temporary_id = null;
        }
        const message = this.store.Message.insert(data, { html: true });
        thread.messages.add(message);
        if (!message.isEmpty && this.store.hasLinkPreviewFeature) {
            this.rpc("/mail/link_preview", { message_id: data.id }, { silent: true });
        }
        return message;
    }
});


import {SelectCreateDialog} from "@web/views/view_dialogs/select_create_dialog";

patch(SelectCreateDialog.prototype, {
    setup() {
        super.setup();
        this.props.multiSelect = false;
        this.props.noCreate = true;
        this.props.editable = "bottom";
    },
    get viewProps() {
        const type = "list";
        const props = {
            loadIrFilters: true,
            ...this.baseViewProps,
            context: this.props.context,
            domain: this.props.domain,
            dynamicFilters: this.props.dynamicFilters,
            resModel: this.props.resModel,
            searchViewId: this.props.searchViewId,
            type,
        };
        props.allowSelectors = this.props.multiSelect;
        return props;
    }
});


// Removes open wizard on fullscreen for mobile devices
import {Dialog} from "@web/core/dialog/dialog";

patch(Dialog.prototype, {
    get isFullscreen() {
        return this.props.fullscreen;
    }
});


// Adds delay before show messages
import {DiscussCoreCommon} from "@mail/discuss/core/common/discuss_core_common_service"

patch(DiscussCoreCommon.prototype, {
    setup() {
        this.messagingService.isReady.then((data) => {
            this.busService.addEventListener("notification", ({ detail: notifications }) => {
                // Do not handle new message notification if the channel was just left. This issue
                // occurs because the "discuss.channel/leave" and the "discuss.channel/new_message"
                // notifications come from the bus as a batch.
                const channelsLeft = new Set(
                    notifications
                        .filter(({ type }) => type === "discuss.channel/leave")
                        .map(({ payload }) => payload.id)
                );
                let i = 0
                for (const notif of notifications.filter(
                    ({ payload, type }) =>
                        type === "discuss.channel/new_message" && !channelsLeft.has(payload.id)
                )) {

                    let self = this;
                    if (["Ева", "Eva"].includes(notif.payload.message.author.name)) {
                        setTimeout(() => {
                            setTimeout(() => {
                                const {id} = notif.payload;
                                self.rpc(
                                    "/discuss/channel/notify_typing",
                                    {
                                        channel_id: id,
                                        is_typing: true,
                                        is_eva: true,
                                    },
                                    {silent: true}
                                ).then(() => {
                                    setTimeout(() => {
                                        self.rpc(
                                            "/discuss/channel/notify_typing",
                                            {
                                                channel_id: id,
                                                is_typing: false,
                                                is_eva: true,
                                            },
                                            {silent: true}
                                        ).then(() => {
                                            self._handleNotificationNewMessage(notif);
                                        })
                                    }, 3000);
                                });
                            }, 1000);

                        }, 6000 * i)

                        i++;
                    } else {
                        self._handleNotificationNewMessage(notif);
                    }


                }
            });
        });
    },


    // async _handleNotificationNewMessage(notif) {
    //     let self = this;
    //     if (notif.payload.message.author.name === "Eva") {
    //         const {id} = notif.payload;
    //         self.rpc(
    //             "/discuss/channel/notify_typing",
    //             {
    //                 channel_id: id,
    //                 is_typing: true,
    //                 is_eva: true,
    //             },
    //             {silent: true}
    //         ).then(async () => {
    //             setTimeout(() => {
    //                 self.rpc(
    //                     "/discuss/channel/notify_typing",
    //                     {
    //                         channel_id: id,
    //                         is_typing: false,
    //                         is_eva: true,
    //                     },
    //                     {silent: true}
    //                 ).then(async () => {
    //
    //                     // super._handleNotificationNewMessage(notif);
    //
    //
    //                     // const { id, message: messageData } = notif.payload;
    //                     // let thread = self.store.Thread.get({ model: "discuss.channel", id });
    //                     // if (!thread || !thread.type) {
    //                     //     thread = self.threadService.fetchChannel(id);
    //                     //     if (!thread) {
    //                     //         return;
    //                     //     }
    //                     // }
    //
    //
    //                     // self.threadService.loadAround3(thread);
    //                 })
    //             }, 2000);
    //         })
    //     } else {
    //         await super._handleNotificationNewMessage(notif);
    //     }
    // }
})


// Edit button for ritual
import {FormController} from "@web/views/form/form_controller";
import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";

export class RitualFormController extends FormController {
    setup() {
        this.props.preventEdit = true;
        super.setup();
    }

    async edit() {
        await this.model.root.save();
        await this.model.load();
        this.model.root.switchMode("edit")
    }

    async saveButtonClicked(params = {}) {
        let saved = await super.saveButtonClicked();
        if (saved) {
            if (!this.env.inDialog) {
                await this.model.load();
                await this.model.root.switchMode("readonly");
            } else {
                await this.model.actionService.doAction({type: "ir.actions.act_window_close"});
            }
        }
        return saved;
    }
}

RitualFormController.template = "sleep.RitualFormView";

export const ritualFormViewe = {
    ...formView,
    Controller: RitualFormController
};
registry.category("views").add("ritual_form", ritualFormViewe);


// Removes squashing of messages
import {Thread} from "@mail/core/common/thread";

patch(Thread.prototype, {
    isSquashed(msg, prevMsg) {
        return false;
    },
});


