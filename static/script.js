// ---------------------------------------------------
// 1. ANIMATION OBSERVER
// ---------------------------------------------------

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {

        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }

    });

}, { threshold: 0.1 });

document.querySelectorAll('.reveal').forEach(el => {
    observer.observe(el);
});


// ---------------------------------------------------
// 2. MODAL MANAGEMENT
// ---------------------------------------------------

const signupModal = document.getElementById('signupModal');
const loginModal = document.getElementById('loginModal');
const subModal = document.getElementById('subModal');

function openSignupModal() {
    signupModal.classList.remove('hidden');
    loginModal.classList.add('hidden');
}

function closeSignupModal() {
    signupModal.classList.add('hidden');
}

function openLoginModal() {
    loginModal.classList.remove('hidden');
    signupModal.classList.add('hidden');
}

function closeLoginModal() {
    loginModal.classList.add('hidden');
}

function openSubModal() {
    subModal.classList.remove('hidden');
}

function closeSubModal() {
    subModal.classList.add('hidden');
}

function switchToLogin() {
    openLoginModal();
}

function switchToSignup() {
    openSignupModal();
}


// ---------------------------------------------------
// 3. SYMPTOM ANALYSIS LOGIC
// ---------------------------------------------------

async function analyzeSymptoms() {

    const inputField = document.getElementById('symptomInput');

    const resultArea = document.getElementById('resultArea');

    const diagnosisText = document.getElementById('diagnosisText');

    const adviceText = document.getElementById('adviceText');

    const doctorContainer = document.getElementById('doctorButtonContainer');

    // NEW ELEMENTS
    const predictionContainer = document.getElementById('predictionContainer');

    const urgencyContainer = document.getElementById('urgencyContainer');

    // Validation
    if (!inputField.value.trim()) {

        alert("Please enter some symptoms first.");

        return;
    }

    // Loading state
    diagnosisText.innerHTML = `
        <span class="text-sky-700 font-bold">
            Consulting AI...
        </span>
    `;

    adviceText.innerHTML = "";

    if (predictionContainer) predictionContainer.innerHTML = "";

    if (urgencyContainer) urgencyContainer.innerHTML = "";

    if (doctorContainer) doctorContainer.innerHTML = "";

    resultArea.classList.remove('hidden');
    const defaultPreview = document.getElementById('defaultPreview');
    if (defaultPreview) {
        defaultPreview.classList.add('hidden');
    }

    try {

        const response = await fetch('/analyze', {

            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify({
                symptoms: inputField.value
            }),
        });

        const data = await response.json();

        // ---------------------------------------------------
        // LOGIN REQUIRED
        // ---------------------------------------------------

        if (data.status === 'login_required') {

            resultArea.classList.add('hidden');
            const defaultPreview = document.getElementById('defaultPreview');
            if (defaultPreview) {
                defaultPreview.classList.add('hidden');
            }

            openLoginModal();
        }

        // ---------------------------------------------------
        // SUBSCRIPTION REQUIRED
        // ---------------------------------------------------

        else if (data.status === 'subscription_required') {

            resultArea.classList.add('hidden');

            openSubModal();
        }

        // ---------------------------------------------------
        // SUCCESS
        // ---------------------------------------------------

        else if (data.status === 'success') {

            // ---------------------------------------------------
            // MAIN DIAGNOSIS
            // ---------------------------------------------------

            diagnosisText.innerHTML = `
                <span class="font-bold text-sky-700">
                    Primary Diagnosis:
                </span>
                ${data.diagnosis}
            `;

            // ---------------------------------------------------
            // ADVICE
            // ---------------------------------------------------

            adviceText.innerHTML = `
                <span class="font-bold text-gray-700">
                    Medical Advice:
                </span>
                ${data.advice}

                <br>

                <span class="text-sky-600 text-sm mt-2 block">
                    Specialist:
                    ${data.recommended_specialist}
                </span>
            `;

            // ---------------------------------------------------
            // URGENCY BADGE
            // ---------------------------------------------------

            if (urgencyContainer) {

                let urgencyColor = "bg-green-500";

                if (data.urgency === "Moderate") {
                    urgencyColor = "bg-yellow-500";
                }

                else if (data.urgency === "High") {
                    urgencyColor = "bg-orange-500";
                }

                else if (data.urgency === "Emergency") {
                    urgencyColor = "bg-red-600";
                }

                urgencyContainer.innerHTML = `
                    <div class="${urgencyColor} text-white px-4 py-2 rounded-lg font-bold inline-block mt-4 shadow">
                        Urgency Level: ${data.urgency}
                    </div>
                `;
            }

            // ---------------------------------------------------
            // TOP PREDICTIONS
            // ---------------------------------------------------

            if (predictionContainer && data.top_predictions) {

                let predictionHTML = `
                    <div class="mt-5">
                        <h3 class="font-bold text-lg text-sky-700 mb-3">
                            Top Possible Conditions
                        </h3>
                `;

                data.top_predictions.forEach((prediction, index) => {

                    predictionHTML += `
                        <div class="bg-white border border-gray-200 rounded-xl p-4 mb-3 shadow-sm">

                            <div class="flex justify-between items-center mb-2">

                                <span class="font-semibold text-gray-800">
                                    ${index + 1}. ${prediction.disease}
                                </span>

                                <span class="text-sky-700 font-bold">
                                    ${prediction.probability}%
                                </span>

                            </div>

                            <div class="w-full bg-gray-200 rounded-full h-3">

                                <div 
                                    class="bg-sky-500 h-3 rounded-full"
                                    style="width: ${prediction.probability}%">
                                </div>

                            </div>

                        </div>
                    `;
                });

                predictionHTML += `</div>`;

                predictionContainer.innerHTML = predictionHTML;
            }

            // ---------------------------------------------------
            // GOOGLE MAPS DOCTOR BUTTON
            // ---------------------------------------------------

            if (doctorContainer && data.recommended_specialist) {

                const specialist = data.recommended_specialist;

                const mapsUrl =
                    `https://www.google.com/maps/search/${specialist}+near+me`;

                doctorContainer.innerHTML = `

                    <a href="${mapsUrl}" target="_blank"
                       class="mt-4 w-full bg-green-600 text-white py-3 rounded-lg font-bold hover:bg-green-700 transition shadow-md flex items-center justify-center gap-2">

                        <span>📍</span>

                        Find ${specialist} Near Me

                    </a>

                    <p class="text-xs text-center text-gray-400 mt-2">
                        Redirects to Google Maps
                    </p>
                `;
            }
        }

        // ---------------------------------------------------
        // ERROR
        // ---------------------------------------------------

        else {

            diagnosisText.innerHTML = `
                <span class="text-red-600 font-bold">
                    Error:
                </span>
                ${data.message}
            `;
        }

    }

    // ---------------------------------------------------
    // SERVER ERROR
    // ---------------------------------------------------

    catch (error) {

        console.error(error);

        diagnosisText.innerHTML = `
            <span class="text-red-600 font-bold">
                Server connection error.
            </span>
        `;
    }
}


