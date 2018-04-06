from serial import Serial
from threading import Thread
from Queue import Queue
from oauth2client.service_account import ServiceAccountCredentials
import signal
import sys
import json
import gspread
import datetime
import csv

class serialWatcher (Thread, Serial):
    def __init__(self, q, port = '/dev/ttyACM0', baudrate = 115200):
        Thread.__init__(self)
        Serial.__init__(self, port, baudrate)
        self.daemon = True
        self.queue = q
    def run(self):
        self.running = True
        while self.running:
            if self.in_waiting:
                line = self.readline()[0:-1];
                try:
                    data = json.loads(line)
                    self.queue.put(data)
                    # print "Sensor data in Queue"
                except:
                    # print "Invalid data discarted"
                    pass
    def stop(self):
        self.running = False

data_queue = Queue(10)
sensor = serialWatcher(q = data_queue)
sensor.start()

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def data_process(data):
    print ("Dato siendo procesado...\n")
    print (data)
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope) # El archivo client_secret.json debe ser generado en https://console.cloud.google.com/apis/
client = gspread.authorize(creds)
sheet = client.open("NOMBRE_DEL_GOOGLE_SHEET").sheet1 # Reemplazar NOMBRE_DEL_GOOGLE_SHEET por el nombre de su google sheet
index=1
filecsv = csv.writer(open("datos.csv","w"), delimiter=',',quoting=csv.QUOTE_ALL)
while True:
    if not data_queue.empty():
        data = data_queue.get()
        data_process(data)   
	timeact=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	row = [timeact,data['current'],data['voltage'],data['temperature']]
	index += 1
	sheet.append_row(row)
	filecsv.writerow(row)
