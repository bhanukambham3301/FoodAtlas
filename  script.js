document.addEventListener("DOMContentLoaded", () => {
    let currentCategoryFilter = 'All';
    let currentVegFilter = 'All';

    // కేటగిరీ బటన్స్ అన్నీ సెలెక్ట్ చేయడం
    const buttons = document.querySelectorAll('#category-filters button, .buttons-group button');

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            // ఆ గ్రూప్‌లో ఉన్న అన్ని బటన్స్ నుండి active-custom తీసేయాలి
            buttons.forEach(btn => btn.classList.remove('active-custom'));

            // మనం క్లిక్ చేసిన బటన్‌కి మాత్రం రెడ్ కలర్ యాడ్ చేయాలి
            button.classList.add('active-custom');

            // కేటగిరీ వాల్యూ తీసుకోవడం
            currentCategoryFilter = button.getAttribute('data-category') || button.innerText;

            // ఫిల్టర్ ఫంక్షన్ కాల్ చేయడం
            applyFilters(currentCategoryFilter, currentVegFilter);
        });
    });

    function applyFilters(targetCat, targetVeg) {
        const cards = document.querySelectorAll('.food-card, .card');

        cards.forEach(card => {
            const cardCategory = (card.getAttribute('data-category') || '').trim().toLowerCase();
            const tCat = targetCat.trim().toLowerCase();

            let matchesCategory = (tCat === 'all' || tCat === 'all categories') || (cardCategory === tCat);

            if (matchesCategory) {
                card.style.display = 'block'; // లేదా 'flex'
            } else {
                card.style.display = 'none';
            }
        });
    }
});