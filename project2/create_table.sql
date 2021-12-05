--- Type for risk
create type risk AS ENUM ('high', 'medium', 'low');

--- Type for status
create type status AS ENUM ('open', 'closed');

--- Change type and change text to ip
create table Investment_Product_new (
    IP_id VARCHAR(20),
    IP_name VARCHAR(100) NOT NULL, 
    Risk_type risk NOT NULL, 
    Curr_yield REAL NOT NULL CHECK (Curr_yield>=0), 
    Min_inv_value REAL NOT NULL CHECK (Min_inv_value>=0), 
    Create_date DATE,
    Expire_date DATE,
    Freezing_time INTEGER NOT NULL CHECK (Freezing_time>=0), 
    Note TEXT,
    Status status NOT NULL, 
    Curr_value REAL CHECK (Curr_value>=0),
    Exp_value REAL CHECK (Exp_value>=0 OR Exp_value=NULL),
    Description TEXT,

    PRIMARY KEY (IP_id), 
    UNIQUE (IP_name)
);

--- Create function for trigger
CREATE FUNCTION check_length() RETURNS trigger AS $check_length$
    DECLARE
        i integer; 
        test real;
    BEGIN
        -- Check that contained_ip and portion are given
        IF NEW.contained_ip IS NULL THEN
            RAISE EXCEPTION 'contained_ip cannot be null';
        END IF;
        IF NEW.portion IS NULL THEN
            RAISE EXCEPTION 'portion cannot be null';
        END IF;

        -- Check the length of contained_ip and portion are same
        IF CARDINALITY(NEW.contained_ip) != CARDINALITY(NEW.portion) THEN
            RAISE EXCEPTION 'contained_ip and portion should have same length';
        END IF;

        -- Check the length of contained_ip and portion are same
        IF CARDINALITY(NEW.contained_ip) != CARDINALITY(NEW.portion) THEN
            RAISE EXCEPTION 'contained_ip and portion should have same length';
        END IF;

        -- Check portion sum to 1

        IF (SELECT SUM(t) FROM UNNEST(NEW.portion) t) >= 1.00001 or (SELECT SUM(t) FROM UNNEST(NEW.portion) t) <= 0.99999 THEN
            SELECT INTO test SUM(t) FROM UNNEST(NEW.portion) t;
            RAISE EXCEPTION 'portion should be sum to 1. Current is %', test;
        END IF;

        -- Check portion are all greater than 0
        FOR i IN array_lower(NEW.portion, 1) .. array_upper(NEW.portion, 1)
        LOOP
            IF NEW.portion[i] <= 0 THEN
                RAISE EXCEPTION 'portion should greater than 0';
            END IF;
        END LOOP;

        RETURN NEW;
    END;
$check_length$ LANGUAGE plpgsql;

--- Create trigger for composed
CREATE TRIGGER check_length BEFORE INSERT OR UPDATE ON composed
    FOR EACH ROW EXECUTE FUNCTION check_length();

--- Create new type of product: composed, combining different portition of  
create table composed(
    IP_id VARCHAR(20),
    contained_ip VARCHAR(20)[10] NOT NULL,
    portion REAL[10] NOT NULL,
    PRIMARY KEY(IP_id),
    FOREIGN KEY(IP_id) REFERENCES Investment_Product_new 
        ON DELETE CASCADE
        ON UPDATE CASCADE
)
INHERITS(Investment_Product_new);

create table stock_new(
    IP_id VARCHAR(20),
    Capital_price REAL CHECK (Capital_price>=0),
    Open_price REAL NOT NULL CHECK (Open_price>=0), 
    Close_price REAL NOT NULL CHECK (Close_price>=0),

    PRIMARY KEY(IP_id),
    FOREIGN KEY(IP_id) REFERENCES Investment_Product_new 
        ON DELETE CASCADE
        ON UPDATE CASCADE
)
INHERITS(Investment_Product_new);

create table bond_new(
    IP_id VARCHAR(20),
    Maturity INTEGER NOT NULL CHECK (Maturity>=0),
    Face_value REAL NOT NULL CHECK (Face_value>=0),
    Issue_price REAL NOT NULL CHECK (Issue_price>=0),

    PRIMARY KEY(IP_id),
    FOREIGN KEY(IP_id) REFERENCES Investment_Product_new 
        ON DELETE CASCADE
        ON UPDATE CASCADE
)
INHERITS(Investment_Product_new);

create table gold_new(
    IP_id VARCHAR(20),
    Gold_price REAL NOT NULL CHECK (Gold_price>=0),

    PRIMARY KEY(IP_id),
    FOREIGN KEY(IP_id) REFERENCES Investment_Product_new 
        ON DELETE CASCADE
        ON UPDATE CASCADE
)
INHERITS(Investment_Product_new);
