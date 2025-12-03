#!/usr/bin/env python3
"""
Infrastructure Health Check Module
OS, Kubernetes, K8s Services health checks
Demo mode support - testable without kubectl
"""

import subprocess
import yaml
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum

class CheckStatus(Enum):
    OK = "OK"
    WARNING = "Warning"
    CRITICAL = "Critical"
    UNKNOWN = "Unknown"

@dataclass
class CheckResult:
    check_id: str
    name: str
    category: str
    description: str
    status: CheckStatus
    value: str
    threshold: Optional[float]
    unit: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    raw_output: str = ""

class InfraChecker:
    def __init__(self, config_path: str = "config/check_items.yaml", demo_mode: bool = False):
        self.config = self._load_config(config_path)
        self.results: List[CheckResult] = []
        self.demo_mode = demo_mode
        
    def _load_config(self, path: str) -> dict:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _run_command(self, command: str, timeout: int = 30) -> tuple:
        """Execute shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", -1
        except Exception as e:
            return "", str(e), -1
    
    def _check_kubectl_available(self) -> bool:
        """Check if kubectl is available"""
        if self.demo_mode:
            return True
        stdout, _, returncode = self._run_command("which kubectl")
        return returncode == 0
    
    def _evaluate_threshold(self, value: str, threshold: float, check_id: str) -> CheckStatus:
        """Determine status based on threshold"""
        try:
            numeric_value = float(value.replace('%', '').strip())
            
            # Items where 0 is OK
            zero_is_ok = ['OS-005', 'K8S-008', 'SVC-004', 'SVC-006', 'SVC-007', 'SVC-008', 'SVC-010']
            
            if check_id in zero_is_ok:
                if numeric_value == 0:
                    return CheckStatus.OK
                elif numeric_value <= 3:
                    return CheckStatus.WARNING
                else:
                    return CheckStatus.CRITICAL
            else:
                if numeric_value < threshold * 0.8:
                    return CheckStatus.OK
                elif numeric_value < threshold:
                    return CheckStatus.WARNING
                else:
                    return CheckStatus.CRITICAL
        except (ValueError, AttributeError):
            return CheckStatus.UNKNOWN
    
    def _get_demo_os_data(self, item_id: str) -> tuple:
        """OS check demo data"""
        demo_data = {
            'OS-001': ('45', CheckStatus.OK, 'Within normal range'),
            'OS-002': ('62.5', CheckStatus.OK, 'Within normal range'),
            'OS-003': ('23', CheckStatus.OK, 'Within normal range'),
            'OS-004': ('up 15 days, 4 hours, 32 minutes', CheckStatus.OK, 'System running normally'),
            'OS-005': ('0', CheckStatus.OK, 'No zombie processes'),
            'OS-006': ('1.25', CheckStatus.OK, 'Within normal range'),
            'OS-007': ('12.3', CheckStatus.OK, 'Within normal range'),
            'OS-008': ('3456', CheckStatus.OK, 'Within normal range'),
            'OS-009': ('128', CheckStatus.OK, 'Within normal range'),
            'OS-010': ('5.15.0-91-generic', CheckStatus.OK, 'Kernel info retrieved'),
        }
        return demo_data.get(item_id, ('N/A', CheckStatus.UNKNOWN, 'No demo data'))
    
    def _get_demo_k8s_data(self, item_id: str) -> tuple:
        """Kubernetes check demo data"""
        demo_data = {
            'K8S-001': ('master-01:Ready\nworker-01:Ready\nworker-02:Ready\nworker-03:Ready', 
                        CheckStatus.OK, 'All nodes healthy (4/4)'),
            'K8S-002': ('master-01:32%\nworker-01:45%\nworker-02:38%\nworker-03:52%', 
                        CheckStatus.OK, 'All node CPU within limits'),
            'K8S-003': ('master-01:58%\nworker-01:62%\nworker-02:55%\nworker-03:71%', 
                        CheckStatus.OK, 'All node memory within limits'),
            'K8S-004': ('coredns-5d78c9869d-abc12:Running\ncoredns-5d78c9869d-def34:Running\netcd-master-01:Running\nkube-apiserver-master-01:Running\nkube-controller-manager-master-01:Running\nkube-proxy-xxxxx:Running\nkube-scheduler-master-01:Running', 
                        CheckStatus.OK, 'All system pods healthy (7/7)'),
            'K8S-005': ('pv-data-01:Bound\npv-data-02:Bound\npv-logs-01:Bound', 
                        CheckStatus.OK, 'All PVs bound (3/3)'),
            'K8S-006': ('data-pvc-01:Bound\ndata-pvc-02:Bound\nlogs-pvc-01:Bound', 
                        CheckStatus.OK, 'All PVCs bound (3/3)'),
            'K8S-007': ('3', CheckStatus.OK, 'Warning events within threshold'),
            'K8S-008': ('0', CheckStatus.OK, 'No NotReady nodes'),
            'K8S-009': ('v1.28.4', CheckStatus.OK, 'Version info retrieved'),
            'K8S-010': ('8', CheckStatus.OK, '8 namespaces'),
        }
        return demo_data.get(item_id, ('N/A', CheckStatus.UNKNOWN, 'No demo data'))
    
    def _get_demo_svc_data(self, item_id: str) -> tuple:
        """Service check demo data"""
        demo_data = {
            'SVC-001': ('nginx-deployment:3/3\napi-server:2/2\nworker-deployment:5/5\nredis:1/1\npostgres:1/1', 
                        CheckStatus.OK, 'All Deployments healthy (5)'),
            'SVC-002': ('mysql:1/1\nredis:3/3\nelasticsearch:3/3', 
                        CheckStatus.OK, 'All StatefulSets healthy (3)'),
            'SVC-003': ('fluentd:4/4\nnode-exporter:4/4\nkube-proxy:4/4', 
                        CheckStatus.OK, 'All DaemonSets healthy (3)'),
            'SVC-004': ('0', CheckStatus.OK, 'No services without endpoints'),
            'SVC-005': ('5', CheckStatus.OK, '5 Ingress resources'),
            'SVC-006': ('0', CheckStatus.OK, 'No high-restart pods'),
            'SVC-007': ('0', CheckStatus.OK, 'No pending pods'),
            'SVC-008': ('0', CheckStatus.OK, 'No failed pods'),
            'SVC-009': ('3', CheckStatus.OK, '3 CronJobs'),
            'SVC-010': ('0', CheckStatus.OK, 'No failed jobs'),
        }
        return demo_data.get(item_id, ('N/A', CheckStatus.UNKNOWN, 'No demo data'))

    def run_os_checks(self) -> List[CheckResult]:
        """Run OS checks"""
        results = []
        for item in self.config['check_items']['os']:
            if self.demo_mode:
                value, status, message = self._get_demo_os_data(item['id'])
            else:
                stdout, stderr, returncode = self._run_command(item['command'])
                
                if returncode != 0 or not stdout:
                    status = CheckStatus.UNKNOWN
                    message = f"Command failed: {stderr}" if stderr else "No result"
                    value = "N/A"
                else:
                    value = stdout
                    if item.get('threshold') is not None:
                        status = self._evaluate_threshold(stdout, item['threshold'], item['id'])
                        if status == CheckStatus.OK:
                            message = "Within normal range"
                        elif status == CheckStatus.WARNING:
                            message = f"Approaching threshold ({item['threshold']}{item['unit']})"
                        else:
                            message = f"Exceeds threshold ({item['threshold']}{item['unit']})"
                    else:
                        status = CheckStatus.OK
                        message = "Check completed"
            
            results.append(CheckResult(
                check_id=item['id'],
                name=item['name'],
                category="OS",
                description=item['description'],
                status=status,
                value=value,
                threshold=item.get('threshold'),
                unit=item.get('unit', ''),
                message=message,
                raw_output=value
            ))
        return results
    
    def run_k8s_checks(self) -> List[CheckResult]:
        """Run Kubernetes cluster checks"""
        results = []
        
        kubectl_available = self._check_kubectl_available()
        
        for item in self.config['check_items']['kubernetes']:
            if self.demo_mode:
                value, status, message = self._get_demo_k8s_data(item['id'])
            elif not kubectl_available:
                value = "N/A"
                status = CheckStatus.UNKNOWN
                message = "kubectl not available"
            else:
                stdout, stderr, returncode = self._run_command(item['command'])
                
                if "error" in stderr.lower() or (returncode != 0 and not stdout):
                    status = CheckStatus.UNKNOWN
                    message = f"Check failed: {stderr[:100]}" if stderr else "Command error"
                    value = "N/A"
                else:
                    value = stdout if stdout and stdout != 'N/A' else "No data"
                    expected = item.get('expected')
                    threshold = item.get('threshold')
                    
                    if expected:
                        lines = [l for l in stdout.strip().split('\n') if l and l != 'N/A']
                        ok_count = sum(1 for line in lines if expected in line)
                        total_count = len(lines) if lines else 0
                        
                        if total_count == 0:
                            status = CheckStatus.UNKNOWN
                            message = "No items to check"
                        elif ok_count == total_count:
                            status = CheckStatus.OK
                            message = f"All items healthy ({ok_count}/{total_count})"
                        elif ok_count > total_count * 0.7:
                            status = CheckStatus.WARNING
                            message = f"Some items unhealthy ({ok_count}/{total_count})"
                        else:
                            status = CheckStatus.CRITICAL
                            message = f"Many items unhealthy ({ok_count}/{total_count})"
                    elif threshold is not None:
                        status = self._evaluate_threshold(stdout, threshold, item['id'])
                        if status == CheckStatus.OK:
                            message = "Within normal range"
                        elif status == CheckStatus.WARNING:
                            message = f"Approaching threshold ({threshold}{item.get('unit','')})"
                        else:
                            message = f"Exceeds threshold ({threshold}{item.get('unit','')})"
                    else:
                        status = CheckStatus.OK
                        message = "Check completed"
            
            results.append(CheckResult(
                check_id=item['id'],
                name=item['name'],
                category="Kubernetes",
                description=item['description'],
                status=status,
                value=value[:300] if value else "N/A",
                threshold=item.get('threshold'),
                unit=item.get('unit', ''),
                message=message,
                raw_output=value[:500] if value else ""
            ))
        return results
    
    def run_service_checks(self) -> List[CheckResult]:
        """Run K8s service checks"""
        results = []
        
        kubectl_available = self._check_kubectl_available()
        
        for item in self.config['check_items']['services']:
            if self.demo_mode:
                value, status, message = self._get_demo_svc_data(item['id'])
            elif not kubectl_available:
                value = "N/A"
                status = CheckStatus.UNKNOWN
                message = "kubectl not available"
            else:
                stdout, stderr, returncode = self._run_command(item['command'])
                
                if "error" in stderr.lower() or (returncode != 0 and not stdout):
                    status = CheckStatus.UNKNOWN
                    message = f"Check failed: {stderr[:100]}" if stderr else "Command error"
                    value = "N/A"
                else:
                    value = stdout if stdout and stdout != 'N/A' else "0"
                    check_type = item.get('check_type', '')
                    threshold = item.get('threshold')
                    
                    if check_type == 'replica_match':
                        lines = [l for l in stdout.strip().split('\n') if l and ':' in l and l != 'N/A']
                        issues = []
                        for line in lines:
                            if '/' in line:
                                parts = line.split(':')
                                if len(parts) >= 2:
                                    replicas = parts[-1]
                                    if '/' in replicas:
                                        try:
                                            avail, desired = replicas.split('/')
                                            if avail != desired:
                                                issues.append(parts[0])
                                        except:
                                            pass
                        
                        if len(lines) == 0 or value == 'N/A':
                            status = CheckStatus.UNKNOWN
                            message = "No items to check"
                        elif len(issues) == 0:
                            status = CheckStatus.OK
                            message = f"All resources healthy ({len(lines)})"
                        elif len(issues) <= 2:
                            status = CheckStatus.WARNING
                            message = f"Some resources unhealthy: {', '.join(issues[:3])}"
                        else:
                            status = CheckStatus.CRITICAL
                            message = f"Many resources unhealthy ({len(issues)})"
                    
                    elif threshold is not None:
                        status = self._evaluate_threshold(stdout, threshold, item['id'])
                        if status == CheckStatus.OK:
                            message = "OK"
                        elif status == CheckStatus.WARNING:
                            message = f"Approaching threshold ({threshold}{item.get('unit','')})"
                        else:
                            message = f"Exceeds threshold ({threshold}{item.get('unit','')})"
                    else:
                        status = CheckStatus.OK
                        message = "Check completed"
            
            results.append(CheckResult(
                check_id=item['id'],
                name=item['name'],
                category="Services",
                description=item['description'],
                status=status,
                value=value[:300] if value else "N/A",
                threshold=item.get('threshold'),
                unit=item.get('unit', ''),
                message=message,
                raw_output=value[:500] if value else ""
            ))
        return results
    
    def run_all_checks(self) -> List[CheckResult]:
        """Run all checks"""
        self.results = []
        self.results.extend(self.run_os_checks())
        self.results.extend(self.run_k8s_checks())
        self.results.extend(self.run_service_checks())
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get check results summary"""
        if not self.results:
            return {}
        
        summary = {
            'total': len(self.results),
            'ok': sum(1 for r in self.results if r.status == CheckStatus.OK),
            'warning': sum(1 for r in self.results if r.status == CheckStatus.WARNING),
            'critical': sum(1 for r in self.results if r.status == CheckStatus.CRITICAL),
            'unknown': sum(1 for r in self.results if r.status == CheckStatus.UNKNOWN),
            'by_category': {
                'OS': {'ok': 0, 'warning': 0, 'critical': 0, 'unknown': 0},
                'Kubernetes': {'ok': 0, 'warning': 0, 'critical': 0, 'unknown': 0},
                'Services': {'ok': 0, 'warning': 0, 'critical': 0, 'unknown': 0}
            }
        }
        
        for r in self.results:
            cat = r.category
            if r.status == CheckStatus.OK:
                summary['by_category'][cat]['ok'] += 1
            elif r.status == CheckStatus.WARNING:
                summary['by_category'][cat]['warning'] += 1
            elif r.status == CheckStatus.CRITICAL:
                summary['by_category'][cat]['critical'] += 1
            else:
                summary['by_category'][cat]['unknown'] += 1
        
        return summary
    
    def to_dict(self) -> List[Dict]:
        """Convert results to dictionary list"""
        return [
            {
                'CheckID': r.check_id,
                'CheckItem': r.name,
                'Category': r.category,
                'Description': r.description,
                'Status': r.status.value,
                'Value': r.value,
                'Threshold': f"{r.threshold}{r.unit}" if r.threshold else "-",
                'Message': r.message,
                'Timestamp': r.timestamp
            }
            for r in self.results
        ]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='Run in demo mode')
    args = parser.parse_args()
    
    checker = InfraChecker(demo_mode=args.demo)
    results = checker.run_all_checks()
    summary = checker.get_summary()
    
    print("\n" + "="*60)
    print("Infrastructure Health Check Results")
    if args.demo:
        print("(Demo Mode)")
    print("="*60)
    print(f"Total Items: {summary['total']}")
    print(f"  - OK: {summary['ok']}")
    print(f"  - Warning: {summary['warning']}")
    print(f"  - Critical: {summary['critical']}")
    print(f"  - Unknown: {summary['unknown']}")
    print("="*60)
    
    for r in results:
        status_icon = "✅" if r.status == CheckStatus.OK else "⚠️" if r.status == CheckStatus.WARNING else "❌" if r.status == CheckStatus.CRITICAL else "❓"
        print(f"{status_icon} [{r.check_id}] {r.name}: {r.message}")
