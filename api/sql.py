from typing import Optional
import psycopg2
from psycopg2 import pool
from datetime import datetime


class DB:
    connection_pool = pool.SimpleConnectionPool(
        1, 100,  # 最小和最大連線數
        user='project_20',
        password='ixapmn',
        host='140.117.68.66',
        port='5432',
        dbname='project_20'
    )

    @staticmethod
    def connect():
        return DB.connection_pool.getconn()

    @staticmethod
    def release(connection):
        DB.connection_pool.putconn(connection)

    @staticmethod
    def execute_input(sql, input):
        if not isinstance(input, (tuple, list)):
            raise TypeError(
                f"Input should be a tuple or list, got: {type(input).__name__}")
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                connection.commit()
        except psycopg2.Error as e:
            print(f"Error executing SQL: {e}")
            connection.rollback()
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def execute(sql):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
        except psycopg2.Error as e:
            print(f"Error executing SQL: {e}")
            connection.rollback()
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def fetchall(sql, input=None):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
            raise []
        finally:
            DB.release(connection)

    @staticmethod
    def fetchone(sql, input=None):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                return cursor.fetchone()
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
            raise e
        finally:
            DB.release(connection)


class Member:
    @staticmethod
    def get_member(account):
        sql = 'SELECT account, password, mid, identity, name FROM "Member" WHERE account = %s'
        return DB.fetchall(sql, (account,))

    @staticmethod
    def get_all_username():
        sql = 'SELECT name FROM "Member"'
        return DB.fetchall(sql)

    @staticmethod
    def get_mid(account):
        sql = 'SELECT mid FROM "Member" WHERE account = %s;'
        result = DB.fetchone(sql, (account,))

        if result:
            return result[0]  # 返回 mId
        else:
            raise ValueError(f"No mId found for account: {account}")

    @staticmethod
    def get_all_account():
        sql = 'SELECT account FROM "Member"'
        return DB.fetchall(sql)

    @staticmethod
    def create_member(input_data):
        sql = 'INSERT INTO "Member" (name, account, password, identity) VALUES (%s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['name'], input_data['account'],
                         input_data['password'], input_data['identity']))

    @staticmethod
    def delete_product(tno, pid):
        sql = 'DELETE FROM record WHERE tno = %s and pid = %s'
        DB.execute_input(sql, (tno, pid))

    @staticmethod
    def get_order(userid):
        sql = 'SELECT * FROM order_list WHERE mid = %s ORDER BY ordertime DESC'
        return DB.fetchall(sql, (userid,))

    @staticmethod
    def get_role(userid):
        sql = 'SELECT identity, name FROM "Member" WHERE mid = %s'
        return DB.fetchone(sql, (userid,))


class Veterinarian:
    @staticmethod
    def create_Veterinarian(input_data):
        sql = 'INSERT INTO "Veterinarian" (name, specialization, phone_number, clinic_hours, mid) VALUES (%s, %s, %s, %s,%s)'
        DB.execute_input(sql, (input_data['name'], input_data['specialization'],
                         input_data['phone_number'], input_data['clinic_hours'], input_data['mid']))
    
    @staticmethod
    def get_veterinarian(mid):
        print(f"目前在 sql 查詢中收到的 mid: {mid}")
        sql = 'SELECT "vId" FROM "Veterinarian" WHERE mid = %s'
        return DB.fetchone(sql, (mid,))     
    
    @staticmethod
    def view_appointment(vId):
        print(f"目前在 sql 查詢中收到的 vId: {vId}")
        today = datetime.today().date()
        sql = 'SELECT * FROM "Appointment" WHERE "vId" = %s AND date = %s AND status = %s'
        return DB.fetchall(sql, (vId, today, 'success'))
    
    @staticmethod
    def get_current_appointment_pid(aId):
        sql = 'SELECT "pId" FROM "Appointment" WHERE "aId" = %s'
        return DB.fetchone(sql, (aId,))

    @staticmethod
    def create_MR(input_data):
        today = datetime.today().date()
        sql = 'INSERT INTO "Medical_Record" (diagnosis, treatment, "vId", "pId") VALUES (%s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['diagnosis'], input_data['treatment'], input_data['pId'], input_data['vId']))

        # Update the status of the appointment
        sql = 'UPDATE "Appointment" SET status = %s WHERE "pId" = %s AND date = %s AND "vId" = %s'
        DB.execute_input(sql, ('end', input_data['pId'], today, input_data['vId']))


