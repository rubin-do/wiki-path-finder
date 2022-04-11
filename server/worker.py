import pika
from grabber import process_url
import json


def on_request(ch, method, props, body):

    req = json.loads(body)

    print(body)

    source_url = req['url_source']
    dest_url = req['url_dest']

    print(source_url, dest_url)

    path = process_url(source_url, dest_url)

    response = json.dumps({
        'length': len(path) - 1,
        'path': path
    }, indent=2) 

    print(response)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=response)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))

    channel = connection.channel()

    channel.queue_declare(queue='rpc_queue')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

    print(" [x] Awaiting RPC requests")
    channel.start_consuming()



if __name__ == '__main__':
    main()