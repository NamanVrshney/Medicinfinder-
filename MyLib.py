import pymysql
def getconnection():
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='naman', autocommit=True)
    cur = conn.cursor()
    return cur

def check_photo(email):
    conn = pymysql.connect(host='localhost',port=3306,user='root', passwd='',db='naman')
    cur = conn.cursor()
    cur.execute("select * from photodata where email='"+email+"' ")
    n = cur.rowcount
    photo = "no"
    if (n>0):
        row = cur.fetchone()
        photo = row[1]
    return photo


def get_admin_name(email):
    cur = getconnection()
    cur.execute("SELECT * FROM admindata where email='" + email + "'")
    n = cur.rowcount
    name = "no"
    if n > 0:
        row = cur.fetchone()
        name = row[0]
    return name


def get_doctors(email):
    cur = getconnection()
    cur.execute("SELECT * FROM doctordata where email_of_hospital='"+email+"'")
    data=cur.fetchall()
    return data

def getdoctor(name,spec,email):
    cur = getconnection()
    cur.execute("SELECT * FROM doctordata where name='"+name+"' AND speciality='"+spec+"' AND email_of_hospital='" + email + "'")
    data = cur.fetchone()
    return data