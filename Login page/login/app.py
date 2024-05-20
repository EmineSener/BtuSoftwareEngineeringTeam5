from flask import Flask,request,session,redirect,url_for,render_template, flash,make_response,abort
from flask_sqlalchemy import SQLAlchemy # Orm gerekli kütüphane
from flask_bcrypt import Bcrypt #Hashing gerekli kütüphane
from flask_session import Session #Oturum için session classi eklendi
from flask_mail import Mail, Message #Mail gönderimi için kütüphane
from werkzeug.utils import secure_filename
import os
import random


app = Flask(__name__)
app.config["SECRET_KEY"] = "1776e8f2a5165e83985f079e"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123qwe123@localhost/flask-app'
app.config["SESSION_PERMANENT"]=False # Tarayıcı kapandığında oturum kapanıcak
app.config["SESSION_TYPE"]='sqlalchemy' # Oturum verileri postgresql üzerinden işlenicek
app.config["REMEMBER_COOKIE_DURATION"] = 3600 * 24 * 30  # 30 Günlük çerez
app.config['UPLOAD_FOLDER'] = 'Login Page/login/static/layout-bootstrap/ppimages/' # Yüklenen dosyaların hangi klasörde tutulacağının yolu
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
db=SQLAlchemy(app)
bcrypt = Bcrypt(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
#Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'testnodejs652@gmail.com'
app.config['MAIL_PASSWORD'] = 'cawwlagteesibkwm'
mail = Mail(app)


# User Model
class Users(db.Model):
    id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    name=db.Column(db.String(255),nullable=False)
    surname=db.Column(db.String(255),nullable=False)
    age = db.Column(db.Integer,nullable=False)
    profileimage = db.Column(db.String,nullable=True)
    username=db.Column(db.String(255),unique=True,nullable=False)
    email=db.Column(db.String(255),unique=True,nullable=False)
    password=db.Column(db.String(255),nullable=False)
    reset_code = db.Column(db.Integer,nullable=True)
    
    def __repr__(self):
        return f'User("{self.id}","{self.name}","{self.surname}","{self.age}","{self.profileimage}","{self.username}","{self.email}","{self.reset_code}")' # User model üzerinde attirbute degerlerine ulasabilmeyi saglar.
# create table
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('userIndex'))

    return render_template('visitorIndex.html')

def is_valid(name,min_length, max_length):
    # Başında veya sonunda boşluk varsa False döndür
    # Birden fazla boşluk içeriyorsa False döndür
    if ' ' in name:
        return False
    if len(name) < min_length or len(name) > max_length:
        return False
    return True

@app.route('/user/register',methods=["POST","GET"])
def register():
    if 'user_id' in session:  # Oturum zaten açıksa
        return redirect(url_for('userIndex'))  # Kullanıcıyı index sayfasına yönlendir

    if request.method == "POST":
        name = request.form.get('name')
        surname = request.form.get('surname')
        age = request.form.get('age')
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        re_password = request.form.get('re_password')

        if username==None or email==None or password==None or name==None or surname==None or age==None:      
            flash('Lütfen bütün alanlari doldurun','danger')
            return redirect('/user/register')
        elif not is_valid(name, 2, 50) or not is_valid(surname, 2, 50) or not is_valid(username, 4, 20) or not is_valid(password, 6, 20):
            flash("Geçersiz giriş. Lütfen belirtilen karakter sınırlarına uygun ve bosluk karekter kullanmadan kayıt yapın.","danger")
            return redirect('/user/register')
        else:
            is_email=Users().query.filter_by(email=email).first()
            is_username=Users().query.filter_by(username=username).first()
            if is_email:
                flash("Bu email daha once alinmis",'danger')
                return redirect('/user/register')
            elif is_username:
                flash("Bu kullanici adi daha once alinmis","danger")
            elif re_password != password:
                flash("Parolalar eslesmiyor",'danger')
            else:
                hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
                user=Users(name=name,surname=surname,age=age,username=username,email=email,password=hash_password,profileimage='/static/layout-bootstrap/ppimages/pp.jpg')
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
        remember_me = request.form.get('remember-me') # Kullanıcı bilgilerini saklamak için çerez oluşturulacak

        # Alanların girilmiş olduğu kontrolü
        if username=="" or password=="":
            flash('Lütfen bütün alanlari doldurun','danger')
            return redirect('/user/login')
        else:
            user = Users().query.filter(Users.username == username).first()
            if user:
                if bcrypt.check_password_hash(user.password,password):
                    session['user_id'] = user.id #session sözlüğünde user_id eklendi
                    if remember_me: # "Beni Hatırla" seçeneği işaretlendiğinde, kullanıcı adı ve şifreyi tarayıcı çerezine kaydet
                        resp = make_response(redirect('/user/index'))
                        resp.set_cookie("username", username, max_age=app.config["REMEMBER_COOKIE_DURATION"])
                        resp.set_cookie("password", password, max_age=app.config["REMEMBER_COOKIE_DURATION"])
                        return resp
                    else: # Eğer oturum sırasında "Beni hatırla" işaretlenmemişse, kullanıcı adı ve şifresi tarayıcıda çerez tutulmayacak ve eğer mevcut çerez varsa onu temizlicek.
                        if "username" in request.cookies:
                            resp = make_response(redirect('/user/index'))
                            resp.set_cookie('username',expires=0) #username çerezi siler.
                            resp.set_cookie('password',expires=0) #password çerezini siler.
                            return resp # tarayıcıya yollandı

                    return redirect('/user/index')
                else:
                    flash("Sifre Hatali",'danger')
                    return redirect('/user/login')
            else:
                flash("Kullanici adi veya sifre hatali!",'danger')
                return redirect('/user/login')
    return render_template('login.html')

