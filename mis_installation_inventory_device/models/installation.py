from odoo import fields, models


class MisInstallation(models.Model):
    _inherit = "mis.device.installation"

    def _prepare_sim_values(self, line):
        stock_sim = line.stock_sim_id
        return {
            "sim_no": stock_sim.sim_no,
            "sim_carrier": stock_sim.sim_carrier,
            "data_plan": stock_sim.data_plan,
            "serial_no": stock_sim.serial_no,
            "puk1": stock_sim.puk1,
            "puk2": stock_sim.puk2,
            "pin1": stock_sim.pin1,
            "pin2": stock_sim.pin2,
        }

    def _prepare_device_values(self, line):
        vals = super()._prepare_device_values(line)
        sim_values = self._prepare_sim_values(line)
        sim = (
            self.env["mis.device.sim"].create(sim_values)
            if not line.stock_sim_id.sim_id
            else line.stock_sim_id.sim_id
        )
        vals.update(
            {
                "imei_no": line.stock_device_id.imei_no,
                "device_model_id": line.stock_device_id.device_model_id.id,
                "sim": sim.id,
            }
        )
        line.stock_sim_id.sim_id = sim
        return vals

    def _create_device_from_stock(self, line):
        if not line.stock_device_id.device_id:
            res = super()._create_device_from_stock(line)
            if not line.stock_device_id:
                line.stock_device_id = res.id
            line.stock_device_id.active = False
            line.stock_sim_id.active = False
            return res
        line.stock_sim_id.active = False
        line.stock_device_id.active = False
        device_vals = self._prepare_device_values(line)
        line.stock_device_id.device_id.write(device_vals)
        return line.stock_device_id.device_id


class MisInstallationLine(models.Model):
    _inherit = "mis.device.installation.line"

    stock_device_id = fields.Many2one("mis.inventory.device", string="Device",)
    stock_sim_id = fields.Many2one("mis.inventory.sim", string="Sim",)
