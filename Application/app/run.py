from gevent.pywsgi import WSGIServer
from flask_app import app
import os

ip = '0.0.0.0'
port = 30000
# app.debug = True
http_server = WSGIServer((ip, port), app)#, keyfile='key.pem', certfile='cert.pem')

http_server.serve_forever()

