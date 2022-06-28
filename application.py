# Importing Required Libraries and Blueprints.

from datetime import date, timedelta
from unicodedata import category, name
from unittest import expectedFailure
from flask import Flask,render_template,redirect,jsonify, request,session, url_for
from numpy import False_
from sqlalchemy import false, true
from flask_mysqldb import MySQL
from cryptography.fernet import Fernet
from time import sleep
from datetime import timedelta
from matplotlib import pyplot
import datetime

# Configuring Flask App and Database.
app = Flask(__name__)
mysql = MySQL(app)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "money_tracker"
app.config["SORT_KEYS"] = False
app.config["JSON_SORT_KEYS"] = False
app.secret_key = Fernet.generate_key()
app.permanent_session_lifetime = timedelta(hours=12)

# Defining Routes.
@app.route("/")
def home():
    return redirect("/login")

@app.route("/register",methods=["POST","GET"])
def register():
    if request.method=="POST":
        input_name = request.form["name"]
        input_email = request.form["email"]
        input_mobile = request.form["mobile"]
        input_category = request.form["category"]
        input_password = request.form["password"]
        cur = mysql.connection.cursor()
        sleep(2)
        cur.execute("INSERT INTO users(full_name,email,mobile,category_id,password) values(%s,%s,%s,%s,%s)",(input_name,input_email,input_mobile,input_category,input_password))
        mysql.connection.commit()
        message = "Account Created !"
        return render_template('register.html',result = message)
    else:
       return render_template("register.html")


@app.route("/login",methods=["GET","POST"])
def login():
    if "email" in session:
            return render_template('profile.html',name=session["name"],email=session["email"],mobile=session["mobile"],city=session["city"],pincode=session["pincode"],password=session["password"],category=session["category"])
    elif request.method=="POST":
        input_email = request.form["email"]
        input_password = request.form["password"]
        cur = mysql.connection.cursor()
        count = cur.execute("SELECT email,password from users where email=%s",(input_email,))
        if count<=0:
            result = "Account with this Email doesn't exist !"
            return render_template('login.html',result=result)
        data = cur.fetchone()
        if input_password==data[1]:
            cur.execute("SELECT * from users where email=%s",(input_email,))
            data = cur.fetchone()
            name = data[1]
            email = data[2]
            mobile = data[3]
            city = data[4]
            pincode = data[5]
            password = data[7]
            dictionary = {
                1:"Employee [Stable Income]",
                2:"Self Employed [Variable Income]",
                3:"Student",
                4:"Housewife/Reitree",
                5:"Others",
            }
            session["id"] = data[0]
            category = dictionary[data[6]]
            session["category"] = dictionary[data[6]]
            session["name"] = data[1]
            session["email"] = data[2]
            session["mobile"] = data[3]
            session["city"] = data[4]
            session["pincode"] = data[5]
            session["password"] = data[7]
            return redirect("/app")
        else:
            result = "Invalid Password !"
            return render_template('login.html',result=result)
    else:
        return render_template('login.html')
        

@app.route('/logout')
def logout():
    if "email" in session:
        session.clear()
        return redirect("/login")
    else:
        return redirect("/login")


# Option Base Page Route
@app.route("/app")
def options():
    return render_template('option.html')

# Profile Routes

@app.route('/profile')
def profile():
    if "id" in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users where id=%s",(session["id"],))
        data = cur.fetchone()
        
        return render_template('profile.html',name=data[1],email=data[2],mobile=data[3],city=data[4],pincode=data[5],password=data[6],category=session["category"])
    else:
        return redirect("/login")

@app.route('/update_profile',methods=["GET","POST"])
def update_profile():
    if "id" in session:
        if request.method=="POST":
            input_name = request.form["fullname"]
            input_mobile = request.form["mobile"]
            input_city = request.form["city"]
            input_pincode = request.form["pincode"]
            input_password = request.form["password"]
            cur = mysql.connection.cursor()
            cur.execute("update users set full_name=%s,mobile=%s,city=%s,pincode=%s,password=%s where id=%s",(input_name,input_mobile,input_city,input_pincode,input_password,session["id"]))
            mysql.connection.commit()
            return redirect("/profile")
        else:
            return render_template('update_profile.html',fullname=session['name'],email=session["email"],mobile=session["mobile"],city=session["city"],pincode=session["pincode"],password=session["password"],category=session["category"])
    else:
        return redirect("/login")

# Source of Income and Expense Tracker Routes.
        
@app.route('/sources',methods=["GET","POST"])
def sources():
    if "email" in session:
        if request.method=="POST":
            input_monthly_pay = request.form["monthly_pay"]
            input_monthly_randomcash = request.form["cash_in"]
            input_monthly_loan = request.form["loan"]
            input_monthly_sip = request.form["sip_installment"]
            input_monthly_stock = request.form["stock"]
            cur = mysql.connection.cursor()
            cur.execute("select id from user_income")
            data = cur.fetchall()
            flag=true
            for ids in data:
                if session["id"] in ids:
                    cur.execute("UPDATE user_income set monthly_pay=%s,random_cash_in=%s,loan_installment=%s,sip_installment=%s,stock_investment=%s where id=%s",(input_monthly_pay,input_monthly_randomcash,input_monthly_loan,input_monthly_sip,input_monthly_stock,session["id"]))
                    mysql.connection.commit()
                    break
                else:
                    flag=false
            
            if flag==false:
                cur.execute("INSERT INTO user_income values(%s,%s,%s,%s,%s,%s)",(session["id"],input_monthly_pay,input_monthly_randomcash,input_monthly_loan,input_monthly_sip,input_monthly_stock))
                mysql.connection.commit()
            result = "Income Source Saved."
            return render_template('income.html',result=result)
        else:
            cur = mysql.connect.cursor()
            count = cur.execute("SELECT * FROM user_income where id=%s",(session["id"],))
            if count<=0:
                return render_template('income.html')
            else:
                data = cur.fetchone()
                return render_template('income.html',monthly_pay = data[1],random_cash=data[2],loan=data[3],sip=data[4],stock=data[5])
    else:
        return redirect("/login")

