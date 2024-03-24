import time

from flask import Flask,render_template,request,url_for,redirect,session
import pymysql
from werkzeug.utils import secure_filename

from MyLib import *
import pymysql
import os

app=Flask(__name__)
app.config['UPLOAD_FOLDER']='./static/photos'

app.secret_key = "super secret key"

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route('/hello_world')
def hello_world():
    cur = getconnection()
    cur.execute("SELECT * FROM hospitals")
    result = cur.fetchall()
    return render_template('index.html', result=result)

@app.route("/search",methods=["GET","POST"])
def home():
    if(request.method=="POST"):
        med_name=request.form["T1"]
        cur=getconnection()
        sql="select * from medicine_medical where med_name LIKE '%"+med_name+"%'"
        cur.execute(sql)
        n=cur.rowcount
        if(n>0):
            data=cur.fetchall()
            return render_template("search.html",data=data,mname=med_name)
        else:
            return render_template("search.html",msg="No match found")
    else:
        return render_template("search.html")

@app.route('/searchD', methods=['GET', 'POST'])
def searchD():
    if (request.method == 'POST'):
        spec = request.form['T1']
        sql = "select * from doctordata where speciality='" + spec + "'"
        cur = getconnection()
        cur.execute(sql)
        result = cur.fetchall()
        return render_template('searchD.html', result=result)
    else:
        return render_template('searchD.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method == "POST"):
        email = request.form["T1"]
        password = request.form["T2"]

        s1 = "select * from logindata where email='"+email+"' AND password='"+password+"'"

        cur = getconnection()

        cur.execute(s1)
        a = cur.rowcount
        if (a == 1):
            data = cur.fetchone()
            ut = data[2]

            #create session
            session["email"]=email
            session["usertype"]=ut

            if (ut == "admin"):
                return redirect(url_for("admin_home"))
            elif (ut == "medical"):
                return redirect(url_for("medical_home"))
            elif (ut == "hospital"):
                return redirect(url_for("hospital_home"))
            else:
                return render_template("login.html", msg="usertype does not exist")
        else:
            return render_template("login.html", msg="Either email or password is incorrect")
    else:
        return render_template("login.html")

@app.route('/loginD')
def loginD():
    return render_template('loginD.html')

@app.route('/checklogin', methods=['GET', 'POST'])
def checklogin():
    if (request.method == 'POST'):
        email = request.form["T1"]
        password = request.form["T2"]
        # connection

        sql = "SELECT * FROM logindata where email='" + email + "' and password='" + password + "'"
        cur = getconnection()
        cur.execute(sql)
        n = cur.rowcount
        if (n > 0):
            # create cookie
            row = cur.fetchone()
            usertype = row[2]
            session["usertype"] = usertype
            session["email"] = email
            if (usertype == "admin"):
                return redirect(url_for('admin_home'))
            elif (usertype == "hospital"):
                return redirect(url_for('hospital_home'))
        else:
            return render_template("loginerror.html")

@app.route('/hospital_home')
def hospital_home():
    if 'usertype' in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'hospital':
            doctors = get_doctors(email)
            return render_template('hospital_home.html', doctors=doctors)
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('auth_error'))

@app.route("/showadmins")
def showadmins():
    if "usertype" in session:
        usertype = session["usertype"]
        email = session["email"]
        if usertype == "admin":
            cur=getconnection()
            cur.execute("SELECT * FROM admindata")
            result=cur.fetchall()
            return render_template("showadmins.html",result=result)
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/editadmin",methods=['GET','POST'])
def editadmin():
    if "usertype" in session:
        usertype = session["usertype"]
        email = session["email"]
        if usertype == "admin":
            if request.method == 'POST':
                email=request.form['email']
                cur=getconnection()
                cur.execute("SELECT * FROM admindata where email='" + email + "'")
                result = cur.fetchall()
                return render_template('editadmin.html', result=result)
            else:
                return redirect(url_for('showadmins'))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/editadmin1",methods=['GET','POST'])
def editadmin1():
    if "usertype" in session:
        usertype = session["usertype"]
        email = session["email"]
        if usertype == "admin":
            if request.method=='POST':
                name=request.form['T1']
                address=request.form['T2']
                contact=request.form['T3']
                email=request.form['T4']
                cur=getconnection()
                sql="update admindata set name='"+name+"', address='"+address+"', contact='"+contact+"' where email='"+email+"'"
                cur.execute(sql)
                n=cur.rowcount
                print(n,sql)
                if(n==1):
                    return render_template('editadmin1.html',result='success')
                else:
                    return render_template('editadmin1.html',result='failure')
            else:
                return render_template(url_for('showadmins'))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/delete_admin",methods=["GET","POST"])
