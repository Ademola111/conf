"""this file contains all our routes, it is like the controller that determines what happhens when the user visit our app"""
import os, random, math
from unicodedata import category
from flask import make_response, render_template, request, redirect, url_for,flash, session 

from werkzeug.security import generate_password_hash, check_password_hash

from confapp import app,db
from confapp.mymodels import State, Skill, User, Admin, Breakout
from confapp.forms import LoginForm

@app.route('/admin/login')
def adminlogin():
    return render_template('admin/login.html')

# @app.route('/admin/submit/login', methods=['GET','POST'])
# def submit_admin():
#     admin_username=request.form.get('username')
#     admin_password=request.form.get('pwd')
#     adlog = session.get('admin')
        
#     #validation
#     if admin_username=="" or admin_password=="":
#         flash("Ensure to fill all field")
#         return redirect('/admin/login')
#     else:
#         k=db.session.query(Admin).filter(Admin.admin_username==admin_username).filter(Admin.admin_password==admin_password).first()
#         if k:
#             id=Admin.admin_id
#             session['admin']=k.admin_id
#             return redirect('/adminpage')
#         else:
#             flash('invalid login credential supplied ')
#             return redirect('/admin/login')

"""using password hash to check for pass """
@app.route('/admin/submit/login', methods=['POST'])
def submitlogin():
    admin_username=request.form.get('username')
    admin_password=request.form.get('pwd')
    #adlog = session.get('admin')
        
    #validation
    if admin_username=="" or admin_password=="":
        flash("Ensure to fill all field")
        return redirect('/admin/login')
    else:
        # k=db.session.query(Admin).filter(Admin.admin_username==admin_username).filter(Admin.admin_password==admin_password).first()
        kod=db.session.query(Admin).filter(Admin.admin_username==admin_username).first()
        formated_pwd=kod.admin_password
        chk = check_password_hash(formated_pwd, admin_password)
        if chk==True:
            # id=Admin.admin_id
            session['admin']=kod.admin_id
            return redirect('/admin/page')
        else:
            flash('invalid login credential supplied ')
            return render_template('admin/login.html',formated_pwd=formated_pwd)

@app.route('/admin/page')
def adminpage():
    adlog=session.get('admin')
    if adlog==None:
        return redirect('/admin/login')
    else:
        adminname=db.session.query(Admin).get(adlog)
        return render_template('admin/index.html', adminname=adminname, adlog=adlog)

@app.route('/admin/upload', methods=['GET', 'POST'])
def admin_upload():
    adlog = session.get('admin')
    if request.method=='GET':
        return render_template('admin/test.html', adlog=adlog)
    else:
        data=request.files.get('image')
        original_name=data.filename
        #generating random strings to be used as our filename
        #method 1
        fn=math.ceil(random.random()*10000000000)
        #spliting to get oiringinal extention
        ext = original_name.split('.')
        save_as = str(fn)+'.'+ext[-1] #not you can use -1 for this location to pick the last value on the list

        #better way to know your file extention
        #method 2
        extn = os.path.splitext(original_name)
        saveas = str(fn)+extn[1]
        #validating the file type to be uploaded
        allowed=['.jpg', '.png', '.gif']
        if extn[1].lower() in allowed:
            data.save(f'confapp/static/assets/img/{saveas}')
            return "submitted"
        else:
            return "file type not allowed"

@app.route('/admin/breakout')
def breakout():
    adlog = session.get('admin')
    if adlog == None:
        return redirect('/admin/login')
    else:
        break_deets = Breakout.query.all() #db.session.query(Breakout).all()
        return render_template('admin/breakout.html', break_deets=break_deets, adlog=adlog)

@app.route('/admin/addbreakout', methods=['GET', 'POST'])
def addbreakout():
    adlog = session.get('admin')
    if adlog == None:
        return redirect('/admin/login')
    else:
        if request.method=="GET":
            s=Skill.query.all()
            return render_template('admin/breakoutform.html', s=s, adlog=adlog)
        else:
            title=request.form.get('title')
            level=request.form.get('skill')

            #requesting image from form
            image=request.files.get('image')
            original_name = image.filename

            #checking if title and level is empty
            if title=="" or level=="":
                flash('title and skill level cannot be empty')
                return redirect('/admin/addbreakout')

            #checking if file is not empty
            if original_name !="":
                extension = os.path.splitext(original_name)
                if extension[1].lower() in ['.jpg','.png']:
                    fn=math.ceil(random.random()*10000000000)
                    save_as=str(fn)+extension[1]
                    image.save(f'confapp/static/assets/img/{save_as}')
                    
                    #inserting into the database
                    b = Breakout(break_title=title, break_picture=save_as, break_skillid=level)
                    db.session.add(b)
                    db.session.commit()
                    return redirect("/admin/breakout")
                else:
                    flash("File Type Not Allowed")
                    return redirect("/admin/addbreakout")
            else:
                save_as=""
                    
                #inserting into the database
                b = Breakout(break_title=title, break_picture=save_as, break_skillid=level)
                db.session.add(b)
                db.session.commit()
                return render_template('admin/breakout.html', adlog=adlog)

@app.route('/admin/breakout/delete/<id>')
def delete_breakout(id):
    adlog = session.get('admin')
    if adlog == None:
        return redirect('/admin/login')
    else:
        b=db.session.query(Breakout).get(id)
        db.session.delete(b)
        db.session.commit()
        flash(f"Breakout session(id) deleted")
        return redirect('/admin/breakout')


@app.route('/admin/logout')
def adminlogout():
    session.get('admin')
    session.pop('admin')
    return redirect('/admin/login')

@app.route('/admin/reg')
def registration():
    
    #users=db.session.query(User).join(State).join(Skill).all()
    # users=db.session.query(User,State, Skill).join(State).join(Skill).filter(Skill.skill_id==1).all()
    # users=db.session.query(User,State, Skill).join(State).join(Skill).filter(Skill.skill_id==1).all() #for filtering 
    # users = User.query.join(State).join(Skill).add_columns(State, Skill).all()
    # users=db.session.query(User,State, Skill).join(State).join(Skill).filter(User.user_fname.ilike('%ol%')).all()
    #users=User.query.join(State,User.user_id==State.state_id).all()
    users=User.query.outerjoin(State,User.user_stateid==State.state_id).add_columns(State).order_by(User.user_fname).all()
    users=User.query.filter_by(user_fname='bola').outerjoin(State,User.user_stateid==State.state_id).add_columns(State).order_by(User.user_fname).all() #note filter_by is ment to be used immediatly before left join
    return render_template('admin/allusers.html', users=users)

"""admin signup"""
@app.route('/admin/signup/', methods=['POST','GET'])
def adminsignup():
    if request.method=='GET':
        return render_template('admin/signup.html')
    else:
        username=request.form.get('username')
        pwd=request.form.get('pwd')
        compwd=request.form.get('compwd')

        if pwd == compwd:
            formated = generate_password_hash(pwd)
            ad = Admin(admin_username=username, admin_password=formated)
            db.session.add(ad)
            db.session.commit()
            flash('New user signed up')
            return redirect('/admin/login')
        else:
            flash('the two password do not match')
            return redirect('/admin/signup')