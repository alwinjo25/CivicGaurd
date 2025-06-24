from flask import Flask, render_template, request, redirect, url_for, flash, send_file, Response
import sqlite3
from io import BytesIO
from PIL import Image
from flask_mail import Mail, Message
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

app = Flask(__name__, template_folder="template")
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'guardcivic@gmail.com' 
app.config['MAIL_PASSWORD'] = 'zhgr aflh wvwt rgja'  

mail = Mail(app)
app.secret_key = 'your_secret_key_here'
user_name = txt_select = ""
comp_text = comp_code = comp1_type = ""
def create_table():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS user (username TEXT PRIMARY KEY, password TEXT,email TEXT,phone TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS complaint (complaint_type TEXT,email TEXT,complaint_code TEXT,photo BLOB,complaint_text TEXT,username TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS guests (complaint_type TEXT,complaint_code TEXT, photo BLOB, complaint_text TEXT,username TEXT,id INTEGER)')
def insert_data(username, password,email,phone):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('INSERT INTO user (username, password,email,phone) VALUES (?, ?, ?, ?)', (username, password,email,phone))

@app.route('/')
def start():  
    return render_template('start.html')


@app.route('/template/login.html')
def login():
    return render_template('login.html')
@app.route('/template/Home.html')
def home():
    return render_template('Home.html')

@app.route('/login', methods=['POST'])
def login_page():
    global user_name
    if request.method == 'POST':
        username = request.form['uname_txt']
        password = request.form['pwd_txt']

        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM user WHERE username=? AND password=?', (username, password))
            user = c.fetchone()
        if user:
            user_name=username
            return render_template("Home.html")
        else:
            flash('Invalid username or password', 'error')
            return render_template("login.html")
@app.route('/NewAccount')
def NewAccount():
    return render_template('NewAccount.html')
@app.route('/template/comp_register.html')
def comp_register():
    return render_template('comp_register.html')

@app.route('/register', methods=['POST'])
def register():
    global user_name
    if request.method == 'POST':
        username = request.form['uname_txt']
        password = request.form['pwd_txt']
        user_name=username
        email = request.form['email']
        phone=request.form['phone']
        

        insert_data(username, password, email, phone)
        flash('Account created successfully! You can now login.', 'success')
        return redirect(url_for('login'))
    
@app.route('/select', methods=['POST'])
def select():
    global txt_select
    if request.method == 'POST':
        txt_select=request.form['comp_type']
        value_to_pass = txt_select
        return render_template('comp_register.html', value_to_pass=value_to_pass)
    return redirect(url_for('comp_register'))

   
@app.route('/template/complaint_select.html')
def complaint_select():
    return render_template('complaint_select.html')


@app.route('/template/EditProfile.html')
def EditProfile():
    return render_template('EditProfile.html')

@app.route('/template/pwd.html')
def password():
    return render_template('pwd.html')

@app.route('/complaint', methods=['POST'])
def submit_complaint():
    global user_name
    global comp_code,comp_text,comp1_type
    if request.method == 'POST':
        comp_type=request.form['complaint_type']
        email = request.form['ccemail_txt']
        complaint_text = request.form['complaint-text']
        complaint_code = generate_complaint_code()
        photo=request.files['profile-photo-upload'].read() 
        print(comp_type,email,complaint_text,complaint_code,photo)
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO complaint (complaint_type,email, complaint_code, photo, complaint_text,username) VALUES (?, ?, ?, ?, ? ,?)",
                      (comp_type,email, complaint_code, photo, complaint_text,user_name))
        c.execute("INSERT INTO guests (complaint_type,complaint_code, photo, complaint_text,username) VALUES (?, ?, ?, ?, ?)",
                      (comp_type, complaint_code, photo, complaint_text,user_name))
        conn.commit()
        conn.close()
        comp_code=complaint_code
        comp1_type=comp_type
        comp_text=complaint_text
        return redirect(url_for('register_success'))
@app.route('/userProfile', methods=['POST'])
def userProfile():
    global user_name
    if request.method == 'POST':
        photo=request.files['profile-photo-upload'].read() 
        email = request.form['email']
        phone=request.form['phone']
         
        conn = sqlite3.connect('database1.db')
        c = conn.cursor()
        
        c.execute("INSERT INTO user_details (,username,email,phone) VALUES ( ?, ?, ?)",
                      (user_name,email,phone))
        conn.commit()
        conn.close()
        return redirect(url_for('Home.html'))
@app.route('/template/register_success.html')
def register_success():
    global comp_text,comp1_type,comp_code
    flash('Complaint registered successfully!', 'success')  

    return render_template('register_success.html',youcomNo_txt=comp_code,ctype_txt=comp1_type,comp_text=comp_text)

@app.route('/send_email',methods=['POST'])
def send_email():

    global comp1_type,comp_text
    msg=''
    if comp1_type == "Electrical and power":
        complaintType=comp1_type
        complaintText=comp_text
        dateTime= datetime.now()
        recipient = "shrithissurya@mcubeinfotech.com"
        subject = "hi"
        body = "hello"
        attachment_data = generate_pdf_attachment(complaintType,complaintText,dateTime)
        msg = Message(subject, sender='guardcivic@gmail.com', recipients=[recipient])
        msg.body = body
        msg.attach("complaint_details.pdf", "application/pdf", attachment_data) 
        mail.send(msg)   
    elif comp1_type == "Law and Order complaint":
        complaintType=comp1_type
        complaintText=comp_text
        dateTime= datetime.now()
        recipient = "sharshad2005@gmail.com"
        subject = "hi"
        body = "hello"
        attachment_data = generate_pdf_attachment(complaintType,complaintText,dateTime) 
        msg = Message(subject, sender='guardcivic@gmail.com', recipients=[recipient])
        msg.body = body
        msg.attach("complaint_details.pdf", "application/pdf", attachment_data) 
        mail.send(msg)
    elif comp1_type == "Land and revenue":
        complaintType=comp1_type
        complaintText=comp_text
        dateTime= datetime.now()
        recipient = "josephalwin025@gmail.com"
        subject = "hi"
        body = "hello"
        attachment_data = generate_pdf_attachment(complaintType,complaintText,dateTime) 
        msg = Message(subject, sender='guardcivic@gmail.com', recipients=[recipient])
        msg.body = body
        msg.attach("complaint_details.pdf", "application/pdf", attachment_data)  
        mail.send(msg)
    return render_template("Home.html")

def generate_pdf_attachment(complaintType, complaintText, dateTime):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    p.setFont("Helvetica", 12)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(15, 750, "CIVIC GUARD")

    p.setFont("Helvetica", 12)
    p.drawString(15, 730, "Date: " + str(dateTime))

    p.drawString(15, 710, "To,")
    p.drawString(15, 695, "Municipal Corporation")
    p.drawString(15, 680, "City Name")

    p.drawString(15, 660, "Subject: Complaint regarding " + complaintType)

    p.drawString(15, 640, "Dear Sir/Madam,")


    y = 620
    lines = complaintText.split("\n")
    for line in lines:
        p.drawString(15, y, line)
        y -= 15  

    p.drawString(15, 420, "Thank you for your attention to this matter.")
    p.drawString(15, 400, "Yours sincerely,")
    p.drawString(15, 385, "Your Name")

    p.save()
    buffer.seek(0)
    return buffer.getvalue()       
@app.route('/changePassword', methods=['POST'])
def changePassword():
    if request.method == 'POST':
        oldPass = request.form['old_pwd']
        newPass = request.form['new_pwd']
        confirmPass = request.form['cnf_pwd_txt']
        
      
        if newPass != confirmPass:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('changePasswordForm'))

       
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        
        c.execute("SELECT password FROM users WHERE username = ?", (user_name,))
        row = c.fetchone()
        if row:
            saved_password = row[0]
            if saved_password == oldPass:
                
                c.execute("UPDATE users SET password = ? WHERE username = ?", (newPass, user_name))
                flash('Password changed successfully', 'success')
                conn.commit()
                conn.close()
                return redirect(url_for('EditProfile'))
        
        flash('Error occurred while changing password.', 'error')
        conn.close()
        return redirect(url_for('changePasswordForm'))
    
    return redirect(url_for('register_success'))

