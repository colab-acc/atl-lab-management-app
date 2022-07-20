from flask import Flask, render_template, request, session, redirect, url_for, Response
from flask_mysqldb import MySQL
import pymysql
import yaml
from fpdf import FPDF
import datetime
import pendulum
import smtplib, ssl
from email.message import EmailMessage

# app = Flask(__name__)
app = Flask('Lab Manangement System')


# Configuring database
db = yaml.load(open('db.yaml'))
app.config["MYSQL_HOST"] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['SECRET_KEY'] = db['my_secret_key']


mysql = MySQL(app)


@app.route("/dashboard")
def dashboard():
    cur = mysql.connection.cursor()

    # for events of today
    today = datetime.datetime.now().day

    # for events of this week
    today = pendulum.now()
    start = today.start_of('week').to_datetime_string()[8:10]
    end = today.end_of('week').to_datetime_string()[8:10]
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

    cur.execute("select count(*) from requests where status='pending'")
    pen = cur.fetchone()
    cur.execute(f"select count(*) from calendar where start_date like '%/{today}/%'")
    teve = cur.fetchone()
    cur.execute(f"select count(*) from calendar where start_date >= '{mon}/{start}/{year}' and start_date <= '{mon}/{end}/{year}'")
    weve = cur.fetchone()
    cur.execute(f"select count(*) from calendar where start_date like '{mon}%'")
    meve = cur.fetchone()

    cur.execute("select * from equipments where quantity < 5")
    varx = cur.fetchall()
    # To subtract the number of active and consumed equipments from allotments table
    var = [[varx[i][j] for j in range(len(varx[i]))] for i in range(len(varx))]
    cur.execute(
        "Select item_code, count(*) from allotment where status='Active' or status='Consumed' group by item_code")
    var2 = cur.fetchall()
    for i in range(len(var)):
        for j in range(len(var2)):
            if var[i][0] == var2[j][0]:
                var[i][2] -= var2[j][1]


    cur.execute("select event_name from calendar")
    ceves = cur.fetchall()

    cur.execute("show tables;")
    tab = cur.fetchall()
    tab = [i[0] for i in tab if i[0] not in ['gmeet', 'users']]

    cur.execute("select * from gmeet")
    valr = cur.fetchall()
    if len(valr)>0:
        valp = 'set'
    else:
        valp = 'notset'

    return render_template("dashboard.html", data=[pen, teve, meve, weve, var, ceves, valp, tab])

@app.route("/home")
def home_page():
    cur = mysql.connection.cursor()
    cur.execute("select gmeet.event_name, meet_link, incharge, guest, start_date, end_date from gmeet, calendar where calendar.event_name = gmeet.event_name")
    links = cur.fetchone()

    return render_template("home.html", data = [links])

@app.route("/atlcalendar")
def atlcalendar():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM calendar order by start_time")
    data = cur.fetchall()
    cur.close()
    output = []
    for record in data:
        dic = {}
        dic['id'] = record[0]
        dic['name'] = record[0].title()
        dic['badge'] = f"{record[1]} - {record[2]}"
        dic['date'] = [f"{record[7]}", f"{record[8]}"]
        dic[
            'description'] = f"{record[9]}<br><br><b>Incharge:</b> {record[3].title()}<br><b>Mentor:</b> {record[6].title()}<br><b>Mode:</b> {record[4]}<br><b>Venue:</b> {record[5]}"
        dic['type'] = 'event'

        output.append(dic)

    return render_template("calendarn.html", output=output)

@app.route("/equipments")
def equipments():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM equipments order by name")
    varx = cur.fetchall()

    # To subtract the number of active and consumed equipments from allotments table
    var = [[varx[i][j] for j in range(len(varx[i]))] for i in range(len(varx))]
    cur.execute("Select item_code, count(*) from allotment where status='Active' or status='Consumed' group by item_code")
    var2 = cur.fetchall()
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

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        record = cur.fetchone()
        if record:
            session['loggedin'] = True
            session['username'] = record[1]
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
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM equipments order by quantity desc")
    data = cur.fetchall()

    return render_template("inventory.html", data=data)

@app.route('/allotment')
def allotment():
    cur = mysql.connection.cursor()
    cur.execute("SELECT allotment.item_code, issued_to, issued_by, date_of_issue, status, renewed_on, renewed_by, name FROM allotment, equipments where allotment.item_code = equipments.item_code order by date_of_issue")

    data = cur.fetchall()

    con = [x for x in data if x[4].lower() == 'consumed']
    act = [y for y in data if y[4].lower() == 'active']
    pen = [y for y in data if y[4].lower() == 'pending']

    return render_template("allotment.html", data=data, con=con, pen=pen, act=act)

