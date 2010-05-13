## exommp_demo.py
## Copyright (c) 2010 Mark Kohler; Hans Rempel
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
#
# Tested with python 2.6
'''Exercise Exosite XMPP API'''

import optparse
import random
import sys
import time
from time import strftime
import threading
import xmpp
import psutil
import ConfigParser
from Tkinter import *

global connection
global datasources
global options
global kill_threads
global threads_running
global outputBox

xmpp.Debug.Debug.colors['got']=xmpp.debug.color_blue
xmpp.Debug.Debug.colors['auth']=xmpp.debug.color_brown
xmpp.Debug.Debug.colors['warn']=xmpp.debug.color_brown
xmpp.Debug.Debug.colors['sent']=xmpp.debug.color_brown

#-------------------------------------------------------------------------------
def main():
#-------------------------------------------------------------------------------
    global connection
    global datasources
    global options
    global kill_threads
    global threads_running
    
    usage = '%prog username@example.com password CIK'
    parser = optparse.OptionParser(usage,
                                   description=__doc__)
    parser.add_option('-d', '--debug',
                      action='store_const',
                      const=['always', 'nodebuilder'],
                      default=[])
    options, args = parser.parse_args()
    config = ConfigureSystem(args)
    config.readconfiguration()
    
    kill_threads = {'cpu':'1','random':'1','sawtooth':'1'}
    threads_running = 0
    ExositeUI().mainloop()
    for k, v in kill_threads.iteritems():
      kill_threads[k] = 1
    
    while threads_running: continue
    
