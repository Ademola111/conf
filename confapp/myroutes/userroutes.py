"""this file contains all our routes, it is like the controller that determines what happhens when the user visit our app"""
import json
import requests, random
from unicodedata import category
from flask import make_response, render_template, request, redirect, url_for,flash, session
from sqlalchemy import desc

from confapp import app,db
from confapp.mymodels import State, Skill, User, Breakout, user_sessions, Contactus, Myorder, OrderDetails, Payment
from confapp.forms import LoginForm, ContactusForm
from confapp import Message, mail

@app.route('/')
def home():
    login = LoginForm()
    cont=ContactusForm()
    id = session.get('loggedin')
    userdeets = User.query.get(id)
    break_deets =Breakout.query.all() #db.session.query(Breakout).all()
    try:
        #connect to API
        response = requests.get('http:127.0.0.1:8082/api/v1.0/listall') #retrieving the json in the request
        hostel_json = json.loads(response.data)
        #retrieve the json in the request
        # response = requests.get('http:127.0.0.1:8082/api/v1.0/listall', auth=('sam', '1234'))
    
        #connect the json in the request
        hostel_json = response.json() #json.loads(response.text)
        hostel_json=json.dumps(response)
        status = hostel_json.get['status'] #to pick the status
    except:
            hostel_json={}

    #pass it to the template as hostel_json=hostel_json 
    return render_template('user/index.html',login=login, cont=cont, userdeets=userdeets, break_deets=break_deets, hostel_json=hostel_json )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=="GET":
        s=Skill.query.all()
        p=State.query.all()
        return render_template('user/register.html', s=s, p=p)
    else:
        email=request.form["email"]
        pwd1=request.form["pwd1"]
        pwd2=request.form["pwd2"]
        fname=request.form["fname"]
        lname=request.form["lname"]
        state=request.form["state"]
        skill=request.form["skill"]

        if email=="" or pwd1=="" or pwd2=="" or fname=="" or lname=="" or skill=="" or state=="":
            flash('Validation faild!')
            return redirect('/register')

        elif pwd1 != pwd2:
            flash('invalid credentials')
            return redirect('/register')

        else:
            prof=User(user_email=email, user_pass=pwd1, user_fname=fname,user_lname=lname,user_skillid=skill, user_stateid=state)
            db.session.add(prof)
            db.session.commit()
            id=prof.user_id
            session['loggedin']=id
            flash('Welcome onboard')
            return redirect('/userhome')

@app.route('/userhome')
def userhome():
    loggedin = session.get('loggedin') #pprotecting a page
    if loggedin == None:
        return redirect('/')
    else:
        cont=ContactusForm()
        userdeets = db.session.query(User).get(loggedin)
        return render_template('user/userhome.html', loggedin=loggedin, cont=cont, userdeets=userdeets)

@app.route('/logout')
def logout():
    session.pop("loggedin")
    return redirect('/')

@app.route('/user/login', methods=['GET','POST'])
def submit_login():
    login=LoginForm()
    cont=ContactusForm()
    username = request.form.get("username") #method 1
    pwd = login.pwd.data #method 2

    #validate
    if login.validate_on_submit():
        #querying the data base to know if user is signed up or not before login
        #deets = User.query.filter(User.user_email==username, User.user_pass==pwd).all() #method 1
        deets = User.query.filter(User.user_email==username).filter(User.user_pass==pwd).first()#method 1
        if deets:
            #retrieving user_id and then keep in session
            id=deets.user_id
            session['loggedin']=id
            return redirect('/userhome')
        else:
            #keep a failed message in flash, then redirect himto login again
            flash('Please login with valid credentials')
            return redirect('/')
    else:
        return render_template('user/index.html', login=login, cont=cont)

"""breakout session"""
@app.route('/user/breakout')
def user_breakout():
    loggedin=session.get('loggedin')    
    if loggedin == None:
        return redirect('/')
    else:
        cont=ContactusForm()
        userdeets = User.query.get(loggedin)
        skill=userdeets.user_skillid
        brksession = Breakout.query.filter(Breakout.break_skillid==skill).all()
        return render_template('user/breakout.html', brksession=brksession, userdeets=userdeets, cont=cont)

@app.route('/user/breakout/<id>')
def breakout_details():
    return "details updated"

@app.route('/user/regbreakout/', methods=['POST','GET'])
def reg_breakout():
    bid=request.form.getlist('bid')
    loggedin=session.get('loggedin')
    user = User.query.get(loggedin)

    #using sqlalchemy to delete a user session
    db.session.execute(f"DELETE FROM user_breakout WHERE user_id='{loggedin}'")
    db.session.commit()
    for i in bid:
        #method 1 SQL Alchemy core
        # q=user_sessions.insert().values(user_id=loggedin, breakout_id=i)
        # db.session.execute(q)
        # db.session.commit()

        # #method 2
        item = Breakout.query.get(i)
        user.mybreakouts.append(item)
        db.session.commit()
    return redirect('/user/regbreakout/')

