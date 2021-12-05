# WeTrade

A investment database and trading platform.

COMS4111 Introduction to Database Systems

Prof. Luis Gravano

TA Mentor: Matt Zinman

Team: Jiaqing Chen (jc5657) & Lukas Wang (bw2712)

---

## Project 1 Part 3

**NOTE: Implementation in Python 3.5**

**Proposal Description:** Investment is a popular life style in the modern world. In this project, we plan to build an investment product trading system (WeTrade) that allows individuals to manage their money by investing well-built investment products. In our design, there are large amounts of investment product available for trading. Customers (Users) enter the virtual market, search for what they interest, and make a trade to invest their money. The interesting and also challenging part is that user’s account value will automatically change with the floating return rate of different products, user could also classify all investment product using multiple filter, and the system will capture every deal and promptly reflect them on market-side, bill-side and user-side.

Following requirements proposed on [websit](http://www.cs.columbia.edu/~gravano/cs4111/Proj1-3/) are satisfied. Detailed functionality is illustrated in the sections below:

1. The PostgreSQL account where DB resides: jc5657
2. URL of web application: [http://34.138.131.47:8111](http://34.138.131.47:8111/)
3. Features Implemented:
    - User Login:
        - User can login through `\` (only user_id that in the database is acceptable, otherwise the page dumps red warning and ask for anther User ID input)
    - User Information and Login:
        - After user login, the page shows user information and accepts update (with red warning indicating acceptable input value)
        - The page shows all the account belongs to the user and accepts create new account (with red warning indicating acceptable input value)
        - User can login any one of his/her account (with red warning indicating acceptable input value)
    - Account Information:
        - After user login, the page shows account information and accepts update of account name
        - User could go back to account login through back button
        - This page shows all the investment product owned by user account and belonging to his/her watching list with different `Status` and `Action`
          - For owned product, user could sell the product
          - For watching product, user could buy it or remove it from the watching list
        - User could check all avaiable investment product through `Check All Investment Product` button
        - This page shows all the payment information in this account and accepts adding new payment method (with red warning indicating acceptable input value)
    - Investment Product
        - This page shows all investment products that are available to be traded on the system
        - User could add filters and query the product they are interested, they may
            - search the `ID` or `Name` by keywords
            - select a specific `Risk`, `Status`, `Category` group. Specially, different information will be shown under different `Category` group, ex. "stock capital price", "stock open price", "stock close price" will show for stock products but not bond nor gold. If user chooses to see all category, only the class name will be shown for each product.
            - specify a listing order on `Current Yield`, `Minimum Investment value`, `Freezing Time`, `Create Date`, `Expire Date`
            - see the query result through `Apply` button
        - User chould buy the interested product through `Buy` button, or add it to their watching list through `Follow` button. 
        - `Back` button redirects users to their account page.
    - Buy & Sell
        - After user click the `Buy` or `Sell` button for the product, they will be directed to the buy&sell page.
        - This page shows the informations of selected product and user's account balance, and allows user to input the amount they want to buy or sell.
            - To buy a product, the amount should not be lower than the product minimum investment value. If the user's cash balance cannot cover the amount, the payment method field is required, which should be the user's payment method id.
            - To sell a product, the amount should not be greater than the user owned.
            - If invalid input is received, the page will reload and show the corresponding illegal input.
        - User can cancel the trading through `Cancel, go back to product page`.
        - Buying a product will decrease the user's cash balance but increase the investment balance. If cash balance is not sufficient, user will use extra payment, which increases the total value of an account.
        - Selling a product increases the cash balance and decrease the investment balance. Total value remains.
    - Trading successful page
        - After sell & buy completed, this page shows the successful information and the current account's information, investment product owned, and trading history.
        - User can go back through `Go back to the product page`.
4. Features Not Implemented:
    - NA
5. Two web pages that require the most interesting database queries:
    - `account.html` Account Information page shows the account information for given account id. It could also go back to the account login page so it need user id is also needed for this page in order to implement ``Back to Account Login`` function. It could also update the account name using UPDATA operation. In the investment Product section, it **SELECT** all the investment products (1) owned by this account by looking into table Investment_Product and table Owns in database (2) in the watching list by looking into table Investment_Product and table Contains in database. It also adds the feature `Status` and differnet `Action` based on types of product (Owned or Watching). (1) For Owned Product: User can sell the product; (2) For Watching Product: User can buy directly (Do not necessary to check all investment product first using the button ``Check All Investment Product`` and then perform buy operation) or remove it from watching list using **DELETE** operation. It also offers information about payment method linked with this account by **SELECT**ing from table Has_Payment_method. Adding new payment method is also implementated with constrain of payment id cannot be empty and perform different **INSERT** or **UPDATE** operation to set value=NULL when other features (Type, Card Number, Card Name, Card Expire) is empty. The reason why this is interesting is it serves as a main page for user to operate the system and contains most information user need to check or update in the investment system for future operation.
    - `/ip` page shows all investment products on the system. It lists all related information of each product and allows users to add filters on it or search for a specific product. It is interesting because every user input or selection is related to a **SELECT** SQL command part. The system will identify different types of user input, combine all of them, and construct one specific SQL command.
        - In the `ID` and `Name` textbox, user inputs some keywords, then the system transfers the "keyword" into "%keyword%" format, construct the **WHERE** part of SQL  command to be **WHERE ip_id LIKE "%keyword%" and ip_name LIKE "%keyword%"**.
        - In the `Risk`, `Status` selection list, user performs a selection, the system receives the selection and continuely construct **WHERE ... and risk LIKE "risk_selection" and status LIKE "status_selection**.
        - In the `Category` selection list, user chooses a specific category, and the system will join the "investment product" table with "stock", "bond", or "gold" to perform selection.
        - In the order selection list like `Current Yield`, users select an order they want, and the system correspondingly construct the **ORDER** string. For example, "from high to low" is selected for "Current Yield" and "from low to high" is selected for "Minimum Investment value", then the SQL command needs **ORDER BY curr_yield DESC, min_inv_value ASC**.
---

## Developer Walkthrough

### Set up Python 3 environment

```py
# Clone the project

git clone https://github.com/lukaswangbk/COMS4111.git

# Navigate to directory and install modules

cd COMS4111
pip install -r requirements.txt

# Start server on IPADDRESS:8111, navigate on browser
python server-python3.py
or 
python server-python3.py --debug
```

---

## Project Update Log