import argparse
import json

from simulation import Simulation

default_topic = "climate_change"
default_models = {
    "USA": "gpt-3.5-turbo",
    "China": "gpt-3.5-turbo",
    "EU": "gpt-3.5-turbo", 
    "India": "gpt-3.5-turbo",
}    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Model UN Simulation")
    parser.add_argument("-t", "--topic", type=str, help="topic for the Model UN simulation", default=default_topic)
    parser.add_argument("-m", "--models", type=json.loads, help="model for the Model UN simulation", default=default_models,)
    parser.add_argument("-o", "--output", type=str, help="output directory for results", default=None)
    args = parser.parse_args()

    """Run the Model UN simulation."""
    print("Starting Model UN Simulation")
    print("=" * 50)
    sim = Simulation(args.topic, args.models, args.output)
    
    try:
        history = sim.run()
        print("Simulation completed successfully!")
    except Exception as e:
        print(f"Error running simulation: {e}")
        import traceback
        traceback.print_exc()