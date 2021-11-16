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
2. URL of web application: [HERE](http://34.138.131.47:8111/)
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
    - `/main` page shows Movies in the database, allows User to browse movies and information such as year, genre, runtime and overview. It shows the Talent that stars in a given movie and Reviews for each movie. On this page, we allow users to write reviews by inputing a rating and review text, which INSERTs a review tuple (or UPDATE it if a review for a movie by the current user already exists). In addition, if a user's review already exists for the movie, the form actually shows the previous review. This page is interesting because it shows a lot of information on movies, stars in each movie, and offers functionality for both browsing other users' reviews and writing reviews. Users are also able to search for movies by name, year or genre.
    - `/theaters` page shows Theaters in the database, displays information such as address, contact info and seat capacity. It shows the Showings at each Theater and allows Users to Book tickets using a form that INSERTs a Book tuple (if it exists, UPDATE the booking). In addition, the page shows the User's existing ticket Bookings. We also display the Reviews for each Theater and allow the User to write a review for each Theater (which inserts a rating and review text, or updates the existing review if it already exists). This page is interesting becuase it offers information on theaters, movie showings at each theater, reviews for theaters, the user's movie showing bookings, and offers functionality for booking showings and writing reviews on the same page.
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