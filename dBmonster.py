# dBmonster - Track WiFi devices with their signal strength in dBm
# by 90N45 - github.com/90N45-d3v

import os

os.system("clear")
print("\r\033[38;5;172m" + "\n                                                   --=-+-=--\n                                                        \\\n                                                   ---=--+--=---\n                 ( ( >*< ) )                             |\\\n     _  ____          |                      _     ---=----+----=---\n    | ||  _ \\         |                     | |          |\n  __| || |_) | _ __  /_\\   ___   _ __   ___ | |_   ___  _|__\n / _` ||  _ < | '_ `'_  | / _ \\ | '_ \\ / __||  _| / _ \\|  __|\n| (_| || |_) || | | | | || (_) || | | |\\__ \\| |_ |  __/| |\n \\__,_||____/ |_| |_| |_| \\___/ |_| |_||___/ \\__| \\___||_|" + "\033[38;5;27m" + "\nby github.com/90N45-d3v" + "\033[39m" + "\033[38;1;231m" + "\n\n Launching dBmonster...")

import re
import time
import requests
from sys import platform
from itertools import count
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.animation import FuncAnimation

x_values = []
y_values = []
index = count() # x axis is count of dBm values

ax = plt.axes()
fig = plt.gcf()

wigle_api_key = ""

if os.path.exists("WiGLE.key"):
	key_file = open("WiGLE.key", "r")
	wigle_api_key = key_file.read().replace("\n", "")
	key_file.close()

### functions

def banner():
	print("\033[38;5;172m" + "\n                                                   --=-+-=--\n                                                        \\\n                                                   ---=--+--=---\n                 ( ( >*< ) )                             |\\\n     _  ____          |                      _     ---=----+----=---\n    | ||  _ \\         |                     | |          |\n  __| || |_) | _ __  /_\\   ___   _ __   ___ | |_   ___  _|__\n / _` ||  _ < | '_ `'_  | / _ \\ | '_ \\ / __||  _| / _ \\|  __|\n| (_| || |_) || | | | | || (_) || | | |\\__ \\| |_ |  __/| |\n \\__,_||____/ |_| |_| |_| \\___/ |_| |_||___/ \\__| \\___||_|" + "\033[38;5;27m" + "\nby github.com/90N45-d3v" + "\033[39m")

def interface_list(): # List detected interfaces
	if platform == "linux": # Linux
		print("\033[38;1;231m" + "\n\n  --- WiFi INTERFACES ---" + "\033[0m") # List WiFi INTERFACES
		os.system("airmon-ng")
	elif platform == "darwin": # MacOS
		print("\033[38;1;231m" + "\n\n  --- WiFi INTERFACES ---" + "\033[0m\n") # List WiFi INTERFACES
		os.system("networksetup -listallhardwareports | grep -A3 Wi-Fi | grep -A1 Device")

def set_channel(): # Change channel on your WiFi card
	if platform == "linux": # Linux
			os.popen("iwconfig " + interface + " channel " + channel)

	elif platform == "darwin": # MacOS
		os.popen("airport " + interface + " -c" + channel)

def interface_check():
	if platform == "linux": # On linux, your WiFi card needs to be set in monitor mode by yourself
		mon_check = os.popen("iwconfig " + interface + " | grep Monitor -c").read()

		if mon_check == "0\n": # If interface isn't in monitor mode:
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Setting " + interface + " in monitor mode...")
			os.system("nmcli dev set " + interface + " managed no")
			os.system("ip link set " + interface + " down")
			os.system("iw " + interface + " set type monitor")
			os.system("ip link set " + interface + " up")

	elif platform == "darwin": # On MacOS you only need to enable WiFi
		os.system("airport " + interface + " -z") # Disconnect from WiFi network if connected
		os.system("tshark -i en0 -I -a duration:2 > /dev/null 2> /dev/null") # Just use tshark for a second
		time.sleep(1)

		wifi_state = int(os.popen("sudo airport en0 -I | grep init -c").read()) # On MacOS "Ventura" (at least mine) are issues disconnecting from wireless networks

		if wifi_state == 0:
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Please disconnect from the current WLAN manually...")

			while wifi_state == 0: # Loop till you are disconnected from any WLAN
				time.sleep(1)
				wifi_state = int(os.popen("sudo airport en0 -I | grep init -c").read())

