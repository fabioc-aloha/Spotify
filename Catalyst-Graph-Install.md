# Catalyst-Graph Installation Guide

A simple setup guide for the Catalyst cognitive architecture visualization system.

**Version**: v2.1 PRIMARY - Optimal 3-Layer Architecture
**Philosophy**: Clarity over Complexity - Enhanced theming with visual comfort

## 📁 Required Files

### Main Script
- `Catalyst-Graph.ps1` (v2.1 PRIMARY - optimal 3-layer architecture)

### Related Files
- `Catalyst-Graphv3-EXPERIMENTAL.ps1` (4-layer experimental - archived for complexity analysis)

### Output Directory
- The script automatically creates `catalyst-graphs/` directory for generated diagrams

## 🚀 Quick Setup

### Prerequisites
- **Windows PowerShell 5.1+** or **PowerShell Core 7+**
- **Visual Studio Code** (recommended for viewing diagrams)

### One-Command Setup
```powershell
# Run from your project directory
.\Catalyst-Graph.ps1 -AutoOpen
```

## 📋 Setup Steps

### Step 1: PowerShell Execution Policy
```powershell
# Allow script execution (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Install VS Code Mermaid Extension (Optional)
```powershell
# For diagram viewing in VS Code
code --install-extension bierner.markdown-mermaid
```

### Step 3: Run the Script
```powershell
# Generate your cognitive architecture diagram
.\Catalyst-Graph.ps1 -AutoOpen
```

*Note: The script automatically creates the `catalyst-graphs/` directory for output files.*

## 🎯 What You Get

- **Catalyst-Graph.ps1 v2.1**: PRIMARY visualization script with optimal 3-layer architecture
- **catalyst-graphs/**: Generated diagram files with enhanced theming
- **Beautiful Diagrams**: Enhanced 3-layer cognitive architecture visualizations with:
  - **Left-right orientation** optimized for wide-screen viewing
  - **Light yellow background** (#fffef7) for visual comfort during extended analysis
  - **Proven cognitive model**: Core → Processing → UI flow
  - **Meta-cognitive insight**: Simpler architecture provides better understanding

## 🔧 Usage Options

```powershell
# Generate and auto-open diagram
.\Catalyst-Graph.ps1 -AutoOpen

# Generate diagram only
.\Catalyst-Graph.ps1
```

## 🛠️ Common Issues

**PowerShell Script Error:**
```powershell
# If you get "execution disabled" error:
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\Catalyst-Graph.ps1 -AutoOpen
```

**Script Not Found:**
```powershell
# Make sure you're in the right folder:
Test-Path ".\Catalyst-Graph.ps1"  # Should return True
```

**Diagram Not Showing:**
```powershell
# Install VS Code Mermaid extension:
code --install-extension bierner.markdown-mermaid
```

## 📊 Sample Output

When you run the script, you'll see:

```
🧠 Catalyst Memory & Synapse Chart Generator v2.1 - Enhanced 3-Layer
==================================================
🔍 Phase 1: Discovering knowledge files...
   ✅ Found 31 files across 5 memory systems
🧠 Phase 2: Analyzing embedded synapses...
   ✅ Discovered 88 synapse connections
🎨 Phase 3: Generating Catalyst Memory Chart...
   ✅ Diagram saved to: .\catalyst-graphs\catalyst-overview-YYYYMMDD-HHMMSS.md

📊 Cognitive Architecture Health:
   � Files: 31 across 5 memory systems
   🔗 Connections: 88 total (57 high-strength)
   💪 Connectivity Ratio: 2.84 connections per file
   🎯 Architecture Status: EXCELLENT

🎉 Catalyst Memory Chart completed successfully!
📁 Output: .\catalyst-graphs\catalyst-overview-YYYYMMDD-HHMMSS.md
```

This creates a beautiful visual diagram of your cognitive architecture with:
- **Enhanced 3-layer structure** showing optimal cognitive flow: Core → Processing → UI
- **Left-right orientation** with horizontal flow for wide-screen optimization
- **Light yellow background** (#fffef7) for reduced eye strain during extended analysis
- **Weight-proportional connection lines** with thickness indicating synapse strength
- **Color-coded file aging** from newest (🟢) to oldest (🔴) with stack rankings
- **Professional theming** with cardinal curves and enhanced spacing

---

*Setup guide for Catalyst-Graph.ps1 v2.1 PRIMARY - Optimal 3-layer cognitive architecture visualization with enhanced theming and meta-cognitive clarity principles*
