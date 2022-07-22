from flask import Flask, render_template, request, session, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import yaml
import random
import string
from fpdf import FPDF
import datetime
import pendulum
import smtplib, ssl
from sqlalchemy import and_, or_, func, update
from email.message import EmailMessage

# app = Flask(__name__)
app = Flask('Lab Manangement System')
app.config['SECRET_KEY'] = "bahahahahah"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Setting database types: Local/Remote
ENV = 'dev'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:anuragrai123@localhost/test_database'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://psmgpdolnookgz:4816740729d6d898692fc41e611cb8ebc9ae75c78070e4bf94bf28023a0f67b3@ec2-34-235-198-25.compute-1.amazonaws.com:5432/dec5e4m23jr5dt'

# Creating database object
db = SQLAlchemy(app)

# Creating db Model
class Allotment(db.Model):
    __tablename__ = 'allotment'
    request_id = db.Column(db.String(5), primary_key =True)
    item_code = db.Column(db.String(5))
    issued_to = db.Column(db.String(100))
    issued_by = db.Column(db.String(100))
    original_DOI = db.Column(db.Date)
    status = db.Column(db.String(10))
    renewed_on = db.Column(db.Date)
    renewed_by = db.Column(db.String(100))

    def __init__(self, request_id, item_code, issued_to, issued_by, date_of_issue, status, renewed_on, renewed_by):
        self.request_id = request_id
        self.item_code = item_code
        self.issued_to = issued_to
        self.issued_by = issued_by
        self.date_of_issue = date_of_issue
        self.status = status
        self.renewed_on = renewed_on
        self.renewed_by = renewed_by

