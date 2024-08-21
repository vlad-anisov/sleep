/** @odoo-module **/
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {cookie} from "@web/core/browser/cookie"
import {patch} from "@web/core/utils/patch";
import {browser} from "@web/core/browser/browser";
import {useDebounced} from "@web/core/utils/timing";
import {SearchBarToggler} from "@web/search/search_bar/search_bar_toggler";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {useEffect, useState} from "@odoo/owl";

export function useSearchBarToggler() {
    const ui = useService("ui");

    let isToggled = false;
    const state = useState({
        isSmall: ui.isSmall,
        showSearchBar: true,
    });
    const updateState = () => {
        state.isSmall = ui.isSmall;
        state.showSearchBar = true;
    };
    updateState();

    function toggleSearchBar() {
        isToggled = !isToggled;
        updateState();
    }

    const onResize = useDebounced(updateState, 200);
    useEffect(
        () => {
            browser.addEventListener("resize", onResize);
            return () => browser.removeEventListener("resize", onResize);
        },
        () => []
    );

    return {
        state,
        component: SearchBarToggler,
        get props() {
            return {
                isSmall: state.isSmall,
                showSearchBar: state.showSearchBar,
                toggleSearchBar,
            };
        },
    };
}


patch(KanbanController.prototype, {
    setup(attributes) {
        super.setup(...arguments);
        // this.searchBarToggler = useSearchBarToggler();
    }
})


// Remove unnecessary menu items
const userMenuRegistry = registry.category("user_menuitems");
userMenuRegistry.remove("documentation");
userMenuRegistry.remove("support");
userMenuRegistry.remove("shortcuts");
userMenuRegistry.remove("separator");
userMenuRegistry.remove("odoo_account");
userMenuRegistry.remove("log_out");
userMenuRegistry.remove("profile");
userMenuRegistry.remove("color_scheme.switch");
userMenuRegistry.remove("web.user_menu");
userMenuRegistry.remove("web_mobile.switch");


//
const systrayRegistry = registry.category("systray")
systrayRegistry.remove("burger_menu")
systrayRegistry.remove("mail.activity_menu")
systrayRegistry.remove("mail.messaging_menu")


//
import { NavBar } from '@web/webclient/navbar/navbar';

// patch(Navbar.prototype, {
//     get showCashMoveButton() {
//         const { cashier } = this.pos;
//         return super.showCashMoveButton && (!cashier || cashier.role == "manager");
//     },
//     get showCloseSessionButton() {
//         return (
//             !this.pos.config.module_pos_hr ||
//             (this.pos.get_cashier().role === "manager" && this.pos.get_cashier().user_id) ||
//             this.pos.get_cashier_user_id() === this.pos.user.id
//         );
//     },
//     get showBackendButton() {
//         return (
//             !this.pos.config.module_pos_hr ||
//             (this.pos.get_cashier().role === "manager" && this.pos.get_cashier().user_id) ||
//             this.pos.get_cashier_user_id() === this.pos.user.id
//         );
//     },
//     async showLoginScreen() {
//         this.pos.reset_cashier();
//         await this.pos.showTempScreen("LoginScreen");
//     },
// });

// Auto dark/light theme
if (window.matchMedia) {
    var match = window.matchMedia('(prefers-color-scheme: dark)')
    if (!cookie.get("color_scheme")) {
        cookie.set("color_scheme", match.matches ? "dark" : "light");
        window.location.reload();
    }
    match.addEventListener('change', () => {
        cookie.set("color_scheme", match.matches ? "dark" : "light");
        window.location.reload();
    })
}

import { ControlPanel } from "@web/search/control_panel/control_panel";
patch(ControlPanel.prototype, {
    onScrollThrottled(){
        return
    }
})




import { ListRenderer } from "@web/views/list/list_renderer";

patch(ListRenderer.prototype, {
    get displayRowCreates() {
        return this.canCreate;
    }
})




//
// import { getActiveActions, archParseBoolean } from "@web/views/utils";
// patch(getActiveActions.prototype, function (rootNode) {
//     return {
//         type: "view",
//         edit: archParseBoolean(rootNode.getAttribute("edit"), true),
//         create: archParseBoolean(rootNode.getAttribute("create"), true),
//         delete: archParseBoolean(rootNode.getAttribute("delete"), true),
//         duplicate: archParseBoolean(rootNode.getAttribute("duplicate"), true),
//         link: archParseBoolean(rootNode.getAttribute("link"), true),
//         unlink: archParseBoolean(rootNode.getAttribute("unlink"), true),
//     };
// })
