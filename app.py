from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
    
app=Flask(__name__)
app.secret_key = "thisissecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@localhost/trial'
db = SQLAlchemy(app)


class hosp_mgmt(db.Model):
    SSN_ID = db.Column(db.Integer, primary_key=True)
    Patient_Name = db.Column(db.String(80), unique=False, nullable=False)
    Patient_Age = db.Column(db.Integer, nullable=False)
    Date_of_Admission = db.Column(db.Date, nullable=False)
    Bed_type = db.Column(db.String(20), nullable=False)
    Address = db.Column(db.String(50), nullable=False)
    City = db.Column(db.String(20), nullable=False)
    State = db.Column(db.String(30), nullable=False)


class master_med(db.Model):
    med_id=db.Column(db.Integer, nullable=False, primary_key=True)
    med_name=db.Column(db.String(30), nullable=False)
    quant_avail=db.Column(db.Integer, nullable=False)
    rate=db.Column(db.Float, nullable=False)

class track_med(db.Model):
    sno=db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    med_id=db.Column(db.Integer, db.ForeignKey('master_med.med_id'))
    qty=db.Column(db.Integer, nullable=False)
    ssn_id=db.Column(db.Integer, db.ForeignKey('hosp_mgmt.SSN_ID'))


# Home Page    
@app.route('/home', methods=['GET','POST'])
def home():
    return render_template('home.html')



# Login Page
@app.route('/login', methods=['GET','POST'])
def login():
    if ('user' in session and session['user']=='admin'):
        return render_template('newRegistration.html')

    if request.method=='POST':
        uname=request.form.get('username')
        pword=request.form.get('pwd')
        if uname=='admin' and pword=='admin_pass':
            session['user']=uname
            flash("Login Successful")
            return render_template('home.html')
        else:
            flash("Incorrect username or password")


    return render_template('login.html')




# Patient Dropdown Functions
# New Patient Registration
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method=='POST':
        # return render_template('your_url.html', code=request.args['code']) 
        # --- use request.args in case of GET method
        # --- use request.form in case of POST method
        ssnid=request.form.get('ssnID')
        name=request.form.get('name')
        age=request.form.get('age')
        doa=request.form.get('doa')
        bedType=request.form.get('bedType')
        addr=request.form.get('addr')
        state=request.form.get('state')
        city=request.form.get('city')

        entry=hosp_mgmt(SSN_ID=ssnid, Patient_Name=name, Patient_Age=age, Date_of_Admission=doa,
        Bed_type=bedType, Address=addr, City=city, State=state)

        db.session.add(entry)
        db.session.commit()

        flash('Patient Successfully Registered!')
        #return redirect(url_for('newRegistration'))
    return render_template('newRegistration.html') 
    

# Update Patient Details
@app.route('/searchPatient', methods=['GET','POST'])
def search_patient():
    if request.method=='POST':
        ssnid=request.form.get('ssnID')
        return redirect(url_for("update_route", ssnId=ssnid))
    else:
        return render_template('updateSearch.html')

@app.route('/update/<ssnId>', methods=['GET','POST'])
def update_route(ssnId):
    if request.method=='POST':
        name=request.form.get('name')
        age=request.form.get('age')
        doa=request.form.get('doa')
        bedType=request.form.get('bedType')
        addr=request.form.get('addr')
        state=request.form.get('state')
        city=request.form.get('city')

            # entry=hosp_mgmt(Patient_Name=name, Patient_Age=age, Date_of_Admission=doa,
            # Bed_type=bedType, Address=addr, City=city, State=state)

        update= hosp_mgmt.query.filter_by(SSN_ID=ssnId).first()
        update.Patient_Name=name
        update.Patient_Age=age
        update.Date_of_Admission=doa
        update.Bed_type=bedType
        update.Address=addr
        update.City=city
        update.State=state

        db.session.commit()
        #return redirect('/'+ ssnId)
    update= hosp_mgmt.query.filter_by(SSN_ID=ssnId).first()
    return render_template('updatePatient.html', update=update)



# View All the patients in hospital
@app.route('/viewAll')
def viewAll():
    #if request.method=='POST':
    fetch=hosp_mgmt.query.all()
    return render_template('viewPatient.html', fetch=fetch)


# Delete Patient
@app.route('/findPatient', methods=['GET','POST'])
def find_patient():
    if request.method=='POST':
        ssnid=request.form.get('ssnID')
        return redirect(url_for("delete_patient", ssnId=ssnid))
    else:
        return render_template('deleteSearch.html')

@app.route('/delete/<ssnId>', methods=['GET','POST'])
def delete_patient(ssnId):
    if request.method=='POST':
        ssnId=request.form.get('ssnID')
        
        update= hosp_mgmt.query.filter_by(SSN_ID=ssnId).first()
        #update = hosp_mgmt.query.filter_by(SSN_ID=ssnId).first()

        db.session.delete(update)
        db.session.commit()
        return redirect('/findPatient')
    update = hosp_mgmt.query.filter_by(SSN_ID=ssnId).first()
    return render_template('delete.html', update=update)
        
    
# logout of the system
@app.route('/logout', methods=['GET','POST'])
def logout():    
    if ('user' in session and session['user']=='admin'):
        session.pop('user')
        flash("Logged out successfully!")
        return redirect('/login')


#Pharmacy Dropdown Functions Start
# search a patient details
@app.route('/pharmFind', methods=['GET','POST'])
def pharmFind_patient():
    if request.method=='POST':
        ssnid=request.form.get('ssnID')
        return redirect(url_for("displayMed", ssnId=ssnid))
    else:
        return render_template('pharmGetPatient.html')

# display details of patient alongwith medicine details
@app.route('/pharmDisplayMed/<ssnId>', methods=['GET','POST'])
def displayMed(ssnId):
   # if request.method==POST:
    display = hosp_mgmt.query.filter_by(SSN_ID=ssnId)
    res=db.session.query(track_med.qty, track_med.ssn_id, master_med.med_name, master_med.rate).join(master_med, track_med.med_id==master_med.med_id and track_med.ssn_id==ssnId).all()
    

    return render_template('pharmDisplayMed.html', display=display, res=res)

#issue more medicines
@app.route('/availCheck', methods=['GET','POST'])
def availCheck():
    if request.method=='POST':
        medname=request.form.get('mname')
        reqQty=request.form.get('qty')
        return redirect(url_for("issueMoreMedi", medname=medname, reqQty=reqQty))
    else:
        return render_template('availMediCheck.html')

@app.route('/issue/<medname>/<reqQty>', methods=['GET','POST'])
def issueMoreMedi(medname, reqQty):
    #if request.method=='POST':
    if ((medname==master_med.med_name) and (reqQty<=master_med.quant_avail)):
        issue=master_med.query.filter_by(med_name=medname).first()
        reqQty=request.form.get('qty')
        #issue=db.session.query(track_med.qty, master_med.med_name, master_med.rate).outerjoin(master_med, track_med.med_id==master_med.med_id).filter(med_name=medname).first()
        master_med.quant_avail=(master_med.quant_avail-reqQty)
        db.session.commit()
    # else:
    #     flash("Sorry!Not enough quantity available!")
    issue=master_med.query.filter_by(med_name=medname).first()
    return render_template('issueMoreMedi.html', issue=issue)
