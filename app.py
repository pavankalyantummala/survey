from flask import Flask
from flaskext.mysql import MySQL
from flask import Flask,request,render_template,json
import os
 
mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'EmpData'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
qpair={}
def renderblog():
    filename = os.path.join(app.static_folder, 'questionnaire.json')
    with open(filename) as blog_file:
        data = json.load(blog_file)
    return data
@app.route("/")
def start():
    p=renderblog()["questionnaire"]
    st = "create table if not exists "+p["name"]+"( username varchar(60) not null "
    qpair["dbname"]=p["name"]
    qpair["name"]="Name"
    for i in p["questions"]:
        qpair[i["identifier"]]=i["headline"]
        st = st +","+ i['identifier'] + " varchar(60) not null "
    st = st +")"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(st)
    conn.close()
    return render_template("index.html", name=p["name"])
@app.route("/guest")
def guest():
    st= "select * from "+ qpair["dbname"]
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(st)
    tmp=cursor.fetchall()
    conn.close()
    return render_template("guest.html",data=tmp,header=qpair,length=len(tmp))
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/Authenticate",methods=['POST'])
def Authenticate():
    username = request.form['username']
    password = request.form['password']
    conn=mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * from User where userName='" + username + "' and password='" + password + "'")
    data = cursor.fetchone()
    if data is None:
     conn.close()
     return render_template('login.html',msg="Username or Password is wrong",success=False)
    else:
     tmp = renderblog()
     cursor.execute("SELECT name from User where userName='" + username + "' and password='" + password + "'")
     name = cursor.fetchone()
     conn.close()
     return render_template("questions.html",dat = tmp['questionnaire']['questions'],name = name[0])

@app.route("/tosignup")
def tosignup():
    return render_template("signup.html")

@app.route("/signup",methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    conn= mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * from User where Username='" + username +"'")
    data = cursor.fetchone()
    if data is None:
     cursor.execute("insert into User values(null,'" + username+"','"+password+"','" + name + "')")
     conn.commit()
     conn.close()
     return render_template('login.html',msg="Registration Success!! Please Login",success=True)
    else:
     return render_template('signup.html',msg="Username already exists",success=False)

@app.route("/question" , methods=['POST'])
def question():
    tmp=request.form.to_dict(flat=False)
    conn= mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select * from "+qpair["dbname"]+" where username = '"+tmp["name"][0]+"'")
    data = cursor.fetchone()
    if(data):
        return render_template("success.html", msg="You have already filled the form")
    st="insert into "+qpair["dbname"]+" values("
    for i in qpair:
        if(i!="dbname"):
            st = st+ "'" + str(tmp[i][0]) +"',"
    st=st[:-1]
    st+=")"
    cursor.execute(st)
    conn.commit()
    conn.close()
    return render_template("success.html",msg = "Success")
if __name__ == "__main__":
    app.run()