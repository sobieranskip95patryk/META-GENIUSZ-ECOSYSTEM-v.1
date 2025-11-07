#!/usr/bin/env python3
"""
Repository Analyzer and Report Generator
Analizuje wszystkie repozytoria z workspace.json i generuje szczegółowy raport.
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
from pathlib import Path


class RepoAnalyzer:
    """Analyzer for GitHub repositories"""
    
    def __init__(self, workspace_file: str = "workspace.json"):
        self.workspace_file = workspace_file
        self.github_token = None  # Can be set via environment variable
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
            
    def get_repo_info(self, repo_url: str) -> Optional[Dict]:
        """Fetch repository information from GitHub API"""
        # Extract owner and repo name from URL
        parts = repo_url.rstrip('.git').split('/')
        owner = parts[-2]
        repo_name = parts[-1]
        
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
            
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {"error": "Repository not found"}
            elif response.status_code == 403:
                return {"error": "API rate limit exceeded"}
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
            
    def get_repo_commits(self, repo_url: str, since_days: int = 90) -> Optional[Dict]:
        """Get recent commits information"""
        parts = repo_url.rstrip('.git').split('/')
        owner = parts[-2]
        repo_name = parts[-1]
        
        since_date = (datetime.now() - timedelta(days=since_days)).isoformat()
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
        
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
            
        params = {'since': since_date, 'per_page': 100}
        
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                commits = response.json()
                return {
                    'count': len(commits),
                    'recent_commits': commits[:5] if commits else []
                }
            else:
                return {'count': 0, 'recent_commits': []}
        except Exception:
            return {'count': 0, 'recent_commits': []}
            
    def analyze_repository(self, repo: Dict) -> Dict:
        """Analyze a single repository"""
        print(f"📊 Analyzing {repo['name']}...")
        
        repo_info = self.get_repo_info(repo['url'])
        commits_info = self.get_repo_commits(repo['url'])
        
        analysis = {
            'name': repo['name'],
            'url': repo['url'],
            'role': repo.get('role', 'N/A'),
            'service': repo.get('service', 'N/A'),
            'description': repo.get('description', 'N/A'),
            'port': repo.get('port', 'N/A'),
        }
        
        if repo_info and 'error' not in repo_info:
            analysis.update({
                'stars': repo_info.get('stargazers_count', 0),
                'forks': repo_info.get('forks_count', 0),
                'watchers': repo_info.get('watchers_count', 0),
                'open_issues': repo_info.get('open_issues_count', 0),
                'size_kb': repo_info.get('size', 0),
                'language': repo_info.get('language', 'Unknown'),
                'created_at': repo_info.get('created_at', 'N/A'),
                'updated_at': repo_info.get('updated_at', 'N/A'),
                'pushed_at': repo_info.get('pushed_at', 'N/A'),
                'default_branch': repo_info.get('default_branch', 'main'),
                'is_private': repo_info.get('private', False),
                'is_archived': repo_info.get('archived', False),
                'license': repo_info.get('license', {}).get('name', 'No license'),
                'topics': repo_info.get('topics', []),
            })
        else:
            analysis['error'] = repo_info.get('error', 'Unknown error')
            
        # Add commits information
        if commits_info:
            analysis['recent_commits_90d'] = commits_info['count']
            
        # Calculate activity score
        analysis['activity_score'] = self.calculate_activity_score(analysis)
        analysis['status'] = self.determine_status(analysis)
        
        return analysis
        
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
        
    def analyze_all(self) -> List[Dict]:
        """Analyze all repositories from workspace"""
        print(f"🚀 Starting analysis of {len(self.workspace['repos'])} repositories...\n")
        
        for repo in self.workspace['repos']:
            analysis = self.analyze_repository(repo)
            self.repos_data.append(analysis)
            
        print(f"\n✅ Analysis complete!\n")
        return self.repos_data
        
    def generate_markdown_report(self, output_file: str = "REPOSITORY_ANALYSIS_REPORT.md"):
        """Generate a comprehensive Markdown report"""
        
        if not self.repos_data:
            self.analyze_all()
            
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
        report.append(f"*Raport wygenerowany automatycznie przez repo_analyzer.py*\n")
        
        # Write report to file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(report)
            
        print(f"📄 Raport zapisany do: {output_file}")
        return output_file
        
    def generate_json_report(self, output_file: str = "repository_analysis.json"):
        """Generate JSON format report"""
        if not self.repos_data:
            self.analyze_all()
            
        report = {
            'analysis_date': datetime.now().isoformat(),
            'total_repositories': len(self.repos_data),
            'summary': {
                'total_stars': sum(r.get('stars', 0) for r in self.repos_data if 'error' not in r),
                'total_forks': sum(r.get('forks', 0) for r in self.repos_data if 'error' not in r),
                'total_size_mb': sum(r.get('size_kb', 0) for r in self.repos_data if 'error' not in r) / 1024,
            },
            'repositories': self.repos_data
        }
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📄 JSON raport zapisany do: {output_file}")
        return output_file


def main():
    """Main entry point"""
    import os
    
    print("="*60)
    print("📊 GitHub Repository Analyzer")
    print("="*60)
    print()
    
    # Check for GitHub token (optional but recommended)
    github_token = os.environ.get('GITHUB_TOKEN')
    if github_token:
        print("✅ GitHub token znaleziony - wyższy limit API")
    else:
        print("ℹ️  Brak tokenu GitHub - ograniczony limit API (60 req/h)")
        print("   Ustaw zmienną GITHUB_TOKEN dla wyższego limitu")
    print()
    
    # Create analyzer
    analyzer = RepoAnalyzer()
    analyzer.github_token = github_token
    
    # Analyze all repositories
    analyzer.analyze_all()
    
    # Generate reports
    print("\n" + "="*60)
    print("📄 Generowanie raportów...")
    print("="*60)
    analyzer.generate_markdown_report()
    analyzer.generate_json_report()
    
    print("\n✅ Analiza zakończona pomyślnie!")
    print("\nWygenerowane pliki:")
    print("  - REPOSITORY_ANALYSIS_REPORT.md (raport szczegółowy)")
    print("  - repository_analysis.json (dane JSON)")
    

if __name__ == "__main__":
    main()
