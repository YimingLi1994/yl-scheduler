import socketserver
import settings
import json
import job_kill


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        self.request.settimeout(2)
        recvstr = self.request.recv(1024).strip().decode('ascii', 'ignore')
        print(recvstr)
        recvobj = json.loads(recvstr)
        retdict = job_kill.kill_job(recvobj['id'])
        retjson = json.dumps(retdict)
        self.request.sendall(retjson.encode('ascii'))


if __name__ == '__main__':
    HOST, PORT = settings.IP, settings.PORT
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()
