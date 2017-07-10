#!/usr/bin/env python
import sys
import cv2
import traceback

#MotionMeerkat
import MotionMeerkat
import CommandArgs

#Entry Point

if __name__ == "__main__":
     print(sys.argv)
     
     #Read in system arguments if they exist
     #if system arg, command line version, skip the GUI
     if len(sys.argv)>= 2:
          
          print("Entering Command Line")
          MM=MotionMeerkat.MotionMeerkat()  
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
          
          #threading
          from threading import Thread
          
          #For hyperlinks
          import webbrowser
          from time import sleep
          from os import startfile
          from os.path import isdir
          from os.path import isfile
          
          class MainScreen(Screen):
               
               def help_site(instance):
                    webbrowser.open("https://github.com/bw4sz/OpenCV_HummingbirdsMotion/wiki")
                  
               def help_issue(instance):
                    webbrowser.open("https://github.com/bw4sz/OpenCV_HummingbirdsMotion/issues")
               
               def on_check_roi(self, value,MM):
                    if value:
                         MM.crop=True
                    else:
                         MM.crop=False
               
               #Drawing checkbox
               def on_check_draw(self, value,MM):     
                    if value:
                         MM.drawSmall='draw'
                    else:
                         MM.drawSmall='enter'
               
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
                    MM.inDEST=self.ids.fc.text
                         
               def run_press(self,root):
                    root.getProgress()
               
               def gotoAdvanced(self,screenmanage):
                    name="A"
                    a=AdvancedScreen(name=name)
                    screenmanage.add_widget(a)
                    screenmanage.transition.direction='left'          
                    screenmanage.current='A'
                    
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
               video_id=ListProperty(["Retrieving File"])
               video_count=ListProperty(["1"])
               
               def assignname(self,MM):
                    self.video_id.append(MM.input)
               
               def MotionM(self,MM):
                    self.waitflag=0   
                    self.errorflag=0                    
                    Thread(target=self.worker,kwargs=dict(MM=MM,pbar=self.ids.pb)).start()
                  
               def worker(self,MM,pbar):
                    try:
                         CommandArgs.CommandArgs(MM)
                         MM.run(pbar=pbar,video_id=self.video_id)          
                         self.waitflag=1
                    except Exception as e:
                         self.tb.append(str(traceback.format_exc()))
                         try:
                              MM.report()               
                         except:
                              pass
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
                    startfile(MM.file_destination + "/" + "Parameters_Results.log")
          
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
                    startfile(MM.file_destination + "/" + "Parameters_Results.log")
               
          class MyScreenManager(ScreenManager):
              
               try:
                    #Create motion instance class
                    MM=MotionMeerkat.MotionMeerkat()
               except Exception as e:
                    traceback.print_exc()
                    if len(sys.argv)<= 2:          
                         k=raw_input("Enter any key to exit:")
                         sys.exit(0)
                    
               def getProgress(self):
                    name="P"
                    s=ProgressScreen(name=name)
                    self.add_widget(s)
                    self.transition.direction='left'          
                    self.current='P'
          
          class MotionMeerkatApp(App):
               def build(self):
                    return MyScreenManager()
          #run app  
          MotionMeerkatApp().run()
          cv2.destroyAllWindows()     