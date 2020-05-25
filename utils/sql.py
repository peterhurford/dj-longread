def table_exists(cur, table_name):
    cur.execute('SELECT * FROM information_schema.tables WHERE table_name=%s', (table_name,))
    return cur.rowcount >= 1


def drop_table(cur, table_name):
    cur.execute('DROP TABLE {}'.format(table_name))
    return None


def escape(text):
    return text.replace('\'', '\'\'')

def enquote(text):
     return '\'' + escape(str(text)) + '\''


def add_row(cur, table_name, column_names, row):
     cur.execute('INSERT INTO {} {} VALUES {}'.format(table_name,
                                                      '(' + ', '.join(column_names) + ')',
                                                      '(' + ', '.join(row) + ')'))
     return None


def delete_row(cur, table_name, column_name, value):
    cur.execute('DELETE FROM {} WHERE {} = {}'.format(table_name, column_name, value))
    return None


def find_row(cur, table_name, col, value, n=1):
    cur.execute('SELECT * FROM {} WHERE {} = {}'.format(table_name, col, enquote(value)))
    if n == 1:
        return cur.fetchone()
    elif n == 'many':
        return cur.fetchall()
    else:
        return ValueError('n must be 1 or many')

