import configparser
import imaplib
import base64
import sys, os
import email
import re
from datetime import datetime
from Config.MySqlConnector import MySqlConnector

path = sys.path.append(os.path.join(os.path.dirname(__file__), '/'))

config = configparser.ConfigParser()
t = config.read('settings.ini')
t = config.read('/home/ayanda/PycharmProjects/flomail/Config/settings.ini')
sections = config.sections()

allowed_origin = config.get('DEFAULT', 'allowed_origin')
db_username = config.get('DEFAULT', 'db_username')
db_password = config.get('DEFAULT', 'db_password')
db_host = config.get('DEFAULT', 'host')
db_name = config.get('DEFAULT', 'db_name')
storage_folder = config.get('DEFAULT', 'storage_folder')

conf_sql = MySqlConnector(db_username, db_password, db_host, db_name)


class EmailServices:

    def get_storage_path(self):
        return storage_folder

    def get_allowed_origins(self):
        return allowed_origin

    def get_emailmessage_data(self, msg):

        plain_text_body = None
        has_attachment = 0
        attachments = {}
        attachment_name = []
        attachment_content = []

        msg_type = msg.get_content_maintype()

        if msg_type == 'multipart':

            for part in msg.get_payload():
                message_part_type = part.get_content_maintype()
                content_data_att = part.get('Content-Disposition')

                if message_part_type == "text" and content_data_att is None:
                    plain_text_body = part.get_payload(decode=True)

                if message_part_type == "image":
                    has_attachment = 1
                    file_name = part.get_filename()
                    file_name = file_name.replace(" ", "_")
                    if file_name not in attachment_name:
                        attachment_name.append(file_name)
                        attachment_content.append({file_name: part.get_payload(decode=True)})

                if message_part_type == 'multipart':
                    for part_two in part.get_payload():
                        message_part_two_type = part_two.get_content_maintype()

                        if message_part_two_type == "image":
                            has_attachment = 1
                            file_name = part_two.get_filename()
                            file_name = file_name.replace(" ", "_")
                            if file_name not in attachment_name:
                                attachment_name.append(file_name)
                                attachment_content.append({file_name: part_two.get_payload(decode=True)})

                        if message_part_two_type == 'text' and content_data_att is None:
                            plain_text_body = part_two.get_payload(decode=True)

                        elif message_part_two_type == 'multipart':
                            for part_three in part_two.get_payload():
                                message_part_three_type = part_three.get_content_maintype()

                                if message_part_three_type == 'text' and content_data_att is None:
                                    plain_text_body = part_three.get_payload(decode=True)

                if message_part_type != 'multipart' and content_data_att is not None:

                    has_attachment = 1
                    file_name = part.get_filename()
                    if file_name is not None:
                        file_name = file_name.replace(" ", "_")
                        if file_name not in attachment_name:
                            attachment_name.append(file_name)
                            attachment_content.append({file_name: part.get_payload(decode=True)})

            if plain_text_body is not None:

                if isinstance(plain_text_body, bytes):
                    try:
                        plain_text_body = plain_text_body.decode()
                    except:
                        plain_text_body = plain_text_body.decode('iso8859-1')

        else:

            plain_text_body = msg.get_payload(decode=True)
            if isinstance(plain_text_body, bytes):
                try:
                    plain_text_body = plain_text_body.decode()
                except:
                    plain_text_body = plain_text_body.decode('iso8859-1')

            # new line or break line is ignored on plain text
            plain_text_body = plain_text_body.replace('\r\n\r\n', '<br>')

        email_names = self.get_email_names(msg)

        return {"email_to": email_names[0], "email_from": email_names[1],
                "body": plain_text_body, "has_attachment": has_attachment,
                "attachment_name": attachment_name, "attachment_content": None,
                "attachments": attachments, "message_date": email_names[2], "subject": email_names[3], }

    def get_new_emails(self, email_user, email_pass):

        replies = {}
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            mail.login(email_user, email_pass)

            mail.select()
            type, data = mail.search(None, 'UNSEEN')
            mail_ids = data[0]
            id_list = mail_ids.split()

            for num in data[0].split():
                typ, data = mail.fetch(num, '(RFC822)')
                raw_email = data[0][1]
                # converts byte literal to string removing b''
                raw_email_string = raw_email.decode('utf-8')
                email_message = email.message_from_string(raw_email_string)
                email_message_data = self.get_emailmessage_data(email_message)
                contact_id = self.get_contact_id(email_message_data[0]['email_from'])
                self.save_new_email(email_message_data, contact_id)
                email_id = num.decode('utf-8')
                replies.update({int(email_id): email_message_data})
        except:
            pass

        return replies

    def save_new_email(self, email_message_data, contact_id):

        if len(email_message_data) != 0:

            email_from = email_message_data[0]['email_from']
            email_to = email_message_data[0]['to']
            subject = email_message_data[0]['subject']
            message_date = email_message_data[0]['received_date']

            account_id = self.get_account_id(email_message_data[0]['email_to'])

            if account_id is not None:
                insrt_qry = 'insert into inbox_email (account_id, contact_id, email_from, email_to, subject,' \
                            ' has_attachment, storage_path, message_date, status_id, created_at) ' \
                            'values(%s, %s, %s, %s, %s, %s, %s, %s, 3, current_timestamp )'

                insrt_qry_values = (account_id, contact_id, email_from, email_to, subject, 0, None, message_date)
                conf_sql.insert_data(insrt_qry, insrt_qry_values)

    def get_email_names(self, email_message):

        local_message_date = email_message['Date']
        # Header Details
        date_tuple = email.utils.parsedate_tz(email_message['Date'])
        if date_tuple:
            local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            local_message_date = "%s" % (str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
        email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
        email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))
        email_only = re.findall(r'[\w\.-]+@[\w\.-]+', email_from)
        email_to = re.findall(r'[\w\.-]+@[\w\.-]+', email_to)
        email_to = email_to[0]
        email_from = email_only[0]

        subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))

        return email_to, email_from, local_message_date, subject

    def get_contacts(self, ):

        qry = 'select id, firstname, lastname, title, mobile_number, email, home_address, work_address from contacts'
        contacts = conf_sql.select_data(qry, ())
        return contacts

    def get_contact_details(self, contact_id):

        qry = 'select id, firstname, lastname, title, mobile_number, email, home_address, work_address ' \
              'from contacts where id = %s'
        contact_detail = conf_sql.select_data(qry, (contact_id,))

        return contact_detail

    def get_accounts(self, ):

        qry = 'select id, from_address from accounts'
        accounts = conf_sql.select_data(qry, ())
        return accounts

    def get_account_details(self, account_id):

        qry = 'select id, name, from_address, smtp_username, smtp_port, smtp_password, imap_username, imap_port, imap_password ' \
              'from accounts where id = %s'
        account_detail = conf_sql.select_data(qry, (account_id,))
        return account_detail

    def get_contact_id(self, email):

        contact_id = False
        if email is not None:
            slct_qry = 'select id from contacts where email = %s'
            slct_qry_values = (email,)

            contact = conf_sql.select_data(slct_qry, slct_qry_values)

            if len(contact) != 0:
                contact_id = contact[0]['id']
            else:
                insrt_qry = 'insert into contacts (email) values (%s)'
                contact_id = conf_sql.insert_data(insrt_qry, slct_qry_values)

        return contact_id

    def send_new_email(self, email_to, account, message, subject, attachment=None, storage_path=None):

        new_email_id = False
        if email_to is None:
            return False

        contact_id = self.get_contact_id(email_to)

        if account is None:
            return False

        account_id = self.get_account_id(account)

        if account_id is not None:
            insrt_qry = 'INSERT INTO outbox_email (created_at, contact_id,account_id,email_body,status_id,' \
                        'email_from, email_to, subject, has_attachment, storage_path)' \
                        ' VALUES (current_timestamp, %s, %s,%s, %s,%s, %s, %s, %s, %s)'
            insrt_values = (contact_id, account_id, message, 1, account, email_to, subject, attachment, storage_path)

            new_email_id = conf_sql.insert_data(insrt_qry, insrt_values)

        return new_email_id

    def get_account_id(self, account):

        account_id = None

        qry = 'select id from accounts where from_address = %s'
        account_data = conf_sql.select_data(qry, (account,))

        if len(account_data) != 0:
            account_id = account_data[0]['id']

        return account_id

    def add_new_account(self, new_account_data):

        if len(new_account_data) != 0:
            name = new_account_data['name']

    def get_outbox(self, account):

        if account is not None:
            account_id = self.get_account_id(account)
            qry = 'select email_to, subject from outbox_email where account_id = %s'
            account_data = conf_sql.select_data(qry, (account_id,))

            return account_data
        return []
