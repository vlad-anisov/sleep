/** @odoo-module **/

import {loadJS} from "@web/core/assets";
import {registry} from "@web/core/registry";

import {Component, onPatched, onWillStart, useEffect, useRef, onMounted} from "@odoo/owl";

export class PlotlyChartWidget extends Component {
    static template = "web_widget_plotly_chart.PlotlyChartWidgetField";
    setup() {
        this.divRef = useRef("plotly");

        onWillStart(async () => {
            await loadJS(
                "/web_widget_plotly_chart/static/src/lib/plotly/plotly-2.18.2.min.js"
            );
            this.updatePlotly();
        });

        onPatched(() => {
            this.updatePlotly();
        });

        useEffect(() => {
            this.updatePlotly();
        });

        onMounted(() => {
            this.updatePlotly();
        });
    }
    updatePlotly(value) {
        // if (bdom && bdom.parentEl) {
        //     const value_html = $(bdom.parentEl);
        //     const div = value_html.find(".plotly-graph-div").first().outerHTML || "";
        //     const script = value_html.find("script").first().textContent || "";
        //
        //     if (this.divRef.el) {
        //         this.divRef.el.innerHTML = div;
        //         new Function(script)();
        //     }
        // }
    }
}

export const TimePickerField = {
    component: PlotlyChartWidget,
    supportedTypes: ["char", "text"],
};

registry.category("fields").add("plotly_chart", TimePickerField);
