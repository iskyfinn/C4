import matplotlib
matplotlib.use('Agg')  # Prevent GUI backend issues
import matplotlib.pyplot as plt
import os
import json
from pathlib import Path as FilePath
from typing import List, Dict, Optional, Union

class C4ContextDiagram:
    def __init__(self, system_name: str, output_filename: str = "c4_level1_context"):
        """
        Initialize a C4 Context Diagram generator.
        
        Args:
            system_name: Name of the main system/software being modeled
            output_filename: Base name for output files (without extension)
        """
        self.system_name = system_name
        self.output_filename = output_filename
        self.users: List[Dict] = []
        self.external_systems: List[Dict] = []
        self.relationships: List[Dict] = []
        self._validate_filename(output_filename)

    def _validate_filename(self, filename: str) -> None:
        """Validate the output filename to prevent path traversal."""
        if not filename.isidentifier():
            raise ValueError("Output filename must be a valid identifier")

    def add_user(self, name: str, description: Optional[str] = None, role: Optional[str] = None) -> 'C4ContextDiagram':
        """
        Add a user/persona to the diagram.
        
        Args:
            name: Name of the user/role
            description: Optional description of the user
            role: Optional role of the user (e.g., "Admin", "Customer")
            
        Returns:
            self for method chaining
        """
        if not name:
            raise ValueError("User name cannot be empty")
        self.users.append({
            "name": name,
            "description": description,
            "role": role
        })
        return self

    def add_external_system(self, name: str, description: Optional[str] = None, protocol: Optional[str] = None) -> 'C4ContextDiagram':
        """
        Add an external system to the diagram.
        
        Args:
            name: Name of the external system
            description: Optional description of the system
            protocol: Optional protocol used (e.g., "HTTP", "gRPC")
            
        Returns:
            self for method chaining
        """
        if not name:
            raise ValueError("External system name cannot be empty")
        self.external_systems.append({
            "name": name,
            "description": description,
            "protocol": protocol
        })
        return self

    def add_relationship(self, source: str, target: str, label: str, bidirectional: bool = False) -> 'C4ContextDiagram':
        """
        Add a relationship between components.
        
        Args:
            source: Source component name
            target: Target component name
            label: Description of the relationship
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
            "bidirectional": bidirectional
        })
        return self

    def from_json(self, json_data: Union[str, Dict]) -> 'C4ContextDiagram':
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
            
        if "users" in json_data:
            for user in json_data["users"]:
                self.add_user(
                    user["name"],
                    user.get("description"),
                    user.get("role")
                )
                
        if "external_systems" in json_data:
            for system in json_data["external_systems"]:
                self.add_external_system(
                    system["name"],
                    system.get("description"),
                    system.get("protocol")
                )
                
        if "relationships" in json_data:
            for rel in json_data["relationships"]:
                self.add_relationship(
                    rel["source"],
                    rel["target"],
                    rel["label"],
                    rel.get("bidirectional", False)
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
            "users": self.users,
            "external_systems": self.external_systems,
            "relationships": self.relationships
        }
        return json.dumps(data, indent=indent)

    def generate(self, output_format: str = "png", dpi: int = 300) -> str:
        """
        Generate the C4 Level 1 Context Diagram.
        
        Args:
            output_format: Image format ('png', 'jpg', 'svg', 'pdf')
            dpi: Image resolution in dots per inch
            
        Returns:
            Path to the generated diagram file
        """
        if output_format not in ["png", "jpg", "svg", "pdf"]:
            raise ValueError(f"Unsupported output format: {output_format}")
            
        output_dir = "diagrams_output"
        FilePath(output_dir).mkdir(exist_ok=True)

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_facecolor('white')
        ax.axis('off')
        ax.set_title(f"Context Diagram: {self.system_name}", fontsize=18, pad=20)

        # Calculate positions dynamically based on number of elements
        max_elements = max(len(self.users), len(self.external_systems), 1)
        vertical_spacing = 10 / max(1, max_elements)

        # Main system properties
        system_box_style = dict(boxstyle="round,pad=0.8", edgecolor='black', facecolor='#f0f0f0', linewidth=2)
        system_font_style = dict(fontsize=16, ha='center', va='center', fontweight='bold')

        # Draw main system in the center
        ax.text(0, 0, self.system_name, **system_font_style, bbox=system_box_style)

        # Draw users on the left
        for idx, user in enumerate(self.users):
            y_offset = (idx - len(self.users)/2) * vertical_spacing
            user_label = f"{user['name']}\n({user['role']})" if user.get('role') else user['name']
            
            ax.text(-5, y_offset, user_label, fontsize=12, ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.5", edgecolor='blue', facecolor='#e0f7fa'))
            
            # Draw relationship arrow
            arrow_style = dict(arrowstyle="->", color='blue', linewidth=1.5)
            ax.annotate("", xy=(-1.5, y_offset*0.2), xytext=(-4, y_offset),
                        arrowprops=arrow_style)
            
            # Add relationship label if exists
            rel_label = self._find_relationship_label(user['name'], self.system_name)
            if rel_label:
                ax.text(-2.5, y_offset*0.6, rel_label, fontsize=10, ha='center', va='center')

        # Draw external systems on the right
        for idx, system in enumerate(self.external_systems):
            y_offset = (idx - len(self.external_systems)/2) * vertical_spacing
            system_label = f"{system['name']}"
            if system.get('protocol'):
                system_label += f"\n({system['protocol']})"
                
            ax.text(5, y_offset, system_label, fontsize=12, ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.5", edgecolor='green', facecolor='#e8f5e9'))
            
            # Draw relationship arrow
            arrow_style = dict(arrowstyle="->", color='green', linewidth=1.5)
            direction = 1  # Default direction (system -> external)
            
            # Find relationship to determine direction
            rel = self._find_relationship(self.system_name, system['name'])
            if rel and rel.get('bidirectional'):
                arrow_style['arrowstyle'] = "<->"
            elif rel and rel['source'] == system['name']:
                direction = -1  # Reverse direction (external -> system)
            
            ax.annotate("", xy=(1.5*direction, y_offset*0.2), xytext=(4*direction, y_offset),
                        arrowprops=arrow_style)
            
            # Add relationship label if exists
            if rel:
                ax.text(2.5*direction, y_offset*0.6, rel['label'], fontsize=10, ha='center', va='center')

        # Save diagram
        output_path = os.path.join(output_dir, f"{self.output_filename}.{output_format}")
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', format=output_format)
        plt.close()

        print(f"Diagram generated at {output_path}")
        return output_path

    def _find_relationship(self, source: str, target: str) -> Optional[Dict]:
        """Find a relationship between two components."""
        for rel in self.relationships:
            if rel['source'] == source and rel['target'] == target:
                return rel
            if rel.get('bidirectional') and rel['source'] == target and rel['target'] == source:
                return rel
        return None

    def _find_relationship_label(self, source: str, target: str) -> Optional[str]:
        """Find the label of a relationship between two components."""
        rel = self._find_relationship(source, target)
        return rel['label'] if rel else None


if __name__ == "__main__":
    # Example usage
    diagram = C4ContextDiagram("Enterprise Solution Architecture Platform")
    
    # Add users with roles
    diagram.add_user("Solution Architect", "Designs system architectures", "Admin")
    diagram.add_user("Business Analyst", "Defines requirements", "User")
    
    # Add external systems with protocols
    diagram.add_external_system("Oracle Financials", "Enterprise financial system", "SOAP")
    diagram.add_external_system("LDAP Server", "Authentication service", "LDAP")
    
    # Add relationships (some bidirectional)
    diagram.add_relationship("Solution Architect", "Enterprise Solution Architecture Platform", "Designs architecture")
    diagram.add_relationship("Business Analyst", "Enterprise Solution Architecture Platform", "Submits requirements")
    diagram.add_relationship("Enterprise Solution Architecture Platform", "Oracle Financials", "Gets financial data")
    diagram.add_relationship("Enterprise Solution Architecture Platform", "LDAP Server", "Authenticates users", bidirectional=True)
    
    # Generate diagram in multiple formats
    diagram.generate(output_format="png")
    diagram.generate(output_format="svg")
    
    # Export/import JSON
    json_data = diagram.to_json(indent=2)
    print("\nDiagram JSON representation:")
    print(json_data)
    
    # Create new diagram from JSON
    new_diagram = C4ContextDiagram("Temp System").from_json(json_data)
    new_diagram.generate(output_format="pdf")



# python C1.py
