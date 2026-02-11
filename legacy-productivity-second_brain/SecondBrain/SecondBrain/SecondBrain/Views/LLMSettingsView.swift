//
//  LLMSettingsView.swift
//  SecondBrain
//

import SwiftUI

struct LLMSettingsView: View {
    @EnvironmentObject var settings: AppSettings
    @State private var providerType: LLMProviderType = .anthropic
    @State private var model: String = ""
    @State private var apiEndpoint: String = ""
    @State private var apiKey: String = ""
    @State private var isTesting = false
    @State private var testResult: String = ""
    @State private var availableModels: [String] = []
    @State private var isLoadingModels = false
    
    var body: some View {
        Form {
            Section(header: Text("LLM Provider")) {
                Picker("Provider", selection: $providerType) {
                    ForEach(LLMProviderType.allCases, id: \.self) { type in
                        Text(type.displayName).tag(type)
                    }
                }
                .onChange(of: providerType) {
                    updateProviderSettings(providerType)
                }
            }
            
            if providerType == .ollama || providerType == .lmStudio {
                Section(header: Text("Local Model Configuration")) {
                    TextField("API Endpoint", text: $apiEndpoint)
                    
                    if isLoadingModels {
                        ProgressView("Loading models...")
                    } else {
                        Picker("Model", selection: $model) {
                            ForEach(availableModels, id: \.self) { modelName in
                                Text(modelName).tag(modelName)
                            }
                        }
                        .disabled(availableModels.isEmpty)
                    }
                    
                    Button("Refresh Models") {
                        loadAvailableModels()
                    }
                }
            }
            
            if providerType.requiresAPIKey {
                Section(header: Text("API Configuration")) {
                    SecureField("API Key", text: $apiKey)
                }
            }
            
            Section {
                Button("Test Connection") {
                    testLLMConnection()
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
        .onAppear {
            loadSettings()
            if providerType == .ollama {
                loadAvailableModels()
            }
        }
    }
    
    private func loadSettings() {
        providerType = settings.llmProviderType
        model = settings.llmModel
        apiEndpoint = settings.llmAPIEndpoint.isEmpty ? providerType.defaultEndpoint : settings.llmAPIEndpoint
        apiKey = settings.llmAPIKey
    }
    
    private func updateProviderSettings(_ type: LLMProviderType) {
        apiEndpoint = type.defaultEndpoint
        model = ""
        availableModels = []
        
        if type == .ollama {
            loadAvailableModels()
        }
    }
    
    private func loadAvailableModels() {
        guard providerType == .ollama else { return }
        
        isLoadingModels = true
        
        // Call Python script to get available models
        let env = ["OLLAMA_BASE_URL": apiEndpoint]
        let result = PythonBridge.shared.executeScript("llm_provider.py", arguments: ["ollama"], environment: env, vaultPath: settings.vaultPath)
        
        DispatchQueue.main.async {
            isLoadingModels = false
            switch result {
            case .success(let output):
                // Parse model list from output
                if let data = output.data(using: .utf8),
                   let json = try? JSONSerialization.jsonObject(with: data) as? [String] {
                    availableModels = json
                } else {
                    // Try to parse from text output
                    let lines = output.components(separatedBy: "\n")
                    availableModels = lines.filter { !$0.isEmpty && !$0.contains("Available") }
                }
            case .failure:
                availableModels = []
            }
        }
    }
    
    private func saveSettings() {
        settings.llmProviderType = providerType
        settings.llmModel = model
        settings.llmAPIEndpoint = apiEndpoint
        settings.llmAPIKey = apiKey
        settings.saveCredentials()
        
        // Set environment variables for Python scripts
        var env: [String: String] = [
            "LLM_PROVIDER": providerType.rawValue
        ]
        
        if !model.isEmpty {
            env["LLM_MODEL"] = model
        }
        
        if providerType == .ollama {
            env["OLLAMA_BASE_URL"] = apiEndpoint
        } else if providerType == .lmStudio {
            env["LMSTUDIO_BASE_URL"] = apiEndpoint
        }
        
        if !apiKey.isEmpty {
            env["LLM_API_KEY"] = apiKey
            if providerType == .anthropic {
                env["ANTHROPIC_API_KEY"] = apiKey
            } else if providerType == .openai {
                env["OPENAI_API_KEY"] = apiKey
            }
        }
    }
    
    private func testLLMConnection() {
        isTesting = true
        testResult = "Testing..."
        
        var env: [String: String] = [
            "LLM_PROVIDER": providerType.rawValue
        ]
        
        if !model.isEmpty {
            env["LLM_MODEL"] = model
        }
        
        if providerType == .ollama {
            env["OLLAMA_BASE_URL"] = apiEndpoint
        } else if providerType == .lmStudio {
            env["LMSTUDIO_BASE_URL"] = apiEndpoint
        }
        
        if !apiKey.isEmpty {
            env["LLM_API_KEY"] = apiKey
            if providerType == .anthropic {
                env["ANTHROPIC_API_KEY"] = apiKey
            } else if providerType == .openai {
                env["OPENAI_API_KEY"] = apiKey
            }
        }
        
        // Test with a simple classification
        let testThought = "Test message for LLM connection"
        let result = PythonBridge.shared.executeScript("process_inbox.py", arguments: ["--test-classify", testThought], environment: env, vaultPath: settings.vaultPath)
        
        DispatchQueue.main.async {
            isTesting = false
            switch result {
            case .success(let output):
                if output.contains("destination") || output.contains("✅") {
                    testResult = "✅ LLM connection successful!"
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
    LLMSettingsView()
        .environmentObject(AppSettings())
}
