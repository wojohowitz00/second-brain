//
//  HelpView.swift
//  SecondBrain
//

import SwiftUI

struct HelpView: View {
    @State private var selectedSection: HelpSection = .gettingStarted
    
    enum HelpSection: String, CaseIterable, Identifiable {
        case gettingStarted = "Getting Started"
        case dailyUsage = "Daily Usage"
        case troubleshooting = "Troubleshooting"
        case tips = "Tips & Best Practices"
        
        var id: String { rawValue }
        
        var icon: String {
            switch self {
            case .gettingStarted: return "play.circle.fill"
            case .dailyUsage: return "clock.fill"
            case .troubleshooting: return "wrench.and.screwdriver.fill"
            case .tips: return "lightbulb.fill"
            }
        }
    }
    
    var body: some View {
        HSplitView {
            // Sidebar
            List(HelpSection.allCases, selection: $selectedSection) { section in
                Label(section.rawValue, systemImage: section.icon)
                    .tag(section)
            }
            .frame(minWidth: 200)
            
            // Content
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    switch selectedSection {
                    case .gettingStarted:
                        GettingStartedContent()
                    case .dailyUsage:
                        DailyUsageContent()
                    case .troubleshooting:
                        TroubleshootingContent()
                    case .tips:
                        TipsContent()
                    }
                }
                .padding()
                .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct GettingStartedContent: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Getting Started")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            SectionView(title: "1. Install Python Dependencies") {
                CodeBlock(code: """
                cd ~/SecondBrain/_scripts
                pip3 install -r requirements.txt
                """)
            }
            
            SectionView(title: "2. Configure Settings") {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Go to Settings and configure:")
                    BulletPoint(text: "Slack: Bot token, channel ID, user ID")
                    BulletPoint(text: "LLM: Choose provider and enter API key")
                    BulletPoint(text: "Obsidian: Select your vault folder")
                }
            }
            
            SectionView(title: "3. Start Background Service") {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Go to Dashboard and click 'Start'")
                    Text("The app will now automatically process messages every 2 minutes")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            SectionView(title: "4. Capture Your First Thought") {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Post a message to your Slack inbox channel:")
                    CodeBlock(code: "Had a great conversation with Sarah about the new product launch")
                    Text("The app will automatically:")
                    BulletPoint(text: "Detect the message")
                    BulletPoint(text: "Classify it (person/project/idea/admin)")
                    BulletPoint(text: "Create a file in your Obsidian vault")
                    BulletPoint(text: "Reply in Slack with confirmation")
                }
            }
        }
    }
}

struct DailyUsageContent: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Daily Usage")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            SectionView(title: "Capturing Thoughts") {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Simply post messages to your Slack inbox channel. The app will:")
                    BulletPoint(text: "Process messages every 2 minutes")
                    BulletPoint(text: "Classify and file automatically")
                    BulletPoint(text: "Reply with confirmation")
                }
            }
            
            SectionView(title: "Dashboard") {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Monitor system status and trigger actions:")
                    BulletPoint(text: "System Status: Shows if everything is healthy")
                    BulletPoint(text: "Quick Actions: Process inbox, health check, digest, review")
                    BulletPoint(text: "Background Service: Start/stop automated processing")
                }
            }
            
            SectionView(title: "Messages View") {
                VStack(alignment: .leading, spacing: 12) {
                    Text("View all messages from your inbox:")
                    BulletPoint(text: "See processing status")
                    BulletPoint(text: "View classification results")
                    BulletPoint(text: "Manually trigger classification")
                }
            }
            
            SectionView(title: "Vault Browser") {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Browse your Obsidian vault:")
                    BulletPoint(text: "Navigate by folder (people/projects/ideas/admin)")
                    BulletPoint(text: "View file contents")
                    BulletPoint(text: "See how thoughts are organized")
                }
            }
            
            SectionView(title: "Logs") {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Monitor real-time processing:")
                    BulletPoint(text: "Filter by type (processing/health/fixes)")
                    BulletPoint(text: "Search logs")
                    BulletPoint(text: "Export for debugging")
                }
            }
        }
    }
}

