/** @odoo-module */
import {_lt} from "@web/core/l10n/translation";
import {RELATIVE_DATE_RANGE_TYPES} from "@spreadsheet/helpers/constants";

RELATIVE_DATE_RANGE_TYPES.push({
  type: "custom",
  description: _lt("Custom Range"),
});

export const extendedDateRanges = RELATIVE_DATE_RANGE_TYPES;
