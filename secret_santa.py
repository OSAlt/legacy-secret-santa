#!/usr/bin/env python 
import yaml
import re
import random
import smtplib
import datetime
import pytz
import time
import socket
import sys
import getopt
import os
import markdown
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pair import Pair
from person import Person

help_message = '''
To use, fill out config.yml with your own participants.

You'll also need to specify your mail server settings.

For more information, see README.
'''

REQRD = (
    'SMTP_SERVER', 
    'SMTP_PORT', 
    'USERNAME', 
    'PASSWORD', 
    'TIMEZONE', 
    'PARTICIPANTS', 
    'FROM',
    'SUBJECT', 
    'MESSAGE',
)

HEADER = """Date: {date}
Content-Type: text/plain; charset="utf-8"
Message-Id: {message_id}
From: {frm}
To: {to}
Subject: {subject}
        
"""

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yml')

def parse_yaml(yaml_path=CONFIG_PATH):
    return yaml.load(open(yaml_path))    

def choose_receiver(giver, receivers):
    choice = random.choice(receivers)
    if choice.name in giver.invalid_matches or giver.name == choice.name:
        if len(receivers) is 1:
            raise Exception('Only one reliever left, try again')
        return choose_receiver(giver, receivers)
    else:
        return choice

def create_pairs(g, r):
    givers = g[:]
    receivers = r[:]
    pairs = []
    for giver in givers:
        try:
            receiver = choose_receiver(giver, receivers)
            receivers.remove(receiver)
            pairs.append(Pair(giver, receiver))
        except:
            return create_pairs(g, r)
    return pairs


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "shc", ["send", "help"])
        except getopt.error, msg:
            raise Usage(msg)
    
        # option processing
        send = False
        for option, value in opts:
            if option in ("-s", "--send"):
                send = True
            if option in ("-h", "--help"):
                raise Usage(help_message)
                
        config = parse_yaml()
        for key in REQRD:
            if key not in config.keys():
                raise Exception(
                    'Required parameter %s not in yaml config file!' % (key,))

        participants = config['PARTICIPANTS']
        if len(participants) < 2:
            raise Exception('Not enough participants specified.')
        
        givers = []
        for person in participants:
            name, email, amazon = re.match(r'([^<]*)<([^>]*)>.*(http.*)', person).groups()
            name = name.strip()
            invalid_matches = []
            person = Person(name, email, invalid_matches, amazon)
            givers.append(person)
        
        receivers = givers[:]
        pairs = create_pairs(givers, receivers)
        if not send:
            print """
Test pairings:
                
%s
                
To send out emails with new pairings,
call with the --send argument:

    $ python secret_santa.py --send
            
            """ % ("\n".join([str(p) for p in pairs]))
        
        if send:
            server = smtplib.SMTP_SSL(config['SMTP_SERVER'], config['SMTP_PORT'])
            # server.starttls()
            server.login(config['USERNAME'], config['PASSWORD'])
        for pair in pairs:
            msg = MIMEMultipart('alternative')

            zone = pytz.timezone(config['TIMEZONE'])
            now = zone.localize(datetime.datetime.now())
            date = now.strftime('%a, %d %b %Y %T %Z') # Sun, 21 Dec 2008 06:25:23 +0000
            message_id = '<%s@%s>' % (str(time.time())+str(random.random()), socket.gethostname())
            frm = config['FROM']
            to = pair.giver.email
            subject = config['SUBJECT'].format(santa=pair.giver.name, santee=pair.receiver.name)
            message = config['MESSAGE']
            if message == 'markdown':
                template_file = config['TEMPLATE']
                file_handle = open(template_file, 'r')
                raw = file_handle.read()
                message = markdown.markdown(raw)
                # if config['TEMPLATE_LOGO']:
                #     message += """<br><img src="cid:logo.png"><br>"""

            body = message.format(
                date=date, 
                message_id=message_id, 
                frm=frm, 
                to=to,
                subject=subject,
                santa=pair.giver.name,
                santee=pair.receiver.name,
                santee_email=pair.receiver.email,
                amazon=pair.receiver.amazon
            )
            if config['TEMPLATE_LOGO']:
                    image_url = config['TEMPLATE_IMAGE']
                    body += """<div align="center"><img alt="Bender Logo" src="{encoded}" /></div>""".format(encoded=image_url)
            msg['Subject'] = subject
            msg['From'] = frm
            msg['To'] = to
            if send:
                part1 = MIMEText(body, 'html')
                msg.attach(part1)

                server.sendmail(frm, [to], msg.as_string())
                print "Emailed %s <%s> which was paired up with %s" % (pair.giver.name, to, pair.receiver.name)


        if send:
            server.quit()
        
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())
