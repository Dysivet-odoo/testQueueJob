# Copyright 2020-2022 Ivan Yelizariev <https://twitter.com/yelizariev>
# Copyright 2021 Denis Mudarisov <https://github.com/trojikman>
# License MIT (https://opensource.org/licenses/MIT).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SyncTriggerAutomation(models.Model):
    _name = "sync.trigger.automation"
    _inherit = ["sync.trigger.mixin", "sync.trigger.mixin.actions"]
    _description = "DB Trigger"
    _sync_handler = "handle_db"

    automation_id = fields.Many2one(
        "base.automation", delegate=True, required=True, ondelete="cascade"
    )

    def unlink(self):
        actions = self.mapped("action_server_id")
        automations = self.mapped("automation_id")
        super().unlink()
        automations.unlink()
        actions.unlink()
        return True

    def start(self, records):
        # delete_my_code
        print("- sync_trigger_automation start")
        print(self)
        print("records =", records)
        if self.active:
            if not self.sync_task_id:
                # workaround for old deployments
                _logger.warning(
                    "Task was deleted, but there is still base.automation record for it: %s"
                    % self.automation_id
                )
                return
            if self.is_record_mail_message(records):
                print(self.sync_task_id)
                self.sync_task_id.start(self, args=(records,), with_delay=True)

    def is_record_mail_message(self, records):
        # Перевірка чи є повідомлення з каналу де спілкується оператор і користувач телеграма
        if records._name == "mail.message":
            if records.model == 'mail.channel':
                channel = self.env['mail.channel'].search([('id', '=', records.res_id)])
                if channel and channel.channel_type == 'multi_livechat_telegram':
                    return True
            return False
        else:
            return True

    def get_code(self):
        return (
                """
    env["sync.trigger.automation"].browse(%s).sudo().start(records)
    """
                % self.id
        )

    @api.onchange("model_id")
    def onchange_model_id(self):
        self.model_name = self.model_id.model

    @api.onchange("trigger")
    def onchange_trigger(self):
        # delete_my_code
        print('- sync_trigger_automation onchange_trigger')
        print('self.trigger =', self.trigger)
        if self.trigger in ["on_create", "on_create_or_write", "on_unlink"]:
            print('trg_date_id =', self.trg_date_id)
            print('trg_date_range =', self.trg_date_range)
            print('trg_date_range_type =', self.trg_date_range_type)
            self.filter_pre_domain = (
                self.trg_date_id
            ) = self.trg_date_range = self.trg_date_range_type = False
            print(self.filter_pre_domain)
        elif self.trigger in ["on_write", "on_create_or_write"]:
            print('trg_date_range =', self.trg_date_range)
            print('trg_date_range_type =', self.self.trg_date_range_type)
            self.trg_date_id = self.trg_date_range = self.trg_date_range_type = False
            print(self.trg_date_id)
        elif self.trigger == "on_time":
            self.filter_pre_domain = False
