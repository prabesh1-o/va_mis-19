/** @odoo-module **/
import {registry} from "@web/core/registry";
import {loadJS, loadCSS} from "@web/core/assets";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
var translation = require("web.translation");
var _t = translation._t;
import {useService} from "@web/core/utils/hooks";
const {Component, onWillStart, onMounted, useRef} = owl;
const {DateTime} = luxon;

export class NepaliDatePickerField extends Component {
  setup() {
    this.orm = useService("orm");
    onWillStart(async () => {
      await loadJS(
        "mis_nepali_date/static/src/js/lib/date_picker/nepali.datepicker.v4.0.4.min.js"
      );
      await loadCSS(
        "mis_nepali_date/static/src/js/lib/date_picker/nepali.datepicker.v4.0.4.min.css"
      );
    });

    onMounted(() => {
      self = this;
      $("#nepali_date").nepaliDatePicker({
        ndpYear: true,
        ndpMonth: true,
        ndpYearCount: 100,
        dateFormat: "DD/MM/YYYY",
        onChange: function() {
          let date_value = $("#nepali_date").val();
          self.props.update(date_value);
          const english_date = NepaliFunctions.BS2AD(date_value, "DD/MM/YYYY");
        },
      });
    });
  }
  get dateValue() {
    if (this.props.value) {
      return this.props.value;
    }
  }

  onBlur(e) {
    let date_value = $("#nepali_date").val();
    if (date_value === "") {
      self.props.update(date_value);
    }
    if (/[a-zA-Z]/.test(date_value)) {
      alert("Error: Date value contains alphabetic characters!");
    }
  }
}
NepaliDatePickerField.template = "mis_nepali_date.NepaliDatePickerField";
NepaliDatePickerField.props = {...standardFieldProps};
NepaliDatePickerField.displayName = "Nepali Date Field";
NepaliDatePickerField.supportedTypes = ["text"];
registry.category("fields").add("nepali_datepicker", NepaliDatePickerField);
