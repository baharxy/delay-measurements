import socket
import time
import sys
import logging
import pdb
logging.basicConfig(filename='time_shift.txt',level=logging.DEBUG)
import ntplib
import datetime
c = ntplib.NTPClient()
import os


 
#DEFINE INPUTS HERE
REFLECTOR_HOST = '134.226.40.138' #IP ADDRESS TO LISTEN FOR INCOMMING PACKETS (v4 or v6)
REFLECTOR_PORT = 60000 #IP PORT TO LISTEN FOR INCOMMING PACKETS
REMOTE_PORT = 60000 #REMOTE PORT TO REFLECT PACKETS TO
REFLECT_SWITCH =0 #REFLECTION ENABLED:1 (TWO-WAY DELAY), REFLECTION DISABLED:0 (ONE-WAY DELAY)
BUFFER = 4096
PACKET_SIZE = 1500 #DATAGRAM SIZE IN BYTES
NR_OF_PACKETS=2000 #TOTAL NR. OF PACKETS TO SEND
PACKETS_PER_SEC=100 #PACKETS PER SECOND
file_name='csv/udp_oneway_' + '%s' %(PACKET_SIZE) +'bytes_' +'%s' %(NR_OF_PACKETS) +'packets'+ '%s' %(PACKETS_PER_SEC)+'sec'+ datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S_%f')[ :-3] + '.csv'


ADDR = (REFLECTOR_HOST, REFLECTOR_PORT)
 
#DUMB CHECK OF IP ADDRESS VERSION
if ':' in REFLECTOR_HOST:
 EchoServer = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
else:
 EchoServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 
#BINDING, PROCESSING AND WRITING TO CSV
try:
 EchoServer.bind(ADDR)
 print ('echo server started on port', ADDR)
except Exception:
 print '***ERROR: Port Binding Failed'

#just to get the offset from the ntp server
command = "ntpq -nc peers | tail -n +3 | grep \* | cut -c 62-71| tr -d ' '   "
ntproc = os.popen(command)
offset=float(  ntproc.read()) / 1000
#offset=float( ntproc.stdout.readline() )

#response = c.request('logger.scss.tcd.ie', version=3)
#time shift
txt = '%.3f' % ( offset)
print txt
while True:
 data, addr = EchoServer.recvfrom(BUFFER)
 #reception time
 actual_time=float(time.time()+offset)
 #get the content
 addlst=addr[0],addr[1]
 if REFLECT_SWITCH == 1:
  EchoServer.sendto('%s' % (data), addlst)
 
 splitdata = data.split(',')
 timecount = splitdata[0].strip("('")
 #measure one way delay
 #one_way_delay = (time.time() - float(timecount))
 one_way_delay = ( actual_time - float(timecount))
 packet_number = str(splitdata[1].strip("' '"))
 packet_number = packet_number.lstrip('0')
 client_interface=str(splitdata[2].strip("' '"))
 #client_interface=client_interface.lstrip()
 #was there to log time shift- but may be this adds additional delay so we only do it once
 #logging.info(txt)

 
 outfile = open(file_name, "a").write(str(str(actual_time)+','+'received , '+ packet_number+' , '+str(one_way_delay)+', '+client_interface+'\n'))
 print (time.ctime()+','+'received , '+ packet_number+' , '+str(one_way_delay)+', '+client_interface)
 
EchoServer.close()



