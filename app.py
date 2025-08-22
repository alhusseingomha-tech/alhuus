from flask import Flask, render_template, redirect, url_for, request, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Project, Visitor, SocialLink, AboutMe, ProjectImage
from utils import log_visitor
from datetime import datetime
import os
from deep_translator import GoogleTranslator
from deep_translator import GoogleTranslator

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# اللغة الافتراضية
@app.before_request
def set_language():
    lang = session.get('lang', 'en')
    if 'lang' in request.args:
        lang = request.args['lang']
        session['lang'] = lang
    request.lang = lang

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    projects = Project.query.all()
    social_links = SocialLink.query.all()
    about_me = AboutMe.query.first()
    return render_template('index.html', projects=projects, lang=request.lang, social_links=social_links, about_me=about_me)

@app.route('/projects')
def projects():
    projects = Project.query.all()
    social_links = SocialLink.query.all()
    return render_template('projects.html', projects=projects, lang=request.lang, social_links=social_links)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """Display detailed information about a specific project"""
    project = Project.query.get_or_404(project_id)
    social_links = SocialLink.query.all()
    
    # Get project images
    project_images = ProjectImage.query.filter_by(project_id=project_id).order_by(ProjectImage.order).all()
    
    # Get next and previous projects for navigation
    all_projects = Project.query.order_by(Project.id).all()
    current_index = next((i for i, p in enumerate(all_projects) if p.id == project_id), 0)
    
    prev_project = all_projects[current_index - 1] if current_index > 0 else None
    next_project = all_projects[current_index + 1] if current_index < len(all_projects) - 1 else None
    
    return render_template('project_detail.html', 
                         project=project, 
                         project_images=project_images,
                         lang=request.lang, 
                         social_links=social_links,
                         prev_project=prev_project,
                         next_project=next_project)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Here you would typically send an email or save to database
        # For now, we'll just flash a success message
        flash('Thank you for your message! I will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html', lang=request.lang)

@app.route('/toggle_dark')
def toggle_dark():
    session['dark'] = not session.get('dark', False)
    return redirect(request.referrer or url_for('index'))

