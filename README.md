# WeTrade

A investment database and trading platform.

COMS4111 Introduction to Database Systems

Prof. Luis Gravano

TA Mentor: Kim Tao

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
        - This page shows all the investment product owned by user account and belonging to his/her watching list with different `Status` and `Actoon`
                - For owned product, user could sell the product
                - For watching product, user could buy it or remove it from the watching list
        - User could check all avaiable investment product through `Check All Investment Product` button
        - This page shows all the payment information in this account and accepts adding new payment method (with red warning indicating acceptable input value)


4. Two web pages that require the most interesting database queries:
    - `/main` page shows Movies in the database, allows User to browse movies and information such as year, genre, runtime and overview. It shows the Talent that stars in a given movie and Reviews for each movie. On this page, we allow users to write reviews by inputing a rating and review text, which INSERTs a review tuple (or UPDATE it if a review for a movie by the current user already exists). In addition, if a user's review already exists for the movie, the form actually shows the previous review. This page is interesting because it shows a lot of information on movies, stars in each movie, and offers functionality for both browsing other users' reviews and writing reviews. Users are also able to search for movies by name, year or genre.
    - `/theaters` page shows Theaters in the database, displays information such as address, contact info and seat capacity. It shows the Showings at each Theater and allows Users to Book tickets using a form that INSERTs a Book tuple (if it exists, UPDATE the booking). In addition, the page shows the User's existing ticket Bookings. We also display the Reviews for each Theater and allow the User to write a review for each Theater (which inserts a rating and review text, or updates the existing review if it already exists). This page is interesting becuase it offers information on theaters, movie showings at each theater, reviews for theaters, the user's movie showing bookings, and offers functionality for booking showings and writing reviews on the same page.

---

## Developer Walkthrough

### Set up Python 3 environment

```py
# Install python 3 dependencies and virtualenv

sudo apt-get install postgresql-9.3 postgresql-server-dev-9.3 git python3-dev python3-pip
sudo pip3 install virtualenv
sudo pip3 install virtualenvwrapper
virtualenv -p python3 env
source env/bin/activate

# Navigate to goodviews directory and install modules

cd goodviews
pip install -r requirements.txt

# Start server on IPADDRESS:8111, navigate on browser
python server-python3.py
```

---

## Project Feedback/Changelog

03-01-2018:

- Updated SQL after Kim's feedback
- Added `NOT NULL` and `CHECK` constraints
- Replaced all instances of `CHAR` iwth `VARCHAR`
- Converted unique identifiers (<id>) to `SERIAL` type, foreign keys still `INTEGER`
