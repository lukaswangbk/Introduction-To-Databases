
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
  return render_template("login.html")


@app.route('/logincheck', methods=['POST'])
def logincheck():
  user_id = request.form['user_id']
  cursor = g.conn.execute('SELECT user_id FROM Users WHERE user_id = %s', user_id)
  user_id = []
  for result in cursor:
    user_id.append(result['user_id'])
  cursor.close()

  if len(user_id) == 0:
    return redirect('/')
  else:
    return redirect(url_for('user', user = user_id))

@app.route('/<user>')
def user(user):
  user = user[2:-2]

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
  user_id = user_id[2:-2]
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
  user_id = user_id[2:-2]

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
    cursor = g.conn.execute("SELECT O.acc_id, A.acc_name, O.since FROM Open O, Account A WHERE user_id = %s AND A.acc_id = O.acc_id", user)
    acc_id = []
    since = []
    acc_name=[]

    for result in cursor:
      acc_id.append(result['acc_id'])
      acc_name.append(result['acc_name'])
      since.append(result['since'])
    cursor.close()

    context = dict(user_id=user_id, user_name=user_name, mobile=mobile, email=email, address=address, passport_no=passport_no, acc_id=acc_id, acc_name=acc_name, since=since)
    return render_template("user.html", **context)
  else:
    context = dict(acc=acc, acc_name=acc_name, cash_balance=cash_balance, inv_balance=inv_balance, total_value=total_value, pay_id=pay_id, type=type, card_no=card_no, card_name=card_name, card_expire=card_expire, create_date=create_date, O_IP_id=O_IP_id, O_amount=O_amount, O_ip_name=O_ip_name, O_risk_type=O_risk_type, O_curr_yield=O_curr_yield, C_IP_id=C_IP_id, C_list_id=C_list_id, C_add_time=C_add_time, C_ip_name=C_ip_name, C_risk_type=C_risk_type, C_curr_yield=C_curr_yield)
    return render_template("account.html", **context)


@app.route('/addaccount', methods=['POST'])
def addaccount():
  acc_id = request.form['acc_id']
  since = request.form['since']
  user_id = request.form['user_id']
  user = user_id
  user_id = user_id[2:-2]
  acc_name = request.form['acc_name']
  if acc_id != '' and since != '' and acc_name != '':
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
  acc_id = acc[2:-2]

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
  create_date = []
  for result in cursor:
    pay_id.append(result['pay_id'])
    type.append(result['type'])
    card_no.append(result['card_no'])
    card_name.append(result['card_name'])
    card_expire.append(result['card_expire'])
    create_date.append(result['create_date'])
  cursor.close()

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
  create_date = request.form['create_date']
  if type != '' and card_no != '' and card_name != '' and card_expire != '' and create_date != '':
    g.conn.execute('INSERT INTO Has_Payment_method VALUES (%s,%s,%s,%s,%s,%s,%s)', pay_id, type, card_no, card_name, card_expire, acc_id, create_date)
  else:
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
    if create_date == '':
      g.conn.execute('UPDATE Has_Payment_method SET create_date = NULL WHERE (pay_id,acc_id) = (%s,%s)', pay_id, acc_id)
    else: 
      g.conn.execute('UPDATE Has_Payment_method SET create_date = %s WHERE (pay_id,acc_id) = (%s,%s)', create_date, pay_id, acc_id)
    
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
  create_date = []
  for result in cursor:
    pay_id.append(result['pay_id'])
    type.append(result['type'])
    card_no.append(result['card_no'])
    card_name.append(result['card_name'])
    card_expire.append(result['card_expire'])
    create_date.append(result['create_date'])
  cursor.close()

  context = dict(acc=acc, acc_name=acc_name, cash_balance=cash_balance, inv_balance=inv_balance, total_value=total_value, pay_id=pay_id, type=type, card_no=card_no, card_name=card_name, card_expire=card_expire, create_date=create_date, O_IP_id=O_IP_id, O_amount=O_amount, O_ip_name=O_ip_name, O_risk_type=O_risk_type, O_curr_yield=O_curr_yield, C_IP_id=C_IP_id, C_list_id=C_list_id, C_add_time=C_add_time, C_ip_name=C_ip_name, C_risk_type=C_risk_type, C_curr_yield=C_curr_yield)
  return render_template("account.html", **context)


@app.route('/checkallinvestmentproduct', methods=['POST'])
def checkallinvestmentproduct():
  acc_id = request.form['acc_id']
  context = dict(acc_id=acc_id)
  return render_template("ip.html", **context)

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