struct TroubleshootingContent: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Troubleshooting")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            TroubleshootingItem(
                issue: "Messages Not Processing",
                solution: """
                1. Check if background service is running (Dashboard)
                2. Verify Slack credentials (Settings → Slack → Test Connection)
                3. Check logs for error messages
                4. Verify channel ID is correct
                """
            )
            
            TroubleshootingItem(
                issue: "LLM Connection Fails",
                solution: """
                Cloud APIs:
                • Verify API key is correct
                • Check you have credits/quota
                • Verify internet connection
                
                Local Models:
                • Verify Ollama/LM Studio is running
                • Check endpoint URL
                • Ensure a model is downloaded
                """
            )
            
            TroubleshootingItem(
                issue: "Can't Find Vault",
                solution: """
                1. Verify vault path in Settings → Obsidian
                2. Check folder structure exists
                3. Ensure you have read/write permissions
                4. Try selecting the vault path again
                """
            )
            
            TroubleshootingItem(
                issue: "Python Script Errors",
                solution: """
                1. Verify scripts exist: ls ~/SecondBrain/_scripts/
                2. Check Python version: python3 --version (needs 3.9+)
                3. Verify dependencies: pip3 install -r requirements.txt
                4. Check script permissions
                """
            )
        }
    }
}

struct TipsContent: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Tips & Best Practices")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            SectionView(title: "Writing Effective Messages") {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Good messages:")
                    BulletPoint(text: "Clear and specific: 'Met with John about Q2 roadmap'")
                    BulletPoint(text: "Include context: 'Sarah mentioned the API is ready'")
                    BulletPoint(text: "Action items: 'Need to follow up with Mike about budget'")
                    
                    Text("Less effective:")
                        .padding(.top)
                    BulletPoint(text: "Too vague: 'Had a meeting'")
                    BulletPoint(text: "Missing context: 'Talked about the thing'")
                }
            }
            
            SectionView(title: "Organizing Your Vault") {
                VStack(alignment: .leading, spacing: 12) {
                    BulletPoint(text: "People: Use full names or consistent nicknames")
                    BulletPoint(text: "Projects: Use descriptive project names")
                    BulletPoint(text: "Ideas: Be specific about the idea")
                    BulletPoint(text: "Admin: Tasks, reminders, system notes")
                }
            }
            
            SectionView(title: "Background Service") {
                VStack(alignment: .leading, spacing: 12) {
                    BulletPoint(text: "Keep it running for best results")
                    BulletPoint(text: "Check logs regularly for errors")
                    BulletPoint(text: "Run health checks if something seems off")
                }
            }
            
            SectionView(title: "Performance Tips") {
                VStack(alignment: .leading, spacing: 12) {
                    BulletPoint(text: "Local models: Faster for privacy, require powerful hardware")
                    BulletPoint(text: "Cloud models: More reliable, require internet and API costs")
                    BulletPoint(text: "Batch processing: The app processes messages efficiently")
                }
            }
        }
    }
}

struct SectionView<Content: View>: View {
    let title: String
    let content: Content
    
    init(title: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.content = content()
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.headline)
            
            content
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(8)
    }
}

struct BulletPoint: View {
    let text: String
    
    var body: some View {
        HStack(alignment: .top, spacing: 8) {
            Text("•")
            Text(text)
        }
    }
}

struct CodeBlock: View {
    let code: String
    
    var body: some View {
        Text(code)
            .font(.system(.body, design: .monospaced))
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color(NSColor.textBackgroundColor))
            .cornerRadius(6)
    }
}

struct TroubleshootingItem: View {
    let issue: String
    let solution: String
    
    var body: some View {
        SectionView(title: issue) {
            Text(solution)
                .font(.body)
        }
    }
}

#Preview {
    HelpView()
}