class Pet:
    @staticmethod
    def create_Pet(input_data):
        sql = 'INSERT INTO "Pet" (name, species, breed, age, gender, mid) VALUES (%s, %s, %s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['pet_name'], input_data['pet_species'], input_data['pet_breed'],
                         input_data['pet_age'], input_data['pet_gender'], input_data['mid']))


class Owner:
    @staticmethod
    def create_Owner(input_data):
        sql = 'INSERT INTO "Owner" (name, phone_number, address, mid) VALUES (%s, %s, %s, %s)'
        DB.execute_input(
            sql, (input_data['name'], input_data['phone_number'], input_data['address'], input_data['mid']))


class Appointment:
    @staticmethod
    def update_status(aId, new_status):
        sql = 'UPDATE "Appointment" SET status = %s WHERE "aId" = %s'
        DB.execute_input(sql, (new_status, aId))

    @staticmethod
    def get_appointments():
        sql = 'SELECT "aId", date FROM "Appointment" WHERE status = %s'
        return DB.fetchall(sql)

    @staticmethod
    def insert_appointment(input_data):
        sql = 'INSERT INTO "Appointment" (aId, date, status) VALUES (%s, %s, %s)'
        DB.execute_input(
            sql, (input_data['aId'], input_data['date'], input_data['status']))

    # 新增：自動更新 Appointment 狀態的方法
    @staticmethod
    def refresh_status():
        sql = 'SELECT "aId", date FROM "Appointment"'
        appointments = DB.fetchall(sql)  # 獲取所有掛號資料
        current_date = datetime.now().date()  # 當前日期

        for appointment in appointments:
            aId, appointment_date = appointment
            if current_date > appointment_date:
                Appointment.update_status("aId", "END")
            else:
                Appointment.update_status("aId", "已完成掛號")


class Cart:
    @staticmethod
    def check(user_id):
        sql = '''SELECT * FROM cart, record 
                 WHERE cart.mid = %s::bigint 
                 AND cart.tno = record.tno::bigint'''
        return DB.fetchone(sql, (user_id,))

    @staticmethod
    def get_cart(user_id):
        sql = 'SELECT * FROM cart WHERE mid = %s'
        return DB.fetchone(sql, (user_id,))

    @staticmethod
    def add_cart(user_id, time):
        sql = 'INSERT INTO cart (mid, carttime, tno) VALUES (%s, %s, nextval(\'cart_tno_seq\'))'
        DB.execute_input(sql, (user_id, time))

    @staticmethod
    def clear_cart(user_id):
        sql = 'DELETE FROM cart WHERE mid = %s'
        DB.execute_input(sql, (user_id,))


class Product:
    @staticmethod
    def count():
        sql = 'SELECT COUNT(*) FROM product'
        return DB.fetchone(sql)

    @staticmethod
    def get_product(pid):
        sql = 'SELECT * FROM product WHERE pid = %s'
        return DB.fetchone(sql, (pid,))

    @staticmethod
    def get_all_product():
        sql = 'SELECT * FROM product'
        return DB.fetchall(sql)

    @staticmethod
    def get_name(pid):
        sql = 'SELECT pname FROM product WHERE pid = %s'
        return DB.fetchone(sql, (pid,))[0]

    @staticmethod
    def add_product(input_data):
        sql = 'INSERT INTO product (pid, pname, price, category, pdesc) VALUES (%s, %s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['pid'], input_data['pname'],
                         input_data['price'], input_data['category'], input_data['pdesc']))

    @staticmethod
    def delete_product(pid):
        sql = 'DELETE FROM product WHERE pid = %s'
        DB.execute_input(sql, (pid,))

    @staticmethod
    def update_product(input_data):
        sql = 'UPDATE product SET pname = %s, price = %s, category = %s, pdesc = %s WHERE pid = %s'
        DB.execute_input(sql, (input_data['pname'], input_data['price'],
                         input_data['category'], input_data['pdesc'], input_data['pid']))


