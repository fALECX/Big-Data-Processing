#!/usr/bin/env python3
import sys
# Count the number of "salaryC gender" 
# That is, "salaryC gender" is the key. 

# using a dictionary to map words to their counts
current_salaryC = None
current_gender = None
current_count = 0
salaryC = None
gender = None

# input comes from STDIN
for line in sys.stdin:
    line = line.strip()
    #print("--%s" % line)
    salaryC,gender,count = line.split('\t')
    #print("----%s\t%s\t%s" % (salaryC,gender,count))
    try:
        count = int(count)
    except ValueError:
        continue
    if current_salaryC == salaryC and current_gender == gender:
        current_count += count
    else:
        if current_salaryC:
               print('%s\t%s\t%s' % (current_salaryC, current_gender, current_count))
        current_count = count
        current_salaryC = salaryC
        current_gender = gender
if current_salaryC == salaryC and current_gender == gender:
    print('%s\t%s\t%s' % (current_salaryC, current_gender, current_count))