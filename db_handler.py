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
    if new_item is None :
        return 
    item_id = new_item.item_id
    product_name = new_item.product_name    
    brand = new_item.brand
    category = new_item.category
    manufact = new_item.manufact
    current_price = new_item.current_price
    start_year = new_item.start_year if new_item.start_year is not None else 2026
    num_owned = new_item.num_owned
    max_finder = "SELECT MAX(i_item_sk) FROM item"
    cur.execute(max_finder)
    item_sk = cur.fetchone()
    if item_sk[0] is None:
        item_sk1=0
    else:
        item_sk1 = item_sk[0]+1
    parameters = (item_sk1, item_id,  f"{start_year}-01-01",product_name, brand, "", category, manufact, current_price, num_owned)
    sql_insert = "INSERT INTO item (i_item_sk, i_item_id, i_rec_start_date, i_product_name, i_brand, i_class, i_category, i_manufact, i_current_price, i_num_owned) VALUES (?,?,?,?,?,?,?,?,?,?)"
    cur.execute(sql_insert, parameters)




def add_customer(new_customer: Customer = None):
    """
    new_customer - A Customer object containing a new customer to be inserted into the DB in the customer table.
        new_customer and its attributes will never be None.
    """
    if new_customer is None:
        return
    
    street_number_street_name, city, state_zip = new_customer.address.split(',', 2)
    street_number, street_name = street_number_street_name.split(' ', 1)
    state, zip_c = state_zip.split(' ', 1)
    max_finder_cu = "SELECT MAX(ca_address_sk) FROM customer_address"
    cur.execute(max_finder_cu)
    address_sk = cur.fetchone()
    if address_sk[0] is None:
        address_sk1=0
    else:
        address_sk1 = address_sk[0]+1
    add_parameters = (address_sk1, street_number.strip(), street_name.strip(), city.strip(), state.strip(), zip_c.strip())
    address_maker = "INSERT INTO customer_address (ca_address_sk, ca_street_number, ca_street_name, ca_city, ca_state,  ca_zip) VALUES (?,?,?,?,?,?)"
    cur.execute(address_maker, add_parameters)

    max_finder_cu = "SELECT MAX(c_customer_sk) FROM customer"
    cur.execute(max_finder_cu)
    customer_sk = cur.fetchone()
    if customer_sk[0] is None:
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
    if original_customer_id is None or new_customer is None:
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
    if item_id is None or customer_id is None:
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
    if item_id is None or customer_id is None:
        return -1
    sql_init = "SELECT COUNT(*) FROM waitlist WHERE item_id = ?"
    param = (item_id,)
    cur.execute(sql_init, param)
    final_position = (cur.fetchone()[0] or 0) +1
    sql_add = "INSERT INTO waitlist (item_id, customer_id, place_in_line) VALUES (?,?,?)"
    params = (item_id, customer_id, final_position)
    cur.execute(sql_add, params)
    return final_position

def update_waitlist(item_id: str = None):
    """
    Removes person at position 1 and shifts everyone else down by 1.
    """
    if item_id is None:
        return
    
    #Delete first item in waitlist
    sql_first = "DELETE FROM waitlist WHERE item_id = ? AND place_in_line = 1"
    param = (item_id,)
    cur.execute(sql_first,param)

    #Update the rest of the waitlist
    sql_update= "UPDATE waitlist SET place_in_line = place_in_line -1 WHERE item_id = ?"
    cur.execute(sql_update, param)

def return_item(item_id: str = None, customer_id: str = None):
    """
    Moves a rental from rental to rental_history with return_date = today.
    """
    if item_id is None or customer_id is None:
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
    if item_id is None or customer_id is None:
        return
    sql_finder = "SELECT due_date FROM rental WHERE item_id = ? AND customer_id = ?"
    params = (item_id, customer_id)
    cur.execute(sql_finder, params)
    dues_collected = cur.fetchone()
    if dues_collected is None:
        print("ERROR rental does not exist")
        return
    d_date = dues_collected[0]
    due_date_final = str(d_date + timedelta(days=14))
    parameters = (due_date_final, item_id, customer_id)
    sql_final = "UPDATE rental SET due_date = ? WHERE item_id = ? AND customer_id = ?"
    cur.execute(sql_final, parameters)

