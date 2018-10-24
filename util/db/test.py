from util.db import mysql


def execute():
    mysql.execute("INSERT INTO EMPLOYEE(FIRST_NAME, LAST_NAME, AGE, SEX, INCOME) \
           VALUES ('%s', '%s', '%d', '%c', '%d' )", ('Mac', 'Mohan', 20, 'M', 2000))


def fetchall():
    results = mysql.fetchall("SELECT * FROM EMPLOYEE WHERE INCOME > '%d'" % 1000)
    for row in results:
        # fname = row[0]
        # lname = row[1]
        # age = row[2]
        # sex = row[3]
        # income = row[4]
        # 打印结果
        print(row)


if __name__ == '__main__':
    # execute()
    fetchall()
