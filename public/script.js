const code = document.getElementById("code");
const output = document.getElementById("output");
const run = document.getElementById("run");

run.addEventListener("click", async () => {
    output.textContent = "Running...";

    try {
        const response = await fetch("/api/run", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                code: code.value
            })
        });

        const data = await response.json();

        if (data.output !== undefined) {
            output.textContent = data.output;
        } else if (data.error !== undefined) {
            output.textContent = data.error;
        } else {
            output.textContent = "Unknown response";
        }
    } catch (error) {
        output.textContent = "Connection error";
    }
});
