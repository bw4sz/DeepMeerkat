import json
import argparse
import glob

class ParseJson:
    def __init__(self,args):
        print("Json Parser")
        self.args=args
        
    def find_json(self):
        self.fns=glob.glob(self.args.input+"prediction.results*")      
    
    def parse_json(self):
        data=[]
        
        for fn in self.fns:
            with open(fn) as f:
                for line in f:
                    data.append(json.loads(line))
                
        print(data)     
        
if __name__=="__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-input',default="C:/Users/Ben/Dropbox/GoogleCloud/" ,help='Path to json directory')
    args = parser.parse_args()    
    
    #parse
    jparser=ParseJson(args)
    
    #find json files
    jparser.find_json()
    
    #read dicts
    jparser.parse_json()
    

    
