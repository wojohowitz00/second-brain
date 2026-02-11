import Foundation
import SwiftUI

@MainActor
class SettingsViewModel: ObservableObject {
    @AppStorage("vaultPath") var vaultPath: String = ""
    @AppStorage("selectedModel") var selectedModel: String = ""
    @AppStorage("slackToken") var slackToken: String = ""
    @AppStorage("slackChannelID") var slackChannelID: String = ""
    
    @Published var availableModels: [String] = []
    @Published var isLoadingModels: Bool = false
    @Published var errorMessage: String?
    
    private let ollamaClient = OllamaClient()
    
    func fetchModels() async {
        isLoadingModels = true
        errorMessage = nil
        do {
            let models = try await ollamaClient.listModels()
            availableModels = models
            if selectedModel.isEmpty, let first = models.first {
                selectedModel = first
            }
        } catch {
            errorMessage = "Failed to load models: \(error.localizedDescription)"
        }
        isLoadingModels = false
    }
    
    func selectVault() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false
        panel.prompt = "Select Vault"
        
        if panel.runModal() == .OK, let url = panel.url {
            vaultPath = url.path
        }
    }
    
    // MARK: - Auto Launch
    @Published var isStartAtLoginEnabled: Bool = false {
        didSet {
            if isStartAtLoginEnabled != oldValue {
                toggleLaunchAgent(enable: isStartAtLoginEnabled)
            }
        }
    }
    
    func checkLaunchAgentStatus() {
        let plistURL = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Library/LaunchAgents/com.richardyu.SecondBrain.plist")
        isStartAtLoginEnabled = FileManager.default.fileExists(atPath: plistURL.path)
    }
    
    private func toggleLaunchAgent(enable: Bool) {
        let plistURL = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Library/LaunchAgents/com.richardyu.SecondBrain.plist")
        
        if enable {
            // Create Plist
            let appPath = Bundle.main.bundlePath
            // Ensure we are pointing to the executable inside the bundle
            let executablePath = appPath + "/Contents/MacOS/Second Brain"
            
            let plistContent = """
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>com.richardyu.SecondBrain</string>
                <key>ProgramArguments</key>
                <array>
                    <string>\(executablePath)</string>
                </array>
                <key>RunAtLoad</key>
                <true/>
                <key>StandardOutPath</key>
                <string>/tmp/com.richardyu.SecondBrain.out</string>
                <key>StandardErrorPath</key>
                <string>/tmp/com.richardyu.SecondBrain.err</string>
            </dict>
            </plist>
            """
            
            do {
                try plistContent.write(to: plistURL, atomically: true, encoding: .utf8)
            } catch {
                print("Failed to enable start at login: \(error)")
                isStartAtLoginEnabled = false // Revert UI
            }
        } else {
            // Remove Plist
            do {
                try FileManager.default.removeItem(at: plistURL)
            } catch {
                print("Failed to disable start at login: \(error)")
            }
        }
    }
}

