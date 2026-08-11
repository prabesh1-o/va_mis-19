/** @odoo-module **/

const {_t} = require("web.core");
const Dialog = require("web.Dialog");

export const customDateRange = {
  startDate: null,
  endDate: null,
  isActive: false,
};

/**
 * Opens a dialog to select custom date range
 * @param {Object} self - The context (this) for dispatching commands
 * @param {Object} cmd - The command object containing filter id and value
 */
export function openCustomDateDialog(self, cmd) {
  const dialog = new Dialog(this, {
    title: _t("Select Date Range"),
    size: "medium",
    buttons: [
      {
        text: _t("Cancel"),
        classes: "btn-secondary",
        close: true,
        click: function() {
          dialog.close();
        },
      },
      {
        text: _t("Apply"),
        classes: "btn-primary",
        click: function() {
          const startDateStr = dialog.el.querySelector("#start_date").value;
          const endDateStr = dialog.el.querySelector("#end_date").value;

          if (!startDateStr || !endDateStr) {
            alert("Please select both start and end dates.");
            return;
          }
          customDateRange.startDate = startDateStr;
          customDateRange.endDate = endDateStr;
          customDateRange.isActive = true;
          dialog.close();

          try {
            self.dispatch("SET_GLOBAL_FILTER_VALUE", {id: cmd.id, value: cmd.value});
          } catch (error) {
            console.error("Error refreshing dashboard:", error);
          }
        },
      },
    ],
    $content: $(`
                <div class="p-4">
                    <div class="form-group row mb-3">
                        <label for="start_date" class="col-sm-3 col-form-label">Start Date</label>
                        <div class="col-sm-9">
                            <input type="date" class="form-control" id="start_date" required>
                        </div>
                    </div>
                    <div class="form-group row">
                        <label for="end_date" class="col-sm-3 col-form-label">End Date</label>
                        <div class="col-sm-9">
                            <input type="date" class="form-control" id="end_date" required>
                        </div>
                    </div>
                </div>
            `),
  });

  dialog.open();
}
