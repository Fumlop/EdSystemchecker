# Elite Dangerous PowerPlay System Checker

Automated tool for analyzing Elite Dangerous PowerPlay system status from Inara data.

**Last Updated:** 2025-07-26 21:52:31 UTC

## 📊 Current PowerPlay Status Reports

### System Status Reports
- **🏛️ [Stronghold Systems](stronghold_status.md)** - Control systems status and undermining analysis
- **🏭 [Exploited Systems](exploited_status.md)** - Exploited systems status and undermining analysis  
- **🛡️ [Fortified Systems](fortified_status.md)** - Fortified systems status and undermining analysis
- **⚔️ [Contested Systems](contested_status.md)** - Contested and expansion systems analysis
- **🎯 [Priority Acquisition](accquise_prio.md)** - High priority acquisition target systems

### JSON Data Files
- **[Stronghold Systems JSON](json/stronghold_systems.json)** - Raw stronghold system data
- **[Exploited Systems JSON](json/exploited_systems.json)** - Raw exploited system data
- **[Fortified Systems JSON](json/fortified_systems.json)** - Raw fortified system data
- **[Contested Systems JSON](json/contested_systems.json)** - Raw contested system data

### System no current Inara data
*All systems up to date!*

## 🚀 Quick Start

## 🚀 Quick Start

### 🔄 Automated Updates
- **🌐 GitHub Actions**: [![Run Workflow](https://img.shields.io/badge/🚀_Update_Reports-GitHub_Actions-success?style=for-the-badge)](https://github.com/Fumlop/EdSystemchecker/actions/workflows/update-reports.yml)
- **💻 Local Pipeline**: Run `python python/github_update.py` (extracts data + generates all reports)

### 📋 Manual Process  
1. **Extract System Data**: Run `python python/extract.py` to process HTML files
2. **Generate Reports**: Run the universal generator:
   ```bash
   python python/create_universal_md.py stronghold
   python python/create_universal_md.py fortified  
   python python/create_universal_md.py exploited
   python python/create_contested_md.py
   ```

### 🛠️ Git Integration
- **Auto-Update Hook**: Git hook automatically updates reports when HTML/JSON files change
- **Batch Script**: `update_github.bat` for one-click local updates with git commit/push
- **Status Badges**: [![Last Commit](https://img.shields.io/github/last-commit/Fumlop/EdSystemchecker?style=flat-square&label=Last%20Update)](https://github.com/Fumlop/EdSystemchecker/commits/main)

### ⚠️ GitHub Actions Setup Required
**First-time Setup:** Enable workflow permissions in [Repository Settings > Actions](https://github.com/Fumlop/EdSystemchecker/settings/actions):
- Set "Workflow permissions" to **"Read and write permissions"**
- Enable **"Allow GitHub Actions to create and approve pull requests"**

## 📈 Report Features

- **Natural Decay Analysis**: Calculates system decay based on PowerPlay formulas
- **Activity Categorization**: High/Medium/Low activity levels
- **Status Indicators**: ✅ Safe systems (≥20%) vs 🔥 At-risk systems (<20%)
- **Net CP Analysis**: Shows which systems are gaining/losing CP
- **Last Cycle Comparison**: Shows progress from previous cycle

## 📝 Column Reference

All reports include these key metrics:
- **Last Cycle %**: System progress from previous PowerPlay cycle
- **Natural Decay %**: Expected decay without player intervention
- **Current Progress %**: Current cycle progress percentage
- **Net CP**: Difference between current and expected progress CP

## 🔄 Data Updates

Reports are automatically generated with timestamps. System data includes:
- Real-time undermining and reinforcement values
- Mathematical decay calculations using official PowerPlay formulas
- Current cycle validation to ensure data freshness