def delete_admin():
        if ("usertype" in session):
            ut = session["usertype"]
            e1 = session["email"]
            if (ut == "admin"):
                if (request.method == "POST"):
                    email = request.form["H1"]
                    cur = getconnection()
                    con = "delete from admindata where email = '" + email + "'"
                    cur.execute(con)
                    b = cur.rowcount

                    if (b > 0):

                        return render_template("delete_admin.html", msg="Data Deleted")
                    else:
                        return render_template("delete_admin.html", msg="no data deleted")
                else:
                    return redirect(url_for("showadmins"))
            else:
                return redirect(url_for("auth_error"))
        else:
            return redirect(url_for("auth_error"))

@app.route("/admin_reg",methods=["GET","POST"])
def admin_reg():
    if "usertype" in session:
        usertype = session["usertype"]
        email = session["email"]
        if usertype == "admin":
            if(request.method=="POST"):
                name=request.form['T1']
                address=request.form['T2']
                contact=request.form['T3']
                email=request.form['T4']
                password=request.form['T5']
                cpassword=request.form['T6']
                usertype="admin"
                msg=""
                cur = getconnection()
                if(password!=cpassword):
                    msg="password not mached with confirm password "
                else:

                    s1="insert into admindata values('"+name+"','"+address+"','"+contact+"','"+email+"')"
                    s2="insert into logindata values('"+email+"','"+password+"','"+usertype+"')"

                cur=getconnection()
                cur.execute(s1)
                a=cur.rowcount
                cur.execute(s2)
                b=cur.rowcount
                if(a==1 and b==1):
                    msg="Data saved and login created "
                elif(a==1):
                    msg="Only data is saved"
                elif(b==1):
                    msg="Only login is created"
                else:
                    msg="No data is saved & no login data is created"
                return render_template("admin_reg.html",vgt=msg)
            else:
                return render_template("admin_reg.html")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/showmedical")
def showmedical():
    if "usertype" in session:
        usertype = session["usertype"]
        email = session["email"]
        if usertype == "admin":
            cur=getconnection()
            cur.execute("SELECT * FROM medicaldata")
            result=cur.fetchall()
            return render_template("showmedical.html",result=result)
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/medical_reg",methods=["GET","POST"])
def medical_reg():
    if "usertype" in session:
        usertype = session["usertype"]
        email = session["email"]
        if usertype == "admin":
            print("Hello1")
            if(request.method=="POST"):   #submit button
                # grab from data
                print("Hello2")
                name=request.form["T1"]
                owner=request.form["T2"]
                l_no=request.form["T3"]
                contact=request.form["T4"]
                address=request.form["T5"]
                email=request.form["T6"]
                password=request.form["T7"]
                cpassword=request.form["T8"]

                usertype="medical"

                msg=""
                if(password!=cpassword):
                    msg="Password not matched with cpassword"
                else:
                    cur=getconnection()
                    s1="insert into medicaldata values('"+name+"','"+owner+"','"+l_no+"','"+email+"','"+address+"','"+contact+"')"
                    s2="insert into logindata values('"+email+"','"+password+"','"+usertype+"')"
                    print(s1)
                    print(s2)
                    cur.execute(s1)
                    a=cur.rowcount

                    cur.execute(s2)
                    b=cur.rowcount
                    print(a,b)
                    if(a==1 and b==1):
                        msg="Data saved and login create"
                    elif(a==1):
                        msg="only data is saved"
                    elif(b==1):
                        msg="Only login is created"
                    else:
                        msg="No data is saved  and no login is created"
                #show responce
                return render_template("medical_reg.html",Naman=msg)
            else:
                return  render_template("medical_reg.html")
        else:
            return redirect(url_for("auth_error"))

