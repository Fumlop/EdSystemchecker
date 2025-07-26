# Elite Dangerous PowerPlay System Checker

Automated tool for analyzing Elite Dangerous PowerPlay system status from Inara data.

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
_norefresh_

## 🚀 Quick Start

1. **Extract System Data**: Run `python extract.py` to process HTML files
2. **Generate Reports**: Run the markdown generators:
   - `python create_stronghold_md.py`
   - `python create_exploited_md.py`
   - `python create_fortified_md.py`
   - `python create_contested_md.py`
   - `python create_accquise_prio.py`

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