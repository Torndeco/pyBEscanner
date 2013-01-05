import binascii
import struct
from _thread import start_new_thread, allocate_lock

def becon_receivemessage(s):
	start_new_thread(becon_keepalive,(s,))
	while 1:
		lock.acquire()
		reply = s.recv(4096)
		lock.release()
		if ord(reply[7:8]) == 2:
			sendmessage(s, becon_acknowledge(ord(reply[8:9])))
			print(reply[9:])
			handle_reply(reply[9:])
		elif ord(reply[7:8]) == 1:
			if reply[9:] != '':
				print(reply[9:])
				handle_reply(reply[9:])
		elif ord(reply[7:8]) == 0:	
			if ord(reply[8:9]) == 0:
				print('Login failed')
			elif ord(reply[8:9]) > 0:
				pass
				# todo: multipacket handeling here

def becon_loginpacket(password):
	message = '\x00' + password
	message = '\xFF' + message
	checksum = binascii.crc32(message) & 0xffffffff
	checksum = struct.pack('l', checksum)
	checksum = checksum[:4]
	return 'BE' + checksum + message

def becon_cmdpacket(keepalive, cmd):
	global sequence

	if keepalive == False:
		message = '\x01' + chr(sequence) + cmd
	else:
		message = '\x01' + chr(sequence)
	message = '\xFF' + message
	sequence += 1
	checksum = binascii.crc32(message) & 0xffffffff
	checksum = struct.pack('l', checksum)
	checksum = checksum[:4]
	return 'BE' + checksum + message

def becon_acknowledge(sequence):
	message = '\x02' + chr(sequence)
	message = '\xFF' + message
	checksum = binascii.crc32(message)
	checksum = struct.pack('l', checksum)
	checksum = checksum[:4]
	return 'BE' + checksum + message

def becon_keepalive(s):
	timer = 0
	while True:
		if timer < 30:
			time.sleep(1)
			timer += 1
		else:
			# fooBar is not send, it's just a placeholder since its a keepalive packet
			sendmessage(s, becon_cmdpacket(True, 'fooBar'))
			timer = 0