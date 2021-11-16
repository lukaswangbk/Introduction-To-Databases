
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for
import datetime
import random

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.74.246.148/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.74.246.148/proj1part2"
#
DATABASEURI = "postgresql://jc5657:jc5657@34.74.246.148/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def login():
  info = ""
  context = dict(info=info)
  return render_template("login.html", **context)


@app.route('/logincheck', methods=['POST'])
def logincheck():
  info = ""
  user_id = request.form['user_id']
  cursor = g.conn.execute('SELECT user_id FROM Users WHERE user_id = %s', user_id)
  user_id = []
  for result in cursor:
    user_id.append(result['user_id'])
  cursor.close()

  if len(user_id) == 0:
    info = "Please input a valid User ID."
    context = dict(info=info)
    return render_template("login.html", **context)
  else:
    return redirect(url_for('user', user = user_id))

@app.route('/<user>')
def user(user):
  user = user.strip("'][")

  # get information in user
  cursor = g.conn.execute("SELECT * FROM Users WHERE user_id = %s", user)
  user_id = []
  user_name = [] 
  mobile = []
  email = []
  address = []
  passport_no = []
 
  for result in cursor:
    user_id.append(result['user_id'])
    user_name.append(result['user_name'])
    mobile.append(result['mobile'])
    email.append(result['email'])
    address.append(result['address'])
    passport_no.append(result['passport_no'])
  cursor.close()

  # get all accounts belong to the user
  cursor = g.conn.execute("SELECT O.acc_id, A.acc_name, O.since FROM Open O, Account A WHERE user_id = %s AND A.acc_id = O.acc_id", user)
  acc_id = []
  since = []
  acc_name=[]

  for result in cursor:
    acc_id.append(result['acc_id'])
    acc_name.append(result['acc_name'])
    since.append(result['since'])
  cursor.close()
  user_id = user_id
  context = dict(user_id=user_id, user_name=user_name, mobile=mobile, email=email, address=address, passport_no=passport_no, acc_id=acc_id, acc_name=acc_name, since=since)
  return render_template("user.html", **context)

@app.route('/updateuserinfo', methods=['POST'])
def updateuserinfo():
  new_name = request.form['new_name']
  new_mobile = request.form['new_mobile']
  new_email = request.form['new_email']
  new_address = request.form['new_address']
  new_passport_no = request.form['new_passport_no']
  user_id = request.form['user_id']
  user = user_id
  user_id = user_id.strip("'][")
  if new_name != '':
    g.conn.execute('UPDATE Users SET User_name = %s WHERE user_id = %s', new_name, user_id)
  if new_mobile != '':
    # Check UNIQUE
    cursor = g.conn.execute('SELECT * FROM Users WHERE Mobile = %s', new_mobile)
    tmp_user_id = []
    for result in cursor:
      tmp_user_id.append(result['user_id'])
    cursor.close()
    if len(tmp_user_id) == 0:
      g.conn.execute('UPDATE Users SET Mobile = %s WHERE user_id = %s', new_mobile, user_id)
  if new_email != '':
    # Check UNIQUE
    cursor = g.conn.execute('SELECT * FROM Users WHERE Email = %s', new_email)
    tmp_user_id = []
    for result in cursor:
      tmp_user_id.append(result['user_id'])
    cursor.close()    
    if len(tmp_user_id) == 0:
      g.conn.execute('UPDATE Users SET Email = %s WHERE user_id = %s', new_email, user_id)
  if new_address != '':
    g.conn.execute('UPDATE Users SET Address = %s WHERE user_id = %s', new_address, user_id)
  if new_passport_no != '':
    # Check UNIQUE
    cursor = g.conn.execute('SELECT * FROM Users WHERE Passport_no = %s', new_passport_no)
    tmp_user_id = []
    for result in cursor:
      tmp_user_id.append(result['user_id'])
    cursor.close()
    if len(tmp_user_id) == 0:
      g.conn.execute('UPDATE Users SET Passport_no = %s WHERE user_id = %s', new_passport_no, user_id)
  return redirect(url_for('user', user = user))

@app.route('/accountcheck', methods=['POST'])
def accountcheck():
  acc_id = request.form['acc_id']
  user_id = request.form['user']
  user_id = user_id.strip("'][")

  # get all the account information
  cursor = g.conn.execute('SELECT * FROM Account WHERE Acc_id = %s AND Acc_id in (SELECT Acc_id FROM Open WHERE user_id = %s)', acc_id, user_id)
  acc = []
  acc_name = []
  cash_balance = []
  inv_balance = []
  total_value = []
  for result in cursor:
    acc.append(result['acc_id'])
    acc_name.append(result['acc_name'])
    cash_balance.append(result['cash_balance'])
    inv_balance.append(result['inv_balance'])
    total_value.append(result['total_value'])
  cursor.close()


  # get owning investment product information
  cursor = g.conn.execute('SELECT * FROM Owns O, Investment_Product IP WHERE O.Acc_id = %s AND O.IP_id = IP.IP_id', acc_id)
  O_IP_id = []
  O_amount = []
  O_ip_name = []
  O_risk_type = []
  O_curr_yield = []
  for result in cursor:
    O_IP_id.append(result['ip_id'])
    O_amount.append(result['amount'])
    O_ip_name.append(result['ip_name'])
    O_risk_type.append(result['risk_type'])
    O_curr_yield.append(result['curr_yield'])
  cursor.close()

  # get watching investment product information
  cursor = g.conn.execute('SELECT * FROM Contains C, Investment_Product IP WHERE C.Acc_id = %s AND C.IP_id = IP.IP_id', acc_id)
  C_IP_id = []
  C_list_id = []
  C_add_time = []
  C_ip_name = []
  C_risk_type = []
  C_curr_yield = []
  for result in cursor:
    C_IP_id.append(result['ip_id'])
    C_list_id.append(result['list_id'])
    C_add_time.append(result['add_time'])
    C_ip_name.append(result['ip_name'])
    C_risk_type.append(result['risk_type'])
    C_curr_yield.append(result['curr_yield'])
  cursor.close()

  # get payment method information
  cursor = g.conn.execute('SELECT * FROM Has_Payment_method WHERE Acc_id = %s', acc_id)
  pay_id = []
  type = []
  card_no = []
  card_name = []
  card_expire = []
  create_date = []
  for result in cursor:
    pay_id.append(result['pay_id'])
    type.append(result['type'])
    card_no.append(result['card_no'])
    card_name.append(result['card_name'])
    card_expire.append(result['card_expire'])
    create_date.append(result['create_date'])
  cursor.close()

  if len(acc) == 0:
    # get information needed to redirect to user.html
    # get information in user
    cursor = g.conn.execute("SELECT * FROM Users WHERE user_id = %s", user_id)
    user_id_back = []
    user_name = [] 
    mobile = []
    email = []
    address = []
    passport_no = []
 
    for result in cursor:
      user_id_back.append(result['user_id'])
      user_name.append(result['user_name'])
      mobile.append(result['mobile'])
      email.append(result['email'])
      address.append(result['address'])
      passport_no.append(result['passport_no'])
    cursor.close()

    # get all accounts belong to the user
    cursor = g.conn.execute("SELECT O.acc_id, A.acc_name, O.since FROM Open O, Account A WHERE user_id = %s AND A.acc_id = O.acc_id", user_id)
    acc_id = []
    since = []
    acc_name=[]

    for result in cursor:
      acc_id.append(result['acc_id'])
      acc_name.append(result['acc_name'])
      since.append(result['since'])
    cursor.close()

    user_id = user_id.split()

    context = dict(user_id=user_id, user_name=user_name, mobile=mobile, email=email, address=address, passport_no=passport_no, acc_id=acc_id, acc_name=acc_name, since=since)
    return render_template("user.html", **context)
  else:
    context = dict(acc=acc, acc_name=acc_name, cash_balance=cash_balance, inv_balance=inv_balance, total_value=total_value, pay_id=pay_id, type=type, card_no=card_no, card_name=card_name, card_expire=card_expire, create_date=create_date, O_IP_id=O_IP_id, O_amount=O_amount, O_ip_name=O_ip_name, O_risk_type=O_risk_type, O_curr_yield=O_curr_yield, C_IP_id=C_IP_id, C_list_id=C_list_id, C_add_time=C_add_time, C_ip_name=C_ip_name, C_risk_type=C_risk_type, C_curr_yield=C_curr_yield)
    return render_template("account.html", **context)


