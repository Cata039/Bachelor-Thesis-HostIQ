"""
Smart Restaurant Management System - Main Simulation Runner
Entry point for running simulations - Agent Communication Focus
"""

from restaurant_model import RestaurantModel


def run_basic_simulation():
    """
    Run a basic simulation with default parameters
    """
    print("\n" + "="*70)
    print("SMART RESTAURANT MANAGEMENT SYSTEM")
    print("Multi-Agent Communication Simulation")
    print("="*70)
    
    # Create and run model - SMALLER for better visibility
    model = RestaurantModel(
        num_customers=10,      # Mai puțini clienți ca să vezi comunicarea
        num_waiters=2,
        simulation_steps=50    # Mai puțini pași
    )
    
    model.run_simulation()
    
    return model


if __name__ == "__main__":
    # Run basic simulation - shows agent communication
    model = run_basic_simulation()
    
    print("\n✅ Simulation complete!")
    print("Check the console output above for agent communication.")

