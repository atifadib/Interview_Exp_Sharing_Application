from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from flaskext.markdown import Markdown
import hashlib

client = MongoClient()
db = client.msrit
app = Flask(__name__, static_url_path='')
Markdown(app)

@app.route('/')
def index():
	"""
	:return: Renders Main Home Page
	"""
	return render_template('index.html')

@app.route('/post',methods=['GET'])
def post():
	"""
	:return: Renders Form Page for Posting
	"""
	return render_template('post.html')

@app.route('/save',methods=['POST'])
def save():
	"""
	:return: Saves the provided Experience into the mongoDB Database.
	"""
	try:
		form_data = request.form
		name = form_data['name']
		company = form_data['company']
		experience = form_data['text']
		date = form_data['date']
		dup_hash = hashlib.sha1(str(name+date+company).encode('utf-8')).hexdigest()
		if len(list(db.interview_Hashes.find({'hash':dup_hash}))) == 0:
			with open('./static/'+dup_hash+'.txt','w') as f:
				f.write(name+"\n"+company+"\n"+date+"\n"+experience+"\n")
			doc = {'name':name,'company':company,'experience':dup_hash,'date':date,'stars':0}
			db.interviews.insert_one(doc);
		return jsonify({"success":"success"})
	except Exception as e:
		print("Error Occured While Saving: ",str(e))
		return jsonify({"success":str(e)})

@app.route('/find',methods=['GET'])
def find():
	"""
	:return: Renders FIND Page
	"""
	return render_template('find.html')

@app.route('/render_table',methods=['POST'])
def load():
	"""
	:return: Loads Data from MongoDB
	"""
	data = []
	for datum in db.interviews.find({}):
		d = { 'name':datum['name'],'company':datum['company'],'experience':datum['experience'],
			  'date':datum['date'],'stars':datum['stars']}
		data.append(d)
	return jsonify(data)

@app.route('/load_experience/<exp_hash>',methods=['GET'])
def load_exp(exp_hash):
	"""
	:param exp_hash: Unique HashID Generated for each shared experience
	:return:
	"""
	exp_hash += '.txt'
	data = []
	with open('./static/'+exp_hash,'r') as f:
		for l in f.readlines():
			data.append(l.strip())
	return render_template('experience.html',name=data[0],company=data[1],date=data[2],exp="\n".join(data[3:]))

@app.route('/resources',methods=['GET'])
def resources():
	"""
	:return: Renders Resource Page
	"""
	return render_template("resources.html")

@app.route('/update_like',methods=['POST'])
def update():
	"""
	:return: Updates the Like Counter
	"""
	try:
		form_data = request.form
		name = form_data['name']
		company = form_data['company']
		date = form_data['date']
		dup_hash = hashlib.sha1(str(name + date + company).encode('utf-8')).hexdigest()
		print(form_data,dup_hash)
		db.interviews.update({'experience':dup_hash},{'$inc':{"stars":1}})
		return jsonify({"success":"success"})
	except Exception as e:
		return jsonify({"success":str(e)})


if __name__ == '__main__':
	app.run()
