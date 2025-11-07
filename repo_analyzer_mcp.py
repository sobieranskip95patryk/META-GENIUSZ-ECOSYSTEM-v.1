#!/usr/bin/env python3
"""
Repository Analyzer and Report Generator (MCP Version)
Analizuje wszystkie repozytoria z workspace.json i generuje szczegółowy raport.
Wersja używająca GitHub MCP - należy uruchomić przez system z dostępem do MCP.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
from pathlib import Path


class RepoAnalyzerMCP:
    """Analyzer for GitHub repositories using MCP tools"""
    
    def __init__(self, workspace_file: str = "workspace.json"):
        self.workspace_file = workspace_file
        self.repos_data = []
        self.load_workspace()
        
    def load_workspace(self):
        """Load workspace.json file"""
        workspace_path = Path(self.workspace_file)
        if not workspace_path.exists():
            print(f"❌ Error: {self.workspace_file} not found!")
            sys.exit(1)
            
        with open(workspace_path, 'r', encoding='utf-8') as f:
            self.workspace = json.load(f)
    
    def parse_repo_url(self, repo_url: str) -> tuple:
        """Extract owner and repo name from URL"""
        parts = repo_url.rstrip('.git').split('/')
        owner = parts[-2]
        repo_name = parts[-1]
        return owner, repo_name
    
    def calculate_activity_score(self, analysis: Dict) -> str:
        """Calculate repository activity score"""
        if 'error' in analysis:
            return "Unknown"
            
        score = 0
        
        # Recent commits
        commits = analysis.get('recent_commits_90d', 0)
        if commits > 20:
            score += 3
        elif commits > 5:
            score += 2
        elif commits > 0:
            score += 1
            
        # Stars
        stars = analysis.get('stars', 0)
        if stars > 10:
            score += 2
        elif stars > 0:
            score += 1
            
        # Recent update (within 30 days)
        pushed_at = analysis.get('pushed_at', '')
        if pushed_at and pushed_at != 'N/A':
            try:
                last_push = datetime.fromisoformat(pushed_at.rstrip('Z'))
                days_since = (datetime.now() - last_push).days
                if days_since < 30:
                    score += 3
                elif days_since < 90:
                    score += 2
                elif days_since < 180:
                    score += 1
            except (ValueError, TypeError):
                pass
                
        # Open issues (indicates engagement)
        if analysis.get('open_issues', 0) > 0:
            score += 1
            
        if score >= 7:
            return "🟢 Very Active"
        elif score >= 4:
            return "🟡 Active"
        elif score >= 2:
            return "🟠 Low Activity"
        else:
            return "🔴 Inactive"
            
    def determine_status(self, analysis: Dict) -> str:
        """Determine repository status"""
        if 'error' in analysis:
            return "⚠️ Error accessing"
            
        if analysis.get('is_archived', False):
            return "📦 Archived"
            
        pushed_at = analysis.get('pushed_at', '')
        if pushed_at and pushed_at != 'N/A':
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
            except (ValueError, TypeError):
                pass
                
        return "❓ Status unknown"
        
    def generate_markdown_report(self, output_file: str = "REPOSITORY_ANALYSIS_REPORT.md"):
        """Generate a comprehensive Markdown report from JSON data"""
        
        # Try to load existing JSON data
        json_file = Path("repository_analysis.json")
        if not json_file.exists():
            print("❌ Error: repository_analysis.json not found!")
            print("   Please run analysis first or manually collect repository data.")
            return None
            
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.repos_data = data.get('repositories', [])
        
        report = []
        report.append("# 📊 Analiza Repozytoriów GitHub\n")
        report.append(f"**Data analizy:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Liczba repozytoriów:** {len(self.repos_data)}\n")
        report.append("---\n")
        
        # Summary statistics
        report.append("## 📈 Podsumowanie\n")
        
        total_stars = sum(r.get('stars', 0) for r in self.repos_data if 'error' not in r)
        total_forks = sum(r.get('forks', 0) for r in self.repos_data if 'error' not in r)
        total_size = sum(r.get('size_kb', 0) for r in self.repos_data if 'error' not in r)
        
        report.append(f"- **Łączna liczba gwiazdek:** {total_stars} ⭐\n")
        report.append(f"- **Łączna liczba forków:** {total_forks} 🍴\n")
        report.append(f"- **Łączny rozmiar:** {total_size / 1024:.2f} MB\n")
        
        # Count by activity level
        activity_levels = {}
        status_counts = {}
        
        for repo in self.repos_data:
            activity = repo.get('activity_score', 'Unknown')
            status = repo.get('status', 'Unknown')
            
            activity_levels[activity] = activity_levels.get(activity, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
            
        report.append("\n### Aktywność repozytoriów:\n")
        for level, count in sorted(activity_levels.items(), reverse=True):
            report.append(f"- {level}: {count} repozytoriów\n")
            
        report.append("\n### Status repozytoriów:\n")
        for status, count in sorted(status_counts.items()):
            report.append(f"- {status}: {count} repozytoriów\n")
            
        # Detailed analysis by category
        report.append("\n---\n")
        report.append("## 📑 Szczegółowa Analiza\n\n")
        
        # Group by role
        by_role = {}
        for repo in self.repos_data:
            role = repo.get('role', 'unknown')
            if role not in by_role:
                by_role[role] = []
            by_role[role].append(repo)
            
        for role, repos in sorted(by_role.items()):
            report.append(f"### {role.upper()}\n\n")
            
            for repo in sorted(repos, key=lambda x: x.get('stars', 0), reverse=True):
                report.append(f"#### {repo['name']}\n")
                report.append(f"- **URL:** {repo['url']}\n")
                report.append(f"- **Opis:** {repo['description']}\n")
                report.append(f"- **Service:** {repo['service']}\n")
                report.append(f"- **Port:** {repo['port']}\n")
                
                if 'error' not in repo:
                    report.append(f"- **Język:** {repo.get('language', 'N/A')}\n")
                    report.append(f"- **Gwiazdki:** {repo.get('stars', 0)} ⭐\n")
                    report.append(f"- **Forki:** {repo.get('forks', 0)} 🍴\n")
                    report.append(f"- **Otwarte issues:** {repo.get('open_issues', 0)}\n")
                    report.append(f"- **Rozmiar:** {repo.get('size_kb', 0) / 1024:.2f} MB\n")
                    report.append(f"- **Ostatni push:** {repo.get('pushed_at', 'N/A')}\n")
                    report.append(f"- **Commity (90 dni):** {repo.get('recent_commits_90d', 0)}\n")
                    report.append(f"- **Licencja:** {repo.get('license', 'N/A')}\n")
                    report.append(f"- **Prywatne:** {'Tak' if repo.get('is_private', False) else 'Nie'}\n")
                    report.append(f"- **Zarchiwizowane:** {'Tak' if repo.get('is_archived', False) else 'Nie'}\n")
                    
                    # Additional details
                    if repo.get('topics'):
                        topics_str = ", ".join(repo['topics'])
                        report.append(f"- **Tagi:** {topics_str}\n")
                else:
                    report.append(f"- **Błąd:** {repo['error']}\n")
                    
                report.append(f"- **Aktywność:** {repo.get('activity_score', 'Unknown')}\n")
                report.append(f"- **Status:** {repo.get('status', 'Unknown')}\n")
                report.append("\n")
                
        # Recommendations section
        report.append("---\n")
        report.append("## 💡 Rekomendacje\n\n")
        
        inactive_repos = [r for r in self.repos_data 
                         if '💤 Not used' in r.get('status', '') or 
                            '😴 Rarely used' in r.get('status', '')]
        
        if inactive_repos:
            report.append("### Repozytoria do rozważenia:\n\n")
            report.append("Następujące repozytoria mają niską aktywność i mogą wymagać uwagi:\n\n")
            
            for repo in inactive_repos:
                report.append(f"- **{repo['name']}** ({repo['url']})\n")
                report.append(f"  - Status: {repo.get('status', 'Unknown')}\n")
                report.append(f"  - Ostatni push: {repo.get('pushed_at', 'N/A')}\n")
                report.append(f"  - Aktywność: {repo.get('activity_score', 'Unknown')}\n")
                report.append("\n")
                
            report.append("\n**Sugestie:**\n")
            report.append("1. Rozważ archiwizację nieużywanych repozytoriów\n")
            report.append("2. Zaktualizuj dokumentację dla aktywnych projektów\n")
            report.append("3. Usuń repozytoria testowe lub tymczasowe\n")
            report.append("4. Skonsoliduj podobne projekty\n")
        else:
            report.append("✅ Wszystkie repozytoria są aktywne lub używane!\n")
            
        report.append("\n---\n")
        report.append(f"*Raport wygenerowany automatycznie przez repo_analyzer_mcp.py*\n")
        
        # Write report to file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(report)
            
        print(f"📄 Raport zapisany do: {output_file}")
        return output_file


def main():
    """Main entry point"""
    
    print("="*60)
    print("📊 GitHub Repository Analyzer (MCP)")
    print("="*60)
    print()
    print("ℹ️  Ta wersja używa GitHub MCP i wymaga danych JSON")
    print("   z poprzednio wykonanej analizy lub z MCP tools.")
    print()
    
    # Create analyzer
    analyzer = RepoAnalyzerMCP()
    
    # Generate report from existing JSON
    print("📄 Generowanie raportu...")
    analyzer.generate_markdown_report()
    
    print("\n✅ Raport wygenerowany pomyślnie!")
    

if __name__ == "__main__":
    main()
