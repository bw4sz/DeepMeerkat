#!/usr/bin/env python
import sys
import cv2
import traceback

#DeepMeerkat
import Meerkat
import CommandArgs
import os

from pathlib import Path
home = str(Path.home())

#Entry Point

if __name__ == "__main__":
     print(sys.argv)
     
     #Read in system arguments if they exist
     #if system arg, command line version, skip the GUI
     if len(sys.argv)>= 2:
          
          DM=Meerkat.DeepMeerkat()
          DM.process_args()
          DM.create_queue()
          if DM.args.threaded:
               from multiprocessing import Pool
               from multiprocessing.dummy import Pool as ThreadPool 
               pool = ThreadPool(2)         
               results = pool.map(DM.run_threaded,DM.queue)
               pool.close()
               pool.join()
     
          else:
               for vid in DM.queue:
                    DM.run(vid=vid,sess=DM.sess)                    
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
               from pathlib import Path
               home = str(Path.home())
               input_file=StringProperty("")               
               output_file=StringProperty(home +"/DeepMeerkat/")    
               dirselect=StringProperty("False")
               try:
                    #Create motion instance class
                    MM=Meerkat.DeepMeerkat()
     
                    #Instantiate Command line args
                    MM.process_args()
                    
                    #set default video and tensorflow model, assuming its been installed in the default location
                    MM.input="C:/Program Files (x86)/DeepMeerkat/Hummingbird.avi"
                    MM.path_to_model="C:/Program Files (x86)/DeepMeerkat/model/"      
                    
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
               
               def on_check_roi(self, value,MM):
                    if value:
                         MM.args.crop=True
                    else:
                         MM.args.crop=False
          
               #Drawing checkbox
               def on_check_draw(self, value,MM):     
                    if value:
                         MM.args.draw_size='draw'
                    else:
                         MM.args.draw_size='enter'
               
               def checkfile(self,MM):
                    if isfile(self.ids.fc.text):
                         self.ids.fc.background_color=(1,1,1,1)
                    elif isdir(self.ids.fc.text):
                         self.ids.fc.background_color=(1,1,1,1)
                    elif self.ids.fc.text=="Input File or Folder":
                         self.ids.fc.background_color=(1,1,1,1)
                    else:
                         self.ids.fc.background_color=(1,0,0,1)
                    
                    #send text to motion object
                    MM.args.input=self.ids.fc.text
                         
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
               home = str(Path.home())               
               wd=home
               
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
               home = str(Path.home())               
               wd=home+"\DeepMeerkat"
               
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

               def worker(self,MM):
                    try:
                         #Collect video queue
                         MM.create_queue()
                         
                         self.tensorflow_loaded="Complete"
                         #set total number
                         self.video_count=len(MM.queue)
                         
                         if MM.args.threaded:
                              self.tensorflow_loaded="Multithreaded version"
                              from multiprocessing import Pool
                              from multiprocessing.dummy import Pool as ThreadPool 
                              pool = ThreadPool(2)         
                              results = pool.map(MM.run_threaded,MM.queue)
                              pool.close()
                              pool.join()
                         else:
                              self.video_id=0
                              for vid in MM.queue:
                                   self.video_id+=1
                                   self.video_name=vid
                                   MM.run(vid=vid,sess=MM.sess) 
                              
                         #save outputs
                         self.total_min=MM.video_instance.total_min
                         self.frame_count=MM.video_instance.frame_count
                         self.len_annotations=len(MM.video_instance.annotations)
                         self.hitrate=round(float(self.len_annotations)/self.frame_count,3) * 100         
                         self.output_annotations=MM.video_instance.output_annotations
                         self.output_args=MM.video_instance.output_args
                         self.waitflag=1
                                                  
                    except Exception as e:
                         self.tb.append(str(traceback.format_exc()))
                         self.errorflag=1
                    
               def MotionM(self,MM):
                    self.waitflag=0   
                    self.errorflag=0                    
                    Thread(target=self.worker,kwargs=dict(MM=MM)).start()
                    
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
                                        
               def openparfile(self,MM):
                    subprocess.call('explorer /n,/e,' + os.path.normpath(MM.args.output))
          
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
               DeepMeerkatApp().run()
               cv2.destroyAllWindows()
     