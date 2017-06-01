---
title: "Training Visualization"
author: "Ben Weinstein"
date: "June 1, 2017"
output: html_document
---




#get file list.filnames<-list.files("C:/Users/Ben/Dropbox/GoogleCloud/Summary",full.names = T,pattern=".csv")preds<-bind_rows(lapply(filnames,function(x){
  
  #read csv
  dat<-read.csv(x)
  
  #assign date
  date<-str_match(x,"DeepMeerkat_(\\w+)_(\\w+)_\\w+.csv")
  dat$date<-format(strptime(date[,2],"%Y%m%d"))
  
  #eval or holdout
  dat$type<-str_match(x,"DeepMeerkat_\\w+_\\w+_(\\w+).csv")[,2]
  return(dat)
  }))## Error in FUN(X[[i]], ...): could not find function "str_match"
#strip key name pathspreds$ID<-as.character(str_match(preds$key,"\\w+.jpg"))## Error in eval(expr, envir, enclos): could not find function "str_match"
preds$TrueLabel<-as.numeric(str_detect(preds$key,"Positives"))## Error in eval(expr, envir, enclos): could not find function "str_detect"
#lookup label in dictlabels<-read.table("dict.txt")## Warning in read.table("dict.txt"): incomplete final line found by
## readTableHeader on 'dict.txt'
preds$PredLabel<-(labels$V1[preds$prediction+1]=="positive")*1## Error in NextMethod("["): object 'preds' not found
sumtable<-preds %>% group_by(date,type,True=TrueLabel,Predicted=PredLabel) %>% summarize("%"=n()/sum(n()))## Error in eval(expr, envir, enclos): object 'preds' not found
kable(sumtable)## Error in inherits(x, "list"): object 'sumtable' not found
#calculate recallretable<-preds %>% group_by(date,type) %>% summarize(recall=sum(TrueLabel==1)/sum(PredLabel==1),accuracy=sum(TrueLabel==1&PredLabel==1)/sum(PredLabel==1))## Error in eval(expr, envir, enclos): object 'preds' not found
recall<-sum((sumtable$Predicted==1))/sum((sumtable$True==1))## Error in eval(expr, envir, enclos): object 'sumtable' not found
kable(retable)## Error in inherits(x, "list"): object 'retable' not found
