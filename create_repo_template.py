#!/usr/bin/env python3
"""
Repository Data Collector
Zbiera dane o repozytoriach korzystając z dostępnych narzędzi GitHub.
Tworzy plik repository_data_collected.json z zebranymi danymi.
"""

import json
from pathlib import Path
from datetime import datetime

def load_workspace(workspace_file="workspace.json"):
    """Load workspace configuration"""
    with open(workspace_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_repo_url(repo_url):
    """Extract owner and repo name from URL"""
    parts = repo_url.rstrip('.git').split('/')
    return parts[-2], parts[-1]

def create_data_template():
    """Create template for collecting repository data"""
    workspace = load_workspace()
    
    repos_template = []
    
    for repo in workspace['repos']:
        owner, name = parse_repo_url(repo['url'])
        
        repos_template.append({
            'name': repo['name'],
            'url': repo['url'],
            'owner': owner,
            'repo_name': name,
            'role': repo.get('role', 'N/A'),
            'service': repo.get('service', 'N/A'),
            'description': repo.get('description', 'N/A'),
            'port': repo.get('port', 'N/A'),
            'compliance': repo.get('compliance', {}),
            # Placeholders for data to be filled by MCP tools
            'stars': 0,
            'forks': 0,
            'watchers': 0,
            'open_issues': 0,
            'size_kb': 0,
            'language': 'Unknown',
            'created_at': 'N/A',
            'updated_at': 'N/A',
            'pushed_at': 'N/A',
            'default_branch': 'main',
            'is_private': False,
            'is_archived': False,
            'license': 'No license',
            'topics': [],
            'recent_commits_90d': 0,
            'needs_mcp_data': True  # Flag indicating data should be collected
        })
    
    output = {
        'collection_date': datetime.now().isoformat(),
        'total_repositories': len(repos_template),
        'repositories': repos_template
    }
    
    output_file = Path('repository_data_template.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created template: {output_file}")
    print(f"   Total repositories: {len(repos_template)}")
    print()
    print("📋 Repositories to collect data for:")
    for repo in repos_template:
        print(f"   - {repo['owner']}/{repo['repo_name']}")
    
    return output_file

if __name__ == "__main__":
    print("="*60)
    print("📊 Repository Data Collection Template Creator")
    print("="*60)
    print()
    create_data_template()
    print()
    print("Next steps:")
    print("1. Use GitHub MCP tools to collect data for each repository")
    print("2. Update repository_data_template.json with actual data")
    print("3. Run repo_analyzer.py to generate the final report")
