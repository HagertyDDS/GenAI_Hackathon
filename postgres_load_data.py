import psycopg2
import pandas as pd

# Global connection object to allow us to operate on local table
try:
    CONN = psycopg2.connect("dbname='template1' user='postgres' host='localhost' password='postgres123'")
    CONN.set_session(autocommit=True)
except:
    print("I am unable to connect to the database")

GET_COMMENTS_QUERY = """
select
    c.table_name,
    c.column_name,
    pgd.description
from pg_catalog.pg_statio_all_tables as st
inner join pg_catalog.pg_description pgd on (
    pgd.objoid = st.relid
)
inner join information_schema.columns c on (
    pgd.objsubid   = c.ordinal_position and
    c.table_schema = st.schemaname and
    c.table_name   = st.relname
);
"""

def get_all_table_comments():
    """
    
    """
    # we use a context manager to scope the cursor session
    with CONN.cursor() as curs:

        try:
            # Get all column comments for all tables in the database
            curs.execute(GET_COMMENTS_QUERY)
            rows = curs.fetchall()
            return rows

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        
def load_car_sale_regression_data_from_csv(csv_file_path):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path, header=None, names=[
            'id', 'brand', 'model', 'model_year', 'mileage', 'fuel_type',
            'engine', 'transmission', 'ext_col', 'int_col', 'accident',
            'clean_title', 'price'
        ])

        # Process the data
        df['model_year'] = pd.to_numeric(df['model_year'], errors='coerce').astype('Int64')
        df['mileage'] = pd.to_numeric(df['mileage'], errors='coerce').astype('Int64')
        df['clean_title'] = df['clean_title'].map({'Yes': True, 'No': False})
        df['price'] = pd.to_numeric(df['price'].str.replace(r'[^\d.]', '', regex=True), errors='coerce').astype('Int64')

        # Trying to keep pre-processing minimal. Just going to drop rows without a target var value
        df.dropna(subset=["price"], inplace=True)

        # Convert DataFrame to list of dictionaries
        car_data = df.to_dict('records')

        # Insert data into the databaseß
        with CONN.cursor() as curs:
            for row in car_data[1:]:

                curs.execute(
                    "INSERT INTO car_sale_regression (id, brand, model, model_year, mileage, fuel_type, engine, "
                    "transmission, ext_col, int_col, accident, clean_title, price) "
                    f"VALUES ({row['id']}, \'{row['brand']}\', \'{row['model']}\', {row['model_year']}, {row['mileage']}, \'{row['fuel_type']}\', \'{row['engine']}\', "
                    f"\'{row['transmission']}\', \'{row['ext_col']}\', \'{row['int_col']}\', \'{row['accident']}\', \'{row['clean_title']}\', {row['price']})",
                    car_data
                )

            print(f"Successfully inserted {len(car_data)} records into the cars table.")

    except Exception as e:
        print(f"An error occurred: {e}")

def get_car_sales_regression_data_from_postgres():
    return pd.read_sql("SELECT * FROM car_sale_regression", CONN)


if __name__ == "__main__":
    # Load the dataset. You only need to do this once
    # load_car_sale_regression_data_from_csv("/Users/csweet/Downloads/playground-series-s4e9/train.csv")

    # Query the comments for the entire db
    # TODO: Write more targeted function to get only columns we need for context
    from pprint import pprint
    pprint(get_all_table_comments())

    # Query data from dataset into pandas dataframe
    df = get_car_sales_regression_data_from_postgres()
    print(df.shape)
