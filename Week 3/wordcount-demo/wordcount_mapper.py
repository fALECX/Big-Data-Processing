#!/usr/bin/env python3
import sys
# Word Count Example
# input comes from standard input STDIN
for line in sys.stdin:
    line = line.strip() #remove leading and trailing whitespaces
    words = line.split(" ") #split the line into words and returns as a list

    for word in words:
        word = ''.join(c for c in word if c.isalnum()) # output alphanumeric item only  
        if word.strip():     
            print('%s\t%s' % (word,"1")) #Emit <key, value> pairs  