def root_check():
	user = os.popen("whoami") # Get current user who runs dBmonster

	if user.read() != "root\n":
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " This tool needs root privileges (try: sudo)\n")
		exit()

def net_check():
	try:
		requests.head("https://github.com/", timeout=3)
		return True
	except:
		return False

def graph(): # Plot figure
	fig.set_facecolor('black') # Window bg color
	ax.set_facecolor('black') # Graph bg color
	ax.spines['left'].set_color('#3f64d9') # Graph axis color (left)
	ax.spines['bottom'].set_color('#3f64d9') # Graph axis color (bottom)
	ax.tick_params(axis='x', colors='#3f64d9') # Graph x axis text color
	ax.tick_params(axis='y', colors='#3f64d9') # Graph y axis text color

def signal_transfer(dBm_signal): # Transfer dBm values to the plot figure
	x_values.append(next(index))
	if dBm_signal < 0: # If recieved dBm is normal, use it
		global dBm_fallback
		dBm_fallback = dBm_signal # Save current signal for line 50
		y_values.append(dBm_signal)
	elif 'dBm_fallback' in globals(): # If recieved dBm signal is broken, use last known dBm value (dBm_fallback)
		y_values.append(dBm_fallback)
	else: # If recieved dBm signal is broken, but there is no fallback, use -65 dBm (Can only be the first recieved signal)
		y_values.append(-60)
	plt.cla()
	plt.plot(x_values, y_values, color='#ff9900')
	plt.pause(0.003)

def mode1_recon(): # Scan for WiFi devices... On MacOS only Networks
	if platform == "linux": # Linux
		print("\n")
		os.system("airodump-ng " + interface + " --band abg") # --band for scanning 2.4 GHz and 5 GHz

	elif platform == "darwin": # MacOS
		print("\n\n \033[38;1;231m --- ACCESS POINTS ---\n\033[0m")
		os.system("airport " + interface + " scan")
		print("\n\n \033[38;1;231m --- ASSOCIATED CLIENTS (2.4GHz) ---\n\033[0m")

		os.system("airport " + interface + " -c2")
		sta_1 = os.popen("tshark --autostop duration:15 -i " + interface + " -I -E separator=\"#\" -T fields -e wlan.da -e wlan.ds.current_channel -e wlan.ssid -f \"type mgt subtype probe-resp\" 2> /dev/null | sort | uniq").read()
		os.system("airport " + interface + " -c5")
		sta_2 = os.popen("tshark --autostop duration:15 -i " + interface + " -I -E separator=\"#\" -T fields -e wlan.da -e wlan.ds.current_channel -e wlan.ssid -f \"type mgt subtype probe-resp\" 2> /dev/null | sort | uniq").read()
		os.system("airport " + interface + " -c8")
		sta_3 = os.popen("tshark --autostop duration:15 -i " + interface + " -I -E separator=\"#\" -T fields -e wlan.da -e wlan.ds.current_channel -e wlan.ssid -f \"type mgt subtype probe-resp\" 2> /dev/null | sort | uniq").read()
		os.system("airport " + interface + " -c11")
		sta_4 = os.popen("tshark --autostop duration:15 -i " + interface + " -I -E separator=\"#\" -T fields -e wlan.da -e wlan.ds.current_channel -e wlan.ssid -f \"type mgt subtype probe-resp\" 2> /dev/null | sort | uniq").read()

		stations = sta_1 + sta_2 + sta_3 + sta_4
		stations = stations.replace("#", "\t").replace("\n\n", "\n")
		print("MAC ADDRESS\t\tCHANNEL\tCONNECTED")
		print(stations)

