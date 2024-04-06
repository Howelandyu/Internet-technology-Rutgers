#Abraham Gale 2020
#feel free to add functions to this part of the project, just make sure that the get_dns_response function works
from resolver_backround import DnsResolver
import threading
import socket
import struct
import argparse
from sys import argv
from time import sleep
from helper_funcs import DNSQuery
class MyResolver(DnsResolver):
	def __init__(self, port):
		self.port = port
		#define variables and locks you will need here
		self.cache_lock = threading.Lock()
	def get_dns_response(self, query):
		#input: A query and any state in self
		#returns: the correct response to the query obtained by asking DNS name servers
		#Your code goes here, when you change any 'self' variables make sure to use a lock
		q = DNSQuery(query)
		print(q)
		a = DNSQuery()
		a.header['ID'] = q.header['ID']
		a.header['QR'] = 1
		a.header['RCODE'] = 2
		print(a)
		return a.to_bytes()
parser = argparse.ArgumentParser(description="""This is a DNS resolver""")
parser.add_argument('port', type=int, help='This is the port to connect to the resolver on',action='store')
args = parser.parse_args(argv[1:])
resolver = MyResolver(args.port)
resolver.wait_for_requests()
