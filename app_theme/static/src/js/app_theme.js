/** @odoo-module **/
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {cookie} from "@web/core/browser/cookie"
import {patch} from "@web/core/utils/patch";
import {browser} from "@web/core/browser/browser";
import {useDebounced} from "@web/core/utils/timing";
import {SearchBarToggler} from "@web/search/search_bar/search_bar_toggler";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {onMounted, useEffect, useState, xml} from "@odoo/owl";

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
let { DropdownItem } = NavBar.components;

DropdownItem.props = {
    ...DropdownItem.props,
    web_icon: { optional: true },
};
patch(DropdownItem.prototype, {
    setup() {
        onMounted(() => {
            window.dispatchEvent(new Event("locationchange"));
        });
    }
})


// Auto dark/light theme
// if (window.matchMedia) {
//     var match = window.matchMedia('(prefers-color-scheme: dark)')
//     if (!cookie.get("color_scheme")) {
//         cookie.set("color_scheme", match.matches ? "dark" : "light");
//         window.location.reload();
//     }
//     match.addEventListener('change', () => {
//         cookie.set("color_scheme", match.matches ? "dark" : "light");
//         window.location.reload();
//     })
// }
if (window.matchMedia) {
    var match = window.matchMedia('(prefers-color-scheme: dark)')
    if (!cookie.get("color_scheme")) {
        cookie.set("color_scheme", "dark");
        window.location.reload();
    }
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
});


// import { ActionContainer } from "@web/webclient/actions/action_container";
// ActionContainer.template = xml`
//     <t t-name="web.ActionContainer">
//       <div class="o_action_manager container">
//         <t t-if="info.Component" t-component="info.Component" className="'o_action'" t-props="info.componentProps" t-key="info.id"/>
//       </div>
//     </t>`;


(() => {
    let oldPushState = history.pushState;
    history.pushState = function pushState() {
        let ret = oldPushState.apply(this, arguments);
        window.dispatchEvent(new Event('pushstate'));
        window.dispatchEvent(new Event('locationchange'));
        return ret;
    };

    let oldReplaceState = history.replaceState;
    history.replaceState = function replaceState() {
        let ret = oldReplaceState.apply(this, arguments);
        window.dispatchEvent(new Event('replacestate'));
        window.dispatchEvent(new Event('locationchange'));
        return ret;
    };

    window.addEventListener('popstate', () => {
        window.dispatchEvent(new Event('locationchange'));
    });
})();

window.addEventListener('locationchange', function () {
    $("a[role='menuitem']").removeClass('primary')
    if (window.location.href){
        let url = window.location.href.split('model=')[1]
        if (url) {
            url = url.split('&')[0].replaceAll(".", "_")
            $(`a[data-menu-xmlid*='${url}']`).addClass('primary')
        } else {
            $("a[role='menuitem']").first().addClass('primary')
        }
    } else {
        $("a[role='menuitem']").first().addClass('primary')
    }
});