//
//  BackgroundService.swift
//  SecondBrain
//

import Foundation
import Combine

class BackgroundService: ObservableObject {
    @Published var isRunning = false
    @Published var lastInboxRun: Date?
    @Published var lastFixRun: Date?
    @Published var lastHealthRun: Date?
    @Published var statusMessage: String = "Stopped"
    
    private var inboxTimer: Timer?
    private var fixTimer: Timer?
    private var healthTimer: Timer?
    
    private let inboxInterval: TimeInterval = 120 // 2 minutes
    private let fixInterval: TimeInterval = 300 // 5 minutes
    private let healthInterval: TimeInterval = 3600 // 1 hour
    
    var vaultPath: String? = nil
    var settings: AppSettings? = nil
    
    private func getEnvironmentVariables() -> [String: String] {
        guard let settings = settings else {
            print("⚠️ BackgroundService: settings is nil")
            return [:]
        }
        
        // Reload credentials from Keychain to ensure they're up to date
        settings.loadCredentials()
        
        var env: [String: String] = [:]
        
        // Slack credentials
        if !settings.slackBotToken.isEmpty {
            env["SLACK_BOT_TOKEN"] = settings.slackBotToken
        }
        if !settings.slackChannelID.isEmpty {
            env["SLACK_CHANNEL_ID"] = settings.slackChannelID
        }
        if !settings.slackUserID.isEmpty {
            env["SLACK_USER_ID"] = settings.slackUserID
        }
        
        // LLM credentials
        if !settings.llmAPIKey.isEmpty {
            env["LLM_API_KEY"] = settings.llmAPIKey
            // Set provider-specific keys
            switch settings.llmProviderType {
            case .anthropic:
                env["ANTHROPIC_API_KEY"] = settings.llmAPIKey
            case .openai:
                env["OPENAI_API_KEY"] = settings.llmAPIKey
            case .ollama:
                if !settings.llmAPIEndpoint.isEmpty {
                    env["OLLAMA_BASE_URL"] = settings.llmAPIEndpoint
                }
            case .lmStudio:
                if !settings.llmAPIEndpoint.isEmpty {
                    env["LMSTUDIO_BASE_URL"] = settings.llmAPIEndpoint
                }
            }
        }
        
        // LLM provider configuration
        env["LLM_PROVIDER"] = settings.llmProviderType.rawValue
        if !settings.llmModel.isEmpty {
            env["LLM_MODEL"] = settings.llmModel
        }
        if !settings.llmAPIEndpoint.isEmpty {
            env["LLM_API_ENDPOINT"] = settings.llmAPIEndpoint
        }
        
        // Vault path
        if !settings.vaultPath.isEmpty {
            env["VAULT_PATH"] = settings.vaultPath
        }
        
        return env
    }
    
    func start() {
        guard !isRunning else { return }
        
        isRunning = true
        statusMessage = "Running"
        
        // Start inbox processing timer (every 2 minutes)
        inboxTimer = Timer.scheduledTimer(withTimeInterval: inboxInterval, repeats: true) { [weak self] _ in
            self?.processInbox()
        }
        processInbox() // Run immediately
        
        // Start fix handler timer (every 5 minutes)
        fixTimer = Timer.scheduledTimer(withTimeInterval: fixInterval, repeats: true) { [weak self] _ in
            self?.processFixes()
        }
        processFixes() // Run immediately
        
        // Start health check timer (every hour)
        healthTimer = Timer.scheduledTimer(withTimeInterval: healthInterval, repeats: true) { [weak self] _ in
            self?.checkHealth()
        }
        checkHealth() // Run immediately
    }
    
    func stop() {
        isRunning = false
        statusMessage = "Stopped"
        
        inboxTimer?.invalidate()
        fixTimer?.invalidate()
        healthTimer?.invalidate()
        
        inboxTimer = nil
        fixTimer = nil
        healthTimer = nil
    }
    
    private func processInbox() {
        statusMessage = "Processing inbox..."
        let env = getEnvironmentVariables()
        let result = PythonBridge.shared.executeScript("process_inbox.py", arguments: [], environment: env, vaultPath: vaultPath)
        
        DispatchQueue.main.async {
            self.lastInboxRun = Date()
            switch result {
            case .success:
                self.statusMessage = "Inbox processed successfully"
            case .failure(let error):
                self.statusMessage = "Inbox processing failed: \(error.localizedDescription)"
            }
        }
    }
    
    private func processFixes() {
        let env = getEnvironmentVariables()
        let result = PythonBridge.shared.executeScript("fix_handler.py", arguments: [], environment: env, vaultPath: vaultPath)
        
        DispatchQueue.main.async {
            self.lastFixRun = Date()
            if case .failure(let error) = result {
                print("Fix handler error: \(error.localizedDescription)")
            }
        }
    }
    
    private func checkHealth() {
        let env = getEnvironmentVariables()
        let result = PythonBridge.shared.executeScript("health_check.py", arguments: ["--quiet"], environment: env, vaultPath: vaultPath)
        
        DispatchQueue.main.async {
            self.lastHealthRun = Date()
            if case .failure(let error) = result {
                print("Health check error: \(error.localizedDescription)")
            }
        }
    }
    
    func triggerManualProcess() {
        processInbox()
    }
    
    func triggerHealthCheck() {
        checkHealth()
    }
    
    func triggerDigest() {
        let env = getEnvironmentVariables()
        let result = PythonBridge.shared.executeScript("daily_digest.py", arguments: [], environment: env, vaultPath: vaultPath)
        if case .failure(let error) = result {
            print("Digest error: \(error.localizedDescription)")
        }
    }
    
    func triggerReview() {
        let env = getEnvironmentVariables()
        let result = PythonBridge.shared.executeScript("weekly_review.py", arguments: [], environment: env, vaultPath: vaultPath)
        if case .failure(let error) = result {
            print("Review error: \(error.localizedDescription)")
        }
    }
}
