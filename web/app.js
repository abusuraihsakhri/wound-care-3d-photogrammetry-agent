/* Local-only demonstration of the existing server-side rule thresholds. */
(function (root) {
  "use strict";

  function validateIdentifier(value, name) {
    if (typeof value !== "string" || !/^[A-Za-z0-9_.-]{1,64}$/.test(value)) {
      throw new Error(name + " must be 1-64 letters, digits, dots, dashes or underscores (synthetic IDs only).");
    }
    return value;
  }

  function validateMetric(value, name) {
    if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 1000) {
      throw new Error(name + " must be a finite number from 0 to 1000.");
    }
    return value;
  }

  function evaluateRule(input) {
    if (!input || typeof input !== "object") {
      throw new Error("An evaluation payload is required.");
    }
    const taskId = validateIdentifier(input.task_id, "Task ID");
    const targetId = validateIdentifier(input.target_identifier, "Target ID");
    const primary = validateMetric(input.primary_metric, "Primary metric");
    const secondary = validateMetric(input.secondary_metric, "Secondary metric");
    if (typeof input.status_descriptor !== "string" ||
        !/^[A-Za-z0-9_.-]{1,64}$/.test(input.status_descriptor)) {
      throw new Error("Status descriptor must contain 1-64 synthetic code characters.");
    }
    if (typeof input.is_critical_flag !== "boolean") {
      throw new Error("Critical flag must be a boolean.");
    }
    const alerts = [];

    if (primary > 25) {
      alerts.push({
        worker: "InvariantQCWorker",
        urgency: "ELEVATED_RISK",
        summary: "Primary metric above the example threshold of 25",
        observed_value: primary
      });
    }
    if (input.is_critical_flag || secondary > 12) {
      alerts.push({
        worker: "SafetyEscalationWorker",
        urgency: input.is_critical_flag ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
        summary: "Explicit critical flag or secondary metric above 12",
        observed_value: secondary
      });
    }
    if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"]
      .some(function (term) { return input.status_descriptor.toUpperCase().includes(term); })) {
      alerts.push({
        worker: "ProtocolConformanceWorker",
        urgency: "ELEVATED_RISK",
        summary: "Status descriptor matched a demonstration anomaly keyword"
      });
    }
    const criticalCount = alerts.filter(function (a) { return a.urgency === "CRITICAL_STAT_PANIC"; }).length;
    const urgency = criticalCount ? "CRITICAL_STAT_PANIC" : alerts.length ? "ELEVATED_RISK" : "ROUTINE";
    return {
      mode: "LOCAL_RULE_DEMONSTRATION",
      clinical_use: "NOT_VALIDATED_FOR_CLINICAL_USE",
      task_id: taskId,
      target_identifier: targetId,
      primary_metric: primary,
      secondary_metric: secondary,
      status_descriptor: input.status_descriptor,
      is_critical_flag: input.is_critical_flag,
      overall_urgency: urgency,
      integrity_status: criticalCount ? "RECALIBRATION_REQUIRED" :
        alerts.length ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
      total_alerts: alerts.length,
      critical_alerts_count: criticalCount,
      alerts: alerts,
      note: "Example thresholds only. No photogrammetry, tissue segmentation, PUSH calculation, HMAC signature or clinical diagnosis."
    };
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { evaluateRule: evaluateRule };
  }

  if (typeof document === "undefined") { return; }

  function setup() {
    const form = document.getElementById("audit-form");
    const output = document.getElementById("output");
    const message = document.getElementById("message");
    const download = document.getElementById("download");
    let latestResult = null;
    let processed = 0;

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      latestResult = null;
      download.disabled = true;
      try {
        const result = evaluateRule({
          task_id: document.getElementById("task_id").value.trim(),
          target_identifier: document.getElementById("target_id").value.trim(),
          primary_metric: Number(document.getElementById("primary_metric").value),
          secondary_metric: Number(document.getElementById("secondary_metric").value),
          status_descriptor: document.getElementById("status_descriptor").value.trim(),
          is_critical_flag: document.getElementById("is_critical").checked
        });
        // Empty number input must be rejected; Number("") would otherwise yield zero.
        if (!document.getElementById("primary_metric").value.trim() ||
            !document.getElementById("secondary_metric").value.trim()) {
          throw new Error("Both metric fields are required.");
        }
        latestResult = result;
        processed += 1;
        document.getElementById("processed-count").textContent = String(processed);
        document.getElementById("alert-count").textContent = String(result.total_alerts);
        message.textContent = "Local evaluation completed. No data was transmitted.";
        output.textContent = JSON.stringify(result, null, 2);
        download.disabled = false;
      } catch (error) {
        message.textContent = "Validation failed: " + error.message;
        output.textContent = "Correct the input fields and run the demonstration again.";
        document.getElementById("alert-count").textContent = "—";
      }
    });

    download.addEventListener("click", function () {
      if (!latestResult) { return; }
      const blob = new Blob([JSON.stringify(latestResult, null, 2) + "\n"], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "wound-audit-demo.json";
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 0);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup, { once: true });
  } else {
    setup();
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
