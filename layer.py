# -*- coding: utf-8 -*-
import os, subprocess, time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.OUT)

from yowsup.layers.interface                           import YowInterfaceLayer					#Reply to the message
from yowsup.layers.interface                           import ProtocolEntityCallback			#Reply to the message
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity			#Body message
from yowsup.layers.protocol_presence.protocolentities  import AvailablePresenceProtocolEntity   #Online
from yowsup.layers.protocol_presence.protocolentities  import UnavailablePresenceProtocolEntity #Offline
from yowsup.layers.protocol_presence.protocolentities  import PresenceProtocolEntity			#Name presence
from yowsup.layers.protocol_chatstate.protocolentities import OutgoingChatstateProtocolEntity	#is writing, writing pause
from yowsup.common.tools                               import Jid 								#is writing, writing pause

#Log, but only creates the file and writes only if you kill by hand from the console (CTRL + C)
#import sys
#class Logger(object):
#    def __init__(self, filename="Default.log"):
#        self.terminal = sys.stdout
#        self.log = open(filename, "a")
#
#    def write(self, message):
#        self.terminal.write(message)
#        self.log.write(message)
#sys.stdout = Logger("/1.txt")
#print "Hello world !" # this is should be saved in yourlogfilename.txt
#------------#------------#------------#------------#------------#------------

allowedPersons=['ALLOWEDNUMBER 1','ALLOWEDNUMBER 2'] #Filter the senders numbers
ap = set(allowedPersons)



name = "NAMEPRESENCE"
filelog = "/home/pi/yowsup/log/idontknow.log"
filelog2 = "/home/pi/yowsup/logs/online_offline.log"

class EchoLayer(YowInterfaceLayer):
    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        if messageProtocolEntity.getType() == 'text':
            time.sleep(0.1)
            self.toLower(messageProtocolEntity.ack()) #Set received (double v)
            time.sleep(0.1)
            self.toLower(PresenceProtocolEntity(name = name)) #Set name Presence
            time.sleep(0.1)
            self.toLower(AvailablePresenceProtocolEntity()) #Set online
            time.sleep(0.1)
            self.toLower(messageProtocolEntity.ack(True)) #Set read (double v blue)
            time.sleep(0.1)
            self.toLower(OutgoingChatstateProtocolEntity(OutgoingChatstateProtocolEntity.STATE_TYPING, Jid.normalize(messageProtocolEntity.getFrom(False)) )) #Set is writing
            time.sleep(0.1)
            self.toLower(OutgoingChatstateProtocolEntity(OutgoingChatstateProtocolEntity.STATE_PAUSED, Jid.normalize(messageProtocolEntity.getFrom(False)) )) #Set no is writing
            time.sleep(0.1)
            self.onTextMessage(messageProtocolEntity) #Send the answer

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        print entity.ack()
        self.toLower(entity.ack())

    def onTextMessage(self,messageProtocolEntity):
        namemitt   = messageProtocolEntity.getNotify()
        message    = messageProtocolEntity.getBody().lower()
        recipient  = messageProtocolEntity.getFrom()
        textmsg    = TextMessageProtocolEntity

        #For a break to use the character \n
        #The sleep you write so #time.sleep(1)

        if messageProtocolEntity.getFrom(False) in ap:
            if message == 'hi':
                answer = "Hello "+namemitt+" how are you? " 
                self.toLower(textmsg(answer, to = recipient ))
                print answer

            elif message == 'hey':
                answer = "Hey "+namemitt+" !"
                self.toLower(textmsg(answer, to = recipient ))
                print answer

	    elif message == 'shutdown':
		answer = "Ok "+namemitt+"."
                self.toLower(textmsg(answer, to = recipient ))
                print answer
                time.sleep(1)
                self.toLower(UnavailablePresenceProtocolEntity())
                time.sleep(0.1)
                os.system('shutdown -h 0')

            elif message == 'temp':
                t=float(subprocess.check_output(["/opt/vc/bin/vcgencmd measure_temp | cut -c6-9"], shell=True)[:-1])
                ts=str(t)
                answer = 'My temperature is'+ts+' °C'
                self.toLower(textmsg(answer, to = recipient ))
                print answer

            elif message == 'reboot':
                answer = "Ok "+namemitt+", reboot..."
                self.toLower(textmsg(answer, to = recipient ))
                print answer
                time.sleep(3)
                self.toLower(UnavailablePresenceProtocolEntity())
                time.sleep(2)
                os.system('reboot')

            elif message == 'on gpio14':
                GPIO.output(14, True) # Pin 2 in up
                answer = "Ok, il GPIO14 è su true"
                self.toLower(textmsg(answer, to = recipient ))
                print answer

            elif message == 'off gpio14':
                GPIO.output(14, False) # Pin 2 in down
                answer = "Ok, il GPIO14 è su false"
                self.toLower(textmsg(answer, to = recipient ))
                print answer

#ERROR
	    else:
		answer = "I dont know, what ("+message+") means."
		self.toLower(textmsg(answer, to = recipient))
                print answer
		out_file = open(filelog,"a")
	        out_file.write("------------------------"+"\n"+"Sender:"+"\n"+namemitt+"\n"+"Number sender:"+"\n"+recipient+"\n"+"Message text:"+"\n"+message+"\n"+"------------------------"+"\n"+"\n")
	        out_file.close()