def mode2_lookup(device):
	mac_brick = device.replace(":", "", 2).partition(":")[0].upper()
	chr_check = "MA-L," + mac_brick + ",\""
	vendor = ""

	if os.path.exists("vendor-db.csv") == False:
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Downloading missing database...")
		mode2_update_vendors()

	print("\033[38;1;231m" + "\n\n --- OSINT Data ---\n" + "\033[0m")

	with open("vendor-db.csv") as csv:
		for line in csv:
			if mac_brick in line:
				if chr_check in line:
					vendor = line.partition("\"")[2].partition("\"")[0]
				else:
					vendor = line.partition(",")[2].partition(",")[2].partition(",")[0]

	if wigle_api_key != "":
		connection = net_check()
		if connection == True:
			wigle_wifi_url = "https://api.wigle.net/api/v2/network/search?onlymine=false&freenet=false&paynet=false&resultsPerPage=1&netid=" + device.replace(":","%3A")
			wigle_bt_url = "https://api.wigle.net/api/v2/bluetooth/search?onlymine=false&showBt=true&showBle=true&resultsPerPage=1&netid=" + device.replace(":","%3A")
			headers = {'User-Agent': 'dBmonster', 'Authorization': 'Basic ' + wigle_api_key}

			wigle_res = requests.get(wigle_wifi_url, headers=headers).json()
			res_count = str(wigle_res).partition("'totalResults': ")[2].partition(",")[0]

			if res_count == "0":
				wigle_res = requests.get(wigle_bt_url, headers=headers).json()

			wigle_type = str(wigle_res).partition("'type': '")[2].partition("'")[0]
			wigle_ssid = str(wigle_res).partition("'ssid': '")[2].partition("'")[0]
			wigle_country = str(wigle_res).partition("'country': '")[2].partition("'")[0]
			wigle_city = str(wigle_res).partition("'city': '")[2].partition("'")[0]
			wigle_street = str(wigle_res).partition("'road': '")[2].partition("'")[0]
			wigle_housenumber = str(wigle_res).partition("'housenumber': ")[2].partition(",")[0]
			wigle_long = str(wigle_res).partition("'trilong': ")[2].partition(",")[0]
			wigle_lat = str(wigle_res).partition("'trilat': ")[2].partition(",")[0]

			if wigle_ssid != "":
				print("\033[38;1;231m" + "SSID: " + "\033[0m" + wigle_ssid)
			if wigle_type == "infra":
				print("\033[38;1;231m" + "Type: " + "\033[0m" + "WiFi AP")
			elif wigle_type != "":
				print("\033[38;1;231m" + "Type: " + "\033[0m" + wigle_type)
			if vendor == "":
				print("\033[38;1;231m" + "Vendor: " + "\033[0m" + "UNKNOWN")
			else:
				print("\033[38;1;231m" + "Vendor: " + "\033[0m" + vendor)
			if wigle_country != "":
				print("\033[38;1;231m" + "CC: " + "\033[0m" + wigle_country)
			if wigle_city != "":
				print("\033[38;1;231m" + "City: " + "\033[0m" + wigle_city)
			if wigle_street != "" and wigle_housenumber != "None":
				print("\033[38;1;231m" + "Road: " + "\033[0m" + wigle_street + " " + wigle_housenumber)
			elif wigle_street != "" and wigle_housenumber == "None":
				print("\033[38;1;231m" + "Road: " + "\033[0m" + wigle_street)
			if wigle_long != "":
				print("\033[38;1;231m" + "Longitude: " + "\033[0m" + wigle_long)
			if wigle_lat != "":
				print("\033[38;1;231m" + "Latitude: " + "\033[0m" + wigle_lat)
		else:
			if vendor == "":
				print("\033[38;1;231m" + "Vendor: " + "\033[0m" + "UNKNOWN")
			else:
				print("\033[38;1;231m" + "Vendor: " + "\033[0m" + vendor)
	else:
		if vendor == "":
			print("\033[38;1;231m" + "Vendor: " + "\033[0m" + "UNKNOWN")
		else:
			print("\033[38;1;231m" + "Vendor: " + "\033[0m" + vendor)


def mode2_update_vendors():
	connection = net_check()

	if connection == True:
		req = requests.get("https://standards-oui.ieee.org/oui/oui.csv")

		if os.path.exists("vendor-db.csv"):
			os.remove("vendor-db.csv")

		with open("vendor-db.csv", "wb") as file:
			file.write(req.content)
	else:
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Can't fetch database... Is your internet connection working?")
		time.sleep(4)
		exit()

def mode3_update(i): # Track MAC address
	if platform == "linux": # Linux
		dBm_signal = int(os.popen("tshark -i " + interface + " -c 1 -T fields -e radiotap.dbm_antsignal ether src " + device + " 2> /dev/null | cut -d , -f 2-").read())
	elif platform == "darwin": # MacOS
		dBm_signal = int(os.popen("tshark -i " + interface + " -I -c 1 -T fields -e radiotap.dbm_antsignal ether src " + device + " 2> /dev/null | cut -d , -f 2-").read())

	signal_transfer(dBm_signal)

