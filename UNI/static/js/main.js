const countdown = document.getElementById("countdown");
const launchDate = new Date("2025-07-01T00:00:00");

const updateCountdown = () => {
    const now = new Date();
    const diff = launchDate - now;

    if (diff <= 0) {
        countdown.textContent = "We have launched!";
        return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
    const mins = Math.floor((diff / 1000 / 60) % 60);
    const secs = Math.floor((diff / 1000) % 60);

    countdown.textContent = `Launching in: ${days} days ${hours}:${mins}:${secs}`;
};

if (countdown) {
    setInterval(updateCountdown, 1000);
    updateCountdown();
}

const plans = {
    "1m": [
        { name: "Starter", price: "₹299/mo", features: ["Curated films", "2 screens", "Monthly newsletter"] },
        { name: "Pro", price: "₹599/mo", features: ["Everything in Starter", "Premieres", "4 screens", "Download access"] },
        { name: "Studio", price: "₹999/mo", features: ["All Pro features", "Submit work", "Community access", "Priority support"] }
    ],
    "6m": [
        { name: "Starter", price: "₹1,699/6mo", features: ["Save ₹95", "Curated films", "2 screens", "Newsletter"] },
        { name: "Pro", price: "₹3,399/6mo", features: ["Save ₹195", "Premieres", "4 screens", "Downloads"] },
        { name: "Studio", price: "₹5,499/6mo", features: ["Save ₹495", "Submit work", "Community", "Priority support"] }
    ],
    "1y": [
        { name: "Starter", price: "₹3,199/yr", features: ["Save ₹389", "Curated films", "2 screens", "Newsletter"] },
        { name: "Pro", price: "₹5,999/yr", features: ["Save ₹1,189", "Premieres", "4 screens", "Downloads"] },
        { name: "Studio", price: "₹9,499/yr", features: ["Save ₹2,489", "Submit work", "Community", "Priority support"] }
    ]
};

function updatePlans() {
    const duration = document.getElementById("planDuration").value;
    container.innerHTML = "";

    plans[duration].forEach(plan => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
        <h2>${plan.name}</h2>
        <div class="price">${plan.price}</div>
        <ul class="features">
          ${plan.features.map(f => `<li>${f}</li>`).join("")}
        </ul>
        <button>Select</button>
      `;
        container.appendChild(card);
    });
}

// Load default (1m) plans
const container = document.getElementById("pricingContainer");
if (container) {
    updatePlans();   
}