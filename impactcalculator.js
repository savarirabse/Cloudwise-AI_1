/* =========================================================
   CLOUDWISE AI
   IMPACT CALCULATOR ENGINE
   ========================================================= */


/* =========================================================
   DOM ELEMENTS
   ========================================================= */

const calculateButton =
    document.getElementById("calculateButton");

const clearButton =
    document.getElementById("clearButton");

const resultsPlaceholder =
    document.getElementById("resultsPlaceholder");

const calculatedResults =
    document.getElementById("calculatedResults");

const monthlySavings =
    document.getElementById("monthlySavings");

const annualSavings =
    document.getElementById("annualSavings");

const savingsPercent =
    document.getElementById("savingsPercent");

const impactScore =
    document.getElementById("impactScore");

const scoreFill =
    document.getElementById("scoreFill");

const scoreDescription =
    document.getElementById("scoreDescription");

const roiValue =
    document.getElementById("roiValue");

const paybackValue =
    document.getElementById("paybackValue");

const insightsContainer =
    document.getElementById("insightsContainer");


/* =========================================================
   INPUTS
   ========================================================= */

const inputIds = [

    "monthlySpend",
    "resources",
    "applications",
    "cloudTeam",
    "criticalApps",
    "computeCost",
    "storageCost",
    "databaseCost",
    "networkCost",
    "utilization",
    "downtime",
    "securityFindings",
    "unusedResources"

];


/* =========================================================
   GET NUMBER
   ========================================================= */

function getNumber(id) {

    const element =
        document.getElementById(id);

    if (!element || element.value === "") {
        return 0;
    }

    const value =
        Number(element.value);

    return Number.isFinite(value)
        ? Math.max(0, value)
        : 0;
}


/* =========================================================
   FORMAT CURRENCY
   ========================================================= */

function formatCurrency(value) {

    if (!Number.isFinite(value)) {
        return "₹0";
    }

    if (value >= 10000000) {

        return "₹" +
            (value / 10000000)
                .toFixed(2) +
            " Cr";

    }

    if (value >= 100000) {

        return "₹" +
            (value / 100000)
                .toFixed(2) +
            "L";

    }

    if (value >= 1000) {

        return "₹" +
            (value / 1000)
                .toFixed(1) +
            "K";

    }

    return "₹" +
        Math.round(value)
            .toLocaleString("en-IN");

}


/* =========================================================
   GET SELECTED CLOUD
   ========================================================= */

function getSelectedCloud() {

    const selected =
        document.querySelector(
            'input[name="cloud"]:checked'
        );

    return selected
        ? selected.value
        : "aws";

}


/* =========================================================
   GET OBJECTIVES
   ========================================================= */

function getObjectives() {

    return Array.from(
        document.querySelectorAll(
            '.objective-option input:checked'
        )
    ).map(
        checkbox => checkbox.value
    );

}


/* =========================================================
   CALCULATE BASE SAVINGS RATE
   =========================================================

   This is an ESTIMATION MODEL for the prototype.

   It should eventually be replaced by Cloudwise's
   production recommendation engine.
   ========================================================= */

function calculateSavingsRate(data) {


    /*
     * Starting optimization opportunity.
     */

    let rate = 0.08;


    /*
     * Utilization adjustment.
     *
     * Lower utilization generally indicates
     * more potential optimization.
     */

    if (data.utilization < 40) {

        rate += 0.07;

    } else if (data.utilization < 60) {

        rate += 0.05;

    } else if (data.utilization < 75) {

        rate += 0.03;

    } else if (data.utilization >= 90) {

        rate -= 0.02;

    }


    /*
     * Idle resources.
     */

    if (data.resources > 0) {

        const idleRatio =
            data.unusedResources /
            data.resources;

        if (idleRatio >= 0.20) {

            rate += 0.06;

        } else if (idleRatio >= 0.10) {

            rate += 0.04;

        } else if (idleRatio >= 0.05) {

            rate += 0.02;

        }

    }


    /*
     * Cloud maturity.
     */

    switch (data.maturity) {

        case "starting":

            rate += 0.05;

            break;

        case "developing":

            rate += 0.03;

            break;

        case "established":

            rate += 0.01;

            break;

        case "optimized":

            rate -= 0.02;

            break;

    }


    /*
     * Cost objective.
     */

    if (
        data.objectives.includes("cost")
    ) {

        rate += 0.02;

    }


    /*
     * Performance objective.
     */

    if (
        data.objectives.includes("performance")
    ) {

        rate += 0.01;

    }


    /*
     * Sustainability objective.
     */

    if (
        data.objectives.includes("sustainability")
    ) {

        rate += 0.01;

    }


    /*
     * Keep result within reasonable
     * prototype range.
     */

    return Math.min(
        Math.max(rate, 0.03),
        0.30
    );

}


