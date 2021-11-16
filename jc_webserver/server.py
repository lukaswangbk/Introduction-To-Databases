
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
# engine.execute(
#   """CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
#   );"""
# )
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


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


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
# @app.route('/')
# def index():
#   """
#   request is a special object that Flask provides to access web request information:
#
#   request.method:   "GET" or "POST"
#   request.form:     if the browser submitted a form, this contains the data in the form
#   request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2
#
#   See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data
#
#   """
#
#   # DEBUG: this is debugging code to see what request looks like
#   print(request.args)
#
#
#   #
#   # example of a database query
#   #
#   cursor = g.conn.execute("SELECT name FROM test")
#   names = []
#   for result in cursor:
#     names.append(result['name'])  # can also be accessed using result[0]
#   cursor.close()
#
#   #
#   # Flask uses Jinja templates, which is an extension to HTML where you can
#   # pass data to a template and dynamically generate HTML based on the data
#   # (you can think of it as simple PHP)
#   # documentation: https://realpython.com/primer-on-jinja-templating/
#   #
#   # You can see an example template in templates/index.html
#   #
#   # context are the variables that are passed to the template.
#   # for example, "data" key in the context variable defined below will be
#   # accessible as a variable in index.html:
#   #
#   #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
#   #     <div>{{data}}</div>
#   #
#   #     # creates a <div> tag for each element in data
#   #     # will print:
#   #     #
#   #     #   <div>grace hopper</div>
#   #     #   <div>alan turing</div>
#   #     #   <div>ada lovelace</div>
#   #     #
#   #     {% for n in data %}
#   #     <div>{{n}}</div>
#   #     {% endfor %}
#   #
#   context = dict(data = names)
#
#
#   #
#   # render_template looks in the templates/ folder for files.
#   # for example, the below file reads template/index.html
#   #
#   return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
# @app.route('/another')
# def another():
#   return render_template("another.html")

@app.route('/exp')
def exp():
  acc_id = '00001'
  c1 = g.conn.execute("SELECT list_id FROM create_watchinglist WHERE acc_id=%s", acc_id)
  list_id = c1.fetchone()[0]
  c1.close()

  context = dict(data=list_id)
  return render_template("exp.html", **context)



@app.route('/ip', methods=['POST', 'GET'])
def ip():
  query = '''SELECT * 
            FROM investment_product'''
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
  context = dict(data=table, title=title)
  return render_template("ip.html", **context)

@app.route('/ip_query', methods=['POST', 'GET'])
def ip_query():
  title = ['ID', 'Name', 'Risk Type', 'Current Yield', 'Minimum Investment value', 'Create Date', 'Expire Date',
           'Freezing Time', 'Note', 'Status', 'Current Value', 'Expected Value', 'Description', 'Category']

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

  context = dict(data=table, title=title)
  return render_template("ip.html", **context)

@app.route('/ip_action', methods=['POST', 'GET'])
def ip_action():
  ip_id = list(request.form)[0]
  acc_id = '00001'
  action = request.form[ip_id]

  if action == 'Buy':
    return redirect(url_for('buy', acc_id=acc_id, ip_id=ip_id))

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

    c3 = g.conn.execute("SELECT * FROM contains WHERE acc_id=%s", acc_id)
    data = []
    for row in c3:
      data.append(list(row))
    context = dict(data=data)
    return render_template('exp.html', **context)


@app.route('/buy/<acc_id>/<ip_id>', methods=['POST', 'GET'])
def buy(acc_id, ip_id):

  info = ""

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

  context = dict(info = info, type=type, data=data, title=title, acc_id=acc_id, ip_id = ip_id)
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
      c2 = g.conn.execute("SELECT pay_id FROM has_payment_method WHERE pay_id=%s and acc_id = %s", payment, acc_id)
      data = list(c2)
      if len(data) == 0:
        transaction = False
        info = "You don't have this payment method."
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

        context = dict(info=info, type=type, data=data, title=title, acc_id=acc_id, ip_id=ip_id)
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
          c_acc = g.conn.execute("SELECT inv_balance, total_value FROM account WHERE acc_id=%s", acc_id)
          data = list(c_acc)
          inv_bal_ori, tot_bal_ori = data[0][0], data[0][1]
          inv_bal_new = float(inv_bal_ori)+float(amount)
          tot_bal_new = float(tot_bal_ori)+float(amount)
          c_acc_update = g.conn.execute("UPDATE account SET inv_balance=%s, total_value=%s WHERE acc_id=%s", inv_bal_new, tot_bal_new, acc_id)
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
