//
//  SlackSettingsView.swift
//  SecondBrain
//

import SwiftUI

struct SlackSettingsView: View {
    @EnvironmentObject var settings: AppSettings
    @State private var botToken: String = ""
    @State private var channelID: String = ""
    @State private var userID: String = ""
    @State private var isTesting = false
    @State private var testResult: String = ""
    
    var body: some View {
        Form {
            Section(header: Text("Slack Configuration")) {
                SecureField("Bot Token", text: $botToken)
                    .onAppear {
                        botToken = settings.slackBotToken
                    }
                
                TextField("Channel ID", text: $channelID)
                    .onAppear {
                        channelID = settings.slackChannelID
                    }
                
                TextField("User ID", text: $userID)
                    .onAppear {
                        userID = settings.slackUserID
                    }
            }
            
            Section {
                Button("Test Connection") {
                    testSlackConnection()
                }
                .disabled(isTesting)
                
                if !testResult.isEmpty {
                    Text(testResult)
                        .foregroundColor(testResult.contains("✅") ? .green : .red)
                        .font(.caption)
                }
            }
            
            Section {
                Button("Save") {
                    saveSettings()
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .frame(maxWidth: 600)
    }
    
    private func saveSettings() {
        settings.slackBotToken = botToken
        settings.slackChannelID = channelID
        settings.slackUserID = userID
        settings.saveCredentials()
    }
    
    private func testSlackConnection() {
        isTesting = true
        testResult = "Testing..."
        
        // Set environment variables temporarily
        let env = [
            "SLACK_BOT_TOKEN": botToken,
            "SLACK_CHANNEL_ID": channelID,
            "SLACK_USER_ID": userID
        ]
        
        let result = PythonBridge.shared.executeScript("slack_client.py", arguments: ["--test"], environment: env, vaultPath: settings.vaultPath)
        
        DispatchQueue.main.async {
            isTesting = false
            switch result {
            case .success(let output):
                if output.contains("success") || output.contains("✅") {
                    testResult = "✅ Connection successful!"
                } else {
                    testResult = "❌ Connection failed: \(output)"
                }
            case .failure(let error):
                testResult = "❌ Error: \(error.localizedDescription)"
            }
        }
    }
}

#Preview {
    SlackSettingsView()
        .environmentObject(AppSettings())
}
