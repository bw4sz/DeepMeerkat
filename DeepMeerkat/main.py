#!/usr/bin/env python
import sys
import cv2
import traceback

#DeepMeerkat
import DeepMeerkat
import CommandArgs

#Entry Point

if __name__ == "__main__":
     print(sys.argv)
     
     #Read in system arguments if they exist
     #if system arg, command line version, skip the GUI
     if len(sys.argv)>= 2:
          
          print("Entering Command Line")
          MM=DeepMeerkat.DeepMeerkat()  
          MM.process_args() 
          MM.run()
                    
          #create blank list to mimic GUI features.
          #MM.wrap(video_id=[],pbar=[])                
     else:            

#run GUI
          #Kivy
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
          
          class MyScreenManager(ScreenManager):

     
               def getProgress(self):
                    name="P"
                    s=ProgressScreen(name=name)
                    self.add_widget(s)
                    self.transition.direction='left'          
                    self.current='P'
     
          class DeepMeerkatApp(App):
               
               input_file=StringProperty("Input File")               
               output_file=StringProperty("Output File")               
               
               try:
                    #Create motion instance class
                    MM=DeepMeerkat.DeepMeerkat()
     
                    #Instantiate Command line args
                    MM.process_args()
                    
                    #set tensorflow status
                    MM.tensorflow_status="Loading"
                    
               except Exception as e:
                    traceback.print_exc()
                    if len(sys.argv)<= 2:          
                         k=raw_input("Enter any key to exit:")
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
                    name="A"
                    a=AdvancedScreen(name=name)
                    screenmanage.add_widget(a)
                    screenmanage.transition.direction='left'          
                    screenmanage.current='A'
               
               def gotoFileOpen(self,screenmanage):
                    fileopen=FileOpen(name="FileOpen")
                    screenmanage.add_widget(fileopen)
                    screenmanage.transition.direction='left'          
                    screenmanage.current='FileOpen'
                    
               def gotoOutdir(self,screenmanage):
                    outdir=FileOpen(name="Outdir")
                    screenmanage.add_widget(outdir)
                    screenmanage.transition.direction='left'          
                    screenmanage.current='Outdir'                  
          
          class FileOpen(Screen):
               
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
               waitflag = NumericProperty()
               errorflag= NumericProperty()
               tb= ListProperty([])
               tensorflow_status= ListProperty([])               
               video_id=ListProperty(["Retrieving File"])
               video_count=ListProperty(["1"])
               
               def assignname(self,MM):
                    self.video_id.append(MM.args.input)
               
               def MotionM(self,MM):
                    self.waitflag=0   
                    self.errorflag=0                    
                    Thread(target=self.worker,kwargs=dict(MM=MM,pbar=self.ids.pb)).start()
                  
               def worker(self,MM,pbar):
                    try:
                         #Collect video queue
                         MM.create_queue()
                         if MM.args.threaded:
                              from multiprocessing import Pool
                              from multiprocessing.dummy import Pool as ThreadPool 
                              pool = ThreadPool(2)         
                              results = pool.map(MM.run,MM.queue)
                              pool.close()
                              pool.join()
                         else:
                              for vid in MM.queue:
                                   self.vid=vid
                                   MM.run(vid=vid)      
                         self.waitflag=1
                    except Exception as e:
                         self.tb.append(str(traceback.format_exc()))
                         self.errorflag=1
                         
               def gotoresults(self,screenmanage):          
                    screenmanage.switch_to(ResultsScreen(),direction='left')
                    
               def gotoErrorScreen(self,screenmanage):
                    name="E"
                    e=ErrorScreen(name=name)
                    screenmanage.add_widget(e)
                    screenmanage.transition.direction='left'          
                    screenmanage.current='E'
                    
          class ResultsScreen(Screen):
                    
               def gotoMain(self,screenmanage):
                    screenmanage.transition.direction='right'          
                    screenmanage.current='GUI'   
                    
               def openfile(self,MM):
                    startfile(MM.args.output + "/" + "Parameters_Results.log")
          
          class ErrorScreen(Screen):
               em=StringProperty()
               def getMessage(self,screenmanage):
                    PScreen=screenmanage.get_screen("P")
                    self.em=PScreen.tb.pop()
               
               def help_issue(instance):
                    webbrowser.open("https://github.com/bw4sz/DeepMeerkat/issues")
               
               def gotoMain(self,screenmanage):
                    #restart
                    screenmanage.transition.direction='right'          
                    screenmanage.current='GUI'      
                    
               def openfile(self,MM):
                    startfile(MM.args.output + "/" + "Parameters_Results.log")
               
          #run app  
          if __name__=="__main__":
               DeepMeerkatApp().run()
               cv2.destroyAllWindows()
     