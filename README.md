# Smart Restaurant Management System

This project simulates a restaurant management system using multi-agent architecture. The system coordinates three types of agents to handle restaurant operations: hosts manage table assignments, customers request seating and meals, and waiters take orders and serve food.

## Instalation
Install the required dependencies:

```bash
pip3 install -r requirements.txt
```

### Running the Application (Web version):
Start the Flask server:
```bash
python3 web_interface.py
```
Open your browser and navigate to:: **http://localhost:5000**

#### Console version:
```bash
python3 main_simulation.py
```

## Project Structure
```bash
.
├── web_interface.py       # Flask server for web interface
├── restaurant_agents.py   # Agent definitions and behaviors
├── restaurant_model.py    # MESA model implementation
├── main_simulation.py     # Console-based simulation
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface template
└── README.md             # This file
```

## Web Interface Features

### Communication Log (Left):
Displays real-time message exchanges between agents with color-coded identification:
* Client - Blue
* Host - Green
* Waiter - Yellow
* Success messages - Light green
* Warnings - Red
Messages auto-scroll to show the latest communications.

### Restaurant Tables (Center Panel):
Visual representation of 10 restaurant tables:
* Green - Available table
* Yellow - Occupied table (shows customer ID)
* Updates in real-time as customers are seated and leave

### Waiting List (Right Panel):
Shows customers waiting for available tables:
* Updates automatically when customers join the queue
* Removes customers automatically when they receive a table
* Displays current waiting count

##  Statistics Dashboard
Real-time metrics displayed at the top of the interface:
* Total Customers - Total number of customers who have visited
* Seated - Currently dining customers
* Available Tables - Number of free tables
* Waiting - Customers in the waiting list

## Controls
* Party Size Input - Enter number of people (1-8) in the party
* Add Customer - Manually add a customer with the specified party size


## Usage Guide
### Basic Operation: 

* Enter a party size (1-8 people) in the input field
* Click "Add Customer" to create a new customer
* Watch the customer interact with the host to request a table
* Observe the waiter taking orders and serving food
* See customers leave after completing their meal


### Stopping the Server
- To stop the Flask server, press CTRL+C in the terminal window.