@app.route('/hospital_reg', methods=['GET', 'POST'])
def hospital_reg():
    if 'usertype' in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'admin':
            if request.method == 'POST':
                name = request.form['T1']
                address = request.form['T3']
                contact = request.form['T5']
                email = request.form['T6']
                password = request.form['T7']
                ut = "hospital"
                photo = 'no'
                cur = getconnection()
                sql = "insert into hospitals values('" + name + "','" + address + "','" + contact + "','" + email + "','" + photo + "')"
                sql2 = "insert into logindata values('" + email + "','" + password + "','" + ut + "')"
                cur.execute(sql)
                n = cur.rowcount
                cur.execute(sql2)
                m = cur.rowcount
                if n == 1 and m == 1:
                    return render_template('hospital_reg.html', result="Data Saved")
                elif n == 1:
                    return render_template('hospital_reg.html', result="Data Saved but login not created")
                elif m == 1:
                    return render_template('hospital_reg.html', result="Login created but data not saved")
                else:
                    return render_template('hospital_reg.html', result="Error : Cannot Saved data")
            else:
                return render_template('hospital_reg.html')
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('auth_error'))


@app.route("/editmedical",methods=["GET","POST"])
def editmedical():
    if "usertype" in session:
        usertype = session["usertype"]
        email = session["email"]
        if usertype == "admin":
            if request.method == 'POST':
                email=request.form['H1']
                cur = getconnection()
                cur.execute("SELECT * FROM medicaldata where email='" + email + "'")
                result = cur.fetchall()
                return render_template('editmedical.html', result=result)
            else:
                return redirect(url_for('showmedical'))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/editmedical1",methods=["GET","POST"])
def editmedical1():
    if "usertype" in session:
        usertype = session["usertype"]
        email = session["email"]
        if usertype == "admin":
            if request.method=='POST':
                name=request.form['T1']
                owner=request.form['T2']
                l_no=request.form['T3']
                email=request.form['T4']
                address=request.form['T5']
                contact = request.form['T6']
                cur=getconnection()
                sql="update medicaldata set name='"+name+"', owner='"+owner+"', l_no='"+l_no+"',address='"+address+"',contact = '"+contact+"' where email='"+email+"'"
                cur.execute(sql)
                n=cur.rowcount
                print(n,sql)
                if(n==1):
                    return render_template('editmedical1.html',result='success')
                else:
                    return render_template('editmedical1.html',result='failure')
            else:
                return render_template(url_for('showmedical'))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/delete_medical",methods=["GET","POST"])
