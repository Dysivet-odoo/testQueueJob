# Copyright 2020 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

import logging

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

from .ir_logging import LOG_DEBUG

_logger = logging.getLogger(__name__)

ODOO = "__odoo__"
ODOO_REF = "ref2"
EXTERNAL = "__external__"
EXTERNAL_REF = "ref1"


class SyncLink(models.Model):

    _name = "sync.link"
    _description = "Resource Links"
    _order = "id desc"

    relation = fields.Char("Relation Name", required=True)
    system1 = fields.Char("System 1", required=True)
    # index system2 only to make search "Odoo links"
    system2 = fields.Char("System 2", required=True, index=True)
    ref1 = fields.Char("Ref 1", required=True)
    ref2 = fields.Char("Ref 2", required=True)
    date = fields.Datetime(
        string="Sync Date", default=fields.Datetime.now, required=True
    )
    model = fields.Char("Odoo Model", index=True)

    # delete_my_code_new
    bot_name = fields.Char("Bot name")

    def _auto_init(self):
        res = super(SyncLink, self)._auto_init()
        tools.create_unique_index(
            self._cr,
            "sync_link_refs_uniq_index",
            self._table,
            ["relation", "system1", "system2", "ref1", "ref2", "model"],
        )
        return res

    @api.model
    def _log(self, *args, **kwargs):
        log = self.env.context.get("log_function")
        if not log:
            return
        kwargs.setdefault("name", "sync.link")
        kwargs.setdefault("level", LOG_DEBUG)
        return log(*args, **kwargs)

    # External links
    @api.model
    def refs2vals(self, external_refs):
        '''references to vals for creating model'''
        # delete_my_code
        print('- sync.link refs2vals')
        print('external_refs =',external_refs)
        external_refs = sorted(
            external_refs.items(), key=lambda code_value: code_value[0]
        )
        system1, ref1 = external_refs[0]
        system2, ref2 = external_refs[1]
        vals = {
            "system1": system1,
            "system2": system2,
            "ref1": ref1,
            "ref2": ref2,
        }
        for k in ["ref1", "ref2"]:
            if vals[k] is None:
                continue
            if isinstance(vals[k], list):
                vals[k] = [str(i) for i in vals[k]]
            else:
                vals[k] = str(vals[k])
        print('vals =',vals)
        return vals

    # delete_my_code_new
    @api.model
    def _set_link_external(
            self, relation, external_refs, bot_name, sync_date=None, allow_many2many=False, model=None
    ):
        # delete_my_code
        print('- sync.link _set_link_external')
        print('relation =', relation)
        print('external_refs = ', external_refs)
        print('sync_date =', sync_date)
        print('allow_many2many =', allow_many2many)
        print('model =', model)

        vals = self.refs2vals(external_refs)
        # Check for existing records
        if allow_many2many:
            existing = self._search_links_external(relation, external_refs,bot_name)
        else:
            # check existing links for a part of external_refs
            refs1 = external_refs.copy()
            refs2 = external_refs.copy()
            for i, k in enumerate(external_refs.keys()):
                if i:
                    refs1[k] = None
                else:
                    refs2[k] = None
            print('refs1 =', refs1)
            print('refs2 =', refs2)
            existing = self._search_links_external(
                relation, refs1, bot_name
            ) or self._search_links_external(relation, refs2, bot_name)
            print('existing =', existing)
            if existing and not (
                    existing.ref1 == vals["ref1"] and existing.ref2 == vals["ref2"]
            ):
                raise ValidationError(
                    _("%s link already exists: %s=%s, %s=%s")
                    % (
                        relation,
                        existing.system1,
                        existing.ref1,
                        existing.system2,
                        existing.ref2,
                    )
                )

        if existing:
            self._log("{} Use existing link: {}".format(relation, vals))
            existing.update_links(sync_date)
            return existing

        if sync_date:
            vals["date"] = sync_date
        vals["relation"] = relation
        if model:
            vals["model"] = model
        vals['bot_name'] = bot_name
        self._log("Create link: %s" % vals)
        print('vals =', vals)
        return self.create(vals)

    # @api.model
    # def _set_link_external(
    #     self, relation, external_refs, sync_date=None, allow_many2many=False, model=None
    # ):
    #     # delete_my_code
    #     print('- sync.link _set_link_external')
    #     print('relation =',relation)
    #     print('external_refs = ',external_refs)
    #     print('sync_date =',sync_date)
    #     print('allow_many2many =',allow_many2many)
    #     print('model =',model)
    #
    #     vals = self.refs2vals(external_refs)
    #     # Check for existing records
    #     if allow_many2many:
    #         existing = self._search_links_external(relation, external_refs)
    #     else:
    #         # check existing links for a part of external_refs
    #         refs1 = external_refs.copy()
    #         refs2 = external_refs.copy()
    #         for i, k in enumerate(external_refs.keys()):
    #             if i:
    #                 refs1[k] = None
    #             else:
    #                 refs2[k] = None
    #         print('refs1 =',refs1)
    #         print('refs2 =',refs2)
    #         existing = self._search_links_external(
    #             relation, refs1
    #         ) or self._search_links_external(relation, refs2)
    #         print('existing =',existing)
    #         if existing and not (
    #             existing.ref1 == vals["ref1"] and existing.ref2 == vals["ref2"]
    #         ):
    #             raise ValidationError(
    #                 _("%s link already exists: %s=%s, %s=%s")
    #                 % (
    #                     relation,
    #                     existing.system1,
    #                     existing.ref1,
    #                     existing.system2,
    #                     existing.ref2,
    #                 )
    #             )
    #
    #     if existing:
    #         self._log("{} Use existing link: {}".format(relation, vals))
    #         existing.update_links(sync_date)
    #         return existing
    #
    #     if sync_date:
    #         vals["date"] = sync_date
    #     vals["relation"] = relation
    #     if model:
    #         vals["model"] = model
    #     self._log("Create link: %s" % vals)
    #     print('vals =',vals)
    #     return self.create(vals)

    # delete_my_code_new
    @api.model
    def _get_link_external(self, relation, external_refs, bot_name, model=None):
        links = self._search_links_external(relation, external_refs, bot_name, model=model)
        # if len(links) > 1:
        #     raise ValidationError(
        #         _(
        #             "get_link found multiple links. Use search_links for many2many relations"
        #         )
        #     )
        self._log("Get link: {} {} -> {}".format(relation, external_refs, links))
        return links

    # @api.model
    # def _get_link_external(self, relation, external_refs, model=None):
    #     links = self._search_links_external(relation, external_refs, model=model)
    #     # if len(links) > 1:
    #     #     raise ValidationError(
    #     #         _(
    #     #             "get_link found multiple links. Use search_links for many2many relations"
    #     #         )
    #     #     )
    #     self._log("Get link: {} {} -> {}".format(relation, external_refs, links))
    #     return links

    # delete_my_code_new
    @api.model
    def _search_links_external(
            self, relation, external_refs, bot_name, model=None, make_logs=False
    ):
        # delete_my_code
        print('- sync.link _search_links_external')
        print('relation =', relation)
        print('external_refs =', external_refs)
        print('model =', model)

        vals = self.refs2vals(external_refs)
        domain = [("relation", "=", relation)]
        if model:
            domain.append(("model", "=", model))
        for k, v in vals.items():
            if not v:
                continue
            operator = "in" if isinstance(v, list) else "="
            domain.append((k, operator, v))
        domain.append(('bot_name', '=', bot_name))
        print('domain =', domain)
        links = self.search(domain)
        if make_logs:
            self._log("Search links: {} -> {}".format(domain, links))
        return links

    # @api.model
    # def _search_links_external(
    #     self, relation, external_refs, model=None, make_logs=False
    # ):
    #     # delete_my_code
    #     print('- sync.link _search_links_external')
    #     print('relation =',relation)
    #     print('external_refs =',external_refs)
    #     print('model =',model)
    #
    #     vals = self.refs2vals(external_refs)
    #     domain = [("relation", "=", relation)]
    #     if model:
    #         domain.append(("model", "=", model))
    #     for k, v in vals.items():
    #         if not v:
    #             continue
    #         operator = "in" if isinstance(v, list) else "="
    #         domain.append((k, operator, v))
    #     print('domain =',domain)
    #     links = self.search(domain)
    #     if make_logs:
    #         self._log("Search links: {} -> {}".format(domain, links))
    #     return links

    def get(self, system):
        res = []
        for r in self:
            if r.system1 == system:
                res.append(r.ref1)
            elif r.system2 == system:
                res.append(r.ref2)
            else:
                raise ValueError(
                    _("Cannot find value for %s. Found: %s and %s")
                    % (system, r.system1, r.system2)
                )
        return res

    # Odoo links
    @property
    def odoo(self):
        res = set()
        model = self.env.context.get("sync_link_odoo_model")
        for r in self:
            if model is None:
                model = r.model
            elif model != r.model:
                raise ValidationError(
                    _("Mixing apples and oranges: %s and %s") % (model, r.model)
                )
            res.add(int(r[ODOO_REF]))
        return self.env[model].browse(res) if model else None

    @property
    def external(self):
        res = [getattr(r, EXTERNAL_REF) for r in self]
        if len(res) == 1:
            return res[0]
        return res

    # delete_my_code_new
    def _set_link_odoo(
        self, record, relation, ref,bot_name, sync_date=None, allow_many2many=False
    ):
        # delete_my_code
        print('- sync.link _set_link_odoo')
        refs = {ODOO: record.id, EXTERNAL: ref}
        print('refs =',refs)
        return self._set_link_external(
            relation, refs, bot_name, sync_date, allow_many2many, record._name
        )

    # def _set_link_odoo(
    #     self, record, relation, ref, sync_date=None, allow_many2many=False
    # ):
    #     # delete_my_code
    #     print('- sync.link _set_link_odoo')
    #     print('record =',record)
    #     print('relation =',relation)
    #     print('ref =',ref)
    #     refs = {ODOO: record.id, EXTERNAL: ref}
    #     return self._set_link_external(
    #         relation, refs, sync_date, allow_many2many, record._name
    #     )

    # delete_my_code_new
    def _get_link_odoo(self, relation, ref, bot_name, model=None):
        refs = {ODOO: None, EXTERNAL: ref}
        return self._get_link_external(relation, refs, bot_name, model=model)

    # def _get_link_odoo(self, relation, ref, model=None):
    #     refs = {ODOO: None, EXTERNAL: ref}
    #     return self._get_link_external(relation, refs, model=model)

    # delete_my_code_new
    def _search_links_odoo(self, records, relation, bot_name, refs=None):
        refs = {ODOO: records.ids, EXTERNAL: refs}
        print('refs =',refs)
        return self._search_links_external(
            relation, refs, bot_name, model=records._name, make_logs=True
        )

    # def _search_links_odoo(self, records, relation, refs=None):
    #     refs = {ODOO: records.ids, EXTERNAL: refs}
    #     return self._search_links_external(
    #         relation, refs, model=records._name, make_logs=True
    #     )

    # Common API

    # delete_my_code_new
    def _get_link(self, rel, ref_info, bot_name, model=None):
        if isinstance(ref_info, dict):
            # External link
            external_refs = ref_info
            return self._get_link_external(rel, external_refs, bot_name, model=model)
        else:
            # Odoo link
            ref = ref_info
            return self._get_link_odoo(rel, ref, bot_name, model=model)

    # def _get_link(self, rel, ref_info, bot_name, model=None):
    #     if isinstance(ref_info, dict):
    #         # External link
    #         external_refs = ref_info
    #         return self._get_link_external(rel, external_refs, model=model)
    #     else:
    #         # Odoo link
    #         ref = ref_info
    #         return self._get_link_odoo(rel, ref, model=model)

    @property
    def sync_date(self):
        return min(r.date for r in self)

    def update_links(self, sync_date=None):
        if not sync_date:
            sync_date = fields.Datetime.now()
        self.write({"date": sync_date})
        return self

    def __xor__(self, other):
        return (self | other) - (self & other)

    def unlink(self):
        self._log("Delete links: %s" % self)
        return super(SyncLink, self).unlink()

    @api.model
    def _get_eval_context(self):
        env = self.env

        # delete_my_code_new
        def set_link(
            rel, external_refs, bot_name, sync_date=None, allow_many2many=False, model=None
        ):
            # Works for external links only
            return env["sync.link"]._set_link_external(
                rel, external_refs, bot_name, sync_date, allow_many2many, model
            )
        # def set_link(
        #     rel, external_refs, sync_date=None, allow_many2many=False, model=None
        # ):
        #     # Works for external links only
        #     return env["sync.link"]._set_link_external(
        #         rel, external_refs, sync_date, allow_many2many, model
        #     )

        # delete_my_code_new
        def search_links(rel, external_refs, bot_name):
            # Works for external links only
            return env["sync.link"]._search_links_external(
                rel, external_refs, bot_name, make_logs=True
            )

        # def search_links(rel, external_refs):
        #     # Works for external links only
        #     return env["sync.link"]._search_links_external(
        #         rel, external_refs, make_logs=True
        #     )

        # delete_my_code_new
        def get_link(rel, ref_info, bot_name, model=None):
            return env["sync.link"]._get_link(rel, ref_info,bot_name, model=model)

        # def get_link(rel, ref_info, model=None):
        #     return env["sync.link"]._get_link(rel, ref_info, model=model)

        return {
            "set_link": set_link,
            "search_links": search_links,
            "get_link": get_link,
        }