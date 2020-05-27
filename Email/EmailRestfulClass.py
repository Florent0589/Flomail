from aiohttp import web
from Email.EmailServiceClass import EmailServices
import json

email_service = EmailServices()


class EmailRestful:

    async def get_new_emails(self, request):

        replies = {}
        post = await request.post()
        email_user = post.get('email')
        email_pass = post.get('password')
        replies = email_service.get_new_emails(email_user, email_pass)

        return web.json_response(replies, text=None, body=None, status=200, reason=None,
                                 headers={"Access-Control-Allow-Origin": email_service.get_allowed_origins()},
                                 content_type='application/json', dumps=json.dumps)

    async def get_outbox(self, request):

        replies = {}
        post = await request.post()
        account = post.get('account')
        replies = email_service.get_outbox(account)

        return web.json_response(replies, text=None, body=None, status=200, reason=None,
                                 headers={"Access-Control-Allow-Origin": email_service.get_allowed_origins()},
                                 content_type='application/json', dumps=json.dumps)

    async def send_new_email(self, request):

        replies = {}
        post = await request.post()
        email_to = post.get('email_to')
        account = post.get('account')
        subject = post.get('subject')
        message = post.get('email_msg')

        replies = email_service.send_new_email(email_to, account, message, subject, None, None)

        return web.json_response(replies, text=None, body=None, status=200, reason=None,
                                 headers={"Access-Control-Allow-Origin": email_service.get_allowed_origins()},
                                content_type='application/json', dumps=json.dumps)

    async def add_new_account(self, request):

        body = await request.text()
        data = json.loads(body)

        return web.json_response(data)

    async def edit_profile(self, request):

        body = await request.text()
        data = json.loads(body)

        return web.json_response(data)

    async def edit_account(self, request):

        body = await request.text()
        data = json.loads(body)

        return web.json_response(data)

    async def delete_account(self, request):

        body = await request.text()
        data = json.loads(body)

        return web.json_response(data)

    async def get_accounts(self, request):

        replies = {}
        body = await request.text()
        replies = email_service.get_accounts()

        return web.json_response(replies, text=None, body=None, status=200, reason=None,
                                 headers={"Access-Control-Allow-Origin": email_service.get_allowed_origins()},
                                 content_type='application/json', dumps=json.dumps)

    async def get_account_details(self, request):

        replies = {}
        body = await request.post()
        account_id = body.get('account_id')
        replies = email_service.get_account_details(account_id)

        return web.json_response(replies, text=None, body=None, status=200, reason=None,
                                 headers={"Access-Control-Allow-Origin": email_service.get_allowed_origins()},
                                 content_type='application/json', dumps=json.dumps)

    async def get_contacts(self, request):

        replies = {}
        body = await request.text()
        replies = email_service.get_contacts()

        return web.json_response(replies, text=None, body=None, status=200, reason=None,
                                 headers={"Access-Control-Allow-Origin": email_service.get_allowed_origins()},
                                 content_type='application/json', dumps=json.dumps)

    async def get_contact_details(self, request):

        replies = {}
        body = await request.post()
        contact_id = body.get('user_id')
        replies = email_service.get_contact_details(contact_id)

        return web.json_response(replies, text=None, body=None, status=200, reason=None,
                                 headers={"Access-Control-Allow-Origin": email_service.get_allowed_origins()},
                                 content_type='application/json', dumps=json.dumps)
