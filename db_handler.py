from MARIADB_CREDS import DB_CONFIG
from mariadb import connect
from models.RentalHistory import RentalHistory
from models.Waitlist import Waitlist
from models.Item import Item
from models.Rental import Rental
from models.Customer import Customer
from datetime import date, timedelta


conn = connect(user=DB_CONFIG["username"], password=DB_CONFIG["password"], host=DB_CONFIG["host"],
               database=DB_CONFIG["database"], port=DB_CONFIG["port"])


cur = conn.cursor()

#add_item: inserts a new item into the item table. You will need to generate a new i_item_sk (e.g., MAX(i_item_sk) + 1). 
#Use new_item.start_year to construct the i_rec_start_date (e.g., '2025-01-01')
def add_item(new_item: Item = None):
    """
    new_item - An Item object containing a new item to be inserted into the DB in the item table.
        new_item and its attributes will never be None.
    """
    if new_item == None :
        return 
    item_id = new_item.item_id
    product_name = new_item.product_name    
    brand = new_item.brand
    category = new_item.category
    manufact = new_item.manufact
    current_price = new_item.current_price
    start_year = new_item.start_year
    num_owned = new_item.num_owned
    max_finder = "SELECT MAX(i_item_sk) FROM item"
    cur.execute(max_finder)
    item_sk = cur.fetchone()
    if item_sk[0] == None:
        item_sk1=0
    else:
        item_sk1 = item_sk[0]+1
    parameters = (item_sk1, item_id,  f"{start_year}-01-01",product_name, brand, None, category, manufact, current_price, num_owned)
    sql_insert = "INSERT INTO item (i_item_sk, i_item_id, i_rec_start_date, i_product_name, i_brand, i_class, i_category, i_manufact, i_current_price, i_num_owned) VALUES (?,?,?,?,?,?,?,?,?,?)"
    cur.execute(sql_insert, parameters)




def add_customer(new_customer: Customer = None):
    """
    new_customer - A Customer object containing a new customer to be inserted into the DB in the customer table.
        new_customer and its attributes will never be None.
    """
    if new_customer == None:
        return
    
    street_number_street_name, city, state_zip = new_customer.address.split(',', 2)
    street_number, street_name = street_number_street_name.split(' ', 1)
    state, zip_c = state_zip.split(' ', 1)
    max_finder_cu = "SELECT MAX(ca_address_sk) FROM customer_address"
    cur.execute(max_finder_cu)
    address_sk = cur.fetchone()
    if address_sk[0] == None:
        address_sk1=0
    else:
        address_sk1 = address_sk[0]+1
    add_parameters = (address_sk1, street_number.strip(), street_name.strip(), city.strip(), state.strip(), zip_c.strip())
    address_maker = "INSERT INTO customer_address (ca_address_sk, ca_street_number, ca_street_name, ca_city, ca_state,  ca_zip) VALUES (?,?,?,?,?,?)"
    cur.execute(address_maker, add_parameters)

    max_finder_cu = "SELECT MAX(c_customer_sk) FROM customer"
    cur.execute(max_finder_cu)
    customer_sk = cur.fetchone()
    if customer_sk[0] == None:
        c_customer_sk1=0
    else:
        c_customer_sk1 = customer_sk[0]+1
    customer_id1 = new_customer.customer_id
    name1, name2 = new_customer.name.split(' ', 1)
    email1 = new_customer.email
    parameters = (c_customer_sk1, customer_id1.strip(), name1.strip(), name2.strip(), address_sk1, email1.strip())
    insert_sql = "INSERT INTO customer (c_customer_sk, c_customer_id, c_first_name, c_last_name, c_current_addr_sk, c_email_address) VALUES (?,?,?,?,?,?)"
    cur.execute(insert_sql, parameters)

def edit_customer(original_customer_id: str = None, new_customer: Customer = None):
    """
    original_customer_id - A string containing the customer id for the customer to be edited.
    new_customer - A Customer object containing attributes to update. If an attribute is None, it should not be altered.
    """
    if original_customer_id == None or new_customer ==None:
        return
    og_id =original_customer_id
    #case of non-empty name
    if new_customer.name != None:
        name1, name2 =new_customer.name.split(" ", 1)
        parameters = (name1, name2, og_id)
        namesql = "UPDATE customer SET c_first_name = ?, c_last_name = ? WHERE c_customer_id = ?"
        cur.execute(namesql, parameters)

    #case of non-empty email_address
    if new_customer.email != None:
        parameters = (new_customer.email, og_id)
        namesql = "UPDATE customer SET c_email_address = ? WHERE c_customer_id = ?"
        cur.execute(namesql, parameters)

    #case of non-empty address which needs to be changed
    if new_customer.address != None:
        street_number_street_name, city, state_zip = new_customer.address.split(',', 2)
        street_number, street_name = street_number_street_name.split(' ', 1)
        state, zip_c = state_zip.strip().split(' ', 1)
        sql_find_old_add = "SELECT c_current_addr_sk FROM customer WHERE c_customer_id =  ?"
        cur.execute(sql_find_old_add, (og_id,))
        old_address_sk = cur.fetchone()[0]
        sql_fix_add= "UPDATE customer_address SET ca_street_number = ?, ca_street_name = ?, ca_city = ?, ca_state=?, ca_zip=? WHERE ca_address_sk = ?"
        parameters = (street_number.strip(), street_name.strip(), city.strip(), state.strip(), zip_c.strip(),old_address_sk)
        cur.execute(sql_fix_add, parameters)



