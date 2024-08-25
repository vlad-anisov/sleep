/** @odoo-module **/

import { RelationalModel } from "@web/model/relational_model/relational_model";
import { makeContext } from "@web/core/context";
import { getFieldsSpec } from "@web/model/relational_model/utils";
import { WarningDialog } from "@web/core/errors/error_dialogs";
import { patch } from "@web/core/utils/patch";

patch(RelationalModel.prototype, {
    async _onchange(
        config,
        { changes = {}, fieldNames = [], evalContext = config.context, onError }
    ) {
        const { fields, activeFields, resModel, resId } = config;
        let context = config.context;
        if (fieldNames.length === 1) {
            const fieldContext = config.activeFields[fieldNames[0]].context;
            context = makeContext([context, fieldContext], evalContext);
        }
        const spec = getFieldsSpec(activeFields, fields, evalContext, { withInvisible: true });
        const args = [resId ? [resId] : [], changes, fieldNames, spec];
        let response;
        try {
            response = await this.orm.call(resModel, "onchange", args, { context });
        } catch (e) {
            if (onError) {
                return onError(e);
            }
            throw e;
        }
        if (response.action){
            return this.action.doAction(response.action)
        }
        if (response.warning) {
            const { type, title, message, className, sticky } = response.warning;
            if (type === "dialog") {
                this.dialog.add(WarningDialog, { title, message });
            } else {
                this.notification.add(message, {
                    className,
                    sticky,
                    title,
                    type: "warning",
                });
            }
        }
        return response.value;
    }
})