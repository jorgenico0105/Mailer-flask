from flask import Blueprint, render_template, request,flash,redirect,url_for,current_app
from app.db import get_db
import sendgrid
from sendgrid.helpers.mail import *

bp = Blueprint('mail', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
def index():
    search = request.args.get('search')  # Buscamos los argumentos en la URL
    print(search)
    db, c = get_db()
    
    if search is None:
        c.execute('SELECT * FROM email')
    else:
        c.execute("SELECT * FROM email WHERE content LIKE %s", ('%' + search + '%',))
    
    mails = c.fetchall()
    
    return render_template('mails/index.html', mails=mails)

@bp.route('/test-env')#ruta creada solo por fines educativos y demostrativos
def test_env():
    return {
        "SENDGRID_KEY": current_app.config.get('SENDGRID_KEY'),
        "FROM_MAIL": current_app.config.get('FROM_MAIL')
    }
@bp.route('/create', methods=['GET','POST'])
def create():
	
	if request.method == 'POST':
		email=request.form.get('email')
		subject=request.form.get('subject')
		content=request.form.get('content')
		errors=[]
		if not email:
			errors.append('Email es obligatorio')
		if not subject:
			errors.append('Asunto es obligatorio')
		if not content:
			errors.append('Contenido es obligatorio')
		if len(errors)==0:
			send(email,subject,content)
			db,c=get_db()
			c.execute("INSERT INTO email (email,subject,content) VALUES (%s,%s,%s)",(email,subject,content))
			db.commit()
			return redirect(url_for('mail.index'))
		else:
			for error in errors:
				flash(error)
				
	return render_template('mails/crear.html')
def send(to,subject,content):
	sg=sendgrid.SendGridAPIClient(api_key=current_app.config.get('SENDGRID_KEY'))	
	from_email = Email(current_app.config.get('FROM_MAIL'))
	to_email=To(to)
	content=Content('text/plain',content)
	mail=Mail(from_email,to_email,subject,content)
	response=sg.client.mail.send.post(request_body=mail.get())
	print(response)