/* =========================================================
   IMPACT SCORE
   ========================================================= */

function calculateImpactScore(data) {

    let score = 50;


    /*
     * Utilization.
     */

    if (data.utilization < 40) {

        score += 18;

    } else if (data.utilization < 60) {

        score += 13;

    } else if (data.utilization < 75) {

        score += 7;

    } else if (data.utilization >= 90) {

        score -= 5;

    }


    /*
     * Idle resources.
     */

    if (data.resources > 0) {

        const idleRatio =
            data.unusedResources /
            data.resources;

        if (idleRatio >= 0.20) {

            score += 15;

        } else if (idleRatio >= 0.10) {

            score += 10;

        } else if (idleRatio >= 0.05) {

            score += 5;

        }

    }


    /*
     * Security findings.
     */

    if (data.securityFindings >= 50) {

        score += 10;

    } else if (data.securityFindings >= 20) {

        score += 7;

    } else if (data.securityFindings >= 5) {

        score += 3;

    }


    /*
     * Downtime.
     */

    if (data.downtime >= 10) {

        score += 10;

    } else if (data.downtime >= 5) {

        score += 7;

    } else if (data.downtime >= 2) {

        score += 3;

    }


    /*
     * Maturity.
     */

    switch (data.maturity) {

        case "starting":
            score += 7;
            break;

        case "developing":
            score += 5;
            break;

        case "established":
            score += 2;
            break;

        case "optimized":
            score -= 5;
            break;

    }


    return Math.min(
        Math.max(Math.round(score), 0),
        100
    );

}


/* =========================================================
   SCORE DESCRIPTION
   ========================================================= */

function getScoreDescription(score) {

    if (score >= 85) {

        return "Very high optimization potential identified across your environment.";

    }

    if (score >= 70) {

        return "Strong optimization potential identified across your environment.";

    }

    if (score >= 50) {

        return "Moderate opportunities exist across your cloud environment.";

    }

    return "Your environment appears relatively optimized based on the information provided.";

}


/* =========================================================
   GENERATE INSIGHTS
   ========================================================= */

function generateInsights(data) {

    const insights = [];


    /*
     * Cost
     */

    if (
        data.unusedResources > 0 ||
        data.utilization < 70
    ) {

        insights.push({

            icon: "₹",

            className: "green",

            title: "Cost Optimization",

            text:
                "Idle and underutilized resources may provide opportunities for reducing cloud spend."

        });

    }


    /*
     * Security
     */

    if (data.securityFindings > 0) {

        insights.push({

            icon: "◈",

            className: "red",

            title: "Security",

            text:
                `${data.securityFindings} open security findings were provided for analysis.`

        });

    } else {

        insights.push({

            icon: "◈",

            className: "red",

            title: "Security",

            text:
                "No open security findings were reported."

        });

    }


    /*
     * Reliability
     */

    if (data.downtime >= 5) {

        insights.push({

            icon: "♢",

            className: "purple",

            title: "Reliability",

            text:
                `${data.downtime} hours of monthly downtime indicates an opportunity to improve reliability.`

        });

    } else {

        insights.push({

            icon: "♢",

            className: "purple",

            title: "Reliability",

            text:
                "Your reported downtime is relatively low; reliability optimization can still be assessed."

        });

    }


    /*
     * Utilization
     */

    if (data.utilization < 60) {

        insights.push({

            icon: "◉",

            className: "blue",

            title: "Resource Utilization",

            text:
                `Average utilization of ${data.utilization}% indicates potential capacity optimization opportunities.`

        });

    }


    return insights.slice(0, 4);

}


