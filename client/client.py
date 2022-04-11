import pika
import uuid
import json
import curses

class URLRpcClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, url_source, url_dest):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        
        request = json.dumps({
            'url_source': url_source,
            'url_dest': url_dest
        }, ensure_ascii=False)

        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=request)
        
        while self.response is None:
            self.connection.process_data_events()
        
        response = json.loads(self.response)

        return response['length'], response['path']

stdscr = curses.initscr()
curses.noecho()

client = URLRpcClient()

def screen_loop():
    stdscr.clear()
    stdscr.refresh()

    t = '### WIKIPEDIA path finder app ###'
    stdscr.addstr(3, curses.COLS // 2 - len(t) // 2, t)

    curses.echo()
    
    stdscr.addstr(6, 10, 'Enter start url: ')
    
    l1 = stdscr.getstr(6, 27, 200)

    stdscr.addstr(8, 10, 'Enter finish url: ')

    l2 = stdscr.getstr(8, 28, 200)

    curses.noecho()

    t = 'Processing ...'
    stdscr.addstr(12, curses.COLS // 2 - len(t) // 2, t)

    stdscr.refresh()

    length, path = client.call(l1.decode('utf-8'), l2.decode('utf-8'))

    t = '! PATH FOUND !'
    stdscr.addstr(12, curses.COLS // 2 - len(t) // 2, t)

    t = f'Path length: {length}'
    stdscr.addstr(14, 4, t)

    t = ' -- > '.join(path)
    stdscr.addstr(16, curses.COLS // 2 - len(t) // 2, t)

    curses.echo()
    stdscr.addstr(20, 1, 'Continue? [y/n]: ')
    c = stdscr.getstr(20, 18, 1)

    if c == b'y':
        screen_loop()




def main():
    screen_loop()


if __name__ == '__main__':
    main()