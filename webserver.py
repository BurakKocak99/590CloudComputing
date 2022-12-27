from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import LoadBalancer as lb



hostName = "localhost"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):

    loadbalancer = lb.Load_Balancer()
    client_count = 0
    max_client_count = 0
    server_start_date_time = time.time()
    Avarage_RTT_time = 0
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

    def do_POST(self):

        self.send_response(200)
        if (time.time() - self.server_start_date_time > 10):
            MyServer.client_count = 0
            MyServer.server_start_date_time = time.time()


        MyServer.max_client_count = MyServer.max_client_count + 1
        MyServer.client_count = MyServer.client_count + 1


        content_length = int(self.headers['Content-Length'])

        image = self.rfile.read(content_length)

        start = time.time()
        body = self.loadbalancer.use_aws_services(str(MyServer.client_count % 10), image, MyServer.client_count)
        end = time.time()
        MyServer.Avarage_RTT_time = (MyServer.Avarage_RTT_time + (end - start))
        print("Content Length: ", content_length)
        print("Client number in 10 Seconds is: ", MyServer.client_count)
        print("Max Client Number: ", MyServer.max_client_count)
        print("RTT time: ", (end-start), "Seconds")
        print("Avarage RTT time is: ",MyServer.Avarage_RTT_time/MyServer.max_client_count)
        if body == 'None':
            body = "<html><head><title>AWS Cloud Computing</title></head><p>Request: [{'itemId': 'Jacuzzi'}, {'itemId': 'Scotch Tape'}]</p><body><p>This is an example web server.</p></body></html>"
            
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>AWS Cloud Computing</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" %body, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))




if __name__ == "__main__":

    webServer = HTTPServer((hostName, serverPort), MyServer)
    server_start_date = time.time()
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

