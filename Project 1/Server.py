import binascii
import socket
import struct
import argparse
from sys import argv

#used https://200ok.ch/posts/2018-12-09_unhexlify.html to get hex character from ord()
def toHex(url):
    label_sizes = getLabelSizes(url)
    hexStr = ""
    for len in label_sizes:
        hexStr = hexStr + len
        size = int(len)
        for x in range(0, size):
            hexStr = hexStr + ('%x' % ord(url[x]))
        url = url[size+1:]
    return hexStr

def getLabelSizes(url):
    label_sizes = list() #list of sizes for each label i.e. www.example.com would have list = [7,3]
    while(url.find('.') != -1):
        indx = url.find('.')
        indx = str(indx)
        if(indx == '1' or indx == '2' or indx == '3' or indx == '4' or indx == '5' or indx == '6' or indx == '7' or indx == '8' or indx == '9'):
            newIndx = '0'+indx
            label_sizes.append(newIndx)
        else:
            label_sizes.append(indx)
        indx = int(indx)
        indx += 1
        url = url[indx:]

    indx = str(len(url))
    if(indx == '1' or indx == '2' or indx == '3' or indx == '4' or indx == '5' or indx == '6' or indx == '7' or indx == '8' or indx == '9'):
        newIndx = '0'+indx
        label_sizes.append(newIndx)
    else:
        label_sizes.append(indx)
    return label_sizes

def hexToDecimal(hexStr):
    ip = ""
    for x in range(0, len(hexStr), 2):
        pair = hexStr[0:2]
        num = int(pair, 16)
        ip = ip + str(num)
        if(x == 6):
            return ip
        ip = ip + '.'
        hexStr = hexStr[2:]

#https://routley.io/posts/hand-writing-dns-messages/ used this link for the code below
def send_udp_message(message, address, port):
    """send_udp_message sends a message to UDP server

    message should be a hexadecimal encoded string
    """
    #message = message.replace(" ", "").replace("\n", "")
    server_address = (address, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(binascii.unhexlify(message), server_address)
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()
    return binascii.hexlify(data).decode("utf-8")



#First we use the argparse package to parse the aruments
parser = argparse.ArgumentParser(description="""YA MUVVA""")
parser.add_argument('port', type=int, action='store')
args = parser.parse_args(argv[1:])

#next we create the server socket and bind it to the given port from command line
ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.bind(('',args.port))
ss.listen(0)
ss_local, addr = ss.accept()
print("[CONNECTION ESTABLISHED]...Connected to Local Server")

while True:
    url = ss_local.recv(512)
    url = url.decode('utf-8')

    if not url:
        break

    #www = "www."
    #if www in url:
        #url = url[4:]
    #=================================

    ss_DNS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("[CONNECTION ESTABLISHED]...Connected to Google DNS Server")

    #url = "facebook.com"
    hexURL = toHex(url)
    dns_header = "AAAA01000001000000000000"
    dns_query = dns_header + hexURL + "0000010001"
    dns_answer = send_udp_message(dns_query,"8.8.8.8", 53)
    print("[MESSAGE RECIEVED]...Google DNS Responded: ")
    print("[HEX RESPONSE]..." + dns_answer)

    #header info
    num_Answers = dns_answer[12:16]
    print("[NUMBER OF ANSWERS]..." + num_Answers)

    #body info
    c00c_indx = dns_answer.index('c00c') #find first instance of c00c because that is where answer(s) begins
    dns_body = dns_answer[c00c_indx:]    #now you have just the body to work with, where all the info is
    record_Type = dns_body[4:8]
    RDLENGTH = dns_body[20:24]

    print("[RECORD TYPE]...." + record_Type)

    if(num_Answers == '0001'):
        #one answer
        if(record_Type != '0001' or RDLENGTH != '0004'):
            notFound = "not found"
            ss_local.sendall(notFound.encode('utf-8'))
        else:
            hexIP = dns_answer[-8:]
            ip = hexToDecimal(hexIP)
            ss_local.sendall(ip.encode('utf-8'))
    else:
        #multiple answers
        print("[MULTIPLE ANSWERS]")
        numAnswers = int(num_Answers)
        ipList = ""
        while(numAnswers > 0):
            RDLENGTH = dns_body[20:24]
            print("[RDLENGTH]..." + RDLENGTH)
            record_Type = dns_body[4:8]
            if(record_Type != '0001' or RDLENGTH != '0004'):
                notFound = "not found"
                ipList = ipList + notFound + ','
                cutOff = int(RDLENGTH, 16)*2
                dns_body = dns_body[24:] #this cuts off right after RDLENGTH
                dns_body = dns_body[cutOff:]
                '''
                dns_body = dns_body[4:]
                try:
                    c00c_indx = dns_body.index('c00c')
                    dns_body = dns_body[c00c_indx:]
                except:
                    print("c00c not found")
                try:
                    c02e_indx = dns_body.index('c02e')
                    dns_body = dns_body[c02e_indx:]
                except:
                    print("c02e not found")
                '''

            else:
                RDATA = dns_body[24:32]
                print("[RDATA]..." + RDATA)
                tmpIP = hexToDecimal(RDATA)
                print("[TRANSLATED IP IS]..." + tmpIP)
                ipList = ipList + tmpIP + ','
                dns_body = dns_body[32:]

            numAnswers -= 1

        if(ipList[len(ipList)-1] == ','):
            ipList = ipList[:len(ipList)-1]

        ss_local.sendall(ipList.encode('utf-8'))

    #====================================


ss_DNS.close()
ss_local.close()
ss.close()