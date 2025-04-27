import matplotlib
matplotlib.use('Agg')  # Force non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
from pathlib import Path as FilePath

class C4CodeDiagram:
    def __init__(self, component_name, output_filename="c4_level4_code"):
        self.component_name = component_name
        self.output_filename = output_filename
        self.classes = []
        self.associations = []
        self.inheritances = []

    def add_class(self, name, description=None, attributes=None, methods=None):
        self.classes.append({
            "name": name,
            "description": description,
            "attributes": attributes or [],
            "methods": methods or []
        })
        return self

    def add_association(self, class1, class2, label=None):
        self.associations.append({"class1": class1, "class2": class2, "label": label})
        return self

    def add_inheritance(self, subclass, superclass):
        self.inheritances.append({"subclass": subclass, "superclass": superclass})
        return self

    def from_json(self, json_data):
        if "classes" in json_data:
            for cls in json_data["classes"]:
                self.add_class(
                    name=cls["name"],
                    description=cls.get("description"),
                    attributes=cls.get("attributes"),
                    methods=cls.get("methods")
                )
        if "associations" in json_data:
            for assoc in json_data["associations"]:
                self.add_association(assoc["class1"], assoc["class2"], assoc.get("label"))
        if "inheritances" in json_data:
            for inh in json_data["inheritances"]:
                self.add_inheritance(inh["subclass"], inh["superclass"])
        return self

    def to_json(self):
        return {
            "classes": self.classes,
            "associations": self.associations,
            "inheritances": self.inheritances
        }

    def generate(self):
        """Generate a simple C4 Level 4 Class Diagram."""
        output_dir = "diagrams_output"
        FilePath(output_dir).mkdir(exist_ok=True)

        fig, ax = plt.subplots(figsize=(14, 9))
        ax.set_facecolor('white')
        ax.axis('off')

        # Layout
        num_classes = len(self.classes)
        spacing_x = 5
        start_x = -spacing_x * (num_classes // 2)
        start_y = 0

        positions = {}
        x = start_x

        for cls in self.classes:
            positions[cls["name"]] = (x, start_y)
            self._draw_class(ax, x, start_y, cls)
            x += spacing_x

        # Draw associations
        for assoc in self.associations:
            if assoc["class1"] in positions and assoc["class2"] in positions:
                self._draw_arrow(ax, positions[assoc["class1"]], positions[assoc["class2"]], assoc.get("label"))

        # Draw inheritances
        for inh in self.inheritances:
            if inh["subclass"] in positions and inh["superclass"] in positions:
                self._draw_arrow(ax, positions[inh["subclass"]], positions[inh["superclass"]], "inherits")

        plt.title(f"C4 Level 4: Code Diagram - {self.component_name}", fontsize=16, pad=20)

        output_path = os.path.join(output_dir, f"{self.output_filename}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Diagram generated at {output_path}")
        return output_path

    def _draw_class(self, ax, x, y, cls):
        width = 3.0
        height = 2.0
        rect = patches.Rectangle((x - width/2, y - height/2), width, height,
                                  linewidth=1.5, edgecolor='black', facecolor='#d0e1f9', alpha=0.8)
        ax.add_patch(rect)
        ax.text(x, y+0.6, cls["name"], ha='center', va='bottom', fontsize=12, fontweight='bold')
        attributes = "\n".join(cls["attributes"]) if cls["attributes"] else ""
        methods = "\n".join(cls["methods"]) if cls["methods"] else ""
        ax.text(x, y-0.2, attributes + ("\n" + methods if methods else ""), ha='center', va='top', fontsize=9)

    def _draw_arrow(self, ax, start, end, label=None):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        ax.annotate("",
                    xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="->", lw=1.5, color='black'))
        if label:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            ax.text(mid_x, mid_y, label, fontsize=8, ha='center', va='center')

if __name__ == "__main__":
    diagram = C4CodeDiagram("Order Management Controller")

    diagram.add_class(
        "OrderController",
        "Handles order HTTP requests",
        attributes=["orderService: OrderService", "paymentService: PaymentService"],
        methods=["createOrder()", "cancelOrder()"]
    )

    diagram.add_class(
        "OrderService",
        "Business logic for orders",
        attributes=["orderRepository: OrderRepository"],
        methods=["createOrder()", "findOrderById()", "updateOrderStatus()"]
    )

    diagram.add_class(
        "OrderRepository",
        "Database access for orders",
        attributes=["dataSource: DataSource"],
        methods=["save()", "findById()"]
    )

    diagram.add_class(
        "PaymentService",
        "Handles payments",
        methods=["processPayment()", "refundPayment()"]
    )

    diagram.add_class(
        "BaseService",
        "Base class for services",
        methods=["logEvent()"]
    )

    diagram.add_association("OrderController", "OrderService", "uses")
    diagram.add_association("OrderController", "PaymentService", "uses")
    diagram.add_association("OrderService", "OrderRepository", "uses")

    diagram.add_inheritance("OrderService", "BaseService")
    diagram.add_inheritance("PaymentService", "BaseService")

    diagram.generate()
