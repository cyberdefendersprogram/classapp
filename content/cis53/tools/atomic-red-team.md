# Atomic Red Team

Atomic Red Team is a free library of small, mapped tests from Red Canary. Each "atomic" runs one MITRE ATT&CK technique on a host (for example T1059.001, PowerShell) so you can check whether your logging and detections notice it. It answers the question every detection engineer must ask: **"If this technique happened here, would we see it?"**

## Overview

Atomic Red Team is useful for:
- **Detection validation**: run a technique, then look for the alert or log line you expected (Roddie, Ch. 9)
- **Finding gaps**: a technique that leaves no trace in your telemetry is a gap, not a pass
- **Purple teaming**: the tester and the defender work from the same ATT&CK ID
- **Regression tests**: rerun the same atomics after you change a rule or an agent

Each atomic is a YAML entry with a description, the **executor** (PowerShell, cmd, bash), any **input arguments**, **prerequisites**, and a **cleanup** command. The tests are small on purpose. They are not malware, but many of them do exactly what malware does, so security tools will often block or flag them.

**Safety note:** run atomics only on a lab VM you own or that we provide, never on your own daily-use computer or a production system. Read the command with `-ShowDetails` before you run it, and run the cleanup afterward. Some tests change settings, create users, or disable protections.

### Installation (Windows lab VM, PowerShell)

```powershell
# 1. Install the execution framework and the atomics folder (follow the project README for the current command)
#    https://github.com/redcanaryco/invoke-atomicredteam
IEX (IWR 'https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install-atomicredteam.ps1' -UseBasicParsing)
Install-AtomicRedTeam -getAtomics

# 2. Load the module
Import-Module "C:\AtomicRedTeam\invoke-atomicredteam\Invoke-AtomicRedTeam.psd1" -Force

# Verify
Invoke-AtomicTest T1059.001 -ShowDetailsBrief
```

Windows Defender may remove the atomics folder or block tests. On a disposable lab VM only, the project documents adding an exclusion for the atomics folder. Do not do this on a real machine. Linux and macOS atomics use `bash`; see the project's README for the supported setup.

## Basic Syntax

```powershell
Invoke-AtomicTest T1059.001 -ShowDetailsBrief      # list the tests for a technique
Invoke-AtomicTest T1059.001 -TestNumbers 1 -ShowDetails   # read exactly what test 1 will do
Invoke-AtomicTest T1059.001 -TestNumbers 1 -CheckPrereqs  # are the prerequisites present?
Invoke-AtomicTest T1059.001 -TestNumbers 1 -GetPrereqs    # install them (read what it installs first)
Invoke-AtomicTest T1059.001 -TestNumbers 1                # run the test
Invoke-AtomicTest T1059.001 -TestNumbers 1 -Cleanup       # undo what it changed
```

:::command-builder{id="atomic-builder"}
tool_name: Invoke-AtomicTest
target_placeholder: "T1059.001"
scan_types:
  - name: "List the Tests for a Technique"
    flag: "-ShowDetailsBrief"
    desc: "Safe. Shows test numbers and names, runs nothing"
  - name: "Read a Test Before You Run It"
    flag: "-TestNumbers 1 -ShowDetails"
    desc: "Safe. Prints the exact command, the input arguments and the cleanup. Always do this first"
  - name: "Check Prerequisites"
    flag: "-TestNumbers 1 -CheckPrereqs"
    desc: "Reports what the test needs and whether it is present. Runs nothing from the test itself"
  - name: "Run a Test"
    flag: "-TestNumbers 1"
    desc: "Executes the technique on this host. Lab VM only"
  - name: "Clean Up After a Test"
    flag: "-TestNumbers 1 -Cleanup"
    desc: "Runs the atomic's cleanup command: removes files, users or settings the test created"
options:
  - name: "Write the Run to a Log"
    flag: "-LoggingModule Default-ExecutionLogger"
    desc: "Records what was run and when, so you can line it up with your alerts afterward"
:::

---

