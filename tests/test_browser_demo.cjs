"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { evaluateRule } = require("../web/app.js");

function payload(changes = {}) {
  return Object.assign({
    task_id: "DEMO-001",
    target_identifier: "SAMPLE-1",
    primary_metric: 10,
    secondary_metric: 5,
    status_descriptor: "NOMINAL",
    is_critical_flag: false
  }, changes);
}

test("nominal and exact thresholds do not trigger alerts", () => {
  const result = evaluateRule(payload({ primary_metric: 25, secondary_metric: 12 }));
  assert.equal(result.overall_urgency, "ROUTINE");
  assert.equal(result.total_alerts, 0);
  assert.equal(result.clinical_use, "NOT_VALIDATED_FOR_CLINICAL_USE");
});

test("anomaly, primary and secondary thresholds all count", () => {
  const result = evaluateRule(payload({
    primary_metric: 25.01, secondary_metric: 12.01, status_descriptor: "discordant"
  }));
  assert.equal(result.overall_urgency, "ELEVATED_RISK");
  assert.equal(result.total_alerts, 3);
});

test("manual critical flag raises critical urgency", () => {
  const result = evaluateRule(payload({ is_critical_flag: true }));
  assert.equal(result.overall_urgency, "CRITICAL_STAT_PANIC");
  assert.equal(result.critical_alerts_count, 1);
});

test("rejects invalid metrics and synthetic identifiers", () => {
  for (const bad of [-1, 1000.001, NaN, Infinity, "5"]) {
    assert.throws(() => evaluateRule(payload({ primary_metric: bad })));
  }
  assert.throws(() => evaluateRule(payload({ target_identifier: "jane@example.com" })));
  assert.throws(() => evaluateRule(payload({ task_id: "<script>" })));
  assert.throws(() => evaluateRule(payload({ status_descriptor: "DISCORDANT\nINJECT" })));
  assert.throws(() => evaluateRule(payload({ is_critical_flag: "false" })));
});
