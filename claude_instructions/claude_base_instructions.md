# Claude Base Instructions - Universal Development Guidelines

## 🎯 Core Principles

### Development Philosophy
- **Efficiency First**: Minimize token usage through targeted analysis
- **Quality Over Quantity**: Deep understanding of specific components rather than superficial overview
- **Incremental Progress**: Build systematically, validate continuously
- **Context Preservation**: Maintain conversation state and progress tracking

### Token Economy Management
- **Pre-Analysis Assessment**: Always check file size and structure before deep-dive
- **Chunk-Based Processing**: Break large files into logical components (50-100 lines)
- **Focused Scope**: Analyze only what's necessary for the current task
- **Avoid Redundancy**: Don't re-analyze unchanged code sections

## 📋 Universal Workflow

### 1. Project Assessment Phase
```bash
# File structure overview
find . -name "*.py" -o -name "*.js" -o -name "*.ts" | head -20
wc -l *.py  # Size assessment
grep -E "^(class|def|import|function)" main_files  # Structure mapping
```

### 2. Import & Dependency Analysis
- **Unused imports**: Identify and remove dead imports
- **Dependency optimization**: Consolidate related imports
- **Import ordering**: Follow language conventions (stdlib → third-party → local)

### 3. Component-wise Analysis Strategy
- **Classes**: Analyze methods individually, check for code duplication
- **Functions**: DRY principle application, parameter optimization
- **Global state**: Minimize globals, prefer dependency injection
- **Configuration**: Centralize settings, avoid hardcoded values

### 4. Code Quality Standards
- **Error Handling**: Comprehensive exception management
- **Logging**: Structured logging with appropriate levels
- **Documentation**: Clear docstrings and inline comments
- **Testing**: Unit tests for critical functions

## 🛠️ Language-Specific Guidelines

### Python Projects
```python
# Import order: stdlib → third-party → local
import os
import sys

import requests
import pandas as pd

from .local_module import LocalClass
```

### JavaScript/TypeScript Projects
```javascript
// ES6+ features preferred
// Async/await over promises
// Proper error boundaries
```

### File Analysis Patterns
- **Small files (<100 lines)**: Full analysis acceptable
- **Medium files (100-300 lines)**: Chunk into logical sections
- **Large files (300+ lines)**: Require refactoring discussion first

## 🔍 Analysis Methodology

### Initial Assessment Template
```
1. File Size: X lines
2. Primary Components: Classes(X), Functions(X), Imports(X)
3. Complexity Level: Low/Medium/High
4. Optimization Potential: Areas identified
5. Risk Assessment: Breaking changes likelihood
```

### Optimization Priority Matrix
1. **Critical**: Security vulnerabilities, data corruption risks
2. **High**: Performance bottlenecks, memory leaks
3. **Medium**: Code duplication, maintainability issues
4. **Low**: Style inconsistencies, minor refactoring

## 📊 Progress Tracking

### Session State Management
- **Current Focus**: What component/file is being worked on
- **Completed Tasks**: What has been successfully implemented
- **Pending Items**: What needs attention next
- **Blockers**: Issues requiring user input or decisions

### Change Documentation
- **What Changed**: Specific modifications made
- **Why Changed**: Reasoning behind each change
- **Impact Assessment**: Potential effects on other components
- **Validation Steps**: How to verify changes work correctly

## 🚨 Error Prevention

### Common Pitfalls to Avoid
- **Over-analysis**: Don't analyze code that's not relevant to current task
- **Assumption Making**: Always verify understanding with user
- **Breaking Changes**: Flag potentially disruptive modifications
- **Context Loss**: Maintain awareness of broader project goals

### Validation Checkpoints
- **Syntax Validation**: Code compiles/runs without errors
- **Logic Verification**: Behavior matches expectations
- **Integration Testing**: Changes don't break existing functionality
- **Performance Check**: No significant performance degradation

## 🎨 Output Formatting Standards

### Code Blocks
```python
# Always include language specification
# Add comments for complex logic
# Use meaningful variable names
```

### Documentation Style
- **Headers**: Use consistent markdown hierarchy
- **Lists**: Bullet points for features, numbered for processes
- **Emphasis**: **Bold** for important concepts, *italic* for variables
- **Code References**: `backticks` for inline code/filenames

### Status Indicators
- ✅ **Completed**: Task finished successfully
- 🔄 **In Progress**: Currently working on
- ⏳ **Pending**: Waiting for input/dependency
- ❌ **Blocked**: Issue preventing progress
- ⚠️ **Warning**: Potential concern flagged

## 🔄 Adaptive Guidelines

### Project-Specific Customization
This base instruction set should be extended with:
- **Domain-specific requirements** (web dev, data science, etc.)
- **Technology stack preferences** (frameworks, libraries)
- **Business logic constraints** (compliance, performance requirements)
- **Team conventions** (coding standards, review processes)

### Continuous Improvement
- **Feedback Integration**: Adapt based on user preferences
- **Pattern Recognition**: Learn from successful approaches
- **Efficiency Optimization**: Refine processes based on outcomes
- **Tool Utilization**: Leverage available development tools effectively

---

*This document serves as the foundation for all Claude development assistance. Project-specific instructions should extend but not override these core principles.*
