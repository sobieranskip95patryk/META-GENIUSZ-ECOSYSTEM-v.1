#!/usr/bin/env python3
"""
Enhanced Repository Analyzer using GitHub MCP Data
Processes repository data collected from GitHub MCP server and generates a comprehensive report.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# This would normally come from the GitHub MCP search_repositories call
# For now, we'll use sample structure to process

def calculate_activity_score(repo: Dict) -> str:
    """Calculate repository activity score based on various metrics"""
    score = 0
    
    # Recent update (within days)
    pushed_at = repo.get('pushed_at', '')
    if pushed_at:
        try:
            last_push = datetime.fromisoformat(pushed_at.rstrip('Z'))
            days_since = (datetime.now() - last_push).days
            if days_since < 30:
                score += 3
            elif days_since < 90:
                score += 2
            elif days_since < 180:
                score += 1
        except:
            pass
            
    # Stars
    stars = repo.get('stargazers_count', 0)
    if stars > 10:
        score += 2
    elif stars > 0:
        score += 1
        
    # Open issues (indicates engagement)
    if repo.get('open_issues_count', 0) > 0:
        score += 1
        
    # Size (indicates content)
    size = repo.get('size', 0)
    if size > 1000:  # >1MB
        score += 1
        
    if score >= 7:
        return "🟢 Very Active"
    elif score >= 4:
        return "🟡 Active"
    elif score >= 2:
        return "🟠 Low Activity"
    else:
        return "🔴 Inactive"

def determine_status(repo: Dict) -> str:
    """Determine repository status based on last activity"""
    if repo.get('archived', False):
        return "📦 Archived"
        
    pushed_at = repo.get('pushed_at', '')
    if pushed_at:
        try:
            last_push = datetime.fromisoformat(pushed_at.rstrip('Z'))
            days_since = (datetime.now() - last_push).days
            
            if days_since > 365:
                return "💤 Not used (1+ year)"
            elif days_since > 180:
                return "😴 Rarely used (6+ months)"
            elif days_since > 90:
                return "🤔 Occasionally used (3+ months)"
            else:
                return "✅ Active"
        except:
            pass
            
    return "❓ Status unknown"

def format_date(date_str: str) -> str:
    """Format ISO date string to readable format"""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.rstrip('Z'))
        return dt.strftime('%Y-%m-%d')
    except:
        return date_str

def generate_report(repos_data: List[Dict], output_file: str = "REPOSITORY_ANALYSIS_REPORT.md"):
    """Generate comprehensive Markdown report"""
    
    # Load workspace for role mapping
    workspace_path = Path("workspace.json")
    role_map = {}
    if workspace_path.exists():
        with open(workspace_path, 'r') as f:
            workspace = json.load(f)
            for repo in workspace.get('repos', []):
                name = repo['url'].rstrip('.git').split('/')[-1]
                role_map[name] = {
                    'role': repo.get('role', 'misc'),
                    'service': repo.get('service', 'N/A'),
                    'description': repo.get('description', 'N/A'),
                    'port': repo.get('port', 'N/A')
                }
    
    # Process each repository
    processed_repos = []
    for repo in repos_data:
        name = repo['name']
        role_info = role_map.get(name, {
            'role': 'misc',
            'service': 'N/A',
            'description': repo.get('description', 'N/A'),
            'port': 'N/A'
        })
        
        processed = {
            'name': name,
            'url': repo['html_url'],
            'role': role_info['role'],
            'service': role_info['service'],
            'description': role_info['description'] or repo.get('description', 'N/A'),
            'port': role_info['port'],
            'stars': repo.get('stargazers_count', 0),
            'forks': repo.get('forks_count', 0),
            'watchers': repo.get('watchers_count', 0),
            'open_issues': repo.get('open_issues_count', 0),
            'size_kb': repo.get('size', 0),
            'language': repo.get('language') or 'Unknown',
            'created_at': format_date(repo.get('created_at', '')),
            'updated_at': format_date(repo.get('updated_at', '')),
            'pushed_at': format_date(repo.get('pushed_at', '')),
            'is_private': repo.get('private', False),
            'is_archived': repo.get('archived', False),
            'license': repo.get('license', {}).get('name') if repo.get('license') else 'No license',
            'has_pages': repo.get('has_pages', False),
            'activity_score': '',
            'status': ''
        }
        
        processed['activity_score'] = calculate_activity_score(repo)
        processed['status'] = determine_status(repo)
        processed_repos.append(processed)
    
    # Generate report
    report = []
    report.append("# 📊 Analiza Repozytoriów GitHub\n\n")
    report.append(f"**Data analizy:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**Liczba repozytoriów:** {len(processed_repos)}\n")
    report.append(f"**Właściciel:** sobieranskip95patryk\n")
    report.append("\n---\n\n")
    
    # Summary statistics
    report.append("## 📈 Podsumowanie\n\n")
    
    total_stars = sum(r['stars'] for r in processed_repos)
    total_forks = sum(r['forks'] for r in processed_repos)
    total_size_mb = sum(r['size_kb'] for r in processed_repos) / 1024
    
    report.append(f"- **Łączna liczba gwiazdek:** {total_stars} ⭐\n")
    report.append(f"- **Łączna liczba forków:** {total_forks} 🍴\n")
    report.append(f"- **Łączny rozmiar:** {total_size_mb:.2f} MB\n")
    report.append(f"- **Języki programowania:** {len(set(r['language'] for r in processed_repos if r['language'] != 'Unknown'))}\n")
    
    # Count by activity level
    activity_levels = {}
    status_counts = {}
    language_counts = {}
    
    for repo in processed_repos:
        activity = repo['activity_score']
        status = repo['status']
        lang = repo['language']
        
        activity_levels[activity] = activity_levels.get(activity, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1
        if lang and lang != 'Unknown':
            language_counts[lang] = language_counts.get(lang, 0) + 1
    
    report.append("\n### 🎯 Aktywność repozytoriów:\n\n")
    for level, count in sorted(activity_levels.items(), reverse=True):
        report.append(f"- {level}: {count} repozytoriów\n")
        
    report.append("\n### 📊 Status repozytoriów:\n\n")
    for status, count in sorted(status_counts.items()):
        report.append(f"- {status}: {count} repozytoriów\n")
        
    report.append("\n### 💻 Najpopularniejsze języki:\n\n")
    for lang, count in sorted(language_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        report.append(f"- **{lang}**: {count} repozytoriów\n")
    
    # Detailed analysis by role
    report.append("\n---\n\n")
    report.append("## 📑 Szczegółowa Analiza według Kategorii\n\n")
    
    # Group by role
    by_role = {}
    for repo in processed_repos:
        role = repo['role']
        if role not in by_role:
            by_role[role] = []
        by_role[role].append(repo)
    
    for role, repos in sorted(by_role.items()):
        report.append(f"### {role.upper()}\n\n")
        
        for repo in sorted(repos, key=lambda x: x['stars'], reverse=True):
            report.append(f"#### [{repo['name']}]({repo['url']})\n\n")
            report.append(f"- **Opis:** {repo['description']}\n")
            if repo['service'] != 'N/A':
                report.append(f"- **Service:** `{repo['service']}`\n")
            if repo['port'] != 'N/A':
                report.append(f"- **Port:** `{repo['port']}`\n")
            report.append(f"- **Język:** {repo['language']}\n")
            report.append(f"- **Rozmiar:** {repo['size_kb'] / 1024:.2f} MB\n")
            report.append(f"- **Gwiazdki:** {repo['stars']} ⭐ | **Forki:** {repo['forks']} 🍴\n")
            report.append(f"- **Otwarte issues:** {repo['open_issues']}\n")
            report.append(f"- **Utworzono:** {repo['created_at']}\n")
            report.append(f"- **Ostatnia aktualizacja:** {repo['updated_at']}\n")
            report.append(f"- **Ostatni push:** {repo['pushed_at']}\n")
            report.append(f"- **Licencja:** {repo['license']}\n")
            
            if repo['has_pages']:
                report.append(f"- **GitHub Pages:** ✅ Aktywne\n")
            
            report.append(f"- **Status:** {repo['status']}\n")
            report.append(f"- **Aktywność:** {repo['activity_score']}\n")
            report.append("\n")
    
    # Recommendations section
    report.append("---\n\n")
    report.append("## 💡 Rekomendacje i Analiza\n\n")
    
    # Identify inactive repos
    inactive_repos = [r for r in processed_repos 
                     if '💤 Not used' in r['status'] or '😴 Rarely used' in r['status']]
    
    empty_repos = [r for r in processed_repos if r['size_kb'] == 0]
    
    active_repos = [r for r in processed_repos if '✅ Active' in r['status']]
    
    # Popular repos (if any)
    popular_repos = [r for r in processed_repos if r['stars'] > 0 or r['forks'] > 0]
    
    if inactive_repos:
        report.append("### ⚠️ Repozytoria o niskiej aktywności\n\n")
        report.append(f"Znaleziono **{len(inactive_repos)}** repozytoriów z niską aktywnością:\n\n")
        
        for repo in sorted(inactive_repos, key=lambda x: x['pushed_at']):
            report.append(f"- **[{repo['name']}]({repo['url']})** - {repo['status']}\n")
            report.append(f"  - Ostatni push: {repo['pushed_at']}\n")
            report.append(f"  - Rozmiar: {repo['size_kb'] / 1024:.2f} MB\n")
        
        report.append("\n**Sugestie:**\n\n")
        report.append("1. Rozważ archiwizację nieużywanych repozytoriów\n")
        report.append("2. Usuń puste lub testowe repozytoria\n")
        report.append("3. Skonsoliduj podobne projekty\n")
        report.append("4. Zaktualizuj dokumentację dla repozytoriów, które planujesz rozwijać\n\n")
    
    if empty_repos:
        report.append(f"### 📭 Puste repozytoria ({len(empty_repos)})\n\n")
        report.append("Następujące repozytoria nie zawierają żadnych plików:\n\n")
        for repo in empty_repos:
            report.append(f"- **[{repo['name']}]({repo['url']})** (utworzone: {repo['created_at']})\n")
        report.append("\n")
    
    if active_repos:
        report.append(f"### ✅ Aktywne repozytoria ({len(active_repos)})\n\n")
        report.append("Te repozytoria są regularnie aktualizowane:\n\n")
        for repo in sorted(active_repos, key=lambda x: x['pushed_at'], reverse=True)[:10]:
            report.append(f"- **[{repo['name']}]({repo['url']})** - ostatni push: {repo['pushed_at']}\n")
        report.append("\n")
    
    if popular_repos:
        report.append(f"### ⭐ Repozytoria z zainteresowaniem społeczności\n\n")
        for repo in sorted(popular_repos, key=lambda x: (x['stars'], x['forks']), reverse=True):
            if repo['stars'] > 0 or repo['forks'] > 0:
                report.append(f"- **[{repo['name']}]({repo['url']})** - {repo['stars']} ⭐, {repo['forks']} 🍴\n")
        report.append("\n")
    
    # General recommendations
    report.append("### 🎯 Ogólne rekomendacje\n\n")
    report.append("1. **Dokumentacja:** Upewnij się, że wszystkie aktywne projekty mają aktualne pliki README\n")
    report.append("2. **Licencje:** Rozważ dodanie licencji do projektów bez licencji\n")
    report.append("3. **GitHub Pages:** Wykorzystaj GitHub Pages dla projektów webowych\n")
    report.append("4. **Topics/Tags:** Dodaj tagi do repozytoriów dla lepszej widoczności\n")
    report.append("5. **Archiwizacja:** Zarchiwizuj nieużywane projekty zamiast ich usuwać\n\n")
    
    report.append("---\n\n")
    report.append(f"*Raport wygenerowany automatycznie przez enhanced_repo_analyzer.py*\n")
    report.append(f"*Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    # Write report to file
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(report)
        
    print(f"✅ Raport zapisany do: {output_file}")
    return output_file

def main():
    """Main entry point"""
    print("="*60)
    print("📊 Enhanced Repository Analyzer")
    print("="*60)
    print()
    
    # Load repository data from JSON file (created by GitHub MCP)
    json_file = Path("github_repos_data.json")
    
    if not json_file.exists():
        print(f"❌ Błąd: {json_file} nie istnieje!")
        print("   Utwórz plik z danymi z GitHub MCP search_repositories")
        return 1
        
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    repos = data.get('items', [])
    
    if not repos:
        print("❌ Błąd: Brak danych o repozytoriach!")
        return 1
    
    print(f"📦 Znaleziono {len(repos)} repozytoriów")
    print()
    
    # Generate report
    generate_report(repos)
    
    print("\n✅ Analiza zakończona pomyślnie!")
    
    return 0

if __name__ == "__main__":
    exit(main())