/* =========================================================
   RENDER INSIGHTS
   ========================================================= */

function renderInsights(insights) {

    insightsContainer.innerHTML = "";


    insights.forEach(
        insight => {

            const item =
                document.createElement("div");

            item.className =
                "insight-item";


            item.innerHTML = `

                <span class="insight-icon ${insight.className}">
                    ${insight.icon}
                </span>

                <div>

                    <strong>
                        ${escapeHtml(insight.title)}
                    </strong>

                    <p>
                        ${escapeHtml(insight.text)}
                    </p>

                </div>

            `;


            insightsContainer.appendChild(item);

        }
    );

}


/* =========================================================
   MAIN CALCULATION
   ========================================================= */

function calculateImpact() {


    /*
     * Remove previous errors.
     */

    document
        .querySelectorAll(".calculator-error")
        .forEach(
            element => element.remove()
        );


    document
        .querySelectorAll(".field-error")
        .forEach(
            element =>
                element.classList.remove(
                    "field-error"
                )
        );


    const monthlySpend =
        getNumber("monthlySpend");


    /*
     * Monthly spend is required.
     */

    if (monthlySpend <= 0) {

        const input =
            document.getElementById(
                "monthlySpend"
            );

        input.classList.add(
            "field-error"
        );

        showCalculatorError(
            "Please enter your monthly cloud spend."
        );

        input.focus();

        return;

    }


    const data = {

        cloud:
            getSelectedCloud(),

        monthlySpend,

        resources:
            getNumber("resources"),

        applications:
            getNumber("applications"),

        cloudTeam:
            getNumber("cloudTeam"),

        criticalApps:
            getNumber("criticalApps"),

        computeCost:
            getNumber("computeCost"),

        storageCost:
            getNumber("storageCost"),

        databaseCost:
            getNumber("databaseCost"),

        networkCost:
            getNumber("networkCost"),

        utilization:
            getNumber("utilization"),

        downtime:
            getNumber("downtime"),

        securityFindings:
            getNumber("securityFindings"),

        unusedResources:
            getNumber("unusedResources"),

        maturity:
            document.getElementById(
                "maturity"
            ).value,

        objectives:
            getObjectives()

    };


    /*
     * Calculate estimated savings rate.
     */

    const savingsRate =
        calculateSavingsRate(data);


    /*
     * Savings.
     */

    const estimatedMonthlySavings =
        data.monthlySpend *
        savingsRate;


    const estimatedAnnualSavings =
        estimatedMonthlySavings *
        12;


    /*
     * Impact score.
     */

    const score =
        calculateImpactScore(data);


    /*
     * ROI.
     *
     * Prototype assumes an estimated
     * implementation investment equal to
     * 3 months of projected savings.
     */

    const implementationCost =
        estimatedMonthlySavings * 3;


    const roi =
        implementationCost > 0
            ? (
                (
                    estimatedAnnualSavings -
                    implementationCost
                ) /
                implementationCost
            ) * 100
            : 0;


    /*
     * Payback.
     */

    const payback =
        estimatedMonthlySavings > 0
            ? implementationCost /
              estimatedMonthlySavings
            : 0;


    /*
     * Update UI.
     */

    monthlySavings.textContent =
        formatCurrency(
            estimatedMonthlySavings
        );


    annualSavings.textContent =
        formatCurrency(
            estimatedAnnualSavings
        );


    savingsPercent.textContent =
        `${(savingsRate * 100).toFixed(1)}% of monthly spend`;


    impactScore.textContent =
        `${score} / 100`;


    scoreFill.style.width =
        `${score}%`;


    scoreDescription.textContent =
        getScoreDescription(score);


    roiValue.textContent =
        `${Math.round(roi)}%`;


    paybackValue.textContent =
        `${payback.toFixed(1)} months`;


    /*
     * Show results.
     */

    resultsPlaceholder.style.display =
        "none";


    calculatedResults.classList.add(
        "show"
    );


    /*
     * Generate insights.
     */

    const insights =
        generateInsights(data);


    renderInsights(insights);


    /*
     * Change progress indicator.
     */

    updateProgress();


    /*
     * Scroll to results on smaller
     * screens.
     */

    if (window.innerWidth <= 850) {

        document
            .querySelector(".impact-results")
            .scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

    }

}


