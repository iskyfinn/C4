import matplotlib
matplotlib.use('Agg')  # Ensure headless plotting
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path as FilePath

class C4ComponentDiagram:
    def __init__(self, container_name, output_filename="c4_level3_component"):
        self.container_name = container_name
        self.output_filename = output_filename
        self.components = []
        self.relationships = []

    def add_component(self, name, technology, description=None):
        self.components.append({
            "name": name,
            "technology": technology,
            "description": description
        })
        return self

    def add_relationship(self, source, target, label):
        self.relationships.append({"source": source, "target": target, "label": label})
        return self

    def from_json(self, json_data):
        if "components" in json_data:
            for comp in json_data["components"]:
                self.add_component(
                    name=comp["name"],
                    technology=comp["technology"],
                    description=comp.get("description")
                )
        if "relationships" in json_data:
            for rel in json_data["relationships"]:
                self.add_relationship(rel["from"], rel["to"], rel["label"])
        return self

    def to_json(self):
        return {
            "container_name": self.container_name,
            "components": self.components,
            "relationships": self.relationships
        }

    def generate(self):
        """Generate a C4 Level 3 Component Diagram."""
        output_dir = "diagrams_output"
        FilePath(output_dir).mkdir(exist_ok=True)

        fig, ax = plt.subplots(figsize=(14, 9))
        ax.set_facecolor('white')
        ax.axis('off')

        center_x, center_y = 0, 0

        # Draw main container boundary
        ax.text(center_x, center_y, self.container_name, fontsize=18, ha='center', va='center', bbox=dict(boxstyle="round,pad=1", edgecolor='black', facecolor='#f0f0f0'))

        # Position components around container
        radius = 5
        angle_step = 360 / max(len(self.components), 1)
        positions = {}

        for idx, comp in enumerate(self.components):
            angle = idx * angle_step
            x = center_x + radius * np.cos(np.radians(angle))
            y = center_y + radius * np.sin(np.radians(angle))
            positions[comp["name"]] = (x, y)
            ax.text(x, y, f"{comp['name']}\n({comp['technology']})", fontsize=10, ha='center', va='center', bbox=dict(boxstyle="round,pad=0.5", edgecolor='blue', facecolor='#e8f5e9'))

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

        plt.title(f"C4 Level 3: Component Diagram - {self.container_name}", fontsize=16, pad=20)

        output_path = os.path.join(output_dir, f"{self.output_filename}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Diagram generated at {output_path}")
        return output_path

if __name__ == "__main__":
    diagram = C4ComponentDiagram("API Application")
    diagram.add_component("Order Controller", "Spring MVC")
    diagram.add_component("Product Catalog Service", "Spring Service")
    diagram.add_component("User Authentication Service", "Spring Security")
    diagram.add_component("Payment Processing", "Stripe SDK")
    diagram.add_relationship("Order Controller", "Product Catalog Service", "Gets product details")
    diagram.add_relationship("Order Controller", "User Authentication Service", "Authenticates user")
    diagram.add_relationship("Order Controller", "Payment Processing", "Handles payments")
    diagram.generate()
