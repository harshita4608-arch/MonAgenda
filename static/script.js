// =====================================================
// MONAGENDA - INTERACTIVE EFFECTS
// =====================================================

document.addEventListener("DOMContentLoaded", function () {

    // -------------------------------------------------
    // 1. Page loaded animation
    // -------------------------------------------------

    document.body.classList.add("page-loaded");


    // -------------------------------------------------
    // 2. Habit completion button
    // -------------------------------------------------

    const habitButtons = document.querySelectorAll(".complete-habit-btn");

    habitButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            button.classList.add("clicked");

            button.innerHTML = "✨ Completing...";

            const xp = document.createElement("div");

            xp.className = "floating-xp";
            xp.innerHTML = "+10 XP ⚡";

            document.body.appendChild(xp);

            setTimeout(function () {
                xp.remove();
            }, 1500);

        });

    });


    // -------------------------------------------------
    // 3. Feature card hover effect
    // -------------------------------------------------

    const cards = document.querySelectorAll(
        ".habit-card, .ls-feature, .card"
    );

    cards.forEach(function (card) {

        card.addEventListener("mouseenter", function () {
            card.classList.add("js-hover");
        });

        card.addEventListener("mouseleave", function () {
            card.classList.remove("js-hover");
        });

    });


    // -------------------------------------------------
    // 4. Pet click reaction
    // -------------------------------------------------

    const pet = document.querySelector(".ls-pet, .coach-pet");

    if (pet) {

        pet.addEventListener("click", function () {

            pet.classList.add("pet-happy");

            const message = document.createElement("div");

            message.className = "pet-message";
            message.innerHTML = "You're doing great! 💜";

            pet.parentElement.appendChild(message);

            setTimeout(function () {

                pet.classList.remove("pet-happy");
                message.remove();

            }, 1800);

        });

    }


    // -------------------------------------------------
    // 5. Button click animation
    // -------------------------------------------------

    const buttons = document.querySelectorAll("button");

    buttons.forEach(function (button) {

        button.addEventListener("click", function () {

            button.classList.add("button-clicked");

            setTimeout(function () {
                button.classList.remove("button-clicked");
            }, 300);

        });

    });


    // -------------------------------------------------
    // 6. Habit celebration
    // -------------------------------------------------

    const completeButtons =
        document.querySelectorAll(".complete-habit-btn");

    completeButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            createCelebration();
            petReaction();

        });

    });


    // -------------------------------------------------
    // 7. Load saved theme
    // -------------------------------------------------

    loadTheme();

});


// =====================================================
// CELEBRATION EFFECT
// =====================================================

function createCelebration() {

    const emojis = ["✨", "🎉", "⭐", "💜", "🔥", "🌱"];

    for (let i = 0; i < 15; i++) {

        const emoji = document.createElement("div");

        emoji.innerText =
            emojis[Math.floor(Math.random() * emojis.length)];

        emoji.classList.add("celebration");

        emoji.style.left =
            Math.random() * 100 + "vw";

        emoji.style.animationDelay =
            Math.random() * 0.5 + "s";

        document.body.appendChild(emoji);

        setTimeout(function () {
            emoji.remove();
        }, 2000);
    }
}


// =====================================================
// PET COACH REACTION
// =====================================================

function petReaction() {

    const pet = document.querySelector(".coach-pet");

    if (!pet) return;

    pet.classList.add("pet-happy");

    pet.innerHTML = "🐼💜";

    setTimeout(function () {

        pet.innerHTML = "🐼";
        pet.classList.remove("pet-happy");

    }, 1500);
}


// =====================================================
// MONAGENDA THEME SYSTEM
// =====================================================




function loadTheme() {

    const savedTheme =
        localStorage.getItem("monagendaTheme");

    if (savedTheme) {

        document.documentElement.setAttribute(
            "data-theme",
            savedTheme
        );

    } else {

        // Default theme
        document.documentElement.setAttribute(
            "data-theme",
            "light"
        );

    }
}
// =====================================================
// MONAGENDA THEME SYSTEM
// =====================================================

function changeTheme(theme) {

    console.log("Changing MonAgenda theme:", theme);

    document.documentElement.setAttribute(
        "data-theme",
        theme
    );

    localStorage.setItem(
        "monagendaTheme",
        theme
    );

}


// =====================================================
// LOAD SAVED THEME
// =====================================================

function loadTheme() {

    const savedTheme =
        localStorage.getItem("monagendaTheme") || "light";

    console.log("Loading MonAgenda theme:", savedTheme);

    document.documentElement.setAttribute(
        "data-theme",
        savedTheme
    );

}


// =====================================================
// START
// =====================================================

document.addEventListener("DOMContentLoaded", function () {

    loadTheme();

});