# Daily Expense Routes.

@app.route("/daily_expense",methods=["GET","POST"])
def daily_expense():
    if "id" in session:
        if request.method=="POST":
            try:
                input_date = date.today()
                input_amount = request.form["amount"]
                input_category = request.form["category"]
                input_importance = request.form["importance"]
                cur = mysql.connection.cursor()
                count = cur.execute("SELECT amount,exp_category,exp_importance FROM daily_expense where id=%s and date=%s",(session["id"],date.today()))
                card_length = 60
                if count>3:
                    session["card_length"] = 70
                if count>7:
                    session["card_length"] = 100
                if count>12:
                    session["card_length"] = 130
                data = cur.fetchall()
                sum=0
                for count in data:
                    sum = sum+count[0]
                
            except:
                return render_template('daily_expense.html',result="All Fields are Mandatory.",today_date = date.today(),card_length=session["card_length"])    
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO daily_expense values(%s,%s,%s,%s,%s,%s)",(session["id"],input_date,input_amount,input_category,input_importance,datetime.datetime.today().month))
            mysql.connection.commit()
            result = "Expense added !"
            dict1 = {1:"Food",2:"Clothing",3:"House Rent",4:"Public Transport",5:"Vehicle Fuel",6:"Party/Drinks",7:"Gift"}
            dict2 = {1:"UI",2:"NUI",3:"UNI",4:"NUNI"}
            return render_template('daily_expense.html',today_date=date.today(),total=sum,data=data,result=result,card_length=session.get("card_length"),dict1=dict1,dict2=dict2)
        else:
            cur = mysql.connection.cursor()
            count = cur.execute("SELECT amount,exp_category,exp_importance FROM daily_expense where id=%s and date=%s",(session["id"],date.today()))
            data = cur.fetchall()
            sum=0
            for count in data:
                sum = sum+count[0]
            dict1 = {1:"Food",2:"Clothing",3:"House Rent",4:"Public Transport",5:"Vehicle Fuel",6:"Party/Drinks",7:"Gift",8:"Others"}
            dict2 = {1:"UI",2:"NUI",3:"UNI",4:"NUNI"}
            return render_template("daily_expense.html",today_date = date.today(),total=sum,data=data,dict1=dict1,dict2=dict2)
    else:
        return redirect("/login")   

# Analysis Routes.

@app.route("/analysis",methods=["GET","POST"])
def analysis():
    if "id" in session:
        if request.method=="POST":
            if request.form["imp"]=="Analyse by Importance":

                cur = mysql.connection.cursor()
                count = cur.execute("SELECT sum(amount),exp_importance from daily_expense where id=%s group by exp_importance",(session["id"],))
                if count>0:
                    data = cur.fetchall()
                    x_axis = []
                    y_axis = []
                    dict1 = {1:"Urgent-Important",2:"Not Urgent-Important",3:"Urgent-Not Important",4:"Not Urgent-Not Important"}
                    for i in data:
                        if dict1[i[1]] not in x_axis: 
                            x_axis.append(dict1[i[1]]+" [{}]".format(i[0]))
                            y_axis.append(i[0])
                        else:
                            temp = x_axis.index(i)
                            i[1] = i[temp] + i[1]
                    
                    pyplot.pie(y_axis,labels=x_axis)
                    #pyplot.show()
                    pyplot.savefig('static/income_graph.png')
                    pyplot.close()
                    return render_template("graph.html")
            elif request.form["imp"]=="Analyse by Category":
                cur = mysql.connection.cursor()
                count = cur.execute("SELECT sum(amount),exp_category from daily_expense where id=%s group by exp_category",(session["id"],))
                if count>0:
                    data = cur.fetchall()
                    x_axis = []
                    y_axis = []
                    dict1 = {1:"Food",2:"Clothing",3:"House Rent",4:"Public Transport",5:"Vehicle Fuel",6:"Party/Drinks",7:"Gift",8:"Others"}
                    for i in data:
                        if dict1[i[1]] not in x_axis: 
                            x_axis.append(dict1[i[1]]+" [{}]".format(i[0]))
                            y_axis.append(i[0])
                        else:
                            temp = x_axis.index(i)
                            i[1] = i[temp] + i[1]
                    
                    pyplot.pie(y_axis,labels=x_axis)
                    #pyplot.show()
                    pyplot.savefig('static/income_graph.png')
                    pyplot.close()
                    return render_template("graph.html")
            elif request.form["imp"]=="Download Expense Report":
                cur = mysql.connection.cursor()
                count = cur.execute("SELECT sum(amount),exp_category from daily_expense where id=%s group by exp_category",(session["id"],))
                return render_template('analysis.html')

        else:
            return render_template("analysis.html")
    else:
        return redirect("/login")

if __name__=="__main__":
    app.run(debug=true)