class Calendar(db.Model):
    __tablename__ = 'calendar'
    event_name = db.Column(db.String(50), primary_key=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    incharge = db.Column(db.String(100))
    mode = db.Column(db.String(20))
    venue = db.Column(db.String(100))
    guest = db.Column(db.String(100))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    description = db.Column(db.String(100))

    def __init__(self, event_name, start_time, end_time, incharge, mode, venue, guest, start_date, end_date, description):
        self.event_name = event_name
        self.start_time = start_time
        self.end_time = end_time
        self.incharge = incharge
        self.mode = mode
        self.venue = venue
        self.guest = guest
        self.start_date = start_date
        self.end_date = end_date
        self.description = description

class Equipments(db.Model):
    __tablename__ = 'equipments'
    item_code = db.Column(db.String(5), primary_key=True)
    name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    location = db.Column(db.String(500))
    paddress = db.Column(db.String(5000))
    specifications = db.Column(db.String(100))
    extras = db.Column(db.String(50))

    def __init__(self, item_code, name, quantity, location, paddress, specifications, extras):
        self.item_code = item_code
        self.name = name
        self.quantity = quantity
        self.location = location
        self.paddress = paddress
        self.specifications = specifications
        self.extras = extras

class Gmeet(db.Model):
    __tablename__ = 'gmeet'
    event_name = db.Column(db.String(50), primary_key=True)
    meet_link = db.Column(db.String(500))

    def __init__(self, event_name, meet_link):
        self.event_name = event_name
        self.meet_link = meet_link

class Requests(db.Model):
    __tablename__ = 'requests'
    request_id = db.Column(db.String(5), primary_key = True)
    item_code = db.Column(db.String(5))
    item_name = db.Column(db.String(100))
    email_id = db.Column(db.String(100))
    date_of_request = db.Column(db.Date)
    status = db.Column(db.String(10))

    def __init__(self, request_id, item_code, item_name, email_id, date_of_request, status):
        self.request_id = request_id
        self.item_code = item_code
        self.item_name = item_name
        self.email_id = email_id
        self.date_of_request = date_of_request
        self.status = status

class Users(db.Model):
    __tablename__ = 'users'
    password = db.Column(db.String(50))
    username = db.Column(db.String(50), primary_key=True)

    def __init__(self, password, username):
        self.password = password
        self.username = username

@app.route("/dashboard")
def dashboard():
    # for events of today
    today = datetime.datetime.now().day

    # for events of this week
    todayutc = pendulum.now()
    start = todayutc.start_of('week').to_datetime_string()[8:10]
    end = todayutc.end_of('week').to_datetime_string()[8:10]
    year = str(datetime.datetime.now().year)
    # _______________________________

    # for events of this month
    mon = str(datetime.datetime.now().month)
    mon = '0'+mon
    mon = mon[-2:]
    dicto = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
             '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
    mon = dicto[mon]
    # __________________________

    pen = db.session.query(Requests).filter(Requests.status=='pending').count()
    teve = db.session.query(Calendar).filter(Calendar.start_date.like(f'%/{today}/%')).count()
    weve = db.session.query(Calendar).filter(and_(Calendar.start_date >= f'{mon}/{start}/{year}' , Calendar.start_date <= f'{mon}/{end}/{year}')).count()
    meve = db.session.query(Calendar).filter(Calendar.start_date.like(f'{mon}%')).count()

    var = db.session.query(Equipments).filter(Equipments.quantity <= 5).all()
    var = [[i.item_code, i.name, i.quantity] for i in var]

    # To subtract the number of active and consumed equipments FROM allotments table
    var2 = db.session.query(Allotment.item_code, func.count(Allotment.status).label("count")).filter(or_(Allotment.status == 'Active', Allotment.status == 'Consumed')).group_by(Allotment.item_code).all()

    for i in range(len(var)):
        for j in range(len(var2)):
            if var[i][0] == var2[j][0]:
                var[i][2] -= var2[j][1]

    ceves = db.session.query(Calendar.event_name).all()

    # List of tables available for download
    tab = ['allotment','equipments','calendar','requests']

    if db.session.query(Gmeet).count() > 0:
        valp = 'set'
    else:
        valp = 'notset'

    return render_template("dashboard.html", data=[pen, teve, meve, weve, var, ceves, valp, tab])

@app.route("/home")
def home_page():
    links = []
    for c, i in db.session.query(Gmeet, Calendar).filter(Gmeet.event_name == Calendar.event_name).all():
        links.append([c.event_name, c.meet_link, i.incharge, i.guest, i.start_date, i.end_date])

    if links == []:
        links = None
    return render_template("home.html", data = links)

@app.route("/atlcalendar")
def atlcalendar():
    data = db.session.query(Calendar).order_by(Calendar.start_time).all()
    output = []
    for record in data:
        dic = {}
        dic['id'] = record.event_name
        dic['name'] = record.event_name
        dic['badge'] = f"{record.start_time} - {record.end_time}"
        dic['date'] = [f"{record.start_date}", f"{record.end_date}"]
        dic[
            'description'] = f"{record.description}<br><br><b>Incharge:</b> {record.incharge.title()}<br><b>Mentor:</b> {record.guest.title()}<br><b>Mode:</b> {record.mode}<br><b>Venue:</b> {record.venue}"
        dic['type'] = 'event'

        output.append(dic)

    return render_template("calendarn.html", output=output)

@app.route("/equipments")
def equipments():
    var = db.session.query(Equipments).all()
    var = [[i.item_code, i.name, i.quantity, i.location, i.paddress, i.specifications, i.extras] for i in var]

    # To subtract the number of active and consumed equipments FROM allotments table
    var2 = db.session.query(Allotment.item_code, func.count(Allotment.status).label("count")).filter(
        or_(Allotment.status == 'Active', Allotment.status == 'Consumed')).group_by(Allotment.item_code).all()

    for i in range(len(var)):
        for j in range(len(var2)):
            if var[i][0] == var2[j][0]:
                var[i][2] -= var2[j][1]


    return render_template("equipments.html", data=var)



@app.route("/", methods=['GET','POST'])
def login():
    msg = ''
    ico = ''
    if request.method=='POST':
        userDetails = request.form
        username = userDetails['username']
        password = userDetails['password']

        if db.session.query(Users).filter(and_(Users.username==username, Users.password==password)).count() >0:
            session['loggedin'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))

        else:
            msg = 'The login credentials, that were provided, are invalid.'
            ico = "fa fa-exclamation"

    return render_template("entry.html", msg=msg, ico=ico)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/inventory')
def inventory():
    data = db.session.query(Equipments.item_code, Equipments.name, Equipments.quantity, Equipments.location, Equipments.paddress, Equipments.specifications, Equipments.extras).order_by(Equipments.item_code.asc()).all()
    return render_template("inventory.html", data=data)

@app.route('/allotment')
def allotment():
    data = []
    for c in db.session.query(Allotment).all():
        data.append([c.request_id, c.item_code, c.issued_to, c.issued_by, c.original_DOI, c.status, c.renewed_on, c.renewed_by])

    con = [x for x in data if x[5].lower() == 'consumed']
    act = [y for y in data if y[5].lower() == 'active']
    pen = [y for y in data if y[5].lower() == 'pending']

    return render_template("allotment.html", data=data, con=con, pen=pen, act=act)

