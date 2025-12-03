#!/usr/bin/env python3
"""
Infrastructure Health Check - Main Script
Weekly/Monthly health check report generation and notification

Usage:
    python main.py                     # Default (weekly)
    python main.py --demo              # Demo mode (sample data)
    python main.py --type monthly      # Monthly report
    python main.py --notify            # Include notifications
"""

import argparse
import os
import sys
import yaml
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from checker import InfraChecker
from report_generator import ReportGenerator, ReportConfig, generate_reports
from notifier import NotificationConfig, NotificationManager


def load_config(config_path: str) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_notification_config(config: dict) -> NotificationConfig:
    notif = config.get('notifications', {})
    
    email_config = notif.get('email', {})
    slack_config = notif.get('slack', {})
    teams_config = notif.get('teams', {})
    discord_config = notif.get('discord', {})
    telegram_config = notif.get('telegram', {})
    webhook_config = notif.get('webhook', {})
    
    return NotificationConfig(
        email_enabled=email_config.get('enabled', False),
        smtp_server=email_config.get('smtp_server', ''),
        smtp_port=email_config.get('smtp_port', 587),
        smtp_user=email_config.get('smtp_user', ''),
        smtp_password=os.environ.get('SMTP_PASSWORD', email_config.get('smtp_password', '')),
        sender=email_config.get('sender', ''),
        recipients=email_config.get('recipients', []),
        use_tls=email_config.get('use_tls', True),
        slack_enabled=slack_config.get('enabled', False),
        slack_webhook_url=os.environ.get('SLACK_WEBHOOK_URL', slack_config.get('webhook_url', '')),
        slack_channel=slack_config.get('channel', '#infra-alerts'),
        teams_enabled=teams_config.get('enabled', False),
        teams_webhook_url=os.environ.get('TEAMS_WEBHOOK_URL', teams_config.get('webhook_url', '')),
        discord_enabled=discord_config.get('enabled', False),
        discord_webhook_url=os.environ.get('DISCORD_WEBHOOK_URL', discord_config.get('webhook_url', '')),
        telegram_enabled=telegram_config.get('enabled', False),
        telegram_bot_token=os.environ.get('TELEGRAM_BOT_TOKEN', telegram_config.get('bot_token', '')),
        telegram_chat_id=os.environ.get('TELEGRAM_CHAT_ID', telegram_config.get('chat_id', '')),
        webhook_enabled=webhook_config.get('enabled', False),
        webhook_url=webhook_config.get('url', ''),
        webhook_headers=webhook_config.get('headers', None)
    )


def create_report_config(config: dict, report_type: str) -> ReportConfig:
    report_conf = config.get('report', {})
    
    return ReportConfig(
        report_type=report_type or report_conf.get('type', 'weekly'),
        company_name=report_conf.get('company_name', 'Company'),
        team_name=report_conf.get('team_name', 'Infrastructure Team'),
        output_dir=report_conf.get('output_dir', './output')
    )