def mode4_deauth_frames(i): # Deauthentication Frames
	if platform == "linux":
		dBm_signal = int(os.popen("tshark -i " + interface + " -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype deauth\" 2> /dev/null | cut -d , -f 2-").read())
	elif platform == "darwin":
		dBm_signal = int(os.popen("tshark -i " + interface + " -I -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype deauth\" 2> /dev/null | cut -d , -f 2-").read())

	signal_transfer(dBm_signal)

def mode4_beacon_frames(i): # Beacon Frames
	if platform == "linux":
		dBm_signal = int(os.popen("tshark -i " + interface + " -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype beacon\" 2> /dev/null | cut -d , -f 2-").read())
	elif platform == "darwin":
		dBm_signal = int(os.popen("tshark -i " + interface + " -I -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype beacon\" 2> /dev/null | cut -d , -f 2-").read())

	signal_transfer(dBm_signal)

def mode4_probe_frames(i): # Probe Request Frames
	if platform == "linux":
		dBm_signal = int(os.popen("tshark -i " + interface + " -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype probe-req\" 2> /dev/null | cut -d , -f 2-").read())
	elif platform == "darwin":
		dBm_signal = int(os.popen("tshark -i " + interface + " -I -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype probe-req\" 2> /dev/null | cut -d , -f 2-").read())

	signal_transfer(dBm_signal)

def mode4_auth_frames(i): # Authentication Frames
	if platform == "linux":
		dBm_signal = int(os.popen("tshark -i " + interface + " -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype auth\" 2> /dev/null | cut -d , -f 2-").read())
	elif platform == "darwin":
		dBm_signal = int(os.popen("tshark -i " + interface + " -I -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype auth\" 2> /dev/null | cut -d , -f 2-").read())

	signal_transfer(dBm_signal)
 
def mode5_chase_detector(): # Track your tracker
	device_list = {}
	splt = "-"

	if platform == "linux":
		while True:
			probe = str(os.popen("tshark -i " + interface + " -c 1 -E separator=\"-\" -T fields -e frame.time_epoch -e wlan.sa_resolved -e wlan.sa -f \"type mgt subtype probe-req\" 2> /dev/null").read())
			time = probe.partition(splt)[0]
			device = probe.partition(splt)[2].partition(splt)[2].partition("\n")[0].upper()
			vendor = probe.partition(splt)[2].partition("_")[0]
			unknown = probe.partition(splt)[2]

			if device in device_list:
				last_seen = device_list.get(device)
				device_list[device] = time
				if float(time) - float(last_seen) > float(interval):
					if vendor == unknown:
						print("\033[38;5;206m" + "\n [!]" + "\033[0m" + "\033[38;1;231m" + " YOU'VE BEEN STALKED" + "\033[0m" + " by " + device)
					else:
						print("\033[38;5;206m" + "\n [!]" + "\033[0m" + "\033[38;1;231m" + " YOU'VE BEEN STALKED" + "\033[0m" + " by " + device + " (Vendor: " + vendor + ")")
					os.system("espeak \"eeeee\" 2> /dev/null > /dev/null")
			else:
				device_list[device] = time
				# print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " New device found: " + device)

	elif platform == "darwin":
		while True:
			probe = str(os.popen("tshark -i " + interface + " -c 1 -I -E separator=\"-\" -T fields -e frame.time_epoch -e wlan.sa_resolved -e wlan.sa -f \"type mgt subtype probe-req\" 2> /dev/null").read())
			time = probe.partition(splt)[0]
			device = probe.partition(splt)[2].partition(splt)[2].partition("\n")[0].upper()
			vendor = probe.partition(splt)[2].partition("_")[0]
			unknown = probe.partition(splt)[2]

			if device in device_list:
				last_seen = device_list.get(device)
				device_list[device] = time
				if float(time) - float(last_seen) > float(interval):
					if vendor == unknown:
						print("\033[38;5;206m" + "\n [!]" + "\033[0m" + "\033[38;1;231m" + " YOU'VE BEEN STALKED" + "\033[0m" + " by " + device)
					else:
						print("\033[38;5;206m" + "\n [!]" + "\033[0m" + "\033[38;1;231m" + " YOU'VE BEEN STALKED" + "\033[0m" + " by " + device + " (Vendor: " + vendor + ")")
					os.system("afplay /System/Library/Sounds/Sosumi.aiff")
			else:
				device_list[device] = time