class Record:
    @staticmethod
    def get_total_money(tno):
        sql = 'SELECT SUM(total) FROM record WHERE tno = %s'
        return DB.fetchone(sql, (tno,))[0]

    @staticmethod
    def check_product(pid, tno):
        sql = 'SELECT * FROM record WHERE pid = %s and tno = %s'
        return DB.fetchone(sql, (pid, tno))

    @staticmethod
    def get_price(pid):
        sql = 'SELECT price FROM product WHERE pid = %s'
        return DB.fetchone(sql, (pid,))[0]

    @staticmethod
    def add_product(input_data):
        sql = 'INSERT INTO record (pid, tno, amount, saleprice, total) VALUES (%s, %s, 1, %s, %s)'
        DB.execute_input(
            sql, (input_data['pid'], input_data['tno'], input_data['saleprice'], input_data['total']))

    @staticmethod
    def get_record(tno):
        sql = 'SELECT * FROM record WHERE tno = %s'
        return DB.fetchall(sql, (tno,))

    @staticmethod
    def get_amount(tno, pid):
        sql = 'SELECT amount FROM record WHERE tno = %s and pid = %s'
        return DB.fetchone(sql, (tno, pid))[0]

    @staticmethod
    def update_product(input_data):
        sql = 'UPDATE record SET amount = %s, total = %s WHERE pid = %s and tno = %s'
        DB.execute_input(
            sql, (input_data['amount'], input_data['total'], input_data['pid'], input_data['tno']))

    @staticmethod
    def delete_check(pid):
        sql = 'SELECT * FROM record WHERE pid = %s'
        return DB.fetchone(sql, (pid,))

    @staticmethod
    def get_total(tno):
        sql = 'SELECT SUM(total) FROM record WHERE tno = %s'
        return DB.fetchone(sql, (tno,))[0]


class Order_List:
    @staticmethod
    def add_order(input_data):
        sql = 'INSERT INTO order_list (oid, mid, ordertime, price, tno) VALUES (DEFAULT, %s, TO_TIMESTAMP(%s, %s), %s, %s)'
        DB.execute_input(sql, (input_data['mid'], input_data['ordertime'],
                         input_data['format'], input_data['total'], input_data['tno']))

    @staticmethod
    def get_order():
        sql = '''
            SELECT o.oid, m.name, o.price, o.ordertime
            FROM order_list o
            NATURAL JOIN member m
            ORDER BY o.ordertime DESC
        '''
        return DB.fetchall(sql)

    @staticmethod
    def get_orderdetail():
        sql = '''
        SELECT o.oid, p.pname, r.saleprice, r.amount
        FROM order_list o
        JOIN record r ON o.tno = r.tno -- 確保兩者都是 bigint 類型
        JOIN product p ON r.pid = p.pid
        '''
        return DB.fetchall(sql)


class Analysis:
    @staticmethod
    def month_price(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), SUM(price) FROM order_list WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def month_count(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), COUNT(oid) FROM order_list WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def category_sale():
        sql = 'SELECT SUM(total), category FROM product, record WHERE product.pid = record.pid GROUP BY category'
        return DB.fetchall(sql)

    @staticmethod
    def member_sale():
        sql = 'SELECT SUM(price), member.mid, member.name FROM order_list, member WHERE order_list.mid = member.mid AND member.identity = %s GROUP BY member.mid, member.name ORDER BY SUM(price) DESC'
        return DB.fetchall(sql, ('user',))

    @staticmethod
    def member_sale_count():
        sql = 'SELECT COUNT(*), member.mid, member.name FROM order_list, member WHERE order_list.mid = member.mid AND member.identity = %s GROUP BY member.mid, member.name ORDER BY COUNT(*) DESC'
        return DB.fetchall(sql, ('user',))