@app.route('/addaccount', methods=['POST'])
def addaccount():
  acc_id = request.form['acc_id']
  since = datetime.date.today()
  user_id = request.form['user_id']
  user = user_id
  user_id = user_id.strip("'][")
  acc_name = request.form['acc_name']
  if acc_id != '' and acc_name != '':
    cursor = g.conn.execute('SELECT * FROM Account WHERE Acc_id = %s', acc_id)
    tmp_acc_id = []
    for result in cursor:
      tmp_acc_id.append(result['acc_id'])
    cursor.close()
    if len(tmp_acc_id) == 0:
      g.conn.execute('INSERT INTO Account VALUES (%s,%s,%s,%s,%s)', acc_id, acc_name, 0, 0, 0)
      g.conn.execute('INSERT INTO Open VALUES (%s,%s,%s)', user_id, acc_id, since)
  return redirect(url_for('user', user = user))

@app.route('/updateaccountinfo', methods=['POST'])
def updateaccountinfo():
  new_name = request.form['new_name']
  acc = request.form['acc']
  acc_id = acc.strip("'][")

  if new_name != '':
    g.conn.execute('UPDATE Account SET Acc_name = %s WHERE Acc_id = %s', new_name, acc_id)
  # get information needed to redirect to account.html

  # get all the account information
  cursor = g.conn.execute('SELECT * FROM Account WHERE Acc_id = %s', acc_id)
  acc = []
  acc_name = []
  cash_balance = []
  inv_balance = []
  total_value = []
  for result in cursor:
    acc.append(result['acc_id'])
    acc_name.append(result['acc_name'])
    cash_balance.append(result['cash_balance'])
    inv_balance.append(result['inv_balance'])
    total_value.append(result['total_value'])
  cursor.close()

  # get owning investment product information
  cursor = g.conn.execute('SELECT * FROM Owns O, Investment_Product IP WHERE O.Acc_id = %s AND O.IP_id = IP.IP_id', acc_id)
  O_IP_id = []
  O_amount = []
  O_ip_name = []
  O_risk_type = []
  O_curr_yield = []
  for result in cursor:
    O_IP_id.append(result['ip_id'])
    O_amount.append(result['amount'])
    O_ip_name.append(result['ip_name'])
    O_risk_type.append(result['risk_type'])
    O_curr_yield.append(result['curr_yield'])
  cursor.close()

  # get watching investment product information
  cursor = g.conn.execute('SELECT * FROM Contains C, Investment_Product IP WHERE C.Acc_id = %s AND C.IP_id = IP.IP_id', acc_id)
  C_IP_id = []
  C_list_id = []
  C_add_time = []
  C_ip_name = []
  C_risk_type = []
  C_curr_yield = []
  for result in cursor:
    C_IP_id.append(result['ip_id'])
    C_list_id.append(result['list_id'])
    C_add_time.append(result['add_time'])
    C_ip_name.append(result['ip_name'])
    C_risk_type.append(result['risk_type'])
    C_curr_yield.append(result['curr_yield'])
  cursor.close()

  # get payment method information
  cursor = g.conn.execute('SELECT * FROM Has_Payment_method WHERE Acc_id = %s', acc_id)
  pay_id = []
  type = []
  card_no = []
  card_name = []
  card_expire = []
  for result in cursor:
    pay_id.append(result['pay_id'])
    type.append(result['type'])
    card_no.append(result['card_no'])
    card_name.append(result['card_name'])
    card_expire.append(result['card_expire'])
  cursor.close()
  create_date = datetime.date.today()
  context = dict(acc=acc, acc_name=acc_name, cash_balance=cash_balance, inv_balance=inv_balance, total_value=total_value, pay_id=pay_id, type=type, card_no=card_no, card_name=card_name, card_expire=card_expire, create_date=create_date, O_IP_id=O_IP_id, O_amount=O_amount, O_ip_name=O_ip_name, O_risk_type=O_risk_type, O_curr_yield=O_curr_yield, C_IP_id=C_IP_id, C_list_id=C_list_id, C_add_time=C_add_time, C_ip_name=C_ip_name, C_risk_type=C_risk_type, C_curr_yield=C_curr_yield)
  return render_template("account.html", **context)


