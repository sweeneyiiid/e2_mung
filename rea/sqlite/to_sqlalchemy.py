# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 11:51:22 2022

@author: reeep
"""

import pymysql
import sqlalchemy
from sqlalchemy import create_engine

sqlalchemy.__version__

#https://docs.sqlalchemy.org/en/14/dialects/mysql.html

engine = create_engine("mysql+pymysql://sql11522555:85XwDJyvDS@sql11.freemysqlhosting.net/sql11522555?charset=utf8mb4")




