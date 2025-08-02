@{
    # Module manifest for Neural Dream State Automation
    RootModule = 'neural-dream.psm1'
    ModuleVersion = '0.8.2'
    GUID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    Author = 'NEWBORN Cognitive Architecture'
    CompanyName = 'Catalyst-NEWBORN'
    Copyright = '(c) 2025 Catalyst-NEWBORN. All rights reserved.'
    Description = 'Neural Memory Optimization and Synaptic Pruning Module for NEWBORN Cognitive Architecture'
    
    # Minimum version of the PowerShell engine required by this module
    PowerShellVersion = '5.1'
    
    # Functions to export from this module
    FunctionsToExport = @(
        'Invoke-DreamState',
        'Invoke-AutomatedMaintenance',
        'dream',
        'neural-housekeeping',
        'optimize-synapses',
        'cognitive-status',
        'scan-orphans'
    )
    
    # Cmdlets to export from this module
    CmdletsToExport = @()
    
    # Variables to export from this module
    VariablesToExport = @()
    
    # Aliases to export from this module
    AliasesToExport = @()
    
    # Private data to pass to the module specified in RootModule/ModuleToProcess
    PrivateData = @{
        PSData = @{
            # Tags applied to this module
            Tags = @('NEWBORN', 'Cognitive', 'Neural', 'Dream', 'Automation', 'Synaptic', 'Memory')
            
            # A URL to the license for this module
            LicenseUri = ''
            
            # A URL to the main website for this project
            ProjectUri = 'https://github.com/fabioc-aloha/Catalyst-NEWBORN'
            
            # A URL to an icon representing this module
            IconUri = ''
            
            # Release notes for this module
            ReleaseNotes = 'Neural Dream State Automation v0.8.2 NILOCTBIUM - Enhanced cognitive architecture maintenance'
        }
    }
}