#-------------------------------------------------------------------------------
class ExositeUI( Frame ):
#-------------------------------------------------------------------------------
    def __init__( self ):
      global connection
      global datasources
      global outputBox
      
      Frame.__init__( self ) 
      
      sXmppServer = StringVar()
      sXmppUser = StringVar()
      sXmppPass = StringVar()
      sXmppCik = StringVar()
      sDSCpuRes = StringVar()
      sDSRanRes = StringVar()
      sDSSawRes = StringVar()
      sMonitoringStatus = StringVar()
      CpuEnable = IntVar()
      RanEnable = IntVar()
      SawEnable = IntVar()
      
      # Create a text frame to hold the text Label and the Entry widget
      self.master.title("Exosite XMPP Example")
      self.master["padx"]=40
      self.master["pady"]=20
      self.master.rowconfigure( 0, weight = 1 )
      self.master.columnconfigure( 0, weight = 1 )
      self.grid( sticky = W+E+N+S )
      self.font = ('Arial', 10)
      
      #Server Section
      row_number = 1
      serverLabel = Label(self, text="Server Parameters:", font = ('Arial', 10, 'bold'))
      serverLabel.grid( row = row_number, column = 1, pady = 5, sticky = W)
      
      #Commander
      row_number +=1
      xmppserverLabel = Label(self, text="Commander:")
      xmppserverLabel.grid( row = row_number, column = 1, sticky = E )
      xmppserverWidget = Entry(self, width = 50, textvariable = sXmppServer)
      xmppserverWidget.grid( row = row_number, column = 2, columnspan = 2 )  
      sXmppServer.set(connection['exosite_bot'])
      
      #User ID
      row_number +=1
      xmppuserLabel = Label( self, text = "User ID:" )
      xmppuserLabel.grid(row=row_number,column=1, sticky = E )
      xmppuserWidget = Entry( self, width = 50, textvariable = sXmppUser)
      xmppuserWidget.grid( row = row_number, column = 2, columnspan = 2 )  
      sXmppUser.set( connection['user_id'] )

      #Password
      row_number += 1
      xmpppassLabel = Label( self, text = "Password:" )
      xmpppassLabel.grid( row = row_number, column = 1, sticky = E )
      xmpppassWidget = Entry( self, show="*", width = 50, textvariable = sXmppPass )
      xmpppassWidget.grid( row = row_number, column = 2, columnspan = 2 )  
      sXmppPass.set( connection['password'] )

      #CIK
      row_number += 1
      xmppcikLabel = Label( self, text = "Device CIK:" )
      xmppcikLabel.grid( row = row_number, column = 1, sticky = E )
      xmppcikWidget = Entry( self, width = 50, textvariable = sXmppCik )
      xmppcikWidget.grid( row = row_number, column = 2, columnspan = 2 )  
      sXmppCik.set( connection['cik'] )
      
      #DataSources Section
      row_number += 1
      datasourcesLabel = Label( self, text = "DataSource Parameters:", font = ('Arial', 10, 'bold'))
      datasourcesLabel.grid( row = row_number, column = 1, pady = 5, sticky = W )
      
      #CPU Monitor
      row_number += 1
      dscpuLabel = Label( self, text = "CPU Monitor Resource #:" )
      dscpuLabel.grid( row = row_number, column = 1, sticky = E )
      dscpuResource = Entry( self, width = 5, textvariable = sDSCpuRes )
      dscpuResource.grid( row = row_number, column = 2, sticky = W )
      sDSCpuRes.set( datasources['cpu_resource'] )
      dscpuStartButton = Button( self, text = "Start", width = 8, command = lambda: CPUMonitor().start() )
      dscpuStartButton.grid( row = row_number, column = 2, padx = 5, pady = 5, sticky = E )
      dscpuStopButton = Button( self, text = "Stop", width = 8, command = lambda: CPUMonitor().stop() )
      dscpuStopButton.grid( row = row_number, column = 3, padx = 5, pady = 5, sticky = W )
      
      #Random Values
      row_number += 1
      dsranvalLabel = Label( self, text = "Random Values Resource #:")
      dsranvalLabel.grid( row = row_number, column = 1 )
      dsranvalResource = Entry( self, width = 5, textvariable = sDSRanRes)
      dsranvalResource.grid( row = row_number, column = 2, sticky = W )
      sDSRanRes.set( datasources['random_resource'] )
      dsranvalStartButton = Button( self, text = "Start", width = 8, command = lambda: RandomValues().start() )
      dsranvalStartButton.grid( row = row_number, column = 2, padx = 5, pady = 5, sticky = E )
      dsranvalStopButton = Button( self, text = "Stop", width = 8, command = lambda: RandomValues().stop() )
      dsranvalStopButton.grid( row = row_number, column = 3, padx = 5, pady = 5, sticky = W )
      
      #Sawtooth Wave
      row_number += 1
      dssawtoothLabel = Label( self, text = "Sawtooth Wave Resource #:" )
      dssawtoothLabel.grid( row = row_number, column = 1 )
      dssawtoothResource = Entry( self, width = 5, textvariable = sDSSawRes )
      dssawtoothResource.grid( row = row_number, column = 2, sticky = W )
      sDSSawRes.set( datasources['sawtooth_resource'] )
      dssawStartButton = Button( self, text = "Start", width = 8, command = lambda: SawtoothWave().start() )
      dssawStartButton.grid( row = row_number, column = 2, padx = 5, pady = 5, sticky = E )
      dssawStopButton = Button( self, text = "Stop", width = 8, command = lambda: SawtoothWave().stop() )
      dssawStopButton.grid( row = row_number, column = 3, padx = 5, pady = 5, sticky = W )
      
      #Use Value Buttons
      row_number += 1
      button0 = Button( self, text = "Apply Values Temporarily", width = 20, command = lambda: testUIConfig( sXmppServer.get(), sXmppUser.get(), sXmppPass.get(), sXmppCik.get(), sDSCpuRes.get(), sDSRanRes.get(), sDSSawRes.get() ) )
      button0.grid( row = row_number, column = 2, pady = 5, sticky = E )
      
      button1 = Button( self, text = "Apply Values to Config", width = 20, command = lambda: writeUIConfig( sXmppServer.get(), sXmppUser.get(), sXmppPass.get(),sXmppCik.get(), sDSCpuRes.get(), sDSRanRes.get(), sDSSawRes.get() ) )
      button1.grid( row = row_number, column = 3, pady = 5, sticky = E )
      
      #Log Window
      self.grid_columnconfigure( 4 , minsize = 400)
      scrollbar = Scrollbar( self )
      scrollbar.grid(row = 1, rowspan = row_number, column = 5, sticky = NS )
      outputBox = Text( self, yscrollcommand=scrollbar.set, width = 60 )
      outputBox['font']=('Arial', 8)
      scrollbar.config( command = outputBox.yview)
      outputBox.grid( row = 1, rowspan = row_number, column = 4, sticky = E)
      
      logtext("===================================================")
      logtext("www.exosite.com to setup an account and for more info.")
      logtext("setup your Exostie XMPP connection yet.  Go to")
      logtext("the boxes are blank to the left, you probably haven't")
      logtext("Defaults are stored in a file called 'options.cfg'. If")
      logtext("")
      logtext("the 'Apply Values...' buttons in order to use them.")
      logtext("When you change a parameter, you have to click one of")
      logtext("")
      logtext("to the right of the different Resources.")
      logtext("To log data, use the Start and Stop buttons located")
      logtext("Welcome!")
      logtext("===================================================")
      
