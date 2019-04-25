
# IBM_MICROSCOPE

- [Schematic](#Schematic)
- [Setup and Use](#Setup-and-Use)
- [Changing Startup Settings](#Changing-Startup-Settings)


## Schematic
![pics](pics/pic.png)

~~~bash
.
├── Installation.docx
├── Pump_Code
│   ├── config.txt
│   ├── configuration.py
│   ├── dropbox_upload_delete.py
│   ├── microscope.py
│   └── pump_system.py
├── README.docx
├── README.md
├── download_delete.py
└── pics
    └── pic.png
~~~

## Setup and Use
There is no setup needed to use the device. The program is automatically run on startup.<br />
Give about 1 minute after starting Raspberry Pi to see pump start working.

## Changing Startup Settings
In terminal start at home folder.<br />
Use preferred text editor to view /etc/rc.local<br />
In the lines directly above “exit 0” add commands to run program, below is an example<br />
Example: sudo python sample_code.py<br />
Tip: if your program needs to access resources that don’t exist in /home, cd into sample code source folder in the line directly before run command<br />
If program runs continuously, add ampersand to end of run command to run program on separate thread<br />
Example: sudo python sample_code.py &<br />
