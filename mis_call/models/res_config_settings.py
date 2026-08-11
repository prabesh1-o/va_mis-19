import ast

from odoo import api, fields, models,Command


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    model_ids = fields.Many2many("ir.model", string="Model")

    @api.model
    def get_values(self):
        """
        Retrieves the configuration settings for the current user. This method
        fetches the 'mis.model_ids' parameter from the configuration and attempts
        to evaluate it as a list of model IDs.

        Returns:
            dict: A dictionary containing the model IDs under the key 'model_ids'.
        """
        res = super(ResConfigSettings, self).get_values()
        model_ids = (
            self.env["ir.config_parameter"].sudo().get_param("mis.model_ids", "[]")
        )
        try:
            model_ids = ast.literal_eval(model_ids)
        except Exception:
            model_ids = []
        res.update({"model_ids": [Command.link(id) for id in model_ids]})
        return res

    def set_values(self):
        """
        Saves the configuration settings for the current user. This method stores
        the 'model_ids' in the system configuration parameters to persist the setting.

        It updates the 'mis.model_ids' parameter with the current model IDs list.
        """
        super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "mis.model_ids", str(self.model_ids.ids),
        )

    def create_method_server_action(self):
        """
        Creates server actions for each model in the configuration parameter 'mis.model_ids'.
        For every model, if a server action named 'Assign call' does not already exist,
        it creates a new one. These actions are associated with the models and are used
        to trigger the call generator functionality.

        Returns:
            list: A list of created actions.
        """
        model_ids_str = (
            self.env["ir.config_parameter"].sudo().get_param("mis.model_ids", "[]")
        )
        created_actions = []
        model_ids = ast.literal_eval(model_ids_str)
        for model_id in model_ids:
            model = self.env["ir.model"].browse(model_id)
            if model.exists():
                existing_action = (
                    self.env["ir.actions.server"]
                    .sudo()
                    .search(
                        [("name", "=", "Assign call"), ("model_id", "=", model.id)],
                        limit=1,
                    )
                )
                if not existing_action:
                    action = (
                        self.env["ir.actions.server"]
                        .sudo()
                        .create(
                            {
                                "name": "Assign call",
                                "model_id": model.id,
                                "binding_model_id": model.id,
                                "binding_view_types": "list,form",
                                "state": "code",
                                "code": "action = env['res.config.settings'].action_open_call_generator()",
                            }
                        )
                    )
                    created_actions.append(action)
        return created_actions

    def action_open_call_generator(self):
        """
        Opens a new form view for the 'mis.call.generator' model. This action is typically
        triggered by the 'Assign call' server action. It provides the necessary context
        for generating calls based on the selected records.

        Returns:
            dict: A dictionary containing the action type, view mode, and other context
                  parameters necessary for the action to be executed.
        """
        active_model = self.env.context.get("active_model")
        model_id = (
            self.env["ir.model"].search([("model", "=", active_model)], limit=1).id
            if active_model
            else False
        )
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mis.call.generator",
            "target": "new",
            "context": {
                "default_active_ids": self.env.context.get("active_ids", []),
                "default_active_model_id": model_id,
                # Passing context to hide "View Calls" button in view opened from "Assign call" server action
                "hide_view_calls_btn": True,
            },
        }
