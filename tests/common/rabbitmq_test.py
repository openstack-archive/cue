# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Authors: Davide Agnello <davide.agnello@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Copyright [2014] Hewlett-Packard Development Company, L.P.
# limitations under the License.

import argparse
import logging
import time

import pika


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('rabbitmq-client').setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", required=True,
                        help="Specify the RabbitMQ host")
    parser.add_argument("-P", "--port", required=True,
                        help="Specify the RabbitMQ port",
                        type=int)
    parser.add_argument("-u", "--user", required=True,
                        help="Specify the RabbitMQ username")
    parser.add_argument("-p", "--password", required=True,
                        help="Specify the RabbitMQ password")
    parser.add_argument("--ssl", dest="ssl", action="store_true",
                        help="Specify whether to use AMQPS protocol")
    args = parser.parse_args()

    host = args.host

    credentials = pika.PlainCredentials(args.user, args.password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        credentials=credentials, host=host, port=args.port, ssl=args.ssl))
    channel = connection.channel()
    channel.queue_declare(queue='hello')

    for count in range(1, 10, 1):
        print("Sending...")
        channel.basic_publish(exchange='', routing_key='hello',
                              body='Hello World!' + str(count))
        print(" [x] Sent 'Hello World!'" + str(count))
        print("Receiving...")
        method_frame, header_frame, body = channel.basic_get('hello')
        if method_frame:
            print(method_frame, header_frame, body)
            channel.basic_ack(method_frame.delivery_tag)
        else:
            print('No message returned')
        time.sleep(1)
    connection.close()
