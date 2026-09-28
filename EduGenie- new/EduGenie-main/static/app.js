const form = document.getElementById("edu-form");

const task = document.getElementById("task");

const input = document.getElementById("input");

const submit = document.getElementById("submit");

const counter = document.getElementById("counter");

const result = document.getElementById("result");

const output = document.getElementById("output");

const errorBox = document.getElementById("error");

const copyButton = document.getElementById("copy");


// ---------------------------------------------------------
// HTML escaping
// ---------------------------------------------------------

function escapeHtml(value) {

    return String(value).replace(
        /[&<>'"]/g,

        character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            "'": "&#39;",
            '"': "&quot;"
        })[character]
    );
}


// ---------------------------------------------------------
// Character counter
// ---------------------------------------------------------

input.addEventListener(
    "input",
    () => {

        counter.textContent =
            `${input.value.length.toLocaleString()} / 20,000`;
    }
);


// ---------------------------------------------------------
// Normal answer renderer
// ---------------------------------------------------------

function renderAnswer(data) {

    output.innerHTML = `
        <div class="answer">
            ${escapeHtml(data.answer)}
        </div>
    `;
}


// ---------------------------------------------------------
// Quiz renderer
// ---------------------------------------------------------

function renderQuiz(data) {

    output.innerHTML = data.questions
        .map((question, index) => {

            const options = question.options
                .map(
                    (option, optionIndex) => {

                        const letter =
                            String.fromCharCode(
                                65 + optionIndex
                            );

                        return `
                            <div class="quiz-option">
                                <strong>${letter}.</strong>
                                ${escapeHtml(option)}
                            </div>
                        `;
                    }
                )
                .join("");

            return `
                <article class="quiz-question">

                    <h3>
                        ${index + 1}.
                        ${escapeHtml(question.question)}
                    </h3>

                    ${options}

                    <div class="quiz-answer">

                        Answer:
                        ${escapeHtml(question.correct_answer)}

                        ${
                            question.explanation
                                ? ` — ${escapeHtml(
                                    question.explanation
                                )}`
                                : ""
                        }

                    </div>

                </article>
            `;
        })
        .join("");
}


// ---------------------------------------------------------
// Learning path renderer
// ---------------------------------------------------------

function renderPath(data) {

    const steps = data.steps
        .map(
            (step, index) => {

                return `
                    <article class="path-step">

                        <h3>
                            ${index + 1}.
                            ${escapeHtml(step.level)}
                            —
                            ${escapeHtml(step.topic)}
                        </h3>

                        <div>
                            <strong>
                                Concepts:
                            </strong>

                            ${step.concepts
                                .map(escapeHtml)
                                .join(", ")}
                        </div>

                        <div>
                            <strong>
                                Suggested time:
                            </strong>

                            ${escapeHtml(
                                step.suggested_time
                            )}
                        </div>

                        <div>
                            <strong>
                                Resources:
                            </strong>

                            ${step.resources
                                .map(escapeHtml)
                                .join(", ")}
                        </div>

                    </article>
                `;
            }
        )
        .join("");

    const tips = data.study_tips
        .map(
            tip =>
                `<li>${escapeHtml(tip)}</li>`
        )
        .join("");

    output.innerHTML = `

        <p>
            <strong>
                ${escapeHtml(data.topic)}
            </strong>

            <br>

            ${escapeHtml(data.goal)}
        </p>

        ${steps}

        <div>

            <strong>
                Study tips
            </strong>

            <ul>
                ${tips}
            </ul>

        </div>
    `;
}


// ---------------------------------------------------------
// General renderer
// ---------------------------------------------------------

function render(data) {

    if (task.value === "quiz") {

        renderQuiz(data);

    } else if (
        task.value === "learn/recommendations"
    ) {

        renderPath(data);

    } else {

        renderAnswer(data);
    }

    result.classList.remove("hidden");
}


// ---------------------------------------------------------
// Submit
// ---------------------------------------------------------

form.addEventListener(
    "submit",
    async event => {

        event.preventDefault();

        const text = input.value.trim();

        errorBox.classList.add("hidden");

        if (!text) {

            errorBox.textContent =
                "Please enter a question, topic, or passage.";

            errorBox.classList.remove("hidden");

            return;
        }

        submit.disabled = true;

        submit.textContent = "Thinking…";

        result.classList.add("hidden");

        try {

            const response = await fetch(
                `/${task.value}`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        text: text
                    })
                }
            );

            const data =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Request failed."
                );
            }

            render(data);

        } catch (error) {

            errorBox.textContent =
                error.message ||
                "Something went wrong.";

            errorBox.classList.remove("hidden");

        } finally {

            submit.disabled = false;

            submit.textContent = "Generate";
        }
    }
);


// ---------------------------------------------------------
// Copy result
// ---------------------------------------------------------

copyButton.addEventListener(
    "click",
    async () => {

        try {

            await navigator.clipboard.writeText(
                output.innerText
            );

            copyButton.textContent = "Copied";

            setTimeout(
                () => {
                    copyButton.textContent = "Copy";
                },
                1200
            );

        } catch {

            copyButton.textContent =
                "Copy failed";
        }
    }
);