"""
Smart Restaurant Management System - Agent Implementation
Multi-agent system for intelligent table management and coordination
"""

from mesa import Agent
import random


class Table:
    """Represents a restaurant table with specific capacity"""
    def __init__(self, table_id, capacity):
        self.table_id = table_id
        self.capacity = capacity
        self.occupied = False
        self.customer_id = None
        self.occupied_since = None
    
    def is_available(self):
        return not self.occupied
    
    def assign(self, customer_id, current_time):
        self.occupied = True
        self.customer_id = customer_id
        self.occupied_since = current_time
    
    def release(self):
        self.occupied = False
        self.customer_id = None
        self.occupied_since = None
    
    def __repr__(self):
        status = "Occupied" if self.occupied else "Available"
        return f"Table {self.table_id} (Cap: {self.capacity}) - {status}"


class HostAgent(Agent):
    """
    HostAgent manages table availability and assigns tables to customers
    Responsibilities:
    - Track available tables
    - Process reservation requests
    - Assign optimal tables based on party size
    - Manage waitlist when restaurant is full
    """
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.tables = self._initialize_tables()
        self.pending_requests = []
        self.waitlist = []
        self.confirmed_reservations = []
        self.rejected_requests = []
        
    def _initialize_tables(self):
        """Create restaurant tables with varying capacities"""
        tables = [
            Table(1, 2),
            Table(2, 2),
            Table(3, 4),
            Table(4, 4),
            Table(5, 6),
            Table(6, 6),
        ]
        return tables
    
    def receive_reservation_request(self, customer_id, party_size, request_time):
        """Process incoming reservation request from CustomerAgent"""
        request = {
            'customer_id': customer_id,
            'party_size': party_size,
            'request_time': request_time,
            'status': 'pending'
        }
        
        # Check immediately if table available
        table = self.find_suitable_table(party_size)
        
        if table:
            # Assign table immediately
            table.assign(customer_id, self.model.current_step)
            request['status'] = 'confirmed'
            request['table_id'] = table.table_id
            request['assigned_time'] = self.model.current_step
            
            self.confirmed_reservations.append(request)
            
            # Notify customer immediately
            customer = self.model.get_customer_by_id(customer_id)
            if customer:
                customer.receive_confirmation(table.table_id, self.model.current_step)
                print(f"Host : Table {table.table_id} available")
            
            self.model.log_event(
                f"HostAgent assigned Table {table.table_id} to Customer {customer_id}",
                'success'
            )
        else:
            # No table available - add to waitlist immediately
            self.waitlist.append(request)
            request['status'] = 'waitlisted'
            
            customer = self.model.get_customer_by_id(customer_id)
            if customer:
                wait_position = len(self.waitlist)
                customer.receive_waitlist_notification(wait_position)
                print(f"Host : All tables occupied (Client {customer_id} on waiting list)")
            
            self.model.log_event(
                f"HostAgent added Customer {customer_id} to waitlist (position {len(self.waitlist)})",
                'warning'
            )
    
    def find_suitable_table(self, party_size):
        """
        Intelligent table assignment algorithm
        Finds the smallest available table that can accommodate the party
        """
        available_tables = [t for t in self.tables if t.is_available()]
        
        if not available_tables:
            return None
        
        # Find tables that can fit the party
        suitable_tables = [t for t in available_tables if t.capacity >= party_size]
        
        if not suitable_tables:
            return None
        
        # Choose the smallest suitable table to optimize space
        suitable_tables.sort(key=lambda x: x.capacity)
        return suitable_tables[0]
    
    def get_available_tables_count(self):
        """Return count of available tables"""
        return sum(1 for t in self.tables if t.is_available())
    
    def get_table_utilization(self):
        """Calculate table utilization percentage"""
        occupied = sum(1 for t in self.tables if not t.is_available())
        return (occupied / len(self.tables)) * 100
    
    def step(self):
        """Process pending requests and manage table assignments"""
        current_time = self.model.current_step
        
        # Check if any waitlisted customers can now be seated
        for request in self.waitlist[:]:
            customer_id = request['customer_id']
            party_size = request['party_size']
            
            table = self.find_suitable_table(party_size)
            if table:
                table.assign(customer_id, current_time)
                request['status'] = 'confirmed'
                request['table_id'] = table.table_id
                request['assigned_time'] = current_time
                
                self.confirmed_reservations.append(request)
                self.waitlist.remove(request)
                
                customer = self.model.get_customer_by_id(customer_id)
                if customer:
                    customer.receive_confirmation(table.table_id, current_time)
                    print(f"\n{'='*60}")
                    print(f"Client {customer_id}: Party of {party_size}")
                    print(f"Host : Table {table.table_id} now available (from waiting list)")
                    print(f"{'='*60}")
                
                self.model.log_event(
                    f"HostAgent seated waitlisted Customer {customer_id} at Table {table.table_id}",
                    'success'
                )


