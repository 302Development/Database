import mysql.connector as mariadb
import json, urllib
from datetime import datetime

#select operator probobly isnt needed
def exicuteNMSQuery(cursorLibrenms, query):
	##########################################
	# this module exicutes the SQL commands
	##########################################
	
	#this is so the results from the processors cores can be returned
	result = []
	cursorLibrenms.execute(query)
	for (value) in cursorLibrenms:
		print(value[0])
		result.append(value[0])
	return(result)
	
	
	
def saveDashboardDOTJSON():
	#########################################
	# this module is to save the JSON file
	##########################################
	with open('/opt/dashboard/html/dashboard.json', 'w') as outfile:
		json.dump(dashboard, outfile)

def getDashboardDOTJSON():
	#########################################
	# this module is to create the structure of the JSON file
	##########################################
	dashboard ={"devices":[], "System":[{"JSONGenTime": str(datetime.now())}]}
	return(dashboard)

def QueryEnviromental(device_ip, fileName):
	###############################################
	# this moduel is to send a HTTP request to the sensors and pull down the JSON
	# file.
	###############################################
	
	#this builds the URL to call the sensors json file
	url = ("http://") + (device_ip) + ("/") + (fileName)
	response = urllib.urlopen(url)
	enviormentalData = json.loads(response.read())
	
	#this is to add data to the variable dashboard which will be saved to dashboard.json
	dashboard["devices"].append({
	"type":"enviormental",
	"CO2": enviormentalData["C02"],
	"TVOC": enviormentalData["TVOC"],
	"temp": enviormentalData["temp"]
	})
	
	
def QueryPerformanceLibreNMS (device_id, mempool_id, storage_id): 
	#########################################
	# this module is to query the database for memory, cpu and storage use
	##########################################
	
	
	#system name (input device_id)
	print("sysname = ")
	query = ("SELECT sysName FROM librenms.devices WHERE device_id= ") + (device_id)
	sysName = exicuteNMSQuery(cursorLibrenms, query)
	
	
	#OS of device (input device_id)
	print("OS = ")
	query = ("SELECT OS FROM librenms.devices WHERE device_id= ") + (device_id)
	OS = exicuteNMSQuery(cursorLibrenms, query)
	
	#Uptime of device (input device_id)
	print("uptime = ")
	query = ("SELECT uptime FROM librenms.devices WHERE device_id= ") + (device_id)
	upTime = exicuteNMSQuery(cursorLibrenms, query)
	upTime = int((((upTime[0]) / 60) / 60) / 24)
	upTime = round(upTime)
	#Percentage of processor use (input device_id)
	print("% of Processor use = ")
	query = ("SELECT processor_usage FROM librenms.processors WHERE device_id= ") + (device_id)
	Proc = exicuteNMSQuery(cursorLibrenms, query)

	
	#memory size (input inputs device_id, mempool_id
	print("mem size = ")
	query = ("select mempool_total from librenms.mempools where mempool_id = ") + (mempool_id) + (" and device_id = ") + (device_id)
	memSize = exicuteNMSQuery(cursorLibrenms, query)
	#converting from bytes to GB
	memSize = float(memSize[0]) / 1073741824
	#needed because it rounds oddly
	memSize = round(memSize)

	#memeory used (input device_id, mempool_id)
	print("% of mem free = ")
	query = ("select mempool_perc from librenms.mempools where mempool_id = ") + (mempool_id) + (" and device_id = ") + (device_id)
	memPercUsed = exicuteNMSQuery(cursorLibrenms, query)
								  
	#storage size (input device_id, storage_id)
	print("storage size = ")
	query = ("select storage_size from librenms.storage where device_id = ") + (device_id) + (" and storage_id = ") + (storage_id)
	storageSize = exicuteNMSQuery(cursorLibrenms, query)
	#converting from bytes to GB
	storageSize = float(storageSize[0]) / 1073741824
	storageSize = round(storageSize)
	
	#storage percentage used (input device_id, storage_id)
	print("% of storage used = ")
	query = ("select storage_perc from librenms.storage where device_id = ") + (device_id) + (" and storage_id = ") + (storage_id)
	storagePercUsed = exicuteNMSQuery(cursorLibrenms, query)
	
	
	#this is used to update the JSON variable based on information that has been resturned from the SQL commmands
	dashboard["devices"].append({
	"type":"performance",
	"sysName": sysName[0],
	"OS": OS[0],
	"upTimeDays": upTime,
	"procPercPerCore": Proc,
	"memSizeGB": memSize,
	"memPercUsed": memPercUsed[0],
	"storageSizeGB": storageSize,
	"storagePercUsed": storagePercUsed[0]
	})
	
								  