@app.route('/addpaymentmethod', methods=['POST'])
def addpaymentmethod():
  pay_id = request.form['pay_id']
  type = request.form['type']
  card_no = request.form['card_no']
  card_name = request.form['card_name']
  card_expire = request.form['card_expire']
  acc_id = request.form['acc_id']
  acc_id = acc_id.strip("'][")
  create_date = datetime.date.today()

  cursor = g.conn.execute('SELECT pay_id FROM Has_Payment_method WHERE acc_id = %s', acc_id)
  all_pay_id = []
  for result in cursor:
    all_pay_id.append(result['pay_id'])
  cursor.close()

  if pay_id not in all_pay_id:
    if pay_id != '' and type != '' and card_no != '' and card_name != '' and card_expire != '':
      g.conn.execute('INSERT INTO Has_Payment_method VALUES (%s,%s,%s,%s,%s,%s,%s)', pay_id, type, card_no, card_name, card_expire, acc_id, create_date)
    elif pay_id != '':
      g.conn.execute('INSERT INTO Has_Payment_method(pay_id,acc_id) VALUES (%s,%s)', pay_id, acc_id)
      if type == '':
        g.conn.execute('UPDATE Has_Payment_method SET type = NULL WHERE (pay_id,acc_id) = (%s,%s)', pay_id, acc_id)
      else: 
        g.conn.execute('UPDATE Has_Payment_method SET type = %s WHERE (pay_id,acc_id) = (%s,%s)', type, pay_id, acc_id)
      if card_no == '':
        g.conn.execute('UPDATE Has_Payment_method SET card_no = NULL WHERE (pay_id,acc_id) = (%s,%s)', pay_id, acc_id)
      else: 
        g.conn.execute('UPDATE Has_Payment_method SET card_no = %s WHERE (pay_id,acc_id) = (%s,%s)', card_no, pay_id, acc_id)
      if card_name == '':
        g.conn.execute('UPDATE Has_Payment_method SET card_name = NULL WHERE (pay_id,acc_id) = (%s,%s)', pay_id, acc_id)
      else: 
        g.conn.execute('UPDATE Has_Payment_method SET card_name = %s WHERE (pay_id,acc_id) = (%s,%s)', card_name, pay_id, acc_id)
      if card_expire == '':
        g.conn.execute('UPDATE Has_Payment_method SET card_expire = NULL WHERE (pay_id,acc_id) = (%s,%s)', pay_id, acc_id)
      else: 
        g.conn.execute('UPDATE Has_Payment_method SET card_expire = %s WHERE (pay_id,acc_id) = (%s,%s)', card_expire, pay_id, acc_id)
    
  # get information needed to redirect to account.html
  # get all the account information
  cursor = g.conn.execute('SELECT * FROM Account WHERE Acc_id = %s', acc_id)
  acc = []
  acc_name = []
  cash_balance = []
  inv_balance = []
  total_value = []
  for result in cursor:
    acc.append(result['acc_id'])
    acc_name.append(result['acc_name'])
    cash_balance.append(result['cash_balance'])
    inv_balance.append(result['inv_balance'])
    total_value.append(result['total_value'])
  cursor.close()

  # get owning investment product information
  cursor = g.conn.execute('SELECT * FROM Owns O, Investment_Product IP WHERE O.Acc_id = %s AND O.IP_id = IP.IP_id', acc_id)
  O_IP_id = []
  O_amount = []
  O_ip_name = []
  O_risk_type = []
  O_curr_yield = []
  for result in cursor:
    O_IP_id.append(result['ip_id'])
    O_amount.append(result['amount'])
    O_ip_name.append(result['ip_name'])
    O_risk_type.append(result['risk_type'])
    O_curr_yield.append(result['curr_yield'])
  cursor.close()

  # get watching investment product information
  cursor = g.conn.execute('SELECT * FROM Contains C, Investment_Product IP WHERE C.Acc_id = %s AND C.IP_id = IP.IP_id', acc_id)
  C_IP_id = []
  C_list_id = []
  C_add_time = []
  C_ip_name = []
  C_risk_type = []
  C_curr_yield = []
  for result in cursor:
    C_IP_id.append(result['ip_id'])
    C_list_id.append(result['list_id'])
    C_add_time.append(result['add_time'])
    C_ip_name.append(result['ip_name'])
    C_risk_type.append(result['risk_type'])
    C_curr_yield.append(result['curr_yield'])
  cursor.close()

  # get payment method information
  cursor = g.conn.execute('SELECT * FROM Has_Payment_method WHERE Acc_id = %s', acc_id)
  pay_id = []
  type = []
  card_no = []
  card_name = []
  card_expire = []
  for result in cursor:
    pay_id.append(result['pay_id'])
    type.append(result['type'])
    card_no.append(result['card_no'])
    card_name.append(result['card_name'])
    card_expire.append(result['card_expire'])
  cursor.close()
  create_date = datetime.date.today()
  context = dict(acc=acc, acc_name=acc_name, cash_balance=cash_balance, inv_balance=inv_balance, total_value=total_value, pay_id=pay_id, type=type, card_no=card_no, card_name=card_name, card_expire=card_expire, create_date=create_date, O_IP_id=O_IP_id, O_amount=O_amount, O_ip_name=O_ip_name, O_risk_type=O_risk_type, O_curr_yield=O_curr_yield, C_IP_id=C_IP_id, C_list_id=C_list_id, C_add_time=C_add_time, C_ip_name=C_ip_name, C_risk_type=C_risk_type, C_curr_yield=C_curr_yield)
  return render_template("account.html", **context)


@app.route('/checkallinvestmentproduct', methods=['POST'])
def checkallinvestmentproduct():
  acc_id = request.form['acc_id']
  return redirect(url_for('ip', acc_id=acc_id))


@app.route('/ip/<acc_id>', methods=['POST', 'GET'])
def ip(acc_id):
  query = '''SELECT * FROM investment_product'''
  cursor = g.conn.execute(query)
  table = []
  for result in cursor:
    row = list(result)

    id = result[0]
    c_stock = g.conn.execute("SELECT * FROM stock where ip_id = %s", id)
    if len(list(c_stock)): row.append("stock")
    c_stock.close()
    c_bond = g.conn.execute("SELECT * FROM bond where ip_id = %s", id)
    if len(list(c_bond)): row.append("bond")
    c_bond.close()
    c_gold = g.conn.execute("SELECT * FROM gold where ip_id = %s", id)
    if len(list(c_gold)): row.append("gold")
    c_gold.close()

    table.append(row)  # can also be accessed using result[0]
  cursor.close()
  title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date', 'Expire Date', 'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description', 'Category']
  context = dict(data=table, title=title, acc_id=acc_id)
  return render_template("ip.html", **context)


@app.route('/ip_query', methods=['POST', 'GET'])
def ip_query():
  title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date', 'Expire Date',
           'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description', 'Category']
  acc = request.form['acc_save']
  acc_id = acc.strip("'][")
  id = request.form['id']
  name = request.form['name']
  risk = request.form['risk']
  status = request.form['status']
  category = request.form['category']
  curr_yield = request.form['curr_yield']
  min_inv_value = request.form['min_inv_value']
  freeze_time = request.form['freeze_time']
  create_date = request.form['create_date']
  expire_date = request.form['expire_date']

  if len(id)==0: id = '%'
  else: id = '%'+id+'%'
  if len(name)==0: name='%'
  else: name = '%'+name+'%'
  if risk=='all': risk='%'
  if status=='all': status='%'

  if category=='all':
    query = '''
              SELECT * FROM investment_product ip
              WHERE ip.ip_id LIKE %s and ip.ip_name LIKE %s and ip.risk_type LIKE %s and ip.status LIKE %s
              '''
  elif category=='stock':
    query = '''
            SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, s.capital_price, s.open_price, s.close_price
            FROM investment_product ip, stock s
            WHERE ip.ip_id = s.ip_id and ip.ip_id LIKE %s and ip.ip_name LIKE %s and ip.risk_type LIKE %s and ip.status LIKE %s
            '''
    title = title[:-1] + ["Stock Capital Price", "Stock Open Price", "Stock Close Price"]

  elif category == 'bond':
    query = '''
            SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, b.maturity, b.face_value, b.issue_price
            FROM investment_product ip, bond b
            WHERE ip.ip_id = b.ip_id and ip.ip_id LIKE %s and ip.ip_name LIKE %s and ip.risk_type LIKE %s and ip.status LIKE %s
            '''
    title = title[:-1] + ["Bond Maturity", "Bond Face Value", "Bond Issue Price"]

  elif category == 'gold':
    query = '''
            SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, g.gold_price
            FROM investment_product ip, gold g
            WHERE ip.ip_id = g.ip_id and ip.ip_id LIKE %s and ip.ip_name LIKE %s and ip.risk_type LIKE %s and ip.status LIKE %s
            '''
    title = title[:-1] + ["Gold Price"]


  if curr_yield=='default' and min_inv_value=='default' and freeze_time=='default' and create_date=='default' and expire_date=='default':
      cursor = g.conn.execute(query, id, name, risk, status)
  else:
    order = " ORDER BY "
    if curr_yield == 'high': order += "ip.curr_yield DESC,"
    elif curr_yield =='low': order += "ip.curr_yield ASC,"
    if min_inv_value == 'high': order += "ip.min_inv_value DESC,"
    elif min_inv_value == 'low': order += "ip.min_inv_value ASC,"
    if freeze_time == 'long': order += "ip.freezing_time DESC,"
    elif freeze_time == 'short': order += "ip.freezing_time ASC,"
    if create_date == 'latest': order += "ip.create_date DESC,"
    elif create_date == 'early': order += "ip.create_date ASC,"
    if expire_date == 'latest': order += "ip.expire_date DESC,"
    elif expire_date == 'early': order += "ip.expire_date ASC,"
    cursor = g.conn.execute(query+order[:-1], id, name, risk, status)

  table = []
  for result in cursor:
    row = list(result)
    if category == 'all':
      id = result[0]
      c_stock = g.conn.execute("SELECT * FROM stock where ip_id = %s", id)
      if len(list(c_stock)): row.append("stock")
      c_stock.close()
      c_bond = g.conn.execute("SELECT * FROM bond where ip_id = %s", id)
      if len(list(c_bond)): row.append("bond")
      c_bond.close()
      c_gold = g.conn.execute("SELECT * FROM gold where ip_id = %s", id)
      if len(list(c_gold)): row.append("gold")
      c_gold.close()

    table.append(row)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data=table, title=title, acc_id=acc)
  return render_template("ip.html", **context)

