import socket,time,os,argparse

ip       = "192.168.1.2"
port     = 22558
SEND_RCU = 889192452 #HuMessage.MSG_REMOTE_PROTOCOL_SEND_RCU_VALUE
n    = 1
if os.name!="nt":
	G,B,R,W,M,C,end= '\033[92m','\033[94m','\033[91m','\x1b[37m','\x1b[35m','\x1b[36m','\033[0m'
	Bold,underline = "\033[1m","\033[4m"
else:
	try:
		import win_unicode_console , colorama
		win_unicode_console.enable()
		colorama.init()
		G,B,R,W,M,C,end= '\033[92m','\033[94m','\033[91m','\x1b[37m','\x1b[35m','\x1b[36m','\033[0m'
		Bold,underline = "\033[1m","\033[4m"
	except:
		G = B = R = W = M = C = Bold = underline = ''

global sendBuf
sendBuf = "".ljust(256,'\0') # The original packet length is 1024 :D #bytearray(1024) #[struct.pack('B', 0)]*1024

#Todo : play with the buffer multiple(1024,512,256...) :D
def arraycopy(src,src_start,copy_to,start,end):
	global sendBuf
	copy_to = list(copy_to)
	for i in range(start,end):
		copy_to[i] = src[src_start]
		src_start +=1
	sendBuf = "".join(copy_to)

def send_button(code):
	global n
	data = "%04x"%code
	type = "rcu" #touch
	arraycopy("hmxra",0,sendBuf,0,len("hmxra"))
	arraycopy(type,0,sendBuf,8,8+len(type) )
	arraycopy(data,0,sendBuf,16,16+len(data) )
	print(W+"-"*14+"("+str(n)+")"+"-"*14)
	print(M+"Buffer length --> "+ R +str(len(sendBuf)))
	print(C+"Hexadecimal(Zero-padded) Button ->"+ B +str(data))
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	s.sendto( sendBuf.encode(), (ip, port))
	s.close()
	n +=1

def main():
	parser = argparse.ArgumentParser(prog='sendUDP.py')
	parser.add_argument("-l", "--list",action="store_true", help="List all available buttons.")
	parser.add_argument("--try-this", metavar='<code>', type=int, help="Try to send a specific code.")
	parser.add_argument("--loop", metavar='<button>', help="keep sending this button every 0.5s (Stop with Ctrl+C)")
	parser.add_argument("-j", "--jam",action="store_true", help="Prevent any one from sending commands to the receiver (Even with the remote controller)")
	parser.add_argument("-b", type=str, metavar='<button>', help="Button to send or buttons seperated by space.", nargs='+')
	args    = parser.parse_args()
	keys = {"+":112,"-":113,"ch+":80,"ch-":81,"ok":88,"u":84,"d":85,"r":83,"l":82,"mute":114,"back":86,"on":1,"off":1,
		"exit":87,
		"0":16,"1":17,"2":18,"3":19,"4":20,"5":21,"6":22,"7":23,"8":24,"9":25}
	if args.list :
		print("""Buttons implemented till now :
	+/-                Refers to volume up/down buttons.
	ch+/ch-            Refers to channel plus/minus buttons.
	Ok/mute/back/exit  Refers to its name of course :3
	U/D/R/L            Arrows buttons (U for up, D for down and so on...)
	0 1...9            Enter channel numbers seperated by spaces
	on/off             Turn the device on/off of course
	""")
	elif args.jam :
		while True:
			try:
				send_button(87) #exit button code :D
			except:
				print("\nYup, enough jamming :D")
				break
	elif args.try_this :
		send_button(int(args.try_this))
	elif args.loop :
		while True:
			try:
				send_button( keys[args.loop.lower()] )
				time.sleep(0.5)
			except:
				print("\nYup, enough looping :D")
				break
	elif args.b:
		print(G+Bold+"\t Humax CLI - By Karim Shoair (D4Vinci)")
		try:
			btns  = args.b    #80 channel_plus |112 #volume_up |97 #Channel_minus |88 #OK
			for btn in btns:
				if btn in list("0123456789"):
					send_button(keys[btn])
				else:
					send_button(keys[btn.lower()])
					time.sleep(0.2)
		except Exception as e:
			#print(e)
			print("Error in sending button!")
	else:
		print("Use --help or -h to list all the options")
		print("""Buttons implemented till now :
	+ 			 Refers to volume up button    (And opposite is - of course)
	ch+ 		 	 Refers to channel plus button (And opposite is ch- of course)
	Ok/mute/back/exit	 Refers to its name of course :3
	U D R L			 Arrows buttons (U for up, D for down and so on...)
	0 1...9			 Enter channel numbers seperated with spaces
	on/off			 Turn the device on/off of course
	""")

if __name__ == '__main__':
	main()