@app.route('/requests')
def requests():
    message = ''
    data = db.session.query(Requests.request_id, Requests.item_code, Requests.item_name, Requests.email_id, Requests.date_of_request, Requests.status).order_by(Requests.date_of_request).all()

    den = [x for x in data if x.status.lower() == 'denied']
    apr = [y for y in data if y.status.lower() == 'approved']
    pen = [y for y in data if y.status.lower() == 'pending']

    return render_template("requests.html", data=data, mess=message, apr = apr, den = den, pen = pen)

@app.route('/update_inv', methods=['POST', 'GET'])
def update_inv():
    if request.method=='POST':
        Details = request.form
        code = Details['code']
        item_name = Details['item_name']
        location = Details['location']
        quantity = Details['quantity']
        specifications = Details['specification']
        extras = Details['extras']

        db.session.query(Equipments).filter(Equipments.item_code == code).update({Equipments.name:item_name, Equipments.location:location, Equipments.quantity:quantity, Equipments.specifications:specifications, Equipments.extras:extras}, synchronize_session = False)
        db.session.commit()

        return redirect(url_for('inventory'))


@app.route('/update_event', methods=['POST', 'GET'])
def update_event():
    if request.method=='POST':

        print('Came to update')
        Details = request.form
        event_name = Details['event_name']
        startt = Details['startt']
        endt = Details['endt']
        description = Details['description']
        incharge = Details['incharge']
        guest = Details['mentor']
        mode = Details['mode']
        venue = Details['venue']

        dicto = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
                 '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}

        li = []
        for j in [Details['startd'], Details['endd']]:
            for i in dicto:
                if i == j[5:7]:
                    js = str(j)
                    month = dicto[i]
                    date = js[-2:]
                    year = js[:4]
                    js = '/'.join([month, date, year])
                    break
            li.append(js)

        startd = li[0]
        endd = li[1]

        db.session.query(Calendar).filter(Calendar.event_name == event_name).update({Calendar.start_date: startd, Calendar.end_date : endd, Calendar.mode : mode, Calendar.venue : venue, Calendar.incharge : incharge, Calendar.start_time : startt, Calendar.end_time : endt, Calendar.description : description, Calendar.guest : guest }, synchronize_session = False)
        db.session.commit()

        return redirect(url_for('calendar'))


@app.route('/add_inv', methods=['POST', 'GET'])
def add_inv():
    if request.method=='POST':
        Details = request.form
        code = Details['code']
        item_name = Details['item_name']
        location = Details['location']
        quantity = Details['quantity']
        specification = Details['specification']
        extras = Details['extras']
        paddress = Details['paddress']


        if db.session.query(Equipments).filter(Equipments.item_code == code).count() > 0:
            show = f'Item with code {code} already present!'
        else:
            row = Equipments(code, item_name, int(quantity), location, paddress, specification, extras)
            db.session.add(row)
            db.session.commit()

            return redirect(url_for('inventory'))

    data = db.session.query(Equipments.item_code, Equipments.name, Equipments.quantity, Equipments.location, Equipments.paddress, Equipments.specifications, Equipments.extras).order_by( Equipments.item_code.asc()).all()
    return render_template("inventory.html", msg = show, data = data)


@app.route('/add_event', methods=['POST', 'GET'])
def add_event():
    if request.method == 'POST':
        Details = request.form
        event_name = Details['event_name']
        startt = Details['startt']
        endt = Details['endt']
        description = Details['description']
        incharge = Details['incharge']
        guest = Details['mentor']
        mode = Details['mode']
        venue = Details['venue']

        dicto = {'01':'January', '02':'February','03':'March','04':'April','05':'May','06':'June','07':'July','08':'August','09':'September','10':'October','11':'November','12':'December'}

        li = []
        for j in [Details['startd'], Details['endd']]:
            for i in dicto:
                if i == j[5:7]:
                    js = str(j)
                    month = dicto[i]
                    date = js[-2:]
                    year = js[:4]
                    js = '/'.join([month, date, year])
                    break
            li.append(js)

        startd = li[0]
        endd = li[1]


        if db.session.query(Calendar).filter(and_(Calendar.event_name==event_name, Calendar.start_date==startd)).count() > 0:
            show = f'Event already exists!'  #confirm it`s implementation
        else:
            row = Calendar(event_name, startt, endt, incharge, mode, venue, guest, startd, endd, description)
            db.session.add(row)
            db.session.commit()

            return redirect(url_for('calendar'))



