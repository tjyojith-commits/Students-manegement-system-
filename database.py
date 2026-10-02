from sqlite3 import Cursor

import pymysql

def get_db_connection():
        conn = pymysql.connect(host="localhost", 
                                           user="root", 
                                           password="1234")
        cur = conn.cursor()
        # create database if not exists        
        try:
            cur.execute("create database if not exists student_db")
            cur.execute("use student_db")
            print("Database is created successfully!")
            cur.close()
            
        except Exception as e:
            print(f"Error: {e}")

        return conn

def get_totalstudents(grade):
    """Returns (total, male, female, others) counts for the given grade."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                COUNT(*) AS total_students,
                SUM(CASE WHEN gender = 'Male'   THEN 1 ELSE 0 END) AS total_male,
                SUM(CASE WHEN gender = 'Female' THEN 1 ELSE 0 END) AS total_female,
                SUM(CASE WHEN gender = 'others' THEN 1 ELSE 0 END) AS total_others
            FROM student
            WHERE grade = %s
        """, (grade,))
        row = cursor.fetchone()
        total  = row[0] if row[0] is not None else 0
        male   = row[1] if row[1] is not None else 0
        female = row[2] if row[2] is not None else 0
        others = row[3] if row[3] is not None else 0
        return total, male, female ,others
    except Exception as e:
        print(f"Error in get_totalstudents: {e}")
        return 0, 0, 0
    finally:
        cursor.close()
        conn.close()
