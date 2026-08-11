from odoo import fields, models


class MisDeviceSim(models.Model):
    _inherit = "mis.device.sim"

    device_history_ids = fields.One2many(
        "mis.sim.device.history", "sim_id", string="Device History"
    )
    device_history_count = fields.Integer(compute="_compute_device_history_count")

    def _compute_device_history_count(self):
        for sim in self:
            sim.device_history_count = len(sim.device_history_ids)

    def return_action_to_open(self):
        """
        To open action while clicking in the button box,
        gets external id from context
        """
        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        if xml_id:
            res = self.env["ir.actions.act_window"]._for_xml_id(xml_id)
            res.update(
                context=dict(self.env.context, default_sim_id=self.id, group_by=False),
                domain=[("sim_id", "=", self.id)],
            )
            return res
        return False