class CustomerAgent(Agent):
    """
    CustomerAgent represents a customer or party requesting a table
    Responsibilities:
    - Send reservation requests to HostAgent
    - Wait for confirmation or alternative suggestions
    - Simulate dining duration
    - Interact with WaiterAgent for orders
    """
    
    def __init__(self, unique_id, model, party_size, arrival_time):
        super().__init__(unique_id, model)
        self.party_size = party_size
        self.arrival_time = arrival_time
        self.status = 'waiting'  # waiting, seated, eating, waitlisted, left
        self.table_id = None
        self.seated_time = None
        self.dining_duration = random.randint(15, 45)  # 15-45 time steps
        self.order_placed = False
        self.food_received = False
        self.waiter_id = None
        self.wait_position = None
        self.patience = random.randint(20, 50)  # How long they'll wait
        self.waiting_time = 0
    
    def send_reservation_request(self):
        """Send reservation request to HostAgent"""
        host = self.model.get_host_agent()
        if host:
            host.receive_reservation_request(
                self.unique_id,
                self.party_size,
                self.model.current_step
            )
            self.model.log_event(
                f"Customer {self.unique_id} requested table for party of {self.party_size}",
                'info'
            )
    
    def receive_confirmation(self, table_id, time):
        """Receive confirmation from HostAgent"""
        self.status = 'seated'
        self.table_id = table_id
        self.seated_time = time
        self.waiting_time = time - self.arrival_time
        
        self.model.log_event(
            f"Customer {self.unique_id} confirmed at Table {table_id} (waited {self.waiting_time} steps)",
            'success'
        )
    
    def receive_waitlist_notification(self, position):
        """Receive notification about waitlist position"""
        self.status = 'waitlisted'
        self.wait_position = position
        
        self.model.log_event(
            f"Customer {self.unique_id} added to waitlist (position {position})",
            'warning'
        )
    
    def place_order(self):
        """Place food order with WaiterAgent"""
        waiter = self.model.assign_waiter(self.unique_id)
        if waiter:
            self.waiter_id = waiter.unique_id
            print(f"\n{'='*60}")
            print(f"Client {self.unique_id}: Order please!")
            waiter.receive_order(self.unique_id, self.table_id)
            self.order_placed = True
            
            self.model.log_event(
                f"Customer {self.unique_id} placed order with Waiter {waiter.unique_id}",
                'info'
            )
    
    def receive_food(self):
        """Receive food from WaiterAgent"""
        self.food_received = True
        self.status = 'eating'
        
        self.model.log_event(
            f"Customer {self.unique_id} received food and started eating",
            'success'
        )
    
    def leave_restaurant(self):
        """Customer finishes dining and leaves"""
        # Release table
        host = self.model.get_host_agent()
        if host and self.table_id:
            for table in host.tables:
                if table.table_id == self.table_id:
                    table.release()
                    break
        
        self.status = 'left'
        
        self.model.log_event(
            f"Customer {self.unique_id} finished dining and left (Table {self.table_id} now available)",
            'info'
        )
    
    def step(self):
        """Customer behavior per time step"""
        current_time = self.model.current_step
        
        if self.status == 'waiting' and current_time == self.arrival_time:
            # Arrive and request table
            self.send_reservation_request()
        
        elif self.status == 'seated' and not self.order_placed:
            # Place order shortly after being seated
            if current_time - self.seated_time >= 2:
                self.place_order()
        
        elif self.status == 'eating':
            # Check if finished dining
            if current_time - self.seated_time >= self.dining_duration:
                self.leave_restaurant()
        
        elif self.status == 'waitlisted':
            # Track waiting time and check patience
            time_waiting = current_time - self.arrival_time
            if time_waiting >= self.patience:
                self.status = 'left'
                self.model.log_event(
                    f"Customer {self.unique_id} left due to long wait",
                    'warning'
                )


class WaiterAgent(Agent):
    """
    WaiterAgent handles food orders and service
    Responsibilities:
    - Receive orders from CustomerAgents
    - Process orders (simulated cooking time)
    - Deliver food to customers
    - Track active orders
    """
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.active_orders = []
        self.completed_orders = []
        self.total_orders_served = 0
    
    def receive_order(self, customer_id, table_id):
        """Receive order from CustomerAgent"""
        order = {
            'customer_id': customer_id,
            'table_id': table_id,
            'order_time': self.model.current_step,
            'preparation_time': random.randint(10, 25),  # 10-25 time steps
            'status': 'preparing'
        }
        self.active_orders.append(order)
        
        print(f"Waiter {self.unique_id}: Order received from Table {table_id}")
        print(f"{'='*60}")
        
        self.model.log_event(
            f"Waiter {self.unique_id} received order from Customer {customer_id} at Table {table_id}",
            'info'
        )
    
    def deliver_food(self, order):
        """Deliver prepared food to customer"""
        customer = self.model.get_customer_by_id(order['customer_id'])
        if customer and customer.status == 'seated':
            print(f"\n{'='*60}")
            print(f"Waiter {self.unique_id}: Your food is ready!")
            print(f"Client {order['customer_id']}: Thank you!")
            print(f"{'='*60}")
            
            customer.receive_food()
            order['status'] = 'delivered'
            order['delivery_time'] = self.model.current_step
            
            self.completed_orders.append(order)
            self.total_orders_served += 1
            
            self.model.log_event(
                f"Waiter {self.unique_id} delivered food to Customer {order['customer_id']}",
                'success'
            )
    
    def step(self):
        """Process orders each time step"""
        current_time = self.model.current_step
        
        for order in self.active_orders[:]:
            if order['status'] == 'preparing':
                time_cooking = current_time - order['order_time']
                
                if time_cooking >= order['preparation_time']:
                    # Food is ready, deliver it
                    self.deliver_food(order)
                    self.active_orders.remove(order)