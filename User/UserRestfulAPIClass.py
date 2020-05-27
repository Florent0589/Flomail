from aiohttp import web
import json


class UserRestfulAPI:

    async def get_users(self, request):

        replies = await request.post()
        headers = {"Access-Control-Allow-Origin": "*"}

        return web.json_response(replies, text=None, body=None, status=200, reason=None,
                                 headers=headers, content_type='application/json', dumps=json.dumps)
