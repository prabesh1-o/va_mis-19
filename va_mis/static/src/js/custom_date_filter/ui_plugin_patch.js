/** @odoo-module **/

import GlobalFiltersUIPlugin from "@spreadsheet/global_filters/plugins/global_filters_ui_plugin";
import { patch } from "@web/core/utils/patch";
import { openCustomDateDialog, customDateRange } from "./custom_dialog";

patch(GlobalFiltersUIPlugin.prototype, "custom_date_filter_patch", {
    handle(cmd) {
        switch (cmd.type) {
            case "ADD_GLOBAL_FILTER":
                this.recordsDisplayName[cmd.filter.id] = cmd.filter.defaultValueDisplayNames;
                break;
            case "EDIT_GLOBAL_FILTER":
                if (
                    this.values[cmd.id] &&
                    this.values[cmd.id].rangeType !== cmd.filter.rangeType
                ) {
                    delete this.values[cmd.id];
                }
                break;
            case "SET_GLOBAL_FILTER_VALUE":
                this.recordsDisplayName[cmd.id] = cmd.displayNames;
                if (!customDateRange.isActive) {
                    if (cmd.value === "custom") openCustomDateDialog(this, cmd);
                }
                if (cmd.value != "custom" || customDateRange.isActive) {
                    this._setGlobalFilterValue(cmd.id, cmd.value);
                    customDateRange.isActive = false;
                }
                break;
            case "SET_MANY_GLOBAL_FILTER_VALUE":
                for (const filter of cmd.filters) {
                    if (filter.value !== undefined) {
                        this.dispatch("SET_GLOBAL_FILTER_VALUE", {
                            id: filter.filterId,
                            value: filter.value,
                        });
                    } else {
                        this.dispatch("CLEAR_GLOBAL_FILTER_VALUE", { id: filter.filterId });
                    }
                }
                break;
            case "REMOVE_GLOBAL_FILTER":
                delete this.recordsDisplayName[cmd.id];
                delete this.values[cmd.id];
                break;
            case "CLEAR_GLOBAL_FILTER_VALUE":
                customDateRange.isActive = false;
                this.recordsDisplayName[cmd.id] = [];
                this._clearGlobalFilterValue(cmd.id);
                break;
        }
    },
});
