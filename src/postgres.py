import psycopg2


# todo make these into a class
def start_connection(user="jtangqt", password=""):
    try:
        connection = psycopg2.connect(user=user,
                                      password=password,
                                      host="127.0.0.1",
                                      port="5432",
                                      database="postgres")

        # Print PostgreSQL Connection properties
        print ("Info: ", connection.get_dsn_parameters())

        # Print PostgreSQL version
        return connection, None
    except (Exception, psycopg2.Error) as error:
        print ("Error: could not connect to PostgreSQL", error)
        return None, error


def close_connection(connection):
    cursor = connection.cursor()
    cursor.close()
    connection.close()
    print("Info: PostgreSQL connection is closed")


def with_postgres_connection(func):
    """Wrap function to setup and tear down a Postgres connection while
    providing a cursor object to make queries with.
    """
    def wrapper(*args, **kwargs):
        connection, err = start_connection()
        if err is not None:
            return err
        try:
            cursor = connection.cursor()
            ret = func(cursor, *args, **kwargs)
            connection.commit()
            count = cursor.rowcount
            print ("Info: {} record successfully {}".format(count, args[-1]))
        except (Exception, psycopg2.Error) as error:
            return error
        finally:
            close_connection(connection)
        return ret
    return wrapper
