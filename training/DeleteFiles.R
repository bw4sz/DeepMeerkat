a<-list.dirs("G:/MaquipucunaFlowers/",recursive = T,full.names = T)

library(stringr)

for(d in a){
  print(d)
  #only get child directories
  di<-list.dirs(d,full.names=T)
  
  if(length(di) > 1){
     next
  }
  
  fil<-list.files(d,full.names=T)
  
  vid=sum(str_detect(string=a,pattern=".tlv"))
  if(vid==0){
    print("Deleted")
    unlink(d,recursive=T,force=T)
  }
}
