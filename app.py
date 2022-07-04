from flask import (Flask,
                   render_template,
                   redirect, 
                   request, 
                   session, 
                   flash)
from flask_sqlalchemy  import SQLAlchemy
from flask_migrate  import Migrate
from dotenv import load_dotenv
from os import  getenv, urandom 




def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY']= urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI']=getenv('POSTGRES')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    db = SQLAlchemy(app=app)
    Migrate(app= app, db = db)
    
    class User(db.Model): 
        id = db.Column(db.Integer, primary_key= True)
        name = db.Column(db.String, nullable = False)
        email = db.Column(db.String, nullable = False)
        password = db.Column(db.String, nullable= False)
    
    class Post (db.Model): 
        id = db.Column(db.Integer, primary_key = True)
        post = db.Column(db.String, nullable= False)
        user_who_sent = db.Column(db.String, nullable = False)
    
    
    
    
    @app.route('/')
    def index():
        return redirect('/signup')
    
  
    @app.route('/signup',methods=['GET','POST'])
    def signup():
        if request.method == 'POST':
            form = request.form   
            u = User(name = form['name'], email = form['email'], password = form['password'])
            
            try: 
                db.session.add(u)
                db.session.commit()
                return redirect('/login')
            
            # Tratamento de um erro  geral  em execução
            # Desvantagem: Menos Otimização de codigo -> Perda de perfomance
            # Vantagem: Flexibilidade de erros
            except Exception: 
                    return '<h1>OPS! Ocorreu um erro</h3>'
              
            
            
        return render_template('signup.html')

    @app.route('/login', methods =['GET','POST'])
    def login():
        #evento de envio de um verbo http
        if request.method== 'POST': 
            form = request.form 
            try: 
                u = User.query.filter_by(email = form['email'], password = form['password']).first()
                if u: 
                    session['logged']=True
                    session['name']= u.name
                    print(u)
                    return redirect('/feed')
                session.pop('_flash', None)
                flash('Usuario não cadastrado')
                return redirect('/login')
            except Exception as e:
                print(e) 
                return redirect('/login')
        return render_template('login.html')

 
    @app.route('/feed',methods = ['GET','POST'])
    def feed():
        
        try: 
             if not session['logged']: 
                 return redirect('/login')
             
             if request.method == 'POST': 
                 post = Post(post=request.form['tt'], user_who_sent=session['name'])
                 try:
                      db.session.add(post)
                      db.session.commit()
                      return redirect('/feed')
                 except Exception:
                     return '<h2>Erro com o banco de dados</h2>'            
             return render_template('feed.html', tts= Post.query.all())
        except KeyError: 
            return redirect('/login')
       
    return app