def mode6_file_analytics(): # Analyse PCAP files
	print("\033[38;1;231m" + "\n\n  --- Access Points ---\n\nMAC Address\t\tSSID" + "\033[0m")
	os.system("tshark -r " + file + " -T fields -e wlan.sa -e wlan.ssid -Y \"wlan.fc.type_subtype == 8 and !(wlan.ssid == \\\"\\\")\" | awk '!seen[$0]++'") # Filter for Beacon frames from AP's

	print("\033[38;1;231m" + "\n\n  --- Stations ---\n\nMAC Address\t\tSearching for SSID" + "\033[0m")
	os.system("tshark -r " + file + " -T fields -e wlan.sa -e wlan.ssid -Y \"wlan.fc.type_subtype == 4 and !(wlan.ssid == \\\"\\\")\" | awk '!seen[$0]++'") # Filter for Probe Request from stations

def mode7_from_file(): # Track MAC address from file
	os.system("tshark -r " + file + " -T fields -e radiotap.dbm_antsignal -Y \"wlan.sa == " + device + "\" 2> /dev/null | cut -d , -f 2- > tmp_dBmonster.txt") # Filter Signals and save them to temporary file

	with open('tmp_dBmonster.txt') as dBm_signal:
		for line in dBm_signal:
			x_values.append(next(index))
			y_values.append(int(line))

	plt.plot(x_values, y_values, color='#ff9900')

### workflow

