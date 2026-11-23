const codeEditor = document.getElementById("code");
const inputEditor = document.getElementById("input");
const runButton = document.getElementById("runButton");
const fileList = document.getElementById("fileList");
const currentFileLabel = document.getElementById("currentFile");
const newFileButton = document.getElementById("newFileButton");
const downloadButton = document.getElementById("downloadButton");
const deleteButton = document.getElementById("deleteButton");
const outputBox = document.getElementById("output");
const errorsBox = document.getElementById("errors");
const statusBox = document.getElementById("status");
const outputTab = document.getElementById("outputTab");
const errorsTab = document.getElementById("errorsTab");

const STORAGE_KEY = "velto_playground_project";

let files = {
    "main.vlt": 'name = "Velto"\n\nsay "Hello, " + name'
};

let activeFile = "main.vlt";
let currentSession = null;
let pollTimer = null;
let lastOutput = "";

function setStatus(message, type = "ready") {
    statusBox.textContent = message;

    statusBox.style.color =
        type === "error" ? "#f87171" :
        type === "running" ? "#facc15" : "#4ade80";
}

function saveProject() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
            files,
            activeFile
        }));

        setStatus("Project saved");
    } catch (error) {
        setStatus("Storage full or unavailable", "error");
    }
}

function loadProject() {
    try {
        const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));

        if (
            saved &&
            saved.files &&
            typeof saved.files === "object" &&
            saved.files["main.vlt"] !== undefined
        ) {
            files = saved.files;
            activeFile = saved.activeFile in files
                ? saved.activeFile
                : "main.vlt";
        }
    } catch (error) {
        setStatus("Could not load saved project", "error");
    }
}

function renderFiles() {
    fileList.innerHTML = "";

    Object.keys(files).forEach(name => {
        const button = document.createElement("button");
        button.className = "file-item";

        if (name === activeFile) {
            button.classList.add("active");
        }

        button.textContent = "📄 " + name;

        button.addEventListener("click", () => {
            switchFile(name);
        });

        fileList.appendChild(button);
    });
}

function switchFile(name) {
    if (!(name in files)) return;

    files[activeFile] = codeEditor.value;
    activeFile = name;

    codeEditor.value = files[name];
    currentFileLabel.textContent = name;

    renderFiles();

    localStorage.setItem(STORAGE_KEY, JSON.stringify({
        files,
        activeFile
    }));

    setStatus("Opened " + name);
}

function createFile() {
    const name = prompt("Enter file name (example: app.vlt)");

    if (!name) return;

    const cleanName = name.trim();

    if (
        !/^[a-zA-Z0-9_-]+\.vlt$/.test(cleanName)
    ) {
        alert("Use a valid .vlt file name.");
        return;
    }

    if (files[cleanName] !== undefined) {
        alert("File already exists.");
        return;
    }

    files[activeFile] = codeEditor.value;
    files[cleanName] = "";

    switchFile(cleanName);
    saveProject();
}

function deleteFile() {
    const names = Object.keys(files);

    if (names.length <= 1) {
        alert("At least one project file is required.");
        return;
    }

    if (!confirm("Delete " + activeFile + "?")) return;

    delete files[activeFile];

    activeFile = Object.keys(files)[0];
    codeEditor.value = files[activeFile];
    currentFileLabel.textContent = activeFile;

    renderFiles();
    saveProject();
}

function downloadFile() {
    files[activeFile] = codeEditor.value;

    const blob = new Blob(
        [files[activeFile]],
        { type: "text/plain;charset=utf-8" }
    );

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = activeFile;
    link.click();

    URL.revokeObjectURL(url);
    saveProject();
}

async function apiRequest(endpoint, data = {}) {
    const response = await fetch(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.error || "Request failed");
    }

    return result;
}

function showOutputTab() {
    outputBox.classList.remove("hidden");
    errorsBox.classList.add("hidden");
    outputTab.classList.add("active");
    errorsTab.classList.remove("active");
}

function showErrorsTab() {
    errorsBox.classList.remove("hidden");
    outputBox.classList.add("hidden");
    errorsTab.classList.add("active");
    outputTab.classList.remove("active");
}

function stopPolling() {
    if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
    }
}

