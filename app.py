from flask import Flask
from flaskext.mysql import MySQL
from flask import Flask,request,render_template,json,session,flash,redirect,url_for
import os

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'ba73b36c4356b4'
app.config['MYSQL_DATABASE_PASSWORD'] = '95ac4042'
app.config['MYSQL_DATABASE_DB'] = 'heroku_890aaae2be83a14'
app.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-east-02.cleardb.com'
mysql.init_app(app)
app.debug = True
app.secret_key = os.urandom(24)
qpair={}
def renderblog():
    filename = os.path.join(app.static_folder, 'questionnaire.json')
    with open(filename) as blog_file:
        data = json.load(blog_file)
    return data
@app.route("/")
def start():
    p = renderblog()
    p=p['questionnaire']
    st = "create table if not exists question ( username varchar(60) not null "
    for i in p["questions"]:
        st = st +","+ i['identifier'] + " varchar(60) not null "
    st = st +")"
    if("name" not in qpair):
              qpair["name"]="Name"
              for i in p["questions"]:
                         qpair[i["identifier"]]=i["headline"]
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(st)
    tmp=cursor.fetchall()
    conn.close()
    return render_template("index.html")
@app.route("/guest")
def guest():
     data = renderblog()
     tmp=data["questionnaire"]
     if("name" not in qpair):
              qpair["name"]="Name"
              for i in tmp["questions"]:
                         qpair[i["identifier"]]=i["headline"]
     st= "select * from question"
     conn = mysql.connect()
     cursor = conn.cursor()
     cursor.execute(st)
     tmp=cursor.fetchall()
     conn.close()
     return render_template("guest.html",data=tmp,header=qpair,length=len(tmp),session = session)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/Authenticate",methods=['POST'])
def Authenticate():
   try:
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
     cursor.execute("SELECT name from User where userName='" + username + "' and password='" + password + "'")
     name = cursor.fetchone()
     conn.close()
     session['username']=name[0]
     return render_template("welcome.html",name = name[0],session=session)
   except:
       flash("Session Expired")
       return redirect(url_for('start'))
    

@app.route("/welcome")
def welcome():
  try:
    tmp=renderblog()
    conn= mysql.connect()
    cursor = conn.cursor()
    if('username' in session):
        cursor.execute("select * from question where username = '"+session["username"]+"'")
        data = cursor.fetchone()
        if(data):
            return render_template("filled.html")
        else:
             return render_template("questions.html",dat = tmp['questionnaire']['questions'],name = session['username'],session=session)
    else:   
             flash("Please login")
             return redirect(url_for('start'))
  except:
      flash("Session Expired")
      return redirect(url_for('start'))

@app.route("/signout")
def signout():
    if( 'username' in session):
            session.pop('username',None)
            flash("Logged out!!")
    return redirect(url_for('start'))


@app.route("/tosignup")
def tosignup():
    return render_template("signup.html")

@app.route("/signup",methods=['POST'])
def signup():
  try:
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
  except:
      flash("Session Expired")
      return redirect(url_for('start'))  

@app.route("/question" , methods=['POST'])
def question():
     tmp=request.form.to_dict(flat=False)
     conn= mysql.connect()
     if("name" not in qpair):
              tmp=renderblog()['questionnaire']
              qpair["name"]="Name"
              for i in tmp["questions"]:
                         qpair[i["identifier"]]=i["headline"]
     cursor = conn.cursor()
     st="insert into question values("
     for i in qpair:
        if(i!="dbname"):
            an=""
            for j in range(len(tmp[i])):
                an=an+tmp[i][j]+", "
            an=an[:-2]
            st = st+ "'" + str(an) +"',"
     st=st[:-1]
     st+=")"
     cursor.execute(st)
     conn.commit()
     conn.close()
     return render_template("filled.html")


if __name__ == "__main__":
    app.run()