def format_issue_message(results: list) -> str:
    issues = [r for r in results if r.get('Status') in ['Warning', 'Critical']]
    
    if not issues:
        return "All check items are healthy."
    
    lines = ["🚨 Action Required Items:"]
    for issue in issues:
        status = issue.get('Status', '')
        icon = "⚠️" if status == 'Warning' else "❌"
        lines.append(f"{icon} [{issue.get('CheckID')}] {issue.get('CheckItem')}")
        lines.append(f"   └─ {issue.get('Message', '')}")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Infrastructure Health Check Report Generator')
    
    parser.add_argument('--config', '-c',
        default=os.path.join(os.path.dirname(SCRIPT_DIR), 'config', 'check_items.yaml'),
        help='Configuration file path')
    parser.add_argument('--type', '-t', choices=['weekly', 'monthly'], help='Report type')
    parser.add_argument('--output-dir', '-o', help='Report output directory')
    parser.add_argument('--demo', action='store_true', help='Demo mode (use sample data)')
    parser.add_argument('--notify', '-n', action='store_true', help='Send notifications')
    parser.add_argument('--notify-on-issues', action='store_true', help='Notify only on issues')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.config):
        print(f"❌ Configuration file not found: {args.config}")
        sys.exit(1)
    
    config = load_config(args.config)
    report_config = create_report_config(config, args.type)
    if args.output_dir:
        report_config.output_dir = args.output_dir
    
    if not args.quiet:
        print("=" * 60)
        print("🔍 Infrastructure Health Check Started")
        if args.demo:
            print("   ⚠️  Demo Mode - Using sample data")
        print(f"   Report Type: {report_config.report_type}")
        print(f"   Company: {report_config.company_name}")
        print(f"   Team: {report_config.team_name}")
        print("=" * 60)
    
    # Run checks
    checker = InfraChecker(args.config, demo_mode=args.demo)
    
    if not args.quiet:
        print("\n📋 Checking OS... (10 items)")
    os_results = checker.run_os_checks()
    
    if not args.quiet:
        print("📋 Checking Kubernetes... (10 items)")
    k8s_results = checker.run_k8s_checks()
    
    if not args.quiet:
        print("📋 Checking Services... (10 items)")
    svc_results = checker.run_service_checks()
    
    checker.results = os_results + k8s_results + svc_results
    results_dict = checker.to_dict()
    summary = checker.get_summary()
    
    # JSON output
    if args.json:
        import json
        output = {
            'summary': summary,
            'results': results_dict,
            'timestamp': datetime.now().isoformat(),
            'demo_mode': args.demo
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return
    
    # Summary output
    if not args.quiet:
        print("\n" + "=" * 60)
        print("📊 Check Results Summary")
        print("=" * 60)
        print(f"  Total Items: {summary['total']}")
        print(f"  ✅ OK: {summary['ok']}")
        print(f"  ⚠️ Warning: {summary['warning']}")
        print(f"  ❌ Critical: {summary['critical']}")
        print(f"  ❓ Unknown: {summary['unknown']}")
        print("=" * 60)
        
        print("\n📂 Results by Category:")
        for cat, cat_summary in summary['by_category'].items():
            print(f"  {cat}: ✅{cat_summary['ok']} ⚠️{cat_summary['warning']} ❌{cat_summary['critical']} ❓{cat_summary['unknown']}")
    
    # Generate reports
    if not args.quiet:
        print("\n📝 Generating reports...")
    
    generated_files = generate_reports(results_dict, summary, report_config)
    
    if not args.quiet:
        print("✅ Reports generated:")
        for fmt, path in generated_files.items():
            print(f"   - {fmt.upper()}: {path}")
    
    # Send notifications
    if args.notify or args.notify_on_issues:
        notif_config = create_notification_config(config)
        manager = NotificationManager(notif_config)
        
        now = datetime.now()
        if report_config.report_type == "weekly":
            week_num = now.isocalendar()[1]
            title = f"[{report_config.company_name}] {now.year} Week {week_num} Infrastructure Health Check Report"
        else:
            title = f"[{report_config.company_name}] {now.year} {now.strftime('%B')} Infrastructure Health Check Report"
        
        message = format_issue_message(results_dict)
        attachments = list(generated_files.values())
        
        if args.notify_on_issues:
            results = manager.send_if_issues(title, message, summary, attachments)
        else:
            results = manager.send_all(title, message, summary, attachments)
        
        if not args.quiet and results:
            print("\n📤 Notification Results:")
            for sender, success in results.items():
                status = "✅" if success else "❌"
                print(f"   {status} {sender}")
    
    # Detailed results
    if not args.quiet:
        print("\n" + "=" * 60)
        print("📋 Detailed Check Results")
        print("=" * 60)
        
        current_category = ""
        for r in results_dict:
            if r['Category'] != current_category:
                current_category = r['Category']
                print(f"\n【 {current_category} 】")
            
            status = r['Status']
            icon = "✅" if status == 'OK' else "⚠️" if status == 'Warning' else "❌" if status == 'Critical' else "❓"
            
            print(f"  {icon} [{r['CheckID']}] {r['CheckItem']}")
            value = r['Value']
            print(f"      Value: {value[:50]}{'...' if len(value) > 50 else ''}")
            print(f"      Result: {r['Message']}")
    
    # Highlight issues
    issues = [r for r in results_dict if r.get('Status') in ['Warning', 'Critical']]
    if issues and not args.quiet:
        print("\n" + "=" * 60)
        print("🚨 Action Required Items")
        print("=" * 60)
        for issue in issues:
            status = issue.get('Status', '')
            icon = "⚠️" if status == 'Warning' else "❌"
            print(f"{icon} [{issue.get('CheckID')}] {issue.get('CheckItem')}")
            print(f"   Status: {status}")
            print(f"   Message: {issue.get('Message', '')}")
            print(f"   Description: {issue.get('Description', '')}")
            print()
    
    if not args.quiet:
        print("=" * 60)
        print("✅ Check Completed")
        print("=" * 60)
    
    # Exit code
    if summary['critical'] > 0:
        sys.exit(2)
    elif summary['warning'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
