#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
a little web service to help with various functions in the cataloging dept.
Main reference:
https://github.com/bormotov/bottle-oracle
Prerequisites: Oracle instant client, python, bottle, cx_Oracle 
pmg
from 2013-04-14
"""

import ConfigParser
import cx_Oracle
import os
import sys

from bottle import *

# parse configuration file finder.cfg
config = ConfigParser()
config.read('./finder.cfg')

USER = config.get('vger', 'user')
PASS = config.get('vger', 'pw')
PORT = config.get('vger', 'port')
SID = config.get('vger', 'sid')
HOST = config.get('vger', 'ip')

DSN = cx_Oracle.makedsn(HOST,PORT,SID)

Q_FIELDS = ['BIB_TEXT.BIB_ID as BIB','BIB_HISTORY.ACTION_DATE','BIB_HISTORY.OPERATOR_ID', 'OPERATOR.LAST_NAME', 'OPERATOR.FIRST_NAME', 'LOCATION.LOCATION_CODE', 'LOCATION.LOCATION_NAME','BIB_TEXT.TITLE_BRIEF','ACTION_TYPE.ACTION_TYPE','ITEM_STATUS_TYPE.ITEM_STATUS_DESC','ITEM_BARCODE.ITEM_BARCODE']

Q_STRING = """SELECT %s
FROM BIB_TEXT INNER JOIN BIB_HISTORY ON BIB_TEXT.BIB_ID = BIB_HISTORY.BIB_ID 
INNER JOIN OPERATOR ON BIB_HISTORY.OPERATOR_ID = OPERATOR.OPERATOR_ID 
INNER JOIN LOCATION ON BIB_HISTORY.LOCATION_ID = LOCATION.LOCATION_ID
INNER JOIN ACTION_TYPE ON BIB_HISTORY.ACTION_TYPE_ID = ACTION_TYPE.ACTION_TYPE_ID
INNER JOIN BIB_ITEM ON BIB_TEXT.BIB_ID = BIB_ITEM.BIB_ID
LEFT JOIN ITEM_STATUS ON BIB_ITEM.ITEM_ID = ITEM_STATUS.ITEM_ID
LEFT JOIN ITEM_STATUS_TYPE ON ITEM_STATUS.ITEM_STATUS = ITEM_STATUS_TYPE.ITEM_STATUS_TYPE
LEFT JOIN ITEM_BARCODE ON ITEM_STATUS.ITEM_ID = ITEM_BARCODE.ITEM_ID
""" % ','.join(Q_FIELDS)

STATUS_STRING = """SELECT ITEM.ITEM_ID, ITEM_STATUS_TYPE.ITEM_STATUS_DESC, ITEM_STATUS.ITEM_STATUS_DATE, ITEM.CREATE_OPERATOR_ID, ITEM.CREATE_DATE, ITEM.MODIFY_OPERATOR_ID, ITEM.MODIFY_DATE
FROM (ITEM INNER JOIN ITEM_STATUS ON ITEM.ITEM_ID = ITEM_STATUS.ITEM_ID) INNER JOIN ITEM_STATUS_TYPE ON ITEM_STATUS.ITEM_STATUS = ITEM_STATUS_TYPE.ITEM_STATUS_TYPE"""

AUTHCALLNO_STRING = """SELECT DISTINCT AUTHOR, BIB_TEXT.TITLE_BRIEF, MFHD_MASTER.DISPLAY_CALL_NO, MFHD_MASTER.NORMALIZED_CALL_NO
FROM BIB_TEXT
LEFT JOIN BIB_MFHD ON BIB_TEXT.BIB_ID = BIB_MFHD.BIB_ID 
LEFT JOIN MFHD_MASTER ON BIB_MFHD.MFHD_ID = MFHD_MASTER.MFHD_ID"""

@error(500)
def error500(error):
    return template('error')

@route('/')
def index_page():
    oradb = cx_Oracle.connect(USER,PASS,DSN)
 
    default = None
    type = request.GET.get('type',default)
    num = request.GET.get('num',default)
 
    if (type is not None) and (num is not None):
		
        if type == 'item':
            rows = oradb.cursor()
            rows.execute(Q_STRING + ' WHERE ITEM_STATUS.ITEM_ID=%s ORDER BY BIB_HISTORY.ACTION_DATE DESC' % num)
            r = rows.fetchall()
            rows.close()
            del rows
            
            getbib = oradb.cursor()
            getbib.execute('SELECT BIB_ITEM.BIB_ID FROM BIB_ITEM WHERE BIB_ITEM.ITEM_ID=%s' % num)
            r1 = getbib.fetchone()
            getbib.close()
            del getbib
            
            getti = oradb.cursor()
            getti.execute('SELECT BIB_TEXT.TITLE_BRIEF FROM BIB_TEXT WHERE BIB_TEXT.BIB_ID=%s' % r1[0])
            r2 = getti.fetchone()
            getti.close()
            del getti
            
            get902 = oradb.cursor()
            get902.execute('SELECT princetondb.GetAllBibTag(BIB_TEXT.BIB_ID,902) FROM BIB_TEXT WHERE BIB_TEXT.BIB_ID=%s ' % r1[0])
            r3 = get902.fetchone()
            get902.close()
            del get902
            
            getbc = oradb.cursor()
            getbc.execute('SELECT ITEM_BARCODE.ITEM_BARCODE from ITEM_BARCODE WHERE ITEM_BARCODE.ITEM_ID=%s' % num)
            r4 = getbc.fetchone()
            getbc.close()
            del getbc
            
            getstat = oradb.cursor()
            getstat.execute(STATUS_STRING + ' WHERE ITEM.ITEM_ID=%s' % num)
            r5 = getstat.fetchall()	
            getstat.close()
            del getstat
            
            return template('views/results',  fields=r, status=r5, bib=r1[0], ti=r2[0], f902=r3[0], itm=num, bc=r4[0])
            oradb.close()
            
        elif type == 'bc':
            rows = oradb.cursor()
            rows.execute(Q_STRING + ' WHERE ITEM_BARCODE.ITEM_BARCODE=substr(%s,1,14) ORDER BY BIB_HISTORY.ACTION_DATE DESC' % num)
            r = rows.fetchall()
            rows.close()
            del rows
            
            getbib = oradb.cursor()
            getbib.execute('SELECT BIB_ITEM.BIB_ID, BIB_ITEM.ITEM_ID FROM BIB_ITEM RIGHT JOIN ITEM_BARCODE ON ITEM_BARCODE.ITEM_ID = BIB_ITEM.ITEM_ID WHERE ITEM_BARCODE.ITEM_BARCODE=substr(%s,1,14)' % num)
            r1 = getbib.fetchone()
            getbib.close()
            del getbib
            
            getti = oradb.cursor()
            getti.execute('SELECT BIB_TEXT.TITLE_BRIEF FROM BIB_TEXT WHERE BIB_TEXT.BIB_ID = %s' % r1[0])
            r2 = getti.fetchone()
            getti.close()
            del getti 
            
            get902 = oradb.cursor()
            get902.execute('SELECT princetondb.GetAllBibTag(BIB_TEXT.BIB_ID,902) FROM BIB_TEXT WHERE BIB_TEXT.BIB_ID =%s' % r1[0])
            r3 = get902.fetchone()
            get902.close()
            del get902
            
            getstat = oradb.cursor()
            getstat.execute(STATUS_STRING + ' WHERE ITEM.ITEM_ID=%s' % r1[1]) 
            r5 = getstat.fetchall()
            getstat.close()
            del getstat
            
            return template('views/results',  fields=r, status=r5, bib=r1[0], ti=r2[0], f902=r3[0], itm=r1[1], bc=num)
            oradb.close()
            
        elif type == 'bib':
            rows = oradb.cursor()
            rows.execute(Q_STRING + ' WHERE BIB_TEXT.BIB_ID=%s ORDER BY BIB_HISTORY.ACTION_DATE DESC' % num)
            r = rows.fetchall()
            rows.close()
            del rows
            
            getti = oradb.cursor()
            getti.execute('SELECT TITLE_BRIEF FROM BIB_TEXT WHERE BIB_ID=%s' % num)
            r2 = getti.fetchone()
            getti.close()
            del getti
            
            get902 = oradb.cursor()
            get902.execute('SELECT princetondb.GetAllBibTag(BIB_TEXT.BIB_ID,902) FROM BIB_TEXT WHERE BIB_ID=%s ' % num) 
            r3 = get902.fetchone()
            get902.close()
            del get902
            
            return template('views/results',  fields=r, status=None, bib=num, ti=r2[0].decode('ascii','ignore'), f902=r3[0],itm=None,bc=None)
            oradb.close()
            
        elif type == 'call':
            getcall = oradb.cursor()
            getcall.execute(AUTHCALLNO_STRING + " WHERE MFHD_MASTER.DISPLAY_CALL_NO like '%s%%' ORDER BY MFHD_MASTER.NORMALIZED_CALL_NO" % num)
            r = getcall.fetchall()
            getcall.close()
            del getcall

            return template('views/results',fields=r, bib=None,callno=True,title=False)
            oradb.close()

        elif type == 'title':
            getti = oradb.cursor()
            getti.execute(AUTHCALLNO_STRING + " WHERE BIB_TEXT.TITLE_BRIEF like '%s%%' ORDER BY MFHD_MASTER.NORMALIZED_CALL_NO" % num)
            r = getti.fetchall()
            print(r)
            getti.close()
            del getti

            return template('views/results',fields=r,
            bib=None, callno=False, title=True)
            oradb.close()
            
        elif type == 'auth':
            getauth = oradb.cursor()
            getauth.execute(AUTHCALLNO_STRING + " WHERE BIB_TEXT.AUTHOR like '%s%%' ORDER BY MFHD_MASTER.NORMALIZED_CALL_NO" % num)
            r = getauth.fetchall()
            getauth.close()
            del getauth

            return template('views/results',fields=r,
            bib=None, callno=None, title=False)
            oradb.close()
    else:
        return template('index')


run(host="0.0.0.0", port=8082, server='paste')
