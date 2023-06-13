import traci
import matplotlib.pyplot as plt

class SumoSimulation:
    def __init__(self, sumocfg_file):
        self.sumocfg_file = sumocfg_file
        self.time_steps = []
        self.vehicle_counts = []
        self.counter = 0

    def run_simulation(self, edges_to_close, simulation_duration, vehicles_list):
        # Connect to the running SUMO simulation
        traci.start(["sumo-gui", "-c", self.sumocfg_file, "--time-to-teleport", "-1"])

        # Retrieve the list of available edges
        edge_list = traci.edge.getIDList()

        # Close the edges
        for edge_id in edges_to_close:
            traci.edge.setDisallowed(edge_id, ["all"])

        while traci.simulation.getMinExpectedNumber() > 0:
            try:
                traci.simulationStep()

                # Get the list of vehicles
                vhList = traci.vehicle.getIDList()
                #print("Vehicle List:", vhList)
                if vhList:
                    if  vehicles_list[self.counter] in vhList:
                        best_lanes = self.calculate_best_lanes(vehicles_list[self.counter])
                    else:
                        self.counter += 1
            except:
                print("vehicle gone")
                self.counter += 1
            #Retrieve data and update lists
            self.time_steps.append(traci.simulation.getTime())
            self.vehicle_counts.append(traci.simulation.getDepartedNumber())

            # Break the loop if the desired simulation duration is reached
            if traci.simulation.getTime() > simulation_duration:
                break

        # End the simulation and close the TraCI connection
        traci.close()
    def stats(self, edges_to_close, simulation_duration, null):
        # Connect to the running SUMO simulation
        traci.start(["sumo", "-c", self.sumocfg_file, "--time-to-teleport", "-1"])

        # Retrieve the list of available edges
        edge_list = traci.edge.getIDList()

        # Close the edges
        for edge_id in edges_to_close:
            traci.edge.setDisallowed(edge_id, ["all"])

        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            # Retrieve data and update lists
            self.time_steps.append(traci.simulation.getTime())
            self.vehicle_counts.append(traci.simulation.getDepartedNumber())

            # Break the loop if the desired simulation duration is reached
            if traci.simulation.getTime() > simulation_duration:
                break

        # End the simulation and close the TraCI connection
        traci.close()
    def plot_results(self):
        # Plot the data
        plt.plot(self.time_steps, self.vehicle_counts)
        plt.xlabel("Simulation Time")
        plt.ylabel("Number of Vehicles Departed")
        plt.title("Vehicle Departures over Time")
        plt.grid(True)
        plt.show()

    def calculate_best_lanes(self, vehicle_id):
        # Get the current lane of the vehicle
        current_lane = traci.vehicle.getLaneID(vehicle_id)

        # Get the neighboring lanes of the current lane
        neighboring_lanes = traci.lane.getLinks(current_lane)
        # print("neighboring_lanes: ",neighboring_lanes)
        # Calculate average vehicle speed for each neighboring lane
        lane_speeds = []
        for lane in neighboring_lanes:
            vehicles = traci.lane.getLastStepVehicleIDs(lane[0])

            speeds = [traci.vehicle.getSpeed(vehicle) for vehicle in vehicles]
            # Get the current time
            current_time = traci.simulation.getTime()

            # Get the current speed of the vehicle in meters per second (m/s)
            current_speed_mps = traci.vehicle.getSpeed(vehicle_id)

            # Convert the speed to kilometers per hour (km/h)
            current_speed_kph = current_speed_mps * 3.6

            print("Vehicle", vehicle_id, "speed at time", current_time, "is", current_speed_kph, "km/h")
            if speeds:
                avg_speed = sum(speeds) / len(speeds)
            else:
                avg_speed = 0
            lane_speeds.append((lane[0], avg_speed))
        # Sort lanes based on average speed in descending order
        sorted_lanes = sorted(lane_speeds, key=lambda x: x[1], reverse=True)

        # Select the best lanes based on your criteria
        best_lanes = [lane[0] for lane in sorted_lanes[:5]]  # Example: Select top 5 lanes with highest average speed
        print("best Lanes of <"+vehicle_id+">",best_lanes)

        return best_lanes


# Create an instance of the SumoSimulation class
simulation = SumoSimulation("../osm.sumocfg")

# Define the list of edges to close

#no constrain
edges_to_close = ["-339112691#1","339112691#0"]

#single constrain
# edges_to_close = ["-724017859#1","724017859#0"]

vehicles_list = ["veh0","veh1","veh2","veh3","veh4","veh5","veh6","veh7","veh8","veh9","veh10","veh11","veh12","veh13","veh14","veh15","veh16","veh17","veh18","veh19","veh20","veh21","veh22"]

# Run the simulation for a specific duration
simulation_duration = 10000  # Replace with your desired duration in simulation steps

# Run the simulation
simulation.run_simulation(edges_to_close, simulation_duration, vehicles_list)
simulation.stats(edges_to_close, 500, vehicles_list)
# Plot the results
simulation.plot_results()