# Sifre degistirme ekranı

@app.route('/user/change-password',methods=['GET','POST'])
def changePassword():
    if 'user_id' in session:
        return redirect(url_for('userIndex'))

    if request.method == "POST":
        your_email = request.form.get('your_email')
        if your_email == "":
            flash("Mail adresi girin",'danger')
            return redirect('/user/change-password')
        user = Users().query.filter(Users.email == your_email).first() # filter ile filter by farkı
        if user:
            user.reset_code = random.randint(100000, 999999)
            db.session.commit()
            
            msg = Message("Sifre Sifirlama Onay Kodu",sender="testnodejs652@gmail.com",recipients=[your_email])
            msg.body = f"Merhaba, sifrenizi degistirmek icin kullanmaniz gereken onay kodu: {user.reset_code}"
            mail.send(msg)
            flash("Onay kodu gonderiliyor. Mailinizi kontrol edin.",'success')  
            return redirect(url_for('confirmPassword', from_changePw=True)) # query string kullanarak su url'e yonlendirilir '/user/confirmPassword?from_confirm=True, redirect tek parametre olur bu yüzden url'e parametre yollarken doğrudan url yazmak yerine url_for fonksiyonu kullanılıyoruz.
        else:
            flash("Mevcut e-postaya ait bir kullanici bulunmuyor.",'danger')
            return redirect('/user/change-password')

    return render_template('change-password.html')

@app.route('/user/confirm-password',methods=['GET','POST'])
def confirmPassword():

    if 'user_id' in session:
        return redirect(url_for('userIndex'))

    if request.method == "POST":
        confirm_code = request.form.get('confirm_password')
        new_password = request.form.get('new_password')
        re_password = request.form.get('re_password')
        if confirm_code == "" or new_password=="" or re_password=="":
            flash("Lutfen Tum alanlari doldurun","danger")
            return redirect(url_for('confirmPassword',from_changePw=True))
        user = Users().query.filter(Users.reset_code == confirm_code).first()
        if not is_valid(new_password, 6, 20):
            flash("Geçersiz Sifre. Lutfen en az 6 karekter uzunlugunda ve bosluk karekteri kullanmadan sifrenizi girin.")
            return redirect(url_for('confirmPassword',from_changePw=True))
        if user:
            if new_password==re_password:
                hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                user.password = hashed_password
                user.reset_code = None
                db.session.commit()
                flash("Dogrulama kodu basarili. Sifreniz basariyla degistirildi.",'success')
                return redirect('/user/login')
            else:
                flash("Girdiginiz parolalar eslesmiyor.","danger")
                return redirect(url_for('confirmPassword',from_changePw=True))
        else:
            flash("Onay kodu hatali!",'danger')
            return redirect(url_for('confirmPassword',from_changePw=True))
    
    from_changePw = request.args.get('from_changePw', False) # Eğer query string aldıysa from_change degerine from_changePw sorgusunun cevabını ata yoksa bos
    if not from_changePw:
        return redirect('/user/change-password') # Eğer doğrudan geldiyse, değişim sayfasına geri dön.

    return render_template('confirm-password.html')


# User Ekranı
@app.route('/user/index',methods=['GET','POST'])
def userIndex():
    if 'user_id' in session:
        user_id = session['user_id']
        user = Users.query.get(user_id) #dogrudan user verisini getirmek için
        return render_template('index.html',user=user)  # Oturum açıkken index sayfasını göster
    else:
        return redirect(url_for('login'))  # Oturum kapalıysa login sayfasına yönlendir

@app.route('/user/logout',methods=['POST','GET'])
def logout():
    if request.method == 'POST':        
        session.clear()
        return redirect('/')
    return redirect(url_for('login')) # Bu sayfalar için 404 sayfası yapılması daha mantıklı(?=)

#Edit profile 
@app.route('/user/edit-profile',methods=["POST","GET"])
def edit_profile():
    if request.method =='GET':
        if 'user_id' in session:
            user_id = session['user_id']
            user = Users.query.get(user_id)
            return render_template('editProfile.html',user=user)
        else:
            abort(404)
    else:
        name = request.form.get('name')
        surname = request.form.get('surname')
        age = request.form.get('age')
        username = request.form.get('username')
        profile_photo = request.files.get('profile_photo')
        user_id = session['user_id']
        user = Users.query.get(user_id)

        if profile_photo and allowed_file(profile_photo.filename):
            filename = secure_filename(profile_photo.filename)
            profile_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_photo_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            user.profileimage = '/static/layout-bootstrap/ppimages/' + profile_photo.filename

        if username==None or name==None or surname==None:      
            flash('Lütfen bütün alanlari doldurun','danger')
            return redirect('/user/edit-profile')
        elif not is_valid(name, 2, 50) or not is_valid(surname, 2, 50) or not is_valid(username, 4, 20):
            flash("Geçersiz giriş. Lütfen belirtilen karakter sınırlarına uygun ve bosluk karekter kullanmadan kayıt yapın.","danger")
            return redirect('/user/edit-profile')
        else:
                user.name = name
                user.surname = surname
                user.age = age
                user.username = username
                db.session.commit()
                flash("Bilgileriniz basariyla guncellendi.","success")
                return redirect('/user/edit-profile')
@app.route('/user/my-profile',methods=['GET'])
def my_profile():
    if 'user_id' in session:
        user_id = session['user_id']
        user = Users.query.get(user_id)
        return render_template('my-profile.html',user=user)
    else:
        abort(404)
#Not Found router
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404
if __name__ == "__main__":
    app.run(debug=True)