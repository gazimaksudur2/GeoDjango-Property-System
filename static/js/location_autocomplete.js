document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("location-search");
  const suggestions = document.getElementById("suggestions");
  const searchTypeInput = document.getElementById("search-type-input");
  const targetIdInput = document.getElementById("target-id-input");
  const radiusContainer = document.getElementById("radius-container");
  const modeButtons = document.querySelectorAll(".search-mode-btn");
  const searchForm = document.getElementById("property-search-form");

  if (!input || !suggestions || !searchTypeInput) {
    return;
  }

  let debounceTimer = null;

  function setSearchMode(mode, clearInput = false) {
    const normalizedMode = mode === "property" ? "property" : "location";
    searchTypeInput.value = normalizedMode;

    if (clearInput) {
      input.value = "";
      if (targetIdInput) {
        targetIdInput.value = "";
      }
    }

    modeButtons.forEach((btn) => {
      const isSelected = btn.getAttribute("data-mode") === normalizedMode;
      if (isSelected) {
        btn.classList.add("bg-blue-600", "text-white", "shadow-sm");
        btn.classList.remove("text-gray-700", "hover:text-gray-900");
      } else {
        btn.classList.remove("bg-blue-600", "text-white", "shadow-sm");
        btn.classList.add("text-gray-700", "hover:text-gray-900");
      }
    });

    if (normalizedMode === "location") {
      input.placeholder = "Search by location (e.g., Gulshan, Banani, Dhanmondi)...";
      if (radiusContainer) {
        radiusContainer.classList.remove("hidden");
      }
    } else {
      input.placeholder = "Search by property title or vibe (e.g., luxury apartment, villa)...";
      if (radiusContainer) {
        radiusContainer.classList.add("hidden");
      }
    }

    suggestions.innerHTML = "";
    suggestions.classList.add("hidden");
  }

  async function fetchLocationSuggestions(query) {
    const response = await fetch(
      `/api/v1/locations/autocomplete/?q=${encodeURIComponent(query)}`
    );
    if (!response.ok) return;
    const locations = await response.json();
    renderLocationDropdown(locations);
  }

  async function fetchPropertySuggestions(query) {
    const response = await fetch(
      `/api/v1/properties/autocomplete/?q=${encodeURIComponent(query)}`
    );
    if (!response.ok) return;
    const properties = await response.json();
    renderPropertyDropdown(properties);
  }

  async function dispatchAutocomplete(query) {
    try {
      const currentMode = searchTypeInput.value || "location";
      if (currentMode === "property") {
        await fetchPropertySuggestions(query);
      } else {
        await fetchLocationSuggestions(query);
      }
    } catch (error) {
      console.error("Autocomplete error:", error);
      suggestions.classList.add("hidden");
    }
  }

  function renderLocationDropdown(locations) {
    suggestions.innerHTML = "";
    if (!locations || !locations.length) {
      suggestions.classList.add("hidden");
      return;
    }

    locations.forEach((location) => {
      const item = document.createElement("div");
      item.className =
        "px-4 py-3 hover:bg-blue-50 cursor-pointer border-b last:border-b-0 flex justify-between items-center";

      item.innerHTML = `
        <div>
          <div class="text-sm font-medium text-gray-800">📍 ${location.name}</div>
          <div class="text-xs text-gray-500">${location.city || ""}${location.country ? ", " + location.country : ""}</div>
        </div>
        <span class="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">Location</span>
      `;

      item.addEventListener("click", () => {
        input.value = location.name;
        if (targetIdInput) {
          targetIdInput.value = location.id;
        }
        suggestions.innerHTML = "";
        suggestions.classList.add("hidden");
        if (searchForm) {
          searchForm.submit();
        }
      });

      suggestions.appendChild(item);
    });

    suggestions.classList.remove("hidden");
  }

  function renderPropertyDropdown(properties) {
    suggestions.innerHTML = "";
    if (!properties || !properties.length) {
      suggestions.classList.add("hidden");
      return;
    }

    properties.forEach((prop) => {
      const item = document.createElement("div");
      item.className =
        "px-4 py-3 hover:bg-purple-50 cursor-pointer border-b last:border-b-0 flex justify-between items-center gap-2";

      item.innerHTML = `
        <div>
          <div class="text-sm font-medium text-gray-800">🏠 ${prop.title}</div>
          <div class="text-xs text-gray-500">${prop.property_type || "Property"} • ${prop.location_name || ""}${prop.city ? ", " + prop.city : ""}</div>
        </div>
        <div class="text-right shrink-0">
          <div class="text-sm font-bold text-blue-600">৳ ${prop.price}</div>
          <span class="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded">${prop.bedrooms} Beds</span>
        </div>
      `;

      item.addEventListener("click", () => {
        input.value = prop.title;
        if (targetIdInput) {
          targetIdInput.value = prop.id;
        }
        suggestions.innerHTML = "";
        suggestions.classList.add("hidden");
        if (searchForm) {
          searchForm.submit();
        }
      });

      suggestions.appendChild(item);
    });

    suggestions.classList.remove("hidden");
  }

  modeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const selectedMode = btn.getAttribute("data-mode");
      if (searchTypeInput.value !== selectedMode) {
        setSearchMode(selectedMode, true);
      }
    });
  });

  setSearchMode(searchTypeInput.value || "location", false);

  input.addEventListener("input", () => {
    if (targetIdInput) {
      targetIdInput.value = "";
    }
    const query = input.value.trim();
    clearTimeout(debounceTimer);

    if (query.length < 2) {
      suggestions.innerHTML = "";
      suggestions.classList.add("hidden");
      return;
    }

    debounceTimer = setTimeout(() => {
      dispatchAutocomplete(query);
    }, 300);
  });

  document.addEventListener("click", (e) => {
    if (!input.contains(e.target) && !suggestions.contains(e.target)) {
      suggestions.classList.add("hidden");
    }
  });

  setSearchMode(searchTypeInput.value || "location", false);
});