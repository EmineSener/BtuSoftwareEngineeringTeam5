from flask import Flask,request,url_for,render_template,redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SECRET_KEY"] = "1776e8f2a5165e83985f079e"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123qwe123@localhost/flask-app-anket2'
db=SQLAlchemy(app)

# User tablosu
class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)
    is_ok = db.Column(db.Boolean, default=False)

# Sorular tablosu
class Sorular(db.Model):
    soru_id = db.Column(db.Integer, primary_key=True)
    soru_metni = db.Column(db.String)

# Secenekler tablosu
class Secenekler(db.Model):
    secenek_id = db.Column(db.Integer, primary_key=True)
    soru_id = db.Column(db.Integer,db.ForeignKey('sorular.soru_id'),nullable=False)
    secenek_metni = db.Column(db.String)

# Yanitlar tablosu
class Yanit(db.Model):
    yanit_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),nullable=False)
    soru_id = db.Column(db.Integer, db.ForeignKey('sorular.soru_id'),nullable=False)
    secenek_id = db.Column(db.Integer, db.ForeignKey('secenekler.secenek_id'),nullable=False)

    
with app.app_context():
    db.create_all()

@app.route('/user/anket',methods=["POST","GET"])
def Anket():

    # Kullanıcı daha önce anket yapmıs mı? Bunun kontrol edilmesi gerek
    user_id = 1 # 1 id'li kullanıcı giriş yapmış olsun. Normalde mevcut oturumdan gelicek bu bilgi
    user = Users().query.filter(Users.user_id == user_id).first() # mevcut kullanıcıdan alabiliriz.
    if request.method == "GET":
        if user.is_ok == False: # Eğer anket daha önce yapılmadıysa anket sayfası yuklensin.
            return render_template('anket.html')
        else:
            return redirect('/user/index') # Yapıldıysa mevcut profil yüklensin

    else:
        yanitlar = {}
        for key, value in request.form.items():
            if key.startswith('Soru_'):
                soru_id = int(key.split('_')[1])  # Soru ID'sini ayır
                yanitlar[soru_id] = value
        
        # Toplanan yanıtları veritabanına kaydediyor
        for soru_id, secenek_id in yanitlar.items():
            yeni_yanit = Yanit(
                user_id=user_id,
                soru_id=soru_id,
                secenek_id=secenek_id
            )
            db.session.add(yeni_yanit)
        
        user = Users().query.filter(Users.user_id == user_id).first()
        user.is_ok = True
        db.session.commit()

        return render_template('test.html',yanit=yanitlar)
    
    

if __name__== "__main__":
    app.run(debug=True)