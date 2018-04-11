import sys
import time
import os
from operator import itemgetter
from itertools import groupby
import subprocess

def video_clips(MotionHistory,frame_rate,input_path,output_path,path_to_ffmpeg):
    ''''
    Clip a video file into pieces based on duration of movement.
    Several rules are applied to create consistant and reasonable clip sizes
    '''
    
    #find beginning and end segments
    #multiply frame number by frame rate to get timestamp        
    clip_range=ClipLength(MotionHistory,frame_rate)
    
    #If no clips, exit.
    if len(clip_range)==0:
        return None
    ##Clip rules for combining segments##
    
    #1) If two consecutive clips are within 20 seconds (n), combine.
    rule1=combine_clips(clip_range,n=20)
    
    #2) If clip duration is less than 2 seconds, remove
    rule2=minimum_duration(rule1,n=2)
    
    #If no clips left after trimming, exit.
    if len(rule2)==0:
        print("No remaining clips")
        return None
    
    #turn back to floats if needed for single file
    if isinstance(rule2[0],float):
        rule2=[rule2]
    
    #for each VideoClip, cut segment using FFMPEG
    print("%d video clips found" % len(rule2))
    vname,ext=os.path.splitext(os.path.basename(input_path))
    
    #each clip should be named sequentially
    #add a small buffer to show beginning and end
    buffer=1
    for index,clip in enumerate(rule2):
        local_path= output_path + "/" + vname+"_"+str(index)+".avi"            
        ffmpeg_extract_subclip(input_path, clip[0]-buffer, clip[1]+buffer, local_path,path_to_ffmpeg)

###Helper Functions#####
def ClipLength(l,frame_rate):

    #get first position of Motion
    indexes = [next(group) for key, group in groupby(enumerate(l), key=itemgetter(1))]

    #number of frames with Motion
    len_indexes = [len(list(group)) for key, group in groupby(l)]

    clip_range=[]

    #Create time ranges by dividing frame counts by frame rate
    for position,length in enumerate(len_indexes):
        if indexes[position][1] == True:
            clip_range.append([float(indexes[position][0])/frame_rate,float(indexes[position][0]+length)/frame_rate])
    return clip_range

def combine_clips(clip_range,n=30):

    #perform iteratively until no more concatanations
    flat_list = [item for sublist in clip_range for item in sublist]
    b = [abs(i - j) > n for i, j in zip(flat_list[:-1], flat_list[1:])]
    m = [i + 1 for i, j in enumerate(b) if j is True]
    m = [0] + m + [len(flat_list)]
    new_groups = [flat_list[i: j] for i, j in zip(m[:-1], m[1:])]
    
    rule1=[[min(x),max(x)] for x in new_groups]    
    
    return rule1

def minimum_duration(clips,n=0):
    cliplist=[]
    for clip in clips:
        if clip[1]-clip[0] > n:
            cliplist.append(clip)    
    return cliplist

#Subclip, originally from 
#https://zulko.github.io/moviepy/_modules/moviepy/video/io/ffmpeg_tools.html

def ffmpeg_extract_subclip(filename, t1, t2, targetname,path_to_ffmpeg):
    """ makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """
    name,ext = os.path.splitext(filename)
    if not targetname:
        T1, T2 = [int(1000*t) for t in [t1, t2]]
        targetname = name+ "%sSUB%d_%d.%s"(name, T1, T2, ext)
    
    cmd = [path_to_ffmpeg,"-y",
      "-i", filename,
      "-ss", "%0.2f"%t1,
      "-t", "%0.2f"%(t2-t1),
      "-vcodec", "copy", "-acodec", "copy", targetname]
    
    subprocess.call(cmd)