def get_filtered_items(filter_attributes: Item,
                       use_patterns: bool = False,
                       min_price: float = -1, max_price: float = -1,
                       min_start_year: int = -1, max_start_year: int = -1
                       ) -> list[Item]: 
    query = """SELECT * FROM item WHERE 1=1"""
    params = []
    if filter_attributes and filter_attributes.item_id:
        query += " AND i_item_id = ?"
        params.append(filter_attributes.item_id)

    if filter_attributes and filter_attributes.product_name:
            if use_patterns:
                query += " AND i_product_name LIKE ?"
            else:
                query += " AND i_product_name  = ?"
            params.append(filter_attributes.product_name)
    if min_price != -1:
        query += " AND i_current_price >= ?"
        params.append(min_price)
    if max_price != -1:
        query += " AND i_current_price <= ?"
        params.append(max_price)

    if min_start_year != -1:
        query += " AND YEAR(i_rec_start_date) >= ?"
        params.append(min_start_year)

    if max_start_year != -1:
        query += " AND YEAR(i_rec_start_date) <= ?"
        params.append(max_start_year)

    cur.execute(query,params)
    rows = cur.fetchall()

    items = []

    for row in rows:
        valid_year = row[2].year if row[2] is not None else 0
        items.append(Item(row[1].strip(),
        row[3].strip(),
        row[4].strip(),
        row[6].strip(), 
        row[7].strip(), 
        float(row[8]), 
        int(valid_year), 
        int(row[9])
    ))

    return items


def get_filtered_customers(filter_attributes: Customer = None, use_patterns: bool = False) -> list[Customer]:
    query = """
    SELECT c.c_customer_id, 
    c.c_first_name, 
    c.c_last_name,
    c.c_email_address,
    a.ca_street_number,
    a.ca_street_name, 
    a.ca_city,
    a.ca_state, 
    a.ca_zip
    FROM customer c
    JOIN customer_address a
    ON c.c_current_addr_sk = a.ca_address_sk
    WHERE 1=1
    """
    params = []

    if filter_attributes and filter_attributes.customer_id:
        query += " AND c.c_customer_id = ?"
        params.append(filter_attributes.customer_id)

    if filter_attributes and filter_attributes.name:
        if use_patterns:
            query += " AND CONCAT(c.c_first_name, ' ', c.c_last_name) LIKE ?"
        else:
            query += " AND CONCAT(c.c_first_name, ' ', c.c_last_name) = ?"
        params.append(filter_attributes.name)

    if filter_attributes and filter_attributes.email:
        if use_patterns:
            query += " AND c.c_email_address LIKE ?"
        else:
            query += " AND c.c_email_address = ?"
        params.append(filter_attributes.email)

    cur.execute(query, params)
    rows = cur.fetchall()

    customers = []
    for row in rows:
        full_name = row[1].strip() + " " + row[2].strip()
        address = f"{row[4].strip()} {row[5].strip()}, {row[6].strip()}, {row[7].strip()}, {row[8].strip()}"
        customers.append(Customer(row[0].strip(), full_name, address,row[3].strip()
        ))
    return customers
    #raise NotImplementedError("you must implement this function")


def get_filtered_rentals(filter_attributes: Rental = None,
                         min_rental_date: str = None,
                         max_rental_date: str = None,
                         min_due_date: str = None,
                         max_due_date: str = None) -> list[Rental]:
    
    query = """SELECT * FROM rental WHERE 1=1"""
    params = []

    if filter_attributes and filter_attributes.item_id:
        query += " AND item_id = ?"
        params.append(filter_attributes.item_id)

    if filter_attributes and filter_attributes.customer_id:
        query += " AND customer_id = ?"
        params.append(filter_attributes.customer_id)

    if min_rental_date:
        query += " AND rental_date >= ?"
        params.append(min_rental_date)
    if max_rental_date:
        query += " AND rental_date <= ?"
        params.append(max_rental_date)

    if min_due_date:
        query += " AND due_date >= ?"
        params.append(min_due_date)

    if max_due_date:
        query += " AND due_date <= ?"
        params.append(max_due_date)

    cur.execute(query, params)
    rows = cur.fetchall()
    rentals = []

    for row in rows:
        rentals.append(Rental(row[0].strip(),
        row[1].strip(), 
        str(row[2]),
        str(row[3])
        ))
    return rentals
  #  raise NotImplementedError("you must implement this function")

