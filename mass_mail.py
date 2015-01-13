#!/usr/bin/env python
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import re
import smtplib
import datetime
import socket
import markdown
import pytz
import time
import yaml
from person import Person


REQRD = (
    'SMTP_SERVER',
    'SMTP_PORT',
    'USERNAME',
    'PASSWORD',
    'TIMEZONE',
    'PARTICIPANTS',
    'FROM',
    'SUBJECT',
)


def load_config(config_file):
    return yaml.load(open(config_file))


def load_participants(config):
    """
        load all the participants from the configuration files and
        :return a list of Person objects.
    """

    people = []
    for person in config['PARTICIPANTS']:
        name, email = re.match(r'([^<]*)<([^>]*)>', person).groups()
        name = name.strip()
        invalid_matches = []
        person = Person(name, email, invalid_matches, None)
        if person is not None:
            people.append(person)

    return people


def send_emails(config, people):
    server = smtplib.SMTP_SSL(config['SMTP_SERVER'], config['SMTP_PORT'])
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
        print "Email was sent to: {name} <{email}>.".format(name=person.name, email=person.email)

    server.quit()


def main():
    parser = argparse.ArgumentParser(description='Santa Mass Email script')
    parser.add_argument('--send', action="store_true", dest="send", default=False, help="Enables Local Mode")
    parser.add_argument('--config', action="store", dest="config", type=str,
                        help="Override default config file (config.yml)and specify your own yaml config",
                        default='config.yml')

    args = parser.parse_args()
    config_file = args.config
    send = args.send
    config = load_config(config_file)
    for key in REQRD:
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
