from flask import Flask,render_template,g,request,session,redirect,url_for
from database import get_db
import os
from werkzeug.security import generate_password_hash,check_password_hash
app = Flask(__name__)
app.secret_key=os.urandom(24)
@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()

def get_current_user():
    user_result=None
    if 'user' in session:
        user=session['user']
        db=get_db()
        user_cursor=db.execute('select * from users where name=? ',[user])
        user_result=user_cursor.fetchone()
    return user_result
@app.route('/')
def index():
    user=get_current_user()
    return render_template('home.html',user=user)
@app.route('/register',methods=['POST','GET'])
def register():
    user=get_current_user()
    if request.method=='POST':
        db=get_db()
        name=request.form['name']
        password=generate_password_hash(request.form['password'])
        db.execute('insert into users (name,password,expert,admin) values(?,?,?,?)',[name,password,'0','0'])
        db.commit()
        session['user']=name
        return redirect(url_for('index'))
    return render_template('register.html',user=user)
@app.route('/login',methods=["POST","GET"])
def login():
    user=get_current_user()
    if request.method=='POST':
        db=get_db()
        name=request.form['name']
        password=request.form['password']
        
        # Debug: Print the user data
        user_cur=db.execute('select * from users where name=?',[name])
        user_result=user_cur.fetchone()
        
        if user_result is None:
            return '<h1>User not found</h1>'
            
        # Debug: Print password comparison
        is_valid = check_password_hash(user_result['password'], password)
        print(f"Stored hash: {user_result['password']}")
        print(f"Password valid: {is_valid}")
        
        if is_valid:
            session['user']=user_result['name']
            return redirect(url_for('index'))
        else:
            return '<h1>The password is incorrect</h1>'
            
    return render_template('login.html',user=user)
@app.route('/logout')

def logout():

    session.pop('user',None)
    return redirect(url_for('index'))   
@app.route('/question')
def question():
    user=get_current_user()
    return render_template('question.html',user=user)
@app.route('/answer')
def answer():
    user=get_current_user()
    return render_template('answer.html',user=user)
@app.route('/ask')
def ask():
    user=get_current_user()
    return render_template('ask.html',user=user)

@app.route('/user')
def users():
    user=get_current_user()
    db=get_db()
    user_cursor=db.execute('select * from users')
    user_result=user_cursor.fetchall()
    return render_template('users.html',user=user,users=user_result)
@app.route('/promte/<user_id>')
def promote(user_id):
    db=get_db()
    db.execute('update users set expert=1 where id=?',[user_id])
    db.commit()
    return redirect(url_for('users'))
@app.route('/unanswered')
def unanswered():
    user=get_current_user()
    return render_template('unanswered.html',user=user)




if __name__ == '__main__':

    app.run(debug=True)
