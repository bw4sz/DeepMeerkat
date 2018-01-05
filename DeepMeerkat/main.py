#!/usr/bin/env python

import os

#export pbr version for tensorflow user
os.environ["PBR_VERSION"]='3.1.1'

import traceback
import sys
from functools import partial

#DeepMeerkat
import Meerkat
import CommandArgs

from pathlib import Path

#OS specific path home
if os.name=="nt":
     home = str(Path.home())
else:
     home=os.path.expanduser("~")

#Entry Point

if __name__ == "__main__":
     print(sys.argv)
     
     #Read in system arguments if they exist
     #if system arg, command line version, skip the GUI
     if len(sys.argv)>= 2:
          
          #Peek at the args to see if threaded, if not, we can make a new tensorflow session
          args=CommandArgs.CommandArgs(argv=None) 
     
          if not args.threaded:
               if args.tensorflow:   
                    #add tensorflow flag for kivy
                    tensorflow_status="Loading"                  
                    sess=start_tensorflow(args)
     
          #Create queue of videos to run
          queue=create_queue(args=args)
     
          if args.threaded:
               from multiprocessing.dummy import Pool
               pool = Pool(3)         
               mapfunc = partial(Meerkat.DeepMeerkat, args=args)        
               results = pool.map(mapfunc, queue)
               pool.close()
               pool.join()
          else:
               for vid in queue:
                    results=Meerkat.DeepMeerkat(vid=vid,args=args,sess=sess)
              
     else:            
          #run GUI
          from kivy.app import App
          from kivy.uix.scatter import Scatter
          from kivy.uix.label import Label
          from kivy.uix.floatlayout import FloatLayout
          from kivy.uix.textinput import TextInput
          from kivy.uix.boxlayout import BoxLayout
          from kivy.uix.button import Button
          from kivy.uix.slider import Slider
          from kivy.uix.checkbox import CheckBox
          from kivy.uix.image import Image
          from kivy.uix.progressbar import ProgressBar
          from kivy.uix.togglebutton import ToggleButton
          from kivy.clock import Clock
          from kivy.properties import NumericProperty
          from kivy.properties import StringProperty
          from kivy.properties import ListProperty
          from kivy.lang import Builder
          from kivy.uix.screenmanager import ScreenManager, Screen
          from kivy.core.clipboard import Clipboard
          
          #box
          import tkinter as tk
          from tkinter import filedialog          
          
          #threading
          from threading import Thread
          
          #For hyperlinks
          import webbrowser
          from time import sleep
          from os.path import isdir
          from os.path import isfile
          import os
          import subprocess
          
          class MyScreenManager(ScreenManager):
               
               def getProgress(self):
                    self.transition.direction='left'          
                    self.current='ProgressScreen'
     
          class DeepMeerkatApp(App):
               
               #OS specific home directory
               from pathlib import Path
               import os
               
               if os.name=="nt":
                    home = str(Path.home())
                    output_file=StringProperty(home +"\DeepMeerkat")    
                    
               else:
                    home=os.path.expanduser("~")
                    output_file=StringProperty(home +"/DeepMeerkat")    
                    
               input_file=StringProperty("")               
               dirselect=StringProperty("False")
               
               try:
                    
                    #Run Meerkat
                    #Peek at the args to see if threaded, if not, we can make a new tensorflow session
                    args=CommandArgs.CommandArgs(argv=None) 
                    
                    #TODO OS dependent paths
                    if os.name=="nt":
                         #set default video and tensorflow model, assuming its been installed in the default location
                         args.input="C:/Program Files/DeepMeerkat/Hummingbird.avi"
                         args.path_to_model="C:/Program Files/DeepMeerkat/model/"
                         args.output=home +"\DeepMeerkat"      
                         
                    else:
                         args.input="/Applications/DeepMeerkat.app/Contents/Resources/Hummingbird.avi"
                         args.path_to_model="/Applications/DeepMeerkat.app/Contents/Resources/model/"
                         args.output=home +"/DeepMeerkat"                          
               
                    
               except Exception as e:
                    traceback.print_exc()
                    if len(sys.argv)<= 2:          
                         k=input("Enter any key to exit:")
                         sys.exit(0)
                         
               def build(self):
                    return MyScreenManager()
          
          class MainScreen(Screen):
               
               def help_site(instance):
                    webbrowser.open("https://github.com/bw4sz/DeepMeerkat/wiki")
                  
               def help_issue(instance):
                    webbrowser.open("https://github.com/bw4sz/DeepMeerkat/issues")
               
               def on_check_roi(self, value,args):
                    if value:
                         args.crop=True
                    else:
                         args.crop=False
          
               #Drawing checkbox
               def on_check_draw(self, value,args):     
                    if value:
                         args.draw_size='draw'
                    else:
                         args.draw_size='enter'
               
               def checkfile(self,args):
                    if isfile(self.ids.fc.text):
                         self.ids.fc.background_color=(1,1,1,1)
                    elif isdir(self.ids.fc.text):
                         self.ids.fc.background_color=(1,1,1,1)
                    elif self.ids.fc.text=="Input File or Folder":
                         self.ids.fc.background_color=(1,1,1,1)
                    else:
                         self.ids.fc.background_color=(1,0,0,1)
                    
                    #send text to motion object
                    args.input=self.ids.fc.text
                         
               def run_press(self,root):
                    root.getProgress()
               
               def gotoAdvanced(self,screenmanage):
                    screenmanage.transition.direction='left'          
                    screenmanage.current='AdvancedScreen'
               
               def gotoFileOpen(self,screenmanage):
                    screenmanage.transition.direction='left'          
                    screenmanage.current='FileOpen'
                    
               def gotoOutdir(self,screenmanage):
                    screenmanage.transition.direction='left'          
                    screenmanage.current='Outdir'                  
          
          class FileOpen(Screen):
               from pathlib import Path
               import os
               
               #OS specific directory
               if os.name=="nt":
                    wd = str(Path.home())
               else:
                    wd=os.path.expanduser("~")
               
               def change_path(self,text,current):
                    if os.path.exists(text): 
                         return text
                    else:
                         return current  
                    
               def gotoMain(self,screenmanage):
                    screenmanage.transition.direction='right'          
                    screenmanage.current='GUI'   
          
          class Outdir(Screen):
               from pathlib import Path
               import os
               
               #OS specific directory
               if os.name=="nt":
                    home = str(Path.home())
                    wd=home+"\DeepMeerkat"
                    
               else:
                    home=os.path.expanduser("~")
                    wd=home+"/DeepMeerkat"
                    
               def change_path(self,text,current):
                    if os.path.exists(text): 
                         return text
                    else:
                         return current  
                    
               def gotoMain(self,screenmanage):
                    screenmanage.transition.direction='right'          
                    screenmanage.current='GUI' 
                    
          class AdvancedScreen(Screen):
               
               def gotoMain(self,screenmanage):
                    screenmanage.transition.direction='right'          
                    screenmanage.current='GUI'   
               def run_press(self,root):
                    root.getProgress()     
                    
          class ProgressScreen(Screen):  
               
               #updated properties for reporting
               len_annotations=NumericProperty()                              
               total_min=NumericProperty()
               frame_count=NumericProperty()
               hitrate=NumericProperty()
               video_name=StringProperty()                                             
               output_args=StringProperty()      
               output_annotations=StringProperty()                              
               tensorflow_loaded=StringProperty("Loading")                              
               
               tb=ListProperty([])                              
               
               waitflag = NumericProperty()
               errorflag= NumericProperty()
               video_id=NumericProperty()
               video_count=NumericProperty()

               def worker(self,args):
                    try:
                         
                    
                         if not args.threaded:
                              if args.tensorflow:   
                                   #add tensorflow flag for kivy
                                   tensorflow_status="Loading"                  
                                   sess=Meerkat.start_tensorflow(args)
                                   self.tensorflow_loaded="Complete"                                   
                    
                         #Create queue of videos to run
                         queue=Meerkat.create_queue(args=args)
                         self.video_count=len(queue)
                         
                         if args.threaded:
                              self.tensorflow_loaded="Multithreaded version"                              
                              from multiprocessing.dummy import Pool
                              pool = Pool(3)
                              mapfunc = partial(Meerkat.DeepMeerkat, args=args)        
                              results = pool.map(mapfunc, queue)                              
                              pool.close()
                              pool.join()
                         else:
                              self.video_id=0                              
                              for vid in queue:
                                   self.video_id+=1
                                   self.video_name=vid                                   
                                   results=Meerkat.DeepMeerkat(vid=vid,args=args,sess=sess)                              
                         
                         #save outputs
                         self.total_min=results.video_instance.total_min
                         self.frame_count=results.video_instance.frame_count
                         self.len_annotations=len(results.video_instance.annotations)
                         self.hitrate=round(float(self.len_annotations)/self.frame_count,3) * 100         
                         self.output_annotations=results.video_instance.output_annotations
                         self.output_args=results.video_instance.output_args
                         self.waitflag=1
                                                  
                    except Exception as e:
                         self.tb.append(str(traceback.format_exc()))
                         self.errorflag=1
                    
               def MotionM(self,args):
                    self.waitflag=0   
                    self.errorflag=0                    
                    Thread(target=self.worker,kwargs=dict(args=args)).start()
                    
               def gotoErrorScreen(self,screenmanage):
                    screenmanage.transition.direction='left'          
                    screenmanage.current='ErrorScreen'
                    
          class ResultsScreen(Screen):
               
               #data reporting
               total_min=NumericProperty()      
               frame_count=NumericProperty()               
               len_annotations=NumericProperty()               
               hitrate=NumericProperty()               
                              
               def gotoMain(self,screenmanage):
                    screenmanage.transition.direction='right'          
                    screenmanage.current='GUI'   
                                        
               def openparfile(self,args):
                    #platform dependent
                    if os.name=="nt":
                         subprocess.call('explorer /n,/e,' + os.path.normpath(args.output))
                    else:
                         subprocess.call(["open", args.output])
          
          class ErrorScreen(Screen):
               em=StringProperty()
               def getMessage(self,screenmanage):
                    PScreen=screenmanage.get_screen("ProgressScreen")
                    self.em=PScreen.tb.pop()
               
               def help_issue(instance):
                    webbrowser.open("https://github.com/bw4sz/DeepMeerkat/issues")
               
               def gotoMain(self,screenmanage):
                    #restart
                    screenmanage.transition.direction='right'          
                    screenmanage.current='GUI'      
               
          #run app  
          if __name__=="__main__":
               try:
                    DeepMeerkatApp().run()
               except Exception as e:
                    traceback.print_exc()
                    if len(sys.argv)<= 2:          
                         k=input("Enter any key to exit:")
                         sys.exit(0)