:::scenario{id="scenario-1" level="beginner"}
title: "Read Before You Run"
goal: "Pick the ATT&CK technique for PowerShell (T1059.001) and read what its first test would do, without running it."
hint: "-ShowDetailsBrief lists the tests. -ShowDetails shows the command. A test you have not read is a test you should not run."
command: "Invoke-AtomicTest T1059.001 -TestNumbers 1 -ShowDetails"
expected_output: |
  [********BEGIN TEST*******]
  Technique: Command and Scripting Interpreter: PowerShell T1059.001
  Atomic Test Name: <name of test 1>
  Executor: <powershell or command_prompt>
  Command: <the exact command it will run>
  Cleanup Command: <what it undoes, if anything>
  [!!!!!!!!END TEST!!!!!!!]
  (names and commands depend on the current atomics release)
:::

:::scenario{id="scenario-2" level="intermediate"}
title: "Run One Test and Find It in the Logs"
goal: "On the lab VM, run one atomic and find the evidence it left. Write down the timestamp, the process name and the command line."
hint: "Note the time before you run. Then look in Windows Event Viewer (Security 4688 process creation if command-line auditing is on, or Sysmon Event ID 1, or PowerShell 4104 script block logging) for the same minute. If nothing is there, your logging is off, and that is a finding."
command: "Invoke-AtomicTest T1059.001 -TestNumbers 1"
expected_output: |
  Executing test: T1059.001-1 <test name>
  Done executing test: T1059.001-1 <test name>
  (then look in your logs for the matching event)
:::

:::scenario{id="scenario-3" level="intermediate"}
title: "Pass, Gap, or Noise?"
goal: "Your rule is supposed to alert on this technique. After you run the atomic, decide which of three results you have."
hint: "Alert fired with the right technique: pass. Telemetry exists but no alert: rule gap. No telemetry at all: visibility gap (fix logging first). Alert fired on harmless activity too: noise (tune it). Always run the cleanup afterward."
command: "Invoke-AtomicTest T1059.001 -TestNumbers 1 -Cleanup"
expected_output: |
  Executing cleanup for test: T1059.001-1 <test name>
  Done executing cleanup for test: T1059.001-1 <test name>
:::

---

## A Validation Record

For every technique you test, keep one row:

| ATT&CK ID | Test | Expected detection | What we saw | Result | Fix |
|---|---|---|---|---|---|
| T1059.001 | 1 | Alert on encoded PowerShell | Event 4104 logged, no alert | Rule gap | Add a rule on the 4104 content |

Rerun the row after you fix it. A result you cannot repeat is not evidence.

## Atomic Red Team and Network Detection

Many atomics are host-only, so they test endpoint logging more than a network sensor. Some produce traffic: DNS lookups, HTTP downloads, a connection to a test server. Capture on the lab network while you run those, and compare what the sensor saw with what the host logged. Where the traffic is encrypted, the network side may see only the destination and timing (see the TLS metadata notes).

## Use in This Course

- **Reading:** Roddie et al., *Practical Threat Detection Engineering*, Ch. 9 (Detection Validation, with Atomic Red Team and CALDERA) is optional reading for Class 5.
- **Companion tools:** [Scapy](/tools/scapy) tests a rule with crafted packets; [CALDERA](/tools/caldera) chains techniques into an automated operation; Atomic Red Team runs one technique at a time.
- **Final project and case studies:** if you propose a detection, say how you would validate it with an atomic or a pcap.

:::quiz{id="quiz-1"}
Q: What should you do before you run an atomic test?
- [ ] Disable all logging so the test runs cleanly
- [x] Read what it will do with -ShowDetails, and know how to clean it up
- [ ] Run it on your own laptop to save time
- [ ] Skip the prerequisites check
:::

:::quiz{id="quiz-2"}
Q: You ran a test and found no log line for it at all. What does that most likely mean?
- [ ] The detection passed
- [ ] The test did not run
- [x] A visibility gap: the activity is not being logged, so fix the logging before the rule
- [ ] The technique is harmless
:::

:::quiz{id="quiz-3"}
Q: What is the main difference between Atomic Red Team and Scapy for validating detections?
- [x] Atomic Red Team runs an ATT&CK technique on a host; Scapy crafts packets to test a network rule
- [ ] Atomic Red Team only works offline
- [ ] Scapy runs techniques on hosts
- [ ] There is no difference
:::
