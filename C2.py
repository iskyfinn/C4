import matplotlib
matplotlib.use('Agg')  # Ensure no GUI errors
import matplotlib.pyplot as plt
import numpy as np
import os
import json
from pathlib import Path as FilePath
from typing import List, Dict, Optional, Union, Tuple

class C4ContainerDiagram:
    def __init__(self, system_name: str, output_filename: str = "c4_level2_container"):
        """
        Initialize a C4 Container Diagram generator.
        
        Args:
            system_name: Name of the main system being modeled
            output_filename: Base name for output files (without extension)
        """
        self.system_name = system_name
        self.output_filename = output_filename
        self.containers: List[Dict] = []
        self.relationships: List[Dict] = []
        self._validate_filename(output_filename)

    def _validate_filename(self, filename: str) -> None:
        """Validate the output filename to prevent path traversal."""
        if not filename.isidentifier():
            raise ValueError("Output filename must be a valid identifier")

    def add_container(self, name: str, technology: str, 
                     description: Optional[str] = None, 
                     container_type: str = "Application",
                     db_schema: Optional[str] = None) -> 'C4ContainerDiagram':
        """
        Add a container to the diagram.
        
        Args:
            name: Name of the container
            technology: Technology stack used
            description: Optional description
            container_type: Type of container (Application, Database, etc.)
            db_schema: For databases, optional schema diagram
            
        Returns:
            self for method chaining
        """
        if not name or not technology:
            raise ValueError("Container name and technology cannot be empty")
            
        self.containers.append({
            "name": name,
            "technology": technology,
            "description": description,
            "type": container_type,
            "db_schema": db_schema
        })
        return self

    def add_relationship(self, source: str, target: str, label: str,
                        protocol: Optional[str] = None,
                        bidirectional: bool = False) -> 'C4ContainerDiagram':
        """
        Add a relationship between containers.
        
        Args:
            source: Source container name
            target: Target container name
            label: Description of the relationship
            protocol: Communication protocol used
            bidirectional: Whether the relationship is bidirectional
            
        Returns:
            self for method chaining
        """
        if not all([source, target, label]):
            raise ValueError("Source, target and label cannot be empty")
            
        self.relationships.append({
            "source": source,
            "target": target,
            "label": label,
            "protocol": protocol,
            "bidirectional": bidirectional
        })
        return self

    def from_json(self, json_data: Union[str, Dict]) -> 'C4ContainerDiagram':
        """
        Load diagram configuration from JSON.
        
        Args:
            json_data: Either a JSON string or a dictionary
            
        Returns:
            self for method chaining
        """
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
            
        if "system_name" in json_data:
            self.system_name = json_data["system_name"]
            
        if "containers" in json_data:
            for container in json_data["containers"]:
                self.add_container(
                    name=container["name"],
                    technology=container["technology"],
                    description=container.get("description"),
                    container_type=container.get("type", "Application"),
                    db_schema=container.get("db_schema")
                )
                
        if "relationships" in json_data:
            for rel in json_data["relationships"]:
                self.add_relationship(
                    source=rel["source"],
                    target=rel["target"],
                    label=rel["label"],
                    protocol=rel.get("protocol"),
                    bidirectional=rel.get("bidirectional", False)
                )
        return self

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        Export diagram configuration to JSON.
        
        Args:
            indent: JSON indentation level (None for compact)
            
        Returns:
            JSON string representation
        """
        data = {
            "system_name": self.system_name,
            "containers": self.containers,
            "relationships": self.relationships
        }
        return json.dumps(data, indent=indent)

    def _get_container_color(self, container_type: str) -> Tuple[str, str]:
        """Get color scheme based on container type."""
        colors = {
            "Application": ('#e3f2fd', '#1565c0'),  # Light blue / Dark blue
            "Database": ('#e8f5e9', '#2e7d32'),    # Light green / Dark green
            "Queue": ('#fff3e0', '#ef6c00'),       # Light orange / Dark orange
            "Browser": ('#f3e5f5', '#7b1fa2'),     # Light purple / Dark purple
            "Mobile": ('#e0f7fa', '#00838f'),      # Light teal / Dark teal
            "API": ('#ffebee', '#c62828')          # Light red / Dark red
        }
        return colors.get(container_type, ('#f5f5f5', '#424242'))  # Default gray

    def generate(self, output_format: str = "png", dpi: int = 300) -> str:
        """
        Generate the C4 Level 2 Container Diagram.
        
        Args:
            output_format: Image format ('png', 'jpg', 'svg', 'pdf')
            dpi: Image resolution in dots per inch
            
        Returns:
            Path to the generated diagram file
        """
        if output_format not in ["png", "jpg", "svg", "pdf"]:
            raise ValueError(f"Unsupported output format: {output_format}")
            
        if not self.containers:
            raise ValueError("No containers added to diagram")

        output_dir = "diagrams_output"
        FilePath(output_dir).mkdir(exist_ok=True)

        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_facecolor('white')
        ax.axis('off')
        ax.set_title(f"C4 Level 2: Container Diagram - {self.system_name}", 
                    fontsize=18, pad=20, fontweight='bold')

        # Main system properties
        system_box_style = dict(boxstyle="round,pad=1.2", edgecolor='black', 
                               facecolor='#bbdefb', linewidth=2)
        ax.text(0, 0, self.system_name, fontsize=16, ha='center', va='center',
               fontweight='bold', bbox=system_box_style)

        # Position containers in a circle around main system
        radius = 6
        angle_step = 360 / len(self.containers)
        positions = {}

        for idx, container in enumerate(self.containers):
            angle = idx * angle_step
            x = np.cos(np.radians(angle)) * radius
            y = np.sin(np.radians(angle)) * radius
            
            positions[container["name"]] = (x, y)
            
            # Get container-specific styling
            bg_color, border_color = self._get_container_color(container["type"])
            container_label = f"{container['name']}\n[{container['technology']}]"
            
            if container.get("description"):
                container_label += f"\n{container['description']}"
                
            if container.get("db_schema"):
                container_label += f"\nSchema: {container['db_schema']}"

            ax.text(x, y, container_label, fontsize=10, ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.6", edgecolor=border_color,
                           facecolor=bg_color, linewidth=1.5))

        # Draw relationships with labels
        for rel in self.relationships:
            source = rel["source"]
            target = rel["target"]
            
            if source not in positions or target not in positions:
                continue
                
            src_pos = positions[source]
            tgt_pos = positions[target]
            
            # Adjust arrow curvature based on positions
            curvature = 0.2 if len(self.containers) > 3 else 0
            arrow_style = dict(arrowstyle="->", color='#555555', 
                             linewidth=1.5, shrinkA=15, shrinkB=15,
                             connectionstyle=f"arc3,rad={curvature}")
            
            if rel.get("bidirectional"):
                arrow_style["arrowstyle"] = "<->"
            
            ax.annotate("", xy=tgt_pos, xytext=src_pos, arrowprops=arrow_style)
            
            # Add relationship label with protocol if specified
            mid_x = (src_pos[0] + tgt_pos[0]) / 2
            mid_y = (src_pos[1] + tgt_pos[1]) / 2
            
            label_text = rel["label"]
            if rel.get("protocol"):
                label_text += f" ({rel['protocol']})"
                
            ax.text(mid_x, mid_y, label_text, fontsize=9, ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))

        # Save diagram
        output_path = os.path.join(output_dir, f"{self.output_filename}.{output_format}")
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', format=output_format)
        plt.close()

        print(f"Diagram generated at {output_path}")
        return output_path


if __name__ == "__main__":
    # Example usage
    diagram = C4ContainerDiagram("Online Banking System")
    
    # Add containers with different types
    diagram.add_container("Web Application", "React + Spring Boot", 
                        "Customer-facing web app", "Application")
    diagram.add_container("Mobile App", "React Native", 
                        "iOS/Android mobile app", "Mobile")
    diagram.add_container("API Gateway", "Spring Cloud Gateway", 
                        "Routes API requests", "API")
    diagram.add_container("Customer Database", "PostgreSQL", 
                        "Stores customer data", "Database", "customer_schema")
    diagram.add_container("Transaction Queue", "RabbitMQ", 
                        "Async transaction processing", "Queue")
    
    # Add relationships with protocols
    diagram.add_relationship("Web Application", "API Gateway", 
                           "Makes API calls", "HTTPS")
    diagram.add_relationship("Mobile App", "API Gateway", 
                           "Makes API calls", "HTTPS")
    diagram.add_relationship("API Gateway", "Customer Database", 
                           "Reads/writes data", "JDBC")
    diagram.add_relationship("API Gateway", "Transaction Queue", 
                           "Pushes transactions", "AMQP")
    diagram.add_relationship("Transaction Queue", "Customer Database", 
                           "Updates balances", "JDBC", bidirectional=True)
    
    # Generate diagram in multiple formats
    diagram.generate(output_format="png")
    diagram.generate(output_format="svg")
    
    # Export/import JSON
    json_data = diagram.to_json(indent=2)
    print("\nDiagram JSON representation:")
    print(json_data)
    
    # Create new diagram from JSON
    new_diagram = C4ContainerDiagram("Temp System").from_json(json_data)
    new_diagram.generate(output_format="pdf")