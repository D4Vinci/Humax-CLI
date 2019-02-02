import socket, time, os, argparse, sys

port     = 22558
SEND_RCU = 889192452 #HuMessage.MSG_REMOTE_PROTOCOL_SEND_RCU_VALUE

parser = argparse.ArgumentParser(prog='sendUDP.py')
parser.add_argument("-i", "--ip", help="Receiver IP address. (Most times 192.168.x.2)")
parser.add_argument("-l", "--list",action="store_true", help="List all available buttons.")
parser.add_argument("--try-this", metavar='<code>', type=int, help="Try to send a specific code.")
parser.add_argument("--loop", metavar='<button>', help="Keep sending this button every 0.5s (Stop with Ctrl+C)")
parser.add_argument("-j", "--jam",action="store_true", help="Prevent all connections to the receiver.")
parser.add_argument("-b", type=str, metavar='btn', help="Buttons separated by space.", nargs='+')
args    = parser.parse_args()

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

buttons_list = """Buttons implemented till now :
	+/-                Refers to volume up/down buttons.
	ch+/ch-            Refers to channel plus/minus buttons.
	U/D/R/L            Arrows buttons (U for up, D for down and so on...)
	0 1...9            Enter channel numbers separated by spaces
	Rec                Record the current program on the current channel
	Stop               Stop recording
	Forward/Backward   Controlling the current file/recording
	on/off             Turn the device on/off of course
	And the following refers to its name:
		  Ok, Mute, Back, Exit, Menu, Media, Last, Settings, Home
"""

global sendBuf
sendBuf = "".ljust(256,'\0') # The original packet length is 1024 :D #bytearray(1024) #[struct.pack('B', 0)]*1024

def arraycopy(src, src_start, copy_to, start, end):
	global sendBuf
	copy_to = list(copy_to)
	for i in range(start,end):
		copy_to[i] = src[src_start]
		src_start +=1
	sendBuf = "".join(copy_to)

def send_button(ip, code, button_name, normal=False):
	data = "%04x"%code
	type = "rcu" #touch
	arraycopy("hmxra",0,sendBuf,0,len("hmxra"))
	arraycopy(type,0,sendBuf,8,8+len(type) )
	arraycopy(data,0,sendBuf,16,16+len(data) )
	if normal:
		print(end+M+Bold+"- "+button_name.capitalize()+" button sent with Buffer length " +str(len(sendBuf))+
			" and the Hexadecimal(Zero-padded) Button is " +str(data))
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	s.sendto( sendBuf.encode(), (ip, port))
	s.close()

def main():
	ip = ""
	if not args.ip:
		print(end+R+Bold+"Receiver ip is required!"+end)
		exit(0)
	else:
		ip = args.ip

	keys = {"+":112,"-":113,"ch+":80,"ch-":81,"ok":88,"u":84,"d":85,"r":83,"l":82,"mute":114,"back":86,"on":1,"off":1,
		"exit":87,"rec":147,"stop":146,"menu":50,"media":61,"last":98,"forward":148,"backward":149,"settings":168,"home":241,
		"0":16,"1":17,"2":18,"3":19,"4":20,"5":21,"6":22,"7":23,"8":24,"9":25}
	if args.jam :
		starting_time = time.time()
		n = 1
		J = "Jamming."
		sys.stdout.write("\n\t"+J)
		while True:
			try:
				send_button(ip, 87, 'Exit') #exit button code :D
				n +=1
				J +="."
				sys.stdout.write(end+G+"\r [+] "+W+"{:12}".format(J) + end+R+Bold+" - Packets sent "+str(n) )
				sys.stdout.flush()
				if len(J)==12:
					J = "Jamming"
			except KeyboardInterrupt:
				print(end+W+Bold+"\n\nSent "+str(n)+" packet(s) in less than "+str( 1+int(time.time()-starting_time) )+" second(s)." )
				break
			except Exception as e:
				#print(e)
				print(end+R+Bold+"Something went wrong while jamming, maybe the receiver blocked us!")
				break

	elif args.try_this :
		send_button(ip, int(args.try_this), "Code "+args.try_this)

	elif args.loop :
		n = 1
		starting_time = time.time()
		n = 1
		J = "Looping."
		sys.stdout.write("\n\t"+J)
		while True:
			try:
				send_button(ip, keys[args.loop.lower()], args.loop )
				time.sleep(0.5)
				n +=1
				J +="."
				sys.stdout.write(end+G+"\r [+] "+W+"{:10}".format(J) + end+R+Bold+" - Packets sent "+str(n) )
				sys.stdout.flush()
				if len(J)==10:
					J = "Looping"
			except KeyboardInterrupt:
				print(end+W+Bold+"\n\nSent "+str(n)+" packet(s) in less than "+str( 1+int(time.time()-starting_time) )+" second(s)." )
				break
			except Exception as e:
				#print(e)
				print(end+R+Bold+"Something went wrong while loop!")
				break

	elif args.b:
		try:
			btns  = args.b    #80 channel_plus |112 #volume_up |97 #Channel_minus |88 #OK
			for btn in btns:
				if btn in list("0123456789"):
					send_button(ip, keys[btn], btn, True)
					time.sleep(0.2)
				else:
					send_button(ip, keys[btn.lower()], btn, True)
					time.sleep(0.5)
		except Exception as e:
			#print(e)
			print(end+R+Bold+"Error in sending button!")

if __name__ == '__main__':
	if args.list :
		print(end+G+buttons_list+end)
	elif len(args.__str__())==75: # To print help if there's no argument at all
		parser.print_help()
		print("\n"+buttons_list)
	else:
		print(end+G+Bold+"Humax IR4000HD terminal client made with ❤️  By Karim 'D4Vinci' Shoair"+end)
		main()
