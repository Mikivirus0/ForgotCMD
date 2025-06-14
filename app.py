from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-super-secret-key-change-this' 

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'forgotcmd123'  

def load_commands():
    try:
        with open('commands.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Missing File")
        return {}

def save_commands(data):
    try:
        with open('commands.json', 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving commands: {e}")
        return False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

commands_data = load_commands()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').lower().strip()
    
    if not query:
        return jsonify([])
    
    results = []
    
    for tool, commands in commands_data.items():
        if query in tool.lower():
            for cmd in commands:
                results.append({
                    'tool': tool,
                    'command': cmd['command'],
                    'description': cmd['description']
                })
        else:
            for cmd in commands:
                if (query in cmd['command'].lower() or 
                    query in cmd['description'].lower()):
                    results.append({
                        'tool': tool,
                        'command': cmd['command'],
                        'description': cmd['description']
                    })
    
    return jsonify(results)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    flash('Successfully logged out!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    global commands_data
    commands_data = load_commands()  
    return render_template('admin_dashboard.html', commands=commands_data)

@app.route('/admin/api/tools', methods=['GET'])
@login_required
def get_tools():
    return jsonify(list(commands_data.keys()))

@app.route('/admin/api/commands/<tool>', methods=['GET'])
@login_required
def get_tool_commands(tool):
    if tool in commands_data:
        return jsonify(commands_data[tool])
    return jsonify([])

@app.route('/admin/api/command', methods=['POST'])
@login_required
def add_command():
    global commands_data
    data = request.json
    tool = data.get('tool')
    command = data.get('command')
    description = data.get('description')
    
    if not all([tool, command, description]):
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    if tool not in commands_data:
        commands_data[tool] = []
    
    for cmd in commands_data[tool]:
        if cmd['command'] == command:
            return jsonify({'success': False, 'message': 'Command already exists'})
    
    commands_data[tool].append({
        'command': command,
        'description': description
    })
    
    if save_commands(commands_data):
        return jsonify({'success': True, 'message': 'Command added successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to save command'})

@app.route('/admin/api/command', methods=['PUT'])
@login_required
def update_command():
    global commands_data
    data = request.json
    tool = data.get('tool')
    old_command = data.get('old_command')
    new_command = data.get('command')
    new_description = data.get('description')
    
    if not all([tool, old_command, new_command, new_description]):
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    if tool not in commands_data:
        return jsonify({'success': False, 'message': 'Tool not found'})
    
    for cmd in commands_data[tool]:
        if cmd['command'] == old_command:
            cmd['command'] = new_command
            cmd['description'] = new_description
            if save_commands(commands_data):
                return jsonify({'success': True, 'message': 'Command updated successfully'})
            else:
                return jsonify({'success': False, 'message': 'Failed to save changes'})
    
    return jsonify({'success': False, 'message': 'Command not found'})

@app.route('/admin/api/command', methods=['DELETE'])
@login_required
def delete_command():
    global commands_data
    data = request.json
    tool = data.get('tool')
    command = data.get('command')
    
    if not all([tool, command]):
        return jsonify({'success': False, 'message': 'Tool and command are required'})
    
    if tool not in commands_data:
        return jsonify({'success': False, 'message': 'Tool not found'})
    
    commands_data[tool] = [cmd for cmd in commands_data[tool] if cmd['command'] != command]
    
    if not commands_data[tool]:
        del commands_data[tool]
    
    if save_commands(commands_data):
        return jsonify({'success': True, 'message': 'Command deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to save changes'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)