import os
import sys
import smtplib
import mimetypes

from warnings import warn

from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import server_config

def __make_attachment(path, mime_type):
    main, sub = mime_type.split('/', 1)
    with open(path, 'r' if main == 'text' else 'rb') as f:
        if main == 'text':
            return MIMEText(f.read(), _subtype = sub)
        elif main == 'image':
            return MIMEImage(f.read(), _subtype = sub)
        elif main == 'audio':
            return MIMEAudio(f.read(), _subtype = sub)
        else:
            attachment = MIMEBase(main, sub)
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            return attachment

def send(**kwargs):
    server_name = kwargs.get('server_name')
    to = kwargs.get('to')
    subject = kwargs.get('subject', None)
    message = kwargs.get('message', None)
    attach = kwargs.get('files', list())

    server = server_config(server_name)

    if len(attach) > 0:
        output = MIMEMultipart()

        text = MIMEText(message, 'plain')
        output.attach(text)

        for info in attach:
            fname = info['path']
            if not os.path.isfile(fname):
                warn('Tried to attach a file {} that is not a file!'.format(fname))
                continue

            full_type, encoding = mimetypes.guess_type(fname)
            if full_type is None or encoding is not None:
                full_type = 'application/octet-stream'

            attachment = __make_attachment(fname, full_type)
            attachment.add_header('Content-Disposition', 'attachment', filename=info['name'])
            output.attach(attachment)

    else:
        output = MIMEText(text, 'plain')

    output['Subject'] = subject
    output['To'] = ', '.join(to)
    output['From'] = '{} <{}>'.format(server['name'], server['email'])
    output['X-Mailer'] = 'MailScape Python (Beta) - https://github.com/CorgiDude/MailScape'
    output.preamble = 'This message was created by eScape in multi-part MIME format.\nUse a MIME 1.0-compliant reader, like MailScape, to read it.\n\n'

    smtp = smtplib.SMTP(server_name)
    if 'tls' in server and server['tls'] == True:
        smtp.starttls()
    if 'user' in server:
        smtp.login(server['user'], server['password'])
    smtp.send_message(output)
    smtp.quit()

