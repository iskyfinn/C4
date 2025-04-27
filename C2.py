import matplotlib
matplotlib.use('Agg')  # Ensure no GUI errors
import matplotlib.pyplot as plt
import os
from pathlib import Path as FilePath

class C4ContainerDiagram:
    def __init__(self, system_name, output_filename="c4_level2_container"):
        self.system_name = system_name
        self.output_filename = output_filename
        self.containers = []
        self.relationships = []

    def add_container(self, name, technology, description=None, container_type="Application"):
        self.containers.append({
            "name": name,
            "technology": technology,
            "description": description,
            "type": container_type
        })
        return self

    def add_relationship(self, source, target, label):
        self.relationships.append({"source": source, "target": target, "label": label})
        return self

    def from_json(self, json_data):
        if "containers" in json_data:
            for container in json_data["containers"]:
                self.add_container(
                    name=container["name"],
                    technology=container["technology"],
                    description=container.get("description"),
                    container_type=container.get("type", "Application")
                )
        if "relationships" in json_data:
            for rel in json_data["relationships"]:
                self.add_relationship(rel["from"], rel["to"], rel["label"])
        return self

    def to_json(self):
        return {
            "system_name": self.system_name,
            "containers": self.containers,
            "relationships": self.relationships
        }

    def generate(self):
        """Generate a C4 Level 2 Container Diagram."""
        output_dir = "diagrams_output"
        FilePath(output_dir).mkdir(exist_ok=True)

        fig, ax = plt.subplots(figsize=(14, 9))
        ax.set_facecolor('white')
        ax.axis('off')

        container_x = 0
        container_y = 0

        # Main system
        ax.text(container_x, container_y, self.system_name, fontsize=18, ha='center', va='center', bbox=dict(boxstyle="round,pad=1", edgecolor='black', facecolor='#e0f7fa'))

        # Position containers around main system
        radius = 6
        angle_step = 360 / max(len(self.containers), 1)
        positions = {}

        for idx, container in enumerate(self.containers):
            angle = idx * angle_step
            x = container_x + radius * 1.5 * np.cos(np.radians(angle))
            y = container_y + radius * np.sin(np.radians(angle))
            positions[container["name"]] = (x, y)
            ax.text(x, y, f"{container['name']}\n({container['technology']})", fontsize=10, ha='center', va='center', bbox=dict(boxstyle="round,pad=0.5", edgecolor='blue', facecolor='#e8f5e9'))

        # Draw relationships
        for rel in self.relationships:
            source = rel["source"]
            target = rel["target"]
            label = rel.get("label", "")
            if source in positions and target in positions:
                ax.annotate("",
                            xy=positions[target],
                            xytext=positions[source],
                            arrowprops=dict(arrowstyle="->", lw=1.5))
                mid_x = (positions[source][0] + positions[target][0]) / 2
                mid_y = (positions[source][1] + positions[target][1]) / 2
                ax.text(mid_x, mid_y, label, fontsize=8, ha='center', va='center')

        plt.title(f"C4 Level 2: Container Diagram - {self.system_name}", fontsize=16, pad=20)

        output_path = os.path.join(output_dir, f"{self.output_filename}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Diagram generated at {output_path}")
        return output_path

if __name__ == "__main__":
    diagram = C4ContainerDiagram("Enterprise Solution Architecture Platform")
    diagram.add_container("API Application", "Spring Boot")
    diagram.add_container("Data Warehouse", "Google BigQuery")
    diagram.add_container("Employee Portal", "React + Node.js")
    diagram.add_relationship("Employee Portal", "API Application", "Calls API")
    diagram.add_relationship("API Application", "Data Warehouse", "Pushes analytics data")
    diagram.generate()
