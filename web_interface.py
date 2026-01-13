"""
Smart Restaurant Management System - Web Interface
"""

from flask import Flask, render_template, jsonify, request
from restaurant_model import RestaurantModel
from restaurant_agents import CustomerAgent
import threading
import random
import time

app = Flask(__name__)

# Global simulation state
simulation = {
    'model': None,
    'running': False,
    'messages': [],
    'step_thread': None
}

def initialize_simulation():
    """Initialize the restaurant simulation"""
    model = RestaurantModel(
        num_customers=0,  # Start with 0, we'll add manually
        num_waiters=2,
        simulation_steps=1000
    )
    simulation['model'] = model
    simulation['messages'] = []
    return model

def add_message(message, msg_type='info'):
    """Add a message to the communication log"""
    timestamp = time.strftime("%H:%M:%S")
    simulation['messages'].append({
        'time': timestamp,
        'message': message,
        'type': msg_type
    })
    # Keep only last 50 messages
    if len(simulation['messages']) > 50:
        simulation['messages'].pop(0)

def simulation_step():
    """Run simulation steps in background"""
    while simulation['running']:
        if simulation['model']:
            simulation['model'].step()
        time.sleep(0.5)  # Half second between steps

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_simulation():
    """Start the simulation"""
    if not simulation['model']:
        initialize_simulation()
    
    simulation['running'] = True
    
    if not simulation['step_thread'] or not simulation['step_thread'].is_alive():
        simulation['step_thread'] = threading.Thread(target=simulation_step, daemon=True)
        simulation['step_thread'].start()
    
    add_message("🟢 Restaurant opened!", 'success')
    return jsonify({'status': 'started'})


@app.route('/api/init', methods=['POST'])
def init_simulation():
    """Initialize simulation without starting"""
    if not simulation['model']:
        initialize_simulation()
    return jsonify({'status': 'initialized'})

@app.route('/api/stop', methods=['POST'])
def stop_simulation():
    """Stop the simulation"""
    simulation['running'] = False
    add_message("🔴 Restaurant closed!", 'warning')
    return jsonify({'status': 'stopped'})

@app.route('/api/reset', methods=['POST'])
def reset_simulation():
    """Reset the simulation"""
    simulation['running'] = False
    initialize_simulation()
    simulation['messages'] = []
    add_message("🔄 Restaurant reset!", 'info')
    return jsonify({'status': 'reset'})

@app.route('/api/add_customer', methods=['POST'])
def add_customer():
    """Add a new customer manually"""
    if not simulation['model']:
        initialize_simulation()
    
    data = request.json
    party_size = data.get('party_size', random.randint(1, 6))
    
    model = simulation['model']
    customer_id = model.current_customer_id
    model.current_customer_id += 1
    
    # Add client message FIRST
    add_message(f"Client {customer_id}: Party of {party_size}", 'client')
    
    # Create new customer
    customer = CustomerAgent(
        unique_id=customer_id,
        model=model,
        party_size=party_size,
        arrival_time=model.current_step
    )
    
    model.customer_agents.append(customer)
    
    # Customer sends request (which will trigger Host response)
    customer.send_reservation_request()
    
    # AUTO-START simulation if not running
    if not simulation['running']:
        simulation['running'] = True
        if not simulation['step_thread'] or not simulation['step_thread'].is_alive():
            simulation['step_thread'] = threading.Thread(target=simulation_step, daemon=True)
            simulation['step_thread'].start()
    
    return jsonify({
        'status': 'added',
        'customer_id': customer_id,
        'party_size': party_size
    })

@app.route('/api/state')
def get_state():
    """Get current simulation state"""
    if not simulation['model']:
        return jsonify({
            'tables': [],
            'waitlist': [],
            'messages': simulation['messages'],
            'stats': {}
        })
    
    model = simulation['model']
    host = model.host_agent
    
    # Get table states
    tables = []
    for table in host.tables:
        tables.append({
            'id': table.table_id,
            'capacity': table.capacity,
            'occupied': table.occupied,
            'customer_id': table.customer_id
        })
    
    # Get waitlist
    waitlist = []
    for request in host.waitlist:
        waitlist.append({
            'customer_id': request['customer_id'],
            'party_size': request['party_size']
        })
    
    # Get statistics
    stats = {
        'total_customers': len(model.customer_agents),
        'customers_seated': sum(1 for c in model.customer_agents if c.status in ['seated', 'eating']),
        'customers_waiting': len(host.waitlist),
        'available_tables': sum(1 for t in host.tables if not t.occupied),
        'total_tables': len(host.tables)
    }
    
    return jsonify({
        'tables': tables,
        'waitlist': waitlist,
        'messages': simulation['messages'][-20:],  # Last 20 messages
        'stats': stats
    })

# Custom message capture for agents
original_print = print

def custom_print(*args, **kwargs):
    """Capture print statements and add to message log"""
    message = ' '.join(str(arg) for arg in args)
    
    # Ignore separator lines
    if message.strip() and not message.strip().startswith('='):
        msg_type = 'info'
        
        if 'Client' in message and 'Party of' in message:
            msg_type = 'client'
        elif 'Client' in message and 'Order please' in message:
            msg_type = 'client'
        elif 'Client' in message and 'Thank you' in message:
            msg_type = 'client'
        elif 'Host' in message and 'available' in message:
            msg_type = 'host'
        elif 'Host' in message and 'waiting list' in message:
            msg_type = 'warning'
        elif 'Waiter' in message and 'Order received' in message:
            msg_type = 'waiter'
        elif 'Waiter' in message and 'food is ready' in message:
            msg_type = 'success'
        
        add_message(message, msg_type)
    
    # Still print to console
    original_print(*args, **kwargs)

# Replace print globally
import builtins
builtins.print = custom_print

if __name__ == '__main__':
    print("🍽️  Starting Restaurant Management System...")
    print("📱 Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000, use_reloader=False)