import mysql.connector as mariadb #pip install
import json, urllib
from datetime import datetime


#select operator probobly isnt needed
def exicuteNMSQuery(cursorLibrenms, query):
	##########################################
	# this module executes the SQL commands
	##########################################
	
	#this is so the results from the processors cores can be returned
	
	cursorLibrenms.execute(query)
	#check if database is being entered
	


def getDeviceConig ():
	##############################################
	# this module is to load the settings from the devices.json file, the file is used to tell the script
	# what to search for in the SQL database or sensor as we only want to target specific sets of information
	##############################################
	
	#loading devices.json into a variable
	dashboard = json.load(open('/home/admin/Jay/dasboard.json')) #change this path to where dashboard file is saved
	count = 0
	
	#this is creating a while loop that will run untill every device listed in devices.json has been loaded into and the calls other
	#modules to exicute the SQL commands
	
	#FORMAT
	#dashboard["devices"]["location in array"]["variable name"]
	#collecting from json file
	
	dashboardtype = dashboard["System"][0]["JSONGenTime"]
	while count < len(dashboard["devices"]): #rename devices to dashboard
		#this is getting the device type so that the script knows what feilds to expect within the json file
		#this is needed because if you try to load a feild that doesnt exist the script will crash
		devicetype = devices["devices"][count]["type"]
		#only looking for config items that are relivant to mesuring performace
		
		if devicetype == "performance":
			memPercUsed = dashboard["devices"][count]["memPercUsed"] #proper format to retrieve variable 
			#from json
			genvar = memPercUsed
			QueryInsert(dashboardtype, genvar)
			#used to identify device in LibreNMS database to target
			device_id = devices["devices"][count]["device_id"]
			#used to specify what memory is wanted to be mesured (libreNMS can show page files
			#etc that may not be wanted to be display
			mempool_id = devices["devices"][count]["mempool_id"]
			#used to specifiy the patition that you want to show because LibreNMS will show thinks like boot partions
			storage_id = devices["devices"][count]["storage_id"]
			
			#parsing the variable to another function to exicute the SQL commands
			QueryInsert(memPercUsed) #change this method to insert query
			
		
		
		elif devicetype == "network":
			
			QueryInsert(device_id, port_ids)

		elif devicetype == "environmental":
			#getting eviromental sensors ip and file name to create the URL call
			device_ip = devices["devices"][count]["ip"]
			fileName = devices["devices"][count]["fileName"]
			
			#parsing the variable to another function to exicute the web calls
			QueryInsert(device_ip, fileName)
		
		elif devicetype == "power":
			device_id = devices["devices"][count]["device_id"]
			
			#parsing the variable to another function to exicute the SQL commands
			QueryInsert(device_id)
		
		#incrementing the count so that it will open the next in device.json file
		count += 1
	


#########################################MAIN###################################

#this is the method to insert
def QueryInsert (device_id):
	query = ("select sensor_current from test where device_id = ") + (device_id) #change to insert sql command
	currentUsed = exicuteNMSQuery(cursorLibrenms, query) #connection to database, change to test
	
	#NMS only returns the current so we do current * voltage to get watts
	watts = float(currentUsed[0]) * 240
	
	#this is to add data to the variable dashboard which will be saved to dashboard.json
	dashboard["devices"].append({
	"type":"power",
	"currentUsedAmps": 	currentUsed[0],
	"Watts": watts,
	})
	


#conntection to LibreNMS database:
sessionConnectionLibrenms = mariadb.connect(user='admin',
                              password='',
                              host='localhost',
                              database='test')
cursorLibrenms = sessionConnectionLibrenms.cursor()


#Close Connection to LibreNMS Database
cursorLibrenms.close()
sessionConnectionLibrenms.close()
#connect to test db using dbeaver