import hashlib
import os
import datetime
import sqlite3
from flask import Flask,render_template,request,g,session,redirect,url_for
from utils import query_stock

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE = os.path.join(app.root_path,'stockquery.db'),
	SECRET_KEY = 'd9e676b26dd741b785c7f7f1cded393a',
))
app.config.from_envvar('FLASKR_SETTINGS',silent=True)
	

def connect_db():
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv
	
def get_db():
	if not hasattr(g,'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db
	
@app.teardown_appcontext
def close_db(error):
	if hasattr(g,'sqlite_db'):
		g.sqlite_db.close()
		
def init_db():
	db = get_db()
	with app.open_resource('schema.sql',mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()
	
@app.cli.command('initdb')
def initdb_command():
	init_db()
	print ('Initialized the database.')

def encode_password(password):
	return hashlib.md5(('slat:stockquery'+password).encode()).hexdigest()
	
def create_user(username,password):
	#创建用户
	raw_password = encode_password(password)
	sql_script = """INSERT INTO user(username,password)
					VALUES('{}','{}')
				 """.format(username,raw_password)
	db = get_db()
	db.execute(sql_script)
	db.commit()
	

	
	
@app.cli.command('initadmin')
def initadmin_command():
	create_user('admin','123456')
	print ('Initialized the admin.')
	
def query_user(username):
	#查询用户
	db = get_db()
	sql_script = """SELECT * FROM user WHERE username='{}'
				 """.format(username)
	cur = db.execute(sql_script)
	user = cur.fetchone()
	return user
	
@app.cli.command('queryadmin')
def queryadmin_command():
	print (dict(query_user('admin')))
	


def add_history(user_id,stock_code,result):
	db = get_db()
	now = datetime.datetime.now()
	sql_script = """INSERT INTO history(user_id,stock_code,result,query_time)
					VALUES ('{}','{}','{}','{}')
				 """.format(user_id,stock_code,result,now)
	db.execute(sql_script)
	db.commit()
def query_all_history(user_id):
	db = get_db()
	sql_script = """SELECT * FROM history
					WHERE user_id={} ORDER BY query_time DESC
				 """.format(user_id)
	cur = db.execute(sql_script)
	histories = cur.fetchall()
	return histories
	

@app.route('/register/',methods=['GET','POST'])
def register():
	#用户注册功能
	context = {}
	if request.method == 'POST':
		#print (request.form)
		username = request.form.get('username')
		password = request.form.get('password')
		re_password = request.form.get('re_password')
		error = None
		
		if not username:
			error = '用户名不能为空'
		elif not (password and re_password):
			error = '请输入密码并确认密码'
		elif password != re_password:
			error = '两次密码不一致'
		elif query_user(username):
			error = '用户已存在'
			
		if error is None:
			create_user(username,password)
			return redirect(url_for('login'))
		else:
			context.update({
				'error':error,
				'username':username
			})
	return render_template('register.html',**context)

@app.route('/login/',methods=['GET','POST'])
def login():
	context = {}
	if request.method == 'POST':
		username = request.form.get('username')
		print (username)
		password = request.form.get('password')
		print (password)
		error = None
		
		if not username:
			error = '请输入用户名'
		else:
			user = query_user(username)
			if not user:
				error = '用户不存在'
			else:
				user_password = dict(user).get('password')
				if user_password != encode_password(password):
					error = '登录密码不正确，请确认密码或者用户名'
				else:
					session['login'] = True
					session['user'] = dict(user)
					return redirect(url_for('query'))
					
		context.update({
			'error':error,
			'username':username
		})
		
					
	return render_template('login.html',**context)
	
@app.route('/logout/')
def logout():
	session['login'] = False
	session['user'] = None
	return redirect(url_for('query'))


@app.route('/')
def query():
	context = {}
	stock_code = request.args.get('stock_code','')
	if stock_code:
		query_result = query_stock(stock_code)
		user = session.get('user')
		if user:
			add_history(user.get('id'),stock_code,query_result)
			
		context.update({
			'stock_code':stock_code,
			'query_result':query_result,
		})
	return render_template('demo_1.html',**context)
	
@app.route('/history/')
def history():
	user = session.get('user')
	if user:
		context = {
			'history': query_all_history(user.get('id'))
		}
	else:
		context = {'history':''}
	return render_template('demo_1.html',**context)
	
@app.route('/help/')
def help():
	help_str="自己查-_-"
	return render_template('demo_1.html',help=help_str)