def delete_medical():
    if ("usertype" in session):
        ut = session["usertype"]
        e1 = session["email"]
        if (ut == "admin"):
            if (request.method == "POST"):
                email = request.form["H1"]
                cur = getconnection()
                con = "delete from medicaldata where email = '"+email+"'"
                cur.execute(con)
                b = cur.rowcount

                if (b > 0):

                    return render_template("delete_medical.html", msg="Data Deleted")
                else:
                    return render_template("delete_medical.html", msg="no data deleted")
            else:
                return redirect(url_for("show_medical"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/logout")
def logout():
    if "usertype" in session:
        session.pop("usertype",None)
        session.pop("usertype",None)
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

@app.route("/admin_home")
def admin_home():
    if ("usertype" in session):
        usertype = session["usertype"]
        email = session["email"]
        if (usertype == "admin"):
            photo = check_photo(email)
            return render_template("admin_home.html",photo=photo)
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/medical_home")
def medical_home():
    if ("usertype" in session):
        usertype = session["usertype"]
        email = session["email"]
        if (usertype == "medical"):
            photo = check_photo(email)
            return render_template("medical_home.html",photo=photo)
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/auth_error")
def auth_error():
    return render_template("auth_error.html")

@app.route("/changepass_admin",methods=["GET","POST"])
def changepass_admin():
    if("usertype" in session):
        ut = session["usertype"]
        e1 = session["email"]
        if(ut == "admin"):
            if(request.method == "POST"):
                old_password = request.form["T1"]
                new_password = request.form["T2"]
                confirm_password = request.form["T3"]

                msg=""
                if(new_password != confirm_password):
                    msg = "Password does not match"
                else:
                    cur=getconnection()
                    s1 = "update logindata set password = '"+new_password+"' where email= '"+e1+"' and password= '"+old_password+"' "
                    cur.execute(s1)
                    a=cur.rowcount
                    if(a==1):
                        msg = "Password changed successfully"
                    else:
                        msg = "Invalid password"
                    return render_template("changepass_admin.html",msg=msg)
            else:
                return render_template("changepass_admin.html")
        else:
            return  redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/changepass_medical",methods=["GET","POST"])
def changepass_medical():
    if("usertype" in session):
        ut = session["usertype"]
        e1 = session["email"]
        if(ut == "medical"):
            if(request.method == "POST"):
                old_password = request.form["T1"]
                new_password = request.form["T2"]
                confirm_password = request.form["T3"]

                msg=""
                if(new_password != confirm_password):
                    msg = "Password does not match"
                else:
                    cn = pymysql.connect(host="localhost",port=3306,user="root",passwd="",db="naman",autocommit=True)
                    s1 = "update logindata set password = '"+new_password+"' where email= '"+e1+"' and password= '"+old_password+"' "
                    cur=cn.cursor()
                    cur.execute(s1)
                    a=cur.rowcount
                    if(a==1):
                        msg = "Password changed successfully"
                    else:
                        msg = "Invalid password"
                    return render_template("changepass_medical.html",msg = msg)
            else:
                return render_template("changepass_medical.html")
        else:
            return  redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/medicine_add",methods=["GET","POST"])
def medicine_add():
    if("usertype" in session):
        ut = session["usertype"]
        e1 = session["email"]
        if(ut == "medical"):
            if(request.method=="POST"):
                name = request.form["T2"]
                company = request.form["T3"]
                unit_prize = request.form["T4"]
                description = request.form["T5"]
                email_of_medical = request.form["T6"]
                cur = getconnection()
                sql = "insert into medicine_data values(0,'"+name+"','"+company+"','"+unit_prize+"','"+description+"','"+email_of_medical+"')"

                cur.execute(sql)
                a=cur.rowcount
                if(a == 1):
                    msg = "Data Saved"
                else:
                    msg = "Data Not Saved"
                return render_template("medicine_add.html",vgt = msg)
            else:
                return render_template("medicine_add.html")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/show_medicine")
def show_medicine():
    if("usertype"in session):
        ut = session["usertype"]
        email = session["email"]
        if(ut == "medical"):
            cur = getconnection()
            sql = "select * from medicine_data"

            cur.execute(sql)
            a= cur.rowcount
            if(a > 0):
                data = cur.fetchall()
                return render_template("show_medicine.html",vgt=data)
            else:
                return render_template("show_medicine.html",msg="Not Found")
        else:
            return redirect(url_for("auth_error"))
    else:
        return  redirect(url_for("auth_error"))

@app.route("/edit_medicine",methods=["GET","POST"])
def edit_medicine():
    if("usertype" in session):
        ut = session["usertype"]
        e1 = session["email"]
        if(ut == "medical"):
            if(request.method=="POST"):
                med_id = request.form["H1"]
                cur = getconnection()
                con = "select * from medicine_data where med_id='" + med_id + "' "
                cur.execute(con)
                b = cur.rowcount

                if (b > 0):
                    data = cur.fetchone()
                    return render_template("edit_medicine.html", vgt=data)
                else:
                    return render_template("edit_medicine.html", msg="no data found")
            else:
                return redirect(url_for("show_medicine"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/edit_medicine_1",methods=["GET","POST"])
def edit_medicine_1():
    if("usertype" in session):
        ut=session["usertype"]
        e1=session["email"]
        if(ut=="medical"):
            if (request.method == "POST"):
                name = request.form["T1"]
                company = request.form["T2"]
                unit_prize = request.form["T3"]
                description = request.form["T4"]
                email_of_medical = request.form["T5"]
                cur = getconnection()
                con = "update medicine_data set name='" + name + "',company='" + company + "', unit_prize= '"+unit_prize+"',description= '"+description+"',email_of_medical= '"+email_of_medical+"'  "
                print(con)
                cur.execute(con)
                c = cur.rowcount

                if (c > 0):
                    return render_template("edit_medicine_1.html", msg="data change and save")
                else:
                    return render_template("edit_medicine_1.html", msg="data change are not save")
            else:
                return redirect(url_for("show_medicine"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/delete_medicine",methods=["GET","POST"])
def delete_medicine():
    if ("usertype" in session):
        ut = session["usertype"]
        e1 = session["email"]
        if (ut == "medical"):
            if (request.method == "POST"):
                med_id = request.form["H1"]
                cur = getconnection()
                con = "delete from medicine_data where med_id='" + med_id + "' "
                cur.execute(con)
                b = cur.rowcount

                if (b > 0):

                    return render_template("delete_medicine.html", msg="Data Deleted")
                else:
                    return render_template("delete_medicine.html", msg="no data deleted")
            else:
                return redirect(url_for("show_medicine"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/show_user_medicine")
def show_user_medicine():
    cur = getconnection()
    sql = "select * from medicine_medical"
    cur.execute(sql)
    a= cur.rowcount
    if(a > 0):
        data = cur.fetchall()
        return render_template("show_user_medicine.html",vgt=data)
    else:
        return render_template("show_user_medicine.html",msg="Not Found")

@app.route('/adminphoto')
def adminphoto():
    return render_template('photoupload_admin.html')

@app.route('/adminphoto1',methods=['GET','POST'])
def adminphoto1():
    if ('usertype' in session):
        usertype = session['usertype']
        email = session['email']
        if (usertype == 'admin'):
            if (request.method == 'POST'):
                file = request.files["F1"]
                if (file):
                    path = os.path.basename(file.filename)
                    file_ext = os.path.splitext(path)[1][1:]
                    filename = str(int(time.time()))+'.'+file_ext
                    filename = secure_filename (filename)
                    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='naman', autocommit=True)
                    cur = conn.cursor()
                    sql = "insert into photodata values('"+email+"','"+filename+"')"
                    try:
                        cur.execute(sql)
                        n = cur.rowcount
                        if (n==1):
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                            return render_template('photoupload_admin1.html',result="success")
                        else:
                            return render_template('photoupload_admin1.html',result="failure")
                    except:
                        return render_template('photoupload_admin1.html',result="duplicate")
            else:
                return render_template('photoupload_admin.html')
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route('/change_adminphoto')
def change_adminphoto():
    if ('usertype' in session):
        usertype = session['usertype']
        email = session['email']
        if (usertype == 'admin'):
            photo = check_photo(email)
            conn = pymysql.connect(host='localhost', port=3306, user='root', passwd="", db='naman',autocommit=True)
            cur = conn.cursor()
            sql = "delete from photodata where email = '"+email+"' "
            cur.execute(sql)
            n = cur.rowcount
            if(n>0):
                os.remove("./static/photos/"+photo)
                return render_template('change_adminphoto.html',data="success")
            else:
                return render_template('change_adminphoto.html',data="failure")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route('/medicalphoto')
def medicalphoto():
    return render_template('photoupload_medical.html')

@app.route('/medicalphoto1',methods=['GET','POST'])
def medicalphoto1():
    if ('usertype' in session):
        usertype = session['usertype']
        email = session['email']
        if(usertype == 'medical'):
            if(request.method == 'POST'):
                file = request.files["F1"]
                if (file):
                    path = os.path.basename(file.filename)
                    file_ext = os.path.splitext(path)[1][1:]
                    filename = str(int(time.time()))+'.'+file_ext
                    filename = secure_filename(filename)
                    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='naman', autocommit=True)
                    cur = conn.cursor()
                    sql = "insert into photodata values ('"+email+"','"+filename+"')"
                    try:
                        cur.execute(sql)
                        n = cur.rowcount
                        if(n == 1):
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                            return render_template('photoupload_medical1.html',result="success")
                        else:
                            return render_template('photoupload_medical1.html',result="failure")
                    except:
                        return render_template('photoupload_medical1.html1',result = "duplicate")
            else:
                return render_template('photoupload_medical.html')
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route('/change_medicalphoto')
def change_medicalphoto():
    if('usertype' in session):
        usertype = session['usertype']
        email = session['email']
        if (usertype == 'medical'):
            photo = check_photo(email)
            conn = pymysql.connect(host='localhost' , port=3306, user='root', passwd="", db='naman' , autocommit=True)
            cur = conn.cursor()
            sql = "delete from photodata where email = '"+email+"' "
            cur.execute(sql)
            n= cur.rowcount
            if(n>0):
                os.remove("./static/photos/"+photo)
                return render_template('change_medicalphoto.html',data="success")
            else:
                return render_template('change_medicalphoto.html',data="failure")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route('/doctor_reg', methods=['GET', 'POST'])
def doctor_reg():
    if 'usertype' in session:
        usertype = session['usertype']
        e1 = session['email']
        if usertype == 'hospital':
            if request.method == 'POST':
                name = request.form['T1']
                spec = request.form['T2']
                quali = request.form['T3']
                tm = request.form['T4']
                daylist = request.form.getlist('C1')
                mon = 'no'
                tue = 'no'
                wed = 'no'
                thu = 'no'
                fri = 'no'
                sat = 'no'
                sun = 'no'
                if 'mon' in daylist:
                    mon = 'yes'
                if 'tue' in daylist:
                    tue = 'yes'
                if 'wed' in daylist:
                    wed = 'yes'
                if 'thu' in daylist:
                    thu = 'yes'

                if 'fri' in daylist:
                    fri = 'yes'
                if 'sat' in daylist:
                    sat = 'yes'
                if 'sun' in daylist:
                    sun = 'yes'

                email_of_hospital = e1
                photo = 'no'
                cur = getconnection()

                sql = "insert into doctordata values('" + name + "','" + spec + "','" + quali + "','" + tm + "','" + mon + "','" + tue + "','" + wed + "','" + thu + "','" + fri + "','" + sat + "','" + sun + "','" + email_of_hospital + "','" + photo + "')"
                cur.execute(sql)
                n = cur.rowcount
                if n == 1:
                    return render_template('DoctorReg.html', data="Doctor Added", args=daylist)
                else:
                    return render_template('DoctorReg.html', data="Error: Cannot add doctor")
            else:
                return render_template('DoctorReg.html')
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('auth_error'))

@app.route('/edit_doctor', methods=['GET', 'POST'])
def edit_doctor():
    if 'usertype' in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'hospital':
            if request.method == 'POST':
                name = request.form['H1']
                spec = request.form['H2']
                doctor = getdoctor(name, spec, email)
                if doctor:
                    return render_template('EditDoctor.html', data=doctor)
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('auth_error'))

@app.route('/edit_doctor1', methods=['GET', 'POST'])
def edit_doctor1():
    if 'usertype' in session:
        usertype = session['usertype']
        e1 = session['email']
        if usertype == 'hospital':
            if request.method == 'POST':
                name = request.form['T1']
                oldname = request.form['oldname']
                spec = request.form['T2']
                spec1 = request.form['spec']
                if spec == 'Select To Change':
                    spec = spec1
                quali = request.form['T3']
                tm = request.form['T4']
                daylist = request.form.getlist('C1')
                mon = 'no'
                tue = 'no'
                wed = 'no'
                thu = 'no'
                fri = 'no'
                sat = 'no'
                sun = 'no'
                if 'mon' in daylist:
                    mon = 'yes'
                if 'tue' in daylist:
                    tue = 'yes'
                if 'wed' in daylist:
                    wed = 'yes'
                if 'thu' in daylist:
                    thu = 'yes'

                if 'fri' in daylist:
                    fri = 'yes'
                if 'sat' in daylist:
                    sat = 'yes'
                if 'sun' in daylist:
                    sun = 'yes'

                email_of_hospital = e1
                photo = 'no'
                cur = getconnection()

                sql = "update doctordata set name='" + name + "',speciality='" + spec + "',qualification='" + quali + "',t='" + tm + "',mon='" + mon + "',tue='" + tue + "',wed='" + wed + "',thu='" + thu + "',fri='" + fri + "',sat='" + sat + "',sun='" + sun + "' where name='" + oldname + "' AND speciality='" + spec1 + "' AND email_of_hospital='" + email_of_hospital + "'"
                cur.execute(sql)
                n = cur.rowcount
                if n == 1:
                    return redirect(url_for('hospital_home'))
                else:
                    return redirect(url_for('hospital_home'))
            else:
                return redirect(url_for('hospital_home'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('auth_error'))

@app.route('/delete_doctor', methods=['GET', 'POST'])
def delete_doctor():
    if 'usertype' in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'hospital':
            if request.method == 'POST':
                name = request.form['H1']
                spec = request.form['H2']
                doctor = getdoctor(name, spec, email)
                if doctor:
                    return render_template('DeleteDoctor.html', row=doctor, )
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('auth_error'))

@app.route('/delete_doctor1', methods=['GET', 'POST'])
def delete_doctor1():
    if 'usertype' in session:
        usertype = session['usertype']
        e1 = session['email']
        if usertype == 'hospital':
            if request.method == 'POST':
                name = request.form['H1']
                spec = request.form['H2']
                cur = getconnection()

                sql = "delete FROM doctordata where name='" + name + "' AND speciality='" + spec + "' AND email_of_hospital='" + e1 + "'"
                cur.execute(sql)
                n = cur.rowcount
                return redirect(url_for('hospital_home'))
            else:
                return redirect(url_for('hospital_home'))
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('auth_error'))

@app.route('/hospital_password', methods=['GET', 'POST'])
def hospital_password():
    if 'usertype' in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'hospital':
            if request.method == 'POST':
                oldpass = request.form['T1']
                newpass = request.form['T2']
                cur = getconnection()
                cur.execute("update logindata set password='" + newpass + "' where password='" + oldpass + "' AND email='" + email + "'")
                n = cur.rowcount
                if n > 0:
                    return render_template('hospital_password.html', result="Password Changed")
                else:
                    return render_template('hospital_password.html', result="Invalid Old Password")
            else:
                return render_template('hospital_password.html')
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('auth_error'))

@app.route('/hospital_profile')
def hospital_profile():
    if 'usertype' in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'hospital':
            cur = getconnection()
            cur.execute("SELECT * FROM hospitals where email='" + email + "'")
            result = cur.fetchone()
            return render_template('HospitalProfile.html', row=result)
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))

