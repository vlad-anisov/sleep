/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class BooleanIconField extends Component {
    static template = "sleep.BooleanIconField";
    static props = {
        ...standardFieldProps,
        icon: { type: String, optional: true },
        no_active_icon: { type: String, optional: true},
        label: { type: String, optional: true },
    };
    static defaultProps = {
        icon: "fa-check-square-o",
    };

    update() {
        this.props.record.update({ [this.props.name]: !this.props.record.data[this.props.name] });
    }
}

export const booleanIconField = {
    component: BooleanIconField,
    displayName: _t("Boolean Icon"),
    supportedOptions: [
        {
            label: _t("Icon"),
            name: "icon",
            type: "string",
        },
        {
            label: _t("No active icon"),
            name: "no_active_icon",
            type: "string",
        },
    ],
    supportedTypes: ["boolean"],
    extractProps: ({ options, string }) => ({
        icon: options.icon,
        no_active_icon: options.no_active_icon,
        label: string,
    }),
};

registry.category("fields").add("boolean_sleep_icon", booleanIconField);
