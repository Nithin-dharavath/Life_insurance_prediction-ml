/* Client-side mirror of server-derived features in schema/user_input.py.
   Note: lifestyle_risk mirrors the SCHEMA rule (`smoker AND bmi>27`) which
   differs from train.py (`smoker OR bmi>27`) — see CLAUDE.md. */
(function () {
  const CATEGORY_COPY = {
    Low:    "You are in a low premium bracket — favorable risk profile.",
    Medium: "You are in a moderate premium bracket — a balanced risk profile.",
    High:   "You are in a high premium bracket — elevated risk profile."
  };

  function computeBMI(weight, height) {
    return weight / (height * height);
  }

  function computeAgeGroup(age) {
    if (age < 18) return "young";
    if (age < 45) return "adult";
    if (age < 65) return "middle-aged";
    return "senior";
  }

  // Mirrors schema/user_input.py (not train.py — see CLAUDE.md gotcha).
  function computeLifestyleRisk(smoker, bmi) {
    if (smoker && bmi > 30) return "high";
    if (smoker && bmi > 27) return "medium";
    return "low";
  }

  function computeCityTier(city) {
    const { TIER_1, TIER_2 } = window.App.cities;
    if (TIER_1.includes(city)) return 1;
    if (TIER_2.includes(city)) return 2;
    return 3;
  }

  window.App = window.App || {};
  window.App.features = {
    computeBMI,
    computeAgeGroup,
    computeLifestyleRisk,
    computeCityTier,
    CATEGORY_COPY
  };
})();