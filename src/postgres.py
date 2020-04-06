import psycopg2

# todo make these into a class
def start_connection(user="jtangqt", password=""):
    try:
        connection = psycopg2.connect(user = user,
                                      password = password,
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")

        # Print PostgreSQL Connection properties
        print ( "Info: ", connection.get_dsn_parameters())

        # Print PostgreSQL version
        return connection, None
    except (Exception, psycopg2.Error) as error:
        print ("Error: could not connect to PostgreSQL", error)
        return None,  error

def close_connection(connection):
    cursor = connection.cursor()
    cursor.close()
    connection.close()
    print("Info: PostgreSQL connection is closed")