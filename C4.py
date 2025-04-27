import matplotlib
matplotlib.use('Agg')  # Force non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import json
from pathlib import Path as FilePath
from typing import List, Dict, Optional, Union, Tuple

class C4CodeDiagram:
    def __init__(self, component_name: str, output_filename: str = "c4_level4_code"):
        """
        Initialize a C4 Level 4 Code Diagram generator.
        
        Args:
            component_name: Name of the component being modeled
            output_filename: Base name for output files (without extension)
        """
        self.component_name = component_name
        self.output_filename = output_filename
        self.classes: List[Dict] = []
        self.associations: List[Dict] = []
        self.inheritances: List[Dict] = []
        self.interfaces: List[Dict] = []
        self._validate_filename(output_filename)

    def _validate_filename(self, filename: str) -> None:
        """Validate the output filename to prevent path traversal."""
        if not filename.isidentifier():
            raise ValueError("Output filename must be a valid identifier")

    def add_class(self, name: str, 
                 description: Optional[str] = None,
                 attributes: Optional[List[str]] = None,
                 methods: Optional[List[str]] = None,
                 class_type: str = "Class",
                 is_abstract: bool = False,
                 is_interface: bool = False) -> 'C4CodeDiagram':
        """
        Add a class to the diagram.
        
        Args:
            name: Name of the class
            description: Optional description
            attributes: List of attributes
            methods: List of methods
            class_type: Type of class (Class, Abstract, Interface, etc.)
            is_abstract: Whether the class is abstract
            is_interface: Whether the class is an interface
            
        Returns:
            self for method chaining
        """
        if not name:
            raise ValueError("Class name cannot be empty")
            
        self.classes.append({
            "name": name,
            "description": description,
            "attributes": attributes or [],
            "methods": methods or [],
            "type": class_type,
            "is_abstract": is_abstract,
            "is_interface": is_interface
        })
        return self

    def add_association(self, class1: str, class2: str, 
                       label: Optional[str] = None,
                       multiplicity: Optional[str] = None,
                       aggregation: bool = False,
                       composition: bool = False) -> 'C4CodeDiagram':
        """
        Add an association between classes.
        
        Args:
            class1: First class in association
            class2: Second class in association
            label: Optional label for the association
            multiplicity: Optional multiplicity (e.g., "1..*")
            aggregation: Whether this is an aggregation relationship
            composition: Whether this is a composition relationship
            
        Returns:
            self for method chaining
        """
        if not class1 or not class2:
            raise ValueError("Class names cannot be empty")
            
        self.associations.append({
            "class1": class1,
            "class2": class2,
            "label": label,
            "multiplicity": multiplicity,
            "aggregation": aggregation,
            "composition": composition
        })
        return self

    def add_inheritance(self, subclass: str, superclass: str) -> 'C4CodeDiagram':
        """
        Add an inheritance relationship.
        
        Args:
            subclass: The subclass
            superclass: The superclass
            
        Returns:
            self for method chaining
        """
        if not subclass or not superclass:
            raise ValueError("Class names cannot be empty")
            
        self.inheritances.append({
            "subclass": subclass,
            "superclass": superclass
        })
        return self

    def add_interface_implementation(self, implementor: str, interface: str) -> 'C4CodeDiagram':
        """
        Add an interface implementation relationship.
        
        Args:
            implementor: The implementing class
            interface: The interface being implemented
            
        Returns:
            self for method chaining
        """
        if not implementor or not interface:
            raise ValueError("Class names cannot be empty")
            
        self.interfaces.append({
            "implementor": implementor,
            "interface": interface
        })
        return self

    def from_json(self, json_data: Union[str, Dict]) -> 'C4CodeDiagram':
        """
        Load diagram configuration from JSON.
        
        Args:
            json_data: Either a JSON string or a dictionary
            
        Returns:
            self for method chaining
        """
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
            
        if "component_name" in json_data:
            self.component_name = json_data["component_name"]
            
        if "classes" in json_data:
            for cls in json_data["classes"]:
                self.add_class(
                    name=cls["name"],
                    description=cls.get("description"),
                    attributes=cls.get("attributes"),
                    methods=cls.get("methods"),
                    class_type=cls.get("type", "Class"),
                    is_abstract=cls.get("is_abstract", False),
                    is_interface=cls.get("is_interface", False)
                )
                
        if "associations" in json_data:
            for assoc in json_data["associations"]:
                self.add_association(
                    class1=assoc["class1"],
                    class2=assoc["class2"],
                    label=assoc.get("label"),
                    multiplicity=assoc.get("multiplicity"),
                    aggregation=assoc.get("aggregation", False),
                    composition=assoc.get("composition", False)
                )
                
        if "inheritances" in json_data:
            for inh in json_data["inheritances"]:
                self.add_inheritance(
                    subclass=inh["subclass"],
                    superclass=inh["superclass"]
                )
                
        if "interfaces" in json_data:
            for interface in json_data["interfaces"]:
                self.add_interface_implementation(
                    implementor=interface["implementor"],
                    interface=interface["interface"]
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
            "component_name": self.component_name,
            "classes": self.classes,
            "associations": self.associations,
            "inheritances": self.inheritances,
            "interfaces": self.interfaces
        }
        return json.dumps(data, indent=indent)

    def _get_class_color(self, class_type: str, is_abstract: bool, is_interface: bool) -> Tuple[str, str]:
        """Get color scheme based on class type."""
        if is_interface:
            return ('#f5f5f5', '#7b1fa2')  # Light gray / Purple
        if is_abstract:
            return ('#e3f2fd', '#0d47a1')  # Light blue / Dark blue
        if class_type == "Entity":
            return ('#e8f5e9', '#2e7d32')  # Light green / Dark green
        if class_type == "Service":
            return ('#fff3e0', '#ef6c00')  # Light orange / Dark orange
        if class_type == "Repository":
            return ('#fce4ec', '#c2185b')  # Light pink / Dark pink
        return ('#ffffff', '#424242')      # White / Dark gray

    def _get_class_font_style(self, is_abstract: bool, is_interface: bool) -> Dict:
        """Get font style based on class properties."""
        style = {"fontsize": 10}
        if is_abstract:
            style["fontstyle"] = "italic"
        if is_interface:
            style["fontstyle"] = "italic"
        return style

    def _draw_class(self, ax, x: float, y: float, cls: Dict) -> None:
        """Draw a class box with all its contents."""
        width = 3.5
        height = 2.5 + (len(cls["methods"]) * 0.2 + (len(cls["attributes"]) * 0.2)
        
        # Adjust height based on content
        if cls["description"]:
            height += 0.4
        if len(cls["methods"]) > 3 or len(cls["attributes"]) > 3:
            height += 0.5
            
        bg_color, border_color = self._get_class_color(
            cls["type"], cls["is_abstract"], cls["is_interface"])
        
        # Draw class box
        rect = patches.Rectangle(
            (x - width/2, y - height/2), width, height,
            linewidth=1.5, edgecolor=border_color, 
            facecolor=bg_color, alpha=0.9)
        ax.add_patch(rect)
        
        # Draw class name compartment
        name_comp_height = 0.6
        name_rect = patches.Rectangle(
            (x - width/2, y - height/2 + height - name_comp_height), 
            width, name_comp_height,
            linewidth=1.5, edgecolor=border_color, 
            facecolor=border_color, alpha=0.2)
        ax.add_patch(name_rect)
        
        # Add class name
        class_name = f"<<interface>>\n{cls['name']}" if cls["is_interface"] else cls["name"]
        ax.text(x, y + height/2 - name_comp_height/2, class_name, 
                ha='center', va='center', fontsize=11, 
                fontweight='bold', color='black')
        
        # Add description if present
        current_y = y + height/2 - name_comp_height - 0.3
        if cls["description"]:
            ax.text(x, current_y, cls["description"], 
                    ha='center', va='top', fontsize=8, wrap=True)
            current_y -= 0.4
            
        # Add attributes
        if cls["attributes"]:
            attributes_text = "\n".join(cls["attributes"])
            ax.text(x - width/2 + 0.1, current_y - 0.1, attributes_text,
                    ha='left', va='top', fontsize=9, family='monospace')
            current_y -= len(cls["attributes"]) * 0.2
            
        # Add methods
        if cls["methods"]:
            methods_text = "\n".join(cls["methods"])
            ax.text(x - width/2 + 0.1, current_y - 0.1, methods_text,
                    ha='left', va='top', fontsize=9, family='monospace')

    def _draw_relationship(self, ax, start: Tuple[float, float], end: Tuple[float, float], 
                          rel_type: str, label: Optional[str] = None,
                          multiplicity: Optional[str] = None) -> None:
        """Draw a relationship between classes."""
        arrow_style = {
            "arrowstyle": "->",
            "color": "#333333",
            "linewidth": 1.5,
            "shrinkA": 15,
            "shrinkB": 15
        }
        
        # Customize arrow based on relationship type
        if rel_type == "inheritance":
            arrow_style["arrowstyle"] = "-|>"
            arrow_style["color"] = "#0d47a1"
        elif rel_type == "interface":
            arrow_style["arrowstyle"] = "-|>"
            arrow_style["linestyle"] = "--"
            arrow_style["color"] = "#7b1fa2"
        elif rel_type == "aggregation":
            arrow_style["arrowstyle"] = "]-"
            arrow_style["color"] = "#ef6c00"
        elif rel_type == "composition":
            arrow_style["arrowstyle"] = "]-"
            arrow_style["color"] = "#c62828"
            
        ax.annotate("", xy=end, xytext=start, arrowprops=arrow_style)
        
        # Add label if provided
        if label or multiplicity:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            
            label_text = ""
            if label:
                label_text += label
            if multiplicity:
                if label_text:
                    label_text += "\n"
                label_text += multiplicity
                
            ax.text(mid_x, mid_y, label_text, fontsize=8, 
                   ha='center', va='center', 
                   bbox=dict(boxstyle="round,pad=0.2", 
                           facecolor='white', alpha=0.8))

    def generate(self, output_format: str = "png", dpi: int = 300) -> str:
        """
        Generate the C4 Level 4 Code Diagram.
        
        Args:
            output_format: Image format ('png', 'jpg', 'svg', 'pdf')
            dpi: Image resolution in dots per inch
            
        Returns:
            Path to the generated diagram file
        """
        if output_format not in ["png", "jpg", "svg", "pdf"]:
            raise ValueError(f"Unsupported output format: {output_format}")
            
        if not self.classes:
            raise ValueError("No classes added to diagram")

        output_dir = "diagrams_output"
        FilePath(output_dir).mkdir(exist_ok=True)

        fig, ax = plt.subplots(figsize=(16, 12))
        ax.set_facecolor('white')
        ax.axis('off')
        ax.set_title(f"C4 Level 4: Code Diagram - {self.component_name}", 
                    fontsize=18, pad=20, fontweight='bold')

        # Calculate positions using a force-directed layout
        positions = self._calculate_positions()

        # Draw all classes
        for cls in self.classes:
            if cls["name"] in positions:
                x, y = positions[cls["name"]]
                self._draw_class(ax, x, y, cls)

        # Draw all relationships
        for assoc in self.associations:
            if assoc["class1"] in positions and assoc["class2"] in positions:
                rel_type = "aggregation" if assoc["aggregation"] else (
                          "composition" if assoc["composition"] else "association")
                self._draw_relationship(
                    ax, positions[assoc["class1"]], positions[assoc["class2"]],
                    rel_type, assoc.get("label"), assoc.get("multiplicity"))

        # Draw inheritances
        for inh in self.inheritances:
            if inh["subclass"] in positions and inh["superclass"] in positions:
                self._draw_relationship(
                    ax, positions[inh["subclass"]], positions[inh["superclass"]],
                    "inheritance")

        # Draw interface implementations
        for interface in self.interfaces:
            if interface["implementor"] in positions and interface["interface"] in positions:
                self._draw_relationship(
                    ax, positions[interface["implementor"]], positions[interface["interface"]],
                    "interface")

        # Save diagram
        output_path = os.path.join(output_dir, f"{self.output_filename}.{output_format}")
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', format=output_format)
        plt.close()

        print(f"Diagram generated at {output_path}")
        return output_path

    def _calculate_positions(self) -> Dict[str, Tuple[float, float]]:
        """Calculate class positions using a simple force-directed layout."""
        # Simple grid layout for demonstration
        # In a real implementation, consider using a proper graph layout algorithm
        positions = {}
        num_classes = len(self.classes)
        cols = int(np.ceil(np.sqrt(num_classes)))
        rows = int(np.ceil(num_classes / cols))
        
        x_spacing = 6
        y_spacing = 5
        start_x = - (cols - 1) * x_spacing / 2
        start_y = (rows - 1) * y_spacing / 2
        
        for idx, cls in enumerate(self.classes):
            col = idx % cols
            row = idx // cols
            x = start_x + col * x_spacing
            y = start_y - row * y_spacing
            positions[cls["name"]] = (x, y)
            
        return positions


if __name__ == "__main__":
    # Example usage
    diagram = C4CodeDiagram("Order Processing Component")
    
    # Add classes with different types
    diagram.add_class(
        "OrderController",
        "Handles HTTP requests for orders",
        attributes=["orderService: OrderService", "paymentService: PaymentService"],
        methods=["createOrder(): Order", "cancelOrder(orderId: String): Boolean"],
        class_type="Controller"
    )
    
    diagram.add_class(
        "OrderService",
        "Core order processing logic",
        attributes=["orderRepository: OrderRepository"],
        methods=["createOrder(order: Order): Order", "findOrderById(id: String): Order"],
        class_type="Service"
    )
    
    diagram.add_class(
        "OrderRepository",
        "Database access for orders",
        attributes=["dataSource: DataSource"],
        methods=["save(order: Order): void", "findById(id: String): Order"],
        class_type="Repository"
    )
    
    diagram.add_class(
        "PaymentService",
        "Handles payment processing",
        methods=["processPayment(order: Order): PaymentResult", "refundPayment(orderId: String): Boolean"],
        class_type="Service"
    )
    
    diagram.add_class(
        "AbstractService",
        "Base service functionality",
        methods=["logEvent(event: String): void"],
        class_type="Service",
        is_abstract=True
    )
    
    diagram.add_class(
        "OrderValidator",
        "Validates order data",
        methods=["validate(order: Order): ValidationResult"],
        class_type="Utility"
    )
    
    diagram.add_class(
        "IEmailService",
        "Interface for email notifications",
        methods=["sendConfirmation(order: Order): void"],
        class_type="Interface",
        is_interface=True
    )
    
    # Add relationships
    diagram.add_association("OrderController", "OrderService", "uses")
    diagram.add_association("OrderController", "PaymentService", "uses")
    diagram.add_association("OrderService", "OrderRepository", "uses", multiplicity="1..*")
    diagram.add_association("OrderService", "OrderValidator", "validates with")
    diagram.add_association("OrderService", "IEmailService", "notifies via")
    diagram.add_association("OrderRepository", "DataSource", "uses", composition=True)
    
    # Add inheritance
    diagram.add_inheritance("OrderService", "AbstractService")
    diagram.add_inheritance("PaymentService", "AbstractService")
    
    # Add interface implementation
    diagram.add_interface_implementation("EmailServiceImpl", "IEmailService")
    
    # Generate diagram in multiple formats
    diagram.generate(output_format="png")
    diagram.generate(output_format="svg")
    
    # Export/import JSON
    json_data = diagram.to_json(indent=2)
    print("\nDiagram JSON representation:")
    print(json_data)
    
    # Create new diagram from JSON
    new_diagram = C4CodeDiagram("Temp Component").from_json(json_data)
    new_diagram.generate(output_format="pdf")