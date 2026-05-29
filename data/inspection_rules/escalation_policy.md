# Inspection Escalation Policy

## Rule ID: ESC-001
Category: Low Severity Issue
Condition: Minor issue with no immediate safety risk or production stop requirement.
Severity: Low
Required Action: Log the issue and notify the responsible team during routine review.
Human Review Required: No

## Rule ID: ESC-002
Category: Medium Severity Issue
Condition: Issue may affect process quality, worker compliance, or equipment condition but does not require immediate shutdown.
Severity: Medium
Required Action: Notify supervisor, correct the issue, and document the action taken.
Human Review Required: Yes

## Rule ID: ESC-003
Category: High Severity Issue
Condition: Issue creates immediate safety risk, equipment damage risk, or serious product quality risk.
Severity: High
Required Action: Stop work or block product release until the issue is reviewed and corrected.
Human Review Required: Yes

## Rule ID: ESC-004
Category: Repeated Violation
Condition: Same type of issue is detected repeatedly in the same area, machine, or process.
Severity: High
Required Action: Escalate to safety manager or quality manager for root cause analysis.
Human Review Required: Yes

## Rule ID: ESC-005
Category: Unclear Visual Evidence
Condition: The AI system cannot confidently determine whether a violation or defect is present.
Severity: Review Needed
Required Action: Mark the case for human review and do not make an automatic decision.
Human Review Required: Yes

## Rule ID: ESC-006
Category: Missing or Incomplete Input
Condition: Uploaded image is blurry, too dark, cropped, or does not show enough context for inspection.
Severity: Review Needed
Required Action: Request a clearer image or additional inspection evidence.
Human Review Required: Yes