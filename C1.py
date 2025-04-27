import matplotlib
matplotlib.use('Agg')  # Prevent GUI backend issues
import matplotlib.pyplot as plt
import os
from pathlib import Path as FilePath

class C4ContextDiagram:
    def __init__(self, system_name, output_filename="c4_level1_context"):
        self.system_name = system_name
        self.output_filename = output_filename
        self.users = []
        self.external_systems = []
        self.relationships = []

    def add_user(self, name, description=None):
        self.users.append({"name": name, "description": description})
        return self

    def add_external_system(self, name, description=None):
        self.external_systems.append({"name": name, "description": description})
        return self

    def add_relationship(self, source, target, label):
        self.relationships.append({"source": source, "target": target, "label": label})
        return self

    def from_json(self, json_data):
        if "users" in json_data:
            for user in json_data["users"]:
                self.add_user(user["name"], user.get("description"))
        if "external_systems" in json_data:
            for system in json_data["external_systems"]:
                self.add_external_system(system["name"], system.get("description"))
        if "relationships" in json_data:
            for rel in json_data["relationships"]:
                self.add_relationship(rel["source"], rel["target"], rel["label"])
        return self

    def to_json(self):
        return {
            "system_name": self.system_name,
            "users": self.users,
            "external_systems": self.external_systems,
            "relationships": self.relationships
        }

def generate(self):
    """Generate a C4 Level 1 Context Diagram."""
    output_dir = "diagrams_output"
    FilePath(output_dir).mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_facecolor('white')
    ax.axis('off')

    # Positions
    user_x, user_y = -5, 0
    system_x, system_y = 0, 0
    external_x, external_y = 5, 0

    print("Users:", self.users)  # <--- Debugging
    print("External Systems:", self.external_systems)  # <--- Debugging
    print("Relationships:", self.relationships)  # <--- Debugging

    # Draw main system
    ax.text(system_x, system_y, self.system_name, fontsize=16, ha='center', va='center', bbox=dict(boxstyle="round,pad=0.5", edgecolor='black', facecolor='#f0f0f0'))

    # Draw users
    for idx, user in enumerate(self.users):
        y_offset = (idx - len(self.users)//2) * 2
        ax.text(user_x, user_y + y_offset, user["name"], fontsize=12, ha='center', va='center', bbox=dict(boxstyle="round,pad=0.5", edgecolor='blue', facecolor='#e0f7fa'))
        ax.annotate("", xy=(system_x-1, system_y+y_offset*0.8), xytext=(user_x+1, user_y+y_offset), arrowprops=dict(arrowstyle="->"))

    # Draw external systems
    for idx, system in enumerate(self.external_systems):
        y_offset = (idx - len(self.external_systems)//2) * 2
        ax.text(external_x, external_y + y_offset, system["name"], fontsize=12, ha='center', va='center', bbox=dict(boxstyle="round,pad=0.5", edgecolor='green', facecolor='#e8f5e9'))
        ax.annotate("", xy=(system_x+1, system_y+y_offset*0.8), xytext=(external_x-1, external_x+y_offset), arrowprops=dict(arrowstyle="->"))

    # Save diagram
    output_path = os.path.join(output_dir, f"{self.output_filename}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Diagram generated at {output_path}")
    return output_path

if __name__ == "__main__":
    diagram = C4ContextDiagram("Enterprise Solution Architecture Platform")
    diagram.add_user("Solution Architect", "Designs system architectures")
    diagram.add_external_system("Oracle Financials", "Enterprise financial system")
    diagram.add_relationship("Solution Architect", "Enterprise Solution Architecture Platform", "Designs")
    diagram.add_relationship("Enterprise Solution Architecture Platform", "Oracle Financials", "Integrates with")

    diagram.generate()



# python C1.py