import logging

import requests

from sys import argv

from pathlib import Path

from PIL import Image

from http.server import BaseHTTPRequestHandler, HTTPServer

FILE_DIR = "Downloads"
AUTHENTICATION_KEY = "kmrhn74zgzcq4nqb"

class S(BaseHTTPRequestHandler):
    def _set_response(self, status):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        status = 200
        response_msg = ""
        # Gets the size of data
        content_length = int(self.headers['Content-Length'])

        # Gets the data itself
        post_data = self.rfile.read(content_length)

        API_key = self.headers['Authorization']
        if API_key != AUTHENTICATION_KEY:
            status = 401
            response_msg = "{'message' : 'Unauthorized client!'}, 401"
        else:
            first_image_url = ""
            second_image_url = ""
            body_data_list = str(post_data).split(",")
            for i in range(len(body_data_list)):
                if i == 0:
                    first_image_url = body_data_list[i][body_data_list[i].find(':') + 1 :].replace(' ', '').replace('\r\n', '').replace("\\", '')[1 : -1]
                else:
                    second_image_url = body_data_list[i][body_data_list[i].find(':') + 1 :].replace(' ', '').replace("\"", '').replace("\\r\\n}", '').replace("\\", '').replace("'", '')
            image1_file = requests.get(first_image_url)
            image2_file = requests.get(second_image_url)
            if image1_file.status_code != 200 or \
                    image2_file.status_code != 200:
                status = 404
                response_msg = "{'message' : 'The url of image files does not exist.'}, 404"
            else:
                home_path = str(Path.home())
                image_file_path = home_path + '/' + FILE_DIR + '/'
                i1_file = image_file_path + first_image_url[first_image_url.rfind("/") + 1 :]
                i2_file = image_file_path + second_image_url[second_image_url.rfind("/") + 1 :]
                open(i1_file, 'wb').write(image1_file.content)
                open(i2_file, 'wb').write(image2_file.content)

                i1 = Image.open(i1_file)
                i2 = Image.open(i2_file)
                pairs = zip(i1.getdata(), i2.getdata())
                if len(i1.getbands()) == 1:
                    dif = sum(abs(p1-p2) for p1,p2 in pairs)
                else:
                    dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))
                ncomponents = i1.size[0] * i1.size[1] * 3
                status = 200
                result = str((dif / 255.0 * 100) / ncomponents)
                response_msg = "{'message' : The percentage of two images similarity is " + result + "%}, 200"

        self._set_response(status)
        self.wfile.write(response_msg.encode("utf-8"))

def run(server_class = HTTPServer, handler_class = S, port = 8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
