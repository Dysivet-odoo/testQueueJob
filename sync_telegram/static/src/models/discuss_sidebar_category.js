/** @odoo-module **/

import { registerPatch } from "@mail/model/model_core";
import { one } from "@mail/model/model_field";
import { clear } from "@mail/model/model_field_command";

registerPatch({
    name: 'DiscussSidebarCategory',
    fields: {
        categoryItemsOrderedByLastAction: {
            compute() {
                if (this.discussAsMLChat_telegram) {
                    return this.categoryItems;
                }
                return this._super();
            },
        },
        discussAsMLChat_telegram: one('Discuss', {
            identifying: true,
            inverse: 'categoryMLChat_telegram',
        }),
        isServerOpen: {
            compute() {
                // there is no server state for non-users (guests)
                if (!this.messaging.currentUser) {
                    return clear();
                }
                if (!this.messaging.currentUser.res_users_settings_id) {
                    return clear();
                }
                if (this.discussAsMLChat_telegram) {
                    return this.messaging.currentUser.res_users_settings_id.is_discuss_sidebar_category_telegram_open;
                }
                return this._super();
            },
        },
        name: {
            compute() {
                if (this.discussAsMLChat_telegram) {
                    return this.env._t("telegram");
                }
                return this._super();
            },
        },
        hasAddCommand: {
            compute() {
                if (this.discussAsMLChat_telegram){
                    return true;
                }
                return this._super();
            },
        },
        orderedCategoryItems: {
            compute() {
                if (this.discussAsMLChat_telegram) {
                    return this.categoryItemsOrderedByLastAction;
                }
                return this._super();
            },
        },
        serverStateKey: {
            compute() {
                if (this.discussAsMLChat_telegram) {
                    return 'is_discuss_sidebar_category_telegram_open';
                }
                return this._super();
            },
        },
        supportedChannelTypes: {
            compute() {
                if (this.discussAsMLChat_telegram) {
                    return ['telegram'];
                }
                return this._super();
            },
        },
    },
});