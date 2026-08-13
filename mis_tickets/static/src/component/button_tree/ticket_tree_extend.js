/** @odoo-module **/

import {ListController} from "@web/views/list/list_controller";
import {registry} from "@web/core/registry";
import {listView} from "@web/views/list/list_view";
import {useService} from "@web/core/utils/hooks";

const {onWillStart, useState} = owl;

export class TicketListController extends ListController {
  setup() {
    super.setup();
    this.orm = useService("orm");
    this.state = useState({
      showButton: false,
    });

    onWillStart(async () => {
      try {
        const ticketMenus = await this.orm.searchRead(
          "mis.ticket.menu",
          [
            ["is_completed", "=", true],
            ["active", "=", false],
          ],
          ["id"]
        );
        const activeId = this.env.searchModel.context.active_id;
        const showButtonBasedOnTickets = ticketMenus[0].id !== activeId;

        const isAdmin = await this.orm.call("res.users", "has_group", [
          "base.group_system",
        ]);

        this.state.showButton = showButtonBasedOnTickets && isAdmin;
      } catch (error) {
        console.error("Error fetching ticket menus:", error);
      }
    });
  }

  async OnHideClick() {
    const activeId = this.env.searchModel.context.active_id;
    await this.orm.call("mis.ticket", "hide_completed_tickets", [], {
      context: {active_id: activeId},
    });
    await this.model.load();
    this.render();
  }
}

registry.category("views").add("button_in_list", {
  ...listView,
  Controller: TicketListController,
  buttonTemplate: "button_ticket.ListView.Buttons",
});