#-------------------------------------------------------------------------------
class ConfigureSystem(object):
#-------------------------------------------------------------------------------
    def __init__(self, args):
        self.args = args
        
    def readconfiguration(self):
        global connection
        global datasources
        #defaults (over-ridden by config file if it exists and has entries)
        try: connection
        except NameError:
          connection = {'exosite_bot':'','user_id':'','password':'','cik':''}
        try: datasources
        except NameError:
          datasources = {'cpu_resource':'','random_resource':'','sawtooth_resource':''}
        
        config = ConfigParser.RawConfigParser()
        config.read('options.cfg')
        config_file_updates = False
        
        try:
          connection['user_id'],connection['password'],connection['cik'] = self.args
        except ValueError:
          print"Command line not specified, trying configuration file"
          for k, v in connection.iteritems():
            try:
              connection[k] = config.get('Connection',k)
            except:
              print "\"%s\" not found in config file." % k
              if not config.has_section('Connection'):
                config.add_section('Connection')
              config.set('Connection',k,v)
              config_file_updates = True
                
        for k, v in datasources.iteritems():
          try:
            datasources[k] = config.get('DataSources',k)
          except:
            print "\"%s\" not found in config file." % k
            if not config.has_section('DataSources'):
              config.add_section('DataSources')
            config.set('DataSources',k,v)
            config_file_updates = True
            
        if config_file_updates:
          with open('options.cfg', 'wb') as configfile:
            config.write(configfile)
    
    def writeconfiguration(self):
        global connection
        global datasources
        config = ConfigParser.RawConfigParser()
        config.read('options.cfg')
        for k, v in connection.iteritems():
            config.set('Connection',k,v)
        for k, v in datasources.iteritems():
          config.set('DataSources',k,v)
        with open('options.cfg', 'wb') as configfile:
          config.write(configfile)
    
#-------------------------------------------------------------------------------
def logtext(logstring):
#-------------------------------------------------------------------------------
  global outputBox
  outputBox.insert(0.0, "%s :: %s\n" % (strftime("%H:%M:%S"),logstring))
  
#-------------------------------------------------------------------------------
def writeUIConfig( Server, User, Pass, Cik, CpuRes, RanRes, SawRes ):
#-------------------------------------------------------------------------------
    global connection
    logtext( "%s :: Sawtooth Wave Resource Number" %  SawRes )
    logtext( "%s :: Random Value Resource Number" %  RanRes )
    logtext( "%s :: CPU Monitor Resource Number" %  CpuRes )
    logtext( "%s :: CIK" % Cik )
    logtext( "%s :: Password" %  Pass )
    logtext( "%s :: UserName" %  User )
    logtext( "%s :: Commander" %  Server )
    logtext("**********************************")
    logtext("Wrote Connection Values to Config File:")
    logtext("**********************************")
    datasources['cpu_resource'] = CpuRes
    datasources['random_resource'] = RanRes
    datasources['sawtooth_resource'] = SawRes
    connection['exosite_bot'] = Server
    connection['user_id'] = User
    connection['password'] = Pass
    connection['cik'] = Cik
    config = ConfigureSystem('')
    config.writeconfiguration()
    
#-------------------------------------------------------------------------------
def testUIConfig( Server, User, Pass, Cik, CpuRes, RanRes, SawRes ):
#-------------------------------------------------------------------------------
    global connection 
    logtext( "%s :: Sawtooth Wave Resource Number" %  SawRes )
    logtext( "%s :: Random Value Resource Number" %  RanRes )
    logtext( "%s :: CPU Monitor Resource Number" %  CpuRes )
    logtext( "%s :: CIK" % Cik )
    logtext( "%s :: Password" %  Pass )
    logtext( "%s :: UserName" %  User )
    logtext( "%s :: Commander" %  Server )
    logtext("**********************************")
    logtext("Using Temporary Connection Values:")
    logtext("**********************************")
    datasources['cpu_resource'] = CpuRes
    datasources['random_resource'] = RanRes
    datasources['sawtooth_resource'] = SawRes
    connection['exosite_bot'] = Server
    connection['user_id'] = User
    connection['password'] = Pass
    connection['cik'] = Cik
    
