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



@app.route('/dns', methods=['GET', 'POST'])
def return_dns():
    print('gotta hit')
    if request.method == "POST":
        print('taht was a post')
        print(request.values)
    elif request.method == "GET":
        # print(request.args)
        query = request.args.get('dns')
        query = query + "==="
        print(query)
        #query_to_bytes = query.encode()
        #print(query_to_bytes)
        #return
        #print(dns.name.from_wire(query, 0))
        ##message = dns.name.from_wire(query, 0)
        #print(message)

        message = base64.b64decode(query)

        dns_message = dns.name.from_wire(message,12)
        print(dns_message)
        return

        hex = base64.b64decode(query).encode('hex')
        print("b64decode: ", message)
        print("encodehex: ", hex)
        return
        #message = dns.name.from_wire(base64.b64decode(query), 0)
        print("urlsafe decode: ", base64.urlsafe_b64decode(query))
        #message2 = dns.name.from_wire(base64.urlsafe_b64decode(query), 0)
        print("standard_b64decode: ", base64.standard_b64decode(query))
        #message3 = dns.name.from_wire(base64.standard_b64decode(query), 0)

        temp = dns.rdata.from_wire(rdclass= dns.rdataclass.IN , \
            rdtype=dns.rdatatype.A, \
            wire = base64.urlsafe_b64decode(query), \
                current = 0, \
                rdlen = len(base64.urlsafe_b64decode(query)))

        #print(decoded)
        #print(decoded.decode('utf-8'))

        # print(request.args.getlist())

    return "Hello dns"




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

