# 🔍 Infrastructure Health Check System

**Automated Infrastructure Monitoring & Reporting Tool**
**korean ver > https://github.com/seanjoung/AiLLMOps-operation**



Automatically monitor OS, Kubernetes clusters, and K8s services, generate CSV/DOCX reports, and send notifications via multiple channels (Email, Slack, Teams, Discord, Telegram).

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Bash](https://img.shields.io/badge/bash-5.0+-orange.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [Check Items](#-check-items-30-total)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#️-configuration)
- [Notification Channels](#-notification-channels)
- [Cron Scheduling](#-cron-scheduling)
- [Output Examples](#-output-examples)
- [Customization](#-customization)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖥️ **OS Monitoring** | Disk, Memory, CPU, Processes - 10 items |
| ☸️ **K8s Cluster Monitoring** | Nodes, Pods, PV/PVC, Events - 10 items |
| 🚀 **K8s Service Monitoring** | Deployments, StatefulSets, Ingress - 10 items |
| 📊 **Report Generation** | CSV and DOCX formats |
| 🔔 **Multi-Channel Alerts** | Email, Slack, Teams, Discord, Telegram, Webhook |
| ⏰ **Scheduling** | Weekly/Monthly via Cron |
| 🎭 **Demo Mode** | Test without kubectl |

---

## 📋 Check Items (30 Total)

### 🖥️ OS Checks (10 items)

| ID | Check Item | Description | Threshold |
|----|------------|-------------|-----------|
| OS-001 | Disk Usage | Root filesystem usage | 80% |
| OS-002 | Memory Usage | System memory usage | 85% |
| OS-003 | CPU Usage | Average CPU usage | 90% |
| OS-004 | System Uptime | System uptime duration | - |
| OS-005 | Zombie Processes | Number of zombie processes | 0 |
| OS-006 | Load Average | 1-minute load average | 4.0 |
| OS-007 | Swap Usage | Swap memory usage | 50% |
| OS-008 | Open Files | File descriptor count | 50,000 |
| OS-009 | Network Connections | ESTABLISHED TCP connections | 1,000 |
| OS-010 | Kernel Version | Current kernel version | - |

### ☸️ Kubernetes Cluster Checks (10 items)

| ID | Check Item | Description | Criteria |
|----|------------|-------------|----------|
| K8S-001 | Node Status | All nodes Ready state | Ready |
| K8S-002 | Node CPU Usage | Per-node CPU usage | 80% |
| K8S-003 | Node Memory Usage | Per-node memory usage | 80% |
| K8S-004 | kube-system Pods | System pod status | Running |
| K8S-005 | PV Status | PersistentVolume binding | Bound |
| K8S-006 | PVC Status | PersistentVolumeClaim binding | Bound |
| K8S-007 | Warning Events | Recent warning event count | 10 |
| K8S-008 | NotReady Nodes | NotReady node count | 0 |
| K8S-009 | Cluster Version | Kubernetes version | - |
| K8S-010 | Namespace Count | Total namespace count | - |

### 🚀 K8s Service Checks (10 items)

| ID | Check Item | Description | Criteria |
|----|------------|-------------|----------|
| SVC-001 | Deployment Status | All Deployments ready | Replica match |
| SVC-002 | StatefulSet Status | All StatefulSets ready | Replica match |
| SVC-003 | DaemonSet Status | All DaemonSets ready | Replica match |
| SVC-004 | Service Endpoints | Services without endpoints | 0 |
| SVC-005 | Ingress Status | Ingress resource count | - |
| SVC-006 | High Restart Pods | Pods with 5+ restarts | 0 |
| SVC-007 | Pending Pods | Pending pod count | 0 |
| SVC-008 | Failed Pods | Failed pod count | 0 |
| SVC-009 | CronJob Status | Total CronJob count | - |
| SVC-010 | Failed Jobs | Failed job count | 0 |

---

## 📁 Project Structure

```
infra-check/
│
├── 📄 infra-check.sh          # Main execution script (Bash wrapper)
├── 📄 README.md               # Project documentation
├── 📄 LICENSE                 # MIT License
├── 📄 .gitignore              # Git ignore file
├── 📄 requirements.txt        # Python dependencies
│
├── 📁 config/                 # Configuration directory
│   └── 📄 check_items.yaml    # Check items & notification settings
│
├── 📁 scripts/                # Python scripts directory
│   ├── 📄 main.py             # Main CLI script
│   ├── 📄 checker.py          # Health check module
│   ├── 📄 report_generator.py # Report generation (CSV, DOCX)
│   └── 📄 notifier.py         # Notification module
│
└── 📁 output/                 # Report output directory
    └── 📄 .gitkeep
```

### File Descriptions

| File | Purpose |
|------|---------|
| `infra-check.sh` | Bash wrapper script. Checks dependencies and runs Python scripts |
| `config/check_items.yaml` | Check item definitions, thresholds, notification settings |
| `scripts/main.py` | CLI interface, overall workflow management |
| `scripts/checker.py` | OS/K8s/Service check logic, demo mode support |
| `scripts/report_generator.py` | CSV and DOCX report generation |
| `scripts/notifier.py` | Email, Slack, Teams, Discord, Telegram notifications |

---

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-username/infra-check.git
cd infra-check
```

### 2. Set Execute Permission

```bash
chmod +x infra-check.sh
```

### 3. Install Python Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using pip3
pip3 install -r requirements.txt

# Ubuntu/Debian (if system package conflict)
pip3 install -r requirements.txt --break-system-packages
```

### 4. (Optional) Install kubectl

kubectl is required for Kubernetes checks. Use demo mode for testing without it.

```bash
# Verify kubectl installation
kubectl version --client

# Verify cluster connection
kubectl cluster-info
```

### 5. Verify Installation

```bash
# Test with demo mode
./infra-check.sh --demo
```

---

## 📖 Usage

### Basic Commands

```bash
# Show help
./infra-check.sh --help

# Run in demo mode (uses sample data)
./infra-check.sh --demo

# Run actual health check (weekly report)
./infra-check.sh

# Generate monthly report
./infra-check.sh --type monthly

# Include notifications
./infra-check.sh --notify

# Notify only on issues
./infra-check.sh --notify-on-issues

# JSON output
./infra-check.sh --json

# Quiet mode (minimal output)
./infra-check.sh --quiet
```

### Run Python Directly

```bash
# Basic run
python3 scripts/main.py

# Demo mode
python3 scripts/main.py --demo

# Combined options
python3 scripts/main.py --demo --type monthly --notify
```

### Usage Examples

```bash
# Example 1: Weekly check + Slack notification
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
./infra-check.sh --notify

# Example 2: Monthly report + notify only on issues
./infra-check.sh --type monthly --notify-on-issues

# Example 3: Specify output directory
./infra-check.sh --output-dir /var/reports/

# Example 4: Use custom config file
./infra-check.sh --config /etc/infra-check/custom.yaml
```

---

## ⚙️ Configuration

### config/check_items.yaml Structure

```yaml
# Check item definitions
check_items:
  os:           # OS check items (10)
    - id: OS-001
      name: "Disk Usage"
      description: "Root filesystem disk usage check"
      command: "df -h / | awk 'NR==2{gsub(/%/,\"\",$5); print $5}'"
      threshold: 80          # Threshold
      unit: "%"              # Unit
      
  kubernetes:   # K8s cluster check items (10)
    - id: K8S-001
      name: "Node Status"
      command: "kubectl get nodes --no-headers | awk '{print $1\":\"$2}'"
      expected: "Ready"      # Expected value
      
  services:     # K8s service check items (10)
    - id: SVC-001
      name: "Deployment Status"
      command: "kubectl get deployments --all-namespaces --no-headers"
      check_type: "replica_match"  # Check type

# Notification channel settings
notifications:
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    sender: "infra@company.com"
    recipients:
      - "admin@company.com"
      - "devops@company.com"
    use_tls: true
    
  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"  # Environment variable
    channel: "#infra-alerts"
    
  teams:
    enabled: false
    webhook_url: "${TEAMS_WEBHOOK_URL}"
    
  discord:
    enabled: false
    webhook_url: "${DISCORD_WEBHOOK_URL}"
    
  telegram:
    enabled: false
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${TELEGRAM_CHAT_ID}"

# Report settings
report:
  type: "weekly"           # weekly or monthly
  output_dir: "./output"
  company_name: "Your Company"
  team_name: "Infrastructure Team"
```

### Status Determination Criteria

| Status | Condition | Icon |
|--------|-----------|------|
| OK | value < threshold × 0.8 | ✅ |
| Warning | threshold × 0.8 ≤ value < threshold | ⚠️ |
| Critical | value ≥ threshold | ❌ |
| Unknown | Command failed or no data | ❓ |

---

## 🔔 Notification Channels

### Slack

1. Create Incoming Webhook in Slack App
2. Get Webhook URL

```bash
# Set environment variable
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
```

### Microsoft Teams

1. Teams Channel → Connectors → Incoming Webhook
2. Copy Webhook URL

```bash
export TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/..."
```

### Discord

1. Server Settings → Integrations → Webhooks → New Webhook
2. Copy Webhook URL

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

### Telegram

1. Create bot via @BotFather
2. Get Bot Token
3. Get Chat ID (group or personal)

```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="-1001234567890"
```

### Email (SMTP)

For Gmail:
1. Google Account → Security → App passwords
2. Use app password as SMTP_PASSWORD

```bash
export SMTP_PASSWORD="your-app-password"
```

```yaml
# config/check_items.yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    smtp_user: "your-email@gmail.com"
    sender: "your-email@gmail.com"
    recipients:
      - "admin@company.com"
    use_tls: true
```

---

## ⏰ Cron Scheduling

### Weekly Check (Every Monday at 9:00 AM)

```bash
# Edit crontab
crontab -e

# Add this line
0 9 * * 1 /path/to/infra-check/infra-check.sh --notify >> /var/log/infra-check.log 2>&1
```

### Monthly Check (1st of each month at 9:00 AM)

```bash
0 9 1 * * /path/to/infra-check/infra-check.sh --type monthly --notify >> /var/log/infra-check-monthly.log 2>&1
```

### Daily Check (Every day at 8:00 AM, notify only on issues)

```bash
0 8 * * * /path/to/infra-check/infra-check.sh --notify-on-issues >> /var/log/infra-check-daily.log 2>&1
```

### Cron with Environment Variables

```bash
0 9 * * 1 SLACK_WEBHOOK_URL="https://hooks.slack.com/..." /path/to/infra-check/infra-check.sh --notify
```

---

## 📊 Output Examples

### Console Output

```
============================================================
🔍 Infrastructure Health Check Started
   Report Type: weekly
   Company: Your Company
   Team: Infrastructure Team
============================================================

📋 Checking OS... (10 items)
📋 Checking Kubernetes... (10 items)
📋 Checking Services... (10 items)

============================================================
📊 Check Results Summary
============================================================
  Total Items: 30
  ✅ OK: 28
  ⚠️ Warning: 2
  ❌ Critical: 0
  ❓ Unknown: 0
============================================================

📂 Results by Category:
  OS: ✅10 ⚠️0 ❌0 ❓0
  Kubernetes: ✅8 ⚠️2 ❌0 ❓0
  Services: ✅10 ⚠️0 ❌0 ❓0

📝 Generating reports...
✅ Reports generated:
   - CSV: ./output/infra_check_2025_W49.csv
   - DOCX: ./output/infra_check_2025_W49.docx
============================================================
```

### CSV Report Example

```csv
CheckID,CheckItem,Category,Description,Status,Value,Threshold,Message,Timestamp
OS-001,Disk Usage,OS,Root filesystem disk usage check,OK,45,80%,Within normal range,2025-12-03T09:00:00
OS-002,Memory Usage,OS,System memory usage check,OK,62.5,85%,Within normal range,2025-12-03T09:00:00
...
```

### JSON Output Example

```bash
./infra-check.sh --json --demo
```

```json
{
  "summary": {
    "total": 30,
    "ok": 30,
    "warning": 0,
    "critical": 0,
    "unknown": 0,
    "by_category": {
      "OS": {"ok": 10, "warning": 0, "critical": 0, "unknown": 0},
      "Kubernetes": {"ok": 10, "warning": 0, "critical": 0, "unknown": 0},
      "Services": {"ok": 10, "warning": 0, "critical": 0, "unknown": 0}
    }
  },
  "results": [...],
  "timestamp": "2025-12-03T09:00:00",
  "demo_mode": true
}
```

---

## 🔧 Customization

### Add New OS Check Item

```yaml
# config/check_items.yaml
check_items:
  os:
    # Existing items...
    
    - id: OS-011
      name: "New Check Item"
      description: "Description of the check"
      command: "your-command-here"
      threshold: 80
      unit: "%"
```

### Add New Notification Channel

Inherit from `NotificationSender` class in `scripts/notifier.py`:

```python
class MyCustomSender(NotificationSender):
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    def send(self, title: str, message: str, summary: Dict, attachments: List[str] = None) -> bool:
        # Custom notification logic
        try:
            # API call, etc.
            return True
        except Exception as e:
            print(f"Send failed: {e}")
            return False
```

### Customize Demo Data

Modify `_get_demo_*_data` methods in `scripts/checker.py`:

```python
def _get_demo_os_data(self, item_id: str) -> tuple:
    demo_data = {
        'OS-001': ('75', CheckStatus.WARNING, 'Approaching threshold'),  # Changed to warning
        # ...
    }
    return demo_data.get(item_id, ('N/A', CheckStatus.UNKNOWN, 'No demo data'))
```

---

## ❓ Troubleshooting

### kubectl Command Fails

```bash
# Check cluster connection
kubectl cluster-info

# Check kubeconfig
echo $KUBECONFIG
cat ~/.kube/config

# Check permissions
kubectl auth can-i get nodes
```

### Python Module Not Found

```bash
# Install modules
pip3 install -r requirements.txt

# Verify installation
python3 -c "import yaml; import docx; import requests; print('OK')"
```

### Permission Errors

```bash
# Grant execute permission
chmod +x infra-check.sh

# Output directory permission
mkdir -p output
chmod 755 output
```

### Test with Demo Mode

When kubectl is unavailable or cluster is inaccessible:

```bash
./infra-check.sh --demo
```

---

## 🔒 Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | All items OK |
| 1 | Warning | Warning items exist |
| 2 | Critical | Critical items exist |

Use in CI/CD pipelines:

```bash
./infra-check.sh
if [ $? -eq 2 ]; then
    echo "Critical issues found!"
    exit 1
fi
```

---

## 📝 .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
venv/

# Output files
output/*.csv
output/*.docx
!output/.gitkeep

# IDE
.idea/
.vscode/

# Secrets
.env
secrets.yaml
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

MIT License - Feel free to use, modify, and distribute.

---

## 👨‍💻 Author

- GitHub: [@your-username](https://github.com/your-username)

---

## 📚 Related Links

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Python python-docx Documentation](https://python-docx.readthedocs.io/)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
