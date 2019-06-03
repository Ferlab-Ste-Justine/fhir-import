from contextlib import contextmanager

import psycopg2


@contextmanager
def db_transaction(connection):
    cursor = connection.cursor()
    try:
        yield cursor
    except:
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def get_connection(args):
    return psycopg2.connect(user=args.user,
                            password=args.password,
                            host=args.host,
                            port=args.port,
                            database=args.schema)
