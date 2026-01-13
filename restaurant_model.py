"""
Smart Restaurant Management System - MESA Model
Main simulation model coordinating all agents
Compatible with MESA 3.x
"""

from mesa import Model, DataCollector
from restaurant_agents import HostAgent, CustomerAgent, WaiterAgent
import random


class RestaurantModel(Model):
    """
    Restaurant Management Multi-Agent Model
    Coordinates interactions between Host, Customer, and Waiter agents
    """
    
    def __init__(self, num_customers=30, num_waiters=3, simulation_steps=100):
        super().__init__()
        self.num_customers = num_customers
        self.num_waiters = num_waiters
        self.simulation_steps = simulation_steps
        self.event_log = []
        self.current_customer_id = 1000
        self.current_step = 0
        
        # Statistics tracking
        self.total_customers_served = 0
        self.total_customers_waiting = 0
        self.total_wait_time = 0
        self.customers_left_unsatisfied = 0
        
        # Create HostAgent (single instance)
        self.host_agent = HostAgent(1, self)
        
        # Create WaiterAgents
        self.waiter_agents = []
        for i in range(num_waiters):
            waiter = WaiterAgent(100 + i, self)
            self.waiter_agents.append(waiter)
        
        # Create CustomerAgents with staggered arrivals
        self.customer_agents = []
        arrival_times = sorted([random.randint(0, simulation_steps - 30) 
                               for _ in range(num_customers)])
        
        for i, arrival_time in enumerate(arrival_times):
            party_size = random.choices([1, 2, 3, 4, 5, 6], 
                                       weights=[5, 30, 20, 25, 15, 5])[0]
            customer = CustomerAgent(self.current_customer_id, self, party_size, arrival_time)
            self.customer_agents.append(customer)
            self.current_customer_id += 1
        
        # Data collector for statistics
        self.datacollector = DataCollector(
            model_reporters={
                "Available Tables": self._count_available_tables,
                "Occupied Tables": self._count_occupied_tables,
                "Customers Waiting": self._count_waiting_customers,
                "Customers Seated": self._count_seated_customers,
                "Customers on Waitlist": self._count_waitlisted_customers,
                "Table Utilization %": self._get_table_utilization,
                "Active Orders": self._count_active_orders,
                "Completed Orders": self._count_completed_orders,
            }
        )
        
        self.log_event("Restaurant simulation initialized", "info")
        self.log_event(f"Configuration: {num_customers} customers, {num_waiters} waiters, "
                      f"{len(self.host_agent.tables)} tables", "info")
    
    def log_event(self, message, level='info'):
        """Log events that occur during simulation"""
        event = {
            'step': self.current_step,
            'level': level,
            'message': message
        }
        self.event_log.append(event)
    
    def get_host_agent(self):
        """Return the HostAgent instance"""
        return self.host_agent
    
    def get_customer_by_id(self, customer_id):
        """Find and return a customer agent by ID"""
        for customer in self.customer_agents:
            if customer.unique_id == customer_id:
                return customer
        return None
    
    def assign_waiter(self, customer_id):
        """Assign a waiter to a customer (round-robin or least busy)"""
        if not self.waiter_agents:
            return None
        
        # Find waiter with fewest active orders
        available_waiter = min(self.waiter_agents, 
                              key=lambda w: len(w.active_orders))
        return available_waiter
    
    def get_all_agents(self):
        """Return all agents in the simulation"""
        all_agents = [self.host_agent] + self.waiter_agents + self.customer_agents
        return all_agents
    
    # Data collector helper methods
    def _count_available_tables(self):
        return sum(1 for t in self.host_agent.tables if t.is_available())
    
    def _count_occupied_tables(self):
        return sum(1 for t in self.host_agent.tables if not t.is_available())
    
    def _count_waiting_customers(self):
        return sum(1 for c in self.customer_agents if c.status == 'waiting')
    
    def _count_seated_customers(self):
        return sum(1 for c in self.customer_agents 
                  if c.status in ['seated', 'eating'])
    
    def _count_waitlisted_customers(self):
        return sum(1 for c in self.customer_agents if c.status == 'waitlisted')
    
    def _get_table_utilization(self):
        return self.host_agent.get_table_utilization()
    
    def _count_active_orders(self):
        return sum(len(w.active_orders) for w in self.waiter_agents)
    
    def _count_completed_orders(self):
        return sum(len(w.completed_orders) for w in self.waiter_agents)
    
    def step(self):
        """Advance the model by one step"""
        self.datacollector.collect(self)
        
        # Manually step through all agents in random order
        all_agents = self.get_all_agents()
        random.shuffle(all_agents)
        
        for agent in all_agents:
            agent.step()
        
        self.current_step += 1
    
    def run_simulation(self, steps=None):
        """Run the complete simulation"""
        if steps is None:
            steps = self.simulation_steps
        
        print(f"\n{'='*60}")
        print(f"AGENT COMMUNICATION LOG")
        print(f"{'='*60}\n")
        
        for i in range(steps):
            self.step()
        
        print(f"\n{'='*60}")
        print(f"Simulation Complete!")
        print(f"{'='*60}\n")
        
        self._print_final_statistics()
    
    def _print_final_statistics(self):
        """Print final simulation statistics"""
        total_customers = len(self.customer_agents)
        customers_served = sum(1 for c in self.customer_agents if c.status == 'left' 
                              and c.table_id is not None)
        customers_left_unsatisfied = sum(1 for c in self.customer_agents 
                                        if c.status == 'left' and c.table_id is None)
        
        customers_with_wait_times = [c for c in self.customer_agents 
                                     if c.waiting_time > 0]
        avg_wait_time = (sum(c.waiting_time for c in customers_with_wait_times) / 
                        len(customers_with_wait_times) if customers_with_wait_times else 0)
        
        total_orders = sum(w.total_orders_served for w in self.waiter_agents)
        
        print("FINAL STATISTICS")
        print("-" * 60)
        print(f"Total Customers: {total_customers}")
        print(f"Customers Served: {customers_served} ({customers_served/total_customers*100:.1f}%)")
        print(f"Customers Left Unsatisfied: {customers_left_unsatisfied}")
        print(f"Average Wait Time: {avg_wait_time:.2f} time steps")
        print(f"Total Food Orders Completed: {total_orders}")
        print(f"Peak Table Utilization: {max(self.datacollector.get_model_vars_dataframe()['Table Utilization %']):.1f}%")
        print(f"Total Events Logged: {len(self.event_log)}")
        print("-" * 60)
    
    def get_event_log(self, level=None, last_n=None):
        """
        Retrieve event log with optional filtering
        level: Filter by event level ('info', 'success', 'warning')
        last_n: Return only the last n events
        """
        events = self.event_log
        
        if level:
            events = [e for e in events if e['level'] == level]
        
        if last_n:
            events = events[-last_n:]
        
        return events
    
    def print_event_log(self, level=None, last_n=50):
        """Print formatted event log"""
        events = self.get_event_log(level, last_n)
        
        print(f"\n{'='*80}")
        print(f"EVENT LOG ({len(events)} events)")
        if level:
            print(f"Filtered by level: {level}")
        if last_n:
            print(f"Showing last {last_n} events")
        print(f"{'='*80}\n")
        
        for event in events:
            level_symbol = {
                'info': 'ℹ️',
                'success': '✅',
                'warning': '⚠️'
            }.get(event['level'], '•')
            
            print(f"[Step {event['step']:3d}] {level_symbol} {event['message']}")
        
        print(f"\n{'='*80}\n")
    
    def export_statistics(self):
        """Export statistics as a dictionary"""
        df = self.datacollector.get_model_vars_dataframe()
        
        return {
            'model_data': df,
            'total_customers': len(self.customer_agents),
            'customers_served': sum(1 for c in self.customer_agents 
                                   if c.status == 'left' and c.table_id is not None),
            'average_wait_time': sum(c.waiting_time for c in self.customer_agents 
                                    if c.waiting_time > 0) / 
                                len([c for c in self.customer_agents if c.waiting_time > 0])
                                if any(c.waiting_time > 0 for c in self.customer_agents) else 0,
            'total_orders': sum(w.total_orders_served for w in self.waiter_agents),
            'event_log': self.event_log
        }
