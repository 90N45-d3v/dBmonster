![dBmonster-bat-banner](https://user-images.githubusercontent.com/79598596/181930036-ebc45598-d6dd-4291-9c4b-05f7b03bde38.png)
<p align="center">
 <img src="https://img.shields.io/badge/Made%20with-Python-blue">
 <img src="https://img.shields.io/github/license/90N45-d3v/dBmonster.svg">
 <img src="https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg">
 <br>
 <img src="https://img.shields.io/badge/-Linux-lightblue">
 <img src="https://img.shields.io/badge/-MacOS-lightgrey">
</p>

<p align="center">
 With dBmonster you are able to scan for nearby WiFi devices and track them trough the signal strength (<a href="https://en.m.wikipedia.org/wiki/DBm">dBm</a>) of their sent packets (sniffed with <a href="https://tshark.dev/setup/about/#what-is-tsharkdev">TShark</a>).
 These dBm values will be plotted to a graph with <a href="https://matplotlib.org/">matplotlib</a>.
 It can help you to identify the exact location of nearby WiFi devices (use a <a href="https://simplewifi.com/blogs/news/omni-directional-vs-antennadirectional-antenna">directional WiFi antenna</a> for the best results) or to find out how your <a href="https://www.makeuseof.com/10-diy-long-range-wi-fi-antennas-you-can-make-at-home/">self made antenna</a> works the best (<a href="https://help.ui.com/hc/en-us/articles/115012664088-UniFi-Introduction-to-Antenna-Radiation-Patterns">antenna radiation patterns</a>).
</p>

## Table of contents
- [Features on Linux and MacOS](https://github.com/90N45-d3v/dBmonster#features-on-linux-and-macos)
- [Installation](https://github.com/90N45-d3v/dBmonster#installation)
- [Has been successfully tested  on...](https://github.com/90N45-d3v/dBmonster#has-been-successfully-tested--on)
- [Troubleshooting for MacOS](https://github.com/90N45-d3v/dBmonster#troubleshooting-for-macos)
- [Working on...](https://github.com/90N45-d3v/dBmonster#working-on)
- [Additional information](https://github.com/90N45-d3v/dBmonster#additional-information)

## Features on Linux and MacOS

| Feature | Linux | MacOS |
| ------- | --------- | --------- |
| Listing WiFi interfaces | ✅ | ✅ |
| Track & scan on 2.4GHz | ✅ | ✅ |
| Track & scan on 5GHz | ✅ | ✅ |
| Scanning for AP | ✅ | ✅ |
| Scanning for STA | ✅ | |
| Beep when device found | ❓ | ✅ |

## Installation
````
git clone https://github.com/90N45-d3v/dBmonster
cd dBmonster

# Install required tools (On MacOS without sudo)
sudo python requirements.py

# Start dBmonster
sudo python dBmonster.py
````

## Has been successfully tested  on...

| Platform 💻 | WiFi Adapter 📡 |
| ------- | --------- |
| Kali Linux | ALFA AWUS036NHA, DIY [Bi-Quad WiFi Antenna](https://www.instructables.com/Bi-Quad-WiFi-Antenna/) |
| MacOS Monterey | Internal card 802.11 a/b/g/n/ac (MBP 2019) |
###### * *should work on any MacOS or Debian based system and with every WiFi card that supports monitor-mode*

## Troubleshooting for MacOS
Normally, you can only enable monitor-mode on the internal wifi card from MacOS with the [airport](https://osxdaily.com/2007/01/18/airport-the-little-known-command-line-wireless-utility/) utility from Apple. Somehow, wireshark (or here TShark) can enable it too on MacOS. Cool, but because of the MacOS system and Wireshark’s workaround, there are many issues running dBmonster on MacOS. After some time, it could freeze and/or you have to stop dBmonster/Tshark manually from the CLI with the ``ps`` command. If you want to run it anyway, here are some helpful tips:

#### Kill dBmonster, if you can't stop it over the GUI

Look if there are any processes, named dBmonster, tshark or python:
````
sudo ps -U root
````
Now kill them with the following command:
````
sudo kill <PID OF PROCESS>
````

#### Stop monitor-mode, if it's enabled after running dBmonster

````
sudo airport <WiFi INTERFACE NAME> sniff
````
Press control + c after a few seconds

###### * *Please contact me on [twitter](https://twitter.com/90N45), if you have anymore problems*

## Working on...
- Capture signal strength data for offline graphs 
- Generate graphs from normal wireshark.pcapng file
- Generate multiple graphs in one coordinate system

### Additional information 
- If the tracked WiFi device is out of range or doesn't send any packets, the graph stops plotting till there is new data. So don't panic ;)
- dBmonster wasn't tested on all systems... If there are any errors or something is going wrong, contact me.
- If you used dBmonster on a non-listed Platform or WiFi Adapter, please open an issue (with Platform and WiFi Adapter information) and I will add your specification to the README.md
