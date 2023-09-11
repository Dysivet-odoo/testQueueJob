# Copyright 2021 Denis Mudarisov <https://github.com/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import werkzeug

from odoo import http
from odoo.http import request


class Website(http.Controller):
    def actions_server(self, path_or_xml_id_or_id, **post):
        # delete_my_code
        print(" - main actions_server")
        print("path_or_xml_id_or_id - ",path_or_xml_id_or_id)
        trigger = request.env["sync.trigger.webhook"]
        action = None
        print('trigger =',trigger)
        action = trigger.sudo().search(
            [
                ("website_path", "=", path_or_xml_id_or_id),
            ],
            limit=1,
        )
        print("action - ", action)
        # run it, return only if we got a Response object
        if action:
            print("action.state = ",action.state)
            if action.state == "code":
                print("action.action_server_id = ", action.action_server_id)
                action_res = action.action_server_id.run()
                if isinstance(action_res, werkzeug.wrappers.Response):
                    return action_res

        return request.redirect("/")
