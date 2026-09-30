let counts = {P1:0, P2:0, P3:0, P4:0};

function predictBug(){

    let desc = document.getElementById("desc").value.trim();

    if(desc === ""){
        alert("Please enter bug description!");
        return;
    }

    let loader = document.getElementById("loader");
    loader.style.display = "block";

    fetch("/predict", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({description: desc})
    })
    .then(res => res.json())
    .then(data => {

        loader.style.display = "none";

        let {severity, priority, confidence, solution} = data;

        // ================= RESULT =================
        document.getElementById("result").innerHTML = `
            <div class="result-box ${priority}">
                <h1>${severity}</h1>
                <p>Priority: ${priority}</p>
                <p>Confidence: ${confidence}%</p>
            </div>
        `;

        // ================= COUNTER =================
        counts[priority]++;
        document.getElementById("p1").innerText = counts.P1;
        document.getElementById("p2").innerText = counts.P2;
        document.getElementById("p3").innerText = counts.P3;
        document.getElementById("p4").innerText = counts.P4;

        // ================= ALERT SYSTEM =================
        let alertMsg = "";
        let icon = "";

        if(priority === "P1"){
            alertMsg = "Critical Bug! Fix immediately!";
            icon = "🚨";
        }
        else if(priority === "P2"){
            alertMsg = "High Priority Bug!";
            icon = "⚠️";
        }
        else if(priority === "P3"){
            alertMsg = "Medium Priority Bug";
            icon = "ℹ️";
        }
        else{
            alertMsg = "Low Priority Bug";
            icon = "✅";
        }
        let alertsdiv=document.getElementById("alerts");
        alertsdiv.innerHTML= `
            <div class="alert-card ${priority} alert-animate">
                ${icon} ${alertMsg}
            </div>
        `+alertsdiv.innerHTML.slice(0,200); 


        // ================= SOLUTION =================
let solutionHTML = "";

// 🔥 RULE BASED
if(solution && solution.source === "rule") {

    solution.data.forEach(r => {
        solutionHTML += `
            <div class="solution-card rule">
                <h4>🧠 ${r.type}</h4>
                <p class="root"><b>Root Cause:</b> ${r.root}</p>
                <ul class="fix-list">
                    ${r.fix.map(f => `<li>${f}</li>`).join("")}
                </ul>
            </div>
        `;
    });
}


else if(solution && solution.source === "hybrid") {

    let html = "";

    // Rule part
    solution.rule.forEach(r => {
        html += `
            <div class="solution-card rule">
                <h4>🧠 ${r.type}</h4>
                <p><b>Root Cause:</b> ${r.root}</p>
                <ul>
                    ${r.fix.map(f => `<li>${f}</li>`).join("")}
                </ul>
            </div>
        `;
    });

    // AI part
    html += `
        <div class="solution-card ai">
            <h4>🤖 AI Suggestion</h4>
            <p>${solution.ai.replace(/\n/g,"<br>")}</p>
        </div>
    `;

    solutionHTML = html;
}

// 🤖 AI ONLY
else if(solution && solution.source === "ai") {

    solutionHTML = `
        <div class="solution-card ai">
            <h4>🤖 AI Solution</h4>
            <p>${solution.data.replace(/\n/g,"<br>")}</p>
        </div>
    `;
}

//  FALLBACK
else {
    solutionHTML = `
        <div class="solution-card">
            <p>No solution found.</p>
        </div>
    `;
}

// FINAL RENDER
document.getElementById("solutions").innerHTML = solutionHTML;
    })
    .catch(err => {
        loader.style.display = "none";

        document.getElementById("alerts").innerHTML += `
            <div class="alert-card P1 alert-animate">
                ❌ Server Error. Try again.
            </div>
        `;
    });
}

// ================= CLEAR =================
function clearText() {
    document.getElementById("desc").value = ""; 
    document.getElementById("result").innerHTML = "";
    document.getElementById("alerts").innerHTML = "";
    document.getElementById("solutions").innerHTML = "";
}