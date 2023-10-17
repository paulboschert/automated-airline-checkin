#!/usr/bin/env python3

from subprocess import Popen
from Client import Client

def test_server_client():
    '''
    We start the server and let it run in the background. Then we ask 
    the client to make a call to the server and we compare the expected value.
    '''
    server = Popen('./src/Server.py')
    client = Client()