@app.route('/user/editprofile/')
def editprofile():
    cont=ContactusForm()
    loggedin=session.get('loggedin')
    userdeets=User.query.get(loggedin)
    all_levels=Skill.query.all()
    all_state=State.query.all()
    return render_template('user/profile.html', userdeets=userdeets, all_levels=all_levels, all_state=all_state, cont=cont)

# @app.route('/user/update/<id>', methods=['POST', 'GET'])
# def update_profile(id):
#     loggedin=session.get('loggedin') #this will redirect to home when attempt of id hacking is none
#     if loggedin == None:
#         return redirect('/')
#     if request.method=='GET': #this will redirect the hacker to home when attempting to make changes to other users id
#         return(redirect(url_for('home')))
    
#     if int(loggedin) == int(id): #this will check if the user loggedin id is equal to the id in the route if not it will redirect to same profile
#         user=User.query.get(id)
#         user.user_fname=request.form.get('fname')
#         user.user_lname=request.form.get('lname')
#         user.user_phone=request.form.get('phone')
#         user.user_skillid=request.form.get('skill')
#         user.user_address=request.form.get('address')
#         user.user_state=request.form.get('state')
#         db.session.commit()
#         flash('Profile update successful')
#     return redirect('/user/editprofile')

"""using loggedin to verify id with route without id, then remember to update your user profile url by removing the id"""
@app.route('/user/update/', methods=['POST', 'GET'])
def update_profile():
    loggedin=session.get('loggedin') #this will redirect to home when attempt of id hacking is none
    if loggedin == None:
        return redirect('/')
    if request.method=='GET': #this will redirect the hacker to home when attempting to make changes to other users id
        return(redirect(url_for('home')))

    user=User.query.get(loggedin)
    user.user_fname=request.form.get('fname')
    user.user_lname=request.form.get('lname')
    user.user_phone=request.form.get('phone')
    user.user_skillid=request.form.get('skill')
    user.user_address=request.form.get('address')
    user.user_state=request.form.get('state')
    db.session.commit()
    flash('Profile update successful')
    return redirect('/user/editprofile')

"""contact form"""
@app.route('/user/contact', methods=['POST', 'get'])
def contact():
    cont=ContactusForm()
    fullname=cont.fullname.data
    email=cont.email.data
    message=cont.message.data
    if cont.validate_on_submit:
        dd=Contactus(contact_name=fullname, contact_email=email, contact_message=message)
        db.session.add(dd)
        db.session.commit()
        cid=dd.contact_id

        if cid:
            return json.dumps({"id":cid, "message":"message sent"})
        else:
            return 'Sorry, please try again'

# """contact form instructor format"""
# @app.route('/user/contact', methods=['POST'])
# def contact():
#     cont=ContactusForm()
#     if cont.validate_on_submit:
#         fullname=cont.fullname.data
#         email=cont.email.data
#         message=cont.message.data
#         dd=Contactus(contact_name=fullname, contact_email=email, contact_message=message)
#         db.session.add(dd)
#         db.session.commit()
#         return redirect('/')

@app.route('/demo/available')
def available():
    return render_template('user/search.html')

@app.route('/check/result')
def result():
    user = request.args.get('us')
    deet = User.query.filter(User.user_email==user).first()
    if deet:
        return f"{user} taken"
    else:
        return f"{user} Available"

@app.route('/check/lga')
def check_state():
    state = State.query.all()
    return render_template('user/load_lga.html', state=state)

@app.route('/demo/lga', methods=['post'])
def check_lga():
    # state = request.form.get('stateid')
    # res=db.session.execute(f"SELECT * FROM lga WHERE state_id={state}")
    # return f"LGS List for {state}"
    state = request.form.get('stateid')
    #TO DO: write a query that wll fetch from LGA table where state_id =state
    res = db.session.execute(f"SELECT * FROM lga WHERE state_id={state}")
    results = res.fetchmany(20)

    select_html = "<select>"
    for x,y,z in results:
        select_html = select_html + f"<option value='{x}'>{z}</option>"
    
    select_html = select_html + "</select>"

    return select_html

@app.route('/donate', methods=['GET', 'POST'])
def donation():
    if request.method=='GET':
        cont=ContactusForm()
        return render_template('user/donation.html', cont=cont)
    else:
        fullname=request.form.get('fullname')
        email = request.form.get('email')
        amt = request.form.get('amt')
        status = 'Pending'
        ref = int(random.random()*10000000)
        session['refno'] = ref

        db.session.execute(f"INSERT INTO donate SET fullname='{fullname}', email='{email}', amt='{amt}', status='{status}', ref='{ref}'")
        db.session.commit()
        return redirect("/confirmpay")

@app.route('/confirmpay')
def confirmpay():
    cont=ContactusForm()
    ref = session.get('refno')
    qry = db.session.execute(f"SELECT * FROM donate WHERE ref='{ref}'")
    data=qry.fetchone()
    return render_template('user/confirmpay.html', data=data, cont=cont )

