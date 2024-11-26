import imp
from flask import render_template, Blueprint, redirect, request, url_for, flash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from link import *
from api.sql import *

from datetime import datetime  # 確保已導入 datetime
from flask import Blueprint, redirect, url_for

api = Blueprint("api", __name__, template_folder="./templates")

# 更新 Appointment 狀態函式


def update_appointment_status():
    current_date = datetime.now().date()  # 獲取當前日期
    appointments = Appointment.get_appointments()  # 獲取所有掛號資料

    for appointment in appointments:
        aid, appointment_date = appointment
        if current_date > appointment_date:
            Appointment.update_status(aid, "END")
        else:
            Appointment.update_status(aid, "已完成掛號")


login_manager = LoginManager(api)
login_manager.login_view = "api.login"
login_manager.login_message = "請先登入"


class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(userid):
    user = User()
    user.id = userid
    data = Member.get_role(userid)
    try:
        user.role = data[0]
        user.name = data[1]
    except:
        pass
    return user


@api.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        account = request.form["account"]
        password = request.form["password"]
        data = Member.get_member(account)

        try:
            DB_password = data[0][1]
            user_id = data[0][2]
            identity = data[0][3]
        except:
            flash("*沒有此帳號")
            return redirect(url_for("api.login"))

        if DB_password == password:
            user = User()
            user.id = user_id
            login_user(user)


            print(f"目前的 mid: {current_user.id}")
            # 根據身份更新 Appointment 狀態
            if identity == "user":
                # Appointment.refresh_status()  # 使用者
                return redirect(url_for("bookstore.bookstore"))
            elif identity == "manager":
                # Appointment.refresh_status()  # 管理員
                return redirect(url_for("vet.view_appointment"))

        else:
            flash("*密碼錯誤，請再試一次")
            return redirect(url_for("api.login"))

    return render_template("login.html")


@api.route('/check_account', methods=['POST'])
def check_account():
    if request.method == 'POST':
        user_account = request.form.get('account')

        # 確保從資料庫獲取現有帳號列表
        exist_account = Member.get_all_account()
        account_list = [i[0] for i in exist_account]  # 簡化提取帳號的邏輯

        # 檢查帳號是否已存在
        if user_account in account_list:
            return {"status": "error", "message": "帳號已存在，請使用其他帳號"}, 400

        return {"status": "success", "message": "帳號可用"}, 200


@api.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        user_name = request.form["username"]
        account = request.form["account"]
        password = request.form["password"]
        identity = request.form["identity"]
        real_name = request.form["real_name"]
        phone_number = request.form["phone_number"]
        address = request.form["address"]
        specialization = request.form["specialization"]
        clinic_hours = request.form["clinic_hours"]
        pet_name = request.form["pet_name"]
        pet_species = request.form["pet_species"]
        pet_breed = request.form["pet_breed"]
        pet_age = request.form["pet_age"]
        pet_gender = request.form["pet_gender"]

        exist_account = Member.get_all_account()
        account_list = []
        for i in exist_account:
            account_list.append(i[0])

        if account in account_list:

            return redirect(url_for("api.register"))
        else:
            input = {
                "name": user_name,
                "account": account,
                "password": password,
                "identity": identity,
            }
            Member.create_member(input)
            member_mid = Member.get_mid(account)
            if identity == "user":
                input = {
                    "name": real_name,
                    "phone_number": phone_number,
                    "address": address,
                    "mid": member_mid
                }
                input_pet = {
                    "pet_name": pet_name,
                    "pet_species": pet_species,
                    "pet_breed": pet_breed,
                    "pet_age": pet_age,
                    "pet_gender": pet_gender,
                    "mid": member_mid
                }
                Owner.create_Owner(input)
                Pet.create_Pet(input_pet)

            else:
                input = {
                    "name": real_name,
                    "phone_number": phone_number,
                    "specialization": specialization,
                    "clinic_hours": clinic_hours,
                    "mid": member_mid
                }
                Veterinarian.create_Veterinarian(input)

            return redirect(url_for("api.login"))

    return render_template("register.html")


@api.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@api.route("/veterinarian", methods=["POST", "GET"])
@login_required
def check_appointment():
    # Step 1: 取得目前登入的使用者的 vId
    mid = current_user.id
    vid_result = Veterinarian.get_veterinarian(mid)
    
    if vid_result:
        vid = vid_result[0]
    else:
        flash("未找到您的獸醫師資料")
        return redirect(url_for('api.login'))

    # Step 2: 使用 vId 獲取預約資料
    appointments = Veterinarian.view_appointment(vid)

    # Step 3: 渲染模板，將預約資料顯示在網頁上
    return render_template('veterinarian.html', appointments=appointments)