@app.route('/ip_action', methods=['POST', 'GET'])
def ip_action():
  print(request.form)
  ip_id = list(request.form)[1]
  acc = request.form['acc']
  acc_id = acc.strip("'][")
  action = request.form[ip_id]

  if action == 'Buy':
    return redirect(url_for('buy', acc_id=acc, ip_id=ip_id))

  elif action == 'Sell':
    return redirect(url_for('sell', acc_id=acc, ip_id=ip_id))

  elif action == 'Follow':
    # add to watching list
    c1 = g.conn.execute("SELECT list_id FROM create_watchinglist WHERE acc_id=%s", acc_id)
    list_id = c1.fetchone()[0]
    c1.close()

    c2_check = g.conn.execute("SELECT * FROM contains WHERE list_id=%s and acc_id=%s and ip_id=%s", list_id, acc_id, ip_id)
    if len(list(c2_check)) == 0:
      today = datetime.date.today()
      c2 = g.conn.execute("INSERT INTO contains VALUES (%s, %s, %s, %s)", list_id, acc_id, ip_id, today)
      c2.close()
    c2_check.close()

    c3 = g.conn.execute("SELECT user_id FROM Open WHERE acc_id=%s", acc_id)
    user_id = c3.fetchone()[0]
    c3.close()

    # redirect to account.html
    # get all the account information
    cursor = g.conn.execute('SELECT * FROM Account WHERE Acc_id = %s AND Acc_id in (SELECT Acc_id FROM Open WHERE user_id = %s)', acc_id, user_id)
    acc = []
    acc_name = []
    cash_balance = []
    inv_balance = []
    total_value = []
    for result in cursor:
      acc.append(result['acc_id'])
      acc_name.append(result['acc_name'])
      cash_balance.append(result['cash_balance'])
      inv_balance.append(result['inv_balance'])
      total_value.append(result['total_value'])
    cursor.close()

    # get owning investment product information
    cursor = g.conn.execute('SELECT * FROM Owns O, Investment_Product IP WHERE O.Acc_id = %s AND O.IP_id = IP.IP_id', acc_id)
    O_IP_id = []
    O_amount = []
    O_ip_name = []
    O_risk_type = []
    O_curr_yield = []
    for result in cursor:
      O_IP_id.append(result['ip_id'])
      O_amount.append(result['amount'])
      O_ip_name.append(result['ip_name'])
      O_risk_type.append(result['risk_type'])
      O_curr_yield.append(result['curr_yield'])
    cursor.close()

    # get watching investment product information
    cursor = g.conn.execute('SELECT * FROM Contains C, Investment_Product IP WHERE C.Acc_id = %s AND C.IP_id = IP.IP_id', acc_id)
    C_IP_id = []
    C_list_id = []
    C_add_time = []
    C_ip_name = []
    C_risk_type = []
    C_curr_yield = []
    for result in cursor:
      C_IP_id.append(result['ip_id'])
      C_list_id.append(result['list_id'])
      C_add_time.append(result['add_time'])
      C_ip_name.append(result['ip_name'])
      C_risk_type.append(result['risk_type'])
      C_curr_yield.append(result['curr_yield'])
    cursor.close()

    # get payment method information
    cursor = g.conn.execute('SELECT * FROM Has_Payment_method WHERE Acc_id = %s', acc_id)
    pay_id = []
    type = []
    card_no = []
    card_name = []
    card_expire = []
    create_date = []
    for result in cursor:
      pay_id.append(result['pay_id'])
      type.append(result['type'])
      card_no.append(result['card_no'])
      card_name.append(result['card_name'])
      card_expire.append(result['card_expire'])
      create_date.append(result['create_date'])
    cursor.close()

    if len(acc) == 0:
      # get information needed to redirect to user.html
      # get information in user
      cursor = g.conn.execute("SELECT * FROM Users WHERE user_id = %s", user_id)
      user_id_back = []
      user_name = [] 
      mobile = []
      email = []
      address = []
      passport_no = []
 
      for result in cursor:
        user_id_back.append(result['user_id'])
        user_name.append(result['user_name'])
        mobile.append(result['mobile'])
        email.append(result['email'])
        address.append(result['address'])
        passport_no.append(result['passport_no'])
      cursor.close()

      # get all accounts belong to the user
      cursor = g.conn.execute("SELECT O.acc_id, A.acc_name, O.since FROM Open O, Account A WHERE user_id = %s AND A.acc_id = O.acc_id", user_id)
      acc_id = []
      since = []
      acc_name=[]

      for result in cursor:
        acc_id.append(result['acc_id'])
        acc_name.append(result['acc_name'])
        since.append(result['since'])
      cursor.close()
      user_id = user_id.split()
      context = dict(user_id=user_id, user_name=user_name, mobile=mobile, email=email, address=address, passport_no=passport_no, acc_id=acc_id, acc_name=acc_name, since=since)
      return render_template("user.html", **context)
    else:
      context = dict(acc=acc, acc_name=acc_name, cash_balance=cash_balance, inv_balance=inv_balance, total_value=total_value, pay_id=pay_id, type=type, card_no=card_no, card_name=card_name, card_expire=card_expire, create_date=create_date, O_IP_id=O_IP_id, O_amount=O_amount, O_ip_name=O_ip_name, O_risk_type=O_risk_type, O_curr_yield=O_curr_yield, C_IP_id=C_IP_id, C_list_id=C_list_id, C_add_time=C_add_time, C_ip_name=C_ip_name, C_risk_type=C_risk_type, C_curr_yield=C_curr_yield)
      return render_template("account.html", **context)


