// ======================================================
// MOBILE NAVIGATION
// ======================================================

const menuButton = document.getElementById("menuButton");
const navbar = document.getElementById("navbar");

menuButton.addEventListener("click", function () {
    navbar.classList.toggle("show");
});

document.querySelectorAll(".navbar a").forEach(function (link) {
    link.addEventListener("click", function () {
        navbar.classList.remove("show");
    });
});


// ======================================================
// EVENT FILTER
// ======================================================

const filterButtons = document.querySelectorAll(".filter-button");
const eventCards = document.querySelectorAll(".event-card");

filterButtons.forEach(function (button) {

    button.addEventListener("click", function () {

        filterButtons.forEach(function (item) {
            item.classList.remove("active");
        });

        button.classList.add("active");

        const selectedCategory = button.dataset.category;

        eventCards.forEach(function (card) {

            const cardCategory = card.dataset.category;

            if (
                selectedCategory === "all" ||
                selectedCategory === cardCategory
            ) {
                card.style.display = "block";
            } else {
                card.style.display = "none";
            }

        });

    });

});


// ======================================================
// SELECT EVENT FROM EVENT CARD
// ======================================================

const registerButtons = document.querySelectorAll(
    ".register-event-button"
);

const eventSelect = document.getElementById("eventName");

registerButtons.forEach(function (button) {

    button.addEventListener("click", function () {

        const selectedEvent = button.dataset.event;

        eventSelect.value = selectedEvent;

        document
            .getElementById("register")
            .scrollIntoView({
                behavior: "smooth"
            });

    });

});


// ======================================================
// LOCAL STORAGE REGISTRATION DATA
// ======================================================

let registrations = JSON.parse(
    localStorage.getItem("collegeEventRegistrations")
) || [];


// ======================================================
// REGISTRATION FORM
// ======================================================

const registrationForm = document.getElementById(
    "eventRegistrationForm"
);

const successMessage = document.getElementById(
    "successMessage"
);

const successText = document.getElementById(
    "successText"
);

registrationForm.addEventListener("submit", function (event) {

    event.preventDefault();

    const studentName = document
        .getElementById("studentName")
        .value
        .trim();

    const studentId = document
        .getElementById("studentId")
        .value
        .trim();

    const studentEmail = document
        .getElementById("studentEmail")
        .value
        .trim();

    const studentPhone = document
        .getElementById("studentPhone")
        .value
        .trim();

    const department = document
        .getElementById("department")
        .value;

    const studyYear = document
        .getElementById("studyYear")
        .value;

    const selectedEvent = document
        .getElementById("eventName")
        .value;

    if (studentPhone.length !== 10) {
        alert("Please enter a valid 10-digit phone number.");
        return;
    }

    const registration = {
        id: Date.now(),
        studentName: studentName,
        studentId: studentId,
        studentEmail: studentEmail,
        studentPhone: studentPhone,
        department: department,
        studyYear: studyYear,
        eventName: selectedEvent,
        status: "Confirmed"
    };

    registrations.push(registration);

    saveRegistrations();

    successText.textContent =
        studentName +
        ", you have successfully registered for " +
        selectedEvent +
        ".";

    registrationForm.style.display = "none";
    successMessage.style.display = "block";

    displayRegistrations();

});


// ======================================================
// SAVE DATA
// ======================================================

function saveRegistrations() {

    localStorage.setItem(
        "collegeEventRegistrations",
        JSON.stringify(registrations)
    );

}


// ======================================================
// DISPLAY REGISTRATIONS
// ======================================================

function displayRegistrations() {

    const tableBody = document.getElementById(
        "registrationTableBody"
    );

    const totalRegistrations = document.getElementById(
        "totalRegistrations"
    );

    const upcomingRegistrations = document.getElementById(
        "upcomingRegistrations"
    );

    tableBody.innerHTML = "";

    totalRegistrations.textContent = registrations.length;
    upcomingRegistrations.textContent = registrations.length;

    if (registrations.length === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-message">
                    No event registrations found.
                </td>
            </tr>
        `;

        return;
    }

    registrations.forEach(function (registration, index) {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${index + 1}</td>

            <td>${registration.studentName}</td>

            <td>${registration.studentId}</td>

            <td>${registration.department}</td>

            <td>${registration.eventName}</td>

            <td>
                <span class="status-badge">
                    ${registration.status}
                </span>
            </td>

            <td>
                <button
                    class="cancel-button"
                    onclick="cancelRegistration(${registration.id})"
                >
                    Cancel
                </button>
            </td>
        `;

        tableBody.appendChild(row);

    });

}


// ======================================================
// CANCEL REGISTRATION
// ======================================================

function cancelRegistration(registrationId) {

    const confirmation = confirm(
        "Do you want to cancel this event registration?"
    );

    if (!confirmation) {
        return;
    }

    registrations = registrations.filter(
        function (registration) {
            return registration.id !== registrationId;
        }
    );

    saveRegistrations();
    displayRegistrations();

}


// ======================================================
// REGISTER ANOTHER EVENT
// ======================================================

const registerAnotherButton = document.getElementById(
    "registerAnotherButton"
);

registerAnotherButton.addEventListener("click", function () {

    registrationForm.reset();

    registrationForm.style.display = "block";
    successMessage.style.display = "none";

});


// ======================================================
// LOAD REGISTRATIONS WHEN PAGE OPENS
// ======================================================

displayRegistrations();