@app.route('/calendar')
def calendar(mg=''):
    data = db.session.query(Calendar).order_by(Calendar.start_time).all()
    output = []
    for record in data:
        dic = {}
        dic['id'] = record.event_name
        dic['name'] = record.event_name
        dic['badge'] = f"{record.start_time} - {record.end_time}"
        dic['date'] = [f"{record.start_date}",f"{record.end_date}"]
        dic['description'] = f"{record.description}<br><br><b>Incharge:</b> {record.incharge.title()}<br><b>Mentor:</b> {record.guest.title()}<br><b>Mode:</b> {record.mode}<br><b>Venue:</b> {record.venue}"
        dic['type'] = 'event'

        # ------------- For edit section

        dicto = {"January": '01', "February": '02', "March": '03', "April": '04', "May": '05', "June": '06',
                 "July": '07', "August": '08', "September": '09', "October": '10', "November": '11', "December": '12'}
        li = []
        for j in [record.start_date, record.end_date]:
            for i in dicto:
                if i is None:
                    continue
                if i.lower() in j.lower():
                    js = str(j)
                    js = js.replace(i, dicto[i])
                    js = js.replace('/', '-')
                    js = js.split('-')
                    js = '-'.join([js[2], js[0], js[1]])
                    break
            li.append(js)

        dic['startd'] = li[0]
        dic['endd'] = li[1]
        dic['startt'] = str(record.start_time)
        dic['endt'] = str(record.end_time)
        dic['descr'] = record.description
        dic['incharge'] = record.incharge
        dic['mentor'] = record.guest
        dic['mode'] = record.mode
        dic['venue'] = record.venue
        output.append(dic)


    return render_template("calendar.html", output=output, msg = mg)

@app.route('/delete_item/<string:id>', methods=['GET', 'POST'])
def delete_item(id):

    db.session.query(Equipments).filter(Equipments.item_code == id).delete()
    db.session.commit()

    return redirect(url_for('inventory'))

@app.route('/delete_event', methods=['GET', 'POST'])
def delete_event():

    db.session.query(Calendar).filter(Calendar.event_name == request.args.get('event_name_e')).delete()
    db.session.commit()

@app.route('/update_status/<string:id>,<string:code>,<string:dat>', methods=['GET','POST'])
def update_status(id, code, dat):
    data = request.form
    status = data['status']

    if status == 'Consumed':
        # cur.execute("update allotment set status=%s where item_code=%s and issued_to=%s and date_of_issue=%s",(status, id, per, dat))
        # cur.execute("update equipments set quantity = (quantity-1) where item_code=%s",(id,))
        db.session.query(Allotment).get(id).status = status
        db.session.commit()
        db.session.query(Equipments).filter(Equipments.item_code == code).update({Equipments.quantity: Equipments.quantity-1})
        db.session.commit()

    else:
        db.session.query(Allotment).get(id).status = status
        db.session.commit()

    return redirect(url_for('allotment'))

@app.route('/update_req/<string:id>,<string:email>,<string:sr>', methods=['GET','POST'])
def update_req(id, email, sr):
    if sr == 'denyf':
        data = request.form
        status = data['status']

        # cur.execute("update requests set status=%s where item_code=%s and email_id=%s",(status, id, email))

        db.session.query(Requests).get(id).status = status
        db.session.commit()

        return redirect(url_for('requests'))
    elif sr == 'appf':
        data = request.form
        pkey = data['request_id']
        item_code = data['item_code']
        email_id = data['email_id']
        issue_date = data['issue_date']
        issuer_name = data['issuer_name']
        startt = data['startt']
        endt = data['endt']
        loc = data['loc']
        additional = data['additional']
        if len(additional) < 0:
            additional = 'none'

        #database update
        # cur.execute("update requests set status='Approved' where item_code=%s and email_id=%s",(pkey, email_id))
        # cur.execute("INSERT INTO allotment(item_code, issued_to, issued_by, date_of_issue, status ) VALUES(%s,%s,%s,%s,'pending')",(item_code, email_id, issuer_name, issue_date))
        # conn.commit()

        db.session.query(Requests).filter(Requests.request_id==pkey).update({Requests.status:"Approved"})
        db.session.commit()
        row = Allotment(pkey, item_code, email_id, issuer_name, issue_date, 'pending', None, None)
        db.session.add(row)
        db.session.commit()

        #mail
        try:
            # msg = EmailMessage()
            # msg.set_content(f'Hey!\nYour Request for item: "{item_code}" has been approved by incharge: "{issuer_name}"\nYou are informed to collect the item anytime between {startt}hrs and {endt}hrs, during school days.\nVenue: "{loc}"\nAdditional Comments by the incharge-\n{additional}\n\n\n<This is a one way communication. Do not repond back!')
            # msg["Subject"] = "ATL Request Update"
            # msg["FROM"] = "testmailflaskapp@gmail.com"
            # msg["To"] = email_id
            #
            # context = ssl.create_default_context()
            #
            # with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
            #     smtp.starttls(context=context)
            #     smtp.login(msg["FROM"], "testmailflaskapp@123")
            #     smtp.send_message(msg)
            return redirect(url_for('requests'))
        except Exception as e:
            print(e)
            message = "Email Could not be send. Make sure you have an active internet connection"
            return render_template("requests.html", data=data, mess=message)


    return redirect(url_for('requests'))