while True:
	os.system("clear")
	banner()

	if platform == "win32": # Windows
		print("\033[48;5;9m" + "\n [?] WTF!?\n*** ONLY LINUX OR MAC ***" + "\033[39m")
		exit()

	root_check()
	interface_list()

	mode = input("\033[38;1;231m" + "\n\n  --- OPTIONS ---\n\n[1]" + "\033[0m" + "\tRecon Of Wireless Landscape\n" + "\033[38;1;231m" + "[2]" + "\033[0m" + "\tMAC Address Information Gathering\n\n" + "\033[38;1;231m" + "[3]" + "\033[0m" + "\tRealtime MAC Address Tracking\n" + "\033[38;1;231m" + "[4]" + "\033[0m" + "\tAdvanced 802.11 Frame Tracking\n" + "\033[38;1;231m" + "[5]" + "\033[0m" + "\tDetection of Potential Stalkers\n\n" + "\033[38;1;231m" + "[6]" + "\033[0m" + "\tPCAP File Analytics\n" + "\033[38;1;231m" + "[7]" + "\033[0m" + "\tTracking From PCAP File\n\n" + "\033[38;1;231m" + "[0]" + "\033[0m" + "\tEXIT" + "\033[38;5;172m" + "\n\n  [*]" + "\033[0m" + " Choose Option: ")

	if mode == "1": # Recon
		interface = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Your WiFi interface: ")
		interface_check()
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Scanning the wireless landscape. This may take some time...")
		time.sleep(3.5)
		os.system("clear")
		mode1_recon()
		input("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Press the enter key to continue... (For tracking in realtime, remind the MAC Address and channel your target has!)")
		continue

	elif mode == "2":
		os.system("clear")
		banner()
		interface_list()
		if wigle_api_key == "":
			sub_mode = input("\033[38;1;231m" + "\n\n  --- MAC Address Information Gathering ---\n\n[1]" + "\033[0m" + "\tCollect Data Via OSINT Sources\n\n" + "\033[38;1;231m" + "[2]" + "\033[0m" + "\tEnter Your WiGLE API Token\n" + "\033[38;1;231m" + "[3]" + "\033[0m" + "\tUpdate/Download Vendor Database\n\n" + "\033[38;1;231m" + "[0]" + "\033[0m" + "\tRETURN" + "\033[38;5;172m" + "\n\n  [*]" + "\033[0m" + " Choose Option: ")
		else:
			sub_mode = input("\033[38;1;231m" + "\n\n  --- MAC Address Information Gathering ---\n\n[1]" + "\033[0m" + "\tCollect Data Via OSINT Sources\n\n" + "\033[38;1;231m" + "[2]" + "\033[0m" + "\tUpdate Your WiGLE API Token\n" + "\033[38;1;231m" + "[3]" + "\033[0m" + "\tUpdate/Download Vendor Database\n\n" + "\033[38;1;231m" + "[0]" + "\033[0m" + "\tRETURN" + "\033[38;5;172m" + "\n\n  [*]" + "\033[0m" + " Choose Option: ")
		if sub_mode == "0":
			continue
		elif sub_mode == "1":
			device = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " MAC Address: ")
			mode2_lookup(device)
			input("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Press the enter key to continue...")
		elif sub_mode == "2":
			if wigle_api_key == "":
				wigle_api_key = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Enter your *encoded* API Token from wigle.net/account: ")
			else:
				wigle_api_key = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Enter your new encoded API Token: ")
				os.remove("WiGLE.key")
			os.system("touch WiGLE.key && echo " + wigle_api_key + " > WiGLE.key")
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " API-Token saved...")
			time.sleep(3.5)
		elif sub_mode == "3":
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Updating the vendor database...")
			mode2_update_vendors()

	elif mode == "3": # Track MAC address
		interface = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Your WiFi interface: ")
		device = input("\033[38;5;172m" + "  [*]" + "\033[39m" + " MAC address to track: ")
		channel = input("\033[38;5;172m" + "  [*]" + "\033[39m" + " WiFi channel from MAC address to track: ")
		interface_check()
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Setting " + interface + " to channel " + channel + "...")
		set_channel()
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Searching for " + device + " on channel " + channel + "...")
		if platform == "linux": # Linux
			os.system("tshark -i " + interface + " -c 1 ether src " + device + " 2> /dev/null > /dev/null")
			os.system("espeak \"device detected\" 2> /dev/null > /dev/null") # Play sound message if found...
		elif platform == "darwin": # MacOS
			os.system("tshark -i " + interface + " -I -c 1 ether src " + device + " 2> /dev/null > /dev/null")
			os.system("say device detected") # Play sound message if found...
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " START TRACKING...\n")
		fig.canvas.manager.set_window_title("dBmonster: " + device) # Window title
		graph()
		animation = FuncAnimation(fig, mode3_update, 2000)
		plt.show()
		print("\033[38;1;231m" + "\nGOOD BYE!\n" + "\033[0m")
		exit()

	elif mode == "4": # Advanced 802.11 Frame Tracking
		os.system("clear")
		banner()
		interface_list()
		sub_mode = input("\033[38;1;231m" + "\n\n  --- Advanced 802.11 Frame Tracking ---\n\n[1]" + "\033[0m" + "\tDeauthentication Frames\n" + "\033[38;1;231m" + "[2]" + "\033[0m" + "\tAuthentication Frames\n" + "\033[38;1;231m" + "[3]" + "\033[0m" + "\tProbe Request Frames\n" + "\033[38;1;231m" + "[4]" + "\033[0m" + "\tBeacon Frames\n\n" + "\033[38;1;231m" + "[0]" + "\033[0m" + "\tRETURN" + "\033[38;5;172m" + "\n\n  [*]" + "\033[0m" + " Choose Option: ")
		if sub_mode == "0":
			continue
		interface = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Your WiFi interface: ")
		channel = input("\033[38;5;172m" + "  [*]" + "\033[39m" + " WiFi channel from frame activity: ")
		interface_check()
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Setting " + interface + " to channel " + channel + "...")
		set_channel()
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Searching for specific 802.11 frame on channel " + channel + "...")
		if sub_mode == "1":
			if platform == "linux":
				os.system("tshark -i " + interface + " -c 1 -f \"type mgt subtype deauth\" 2> /dev/null > /dev/null")
				os.system("espeak \"deauthentication frame detected\" 2> /dev/null > /dev/null") # Play sound message if found...
			elif platform == "darwin":
				os.system("tshark -i " + interface + " -I -c -f \"type mgt subtype deauth\" 2> /dev/null > /dev/null")
				os.system("say deauthentication frame detected") # Play sound message if found...
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " START TRACKING...\n")
			fig.canvas.manager.set_window_title("dBmonster: Deauthentication Frames") # Window title
			graph()
			animation = FuncAnimation(fig, mode4_deauth_frames, 2000)
			plt.show()

		elif sub_mode == "2":
			if platform == "linux":
				os.system("tshark -i " + interface + " -c 1 -f \"type mgt subtype auth\" 2> /dev/null > /dev/null")
				os.system("espeak \"authentication frame detected\" 2> /dev/null > /dev/null") # Play sound message if found...
			elif platform == "darwin":
				os.system("tshark -i " + interface + " -I -c 1 -f \"type mgt subtype auth\" 2> /dev/null > /dev/null")
				os.system("say authentication frame detected") # Play sound message if found...
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " START TRACKING...\n")
			fig.canvas.manager.set_window_title("dBmonster: Authentication Frames") # Window title
			graph()
			animation = FuncAnimation(fig, mode4_auth_frames, 2000)
			plt.show()

		elif sub_mode == "3":
			if platform == "linux":
				os.system("tshark -i " + interface + " -c 1 -f \"type mgt subtype probe-req\" 2> /dev/null > /dev/null")
				os.system("espeak \"probe request detected\" 2> /dev/null > /dev/null") # Play sound message if found...
			elif platform == "darwin":
				os.system("tshark -i " + interface + " -I -c 1 -f \"type mgt subtype probe-req\" 2> /dev/null > /dev/null")
				os.system("say probe request detected") # Play sound message if found...
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " START TRACKING...\n")
			fig.canvas.manager.set_window_title("dBmonster: Probe Request Frames") # Window title
			graph()
			animation = FuncAnimation(fig, mode4_probe_frames, 2000)
			plt.show()

		elif sub_mode == "4":
			if platform == "linux":
				os.system("tshark -i " + interface + " -c 1 -f \"type mgt subtype beacon\" 2> /dev/null > /dev/null")
				os.system("espeak \"beacon frame detected\" 2> /dev/null > /dev/null") # Play sound message if found...
			elif platform == "darwin":
				os.system("tshark -i " + interface + " -I -c 1 -f \"type mgt subtype beacon\" 2> /dev/null > /dev/null")
				os.system("say beacon frame detected") # Play sound message if found...
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " START TRACKING...\n")
			fig.canvas.manager.set_window_title("dBmonster: Beacon Frames") # Window title
			graph()
			animation = FuncAnimation(fig, mode4_beacon_frames, 2000)
			plt.show()
		print("\033[38;1;231m" + "\nGOOD BYE!\n" + "\033[0m")
		exit()

	elif mode == "5": # Track your tracker
		interface = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Your WiFi interface: ")
		channel = input("\033[38;5;172m" + "  [*]" + "\033[39m" + " WiFi channel to use (not that important here): ")
		interval = input("\033[38;5;172m" + "  [*]" + "\033[39m" + " Time spent with a device until the alarm (in seconds | 100s = 1.6min): ")
		interface_check()
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Setting " + interface + " to channel " + channel + "...")
		set_channel()
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Search for devices that have been sending probe requests for over " + interval + " seconds...")
		mode5_chase_detector()
		continue

	elif mode == "6": # PCAP File Analytics
		file = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Enter path to PCAP file: ")
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Analyzing file " + file + "...")
		mode6_file_analytics()
		input("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Press the enter key to continue... (For tracking from file, remind the MAC Address your target has!)")
		continue

	elif mode == "7": # Track MAC address from file
		file = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Enter path to PCAP file: ")
		device = input("\033[38;5;172m" + "  [*]" + "\033[39m" + " MAC address to track: ")
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Searching for " + device + " in file " + file + "...")
		fig.canvas.manager.set_window_title("dBmonster: " + device) # Window title
		ax.set_xlabel('Amount of recieved packets') # Graph x axis label text
		ax.set_ylabel('Signal strength [dBm]') # Graph y axis label text
		ax.xaxis.label.set_color('#3f64d9') # Graph x axis label color
		ax.yaxis.label.set_color('#3f64d9') # Graph y axis label color
		graph()
		mode7_from_file()
		plt.show()
		if os.path.exists("tmp_dBmonster.txt"): # If it exists, delete temporary file
			os.remove("tmp_dBmonster.txt")
		continue

	elif mode == "0": # EXIT
		if os.path.exists("tmp_dBmonster.txt"): # If it exists, delete temporary file
			os.remove("tmp_dBmonster.txt")

		print("\033[38;1;231m" + "\nGOOD BYE!\n" + "\033[0m")
		exit()