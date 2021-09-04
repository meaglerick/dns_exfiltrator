#! /usr/bin/env python3

from scapy.all import DNS, DNSQR, DNSRR, IP, send, sniff, sr1, UDP
import random
import string
import sys, argparse
import time

#adapted from: https://thepacketgeek.com/scapy/building-network-tools/part-09/
apexdomain = ''


def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def get_random_ip_address():
    #def randquad(): return str(random.randint(1,223))
    randIP = [str(random.randint(1,223)) for i in range(0,4)]
    return '.'.join(x for x in randIP)

def dns_responder(pkt: IP):
    global apexdomain
    
    
    queryname = pkt["DNS Question Record"].qname #byte class
    if (DNS in pkt and pkt[DNS].opcode == 0 and pkt[DNS].ancount == 0):
        if apexdomain in str(queryname) and (pkt["DNS Question Record"].qtype == 1): #A Record (AAAA Record == 28)
            
            #A DNS response for an A record should come back
            # 1. The original Question
            # 2. An RR count
            # 3. The A record answers

            #here's another test packet -> DNS response with a CNAME, sends back a CNAME -> redirct with bogus data
            
            aliasanswer = bytes(get_random_string(48) + '.' + apexdomain, 'utf-8')            
            dnsARecordAnswer = DNSRR(rrname=aliasanswer, type=1, rclass=1, rdlen=None, rdata=get_random_ip_address()) 
            dnsCNameAnswer = DNSRR(rrname=queryname, type=5, rclass=1, ttl=60, rdlen=None, rdata=aliasanswer)
            dnsOriginalQuery = DNSQR(qname=queryname, qtype=1, qclass=1)

            l5 = DNS(length=None, id=pkt[DNS].id, qr=1, opcode=0, aa=0, tc=0, rd=1, ra=1, z=0, ad=0, cd=0, rcode=0, qdcount=1, ancount=2, nscount=0, arcount=0, qd=dnsOriginalQuery,
                an=dnsCNameAnswer/dnsARecordAnswer, ns=None, ar=None)
            l4 = UDP(dport=pkt[UDP].sport, sport=53)
            l3 = IP(dst=pkt[IP].src, src=pkt[IP].dst)
            response_packet: IP
            response_packet = l3/l4/l5
            send(response_packet)
            print("Responding with: ", response_packet.summary())
        else:
            pass #not the right dns query
            
    return None
                    

def start_sniffer(bpf_filter, listen_int):
    print('Sniffing on ', listen_int, ' with a filter of: ', bpf_filter)
    #sniff(filter=bpf_filter, prn=dns_responder(dns_server_ip), listen_int=listen_int)

    #sniff(filter=bpf_filter, prn=dns_responder, listen_int='ens38')
    sniff(filter=bpf_filter, prn=dns_responder, iface = listen_int)
    #sniff(filter=bpf_filter, prn=dns_responder, listen_int=listen_int)
    

def send_random_dns_query(dnsserver, apexdomain):
    while True:
        searchquery = get_random_string(random.randint(24,48)) + '.' + apexdomain
        l5 = DNS(rd=1, qd=DNSQR(qname=searchquery,qtype="A"))
        l4 = UDP(dport=53)
        l3 = IP(dst=dnsserver)
        packet = l3/l4/l5
        randomtime = random.randint(1,5)
        print("Sending randomized DNS to ", dnsserver, " Sleeping for: ", randomtime, " seconds\n", packet.summary())
        send(packet)
        time.sleep(randomtime)

def main(args):

    print(args)
    if(args['listener']):
        print("Starting DNS listener/responder")
        global listen_int, local_ip, apexdomain
        
        
        listen_int = args['interface']
        #local_ip = args['dns']
        dns_server_ip = args['dns']
        apexdomain = args['apexdomain']
        
        #bpf_filter =  f"udp port 53 and ip dst {args['dns']}"
        bpf_filter =  "udp port 53"
        print(listen_int)
        start_sniffer(bpf_filter, listen_int)

    else:
        
        send_random_dns_query(args['dns'], args['apexdomain'])

if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument('--listener', dest='listener', help='Define if this is going to listen for DNS queries \
        or send queries to a DNS server', action='store_true')
    ap.add_argument("-d", "--dns", type=str, help='The upstream DNS Server address \
        if this is a sending DNS tumbler. Otherwise, omit.')
    ap.add_argument("-a", "--apexdomain", type=str, help='The Apex domain')
    ap.add_argument("-i", "--interface", type=str, default='',
        help='If this is a responding dns tumbler, define the interface \
        to listen on. Otherwise omit')

    args = vars(ap.parse_args())
    
    main(args)