@app.route('/place_request', methods=['GET','POST'])
def place_request():
    data = request.form
    item_code = data['item_code']
    item_name = data['item_name']
    email = data['email_id']
    date = data['today_date']
    # datech = date[-2:] + '-' + date[5:7] + '-' + date[:4]

    random_id = ''.join(random.choices(string.ascii_uppercase+string.digits, k=5)).upper()
    while db.session.query(Requests).filter(Requests.request_id == random_id).count() > 0:
        random_id = ''.join(random.choices(string.ascii_uppercase+string.digits, k=5)).upper()
    else:
        row = Requests(random_id, item_code, item_name, email, date, 'pending')
        db.session.add(row)
        db.session.commit()


    return redirect(url_for('equipments'))


@app.route('/gmeet', methods=['get','post'])
def gmeet():
    data = request.form
    event_name = data['evename']
    meet_link = data['meetlink']

    db.session.query(Gmeet).delete()
    db.session.commit()

    row = Gmeet(event_name, meet_link)
    db.session.add(row)
    db.session.commit()

    return redirect(url_for('dashboard'))

@app.route('/remove_gmeet', methods=['get','post'])
def remove_gmeet():
    db.session.query(Gmeet).delete()
    db.session.commit()

    return redirect(url_for('dashboard'))


# Downloading report section-
@app.route('/report',  methods=['get','post'])
def report():
    data = request.form
    table_name = data['tabname'].title()
    try:
        res = globals()[table_name].__table__.columns
        res = [i.name for i in res]

        result = db.session.query(globals()[table_name]).all()
        result = [[getattr(row,colname) for colname in res] for row in result]
        print(result)

        pdf = FPDF()
        pdf.add_page()
        page_width = pdf.w - 2 * pdf.l_margin
        pdf.l_margin = pdf.l_margin*2.8
        pdf.r_margin = pdf.r_margin*2.8


        pdf.set_font('Times', 'B', 20.0)
        # pdf.image('.//static//background2.jpg', 0, 0, pdf.w, pdf.h, 'JPG')
        pdf.image(
            'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQw0PGEgmhWcshuU9JhjfwzeBZSug995UzAGjdIKh3WKgEOL6aFxhpAUxmlKux5SZYHat4&usqp=CAU',
            page_width / 5, 5, 10, 10, 'PNG')

        pdf.cell(page_width, 0.0, 'LAB MANAGEMENT SYSTEM', align='C')
        pdf.ln(15)
        page_width = pdf.w - 2 * pdf.l_margin
        pdf.set_font('Courier', 'B', 18.0)
        pdf.cell(page_width, 0.0, f'{table_name}'.upper()+' REPORT', align='C')
        pdf.ln(15)

        pdf.set_font('Courier', '', 12)
        col_width = page_width/0.9
        pdf.ln(1)
        th = pdf.font_size

        page_lis = [1]
        i = 1
        for row in result:
            pdf.cell(page_width, 0.0, 'Record ' + str(i), align='C')
            pdf.ln(th)
            for column in range(len(row)):
                if pdf.page_no() not in page_lis:
                    # pdf.image('.//static//background2.jpg', 0, 0, pdf.w, pdf.h, 'JPG')
                    page_lis.append(pdf.page_no())
                    pdf.ln(15)
                pdf.set_font('Courier', 'B', 12)
                pdf.cell(col_width/4, th, '  '+str(res[column]).title() + ' : ', border=1) #align='C'
                pdf.set_font('Courier', '', 12)
                pdf.multi_cell(col_width/1.5, th, '  '+str(row[column]), border=1)
                # pdf.ln(th)
            pdf.ln(15)
            i += 1


        pdf.set_font('Times', '', 14.0)
        pdf.cell(page_width, 0.0, '-: End Of Report :-', align='C')

        return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                        headers={'Content-Disposition': f'attachment;filename={table_name+"_report"}.pdf'})
    except Exception as e:
        print(e)


if __name__ == "__main__":
    app.run()