@app.route('/removewatching', methods=['POST', 'GET'])
def removewatching():
  print(request.form)
  ip_id = list(request.form)[1]
  acc = request.form['acc']
  acc_id = acc.strip("'][")
  #  remove from watching list
  c1 = g.conn.execute("SELECT list_id FROM create_watchinglist WHERE acc_id=%s", acc_id)
  list_id = c1.fetchone()[0]
  c1.close()

  c2_check = g.conn.execute("DELETE FROM contains WHERE list_id=%s and acc_id=%s and ip_id=%s", list_id, acc_id, ip_id)
  c2_check.close()

  c3 = g.conn.execute("SELECT user_id FROM Open WHERE acc_id=%s", acc_id)
  user_id = c3.fetchone()[0]
  c3.close()

  # redirect to account.html
  # get all the account information
  cursor = g.conn.execute('SELECT * FROM Account WHERE Acc_id = %s AND Acc_id in (SELECT Acc_id FROM Open WHERE user_id = %s)', acc_id, user_id)
  acc = []
  acc_name = []
  cash_balance = []
  inv_balance = []
  total_value = []
  for result in cursor:
    acc.append(result['acc_id'])
    acc_name.append(result['acc_name'])
    cash_balance.append(result['cash_balance'])
    inv_balance.append(result['inv_balance'])
    total_value.append(result['total_value'])
  cursor.close()

  # get owning investment product information
  cursor = g.conn.execute('SELECT * FROM Owns O, Investment_Product IP WHERE O.Acc_id = %s AND O.IP_id = IP.IP_id', acc_id)
  O_IP_id = []
  O_amount = []
  O_ip_name = []
  O_risk_type = []
  O_curr_yield = []
  for result in cursor:
    O_IP_id.append(result['ip_id'])
    O_amount.append(result['amount'])
    O_ip_name.append(result['ip_name'])
    O_risk_type.append(result['risk_type'])
    O_curr_yield.append(result['curr_yield'])
  cursor.close()

  # get watching investment product information
  cursor = g.conn.execute('SELECT * FROM Contains C, Investment_Product IP WHERE C.Acc_id = %s AND C.IP_id = IP.IP_id', acc_id)
  C_IP_id = []
  C_list_id = []
  C_add_time = []
  C_ip_name = []
  C_risk_type = []
  C_curr_yield = []
  for result in cursor:
    C_IP_id.append(result['ip_id'])
    C_list_id.append(result['list_id'])
    C_add_time.append(result['add_time'])
    C_ip_name.append(result['ip_name'])
    C_risk_type.append(result['risk_type'])
    C_curr_yield.append(result['curr_yield'])
  cursor.close()

  # get payment method information
  cursor = g.conn.execute('SELECT * FROM Has_Payment_method WHERE Acc_id = %s', acc_id)
  pay_id = []
  type = []
  card_no = []
  card_name = []
  card_expire = []
  create_date = []
  for result in cursor:
    pay_id.append(result['pay_id'])
    type.append(result['type'])
    card_no.append(result['card_no'])
    card_name.append(result['card_name'])
    card_expire.append(result['card_expire'])
    create_date.append(result['create_date'])
  cursor.close()

  if len(acc) == 0:
    # get information needed to redirect to user.html
    # get information in user
    cursor = g.conn.execute("SELECT * FROM Users WHERE user_id = %s", user_id)
    user_id_back = []
    user_name = [] 
    mobile = []
    email = []
    address = []
    passport_no = []
 
    for result in cursor:
      user_id_back.append(result['user_id'])
      user_name.append(result['user_name'])
      mobile.append(result['mobile'])
      email.append(result['email'])
      address.append(result['address'])
      passport_no.append(result['passport_no'])
    cursor.close()

    # get all accounts belong to the user
    cursor = g.conn.execute("SELECT O.acc_id, A.acc_name, O.since FROM Open O, Account A WHERE user_id = %s AND A.acc_id = O.acc_id", user_id)
    acc_id = []
    since = []
    acc_name=[]

    for result in cursor:
      acc_id.append(result['acc_id'])
      acc_name.append(result['acc_name'])
      since.append(result['since'])
    cursor.close()
    user_id = user_id.split()
    context = dict(user_id=user_id, user_name=user_name, mobile=mobile, email=email, address=address, passport_no=passport_no, acc_id=acc_id, acc_name=acc_name, since=since)
    return render_template("user.html", **context)
  else:
    context = dict(acc=acc, acc_name=acc_name, cash_balance=cash_balance, inv_balance=inv_balance, total_value=total_value, pay_id=pay_id, type=type, card_no=card_no, card_name=card_name, card_expire=card_expire, create_date=create_date, O_IP_id=O_IP_id, O_amount=O_amount, O_ip_name=O_ip_name, O_risk_type=O_risk_type, O_curr_yield=O_curr_yield, C_IP_id=C_IP_id, C_list_id=C_list_id, C_add_time=C_add_time, C_ip_name=C_ip_name, C_risk_type=C_risk_type, C_curr_yield=C_curr_yield)
    return render_template("account.html", **context)


@app.route('/buy/<acc_id>/<ip_id>', methods=['POST', 'GET'])
def buy(acc_id, ip_id):

  info = ""
  acc_id = acc_id.strip("'][")
  c1 = g.conn.execute('''
          SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, s.capital_price, s.open_price, s.close_price
          FROM investment_product ip, stock s
          WHERE ip.ip_id = s.ip_id and ip.ip_id = %s
          ''', ip_id)
  data = list(c1)
  if len(data) > 0:
    type = 'stock'
    title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date', 'Expire Date',
           'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description', 'Stock Capital Price', 'Stock Open Price', 'Stock Close Price']
  else:
    c2 = g.conn.execute('''
                SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, b.maturity, b.face_value, b.issue_price
                FROM investment_product ip, bond b
                WHERE ip.ip_id = b.ip_id and ip.ip_id = %s
                ''', ip_id)
    data = list(c2)
    if len(data) > 0:
      type = 'bond'
      title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date', 'Expire Date',
               'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description', 'Bond Maturity',
               'Bond Face Value', 'Bond Issue Price']
    else:
      c3 = g.conn.execute('''
                    SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, g.gold_price
                    FROM investment_product ip, gold g
                    WHERE ip.ip_id = g.ip_id and ip.ip_id = %s
                    ''', ip_id)
      data = list(c3)
      if len(data) > 0:
        type = 'gold'
        title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date', 'Expire Date',
                 'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description', 'Gold Price']
      c3.close()
    c2.close()
  c1.close()

  c4 = g.conn.execute('''
      SELECT cash_balance, inv_balance, total_value
      FROM account
      WHERE acc_id = %s
      ''', acc_id)

  vals = list(c4)
  val = [vals[0][0], vals[0][1], vals[0][2]]
  c4.close()

  context = dict(info = info, type=type, data=data, title=title, acc_id=acc_id, ip_id = ip_id, val=val)
  return render_template("buy.html", **context)

def generate_id(n):
  id = ""
  for i in range(n):
    ch = chr(random.randrange(ord('0'), ord('9') + 1))
    id += ch
  return id

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False


