from aiosmtpd.controller import Controller

import time

class Handler:
    async def handle_DATA(self, _server, _session, envelope):
        print('Message from %s' % envelope.mail_from)
        print('Message for %s' % envelope.rcpt_tos)
        print('Message data:\n')
        for ln in envelope.content.decode('utf8', errors='replace').splitlines():
            print(f'> {ln}'.strip())
        print('-'*40)
        return '250 Message accepted for delivery'

controller = Controller(Handler(), hostname='', port=8025)
controller.start()
print('Server started.')
print(f'hostname: {repr(controller.hostname)}')
print(f'port    : {controller.port}')
while True: time.sleep(1)
controller.stop()