def QueryPowerLibreNMS (device_id):
	print("current used = ")
	query = ("select sensor_current from librenms.sensors where device_id = ") + (device_id)
	currentUsed = exicuteNMSQuery(cursorLibrenms, query)
	
	#NMS only returns the current so we do current * voltage to get watts
	watts = float(currentUsed[0]) * 240
	
	#this is to add data to the variable dashboard which will be saved to dashboard.json
	dashboard["devices"].append({
	"type":"power",
	"currentUsedAmps": 	currentUsed[0],
	"Watts": watts,
	})
	

def QueryNetworkLibreNMS(device_id, port_ids):
	#check poll time of ports
	query = ("SELECT poll_period from librenms.ports WHERE port_id = ") + (port_ids[0]) + (" and device_id = ") + (device_id)
	pollTime = exicuteNMSQuery(cursorLibrenms, query)
	
	
	#this is used to add all of the port values togeather if there are multiple in the port_ids array
	portCount = 0
	print ("network ports")
	print (port_ids)
	outOctDeltaTotal = 0
	inOctDeltaTotal = 0
	while portCount < len(port_ids):
				#loops throught the size of the array to add all of the upload and download values togeather
				#if there is only one it will only go through once
				query = ("SELECT ifInOctets_delta from librenms.ports WHERE port_id = ") + (port_ids[portCount]) + (" and device_id = ") + (device_id)
				inOctDelta = exicuteNMSQuery(cursorLibrenms, query)
				inOctDeltaTotal = inOctDeltaTotal + float(inOctDelta[0])
				
				query = ("SELECT ifOutOctets_delta from librenms.ports WHERE port_id = ") + (port_ids[portCount]) + (" and device_id = ") + (device_id)
				outOctDelta = exicuteNMSQuery(cursorLibrenms, query)
				outOctDeltaTotal = outOctDeltaTotal + float(outOctDelta[0])
				
				portCount = portCount + 1
	MbsIn = str(((((inOctDeltaTotal) / pollTime[0]) * 8) /1000) /1000)
	MbsOut = str(((((outOctDeltaTotal) / pollTime[0]) * 8) /1000) /1000)
	
	#saving data to JSON file
	dashboard["devices"].append({
	"type":"network",
	"Mb/sIn": MbsIn,
	"Mb/sOut": MbsOut
	})

def getDeviceConig ():
	##############################################
	# this module is to load the settings from the devices.json file, the file is used to tell the script
	# what to search for in the SQL database or sensor as we only want to target specific sets of information
	##############################################
	
	#loading devices.json into a variable
	devices = json.load(open('/home/admin/Jay/devices.json'))
	count = 0
	
	#this is creating a while loop that will run untill every device listed in devices.json has been loaded into and the calls other
	#modules to exicute the SQL commands
	while count < len(devices["devices"]):
		#this is getting the device type so that the script knows what feilds to expect within the json file
		#this is needed because if you try to load a feild that doesnt exist the script will crash
		devicetype = devices["devices"][count]["type"]
		#only looking for config items that are relivant to mesuring performace
		if devicetype == "performance":
			#used to identify device in LibreNMS database to target
			device_id = devices["devices"][count]["device_id"]
			#used to specify what memory is wanted to be mesured (libreNMS can show page files
			#etc that may not be wanted to be display
			mempool_id = devices["devices"][count]["mempool_id"]
			#used to specifiy the patition that you want to show because LibreNMS will show thinks like boot partions
			storage_id = devices["devices"][count]["storage_id"]
			
			#parsing the variable to another function to exicute the SQL commands
			QueryPerformanceLibreNMS(device_id, mempool_id,storage_id)
		
		
		elif devicetype == "network":
			#getting device ID for query
			device_id = devices["devices"][count]["device_id"]
			#getting array of ports to add or if single just read that portt
			port_ids = devices["devices"][count]["port_ids"]
			
			#parsing the variable to another function to exicute the SQL commands
			QueryNetworkLibreNMS(device_id, port_ids)

		elif devicetype == "environmental":
			#getting eviromental sensors ip and file name to create the URL call
			device_ip = devices["devices"][count]["ip"]
			fileName = devices["devices"][count]["fileName"]
			
			#parsing the variable to another function to exicute the web calls
			QueryEnviromental(device_ip, fileName)
		
		elif devicetype == "power":
			device_id = devices["devices"][count]["device_id"]
			
			#parsing the variable to another function to exicute the SQL commands
			QueryPowerLibreNMS(device_id)
		
		#incrementing the count so that it will open the next in device.json file
		count += 1
	


#########################################MAIN###################################


#conntection to LibreNMS database:
sessionConnectionLibrenms = mariadb.connect(user='admin',
                              password='',
                              host='localhost',
                              database='librenms')
cursorLibrenms = sessionConnectionLibrenms.cursor()

dashboard = getDashboardDOTJSON()
getDeviceConig ()
saveDashboardDOTJSON()

#Close Connection to LibreNMS Database
cursorLibrenms.close()
sessionConnectionLibrenms.close()