async function pollOutput() {
    if (!currentSession) return;

    try {
        const result = await apiRequest("/poll", {
            session_id: currentSession
        });

        const newOutput = result.output || "";

        if (newOutput !== lastOutput) {
            lastOutput = newOutput;
            outputBox.textContent = newOutput || "Waiting for output...";
            outputBox.scrollTop = outputBox.scrollHeight;
            showOutputTab();
        }

        if (!result.running) {
            stopPolling();
            currentSession = null;
            runButton.disabled = false;

            if (result.exit_code === 0) {
                setStatus("Finished");
            } else {
                setStatus("Program error", "error");
                errorsBox.textContent =
                    newOutput || "Program exited with an error.";
            }
        }
    } catch (error) {
        stopPolling();
        currentSession = null;
        runButton.disabled = false;
        setStatus("Connection error", "error");
        errorsBox.textContent = error.message;
        showErrorsTab();
    }
}

async function runProgram() {
    if (currentSession) {
        setStatus("A program is already running", "error");
        return;
    }

    files[activeFile] = codeEditor.value;
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
        files,
        activeFile
    }));

    stopPolling();

    outputBox.textContent = "";
    errorsBox.textContent = "No errors.";
    lastOutput = "";

    showOutputTab();
    setStatus("Starting...", "running");
    runButton.disabled = true;

    try {
        const result = await apiRequest("/start", {
            code: codeEditor.value
        });

        currentSession = result.session_id;
        setStatus("Running...", "running");

        pollTimer = setInterval(pollOutput, 250);
        await pollOutput();
    } catch (error) {
        runButton.disabled = false;
        setStatus("Failed", "error");
        errorsBox.textContent = error.message;
        showErrorsTab();
    }
}

async function sendInput() {
    if (!currentSession) {
        setStatus("No running program", "error");
        return;
    }

    const value = inputEditor.value;

    if (!value) return;

    try {
        await apiRequest("/input", {
            session_id: currentSession,
            input: value
        });

        inputEditor.value = "";
        setStatus("Input sent");
    } catch (error) {
        setStatus("Input failed", "error");
        errorsBox.textContent = error.message;
        showErrorsTab();
    }
}

async function stopProgram() {
    if (!currentSession) return;

    const session = currentSession;

    stopPolling();
    currentSession = null;

    try {
        await apiRequest("/stop", {
            session_id: session
        });
    } catch (error) {
        errorsBox.textContent = error.message;
    }

    runButton.disabled = false;
    setStatus("Stopped", "error");
}

runButton.addEventListener("click", runProgram);
newFileButton.addEventListener("click", createFile);
downloadButton.addEventListener("click", downloadFile);
deleteButton.addEventListener("click", deleteFile);

outputTab.addEventListener("click", showOutputTab);
errorsTab.addEventListener("click", showErrorsTab);

codeEditor.addEventListener("input", () => {
    files[activeFile] = codeEditor.value;

    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
            files,
            activeFile
        }));
    } catch (error) {
        setStatus("Auto Save failed", "error");
    }
});

codeEditor.addEventListener("keydown", event => {
    if (event.key === "Tab") {
        event.preventDefault();

        const start = codeEditor.selectionStart;
        const end = codeEditor.selectionEnd;

        codeEditor.value =
            codeEditor.value.substring(0, start) +
            "    " +
            codeEditor.value.substring(end);

        codeEditor.selectionStart = start + 4;
        codeEditor.selectionEnd = start + 4;

        files[activeFile] = codeEditor.value;
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
            files,
            activeFile
        }));
    }
});

const inputActions = document.createElement("div");
inputActions.className = "input-actions";

const sendButton = document.createElement("button");
sendButton.textContent = "Send Input";
sendButton.className = "run-button";
sendButton.addEventListener("click", sendInput);

const stopButton = document.createElement("button");
stopButton.textContent = "Stop";
stopButton.className = "small-button";
stopButton.addEventListener("click", stopProgram);

inputActions.append(sendButton, stopButton);
inputEditor.parentElement.appendChild(inputActions);

inputEditor.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendInput();
    }
});

loadProject();
codeEditor.value = files[activeFile];
currentFileLabel.textContent = activeFile;

renderFiles();
setStatus("Ready");
