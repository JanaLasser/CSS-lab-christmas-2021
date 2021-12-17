which_max<-function(v)
{
  #function to compute the most relevant affective dimension
  l<-c('neg','neu','pos')
  return(l[which(v==max(v))])
}
