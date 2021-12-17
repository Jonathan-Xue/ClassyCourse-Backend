import csv
import psycopg2
import psycopg2.pool

from db_config import *

# Database
class DB:
    def __init__(self, reset):
        self.cnx_pool = None
        self.setup(reset=reset)

    def setup(self, reset):
        # Cleanup
        if self.cnx_pool:
            self.cnx_pool.closeall()

        # Database
        cnx = psycopg2.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, dbname='postgres')
        cnx.autocommit = True
        cursor = cnx.cursor()

        if reset:
            cursor.execute("DROP DATABASE IF EXISTS {}".format(DATABASE))

        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname='{}'".format(DATABASE))
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE {}".format(DATABASE))
        
        cursor.close()
        cnx.commit()
        cnx.close()

        # SQL Pool
        self.cnx_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1, maxconn=10,
            host=HOST, port=PORT, user=USER, password=PASSWORD, dbname=DATABASE,
        )

        # Tables
        cnx = self.cnx_pool.getconn()
        cursor = cnx.cursor()

        for name, ddl in TABLES.items():
            print("Creating table {}: ".format(name), end='')
            cursor.execute(ddl)
            print("OK.")

        cursor.close()
        cnx.commit()
        self.cnx_pool.putconn(cnx)
        
    def insert_record(self, year, term, subject, number, name, instructor, sched_type, a_plus, a, a_minus, b_plus, b, b_minus, c_plus, c, c_minus, d_plus, d, d_minus, f, w):
        cnx = self.cnx_pool.getconn()
        cursor = cnx.cursor()

        cursor.execute("INSERT INTO grades(year, term, subject, number, name, instructor, sched_type, a_plus, a, a_minus, b_plus, b, b_minus, c_plus, c, c_minus, d_plus, d, d_minus, f, w) " + \
                       "VALUES ({}, '{}', '{}', {}, '{}', '{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})".format(year, term, subject, number, name.replace("'", "''"), instructor.replace("'", "''"), sched_type, a_plus, a, a_minus, b_plus, b, b_minus, c_plus, c, c_minus, d_plus, d, d_minus, f, w))
        
        cursor.close()
        cnx.commit()
        self.cnx_pool.putconn(cnx)

    def get_course_avg(self, subject, number, name):
        cnx = self.cnx_pool.getconn()
        cursor = cnx.cursor()

        # Results
        cursor.execute("SELECT SUM(a_plus) as a_plus, SUM(a) as a, SUM(a_minus) as a_minus, SUM(b_plus) as b_plus, SUM(b) as b, SUM(b_minus) as b_minus, SUM(c_plus) as c_plus, SUM(c) as c, SUM(c_minus) as c_minus, SUM(d_plus) as d_plus, SUM(d) as d, SUM(d_minus) as d_minus, SUM(f) as f, SUM(w) as w " + \
                       "FROM grades " + \
                       "WHERE subject='{}' AND number={} AND name='{}'".format(subject, number, name.replace("'", "''")))
        results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()][0]

        # Calculate Average GPA
        sum = 0
        count = 0
        for key, val in results.items():
            if GPA_MAP[key] != None and val != None:
                sum += (GPA_MAP[key] * val)
                count += val

        cursor.close()
        cnx.commit()
        self.cnx_pool.putconn(cnx)

        return None if count == 0 else sum / count
    
    def get_course_statistics(self, subject, number, name):
        cnx = self.cnx_pool.getconn()
        cursor = cnx.cursor()

        results = {}

        # Aggregate
        cursor.execute("SELECT SUM(a_plus) as a_plus, SUM(a) as a, SUM(a_minus) as a_minus, SUM(b_plus) as b_plus, SUM(b) as b, SUM(b_minus) as b_minus, SUM(c_plus) as c_plus, SUM(c) as c, SUM(c_minus) as c_minus, SUM(d_plus) as d_plus, SUM(d) as d, SUM(d_minus) as d_minus, SUM(f) as f, SUM(w) as w " + \
                       "FROM grades " + \
                       "WHERE subject='{}' AND number={} AND name='{}' ".format(subject, number, name.replace("'", "''")))
        results['aggregate'] = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()][0]

        # Granular
        cursor.execute("SELECT instructor, SUM(a_plus) as a_plus, SUM(a) as a, SUM(a_minus) as a_minus, SUM(b_plus) as b_plus, SUM(b) as b, SUM(b_minus) as b_minus, SUM(c_plus) as c_plus, SUM(c) as c, SUM(c_minus) as c_minus, SUM(d_plus) as d_plus, SUM(d) as d, SUM(d_minus) as d_minus, SUM(f) as f, SUM(w) as w " + \
                       "FROM grades " + \
                       "WHERE subject='{}' AND number={} AND name='{}' ".format(subject, number, name.replace("'", "''")) + \
                       "GROUP BY instructor")
        results['granular'] = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

       

        cursor.close()
        cnx.commit()
        self.cnx_pool.putconn(cnx)

        return results