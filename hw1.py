import socket
import os
import http_utils
import urllib

def find_path(url):
    return url[1:]


def make_headers():
    headers = {"Connection": " close", "Content-Type": " text/html"}
    return headers


def build_page(path, files, dirs):
    if path == "/":
        parent = "/"
    else:
        parent = path.rsplit("/", 1)[0]
    page = """<!DOCTYPE html> 
           <html> 
                <body>
                    <ul>
           """
    page = page + "<li> <a href=\"..\"> parent </a> </li>"
    for file in files:
        page = page + "<li>" + file + "</li>\r\n"
    for d in dirs:  # should quote here
        page = page + "<li> <a href=\"" + d + "/\">" + d + "</a> </li>"
    page = page + """       </ul>
                        </body> 
                  </html>"""
    return page


def get_data(path):
    r, d, f = next(os.walk('./'+path))
    return f, d

def error(code):
    x, y = http_utils.make_response(code, {"Connection": " close"}, "error")
    return x+y


def handle_request(msg):
    try:
        request = http_utils.decode_http(msg)
        url = request['Request'].split(' ')
        if not url[0] == 'GET':
            print(501)
            return error(501)
        if "Host" not in request:
            print(400)
            return error(400)
        path = urllib.parse.unquote(find_path(url[1]))
        # print(path+"-----------------------------------")
        if not os.path.isdir("./"+path):
            print(404)
            return error(404)
        files, dirs = get_data(path)
        page = build_page(path, files, dirs)
        headers = make_headers()
        x, y = http_utils.make_response(200, headers, page)
        print(200)
        return x+y
    except Exception:
        return error(500)


while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 8888))
        s.listen()
        conn, addr = s.accept()
        with conn:
            message = conn.recv(4096)
            if not message:
                continue
            answer = handle_request(message)
            conn.sendall(answer)