@app.route('/changePasswordForm')
def changePasswordForm():
    return render_template('change_password.html')
                   


def generate_complaint_code():
    import uuid
    return str(uuid.uuid4().hex)[:8].upper()

@app.route('/photo/<int:photo_id>')
def view_photo(photo_id):
   
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    
    c.execute("SELECT photo FROM guests WHERE photo_id = ?", (photo_id,))
    photo_blob = c.fetchone()[0]

    
    conn.close()

    
    photo_stream = BytesIO(photo_blob)

    image = Image.open(BytesIO(photo_stream))

    
    photo_stream.seek(0)

    
    return render_template("complaint-list.html", image=image.show())


@app.route('/image/<int:image_id>')
def get_image(image_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("select photo from guests where id=?", (image_id,))
    image_data = c.fetchone()[0]
    return Response(image_data, mimetype='image/png')


@app.route('/complaint_list')
def complaint_list():
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM guests")
    data = c.fetchall()
    conn.close()
    
    return render_template('complaint-list.html', data=data)

@app.route('/search_by_code', methods=['POST'])
def search_by_code():
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    search_code = request.form['search_code']
    
    c.execute("SELECT * FROM guests WHERE complaint_code = ?", (search_code,))
    search_results = c.fetchall()
    conn.close()
    
    return render_template('complaint-list.html', data=search_results)


@app.route('/search_by_type', methods=['POST'])
def search_by_type():
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    search_type = request.form['search_type']
    
    c.execute("SELECT * FROM guests WHERE complaint_type LIKE ?", ('%' + search_type + '%',))
    search_results = c.fetchall()
    conn.close()
    
    return render_template('complaint-list.html', data=search_results)

if __name__ == '__main__':
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        create_table()  
    app.run(debug=True)