@app.route('/user/showbreakout')
def showbreakout():
    loggedin=session.get('loggedin')
    if loggedin == None:
        return redirect('/')
    else:
        userdeets = User.query.get(loggedin)
        userskill= userdeets.user_skillid
        breakout = db.session.query(Breakout).filter(Breakout.break_skillid==userskill).all()
        cont=ContactusForm()
        return render_template('user/showbreakout.html', userdeets=userdeets, userskill=userskill, cont=cont, breakout=breakout)

#The user submits selected breakouts to this route
@app.route("/user/sendbreakout", methods=['POST','GET'])
def send_breakout():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/")
    if request.method=='POST':
        #retrieve form data, breakout ids
        bid = request.form.getlist('bid')

        #insert new recd into myorder,
        mo = Myorder(order_userid=loggedin)
        db.session.add(mo)
        db.session.commit()
        orderid = mo.order_id
        #generate a trans ref using random (save in session), insert into payment table
        ref = int(random.random() * 10000000)
        session['refno'] = ref
        #loop over the selected breakout ids and insert into
        #order_details, 
        totalamt = 0
        for b in bid:
            breakdeets = Breakout.query.get(b)
            break_amt = breakdeets.break_amt
            totalamt = totalamt + break_amt
            od = OrderDetails(det_orderid=orderid,det_breakid=b,det_breakamt=break_amt)
            db.session.add(od)

        db.session.commit()
        p = Payment(pay_userid=loggedin,pay_orderid=orderid,pay_ref=ref,pay_amt=totalamt)       
        db.session.add(p) 
        db.session.commit()
        return redirect("/user/confirm_breakout")    
    else:
        return redirect("/user/home")

#This route will show all chosen sessions and connect to paystack
@app.route("/user/confirm_breakout", methods=['POST','GET'])
def confirm_break():
    loggedin = session.get('loggedin')
    ref = session.get('refno')
    if loggedin == None or ref == None:
        return redirect("/")
    userdeets = User.query.get(loggedin) 
    deets = Payment.query.filter(Payment.pay_ref==ref).first() 

    if request.method == 'GET':          
        cont = ContactusForm()                
        return render_template("user/show_breakout_confirm.html",deets = deets,userdeets=userdeets,cont=cont)
    else:
        url = "https://api.paystack.co/transaction/initialize"
        
        data = {"email":userdeets.user_email,"amount":deets.pay_amt*100, "reference":deets.pay_ref}
        headers = {"Content-Type": "application/json", "Authorization":"Bearer sk_test_9ebd9bc239bcde7a0f43e2eab48b18ef1910356f"}

        response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))

        rspjson = json.loads(response.text) 
        if rspjson.get('status')==True:
            authurl=rspjson['data']['authorization_url']
            return redirect(authurl)
        else:
            return "please try again"

#4. This  is the landing page for paystack, you are to connect to paystack and check the actual details of the transaction, then update yopur database
@app.route("/user/payverify")
def paystack():
    reference = request.args.get('reference')
    ref = session.get('refno')
    #update our database 
    headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_9ebd9bc239bcde7a0f43e2eab48b18ef1910356f"}

    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    rsp =response.json()#in json format
    if rsp['data']['status'] =='success':
        amt = rsp['data']['amount']
        ipaddress = rsp['data']['ip_address']
        p = Payment.query.filter(Payment.pay_ref==ref).first()
        p.pay_status = 'paid'
        db.session.add(p)
        db.session.commit()
        return "Payment Was Successful"  #update database and redirect them to the feedback page
    else:
        p = Payment.query.filter(Payment.pay_ref==ref).first()
        p.pay_status = 'failed'
        db.session.add(p)
        db.session.commit()
        return "Payment Failed"  
    #return render_template("user/demo.html", response=rsp)

@app.route('/sendmail')
def sendmail():
    subject="Automated Email"
    sender="admin@conf.com"
    recipient = ["virgintinny@gmail.com"]
    
    #instantiate an object of Message
    # msg=Message(subject=subject, sender=sender, recipients=recipient, body="This is a sample email send from conference app")
    # mail.send(msg)
   

# method 2 : To send an HTML mail 

    msg=Message()
    msg.subject=subject
    msg.sender=sender
    msg.body = "Test Message Again"
    msg.recipients = recipient
    
    # sending HTML
    htmlstr = "<div>Thank you you have subscribed....<h1><p>You can continue here</p></h1></div>"

    msg.html=htmlstr
    with app.open_resource("invite.pdf") as fp:
        msg.attach("ademola_saveas.pdf", 'application/pdf', fp.read()) #here will save the file as ademola_saveas
        msg.attach("ademola.pdf", 'application/pdf', fp.read()) ##here will save the file as ademola

    mail.send(msg)
    return "Mail Sent"