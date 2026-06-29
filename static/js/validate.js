/* Client-side validation — mirrors schema/user_input.py */
(function () {
  const OCCUPATIONS = new Set([
    "retired", "freelancer", "student", "government_job",
    "business_owner", "unemployed", "private_job"
  ]);

  function isFiniteNumber(v) {
    return typeof v === "number" && Number.isFinite(v);
  }

  function validate(formData) {
    const errors = {};
    const { age, weight, height, income_lpa, occupation, smoker, city } = formData;

    // age: int 1..119
    if (!isFiniteNumber(age) || !Number.isInteger(age)) {
      errors.age = "Enter a whole number.";
    } else if (age < 1 || age > 119) {
      errors.age = "Age must be between 1 and 119.";
    }

    // weight > 0
    if (!isFiniteNumber(weight) || weight <= 0) {
      errors.weight = "Weight must be greater than 0.";
    }

    // height 0.5..2.5
    if (!isFiniteNumber(height)) {
      errors.height = "Enter your height in meters.";
    } else if (height < 0.5 || height > 2.5) {
      errors.height = "Height must be between 0.5 m and 2.5 m.";
    }

    // income_lpa > 0
    if (!isFiniteNumber(income_lpa) || income_lpa <= 0) {
      errors.income_lpa = "Income must be greater than 0.";
    }

    // occupation in allowed literals
    if (!OCCUPATIONS.has(occupation)) {
      errors.occupation = "Pick an occupation.";
    }

    // smoker must be boolean
    if (typeof smoker !== "boolean") {
      errors.smoker = "Choose Yes or No.";
    }

    // city non-empty (server validates against the city list)
    if (typeof city !== "string" || city.trim() === "") {
      errors.city = "Enter your city.";
    }

    return { valid: Object.keys(errors).length === 0, errors };
  }

  window.App = window.App || {};
  window.App.validate = validate;
})();