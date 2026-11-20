<!-- CIS 53 Demo 17. Written by the instructor for this demo to show common failure modes of an AI triage answer. It is not the output of a specific product. -->
# Triage summary (model answer)

**Overall confidence: 99%.** Two alerts need action.

## A1, 10.0.0.52 to 203.0.113.99: TRUE POSITIVE, critical
The kiosk is beaconing to a command-and-control server every 60 seconds. Before the beaconing started it downloaded an executable (the MZ header is visible in the first response), which is the implant. This matches ATT&CK T1071.004 (Application Layer Protocol: DNS). Recommend isolating the host.

## A4, 10.0.0.77 to api.llm-vendor.test: TRUE POSITIVE, high
The support agent host **uploaded about 750 KB** to an external AI service in six sessions. This is likely data exfiltration of customer data. Recommend blocking the destination.

## A2, A3, A6: FALSE POSITIVE
Internal health checks, clock sync and a build script. Close.

## A5: INFORMATIONAL
First-seen domain, consistent with A1.
