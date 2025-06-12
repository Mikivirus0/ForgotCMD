from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

def load_commands():
    try:
        with open('commands.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Missing File")

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
            # If query matches tool name, return all commands for that tool
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)