@app.route('/buy_check', methods=['POST', 'GET'])
def buy_check():
  if request.method == 'POST':
      acc_id = request.form['acc_id']
      ip_id = request.form['ip_id']
      amount = request.form['amount']
      payment = request.form['payment']
      acc_id = acc_id.strip("'][")
      transaction = True

      # check amount > min_inv_value
      c1 = g.conn.execute("SELECT min_inv_value FROM investment_product WHERE ip_id=%s", ip_id)
      min_inv_value = c1.fetchone()[0]
      if is_number(amount) == False:
        transaction = False
        info = "Please input a valid amount."
      elif float(min_inv_value) > float(amount):
          transaction = False
          info = "The invesment amount needs to be larger than minimum investment value."
      c1.close()

      # check payment method correct
      c_acc = g.conn.execute("SELECT cash_balance FROM account WHERE acc_id=%s", acc_id)
      cash_bal = c_acc.fetchone()[0]
      if float(cash_bal) < float(amount):
        c2 = g.conn.execute("SELECT pay_id FROM has_payment_method WHERE pay_id=%s and acc_id = %s", payment, acc_id)
        data = list(c2)
        if len(data) == 0:
          transaction = False
          info = "You need to have a payment method to cover the amount but you enter an invalid one."
        c2.close()

      if transaction == False:
        c1 = g.conn.execute('''
                SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, s.capital_price, s.open_price, s.close_price
                FROM investment_product ip, stock s
                WHERE ip.ip_id = s.ip_id and ip.ip_id = %s
                ''', ip_id)
        data = list(c1)
        if len(data) > 0:
          type = 'stock'
          title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date', 'Expire Date',
                   'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description',
                   'Stock Capital Price', 'Stock Open Price', 'Stock Close Price']
        else:
          c2 = g.conn.execute('''
                      SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, b.maturity, b.face_value, b.issue_price
                      FROM investment_product ip, bond b
                      WHERE ip.ip_id = b.ip_id and ip.ip_id = %s
                      ''', ip_id)
          data = list(c2)
          if len(data) > 0:
            type = 'bond'
            title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date',
                     'Expire Date',
                     'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description',
                     'Bond Maturity',
                     'Bond Face Value', 'Bond Issue Price']
          else:
            c3 = g.conn.execute('''
                          SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, g.gold_price
                          FROM investment_product ip, gold g
                          WHERE ip.ip_id = g.ip_id and ip.ip_id = %s
                          ''', ip_id)
            data = list(c3)
            if len(data) > 0:
              type = 'gold'
              title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date',
                       'Expire Date',
                       'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description',
                       'Gold Price']
            c3.close()
          c2.close()
        c1.close()

        c4 = g.conn.execute('''
          SELECT cash_balance, inv_balance, total_value
          FROM account
          WHERE acc_id = %s
          ''', acc_id)

        vals = list(c4)
        val = [vals[0][0], vals[0][1], vals[0][2]]
        c4.close()

        context = dict(info = info, type=type, data=data, title=title, acc_id=acc_id, ip_id = ip_id, val=val)
        return render_template("buy.html", **context)

      else:
        # make transaction
          # add to owns
          c_own_check = g.conn.execute("SELECT * FROM owns WHERE acc_id=%s and ip_id=%s", acc_id, ip_id)
          data = list(c_own_check)
          if len(data) == 0:
            c_own = g.conn.execute('''
                  INSERT INTO owns VALUES(%s, %s, %s)
                  ''', acc_id, ip_id, amount)
            c_own.close()
          else:
            original_amount = data[0][2]
            new_amount = float(original_amount)+float(amount)
            c_own = g.conn.execute('''
                  UPDATE owns SET amount=%s WHERE acc_id=%s and ip_id=%s
                  ''', new_amount, acc_id, ip_id)
            c_own.close()

          # update account value
          c_acc = g.conn.execute("SELECT cash_balance, inv_balance, total_value FROM account WHERE acc_id=%s", acc_id)
          data = list(c_acc)
          cash_bal_ori, inv_bal_ori, tot_bal_ori = data[0][0], data[0][1], data[0][2]

          if float(cash_bal_ori) >= float(amount):
              cash_bal_new = float(cash_bal_ori)-float(amount)
          else:
              cash_bal_new = 0

          inv_bal_new = float(inv_bal_ori)+float(amount)
          tot_bal_new = cash_bal_new + inv_bal_new
          c_acc_update = g.conn.execute("UPDATE account SET cash_balance=%s, inv_balance=%s, total_value=%s WHERE acc_id=%s", cash_bal_new, inv_bal_new, tot_bal_new, acc_id)
          c_acc_update.close()
          c_acc.close()

          # add to bill
          bill_id = generate_id(5)
          c_check = g.conn.execute("SELECT * FROM bill WHERE bill_id = %s", bill_id)
          data = list(c_check)
          while len(data)!=0:
            bill_id = generate_id(6)
            c_check = g.conn.execute("SELECT * FROM bill WHERE bill_id = %s", bill_id)
            data = list(c_check)
          c_check.close()

          today = datetime.date.today()
          c_bill = g.conn.execute('''
                INSERT INTO bill VALUES(%s, %s, %s, %s, %s)
                ''', bill_id, today, 'buy', amount, '')
          c_bill.close()

          # add to trade
          c_trade = g.conn.execute('''
                INSERT INTO trade VALUES(%s, %s, %s)
                ''', acc_id, ip_id, bill_id)
          c_trade.close()

          info = "Successful to buy the product!"

          c = g.conn.execute("SELECT * FROM account WHERE acc_id=%s", acc_id)
          acc = []
          for result in c:
            acc.append(list(result))
          c.close()

          c1 = g.conn.execute("SELECT * FROM owns WHERE acc_id=%s", acc_id)
          own = []
          for result in c1:
            own.append(list(result))
          c1.close()

          c2 = g.conn.execute("SELECT t.acc_id, t.ip_id, t.bill_id, b.date, b.type, b.amount, b.note FROM bill b, trade t WHERE b.bill_id=t.bill_id and t.acc_id=%s", acc_id)
          bill = []
          for result in c2:
            bill.append(list(result))
          c2.close()

          context = dict(data=info, acc=acc, own=own, bill=bill)
          c2.close()
          return render_template("buy_success.html", **context)

  else:
    return redirect('ip.html')


@app.route('/sell/<acc_id>/<ip_id>', methods=['POST', 'GET'])
def sell(acc_id, ip_id):

  info = ""
  acc_id = acc_id.strip("'][")
  c1 = g.conn.execute('''
          SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, s.capital_price, s.open_price, s.close_price
          FROM investment_product ip, stock s
          WHERE ip.ip_id = s.ip_id and ip.ip_id = %s
          ''', ip_id)
  data = list(c1)
  if len(data) > 0:
    type = 'stock'
    title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date', 'Expire Date',
           'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description', 'Stock Capital Price', 'Stock Open Price', 'Stock Close Price']
  else:
    c2 = g.conn.execute('''
                SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, b.maturity, b.face_value, b.issue_price
                FROM investment_product ip, bond b
                WHERE ip.ip_id = b.ip_id and ip.ip_id = %s
                ''', ip_id)
    data = list(c2)
    if len(data) > 0:
      type = 'bond'
      title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date', 'Expire Date',
               'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description', 'Bond Maturity',
               'Bond Face Value', 'Bond Issue Price']
    else:
      c3 = g.conn.execute('''
                    SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, g.gold_price
                    FROM investment_product ip, gold g
                    WHERE ip.ip_id = g.ip_id and ip.ip_id = %s
                    ''', ip_id)
      data = list(c3)
      if len(data) > 0:
        type = 'gold'
        title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date', 'Expire Date',
                 'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description', 'Gold Price']
      c3.close()
    c2.close()
  c1.close()

  c4 = g.conn.execute('''
      SELECT cash_balance, inv_balance, total_value
      FROM account
      WHERE acc_id = %s
      ''', acc_id)
  vals = list(c4)
  val = [vals[0][0], vals[0][1], vals[0][2]]
  c4.close()

  c5 = g.conn.execute('''
        SELECT amount FROM owns WHERE acc_id=%s and ip_id=%s
    ''', acc_id, ip_id)
  val.append(c5.fetchone()[0])
  c5.close()

  context = dict(info = info, type=type, data=data, title=title, acc_id=acc_id, ip_id = ip_id, val=val)
  return render_template("sell.html", **context)

