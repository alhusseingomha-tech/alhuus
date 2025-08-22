from flask import request
from datetime import datetime

def get_client_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        ip = request.environ['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.remote_addr
    return ip

def log_visitor(db, Visitor, lang):
    ip = get_client_ip()
    visit = Visitor(ip=ip, visit_time=datetime.utcnow(), duration=0, lang=lang)
    db.session.add(visit)
    db.session.commit()