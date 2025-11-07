# Repository Analyzer Tools

This directory contains tools for analyzing GitHub repositories and generating comprehensive reports.

## 🎯 Purpose

The problem statement (in Polish) was: "Can you work on my profile and, for example, delete unused repositories or check all of them and create a report?"

These tools provide:
1. Automated analysis of all GitHub repositories
2. Activity and health metrics for each repository
3. Identification of inactive/unused repositories
4. Recommendations for repository management

## 📊 Tools

### 1. `enhanced_repo_analyzer.py` ⭐ **RECOMMENDED**
The main analysis tool that processes repository data and generates comprehensive reports.

**Usage:**
```bash
# First, get repository data (already provided in github_repos_data.json)
python3 enhanced_repo_analyzer.py
```

**Output:**
- `REPOSITORY_ANALYSIS_REPORT.md` - Detailed Markdown report with recommendations

### 2. `repo_analyzer.py`
Direct API-based analyzer (may hit rate limits without authentication).

**Usage:**
```bash
python3 repo_analyzer.py
```

### 3. Supporting Files
- `workspace.json` - Repository configuration with roles and services
- `github_repos_data.json` - GitHub API data cache
- `repos.txt` - List of repository URLs

## 📋 Generated Reports

### REPOSITORY_ANALYSIS_REPORT.md
A comprehensive analysis report including:

- **Summary Statistics**
  - Total repositories count
  - Stars, forks, and size metrics
  - Programming languages used
  
- **Activity Analysis**
  - Active repositories (updated within 90 days)
  - Low activity repositories
  - Inactive repositories (1+ year)
  
- **Categorized Analysis**
  - Grouped by role (core, content, gateway, etc.)
  - Detailed metrics for each repository
  - Last update dates and sizes
  
- **Recommendations**
  - Repositories to consider archiving
  - Empty repositories to clean up
  - Suggestions for improvement

## 🔍 Key Metrics

The analyzer evaluates repositories based on:

1. **Last Update Date** - How recently code was pushed
2. **Repository Size** - Amount of content (files, assets)
3. **Stars & Forks** - Community engagement
4. **Open Issues** - Active development
5. **License** - Proper licensing
6. **GitHub Pages** - Web presence

## 🎯 Activity Scores

- 🟢 **Very Active** - Updated within 30 days, good engagement
- 🟡 **Active** - Updated within 90 days
- 🟠 **Low Activity** - Updated within 180 days
- 🔴 **Inactive** - Not updated for 180+ days

## 💡 Usage Recommendations

1. **Review the Report** - Read `REPOSITORY_ANALYSIS_REPORT.md` to understand your repository landscape

2. **Identify Unused Repos** - Check the "Repozytoria o niskiej aktywności" section

3. **Take Action**:
   - Archive completed/deprecated projects
   - Delete empty test repositories
   - Update documentation for active projects
   - Add licenses where missing

4. **Re-run Periodically** - Run the analyzer monthly/quarterly to track changes

## 📦 Dependencies

- Python 3.8+
- `requests` library (for direct API access)
- Standard library modules: `json`, `datetime`, `pathlib`

## 🔒 Security Note

These tools only **read** repository data. They do **not**:
- Delete or modify repositories
- Change repository settings
- Access private data
- Make any changes to your GitHub account

You maintain full control over any actions taken based on the report recommendations.

## 📝 Example Output

```markdown
# 📊 Analiza Repozytoriów GitHub

**Data analizy:** 2025-11-07
**Liczba repozytoriów:** 22

## 📈 Podsumowanie
- **Łączny rozmiar:** 243.10 MB
- **Języki programowania:** 4

### 🎯 Aktywność repozytoriów:
- 🟡 Active: 5 repozytoriów
- 🟠 Low Activity: 17 repozytoriów

## 💡 Rekomendacje
1. Rozważ archiwizację nieużywanych repozytoriów
2. Usuń puste lub testowe repozytoria
3. Zaktualizuj dokumentację
```

## 🤝 Contributing

These tools are part of the Meta-Geniusz ecosystem. For questions or improvements, refer to the main README.

---

*Part of the Meta-Geniusz® AI Ecosystem*