@app.route('/sell_check', methods=['POST', 'GET'])
def sell_check():
  if request.method == 'POST':
      acc_id = request.form['acc_id']
      ip_id = request.form['ip_id']
      amount = request.form['amount']

      transaction = True

      # check own_amount > amount
      c1 = g.conn.execute("SELECT amount FROM owns WHERE acc_id=%s and ip_id=%s", acc_id, ip_id)
      amount_owned = c1.fetchone()[0]
      if is_number(amount) == False:
        transaction = False
        info = "Please input a valid amount."
      elif float(amount) <= 0:
        transaction = False
        info = "Please input a valid positive amount."
      elif float(amount) > float(amount_owned):
          transaction = False
          info = "Cannot sell more than you owned."
      c1.close()

      if transaction == False:
        c1 = g.conn.execute('''
                SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, s.capital_price, s.open_price, s.close_price
                FROM investment_product ip, stock s
                WHERE ip.ip_id = s.ip_id and ip.ip_id = %s
                ''', ip_id)
        data = list(c1)
        if len(data) > 0:
          type = 'stock'
          title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date', 'Expire Date',
                   'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description',
                   'Stock Capital Price', 'Stock Open Price', 'Stock Close Price']
        else:
          c2 = g.conn.execute('''
                      SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, b.maturity, b.face_value, b.issue_price
                      FROM investment_product ip, bond b
                      WHERE ip.ip_id = b.ip_id and ip.ip_id = %s
                      ''', ip_id)
          data = list(c2)
          if len(data) > 0:
            type = 'bond'
            title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date',
                     'Expire Date',
                     'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description',
                     'Bond Maturity',
                     'Bond Face Value', 'Bond Issue Price']
          else:
            c3 = g.conn.execute('''
                          SELECT ip.ip_id, ip.ip_name, ip.risk_type, ip.curr_yield, ip.min_inv_value, ip.create_date, ip.expire_date, ip.freezing_time, ip.note, ip.status, ip.curr_value, ip.exp_value, ip.description, g.gold_price
                          FROM investment_product ip, gold g
                          WHERE ip.ip_id = g.ip_id and ip.ip_id = %s
                          ''', ip_id)
            data = list(c3)
            if len(data) > 0:
              type = 'gold'
              title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date',
                       'Expire Date',
                       'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description',
                       'Gold Price']
            c3.close()
          c2.close()
        c1.close()

        c4 = g.conn.execute('''
          SELECT cash_balance, inv_balance, total_value
          FROM account
          WHERE acc_id = %s
          ''', acc_id)
        vals = list(c4)
        val = [vals[0][0], vals[0][1], vals[0][2]]
        c4.close()

        c5 = g.conn.execute('''
            SELECT amount FROM owns WHERE acc_id=%s and ip_id=%s
            ''', acc_id, ip_id)
        val.append(c5.fetchone()[0])
        c5.close()

        context = dict(info=info, type=type, data=data, title=title, acc_id=acc_id, ip_id=ip_id, val=val)
        return render_template("sell.html", **context)

      else:
        # make transaction
          # deduct to owns
          c_own_check = g.conn.execute("SELECT * FROM owns WHERE acc_id=%s and ip_id=%s", acc_id, ip_id)
          data = list(c_own_check)
          original_amount = data[0][2]
          new_amount = float(original_amount)-float(amount)
          if new_amount > 0:
            c_own = g.conn.execute('''
                  UPDATE owns SET amount=%s WHERE acc_id=%s and ip_id=%s
                  ''', new_amount, acc_id, ip_id)
          else:
            c_own = g.conn.execute('''
                  DELETE FROM owns WHERE acc_id=%s and ip_id=%s
                  ''', acc_id, ip_id)
          c_own.close()

          # update account value
          c_acc = g.conn.execute("SELECT cash_balance, inv_balance FROM account WHERE acc_id=%s", acc_id)
          data = list(c_acc)
          cash_bal_ori, inv_bal_ori = data[0][0], data[0][1]
          inv_bal_new = float(inv_bal_ori)-float(amount)
          cash_bal_new = float(cash_bal_ori)+float(amount)
          c_acc_update = g.conn.execute("UPDATE account SET cash_balance=%s, inv_balance=%s WHERE acc_id=%s", cash_bal_new, inv_bal_new, acc_id)
          c_acc_update.close()
          c_acc.close()

          # add to bill
          bill_id = generate_id(5)
          c_check = g.conn.execute("SELECT * FROM bill WHERE bill_id = %s", bill_id)
          data = list(c_check)
          while len(data)!=0:
            bill_id = generate_id(6)
            c_check = g.conn.execute("SELECT * FROM bill WHERE bill_id = %s", bill_id)
            data = list(c_check)
          c_check.close()

          today = datetime.date.today()
          c_bill = g.conn.execute('''
                INSERT INTO bill VALUES(%s, %s, %s, %s, %s)
                ''', bill_id, today, 'sell', amount, '')
          c_bill.close()

          # add to trade
          c_trade = g.conn.execute('''
                INSERT INTO trade VALUES(%s, %s, %s)
                ''', acc_id, ip_id, bill_id)
          c_trade.close()

          info = "Successful to sell the product!"

          c = g.conn.execute("SELECT * FROM account WHERE acc_id=%s", acc_id)
          acc = []
          for result in c:
            acc.append(list(result))
          c.close()

          c1 = g.conn.execute("SELECT * FROM owns WHERE acc_id=%s", acc_id)
          own = []
          for result in c1:
            own.append(list(result))
          c1.close()

          c2 = g.conn.execute("SELECT t.acc_id, t.ip_id, t.bill_id, b.date, b.type, b.amount, b.note FROM bill b, trade t WHERE b.bill_id=t.bill_id and t.acc_id=%s", acc_id)
          bill = []
          for result in c2:
            bill.append(list(result))
          c2.close()

          context = dict(data=info, acc=acc, own=own, bill=bill)
          c2.close()
          return render_template("buy_success.html", **context)

  else:
    return redirect('ip.html')