// ---------------------------------------------------
// 4. AUTH & PAYMENT LOGIC
// ---------------------------------------------------

async function submitSignup() {

    const email = document.getElementById('signupEmail').value;

    const password = document.getElementById('signupPass').value;

    if (!email || !password) {

        alert("Please fill all fields.");

        return;
    }

    const response = await fetch('/signup', {

        method: 'POST',

        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            email,
            password
        })
    });

    const data = await response.json();

    if (data.status === 'success') {

        alert(data.message);

        switchToLogin();
    }

    else {

        alert(data.message);
    }
}


async function submitLogin() {

    const email = document.getElementById('loginEmail').value;

    const password = document.getElementById('loginPass').value;

    if (!email || !password) {

        alert("Please fill all fields.");

        return;
    }

    const response = await fetch('/login', {

        method: 'POST',

        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            email,
            password
        })
    });

    const data = await response.json();

    if (data.status === 'success') {

        window.location.reload();
    }

    else {

        alert(data.message);
    }
}


async function buyPremium() {

    const response = await fetch('/upgrade', {
        method: 'POST'
    });

    const data = await response.json();

    if (data.status === 'success') {

        alert("Payment Successful! Premium Features Unlocked.");

        closeSubModal();

        analyzeSymptoms();
    }

    else {

        alert("Payment Error.");
    }
}