@app.route('/requests')
def requests():
    message = ''
    cur = mysql.connection.cursor()
    cur.execute("select * from requests order by date_of_request desc")

    data = cur.fetchall()

    den = [x for x in data if x[4].lower() == 'denied']
    apr = [y for y in data if y[4].lower() == 'approved']
    pen = [y for y in data if y[4].lower() == 'pending']

    return render_template("requests.html", data=data, mess=message, apr = apr, den = den, pen = pen)

@app.route('/update_inv', methods=['POST', 'GET'])
def update_inv():
    if request.method=='POST':
        Details = request.form
        code = Details['code']
        item_name = Details['item_name']
        location = Details['location']
        quantity = Details['quantity']
        specification = Details['specification']
        extras = Details['extras']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE equipments set name=%s, location=%s, quantity=%s, specifications=%s, extras=%s where item_code=%s;",(item_name, location, quantity, specification, extras, code))
        mysql.connection.commit()

        return redirect(url_for('inventory'))


@app.route('/update_event', methods=['POST', 'GET'])
def update_event():
    cur = mysql.connection.cursor()
    if request.method=='POST':
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

        cur.execute("update calendar set start_date=%s, end_date=%s, mode=%s, venue=%s, incharge=%s, start_time=%s, end_time=%s, description=%s, guest=%s where event_name=%s",
                (startd, endd, mode, venue, incharge, startt, endt, description, guest, event_name))
        mysql.connection.commit()
        return redirect(url_for('calendar'))


@app.route('/add_inv', methods=['POST', 'GET'])
def add_inv():
    cur = mysql.connection.cursor()
    if request.method=='POST':
        Details = request.form
        code = Details['code']
        item_name = Details['item_name']
        location = Details['location']
        quantity = Details['quantity']
        specification = Details['specification']
        extras = Details['extras']
        paddress = Details['paddress']


        cur.execute("SELECT * FROM EQUIPMENTS WHERE ITEM_CODE=%s",(code,))
        check = cur.fetchall()
        if len(check) > 0:
            show = f'Item with code {code} already present!'
        else:
            cur.execute("INSERT INTO EQUIPMENTS VALUES(%s, %s, %s, %s, %s, %s, %s)",(code, item_name, quantity,  location, paddress, specification, extras, ))
            mysql.connection.commit()
            return redirect(url_for('inventory'))

    cur.execute("SELECT * FROM equipments order by name")
    data = cur.fetchall()
    return render_template("inventory.html", msg = show, data = data)


