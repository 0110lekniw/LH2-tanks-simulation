import datetime
import os


def file_date(filename):
    with open(filename, 'w') as file1:
        pass

    path = os.path.abspath(filename)

    date_created = datetime.date.today()

    str_DT = date_created.strftime('%Y-%m-%d')

    return str_DT