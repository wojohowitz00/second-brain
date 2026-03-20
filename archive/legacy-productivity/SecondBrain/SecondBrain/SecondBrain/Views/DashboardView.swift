//
//  DashboardView.swift
//  SecondBrain
//

import SwiftUI

struct DashboardView: View {
    @EnvironmentObject var backgroundService: BackgroundService
    @EnvironmentObject var settings: AppSettings
    @State private var systemStatus: SystemStatus = .unknown
    @State private var lastSuccessTime: String = "Never"
    @State private var failureCountToday: Int = 0
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // System Status
                StatusCard(title: "System Status") {
                    HStack {
                        StatusIndicator(status: systemStatus)
                        Text(systemStatus.displayName)
                            .font(.headline)
                    }
                    
                    if backgroundService.isRunning {
                        Text("Background service is running")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    } else {
                        Text("Background service is stopped")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                // Quick Stats
                HStack(spacing: 16) {
                    StatCard(title: "Last Success", value: lastSuccessTime)
                    StatCard(title: "Failures Today", value: "\(failureCountToday)")
                    StatCard(title: "Status", value: backgroundService.statusMessage)
                }
                
                // Quick Actions
                StatusCard(title: "Quick Actions") {
                    VStack(spacing: 12) {
                        HStack(spacing: 12) {
                            ActionButton(title: "Process Inbox", icon: "arrow.clockwise") {
                                backgroundService.triggerManualProcess()
                            }
                            
                            ActionButton(title: "Health Check", icon: "heart.fill") {
                                backgroundService.triggerHealthCheck()
                            }
                        }
                        
                        HStack(spacing: 12) {
                            ActionButton(title: "Daily Digest", icon: "sunrise.fill") {
                                backgroundService.triggerDigest()
                            }
                            
                            ActionButton(title: "Weekly Review", icon: "calendar") {
                                backgroundService.triggerReview()
                            }
                        }
                    }
                }
                
                // Background Service Control
                StatusCard(title: "Background Service") {
                    HStack {
                        if backgroundService.isRunning {
                            Button("Stop") {
                                backgroundService.stop()
                            }
                            .buttonStyle(.borderedProminent)
                            .tint(.red)
                        } else {
                            Button("Start") {
                                backgroundService.start()
                            }
                            .buttonStyle(.borderedProminent)
                        }
                        
                        Spacer()
                        
                        if let lastRun = backgroundService.lastInboxRun {
                            Text("Last inbox run: \(lastRun.formatted(date: .omitted, time: .shortened))")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }
            }
            .padding()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .onAppear {
            loadSystemStatus()
        }
        .onReceive(backgroundService.$lastInboxRun) { _ in
            loadSystemStatus()
        }
    }
    
    private func loadSystemStatus() {
        // Build environment variables from settings
        var env: [String: String] = [:]
        if !settings.slackBotToken.isEmpty {
            env["SLACK_BOT_TOKEN"] = settings.slackBotToken
        }
        if !settings.slackChannelID.isEmpty {
            env["SLACK_CHANNEL_ID"] = settings.slackChannelID
        }
        if !settings.slackUserID.isEmpty {
            env["SLACK_USER_ID"] = settings.slackUserID
        }
        if !settings.llmAPIKey.isEmpty {
            env["LLM_API_KEY"] = settings.llmAPIKey
            if settings.llmProviderType == .anthropic {
                env["ANTHROPIC_API_KEY"] = settings.llmAPIKey
            } else if settings.llmProviderType == .openai {
                env["OPENAI_API_KEY"] = settings.llmAPIKey
            }
        }
        env["LLM_PROVIDER"] = settings.llmProviderType.rawValue
        
        // Check health via Python script
        let result = PythonBridge.shared.executeScript("health_check.py", arguments: ["--quiet"], environment: env, vaultPath: settings.vaultPath)
        
        switch result {
        case .success(let output):
            if output.contains("HEALTHY") {
                systemStatus = .healthy
            } else {
                systemStatus = .unhealthy
            }
        case .failure:
            systemStatus = .unknown
        }
        
        // Get last success time from state file
        let vaultPath = settings.vaultPath
        let stateFile = URL(fileURLWithPath: vaultPath).appendingPathComponent("_scripts/.state/last_run.json")
        
        if let data = try? Data(contentsOf: stateFile),
           let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           let lastSuccess = json["last_success"] as? String {
            if let date = ISO8601DateFormatter().date(from: lastSuccess) {
                let formatter = DateFormatter()
                formatter.dateStyle = .short
                formatter.timeStyle = .short
                lastSuccessTime = formatter.string(from: date)
            }
        }
        
        // Get failure count
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        let failedLog = URL(fileURLWithPath: vaultPath)
            .appendingPathComponent("_inbox_log")
            .appendingPathComponent("FAILED-\(dateFormatter.string(from: Date())).md")
        
        if let content = try? String(contentsOf: failedLog, encoding: .utf8) {
            failureCountToday = content.components(separatedBy: "\n## ").count - 1
        }
    }
}

struct StatusCard<Content: View>: View {
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

struct StatCard: View {
    let title: String
    let value: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.title2)
                .fontWeight(.semibold)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(8)
    }
}

struct ActionButton: View {
    let title: String
    let icon: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                Text(title)
            }
            .frame(maxWidth: .infinity)
        }
        .buttonStyle(.bordered)
    }
}

#Preview {
    DashboardView()
        .environmentObject(BackgroundService())
        .environmentObject(AppSettings())
}
