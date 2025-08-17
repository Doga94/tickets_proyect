from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models.user import User
from ..models.ticket import Ticket
from ..models.response import Response
from .. import db
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, current_user, login_required

main = Blueprint('main', __name__)
bcrypt = Bcrypt()

@main.route("/")
def index():
    return render_template('base.html')

@main.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            flash('Username or email already exist.', 'danger')
            return redirect(url_for('main.register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('main.index'))
    return render_template('register.html')


@main.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid credentials!', 'danger')
            return redirect(url_for('main.login'))
    return render_template('login.html')

@main.route("/create-ticket", methods=['GET', 'POST'])
@login_required
def create_ticket():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        is_urgent = True if request.form.get('is_ugent') == 'on' else False

        new_ticket = Ticket(
            title=title,
            description=description,
            is_urgent=is_urgent,
            user_id=current_user.id
        )

        db.session.add(new_ticket)
        db.session.commit()

        flash('Ticket created successfully!', 'success')
        return redirect(url_for('main.view_tickets'))
    return render_template('create_ticket.html')

@main.route("/edit-ticket/<int:ticket_id>", methods=['GET', 'POST'])
@login_required
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if ticket.author.id != current_user.id:
        flash("You are not allowed to edit this ticket", "danger")
        return redirect(url_for('main.view_tickets'))
    
    if request.method == 'POST':
        ticket.title = request.form['title']
        ticket.description = request.form['description']
        ticket.is_urgent = True if request.form.get('is_urgent') == 'on' else False

        db.session.commit()
        flash("Ticket update successfully", "success")
        return redirect(url_for('main.view_tickets'))
    return render_template("edit_ticket.html", ticket=ticket)

@main.route("/delete-ticket/<int:ticket_id>", methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if current_user.role == 'agent' or ticket.author.id == current_user.id:
        db.session.delete(ticket)
        db.session.commit()
        flash('Ticket deleted successfully', 'success')
    else:
        flash('You are not allowed to delete this ticket', 'danger')
    return redirect(url_for('main.view_tickets'))

@main.route("/respond-ticket/<int:ticket_id>", methods=['POST'])
@login_required
def respond_ticket(ticket_id):
    if current_user.role != 'agent':
        flash("Only agents can respond to tickets", "danger")
        return redirect(url_for('main.view_tickets'))

    ticket = Ticket.query.get_or_404(ticket_id)
    message = request.form.get('message', '').strip()

    if not message:
        flash("Response message is required", "danger")
        return redirect(url_for('main.ticket_detail', ticket_id=ticket.id))
    
    response = Response(
        message=message,
        ticket_id=ticket.id,
        agent_id = current_user.id
    )
    db.session.add(response)
    db.session.commit()

    flash("Response added successfully", "success")
    return redirect(url_for('main.ticket_detail', ticket_id=ticket.id))

@main.route("/tickets")
@login_required
def view_tickets():
    status = request.args.get('status')
    base_query = Ticket.query

    if current_user.role == 'agent':
        if status in {'open', 'in_progress', 'resolved'}:
            base_query = base_query.filter_by(status=status)
        tickets = base_query.order_by(Ticket.created_at.desc()).all()
    else:
        base_query = base_query.filter_by(user_id=current_user.id)
        if status in {'open', 'in_progress', 'resolved'}:
            base_query = base_query.filter_by(status=status)
        tickets = base_query.order_by(Ticket.created_at.desc()).all()

    return render_template('tickets.html', tickets=tickets)

@main.route("/ticket/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    #Esta parte debe ser los permisos
    if current_user.role != 'agent' and ticket.author.id != current_user.id:
        flash("You are not allowed to see this ticket", "danger")
        return redirect(url_for('main.view_tickets'))
    return render_template('ticket_detail.html', ticket=ticket)

@main.route("/tickect<int:ticket_id>/status", methods=['POST'])
@login_required
def update_ticket_status(ticket_id):
    if current_user.role != 'agent':
        flash("Only agent can change ticket status", "danger")
        return redirect(url_for('main.ticket_detail', ticket_id=ticket_id))
    
    ticket = Ticket.query.get_or_404(ticket_id)
    new_status = request.form.get('status', '').strip()

    allowed = {'open', 'in_progress', 'resolved'}
    if new_status not in allowed:
        flash("Invalid status value", "danger")
        return redirect(url_for('main.ticket_detail', ticket_id=ticket.id))
    
    ticket.status = new_status
    db.session.commit()
    flash("Ticket status updated", "success")
    return redirect(url_for('main.ticket_detail', ticket_id=ticket.id))


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('main.login'))