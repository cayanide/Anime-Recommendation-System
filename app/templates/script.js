// Function to toggle password visibility
unction togglePassword() {
  const passwordField = document.getElementById("password");
  const eyeIcon = document.getElementById("eye-icon");

  if (passwordField.type === "password") {
    passwordField.type = "text";
    eyeIcon.innerText = "🙈"; // Hide icon when password is visible
  } else {
    passwordField.type = "password";
    eyeIcon.innerText = "👁️"; // Show icon when password is hidden
  }
}

// Function to toggle token visibility
function toggleTokenVisibility() {
  const tokenField = document.getElementById("token");
  const eyeIcon = document.getElementById("eye-icon-token"); // Use a unique ID for token visibility

  // Toggle the visibility of the token field
  if (tokenField.type === "password") {
    tokenField.type = "text";
    eyeIcon.innerText = "🙈"; // Hide icon when token is visible
  } else {
    tokenField.type = "password";
    eyeIcon.innerText = "👁️"; // Show icon when token is hidden
  }
}


// Function to proceed to the next page (redirect after token display)
function proceed() {
  window.location.href = "/home"; // Link to the next page after token display
}

// Function to fetch anime recommendations from API based on user preferences
async function fetchAnimeRecommendations() {
  const userId = localStorage.getItem("user_id"); // You can store this in localStorage or sessionStorage

  try {
    const response = await fetch(
      `/api/anime_recommendations?user_id=${userId}`,
    );
    const data = await response.json();
    const recommendationsDiv = document.getElementById("anime-recommendations");

    // Clear any existing recommendations
    recommendationsDiv.innerHTML = "";

    // Check if there are recommendations to display
    if (data && data.recommendations) {
      data.recommendations.forEach((anime) => {
        const animeCard = document.createElement("div");
        animeCard.classList.add("anime-card");
        animeCard.innerHTML = `
          <img src="${anime.coverImage.large}" alt="${anime.title.romaji}" />
          <h3>${anime.title.romaji}</h3>
        `;
        recommendationsDiv.appendChild(animeCard);
      });
    } else {
      recommendationsDiv.innerHTML =
        "<p>No recommendations available at the moment.</p>";
    }
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    const recommendationsDiv = document.getElementById("anime-recommendations");
    recommendationsDiv.innerHTML = "<p>Failed to load recommendations.</p>";
  }
}

// Function to handle search results
async function fetchSearchResults() {
  const query = document.getElementById("search-query").value.trim();

  if (!query) {
    alert("Please enter a search term.");
    return;
  }

  try {
    const response = await fetch(
      `/api/search?query=${encodeURIComponent(query)}`,
    );
    const data = await response.json();
    const resultsDiv = document.getElementById("search-results");

    // Clear any existing results
    resultsDiv.innerHTML = "";

    // Check if there are any search results
    if (data && data.searchResults && data.searchResults.length > 0) {
      data.searchResults.forEach((result) => {
        const resultCard = document.createElement("div");
        resultCard.classList.add("result-card");
        resultCard.innerHTML = `
          <img src="${result.coverImage.large}" alt="${result.title.romaji}" />
          <h3>${result.title.romaji}</h3>
        `;
        resultsDiv.appendChild(resultCard);
      });
    } else {
      resultsDiv.innerHTML = "<p>No results found for your search.</p>";
    }
  } catch (error) {
    console.error("Error fetching search results:", error);
    const resultsDiv = document.getElementById("search-results");
    resultsDiv.innerHTML = "<p>Failed to load search results.</p>";
  }
}

// Call the function to fetch anime recommendations when the page loads
window.onload = function () {
  fetchAnimeRecommendations();
};
