# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 11:33:26 2022

@author: grego
"""

import mysql.connector


def database():
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="PASSWD",
      database = "AIRY"
    )
    
    mycursor = mydb.cursor()
     
    mycursor.execute("SELECT * FROM DATA")
    myresult = mycursor.fetchall()
    
    listOne = myresult[0]
    x = listOne[1]
    y = listOne[2]
    signal = listOne[3]
    m = [x, y, signal]
    return m