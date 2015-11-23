from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from santa_lib.pair import Pair
from santa_lib.person import Person
import datetime
import markdown
import pytz
import random
import smtplib
import socket
import time
import yaml


class Santa(object):
    REQUIRED = ['SMTP_SERVER', 'SMTP_PORT', 'USERNAME', 'PASSWORD', 'TIMEZONE', 'PARTICIPANTS', 'FROM', 'SUBJECT',
                'TEMPLATE']

    TEMPLATE_MSG = """
Test pairings:

%s

To send out emails with new pairings,
call with the --send argument:

    $ python secret_santa.py --send

"""

    def __init__(self, logger, send, config_file):
        self.send_action = send
        self.logger = logger
        # load Config
        self.config = yaml.load(open(config_file))

        for key in self.REQUIRED:
            if key not in self.config.keys():
                raise Exception('Required parameter %s not in yaml config file!' % (key,))

    def choose_receiver(self, giver, receivers):
        """
          Attempts to match the giver to one of the potential receivers.
          :param giver:  the person giving a gift
          :param receivers:  potential gift receiver
        """
        choice = random.choice(receivers)
        if choice.name in giver.invalid_matches or giver.name == choice.name or choice.continent != giver.continent:
            if len(receivers) is 1:
                raise Exception('Only one receiver left, try again')
            return self.choose_receiver(giver, receivers)
        else:
            return choice

    def create_pairs(self, givers_list, receivers_list):
        """
        create a pair from a givers list to a receivers list
        :param receivers_list:
        :param givers_list:

        """
        givers = givers_list[:]
        receivers = receivers_list[:]
        pairs = []
        for giver in givers:
            try:
                receiver = self.choose_receiver(giver, receivers)
                receivers.remove(receiver)
                pairs.append(Pair(giver, receiver))
            except:
                return self.create_pairs(givers_list, receivers_list)
        return pairs

    def send_mail(self, pairs):
        # Connect to mail server
        server = smtplib.SMTP_SSL(self.config['SMTP_SERVER'], self.config['SMTP_PORT'])
        # server.starttls()
        server.login(self.config['USERNAME'], self.config['PASSWORD'])

        for pair in pairs:
            msg = MIMEMultipart('alternative')

            zone = pytz.timezone(self.config['TIMEZONE'])
            now = zone.localize(datetime.datetime.now())
            date = now.strftime('%a, %d %b %Y %T %Z')  # Sun, 21 Dec 2008 06:25:23 +0000
            message_id = '<%s@%s>' % (str(time.time()) + str(random.random()), socket.gethostname())
            frm = self.config['FROM']
            to = pair.giver.email
            subject = self.config['SUBJECT'].format(santa=pair.giver.name, santee=pair.receiver.name)
            template_file = self.config['TEMPLATE']
            file_handle = open(template_file, 'r')
            raw = file_handle.read()
            message = markdown.markdown(raw)
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
            if self.config['TEMPLATE_LOGO']:
                image_url = self.config['TEMPLATE_IMAGE']
                body += """<div align="center"><img alt="Bender Logo" src="{encoded}" /></div>""".format(
                    encoded=image_url)
            msg['Subject'] = subject
            msg['From'] = frm
            msg['To'] = to
            part1 = MIMEText(body, 'html')
            msg.attach(part1)
            server.sendmail(frm, [to], msg.as_string())
            self.logger.info("Emailed %s <%s> which was paired up with %s" % (pair.giver.name, to, pair.receiver.name))

        # disconnect from server
        server.quit()

    def process_data(self):
        """
            TODO: refactor this method.
        """
        participants = self.config['PARTICIPANTS']
        if len(participants) < 2:
            raise Exception('Not enough participants specified.')

        givers = []
        for person in participants:
            person = Person.construct_santa_recipient(person)
            givers.append(person)

        receivers = givers[:]
        pairs = self.create_pairs(givers, receivers)

        if self.send_action:
            self.send_mail(pairs)
        else:
            self.logger.info(self.TEMPLATE_MSG % ("\n".join([str(p) for p in pairs])))
            return


