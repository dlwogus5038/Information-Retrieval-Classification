#!/usr/bin/python
# -*- coding: UTF-8 -*-

f = open("C:\\Users\\dlwog\\Pictures\\hi\\dict.txt", 'r', encoding="utf-8")
lines = f.readlines()
for line in lines:
    str = line.split(' ',1)
    print(str[0])