# لوحة التحكم
@app.route('/admin-2025-login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def dashboard():
    projects = Project.query.all()
    return render_template('admin/dashboard.html', projects=projects)

@app.route('/admin/project/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        try:
            # جلب البيانات من النموذج (العربية فقط)
            title_ar = request.form['title_ar']
            description_ar = request.form['description_ar']
            detailed_description_ar = request.form.get('detailed_description_ar', '')
            technologies = request.form.get('technologies', '')
            link = request.form.get('link', '')
            
            # الترجمة التلقائية للمحتوى الإنجليزي من العربي
            title_en = GoogleTranslator(source='ar', target='en').translate(title_ar)
            description_en = GoogleTranslator(source='ar', target='en').translate(description_ar)
            detailed_description_en = GoogleTranslator(source='ar', target='en').translate(detailed_description_ar)
            
            # إنشاء المشروع
            project = Project(
                title_ar=title_ar,
                title_en=title_en,
                description_ar=description_ar,
                description_en=description_en,
                detailed_description_ar=detailed_description_ar,
                detailed_description_en=detailed_description_en,
                technologies=technologies,
                link=link
            )
            
            db.session.add(project)
            db.session.flush()  # للحصول على ID المشروع
            
            # معالجة الصورة الرئيسية
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    filename = f"project_{project.id}_{file.filename}"
                    file.save(os.path.join('static/images', filename))
                    project.image = filename
            
            # معالجة الصور الإضافية
            if 'additional_images[]' in request.files:
                files = request.files.getlist('additional_images[]')
                for index, file in enumerate(files):
                    if file and file.filename:
                        filename = f"project_{project.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{index}_{file.filename}"
                        file.save(os.path.join('static/images', filename))
                        
                        project_image = ProjectImage(
                            project_id=project.id,
                            image_path=filename,
                            order=index
                        )
                        db.session.add(project_image)
            
            db.session.commit()
            flash('تم إضافة المشروع بنجاح', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إضافة المشروع: {str(e)}', 'error')
            return redirect(url_for('add_project'))
    
    return render_template('admin/edit_project.html', project=None)

@app.route('/admin/project/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
def edit_project(pid):
    project = Project.query.get_or_404(pid)
    
    if request.method == 'POST':
        try:
            # تحديث البيانات الأساسية (العربية فقط)
            project.title_ar = request.form['title_ar']
            project.description_ar = request.form['description_ar']
            project.detailed_description_ar = request.form.get('detailed_description_ar', '')
            project.technologies = request.form.get('technologies', '')
            project.link = request.form['link']
            
            # الترجمة التلقائية للمحتوى الإنجليزي من العربي
            project.title_en = GoogleTranslator(source='ar', target='en').translate(project.title_ar)
            project.description_en = GoogleTranslator(source='ar', target='en').translate(project.description_ar)
            project.detailed_description_en = GoogleTranslator(source='ar', target='en').translate(project.detailed_description_ar)
            
            # معالجة الصورة الرئيسية
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    filename = f"project_{project.id}_{file.filename}"
                    file.save(os.path.join('static/images', filename))
                    project.image = filename
            
            # معالجة الصور الإضافية
            if 'additional_images[]' in request.files:
                files = request.files.getlist('additional_images[]')
                for file in files:
                    if file and file.filename:
                        filename = f"project_{project.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
                        file.save(os.path.join('static/images', filename))
                        
                        # إنشاء سجل صورة جديد
                        project_image = ProjectImage(
                            project_id=project.id,
                            image_path=filename,
                            order=0
                        )
                        db.session.add(project_image)
            
            db.session.commit()
            flash('تم تحديث المشروع بنجاح', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تحديث المشروع: {str(e)}', 'error')
            return redirect(url_for('edit_project', pid=pid))
    
    # جلب الصور الحالية
    project_images = ProjectImage.query.filter_by(project_id=project.id).all()
    return render_template('admin/edit_project.html', project=project, project_images=project_images)

@app.route('/admin/project/delete/<int:pid>')
@login_required
def delete_project(pid):
    project = Project.query.get_or_404(pid)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/admin/analytics')
@login_required
def analytics():
    visitors = Visitor.query.order_by(Visitor.visit_time.desc()).all()
    return render_template('admin/analytics.html', visitors=visitors)

@app.route('/admin/social', methods=['GET', 'POST'])
@login_required
def manage_social():
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        icon = request.form['icon']
        link = SocialLink(name=name, url=url, icon=icon)
        db.session.add(link)
        db.session.commit()
        flash('تمت إضافة الرابط بنجاح')
        return redirect(url_for('manage_social'))
    links = SocialLink.query.all()
    return render_template('admin/social.html', links=links)

@app.route('/admin/social/delete/<int:sid>')
@login_required
def delete_social(sid):
    link = SocialLink.query.get_or_404(sid)
    db.session.delete(link)
    db.session.commit()
    flash('تم حذف الرابط')
    return redirect(url_for('manage_social'))

@app.route('/admin/social/edit/<int:sid>', methods=['GET', 'POST'])
@login_required
def edit_social(sid):
    link = SocialLink.query.get_or_404(sid)
    if request.method == 'POST':
        link.name = request.form['name']
        link.url = request.form['url']
        link.icon = request.form['icon']
        db.session.commit()
        flash('تم تعديل الرابط')
        return redirect(url_for('manage_social'))
    return render_template('admin/edit_social.html', link=link)

@app.route('/admin/about', methods=['GET', 'POST'])
@login_required
def edit_about():
    about = AboutMe.query.first()
    if request.method == 'POST':
        text_ar = request.form['text_ar']
        text_en = GoogleTranslator(source='ar', target='en').translate(text_ar)
        if about:
            about.text_ar = text_ar
            about.text_en = text_en
        else:
            about = AboutMe(text_ar=text_ar, text_en=text_en)
            db.session.add(about)
        db.session.commit()
        flash('تم تحديث نبذة عني')
        return redirect(url_for('edit_about'))
    return render_template('admin/about.html', about=about)

@app.route('/admin/project/image/delete/<int:image_id>', methods=['DELETE'])
@login_required
def delete_project_image(image_id):
    """Delete a project image"""
    try:
        image = ProjectImage.query.get_or_404(image_id)
        image_path = os.path.join('static/images', image.image_path)
        
        # حذف الملف من النظام
        if os.path.exists(image_path):
            os.remove(image_path)
        
        # حذف السجل من قاعدة البيانات
        db.session.delete(image)
        db.session.commit()
        
        return '', 204
    except Exception as e:
        db.session.rollback()
        return str(e), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
