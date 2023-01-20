# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 11:33:26 2022

@author: grego

"""

import mysql.connector
import time


def database():
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="PASSWD",
      database = "AIRY"
    )
    
    mycursor = mydb.cursor()
    
    sql = "UPDATE DATA SET HANDLER = %s WHERE ID = %s"
    values = (0, 1)
    mycursor.execute(sql, values)
    mydb.commit()
    
    #time.time(2)
     
    mycursor.execute("SELECT * FROM DATA")
    myresult = mycursor.fetchall()
    
    listOne = myresult[0]
    x = listOne[1]
    y = listOne[2]
    signal = listOne[3]
    SW = listOne[4]
    m = [x, y, signal, SW]
    return m