#-------------------------------------------------------------------------------
def connect ( identifier ):
#-------------------------------------------------------------------------------
    global connection
    global kill_threads
    global threads_running
    try:
      jid = xmpp.protocol.JID(connection['user_id'])
    except:
      print "Unable to establish XMPP connection"
      logtext("Unable to establish XMPP connection!")
      kill_threads[identifier] = 1
      if threads_running:
        threads_running -= 1
      return -1
    cl = xmpp.Client(jid.getDomain(), debug=options.debug)
    messenger = Messenger(cl)
    con = cl.connect()
    try:
      auth = cl.auth(jid.getNode(), connection['password'])
    except:
      print "Authentication failed"
      logtext("Authentication failed!")
      kill_threads[identifier] = 1
      if threads_running:
        threads_running -= 1
      return -1
    if not auth:
      print "Authentication failed"
      logtext("Authentication failed!")
      kill_threads[identifier] = 1
      if threads_running:
        threads_running -= 1
      return -1
    cl.RegisterHandler('message', messenger.message_handler)
    msg = xmpp.protocol.Message(to=connection['exosite_bot'],
                                body='setcik %s\n' % connection['cik'],
                                typ='chat')
    messenger.send(msg)
    if messenger.wait() == -1:
      print "Timed out waiting for response"
      logtext("Timed out waiting for response!")
      kill_threads[identifier] = 1
      if threads_running:
        threads_running -= 1
      return -1
      
    return messenger
#-------------------------------------------------------------------------------
class CPUMonitor ( threading.Thread ):
#-------------------------------------------------------------------------------
    def __init__ ( self ):
      self.identifier = "cpu"
      threading.Thread.__init__ ( self )
    
    def stop ( self ):
      global kill_threads
      if kill_threads[self.identifier] == 1:
        logtext("CPU Monitor already stopped")
        return
      else:
        logtext("Stopping CPU Monitor...")
      kill_threads[self.identifier] = 1
      
    def run ( self ):
      global connection
      global options
      global kill_threads
      global threads_running
      global datasources
      
      if not kill_threads[self.identifier]:
        logtext("CPU Monitor already started")
        return
      else:
        logtext("Starting CPU Monitor")
      
      threads_running += 1
      kill_threads[self.identifier] = 0
      self.messenger = connect(self.identifier)
      
      if self.messenger == -1:
        print "Could not connect."
        logtext("Could not connect!")
        return
      
      cds = CreateDataSource('cpu_time',datasources['cpu_resource'])
      self.messenger.send(cds.make_msg(), cds.message_handler)
      self.messenger.wait()
      self.writer = DataWriter(cds.get_resource_id())
      
      total = 0
      samples = 0
      while not kill_threads[self.identifier]:
        total += round(psutil.cpu_percent(),2)
        samples += 1
        time.sleep(1)
        if samples > 5:
          average = round(total/samples,2)
          self.messenger.send(self.writer.make_msg(average))
          self.messenger.wait()
          logtext("CPU Monitor wrote %i" % average)
          samples = 0
          total = 0
          
      if threads_running:
        threads_running -= 1
      
      logtext("CPU Monitor stopped.")

#-------------------------------------------------------------------------------
class RandomValues ( threading.Thread ):
#-------------------------------------------------------------------------------
    def __init__ ( self ):
      self.identifier = "random"
      threading.Thread.__init__ ( self )
      
    def stop ( self ):
      global kill_threads
      if kill_threads[self.identifier] == 1:
        logtext("Random Values already stopped")
        return
      else:
        logtext("Stopping Random Values...")
      kill_threads[self.identifier] = 1
      
    def run ( self ):
      global kill_threads
      global threads_running
      global datasources
      global connection
      global options
      
      if not kill_threads[self.identifier]:
        logtext("Random Values already started")
        return
      else:
        logtext("Starting Random Values")
      
      threads_running += 1
      kill_threads[self.identifier] = 0
      self.messenger = connect(self.identifier)
      
      if self.messenger == -1:
        print "Could not connect."
        logtext("Could not connect!")
        return
      
      cds = CreateDataSource('random_value',datasources['random_resource'])
      self.messenger.send(cds.make_msg(), cds.message_handler)
      self.messenger.wait()
      self.writer = DataWriter(cds.get_resource_id())
      
      while not kill_threads[self.identifier]:
        value = round(random.uniform(1, 52),2)
        self.messenger.send(self.writer.make_msg(value))
        self.messenger.wait()
        time.sleep(5)
        logtext( "Random Values wrote %i" % value)
      
      if threads_running:
        threads_running -= 1
      
      logtext("Random Values stopped.")
      