def get_filtered_rental_histories(filter_attributes: RentalHistory = None,
                                  min_rental_date: str = None,
                                  max_rental_date: str = None,
                                  min_due_date: str = None,
                                  max_due_date: str = None,
                                  min_return_date: str = None,
                                  max_return_date: str = None) -> list[RentalHistory]:
    query =  """
    SELECT * FROM rental_history WHERE 1=1
    """

    params = []

    if filter_attributes and filter_attributes.item_id:
        query += " AND item_id = ?"
        params.append(filter_attributes.item_id)

    if filter_attributes and filter_attributes.customer_id:
        query += " AND customer_id = ?"
        params.append(filter_attributes.customer_id)

    if min_rental_date:
        query += " AND rental_date >= ?"
        params.append(min_rental_date)

    if max_rental_date:
        query += " AND rental_date =< ?"
        params.append(max_rental_date)

    
    if min_due_date:
        query += " AND due_date >= ?"
        params.append(min_due_date)

    if max_due_date:
        query += " AND due_date =< ?"
        params.append(max_due_date)

    if min_return_date:
        query += " AND return_date =< ?"
        params.append(min_return_date)
    
    if max_return_date:
        query += " AND return_date >= ?"
        params.append(max_return_date)

    #execute the query

    cur.execute(query, params)
    rows = cur.fetchall()

    rental_histories = []
    for row in rows:
        rental_histories.eappend(RentalHistory(row[0].strip(),
        row[1].strip(),
        str(row[2]),
        str(row[3]),
        str(row[4])
        ))
    return rental_histories
    # raise NotImplementedError("you must implement this function")

def get_filtered_waitlist(filter_attributes: Waitlist = None,
                          min_place_in_line: int = -1,
                          max_place_in_line: int = -1) -> list[Waitlist]:

    query = """SELECT * FROM waitlist WHERE 1=1"""
    params = []
    if filter_attributes and filter_attributes.item_id:
        query += " AND item_id = ?"
        params.append(filter_attributes.item_id)

    if filter_attributes and filter_attributes.customer_id:
        query += " AND customer_id = ?"
        params.append(filter_attributes.customer_id)

    if min_place_in_line != -1:
        query += " AND place_in_line >= ?"
        params.append(min_place_in_line)

    if max_place_in_line != -1:
        query += " AND place_in_line <= ?"
        params.append(max_place_in_line)

    cur.execute(query, params)
    rows = cur.fetchall()

    waitlist_entries = []
    for row in rows:
        waitlist_entries.append(Waitlist(
            row[0].strip(),
            row[1].strip(),
            row[2]
        ))
    return waitlist_entries
    #raise NotImplementedError("you must implement this function")


def number_in_stock(item_id: str = None) -> int:
    """
    Returns num_owned - active rentals. Returns -1 if item doesn't exist.
    """
    if item_id is None:
        return -1
    sql_count_stock = "SELECT i_num_owned FROM item WHERE i_item_id = ?"
    sql_count_rentals = "SELECT COUNT(*) FROM rental WHERE item_id = ?"
    param = (item_id,)
    #count the number in potential stock
    cur.execute(sql_count_stock, param)
    stock_count = cur.fetchone()
    if  stock_count is None or stock_count[0] == 0:
        return -1
    in_stock = stock_count[0]
    #count those in rentals
    cur.execute(sql_count_rentals, param)
    rental_count = cur.fetchone()
    if  rental_count[0] is None:
        return -1
    num_rented = rental_count[0]
    if in_stock - num_rented <0:
        return -1
    return in_stock - num_rented

def place_in_line(item_id: str = None, customer_id: str = None) -> int:
    query = "SELECT place_in_line FROM waitlist WHERE item_id = ? AND customer_id = ?"
    cur.execute(query, (item_id, customer_id))
    row = cur.fetchone()
    if row:
        return row[0]
    else:
        return -1


def line_length(item_id: str = None) -> int:
    query = "SELECT COUNT(*) FROM waitlist WHERE item_id = ?"
    cur.execute(query, (item_id,))
    row = cur.fetchone()
    return row[0]


def save_changes():
    conn.commit()
    #raise NotImplementedError("you must implement this function")


def close_connection():
    cur.close()
    conn.close()
    #raise NotImplementedError("you must implement this function")
