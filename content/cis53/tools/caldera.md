# CALDERA

CALDERA is MITRE's open-source adversary-emulation platform. You run a server, install small agents on lab machines, and tell the server to run an **adversary profile**: an ordered set of ATT&CK techniques. It then carries them out automatically and records what happened. Where Atomic Red Team runs one technique at a time, CALDERA runs a whole attack chain, so you can see whether your detections catch the **sequence**, not just a single step.

## Overview

CALDERA is useful for:
- **Testing a chain of detections**: discovery, then credential access, then lateral movement, all in one run
- **Repeatable exercises**: the same adversary profile, run again after you tune a rule
- **Purple teaming**: the operation log lists every ability, its ATT&CK ID and its time, ready to compare with your alerts
- **Automated validation**: run on a schedule to catch a detection that silently stopped working

Key terms:
- **Agent**: software on a target host that asks the server what to do (the default agent is called Sandcat).
- **Ability**: one action tied to an ATT&CK technique (a command plus its executor).
- **Adversary profile**: an ordered group of abilities.
- **Operation**: a run of a profile against a group of agents.
- **Fact**: something the operation learned (a user name, a host) that later abilities can use.

**Safety note:** CALDERA gives the server remote command execution on every agent. Run it only on an isolated lab network with machines you own or that we provide. Never expose the server to the internet, never install an agent on a computer you use for anything else, and never use the default passwords on a network others can reach.

### Installation (Linux or macOS lab host)

```bash
# Check the project README first: https://github.com/mitre/caldera (requirements change between versions)
git clone https://github.com/mitre/caldera.git --recursive
cd caldera
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start the server (the first start builds the web interface and can take a few minutes)
python3 server.py --insecure --build
```

Open `http://localhost:8888`. The `--insecure` flag loads a development configuration with well-known default credentials, so use it only on an isolated lab host that nothing else can reach. Credentials are printed or set in the configuration file; check the README for your version.

To run the server in a container instead, the project provides a Dockerfile. Same safety rule: lab network only.

## Basic Workflow

1. **Start the server** and sign in as the red-team user.
2. **Deploy an agent** (Agents page, Deploy an agent): choose the platform, copy the generated one-line command, and run it **on the lab VM**. The agent appears in the list and checks in every few seconds.
3. **Pick an adversary profile** (Adversary page). Start with a small, discovery-only one.
4. **Create an operation** (Operations page): choose the group of agents and the profile. Leave the obfuscation setting and the planner at the defaults to begin with.
5. **Run it and watch.** Each ability shows its status, output, and ATT&CK ID.
6. **Compare** the operation log with your alerts, then **tune**, then run again.

:::command-builder{id="caldera-builder"}
tool_name: "python3 server.py"
target_placeholder: ""
scan_types:
  - name: "Start the Server (lab only, default config)"
    flag: "--insecure"
    desc: "Development configuration with default credentials. Isolated lab host only"
  - name: "Start and Build the Web Interface"
    flag: "--insecure --build"
    desc: "Needed on first start (and after updates) to build the UI"
  - name: "Start With Debug Logging"
    flag: "--insecure --log DEBUG"
    desc: "More detail when an agent does not check in"
options:
  - name: "Use Your Own Configuration"
    flag: "-E local"
    desc: "Loads conf/local.yml, where you set your own users and passwords (recommended beyond a single throwaway lab VM)"
:::

---

:::scenario{id="scenario-1" level="beginner"}
title: "Read an Adversary Profile Before You Run It"
goal: "Open an adversary profile in the web interface and list its abilities in order, with their ATT&CK IDs and the command each will run."
hint: "Adversary page, choose a profile. For each ability, note the tactic, the technique ID and the executor. Which of these would your sensor or host logging see?"
command: "(in the web interface) Adversary -> select a profile -> read each ability"
expected_output: |
  A numbered list of abilities, each with a tactic (for example Discovery), an ATT&CK technique ID, and the command that will run on the agent.
:::

:::scenario{id="scenario-2" level="intermediate"}
title: "Run a Discovery Operation and Match the Log"
goal: "Run a discovery-only profile against one lab agent. For each ability in the operation log, find the matching event in your own logs or packet capture."
hint: "Write down the operation start time. Each ability has its own timestamp. Look for the same minute in Sysmon, Windows Security 4688, auditd, or a Zeek log. Abilities with no match are your visibility gaps."
command: "(in the web interface) Operations -> Create operation -> pick the agent group and a discovery profile -> Start"
expected_output: |
  An operation page where each ability turns from queued to success or fail, with its command output.
:::

:::scenario{id="scenario-3" level="intermediate"}
title: "Detect the Agent's Beacon"
goal: "The CALDERA agent checks in to the server on a timer. Capture traffic on the lab network and find the beacon."
hint: "This is the Class 5 hunting loop. Hypothesis: a host contacts one destination at regular intervals. Group by destination and look at the time between connections. A fixed interval with a little jitter is a classic beacon pattern, and a good example of an indicator that is easy for an attacker to change (Pyramid of Pain)."
command: "zeek -r lab-capture.pcap && cat conn.log | zeek-cut ts id.orig_h id.resp_h id.resp_p duration"
expected_output: |
  Rows from the agent host to the server address and port (8888 by default), repeating every few seconds.
:::

---

## CALDERA or Atomic Red Team?

| | Atomic Red Team | CALDERA |
|---|---|---|
| Unit of work | One technique | A chain of abilities (an operation) |
| Needs a server | No | Yes, plus an agent on each target |
| Good for | "Does this one detection work?" | "Do we catch the sequence, and how fast?" |
| Effort | Low | Higher setup, more realistic |
| Risk | Runs locally on one host | Remote command execution: isolate it |

Use Atomic Red Team to validate individual rules, then CALDERA to test how the rules work together.

## Pitfalls

- **Default credentials.** Change them for anything beyond a throwaway lab VM, and never expose port 8888 beyond the lab.
- **Antivirus removes the agent.** That is a result about your endpoint protection, not a CALDERA bug. Record it; on a lab VM you can add an exclusion for the agent.
- **Agent never checks in.** Check the server address in the one-line command, the firewall, and that the agent's host can reach port 8888 on the server.
- **Operations change hosts.** Some abilities create files, users or scheduled tasks. Read the profile first and use a snapshot you can revert.

## Use in This Course

- **Reading:** Roddie et al., *Practical Threat Detection Engineering*, Ch. 9 (Detection Validation: Atomic Red Team and CALDERA), optional for Class 5.
- **Hunting loop (Class 5):** the agent's regular check-in is the beacon you hunt in Demo 15.
- **Companion tools:** [Atomic Red Team](/tools/atomic-red-team) for single techniques; [Scapy](/tools/scapy) for crafted packets.

:::quiz{id="quiz-1"}
Q: What is a CALDERA operation?
- [ ] A single packet sent to a target
- [x] A run of an adversary profile (a chain of abilities) against a group of agents
- [ ] A type of detection rule
- [ ] The web interface login
:::

:::quiz{id="quiz-2"}
Q: Why must the CALDERA server stay on an isolated lab network?
- [ ] It uses too much bandwidth
- [x] It can run commands on every agent, and the development configuration has default credentials
- [ ] It only works offline
- [ ] Agents cannot reach the internet anyway
:::

:::quiz{id="quiz-3"}
Q: The agent checks in to the server every few seconds. Which hunting idea finds it?
- [ ] A hash lookup of the agent file
- [ ] An alert on the server's operating system
- [x] A query for hosts contacting one destination at regular intervals (beaconing)
- [ ] A list of all DNS names
:::
