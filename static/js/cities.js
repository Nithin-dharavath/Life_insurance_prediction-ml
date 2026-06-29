/* Tier 1 + Tier 2 cities — must stay in sync with city/city_tier.py.
   Order: tier_1 first, then tier_2. */
(function () {
  const TIER_1 = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"
  ];
  const TIER_2 = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam",
    "Coimbatore", "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur",
    "Raipur", "Amritsar", "Varanasi", "Agra", "Dehradun", "Mysore", "Jabalpur",
    "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik", "Allahabad", "Udaipur",
    "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode",
    "Warangal", "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol",
    "Siliguri"
  ];
  const ALL = TIER_1.concat(TIER_2);

  window.App = window.App || {};
  window.App.cities = { TIER_1, TIER_2, ALL };

  // Populate the datalist on load
  document.addEventListener("DOMContentLoaded", () => {
    const list = document.getElementById("cities");
    if (!list) return;
    const frag = document.createDocumentFragment();
    for (const city of ALL) {
      const opt = document.createElement("option");
      opt.value = city;
      frag.appendChild(opt);
    }
    list.appendChild(frag);
  });
})();