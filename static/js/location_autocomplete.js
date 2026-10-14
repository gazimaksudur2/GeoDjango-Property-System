document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("location-search");
  const suggestions = document.getElementById("suggestions");

  if (!input || !suggestions) {
    console.warn("Autocomplete elements not found");
    return;
  }

  let debounceTimer = null;

  input.addEventListener("input", () => {
    const query = input.value.trim();

    clearTimeout(debounceTimer);

    if (query.length < 2) {
      suggestions.innerHTML = "";
      suggestions.classList.add("hidden");

      return;
    }

    debounceTimer = setTimeout(async () => {
      try {
        const response = await fetch(
          `/api/v1/locations/autocomplete/?q=${encodeURIComponent(query)}`,
        );

        const locations = await response.json();

        suggestions.innerHTML = "";

        if (!locations.length) {
          suggestions.classList.add("hidden");

          return;
        }

        locations.forEach((location) => {
          const item = document.createElement("div");

          item.className = `
                    px-4 py-3
                    hover:bg-gray-100
                    cursor-pointer
                    border-b
                    last:border-b-0
                    `;

          item.innerHTML = `
                <div class="text-sm text-gray-800">
                    ${location.name}, ${location.city}, ${location.country}
                </div>
            `;

          item.onclick = () => {
            input.value = location.name;

            suggestions.innerHTML = "";

            suggestions.classList.add("hidden");
          };

          suggestions.appendChild(item);
        });

        suggestions.classList.remove("hidden");
      } catch (error) {
        console.error("Autocomplete error:", error);

        suggestions.classList.add("hidden");
      }
    }, 300);
  });
});
