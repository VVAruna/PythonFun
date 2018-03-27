import sys
import os
import re
import logging
import datetime
import time
import glob
import shutil
import subprocess # Added for adding commands to console
from datetime import datetime
from tabulate import tabulate
from CameraController.device.camera import Camera
from CameraController.device.cameralog import CameraLog #Added to access camera logs from camera controller function


def logging_info(msg):
    logging.Logger(msg)
    print (msg)


def printCamStatus(ip, camera, data):

    camData=[]
    camData.append(ip)
    camData.append(camera.cp.props.get('Model'))
    camData.append(camera.cp.props.get('FirmwareVersion'))

    info = data.split('\n')
    # Print camera's uptime in human syntax
    info[0] = info[0].strip()
    info[0] = info[0].replace('Rel ', '')
    info[0] = info[0].replace('d', ' days ')
    info[0] = info[0].replace('h', ' hours ')
    info[0] = info[0].replace('m', ' minutes ')
    info[0] = re.sub(r'\ds', ' seconds ', info[0])

    camData.append(info[0])
    # Print camera load
    perf = info[2].split(',')
    cpu1=perf[0].strip()+","+perf[1].strip()
    cpu1=cpu1.replace('SysCpu ','')
    camData.append(cpu1)

    cpu2=perf[3].strip()
    cpu2=cpu2.replace('ProcCpu ','')
    camData.append(cpu2)

    mem=perf[4].strip().replace('SysMem ','')
    camData.append(mem)

    # Look for ValService performance
    for i in range(4, len(info)):
        match = re.search('ValService', info[i])
        if match:
            valService=info[i].strip()
            valService=valService.replace('-- ValService','')
            valService = re.sub(r'\d+\s\:\s','',valService)
            valService = re.sub(r'\sPrio\s.+','',valService)
            camData.append(valService)
            break
		
# Adding code to activate logger levels for capturing system logs and checking VAL Exception		
    camera.avigilon_client.client.service.ExecuteConsoleCmd(0, 'logger')
    camera.avigilon_client.client.service.ExecuteConsoleCmd(0, 'sll %s %s' % ("Vas.ValService", "DEBUG"))
    camera.avigilon_client.client.service.ExecuteConsoleCmd(0, 'exit')
    camera.avigilon_client.client.service.ExecuteConsoleCmd(0, 'vas')
    camera.avigilon_client.client.service.ExecuteConsoleCmd(0, 'evs %s' % ("10"))
    camera.avigilon_client.client.service.ExecuteConsoleCmd(0, 'exit')
    time.sleep(100)
	
    if camera.event_client is None:
       camera.create_event_client()

    if camera.avigilon_client is None:
       camera.create_avigilon_client()
		
    logs=camera.camera_log.get_system_logs()
	 
    err = "VAL::EXCEPTION"
    valException = "NONE"
    for data in logs:
	    if (data.find(err) != -1):
		    valException = data
	  	    break
   
    camData.append(valException)     
    return camData;

def main(argv):

    camFile = argv[1]
    cams=[]
    if (len(argv) != 2 ):
        logging.warning("Wrong arguments number. Configuration file full path has to be defined.")
        exit(-1)
    try:    #read and parse config file (IP,User,Passwd )

        f= open(camFile, 'rU')
        for line in f:
            line=line.strip()
            cams.append(line)
        f.close()

    except:
        logging.warning("Error in reading input file " + camFile )
        exit(-1)

    StatusTable=[]
    headers=["IP","Model","FW Version","Uptime","SysCpu","ProcCpu","SysMem","ValService","VAL EXCEPTION"]

    for cam in cams:
        credentials=cam.split(',')
        try: #Create camera object
            print "Try to create camera object with the following params: " + credentials[0] + "," + credentials[1] + "," + credentials[2]
            camObject=Camera(credentials[1],credentials[2],credentials[0])
    #    camera.cp.print_camera_properties()
        except:
            logging.warning( "Failed to create camera object ip: %s, user: %s, password: %s",credentials[0],credentials[1],credentials[2])
            continue

        try:
            gssOutput = camObject.avigilon_client.gss()
        except:
            logging.warning("Error in getting camera " + credentials[0] + "status " )
            continue
    #print gssOutput['Output']

        camData=printCamStatus(credentials[0], camObject, gssOutput['Output'])
        StatusTable.append(camData)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    #outfile = "C:\\Logs\cameras_"+timestamp+".txt"
    #f1=open(outfile,'w')
    #print >> f1, tabulate(StatusTable,headers,tablefmt="grid")
    print tabulate(StatusTable,headers,tablefmt="grid")



if __name__ == "__main__":
    main(sys.argv)