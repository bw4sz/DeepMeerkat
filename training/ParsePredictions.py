import json
import argparse
import glob
import csv

class ParseJson:
    def __init__(self,args):
        print("Json Parser")
        self.args=args
        
    def find_json(self):
        self.fns=glob.glob(self.args.input+"prediction.results*")      
    
    def parse_json(self):
        self.data=[]
        
        for fn in self.fns:
            with open(fn) as f:
                for line in f:
                    self.data.append(json.loads(line))
                
        print(self.data)
    def write_table(self):
        with open("test.csv",'w',newline="") as outfile:
            w = csv.DictWriter(outfile,self.data[0].keys())
            w.writeheader()
            w.writerows(self.data)

        outfile.close()
        
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
    
    #write to table
    jparser.write_table()
    

    