#-------------------------------------------------------------------------------
class SawtoothWave ( threading.Thread ):
#-------------------------------------------------------------------------------
    def __init__ ( self ):
      self.identifier = "sawtooth"
      threading.Thread.__init__ ( self )
      
    def stop ( self ):
      global kill_threads
      if kill_threads[self.identifier] == 1:
        logtext("Sawtooth Wave already stopped")
        return
      else:
        logtext("Stopping Sawtooth Wave...")
      kill_threads[self.identifier] = 1
      
    def run ( self ):
      global kill_threads
      global threads_running
      global datasources
      global connection
      global options
      
      if not kill_threads[self.identifier]:
        logtext("Sawtooth Wave already started")
        return
      else:
        logtext("Starting Sawtooth Wave")
      
      threads_running += 1
      kill_threads[self.identifier] = 0
      self.messenger = connect(self.identifier)
      
      if self.messenger == -1:
        print "Could not connect."
        logtext("Could not connect!")
        return
      
      cds = CreateDataSource('sawtooth_wave',datasources['sawtooth_resource'])
      self.messenger.send(cds.make_msg(), cds.message_handler)
      self.messenger.wait()
      self.writer = DataWriter(cds.get_resource_id())
      
      operator = 1
      value = 0
      while not kill_threads[self.identifier]:
        value = value + operator
        self.messenger.send(self.writer.make_msg(value))
        self.messenger.wait()
        time.sleep(2)
        logtext( "Sawtooth wrote %i" % value)
        if value == 0 or value > 4: operator *= -1
        
      if threads_running:
        threads_running -= 1
      
      logtext("Sawtooth Wave stopped.")
      
#-------------------------------------------------------------------------------
class Messenger(object):
#-------------------------------------------------------------------------------
    def __init__(self, client):
        self.wait_for_response = False
        self.callback = None
        self.client = client

    def wait(self):
        start = time.clock()
        while self.wait_for_response:
            if time.clock() - start > 10: return -1
            if not self.client.Process(1):
                print 'disconnected'
                break

    def message_handler(self, con, event):
        response = event.getBody()
        if self.callback:
            self.callback(response)
        else:
            if response.find("ok") == -1:
              logtext("ERROR: XMPP response: %s" % response)
        self.wait_for_response = False

    def send(self, message, callback=None):
        self.wait_for_response = True
        self.callback = callback
        self.client.send(message)
        
#-------------------------------------------------------------------------------
class CreateDataSource(object):
#-------------------------------------------------------------------------------
    def __init__(self, desc1, desc2):
        global connection
        self.resource_id = desc2
        body = 'rdscreate %s %s 1 na 0' % (desc1, self.resource_id)
        self.msg = xmpp.protocol.Message(connection['exosite_bot'], body, typ='chat')

    def make_msg(self):
        return self.msg

    def message_handler(self, response):
        self.remote_id = response
        if response.find("error") != -1:
          if response.find("duplicate") != -1:
            print "Duplicate DataSource, continuing."
          else:
            print "CreateDataSource Error: response: %s" % response
        else:
          print "CreateDataSource: response: %s" % response

    def get_resource_id(self):
        return self.resource_id

    def get_remote_id(self):
        return self.remote_id

#-------------------------------------------------------------------------------
class DataWriter(object):
#-------------------------------------------------------------------------------
    def __init__(self, resource_id):
        self.resource_id = resource_id

    def make_msg(self, data_value):
        global connection
        body = 'write %s %s' % (self.resource_id, data_value)
        return xmpp.protocol.Message(connection['exosite_bot'], body, typ='chat')

#-------------------------------------------------------------------------------
class DataReader(object):
#-------------------------------------------------------------------------------
    def __init__(self, remote_id):
        self.remote_id = remote_id

    def make_msg(self):
        global connection
        body = 'rdsread %s 100' % self.remote_id
        return xmpp.protocol.Message(connection['exosite_bot'], body, typ='chat')

if __name__ == '__main__':
    sys.exit(main())
