Phase 1: Correctness and Risk Reduction
Goal: Eliminate defects, inconsistent logic, and security risks before any structural or feature work.

Correct the confidence field naming inconsistency between model/predict.py and the Streamlit consumer.

Resolve the lifestyle_risk rule mismatch between training and inference logic, then retrain the model.

Ensure response_model=Output is either actively enforced in app.py or removed if unused.

Replace direct exception exposure in app.py with sanitized client-facing errors and server-side logging.

Remove unused imports from the application codebase.

Phase 2: Shared Business Logic
Goal: Consolidate duplicated logic and establish a single source of truth for reusable rules.

Centralize city-tier definitions in one shared module.

Extract feature engineering logic into a reusable module for both training and serving paths.

Align bmi, age_group, lifestyle_risk, and city_tier computation across the pipeline.

Store model version metadata alongside the trained artifact instead of maintaining it as a manual constant.

Introduce a project configuration standard such as pyproject.toml and treat dependency files as generated or managed outputs.

Phase 3: Data Integrity and Model Governance
Goal: Improve reproducibility, traceability, and validation of model training.

Vendor or version the training dataset locally to remove dependency on a live external source.

Persist training and evaluation metrics after each retrain.

Add automated post-training validation checks for minimum performance thresholds and class coverage.

Verify label alignment between training data and inference-time output classes.

Establish regression safeguards for model artifact behavior across refactors.

Phase 4: API Robustness and Operational Readiness
Goal: Make the service reliable, observable, and safe for downstream consumers.

Add CORS support for browser-based clients and the Streamlit frontend.

Externalize the API endpoint configuration instead of hardcoding it.

Validate city input explicitly and return clear errors for unsupported values.

Add structured logging for request metadata, latency, predictions, and confidence scores.

Expose operational metrics such as request counts and health status.

Harden the container by running as non-root, adding health checks, and pinning the base image.

Phase 5: Frontend Resilience and UX
Goal: Improve user experience and make the UI resilient to backend failures.

Handle API failures gracefully in the Streamlit frontend, including non-200 responses and malformed payloads.

Display derived model features such as BMI, age group, lifestyle risk, and city tier.

Add concise explanatory text for each predicted premium category.

Phase 6: Testing and Continuous Integration
Goal: Lock in expected behavior and prevent regressions through automation.

Add unit tests for schema validation and feature computation.

Add contract tests for the prediction endpoint.

Add regression tests for model output stability.

Implement CI to run tests, install dependencies, and build the container image.

Phase 7: Repository Hygiene and Documentation
Goal: Improve maintainability, onboarding, and long-term project clarity.

Stop tracking generated model artifacts in version control.

Normalize dependency file encoding for readability and tooling compatibility.

Add a comprehensive README.md covering architecture, setup, deployment, and usage examples.

Expand .gitignore to include environment files, virtual environments, caches, and IDE metadata.

Add a license file.

Document the API contract with request and response schemas, examples, and error cases.

Add docstrings to public functions and schema modules.

Recommended Delivery Sequence
Correctness and risk reduction.

Shared business logic.

Data integrity and model governance.

API robustness and operational readiness.

Testing and CI.

Frontend resilience and UX.

Repository hygiene and documentation.