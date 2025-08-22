from app import app, db
from models import User

with app.app_context():
    username = input("ادخل اسم المستخدم للأدمن: ")
    password = input("ادخل كلمة المرور: ")

    if User.query.filter_by(username=username).first():
        print("❌ المستخدم موجود بالفعل.")
    else:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print("✅ تم إنشاء الأدمن بنجاح.")