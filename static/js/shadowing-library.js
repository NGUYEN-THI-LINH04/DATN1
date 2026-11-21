
document.addEventListener("DOMContentLoaded", () => {
    const search = document.getElementById("shadowingSearch");
    const filter = document.getElementById("shadowingModeFilter");
    const cards = Array.from(
        document.querySelectorAll(".shadowing-video-card")
    );
    const counter = document.getElementById("shadowingVideoCount");
    const empty = document.getElementById("shadowingEmpty");

    if (!search || !filter || !counter || !empty) return;

    function normalize(text) {
        return (text || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .trim();
    }

    function updateVideos() {
        const keyword = normalize(search.value);
        const selectedMode = filter.value;
        let visibleCount = 0;

        cards.forEach(card => {
            const title = normalize(card.dataset.title);
            const modes = (card.dataset.modes || "")
                .split(",")
                .map(mode => mode.trim());

            const matchesSearch = title.includes(keyword);
            const matchesMode =
                selectedMode === "all" ||
                modes.includes(selectedMode);

            const visible = matchesSearch && matchesMode;
            card.hidden = !visible;

            if (visible) visibleCount++;
        });

        counter.textContent = `${visibleCount} video`;
        empty.hidden = visibleCount > 0;
    }

    search.addEventListener("input", updateVideos);
    filter.addEventListener("change", updateVideos);

    updateVideos();
});
