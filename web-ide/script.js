const editor = document.getElementById("editor");
const output = document.getElementById("output");
const runButton = document.getElementById("run");
const clearButton = document.getElementById("clear");

runButton.addEventListener("click", async () => {
    output.textContent = "Running...";

    try {
        const response = await fetch("/run", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                code: editor.value
            })
        });

        const data = await response.json();

        if (data.output !== undefined) {
            output.textContent = data.output;
            return;
        }

        if (data.error !== undefined) {
            output.textContent = data.error;
            return;
        }

        output.textContent = "Unknown response";
    } catch (error) {
        output.textContent = "Unable to connect to Velto server.";
    }
});

clearButton.addEventListener("click", () => {
    output.textContent = "";
});
