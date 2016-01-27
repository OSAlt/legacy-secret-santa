#!/usr/bin/env python
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import smtplib
import datetime
import socket
import markdown
import pytz
import time
import yaml

from santa_lib.common import setup_logger
from santa_lib.person import Person

REQUIRED = ['SMTP_SERVER', 'SMTP_PORT', 'USERNAME', 'PASSWORD', 'TIMEZONE', 'PARTICIPANTS', 'FROM', 'SUBJECT']

global logger

def load_config(config_file):
    try:
        return yaml.load(open(config_file))
    except:
        logger.error("Error, %s was not found" % config_file)


def load_participants(config):
    """
        load all the participants from the configuration files and
        :return a list of Person objects.
    """

    people = []
    for person in config['PARTICIPANTS']:
        person = Person.construct_email_recipient(person)
        if person is not None:
            people.append(person)
    return people


def send_emails(config, people):
    server = None
    if config.get('USE_TLS'):
        server = smtplib.SMTP(config['SMTP_SERVER'], config['SMTP_PORT'])
        server.starttls()
    else:
        server = smtplib.SMTP_SSL(config['SMTP_SERVER'], config['SMTP_PORT'])
    # server = smtplib.SMTP(config['SMTP_SERVER'], config['SMTP_PORT'])
    server.login(config['USERNAME'], config['PASSWORD'])

    for person in people:
        msg = MIMEMultipart('alternative')

        zone = pytz.timezone(config['TIMEZONE'])
        now = zone.localize(datetime.datetime.now())
        date = now.strftime('%a, %d %b %Y %T %Z')  # Sun, 21 Dec 2008 06:25:23 +0000
        message_id = '<%s@%s>' % (str(time.time()) + str(random.random()), socket.gethostname())
        frm = config['FROM']
        to = person.email  # pair.giver.email
        subject = config['SUBJECT']
        template_file = config['TEMPLATE']
        file_handle = open(template_file, 'r')
        raw = file_handle.read()
        message = markdown.markdown(raw)

        body = message.format(
                date=date,
                message_id=message_id,
                frm=frm,
                to=to,
                subject=subject,
                person=person.name
        )
        if config['TEMPLATE_LOGO']:
            image_url = config['TEMPLATE_IMAGE']
            body += """<div align="center"><img alt="Bender Logo" src="{encoded}" /></div>""".format(
                    encoded=image_url)
        msg['Subject'] = subject
        msg['From'] = frm
        msg['To'] = to
        part1 = MIMEText(body, 'html')
        msg.attach(part1)

        server.sendmail(frm, [to], msg.as_string())
        logger.info("Email was sent to: {} <{}>.".format(person.name, person.email))

    server.quit()


def main():
    global logger
    parser = argparse.ArgumentParser(description='Santa Mass Email script')
    parser.add_argument('--send', action="store_true", dest="send", default=False, help="Enables Local Mode")
    parser.add_argument('--config', action="store", dest="config", type=str,
                        help="Override default config file (config.yml)and specify your own yaml config",
                        default='mass_mail.yml')

    args = parser.parse_args()

    logger = setup_logger(['console_logger', 'file_logger'], 'mass_mail.log')

    config_file = args.config
    send = args.send
    config = load_config(config_file)

    if config is None:
        return

    for key in REQUIRED:
        if key not in config.keys():
            raise Exception(
                    'Required parameter %s not in yaml config file!' % (key,))

    ## Load participants
    people = load_participants(config)

    ## send emails.
    if send:
        send_emails(config, people)


if __name__ == "__main__":
    main()
