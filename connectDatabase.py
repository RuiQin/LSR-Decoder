import psycopg2
import sys

con = None

def insert(data, query):
    print "Start inserting data into database ..."
    try:         
        con = psycopg2.connect(dbname="dbname", user="username", password="password")           
        cur = con.cursor()
      
        cur.executemany(query, data)       
        con.commit()           
    except psycopg2.DatabaseError, e:        
        if con:
            con.rollback()        
        print 'Error %s' % e    
        sys.exit(1)                
    finally:       
        if con:
            con.close()
            print "Finish inserting."