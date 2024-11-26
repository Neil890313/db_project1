# vet.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from api.sql import Veterinarian as VetModel

vet = Blueprint('vet', __name__, template_folder='../templates')

@vet.route("/view_appointment", methods=["GET", "POST"])
@login_required
def view_appointment():
    current_user_name = current_user.name
    mid = current_user.id
    vid_data = VetModel.get_veterinarian(mid)
    if vid_data:
        vid = vid_data[0]
        appointments = VetModel.view_appointment(vid)
        return render_template("view_appointment.html", appointments=appointments, user=current_user_name)
    else:
        flash("不存在的獸醫ID。")
        return redirect(url_for("api.login"))

@vet.route("/write_medical_record/<int:aId>", methods=["GET", "POST"])
@login_required
def write_medical_record(aId):
    mid = current_user.id
    vid_result = VetModel.get_veterinarian(mid)
    if vid_result:
        vId = vid_result[0]
    else:
        flash("未找到您的獸醫資料")
        return redirect(url_for("api.login"))

    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        treatment = request.form.get('treatment')
        pId = request.form.get('pId')

        # 创建输入数据字典
        input_data = {
            'diagnosis': diagnosis,
            'treatment': treatment,
            'pId': pId,
            'vId': vId
        }

        # 调用 create_MR 方法
        VetModel.create_MR(input_data)

        # 重定向回预约列表
        return redirect(url_for('vet.view_appointment'))
    else:
        # 處理 GET 請求，獲取 pId 並渲染模板
        pId_result = VetModel.get_current_appointment_pid(aId)
        if pId_result:
            pId = pId_result[0]
        else:
            flash("未找到該預約的寵物ID")
            return redirect(url_for('vet.view_appointment'))

        return render_template('write_medical_record.html', vId=vId, pId=pId, aId=aId)