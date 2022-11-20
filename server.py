from aiosmtpd.controller import Controller

try:
    import boto3
except:
    boto3 = None

import datetime
import email.parser
import email.policy
import os
import socket
import time
import traceback

if boto3:
    try:
        sns_client = boto3.client(
            'sns',
            region_name='us-west-2',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        )
        sns_topic_arn = os.environ['AWS_SNS_TOPIC_ARN']
    except:
        sns_client = None
        traceback.print_exc()
        print()

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
        if sns_client:
            try:
                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Message=report,
                    Subject=f'smtp-docker {socket.gethostname()}',
                )
            except Exception as e:
                print(e)
                raise Exception('Something went wrong.')
        return '250 Message accepted for delivery'

controller = Controller(Handler(), hostname='', port=8025)
controller.start()
print('Server started.')
print(f'hostname: {repr(controller.hostname)}')
print(f'port    : {controller.port}')
print('-'*40)
while True: time.sleep(1)
controller.stop()