def rent_item(item_id: str = None, customer_id: str = None):
    """
    item_id - A string containing the Item ID for the item being rented.
    customer_id - A string containing the customer id of the customer renting the item.
    """
    if item_id == None or customer_id == None:
        return
    today = str(date.today())
    due_date = str(date.today() + timedelta(days=14))
    sql = "INSERT INTO rental (item_id, customer_id, rental_date, due_date) VALUES (?,?,?,?)"
    parameters = (item_id, customer_id, today, due_date)
    cur.execute(sql, parameters)



def waitlist_customer(item_id: str = None, customer_id: str = None) -> int:
    """
    Returns the customer's new place in line.
    """
    raise NotImplementedError("you must implement this function")

def update_waitlist(item_id: str = None):
    """
    Removes person at position 1 and shifts everyone else down by 1.
    """
    raise NotImplementedError("you must implement this function")


def return_item(item_id: str = None, customer_id: str = None):
    """
    Moves a rental from rental to rental_history with return_date = today.
    """
    if item_id == None or customer_id == None:
        return
    today = str(date.today())
    init_search_params = (item_id, customer_id)
    init_search_sql = "SELECT rental_date, due_date FROM rental WHERE item_id = ? AND customer_id = ?"
    cur.execute(init_search_sql, init_search_params)
    output = cur.fetchone()
    if output != None:
        rent_date = output[0]
        date_due = output[1]
    else:
        return
    create_new = "INSERT INTO rental_history (item_id, customer_id, rental_date, due_date, return_date) VALUES (?,?,?,?,?)"
    final_params = (item_id, customer_id, rent_date, date_due, today)
    cur.execute(create_new, final_params)
    clear_entry = "DELETE FROM rental WHERE item_id = ? AND customer_id = ?"
    cur.execute(clear_entry, init_search_params)
    

def grant_extension(item_id: str = None, customer_id: str = None):
    """
    Adds 14 days to the due_date.
    """
    raise NotImplementedError("you must implement this function")


def get_filtered_items(filter_attributes: Item = None,
                       use_patterns: bool = False,
                       min_price: float = -1,
                       max_price: float = -1,
                       min_start_year: int = -1,
                       max_start_year: int = -1) -> list[Item]:
    """
    Returns a list of Item objects matching the filters.
    """
    raise NotImplementedError("you must implement this function")


def get_filtered_customers(filter_attributes: Customer = None, use_patterns: bool = False) -> list[Customer]:
    """
    Returns a list of Customer objects matching the filters.
    """
    raise NotImplementedError("you must implement this function")


def get_filtered_rentals(filter_attributes: Rental = None,
                         min_rental_date: str = None,
                         max_rental_date: str = None,
                         min_due_date: str = None,
                         max_due_date: str = None) -> list[Rental]:
    """
    Returns a list of Rental objects matching the filters.
    """
    raise NotImplementedError("you must implement this function")


def get_filtered_rental_histories(filter_attributes: RentalHistory = None,
                                  min_rental_date: str = None,
                                  max_rental_date: str = None,
                                  min_due_date: str = None,
                                  max_due_date: str = None,
                                  min_return_date: str = None,
                                  max_return_date: str = None) -> list[RentalHistory]:
    """
    Returns a list of RentalHistory objects matching the filters.
    """
    raise NotImplementedError("you must implement this function")


def get_filtered_waitlist(filter_attributes: Waitlist = None,
                          min_place_in_line: int = -1,
                          max_place_in_line: int = -1) -> list[Waitlist]:
    """
    Returns a list of Waitlist objects matching the filters.
    """
    raise NotImplementedError("you must implement this function")


def number_in_stock(item_id: str = None) -> int:
    """
    Returns num_owned - active rentals. Returns -1 if item doesn't exist.
    """
    raise NotImplementedError("you must implement this function")


def place_in_line(item_id: str = None, customer_id: str = None) -> int:
    """
    Returns the customer's place_in_line, or -1 if not on waitlist.
    """
    raise NotImplementedError("you must implement this function")


def line_length(item_id: str = None) -> int:
    """
    Returns how many people are on the waitlist for this item.
    """
    raise NotImplementedError("you must implement this function")


def save_changes():
    """
    Commits all changes made to the db.
    """
    raise NotImplementedError("you must implement this function")


def close_connection():
    """
    Closes the cursor and connection.
    """
    raise NotImplementedError("you must implement this function")
