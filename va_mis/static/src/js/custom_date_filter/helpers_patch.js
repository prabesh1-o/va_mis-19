/** @odoo-module **/
import * as helpers from "@spreadsheet/global_filters/helpers";
import {patch} from "@web/core/utils/patch";
import {Domain} from "@web/core/domain";
import {serializeDate, serializeDateTime} from "@web/core/l10n/dates";
import {customDateRange} from "./custom_dialog";

const {DateTime} = luxon;

patch(helpers, "va_mis.helpers", {
  getRelativeDateDomain(now, offset, rangeType, fieldName, fieldType) {
    let endDate = now.minus({day: 1}).endOf("day");
    let startDate = endDate;
    switch (rangeType) {
      case "last_week": {
        const offsetParam = {day: 7 * offset};
        endDate = endDate.plus(offsetParam);
        startDate = now.minus({day: 7}).plus(offsetParam);
        break;
      }
      case "last_month": {
        const offsetParam = {day: 30 * offset};
        endDate = endDate.plus(offsetParam);
        startDate = now.minus({day: 30}).plus(offsetParam);
        break;
      }
      case "last_three_months": {
        const offsetParam = {day: 90 * offset};
        endDate = endDate.plus(offsetParam);
        startDate = now.minus({day: 90}).plus(offsetParam);
        break;
      }
      case "last_six_months": {
        const offsetParam = {day: 180 * offset};
        endDate = endDate.plus(offsetParam);
        startDate = now.minus({day: 180}).plus(offsetParam);
        break;
      }
      case "last_year": {
        const offsetParam = {day: 365 * offset};
        startDate = now.minus({day: 365}).plus(offsetParam);
        break;
      }
      case "last_three_years": {
        const offsetParam = {day: 3 * 365 * offset};
        endDate = endDate.plus(offsetParam);
        startDate = now.minus({day: 3 * 365}).plus(offsetParam);
        break;
      }
      case "custom": {
        const inputStartDate = DateTime.fromISO(customDateRange.startDate);
        const inputEndDate = DateTime.fromISO(customDateRange.endDate).endOf("day");
        const period = Math.floor(inputEndDate.diff(inputStartDate, "days").days);
        const offsetParam = {day: period * offset};
        endDate = inputEndDate.plus(offsetParam);
        startDate = inputEndDate.minus({day: period}).plus(offsetParam);
        break;
      }
      default:
        return undefined;
    }
    startDate = startDate.startOf("day");

    let leftBound, rightBound;
    if (fieldType === "date") {
      leftBound = serializeDate(startDate);
      rightBound = serializeDate(endDate);
    } else {
      leftBound = serializeDateTime(startDate);
      rightBound = serializeDateTime(endDate);
    }

    return new Domain([
      "&",
      [fieldName, ">=", leftBound],
      [fieldName, "<=", rightBound],
    ]);
  },
});
