from flask import Flask,request,session,redirect,url_for,render_template, flash
from flask_sqlalchemy import SQLAlchemy # Orm gerekli kütüphane
from flask_bcrypt import Bcrypt #Hashing gerekli kütüphane
from flask_session import Session #Oturum için session classi eklendi
import psycopg2
import re


app = Flask(__name__)
app.config["SECRET_KEY"] = "1776e8f2a5165e83985f079e"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123qwe123@localhost/flask-app'
app.config["SESSION_PERMANENT"]=False # Tarayıcı kapandığında oturum kapanıcak
app.config["SESSION_TYPE"]='sqlalchemy' # Oturum verileri postgresql üzerinden işlenicek
db=SQLAlchemy(app)
bcrypt = Bcrypt(app)


# User Model
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    username=db.Column(db.String(255),unique=True,nullable=False)
    email=db.Column(db.String(255),unique=True,nullable=False)
    password=db.Column(db.String(255),nullable=False)
    
    def __repr__(self):
        return f'User("{self.id}","{self.username}","{self.email}")'
# create table
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/user/index')

    return render_template('index-2.html')

@app.route('/user/register',methods=["POST","GET"])
def register():
    if 'user_id' in session:  # Oturum zaten açıksa
        return redirect(url_for('userIndex'))  # Kullanıcıyı index sayfasına yönlendir

    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')

        if username=="" or email=="" or password=="":
            flash('Lütfen bütün alanlari doldurun','danger')
            return redirect('/user/register')
        else:
            is_email=User().query.filter_by(email=email).first()
            is_username=User().query.filter_by(username=username).first()
            if is_email:
                flash("Bu email daha once alinmis",'danger')
                return redirect('/user/register')
            elif is_username:
                flash("Bu kullanici adi daha once alinmis","danger")
            else:
                hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
                user=User(username=username,email=email,password=hash_password)
                db.session.add(user)
                db.session.commit()
                flash('Kullanici Kaydi Basariyla Olusturuldu!','success')
                return redirect('/user/register')

    return render_template('register.html')

# Login Ekranı
@app.route('/user/login',methods=['GET','POST'])
def login():
    if 'user_id' in session:  # Oturum zaten açıksa
        return redirect(url_for('userIndex'))  # Kullanıcıyı index sayfasına yönlendir

    if request.method == 'POST':
        #Formdan bilgileri al
        username = request.form.get('your_name')
        password = request.form.get('your_password')
        
        # Alanların girilmiş olduğu kontrolü
        if username=="" or password=="":
            flash('Lütfen bütün alanlari doldurun','danger')
            return redirect('/user/login')
        else:
            user = User().query.filter(User.username == username).first()
            if user:
                if bcrypt.check_password_hash(user.password,password):
                    session['user_id'] = user.id
                    flash("Kullanici Girisi basarili",'success')
                    return redirect('/user/index')
                else:
                    flash("Sifre Hatali",'danger')
                    return redirect('/user/login')
            else:
                flash("Kullanici adi veya sifre hatali!",'danger')
                return redirect('/user/login')
    return render_template('login.html')

# User Ekranı
@app.route('/user/index',methods=['GET','POST'])
def userIndex():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        return render_template('index.html',user=user)  # Oturum açıkken index sayfasını göster
    else:
        return redirect(url_for('login'))  # Oturum kapalıysa login sayfasına yönlendir
    
    # if request.method == "POST": # Cikis islemi veya güncelleme islemleri olabilir?
    #     pass

@app.route('/user/logout',methods=['POST'])
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)