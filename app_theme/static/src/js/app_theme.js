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
        this.searchBarToggler = useSearchBarToggler();
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
