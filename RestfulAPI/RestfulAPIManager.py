from aiohttp import web
from Email.EmailRestfulClass import EmailRestful
from User.UserRestfulAPIClass import UserRestfulAPI
from Config.MySqlConnector import MySqlConnector


def Main():
    app = web.Application()
    rst = EmailRestful()
    usr = UserRestfulAPI()


    # EMAILS
    app.add_routes(
        [web.post("/send_new_email", rst.send_new_email),
         web.post("/get_new_emails", rst.get_new_emails),
         web.post("/get_outbox", rst.get_outbox),
         web.post("/add_new_account", rst.add_new_account), ]
    )

    # USERS
    app.add_routes(
        [web.post("/get_users", usr.get_users), ])

    # ACCOUNTS
    app.add_routes(
        [web.post("/edit_profile", rst.edit_profile),
         web.post("/edit_account", rst.edit_account),
         web.post("/delete_account", rst.delete_account),
         web.post("/get_accounts", rst.get_accounts),
         web.post("/get_account_details", rst.get_account_details), ])

    # CONTACTS
    app.add_routes(
        [web.post("/get_contact_details", rst.get_contact_details),
         web.post("/get_contacts", rst.get_contacts), ])

    web.run_app(app, host='127.0.0.1', port=8009)


if __name__ == '__main__':
    Main()
