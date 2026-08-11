/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";

export function useVASettings() {
    const title = useService("title");

    onWillStart(() => {
        console.log("VA MIS initialized safely");
        if (title) {
            title.setParts({ zopenerp: "VA MIS" });
        }
    });
}