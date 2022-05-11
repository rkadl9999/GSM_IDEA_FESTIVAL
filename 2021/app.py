from flask import Flask, render_template
from flask import request
from flask import session
from flask.json import jsonify
import pymysql
from pymysql import NULL
from werkzeug.utils import redirect

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
#DataBase 정보
db = pymysql.connect(host='localhost',port=3306,user='root',passwd='root',db='project_gsm',charset='utf8')
#비밀키
app.secret_key = 'SECRET_KEY'
#변수
success = {'result' : 'true'}
false = {'result' : 'false'}


#Main
@app.route('/write')
def write():
    if 'user_id' in session:
        return render_template('posting.html')
    else:
        return redirect('/login')

@app.route('/new_user')
def new_user():
        return render_template('signup.html')

@app.route('/login', methods=['GET','POST']) #Login
def user_login():
    db.connect()
    user_id = request.args.get('user_id',NULL)
    password = request.args.get('password',NULL)
    cursor = db.cursor()
    sql = """SELECT password FROM user_info WHERE id = '%s'""" % (user_id)
    cursor.execute(sql)
    result = cursor.fetchall()
    result = str(list(result))[3:len(result)-5] #순수한 password 값만 빼오는 문장
    db.close()
    if password == result: #로그인 성공
        print('성공')
        session['user_id'] = user_id
        return success
    else: #로그인 실패
        return false
    
@app.route('/logout') #Logout
def logout():
    if 'user_id' in session:
        session.clear()
        return success
    else:
        return redirect('/login')

@app.route('/sign_up', methods=['GET','POST']) #Sign_Up
def sign_up():
    db.connect()
    user_id = request.form['user_id']
    password = request.form['password']
    cursor = db.cursor()
    if user_id != NULL and password != NULL:
        sql = """INSERT INTO user_info VALUES ('%s','%s',0,0,0,0)""" % (user_id,password)
        cursor.execute(sql)
        db.commit()
    else:
        db.close()
        return false
    db.close()
    return success

@app.route('/comunity', methods=['GET','POST']) #Post
def comunity():
        db.connect()
        num = request.args.get('num',NULL)
        cursor = db.cursor()
        sql = "SELECT * FROM board;"
        cursor.execute(sql)
        post_list = cursor.fetchall()
        db.close()
        if post_list == ():
            return 'No post !'
        else:
            if num != NULL:
                result = list(post_list[int(num)])
                return jsonify(result)
            else:
                result = list(post_list)
                f = open("board.txt",'w')
                for i in range(len(result)):
                    post = {'num' : result[i][0],
                            'title' : result[i][1],
                            'name' : result[i][2],
                            'view' : result[i][3],
                            'content' : result[i][4]}
                    print(post, file=f)
                f.close()
                f = open("board.txt",'r')
                result = f.readlines()
                f.close()
                return jsonify(result)
    
@app.route('/posting', methods=['GET','POST']) #Posting
def posting():
        db.connect()
        title = request.form['title']
        context = request.form['context']
        name = session['user_id']
        cursor = db.cursor()
        sql = """INSERT INTO board VALUES (NULL,'%s','%s',0,'%s')""" % (title,name,context)
        cursor.execute(sql)
        db.commit()
        db.close()
        return success
    
@app.route('/user_info') #유저 정보
def user():
    db.connect()
    user_id = request.args.get('id',NULL)
    cursor = db.cursor()
    sql = """SELECT * FROM user_info where id = '%s'""" % (user_id)
    cursor.execute(sql)
    user = cursor.fetchall()
    user_info = {'name' : user[0][0],
                     'coin' : user[0][2],
                     'outside' : user[0][3],
                     'no_clean' : user[0][4],
                     'choose_sit' : user[0][5]}
    sql = """SELECT * FROM board where name = '%s'""" % (user_id)   
    cursor.execute(sql)
    poster = cursor.fetchall()
    print(poster)
    db.close()
    return user_info
    
@app.route('/shop', methods=['GET','POST']) #shop
def shop():
        db.connect()
        cursor = db.cursor()
        username = request.args.get('id',NULL)
        num = request.args.get('list',NULL)
        exception = """SELECT coin FROM user_info WHERE id = '%s'""" % (username)
        cursor.execute(exception)
        exception = int(cursor.fetchall()[0][0])
        if exception <= 0:  #코인 예외 처리
            return false
        else:
            data = (num,num,username)
            sql = """UPDATE user_info SET coin = coin - 50 WHERE id = '%s'""" % (username)
            cursor.execute(sql)
            sql2 = """UPDATE user_info SET %s = %s + 1 WHERE id = '%s'""" % (data)
            cursor.execute(sql2)
            db.commit()
            sql3 = """SELECT coin FROM user_info where id = '%s'""" % (username)
            cursor.execute(sql3)
            current_coin = str(list(cursor.fetchall()))[2:len(cursor.fetchall())-3]
            sql4 = """SELECT * FROM user_info where id = '%s'""" % (username)
            cursor.execute(sql4)
            current_coupon = list(cursor.fetchall())
            db.close()
            finish = {'result' : 'true',
                      'current_coin' : current_coin,
                      'outside' : current_coupon[0][3],
                      'no_clean' : current_coupon[0][4],
                      'choose_sit' : current_coupon[0][5]}
            return finish
        
@app.route('/insert_coin', methods=['GET']) #Insert Coin
def coin():
    if 'user_id' in session:
        db.connect()
        cursor = db.cursor()
        coin = request.args.get('coin',NULL)
        username = session['user_id']
        if coin == NULL or coin == 0:
            return false
        else:
            data = (coin,username)
            sql = """UPDATE user_info SET coin = coin + %s WHERE id = '%s'""" % (data)
            cursor.execute(sql)
            db.commit()
            db.close()
            return success
    else:
        redirect('/login')

#실행
if __name__ =='__main__':
    app.run(host='0.0.0.0', debug=True)
