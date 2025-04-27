import matplotlib
matplotlib.use('Agg')  # Ensure headless plotting
import matplotlib.pyplot as plt
import numpy as np
import os
import json
from pathlib import Path as FilePath
from typing import List, Dict, Optional, Union, Tuple

class C4ComponentDiagram:
    def __init__(self, container_name: str, output_filename: str = "c4_level3_component"):
        """
        Initialize a C4 Component Diagram generator.
        
        Args:
            container_name: Name of the container being modeled
            output_filename: Base name for output files (without extension)
        """
        self.container_name = container_name
        self.output_filename = output_filename
        self.components: List[Dict] = []
        self.relationships: List[Dict] = []
        self._validate_filename(output_filename)

    def _validate_filename(self, filename: str) -> None:
        """Validate the output filename to prevent path traversal."""
        if not filename.isidentifier():
            raise ValueError("Output filename must be a valid identifier")

    def add_component(self, name: str, technology: str, 
                     description: Optional[str] = None,
                     component_type: str = "Service",
                     interface: Optional[str] = None) -> 'C4ComponentDiagram':
        """
        Add a component to the diagram.
        
        Args:
            name: Name of the component
            technology: Technology implementation
            description: Optional description
            component_type: Type of component (Service, Controller, etc.)
            interface: Optional interface specification
            
        Returns:
            self for method chaining
        """
        if not name or not technology:
            raise ValueError("Component name and technology cannot be empty")
            
        self.components.append({
            "name": name,
            "technology": technology,
            "description": description,
            "type": component_type,
            "interface": interface
        })
        return self

    def add_relationship(self, source: str, target: str, label: str,
                        protocol: Optional[str] = None,
                        bidirectional: bool = False,
                        async_comm: bool = False) -> 'C4ComponentDiagram':
        """
        Add a relationship between components.
        
        Args:
            source: Source component name
            target: Target component name
            label: Description of the relationship
            protocol: Communication protocol used
            bidirectional: Whether the relationship is bidirectional
            async_comm: Whether the communication is asynchronous
            
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
            "bidirectional": bidirectional,
            "async": async_comm
        })
        return self

    def from_json(self, json_data: Union[str, Dict]) -> 'C4ComponentDiagram':
        """
        Load diagram configuration from JSON.
        
        Args:
            json_data: Either a JSON string or a dictionary
            
        Returns:
            self for method chaining
        """
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
            
        if "container_name" in json_data:
            self.container_name = json_data["container_name"]
            
        if "components" in json_data:
            for comp in json_data["components"]:
                self.add_component(
                    name=comp["name"],
                    technology=comp["technology"],
                    description=comp.get("description"),
                    component_type=comp.get("type", "Service"),
                    interface=comp.get("interface")
                )
                
        if "relationships" in json_data:
            for rel in json_data["relationships"]:
                self.add_relationship(
                    source=rel["source"],
                    target=rel["target"],
                    label=rel["label"],
                    protocol=rel.get("protocol"),
                    bidirectional=rel.get("bidirectional", False),
                    async_comm=rel.get("async", False)
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
            "container_name": self.container_name,
            "components": self.components,
            "relationships": self.relationships
        }
        return json.dumps(data, indent=indent)

    def _get_component_color(self, component_type: str) -> Tuple[str, str]:
        """Get color scheme based on component type."""
        colors = {
            "Service": ('#e3f2fd', '#1565c0'),      # Light blue / Dark blue
            "Controller": ('#e8f5e9', '#2e7d32'),   # Light green / Dark green
            "Repository": ('#fff3e0', '#ef6c00'),   # Light orange / Dark orange
            "Client": ('#f3e5f5', '#7b1fa2'),       # Light purple / Dark purple
            "Utility": ('#e0f7fa', '#00838f'),      # Light teal / Dark teal
            "Gateway": ('#ffebee', '#c62828')       # Light red / Dark red
        }
        return colors.get(component_type, ('#f5f5f5', '#424242'))  # Default gray

    def generate(self, output_format: str = "png", dpi: int = 300) -> str:
        """
        Generate the C4 Level 3 Component Diagram.
        
        Args:
            output_format: Image format ('png', 'jpg', 'svg', 'pdf')
            dpi: Image resolution in dots per inch
            
        Returns:
            Path to the generated diagram file
        """
        if output_format not in ["png", "jpg", "svg", "pdf"]:
            raise ValueError(f"Unsupported output format: {output_format}")
            
        if not self.components:
            raise ValueError("No components added to diagram")

        output_dir = "diagrams_output"
        FilePath(output_dir).mkdir(exist_ok=True)

        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_facecolor('white')
        ax.axis('off')
        ax.set_title(f"C4 Level 3: Component Diagram - {self.container_name}", 
                    fontsize=18, pad=20, fontweight='bold')

        # Draw main container boundary
        container_box = plt.Rectangle((-8, -6), 16, 12, 
                                    linewidth=2, edgecolor='#333333',
                                    facecolor='#f5f5f5', alpha=0.3)
        ax.add_patch(container_box)
        ax.text(0, -6.5, self.container_name, fontsize=14, ha='center', va='top',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#333333'))

        # Position components in a smart layout
        positions = self._calculate_positions()

        # Draw components
        for comp in self.components:
            x, y = positions[comp["name"]]
            
            # Get component-specific styling
            bg_color, border_color = self._get_component_color(comp["type"])
            component_label = f"{comp['name']}\n[{comp['technology']}]"
            
            if comp.get("description"):
                component_label += f"\n{comp['description']}"
                
            if comp.get("interface"):
                component_label += f"\nInterface: {comp['interface']}"

            ax.text(x, y, component_label, fontsize=10, ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.6", edgecolor=border_color,
                           facecolor=bg_color, linewidth=1.5, alpha=0.9))

        # Draw relationships with labels
        for rel in self.relationships:
            source = rel["source"]
            target = rel["target"]
            
            if source not in positions or target not in positions:
                continue
                
            src_pos = positions[source]
            tgt_pos = positions[target]
            
            # Style arrow based on relationship properties
            arrow_style = dict(arrowstyle="->", color='#555555', 
                             linewidth=1.5, shrinkA=15, shrinkB=15)
            
            if rel.get("bidirectional"):
                arrow_style["arrowstyle"] = "<->"
            if rel.get("async"):
                arrow_style["arrowstyle"] = "-|>"
                arrow_style["linestyle"] = "--"
            
            # Adjust curvature for better visualization
            curvature = 0.2 if len(self.components) > 3 else 0
            arrow_style["connectionstyle"] = f"arc3,rad={curvature}"
            
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

    def _calculate_positions(self) -> Dict[str, Tuple[float, float]]:
        """Calculate optimal positions for components based on relationships."""
        positions = {}
        
        # Simple circular layout for now - could be enhanced with graph layout algorithms
        radius = 5
        angle_step = 360 / len(self.components)
        
        for idx, comp in enumerate(self.components):
            angle = idx * angle_step
            x = np.cos(np.radians(angle)) * radius
            y = np.sin(np.radians(angle)) * radius
            positions[comp["name"]] = (x, y)
            
        return positions


if __name__ == "__main__":
    # Example usage
    diagram = C4ComponentDiagram("Order Processing Microservice")
    
    # Add components with different types
    diagram.add_component("Order Controller", "Spring MVC", 
                         "Handles HTTP requests", "Controller", "REST API")
    diagram.add_component("Order Service", "Spring Service", 
                         "Core order logic", "Service")
    diagram.add_component("Payment Client", "Stripe SDK", 
                         "Handles payment processing", "Client")
    diagram.add_component("Inventory Client", "gRPC", 
                         "Communicates with inventory service", "Client")
    diagram.add_component("Order Repository", "JPA/Hibernate", 
                         "Persists order data", "Repository", "JPA Interface")
    diagram.add_component("Event Publisher", "Kafka", 
                         "Publishes order events", "Utility")
    
    # Add relationships with protocols and types
    diagram.add_relationship("Order Controller", "Order Service", 
                           "Delegates business logic", "Method call")
    diagram.add_relationship("Order Service", "Payment Client", 
                           "Processes payments", "HTTPS")
    diagram.add_relationship("Order Service", "Inventory Client", 
                           "Checks product availability", "gRPC")
    diagram.add_relationship("Order Service", "Order Repository", 
                           "Persists orders", "JPA", bidirectional=True)
    diagram.add_relationship("Order Service", "Event Publisher", 
                           "Publishes order events", "Kafka", async_comm=True)
    
    # Generate diagram in multiple formats
    diagram.generate(output_format="png")
    diagram.generate(output_format="svg")
    
    # Export/import JSON
    json_data = diagram.to_json(indent=2)
    print("\nDiagram JSON representation:")
    print(json_data)
    
    # Create new diagram from JSON
    new_diagram = C4ComponentDiagram("Temp Container").from_json(json_data)
    new_diagram.generate(output_format="pdf")