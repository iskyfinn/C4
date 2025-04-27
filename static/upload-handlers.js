const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const levelSelect = document.getElementById('levelSelect');
const statusDiv = document.getElementById('status');
const diagramSVG = document.getElementById('diagramSVG');

const app = new DiagramApp("diagramSVG"); // Initialize DiagramApp

uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const file = fileInput.files[0];
    const level = levelSelect.value;

    if (!file || !level) {
        statusDiv.className = 'error';
        statusDiv.innerText = "Please select a file and a C4 level.";
        return;
    }

    const formData = new FormData();
    formData.append('file', file, file.name);
    formData.append('level', level);

    statusDiv.className = 'loading';
    statusDiv.innerText = "Uploading and processing...";

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            let errorText = "Upload failed.";
            try {
                errorText = await response.text();
            } catch (e) {
                console.error("Could not get response text", e);
            }
            throw new Error(`HTTP error ${response.status}: ${errorText}`);
        }

        const data = await response.json();

        if (data.c4Data) {
            console.log("Received c4Data:", data.c4Data);

            statusDiv.className = 'success';
            statusDiv.innerText = data.message || "Diagram parsed successfully!";

            // *** RENDER THE DIAGRAM ***
            app.setCurrentLevel(level);
            app.data[level] = data.c4Data;
            app.initializePositions();
            app.renderDiagram();
            // *************************

        } else if (data.error) {
            statusDiv.className = 'error';
            statusDiv.innerText = "Error: " + data.error;
        } else {
            statusDiv.className = 'error';
            statusDiv.innerText = "Unexpected response from server.";
        }

    } catch (error) {
        console.error("Upload failed:", error);
        statusDiv.className = 'error';
        statusDiv.innerText = "Upload failed: " + error.message;
    }
});