@app.route('/hospital_photo', methods=['GET', 'POST'])
def hospital_photo():
    if 'usertype' in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'admin':
            if request.method == 'POST':
                file = request.files['F1']
                email_hos = request.form['H1']
                if file:
                    path = os.path.basename(file.filename)
                    file_ext = os.path.splitext(path)[1][1:]
                    filename = str(int(time.time())) + '.' + file_ext
                    filename = secure_filename(filename)
                    cur = getconnection()
                    sql = "update hospitals set photo='" + filename + "' where email='" + email_hos + "'"

                    try:
                        cur.execute(sql)
                        n = cur.rowcount
                        if n == 1:
                            file.save(os.path.join('./static/hospital_photos', filename))
                            return render_template('hospital_photo.html', result="success")
                        else:
                            return render_template('hospital_photo.html', result="failure")
                    except:
                        return render_template('hospital_photo.html', result="duplicate")
            else:
                return render_template('show_hospitals.html')

        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('auth_error'))

@app.route('/show_hospitals')
def show_hospitals():
    if 'usertype' in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'admin':
            cur = getconnection()
            cur.execute("SELECT * FROM hospitals")
            result = cur.fetchall()
            return render_template('show_hospitals.html', result=result)
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('auth_error'))

@app.route('/chnage_hospital_photo', methods=['GET', 'POST'])
def chnage_hospital_photo():
    if 'usertype' in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'admin':
            if request.method == 'POST':
                email_hos = request.form['H1']
                photo = request.form['H2']

                cur = getconnection()
                sql = "update hospitals set photo='no' where email='" + email_hos + "'"
                cur.execute(sql)
                n = cur.rowcount
                if n > 0:
                    os.remove("./static/hospital_photos/" + photo)
                    return render_template('chnage_hospital_photo.html', data="success")
                else:
                    return render_template('chnage_hospital_photo.html', data="failure")
            else:
                return render_template('show_hospitals.html')
        else:
            return redirect(url_for('auth_error'))
    else:
        return redirect(url_for('auth_error'))

@app.route('/edit_hospital', methods=['GET', 'POST'])
def edit_hospital():
    if 'usertype' in session:
        usertype = session['usertype']
        e1 = session['email']
        if usertype == 'admin':
            email_of_hospital = request.form['H1']
            cur = getconnection()
            cur.execute("SELECT * FROM hospitals where email='" + email_of_hospital + "'")
            result = cur.fetchall()
            return render_template('EditHospital.html', result=result)
        else:
            return redirect(url_for('auth_error'))


@app.route('/edit_hospital1', methods=['GET', 'POST'])
def edit_hospital1():
    if 'usertype' in session:
        usertype = session['usertype']
        e1 = session['email']
        if usertype == 'admin':
            name = request.form['T1']
            address = request.form['T2']
            contact = request.form['T3']
            email_of_hospital = request.form['T4']
            sql = "update hospitals set hos_name='" + name + "',address='" + address + "',contact='" + contact + "' where email='" + email_of_hospital + "'"
            cur = getconnection()
            cur.execute(sql)
            n = cur.rowcount
            return redirect(url_for('hospital_home'))
        else:
            return redirect(url_for('auth_error'))


if __name__=="__main__":
    app.run(debug=True)