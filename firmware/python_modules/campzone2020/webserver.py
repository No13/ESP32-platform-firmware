import _thread, time, socket, network

class webserver:
    
    _http_socket = None
    _sta = None
    _paths = {}
    _server = None
    def __init__(self):
        self._sta = network.WLAN(network.STA_IF)

    def on_path(self,path,function):
        self._paths[path] = function
        return True

    def start(self):
        self._server = _thread.start_new_thread("webserver",self.webserver_thread,[self.handle_request])

    def handle_request(self,data):
        try:
            path = data['url'].split("?")[0]

            if path in self._paths:
                response = 'HTTP/1.0 200 OK\r\n\r\n'
                response += self._paths[path](data)
            else:
                response = "HTTP/1.0 404 Not Found\r\n\r\n<pre>Request could not be processed.</pre>"
            data['socket'].send(response)
            data['socket'].close()
        except BaseException as e:
            print("Error in handling request:",e)

    def webserver_thread(self,callback):
        # Not sure if this needs to be global...
        global http_socket
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        http_socket = socket.socket()
        http_socket.bind(addr)
        http_socket.listen(True)
        http_socket.setblocking(False)
        print("Webserver started")
        while True:
            try:
                cl, addr = http_socket.accept()
            except:
                time.sleep(0.1)
                continue
            try:
                cl_file = cl.makefile('rwb', 0)
                # Retrieve request from incoming connection
                request = cl_file.recv(1024).decode("utf-8")
                request = request.split("\r\n")
                try:
                    temp_request = request[0].split(" ")
                    http_method = temp_request[0]
                    postdata = {}
                    if(http_method == "POST"):
                        for line in request:
                            if ('Content-Length' in line) and (int(line.split(': ')[1]) > 0):
                                # Try to retrieve post stuff
                                try:
                                    form_data = cl_file.recv(1024).decode("utf-8")
                                    formfields = form_data.split('&')
                                    for field in formfields:
                                        data = field.split('=')
                                        postdata[data[0]] = data[1]
                                except:
                                    pass

                    if postdata == {}:
                        req = { 'client': addr[0], 'method': http_method, 'url': temp_request[1], 'socket': cl }
                    else:
                        req = { 'client': addr[0], 'method': temp_request[0], 'url': temp_request[1], 'postdata': postdata, 'socket': cl }
                    callback(req)
                except BaseException as e:
                    print("Invalid request",e, request)
                    continue
            except BaseException as e:
                print(e)
            time.sleep(0.1)