/* =========================================================
   PROGRESS UPDATE
   ========================================================= */

function updateProgress() {

    const steps =
        document.querySelectorAll(
            ".progress-step"
        );


    steps.forEach(
        step => {

            step.classList.add(
                "active"
            );

        }
    );

}


/* =========================================================
   ERROR MESSAGE
   ========================================================= */

function showCalculatorError(message) {

    const error =
        document.createElement("div");

    error.className =
        "calculator-error";

    error.textContent =
        message;


    const formCard =
        document.querySelector(
            ".impact-form-card"
        );


    const actions =
        document.querySelector(
            ".form-actions"
        );


    formCard.insertBefore(
        error,
        actions
    );

}


/* =========================================================
   CLEAR FORM
   ========================================================= */

function clearCalculator() {


    /*
     * Reset inputs.
     */

    inputIds.forEach(
        id => {

            const input =
                document.getElementById(id);

            if (input) {
                input.value = "";
            }

        }
    );


    /*
     * Reset selects.
     */

    document
        .querySelectorAll(
            ".form-group select"
        )
        .forEach(
            select => {
                select.selectedIndex = 0;
            }
        );


    /*
     * Reset cloud provider.
     */

    const aws =
        document.querySelector(
            'input[name="cloud"][value="aws"]'
        );

    if (aws) {
        aws.checked = true;
    }


    /*
     * Reset objectives.
     */

    document
        .querySelectorAll(
            '.objective-option input'
        )
        .forEach(
            checkbox => {

                checkbox.checked =
                    checkbox.value === "cost";

            }
        );


    /*
     * Reset errors.
     */

    document
        .querySelectorAll(
            ".field-error"
        )
        .forEach(
            element =>
                element.classList.remove(
                    "field-error"
                )
        );


    document
        .querySelectorAll(
            ".calculator-error"
        )
        .forEach(
            element =>
                element.remove()
        );


    /*
     * Hide calculated results.
     */

    calculatedResults.classList.remove(
        "show"
    );


    resultsPlaceholder.style.display =
        "block";


    /*
     * Reset insights.
     */

    insightsContainer.innerHTML = `

        <div class="insight-item">

            <span class="insight-icon green">
                ₹
            </span>

            <div>

                <strong>
                    Cost Optimization
                </strong>

                <p>
                    Enter your cloud metrics
                    to identify opportunities.
                </p>

            </div>

        </div>


        <div class="insight-item">

            <span class="insight-icon red">
                ◈
            </span>

            <div>

                <strong>
                    Security
                </strong>

                <p>
                    Your security findings will
                    be analyzed here.
                </p>

            </div>

        </div>


        <div class="insight-item">

            <span class="insight-icon purple">
                ♢
            </span>

            <div>

                <strong>
                    Reliability
                </strong>

                <p>
                    Downtime and reliability
                    metrics will be analyzed.
                </p>

            </div>

        </div>

    `;


    /*
     * Reset progress.
     */

    const steps =
        document.querySelectorAll(
            ".progress-step"
        );


    steps.forEach(
        (step, index) => {

            if (index === 0) {

                step.classList.add(
                    "active"
                );

            } else {

                step.classList.remove(
                    "active"
                );

            }

        }
    );

}


/* =========================================================
   ESCAPE HTML
   ========================================================= */

function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value;

    return div.innerHTML;

}


/* =========================================================
   EVENTS
   ========================================================= */

calculateButton.addEventListener(
    "click",
    calculateImpact
);


clearButton.addEventListener(
    "click",
    clearCalculator
);


/* =========================================================
   AUTO LIMIT UTILIZATION
   ========================================================= */

document
    .getElementById("utilization")
    .addEventListener(
        "input",
        function () {

            if (this.value > 100) {
                this.value = 100;
            }

            if (this.value < 0) {
                this.value = 0;
            }

        }
    );