@app.route('/back_action', methods=['POST', 'GET'])
def back_action():
  acc = request.form['acc']
  acc_id = acc.strip("'][")
 
  c3 = g.conn.execute("SELECT user_id FROM Open WHERE acc_id=%s", acc_id)
  user_id = c3.fetchone()[0]
  c3.close()

  # redirect to account.html
  # get all the account information
  cursor = g.conn.execute('SELECT * FROM Account WHERE Acc_id = %s AND Acc_id in (SELECT Acc_id FROM Open WHERE user_id = %s)', acc_id, user_id)
  acc = []
  acc_name = []
  cash_balance = []
  inv_balance = []
  total_value = []
  for result in cursor:
    acc.append(result['acc_id'])
    acc_name.append(result['acc_name'])
    cash_balance.append(result['cash_balance'])
    inv_balance.append(result['inv_balance'])
    total_value.append(result['total_value'])
  cursor.close()

  # get owning investment product information
  cursor = g.conn.execute('SELECT * FROM Owns O, Investment_Product IP WHERE O.Acc_id = %s AND O.IP_id = IP.IP_id', acc_id)
  O_IP_id = []
  O_amount = []
  O_ip_name = []
  O_risk_type = []
  O_curr_yield = []
  for result in cursor:
    O_IP_id.append(result['ip_id'])
    O_amount.append(result['amount'])
    O_ip_name.append(result['ip_name'])
    O_risk_type.append(result['risk_type'])
    O_curr_yield.append(result['curr_yield'])
  cursor.close()

  # get watching investment product information
  cursor = g.conn.execute('SELECT * FROM Contains C, Investment_Product IP WHERE C.Acc_id = %s AND C.IP_id = IP.IP_id', acc_id)
  C_IP_id = []
  C_list_id = []
  C_add_time = []
  C_ip_name = []
  C_risk_type = []
  C_curr_yield = []
  for result in cursor:
    C_IP_id.append(result['ip_id'])
    C_list_id.append(result['list_id'])
    C_add_time.append(result['add_time'])
    C_ip_name.append(result['ip_name'])
    C_risk_type.append(result['risk_type'])
    C_curr_yield.append(result['curr_yield'])
  cursor.close()

  # get payment method information
  cursor = g.conn.execute('SELECT * FROM Has_Payment_method WHERE Acc_id = %s', acc_id)
  pay_id = []
  type = []
  card_no = []
  card_name = []
  card_expire = []
  create_date = []
  for result in cursor:
    pay_id.append(result['pay_id'])
    type.append(result['type'])
    card_no.append(result['card_no'])
    card_name.append(result['card_name'])
    card_expire.append(result['card_expire'])
    create_date.append(result['create_date'])
  cursor.close()

  if len(acc) == 0:
    # get information needed to redirect to user.html
    # get information in user
    cursor = g.conn.execute("SELECT * FROM Users WHERE user_id = %s", user_id)
    user_id_back = []
    user_name = [] 
    mobile = []
    email = []
    address = []
    passport_no = []

    for result in cursor:
      user_id_back.append(result['user_id'])
      user_name.append(result['user_name'])
      mobile.append(result['mobile'])
      email.append(result['email'])
      address.append(result['address'])
      passport_no.append(result['passport_no'])
    cursor.close()

    # get all accounts belong to the user
    cursor = g.conn.execute("SELECT O.acc_id, A.acc_name, O.since FROM Open O, Account A WHERE user_id = %s AND A.acc_id = O.acc_id", user_id)
    acc_id = []
    since = []
    acc_name=[]

    for result in cursor:
      acc_id.append(result['acc_id'])
      acc_name.append(result['acc_name'])
      since.append(result['since'])
    cursor.close()
    user_id = user_id.split()
    context = dict(user_id=user_id, user_name=user_name, mobile=mobile, email=email, address=address, passport_no=passport_no, acc_id=acc_id, acc_name=acc_name, since=since)
    return render_template("user.html", **context)
  else:
    context = dict(acc=acc, acc_name=acc_name, cash_balance=cash_balance, inv_balance=inv_balance, total_value=total_value, pay_id=pay_id, type=type, card_no=card_no, card_name=card_name, card_expire=card_expire, create_date=create_date, O_IP_id=O_IP_id, O_amount=O_amount, O_ip_name=O_ip_name, O_risk_type=O_risk_type, O_curr_yield=O_curr_yield, C_IP_id=C_IP_id, C_list_id=C_list_id, C_add_time=C_add_time, C_ip_name=C_ip_name, C_risk_type=C_risk_type, C_curr_yield=C_curr_yield)
    return render_template("account.html", **context)


@app.route('/backtoaccountlogin', methods=['POST', 'GET'])
def backtoaccountlogin():
  acc = request.form['acc']
  acc_id = acc.strip("'][")
 
  c3 = g.conn.execute("SELECT user_id FROM Open WHERE acc_id=%s", acc_id)
  user_id = c3.fetchone()[0]
  c3.close()

  # redirect to account.html
  # get all the account information
  cursor = g.conn.execute('SELECT * FROM Account WHERE Acc_id = %s AND Acc_id in (SELECT Acc_id FROM Open WHERE user_id = %s)', acc_id, user_id)
  acc = []
  acc_name = []
  cash_balance = []
  inv_balance = []
  total_value = []
  for result in cursor:
    acc.append(result['acc_id'])
    acc_name.append(result['acc_name'])
    cash_balance.append(result['cash_balance'])
    inv_balance.append(result['inv_balance'])
    total_value.append(result['total_value'])
  cursor.close()

  # get owning investment product information
  cursor = g.conn.execute('SELECT * FROM Owns O, Investment_Product IP WHERE O.Acc_id = %s AND O.IP_id = IP.IP_id', acc_id)
  O_IP_id = []
  O_amount = []
  O_ip_name = []
  O_risk_type = []
  O_curr_yield = []
  for result in cursor:
    O_IP_id.append(result['ip_id'])
    O_amount.append(result['amount'])
    O_ip_name.append(result['ip_name'])
    O_risk_type.append(result['risk_type'])
    O_curr_yield.append(result['curr_yield'])
  cursor.close()

  # get watching investment product information
  cursor = g.conn.execute('SELECT * FROM Contains C, Investment_Product IP WHERE C.Acc_id = %s AND C.IP_id = IP.IP_id', acc_id)
  C_IP_id = []
  C_list_id = []
  C_add_time = []
  C_ip_name = []
  C_risk_type = []
  C_curr_yield = []
  for result in cursor:
    C_IP_id.append(result['ip_id'])
    C_list_id.append(result['list_id'])
    C_add_time.append(result['add_time'])
    C_ip_name.append(result['ip_name'])
    C_risk_type.append(result['risk_type'])
    C_curr_yield.append(result['curr_yield'])
  cursor.close()

  # get payment method information
  cursor = g.conn.execute('SELECT * FROM Has_Payment_method WHERE Acc_id = %s', acc_id)
  pay_id = []
  type = []
  card_no = []
  card_name = []
  card_expire = []
  create_date = []
  for result in cursor:
    pay_id.append(result['pay_id'])
    type.append(result['type'])
    card_no.append(result['card_no'])
    card_name.append(result['card_name'])
    card_expire.append(result['card_expire'])
    create_date.append(result['create_date'])
  cursor.close()

  # get information needed to redirect to user.html
  # get information in user
  cursor = g.conn.execute("SELECT * FROM Users WHERE user_id = %s", user_id)
  user_id_back = []
  user_name = [] 
  mobile = []
  email = []
  address = []
  passport_no = []

  for result in cursor:
    user_id_back.append(result['user_id'])
    user_name.append(result['user_name'])
    mobile.append(result['mobile'])
    email.append(result['email'])
    address.append(result['address'])
    passport_no.append(result['passport_no'])
  cursor.close()

  # get all accounts belong to the user
  cursor = g.conn.execute("SELECT O.acc_id, A.acc_name, O.since FROM Open O, Account A WHERE user_id = %s AND A.acc_id = O.acc_id", user_id)
  acc_id = []
  since = []
  acc_name=[]

  for result in cursor:
    acc_id.append(result['acc_id'])
    acc_name.append(result['acc_name'])
    since.append(result['since'])
  cursor.close()
  user_id = user_id.split()
  context = dict(user_id=user_id, user_name=user_name, mobile=mobile, email=email, address=address, passport_no=passport_no, acc_id=acc_id, acc_name=acc_name, since=since)
  return render_template("user.html", **context)

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
