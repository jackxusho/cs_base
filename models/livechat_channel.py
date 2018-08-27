# coding=utf-8

import logging
import random


from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class LivechatChannel(models.Model):

    _inherit = 'im_livechat.channel'

    group_ids = fields.Many2many('cs.group', string=u'客服组')


    @api.model
    def get_mail_channel(self, livechat_channel_id, anonymous_name):
        channel = self.sudo().browse(livechat_channel_id)
        if channel.group_ids:
            agents = []
            for group in channel.group_ids:
                agents += group.agent_ids
            users = [agent.user_id for agent in agents]
        else:
            users = self.sudo().browse(livechat_channel_id).get_available_users()

        if len(users) == 0:
            return False
        # choose the res.users operator and get its partner id
        user = random.choice(users)
        operator_partner_id = user.partner_id.id
        # partner to add to the mail.channel
        channel_partner_to_add = [(4, operator_partner_id)]
        if self.env.uid:  # if the user if logged (portal user), he can be identify
            channel_partner_to_add.append((4, self.env.user.partner_id.id))
        # create the session, and add the link with the given channel
        mail_channel = self.env["mail.channel"].with_context(mail_create_nosubscribe=False).sudo().create({
            'channel_partner_ids': channel_partner_to_add,
            'livechat_channel_id': livechat_channel_id,
            'anonymous_name': anonymous_name,
            'channel_type': 'livechat',
            'name': ', '.join([anonymous_name, user.name]),
            'public': 'private',
            'email_send': False,
        })
        return mail_channel.sudo().with_context(im_livechat_operator_partner_id=operator_partner_id).channel_info()[0]
