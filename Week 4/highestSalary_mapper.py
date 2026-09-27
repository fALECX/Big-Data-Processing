#!/usr/bin/env python3
import sys
# count the number of employee based on salary group
# salary<10000 low; 
# 10000<=salary<20000 low middle; 
# 20000<=salary<30000 high middle;  
# 30000<=salary high;  

# input comes from standard input STDIN
for line in sys.stdin:
    line = line.strip() #remove leading and trailing whitespaces
    id, name, age, gender, salary = line.split("\t") #split the line into words and returns as a list

    if float(salary)<10000: salaryC = "low" 
    elif 10000<=float(salary)<20000: salaryC = "low_middle" 
    elif 20000<=float(salary)<30000:salaryC = "high_middle"   
    else: salaryC = "high"
    
    print('%s\t%s\t%s' % (salaryC,gender,"1")) #Emit <key, value> pairs  