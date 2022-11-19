from aiosmtpd.controller import Controller

import datetime
import email.parser
import email.policy
import time

class Handler:
    async def handle_DATA(self, _server, _session, envelope):
        msg = email.parser.BytesParser(policy=email.policy.default).parsebytes(envelope.content)
        body = msg.get_body(preferencelist=('plain', 'html'))
        report = '\n'.join([
            datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
            f'from   : {envelope.mail_from}',
            f'to     : {envelope.rcpt_tos}',
            f'subject: {msg["Subject"]}',
            f'date   : {msg["Date"]}',
            '',
            str(body),
        ])
        print(report)
        print('-'*40)
        return '250 Message accepted for delivery'

controller = Controller(Handler(), hostname='', port=8025)
controller.start()
print('Server started.')
print(f'hostname: {repr(controller.hostname)}')
print(f'port    : {controller.port}')
print('-'*40)
while True: time.sleep(1)
controller.stop()