@app.route('/add_event', methods=['POST', 'GET'])
def add_event():
    cur = mysql.connection.cursor()
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

        cur.execute("SELECT * FROM CALENDAR WHERE EVENT_NAME=%s AND START_DATE=%s", (event_name, startd))
        check = cur.fetchall()
        if len(check) > 0:
            show = f'Event already exists!'  #confirm it`s implementation
        else:
            cur.execute("INSERT INTO CALENDAR VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (event_name, startt, endt, incharge, mode, venue, guest, startd, endd, description))
            mysql.connection.commit()
            return redirect(url_for('calendar'))



@app.route('/calendar')
def calendar(mg=''):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM calendar order by start_time")
    data = cur.fetchall()
    output = []
    for record in data:
        dic = {}
        dic['id'] = record[0]
        dic['name'] = record[0].title()
        dic['badge'] = f"{record[1]} - {record[2]}"
        dic['date'] = [f"{record[7]}",f"{record[8]}"]
        dic['description'] = f"{record[9]}<br><br><b>Incharge:</b> {record[3].title()}<br><b>Mentor:</b> {record[6].title()}<br><b>Mode:</b> {record[4]}<br><b>Venue:</b> {record[5]}"
        dic['type'] = 'event'

        # ------------- For edit section

        dicto = {"January": '01', "February": '02', "March": '03', "April": '04', "May": '05', "June": '06',
                 "July": '07', "August": '08', "September": '09', "October": '10', "November": '11', "December": '12'}
        li = []
        for j in [record[7], record[8]]:
            for i in dicto:
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
        dic['startt'] = str(record[1])
        dic['endt'] = str(record[2])
        dic['descr'] = record[9]
        dic['incharge'] = record[3]
        dic['mentor'] = record[6]
        dic['mode'] = record[4]
        dic['venue'] = record[5]
        dic['descr'] = record[9]
        output.append(dic)


    return render_template("calendar.html", output=output, msg = mg)

@app.route('/delete_item/<string:id>', methods=['GET', 'POST'])
def delete_item(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM equipments where item_code = %s",[id])
    mysql.connection.commit()

    return redirect(url_for('inventory'))

@app.route('/delete_event', methods=['GET', 'POST'])
def delete_event():
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM calendar where event_name=%s", (request.args.get('event_name_e'),))
    mysql.connection.commit()


@app.route('/update_status/<string:id>,<string:per>,<string:dat>', methods=['GET','POST'])
def update_status(id, per, dat):
    cur = mysql.connection.cursor()
    data = request.form
    status = data['status']

    if status == 'Consumed':
        cur.execute("update allotment set status=%s where item_code=%s and issued_to=%s and date_of_issue=%s",(status, id, per, dat))
        cur.execute("update equipments set quantity = (quantity-1) where item_code=%s",(id,))
        mysql.connection.commit()
    else:
        cur.execute("update allotment set status=%s where item_code=%s and issued_to=%s and date_of_issue=%s",(status, id, per, dat))
        mysql.connection.commit()

    return redirect(url_for('allotment'))

@app.route('/update_req/<string:id>,<string:email>,<string:sr>', methods=['GET','POST'])
def update_req(id, email, sr):
    cur = mysql.connection.cursor()
    if sr == 'denyf':
        data = request.form
        status = data['status']

        cur.execute("update requests set status=%s where item_code=%s and email_id=%s",(status, id, email))
        mysql.connection.commit()
        return redirect(url_for('requests'))
    elif sr == 'appf':
        data = request.form
        item_code = data['item_code']
        item_name = data['item_name']
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
        cur.execute("update requests set status='Approved' where item_code=%s and email_id=%s",(item_code, email_id))
        cur.execute("insert into allotment(item_code, issued_to, issued_by, date_of_issue, status ) values(%s,%s,%s,%s,'pending')",(item_code, email_id, issuer_name, issue_date))
        mysql.connection.commit()
        
        #mail
        try:
            msg = EmailMessage()
            msg.set_content(f'Hey!\nYour Request for item: "{item_name}" has been approved by incharge: "{issuer_name}"\nYou are informed to collect the item anytime between {startt}hrs and {endt}hrs, during school days.\nVenue: "{loc}"\nAdditional Comments by the incharge-\n{additional}\n\n\n<This is a one way communication. Do not repond back!')
            msg["Subject"] = "ATL Request Update"
            msg["From"] = "testmailflaskapp@gmail.com"
            msg["To"] = email_id

            context = ssl.create_default_context()

            with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
                smtp.starttls(context=context)
                smtp.login(msg["From"], "testmailflaskapp@123")
                smtp.send_message(msg)
            return redirect(url_for('requests'))
        except Exception as e:
            print(e)
            message = "Email Could not be send. Make sure you have an active internet connection"
            cur.execute("select * from requests order by date_of_request desc")
            data = cur.fetchall()

            return render_template("requests.html", data=data, mess=message)
        

    return redirect(url_for('requests'))

@app.route('/place_request', methods=['GET','POST'])
def place_request():
    data = request.form
    item_code = data['item_code']
    item_name = data['item_name']
    email = data['email_id']
    date = data['today_date']
    datech = date[-2:] + '-' + date[5:7] + '-' + date[:4]

    cur = mysql.connection.cursor()
    cur.execute("select * from requests")
    ch = cur.fetchall()
    for i in ch:
        if i[0] == item_code and i[2] == email and i[3] == datech:
            break
    else:
        cur.execute("insert into requests values(%s, %s, %s, %s, 'pending')",(item_code, item_name, email, date))
        mysql.connection.commit()

    return redirect(url_for('equipments'))


@app.route('/gmeet', methods=['get','post'])
def gmeet():
    cur = mysql.connection.cursor()
    data = request.form
    event_name = data['evename']
    meet_link = data['meetlink']

    cur.execute("delete from gmeet")
    mysql.connection.commit()
    cur.execute("insert into gmeet values(%s, %s)",(event_name, meet_link))
    mysql.connection.commit()

    return redirect(url_for('dashboard'))

@app.route('/remove_gmeet', methods=['get','post'])
def remove_gmeet():
    cur = mysql.connection.cursor()
    cur.execute("delete from gmeet")
    mysql.connection.commit()

    return redirect(url_for('dashboard'))


# Downloading report section-
@app.route('/report',  methods=['get','post'])
def report():
    data = request.form
    table_name = data['tabname']
    try:
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * from {table_name}")
        result = cur.fetchall()

        cur.execute(f'desc {table_name}')
        res = cur.fetchall()
        res = [i[0] for i in res]

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
    app.run(debug=True, port=8000)

