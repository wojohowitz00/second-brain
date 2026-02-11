//
//  AppSettings.swift
//  SecondBrain
//

import Foundation
import Combine

class AppSettings: ObservableObject {
    @Published var vaultPath: String {
        didSet {
            UserDefaults.standard.set(vaultPath, forKey: "vaultPath")
        }
    }
    
    @Published var slackBotToken: String = ""
    @Published var slackChannelID: String = ""
    @Published var slackUserID: String = ""
    
    @Published var llmProviderType: LLMProviderType = .anthropic {
        didSet {
            UserDefaults.standard.set(llmProviderType.rawValue, forKey: "llmProviderType")
        }
    }
    
    @Published var llmModel: String = ""
    @Published var llmAPIEndpoint: String = ""
    @Published var llmAPIKey: String = ""
    
    @Published var setupCompleted: Bool {
        didSet {
            UserDefaults.standard.set(setupCompleted, forKey: "setupCompleted")
        }
    }
    
    init() {
        // Initialize stored properties first
        self.vaultPath = UserDefaults.standard.string(forKey: "vaultPath") ?? 
            (FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent("SecondBrain").path)
        self.llmProviderType = LLMProviderType(
            rawValue: UserDefaults.standard.string(forKey: "llmProviderType") ?? "anthropic"
        ) ?? .anthropic
        
        // Initialize setupCompleted with a temporary value
        self.setupCompleted = false
        
        // Now we can call loadCredentials() since all properties are initialized
        loadCredentials()
        
        // Check if setup is completed - either explicitly set, or if credentials exist
        let explicitSetupCompleted = UserDefaults.standard.bool(forKey: "setupCompleted")
        let hasCredentials = !slackBotToken.isEmpty || !llmAPIKey.isEmpty
        
        // Update setupCompleted if needed
        if explicitSetupCompleted || hasCredentials {
            self.setupCompleted = true
        }
    }
    
    func loadCredentials() {
        let keychain = KeychainManager.shared
        slackBotToken = keychain.get(key: "slackBotToken") ?? ""
        slackChannelID = keychain.get(key: "slackChannelID") ?? ""
        slackUserID = keychain.get(key: "slackUserID") ?? ""
        llmAPIKey = keychain.get(key: "llmAPIKey") ?? ""
    }
    
    func saveCredentials() {
        let keychain = KeychainManager.shared
        if !slackBotToken.isEmpty {
            _ = keychain.set(key: "slackBotToken", value: slackBotToken)
        }
        if !slackChannelID.isEmpty {
            _ = keychain.set(key: "slackChannelID", value: slackChannelID)
        }
        if !slackUserID.isEmpty {
            _ = keychain.set(key: "slackUserID", value: slackUserID)
        }
        if !llmAPIKey.isEmpty {
            _ = keychain.set(key: "llmAPIKey", value: llmAPIKey)
        }
    }
}

enum LLMProviderType: String, CaseIterable {
    case anthropic = "anthropic"
    case openai = "openai"
    case ollama = "ollama"
    case lmStudio = "lmstudio"
    
    var displayName: String {
        switch self {
        case .anthropic: return "Anthropic Claude"
        case .openai: return "OpenAI"
        case .ollama: return "Ollama (Local)"
        case .lmStudio: return "LM Studio (Local)"
        }
    }
    
    var defaultEndpoint: String {
        switch self {
        case .anthropic: return "https://api.anthropic.com"
        case .openai: return "https://api.openai.com/v1"
        case .ollama: return "http://localhost:11434"
        case .lmStudio: return "http://localhost:1234/v1"
        }
    }
    
    var requiresAPIKey: Bool {
        switch self {
        case .anthropic, .openai: return true
        case .ollama, .lmStudio: return false
        }
    }
}
