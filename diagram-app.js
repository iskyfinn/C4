class DiagramApp {
    constructor(svgId) {
        this.svg = d3.select(`#${svgId}`);
        this.data = {
            c1: null,
            c2: null,
            c3: null,
            c4: null
        }; // Store data for each level
        this.positions = {
            c1: {},
            c2: {},
            c3: {},
            c4: {}
        }; // Store positions for each level
        this.currentLevel = "c3"; // Default, but MUST be set by your app!
        this.zoom = d3.zoom().on("zoom", (e) => {
            this.getDiagramGroup().attr("transform", e.transform);
        });
        this.svg.call(this.zoom);
    }

    setCurrentLevel(level) {
        this.currentLevel = level;
    }

    getCurrentData() {
        return this.data[this.currentLevel];
    }

    getCurrentPositions() {
        return this.positions[this.currentLevel];
    }

    getDiagramGroup() {
        // Helper to get the current diagram's group
        let groupId = `diagramGroup-${this.currentLevel}`;
        let group = this.svg.select(`#${groupId}`);
        if (group.empty()) {
            group = this.svg.append("g").attr("id", groupId);
        }
        return group;
    }

    initializePositions() {
        const data = this.getCurrentData();
        if (!data) return;

        this.positions[this.currentLevel] = {}; // Reset positions
        let x = 100,
            y = 100;

        if (this.currentLevel === "c1") {
            // Context Diagram layout
            if (data.systems) {
                data.systems.forEach((sys) => {
                    this.positions[this.currentLevel][sys.name] = { x, y };
                    x += 300;
                    if (x > 1000) {
                        x = 100;
                        y += 200;
                    }
                });
            }
            if (data.users) {
                data.users.forEach((user) => {
                    this.positions[this.currentLevel][user.name] = { x, y: y + 200 };
                    x += 200;
                });
            }
        } else if (this.currentLevel === "c2") {
            // Container Diagram layout
            if (data.containers) {
                data.containers.forEach((container) => {
                    this.positions[this.currentLevel][container.name] = { x, y };
                    x += 300;
                    if (x > 1000) {
                        x = 100;
                        y += 200;
                    }
                });
            }
        } else if (this.currentLevel === "c3") {
            // Component Diagram layout
            if (data.components) {
                data.components.forEach((comp) => {
                    this.positions[this.currentLevel][comp.name] = { x, y };
                    x += 300;
                    if (x > 1000) {
                        x = 100;
                        y += 200;
                    }
                });
            }
        } else if (this.currentLevel === "c4") {
            // Code Diagram layout (very basic example!)
            if (data.classes) {
                data.classes.forEach((cls) => {
                    this.positions[this.currentLevel][cls.name] = { x, y };
                    x += 250;
                    y += 150;
                });
            }
        }
    }

    renderDiagram() {
        const data = this.getCurrentData();
        if (!data) return;

        const g = this.getDiagramGroup();
        g.selectAll("*").remove();

        if (this.currentLevel === "c1") {
            // Render Context Diagram
            if (data.systems) {
                data.systems.forEach((sys) => {
                    const pos = this.getCurrentPositions()[sys.name];
                    if (pos) {
                        g.append("rect")
                            .attr("x", pos.x)
                            .attr("y", pos.y)
                            .attr("width", 200)
                            .attr("height", 120)
                            .attr("fill", "#bbdefb")
                            .attr("stroke", "#1976d2");
                        g.append("text")
                            .attr("x", pos.x + 100)
                            .attr("y", pos.y + 60)
                            .attr("text-anchor", "middle")
                            .attr("alignment-baseline", "middle")
                            .text(sys.name);
                    }
                });
            }
            if (data.users) {
                data.users.forEach((user) => {
                    const pos = this.getCurrentPositions()[user.name];
                    if (pos) {
                        g.append("circle")
                            .attr("cx", pos.x)
                            .attr("cy", pos.y)
                            .attr("r", 40)
                            .attr("fill", "#ffcc80")
                            .attr("stroke", "#e65100");
                        g.append("text")
                            .attr("x", pos.x)
                            .attr("y", pos.y)
                            .attr("text-anchor", "middle")
                            .attr("alignment-baseline", "middle")
                            .text(user.name);
                    }
                });
            }
            if (data.relationships) {
                data.relationships.forEach((rel) => {
                    const from = this.getCurrentPositions()[rel.from];
                    const to = this.getCurrentPositions()[rel.to];
                    if (from && to) {
                        g.append("line")
                            .attr("x1", from.x)
                            .attr("y1", from.y)
                            .attr("x2", to.x)
                            .attr("y2", to.y)
                            .attr("stroke", "#888")
                            .attr("stroke-width", 2)
                            .attr("marker-end", "url(#arrow)");
                        g.append("text")
                            .attr("x", (from.x + to.x) / 2)
                            .attr("y", (from.y + to.y) / 2)
                            .attr("text-anchor", "middle")
                            .text(rel.label);
                    }
                });
            }
        } else if (this.currentLevel === "c2") {
            // Render Container Diagram
            if (data.containers) {
                data.containers.forEach((container) => {
                    const pos = this.getCurrentPositions()[container.name];
                    if (pos) {
                        g.append("rect")
                            .attr("x", pos.x)
                            .attr("y", pos.y)
                            .attr("width", 200)
                            .attr("height", 120)
                            .attr("fill", "#bbdefb")
                            .attr("stroke", "#1976d2");
                        g.append("text")
                            .attr("x", pos.x + 100)
                            .attr("y", pos.y + 60)
                            .attr("text-anchor", "middle")
                            .attr("alignment-baseline", "middle")
                            .text(container.name);
                    }
                });
            }
            if (data.relationships) {
                data.relationships.forEach((rel) => {
                    const from = this.getCurrentPositions()[rel.from];
                    const to = this.getCurrentPositions()[rel.to];
                    if (from && to) {
                        g.append("line")
                            .attr("x1", from.x)
                            .attr("y1", from.y)
                            .attr("x2", to.x)
                            .attr("y2", to.y)
                            .attr("stroke", "#888")
                            .attr("stroke-width", 2)
                            .attr("marker-end", "url(#arrow)");
                        g.append("text")
                            .attr("x", (from.x + to.x) / 2)
                            .attr("y", (from.y + to.y) / 2)
                            .attr("text-anchor", "middle")
                            .text(rel.label);
                    }
                });
            }
        } else if (this.currentLevel === "c3") {
            // Render Component Diagram (original logic, but using getCurrentData)
            if (data.components) {
                data.components.forEach((comp) => {
                    const pos = this.getCurrentPositions()[comp.name];
                    if (pos) {
                        g.append("rect")
                            .attr("x", pos.x)
                            .attr("y", pos.y)
                            .attr("width", 180)
                            .attr("height", 100)
                            .attr("fill", "#e8f5e9")
                            .attr("stroke", "#333");

                        g.append("text")
                            .attr("x", pos.x + 90)
                            .attr("y", pos.y + 50)
                            .attr("text-anchor", "middle")
                            .attr("alignment-baseline", "middle")
                            .text(comp.name);
                    }
                });
            }
            if (data.relationships) {
                data.relationships.forEach((rel) => {
                    const from = this.getCurrentPositions()[rel.from];
                    const to = this.getCurrentPositions()[rel.to];
                    if (from && to) {
                        g.append("line")
                            .attr("x1", from.x + 90)
                            .attr("y1", from.y + 50)
                            .attr("x2", to.x + 90)
                            .attr("y2", to.y)
                            .attr("stroke", "#888")
                            .attr("stroke-width", 2)
                            .attr("marker-end", "url(#arrow)");
                        g.append("text")
                            .attr("x", (from.x + to.x) / 2)
                            .attr("y", (from.y + to.y) / 2)
                            .attr("text-anchor", "middle")
                            .text(rel.label);
                    }
                });
            }
        } else if (this.currentLevel === "c4") {
            // Render Code Diagram (very basic example)
            if (data.classes) {
                data.classes.forEach((cls) => {
                    const pos = this.getCurrentPositions()[cls.name];
                    if (pos) {
                        g.append("rect")
                            .attr("x", pos.x)
                            .attr("y", pos.y)
                            .attr("width", 150)
                            .attr("height", 80)
                            .attr("fill", "#fff3e0")
                            .attr("stroke", "#bf360c");

                        g.append("text")
                            .attr("x", pos.x + 75)
                            .attr("y", pos.y + 40)
                            .attr("text-anchor", "middle")
                            .attr("alignment-baseline", "middle")
                            .text(cls.name);
                    }
                });
            }
            if (data.associations) {
                data.associations.forEach((assoc) => {
                    const from = this.getCurrentPositions()[assoc.from];
                    const to = this.getCurrentPositions()[assoc.to];
                    if (from && to) {
                        g.append("line")
                            .attr("x1", from.x)
                            .attr("y1", from.y)
                            .attr("x2", to.x)
                            .attr("y2", to.y)
                            .attr("stroke", "#888")
                            .attr("stroke-width", 1)
                            .attr("marker-end", "url(#arrow)");
                        g.append("text")
                            .attr("x", (from.x + to.x) / 2)
                            .attr("y", (from.y + to.y) / 2 - 10)
                            .attr("text-anchor", "middle")
                            .text(assoc.label);
                    }
                });
            }
        }
    }
}

let app = new DiagramApp("diagramSVG"); // Initialize with the SVG ID