//
//  WelcomeView.swift
//  SecondBrain
//

import SwiftUI
import UniformTypeIdentifiers

struct WelcomeView: View {
    @EnvironmentObject var settings: AppSettings
    @State private var currentStep: SetupStep = .welcome
    @Binding var isPresented: Bool
    
    enum SetupStep {
        case welcome
        case slack
        case llm
        case obsidian
        case complete
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Progress indicator
            if currentStep != .welcome && currentStep != .complete {
                ProgressView(value: progressValue, total: 3)
                    .progressViewStyle(.linear)
                    .padding()
            }
            
            // Content
            Group {
                switch currentStep {
                case .welcome:
                    WelcomeStepView(onContinue: { currentStep = .slack })
                case .slack:
                    SetupSlackStepView(
                        onContinue: { currentStep = .llm },
                        onSkip: { currentStep = .llm }
                    )
                case .llm:
                    SetupLLMStepView(
                        onContinue: { currentStep = .obsidian },
                        onSkip: { currentStep = .obsidian }
                    )
                case .obsidian:
                    SetupObsidianStepView(
                        onContinue: { completeSetup() },
                        onSkip: { completeSetup() }
                    )
                case .complete:
                    SetupCompleteView(onFinish: { isPresented = false })
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .frame(width: 800, height: 600)
    }
    
    private var progressValue: Double {
        switch currentStep {
        case .welcome: return 0
        case .slack: return 1
        case .llm: return 2
        case .obsidian: return 3
        case .complete: return 3
        }
    }
    
    private func completeSetup() {
        settings.setupCompleted = true
        currentStep = .complete
    }
}

struct WelcomeStepView: View {
    let onContinue: () -> Void
    
    var body: some View {
        VStack(spacing: 30) {
            Image(systemName: "brain.head.profile")
                .font(.system(size: 80))
                .foregroundColor(.blue)
            
            Text("Welcome to Second Brain")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            Text("Capture your thoughts from Slack and organize them automatically in Obsidian")
                .font(.title3)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            
            VStack(alignment: .leading, spacing: 16) {
                FeatureRow(icon: "message.fill", text: "Post thoughts to Slack")
                FeatureRow(icon: "brain.head.profile", text: "AI-powered classification")
                FeatureRow(icon: "folder.fill", text: "Organized in Obsidian vault")
                FeatureRow(icon: "arrow.clockwise", text: "Automatic background processing")
            }
            .padding()
            .background(Color(NSColor.controlBackgroundColor))
            .cornerRadius(12)
            .padding(.horizontal, 40)
            
            Button("Get Started") {
                onContinue()
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
        }
        .padding(40)
    }
}

struct FeatureRow: View {
    let icon: String
    let text: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(.blue)
                .frame(width: 24)
            Text(text)
                .font(.body)
        }
    }
}

struct SetupSlackStepView: View {
    @EnvironmentObject var settings: AppSettings
    let onContinue: () -> Void
    let onSkip: () -> Void
    
    @State private var botToken: String = ""
    @State private var channelID: String = ""
    @State private var userID: String = ""
    @State private var isTesting = false
    @State private var testResult: String = ""
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Configure Slack")
                .font(.title)
                .fontWeight(.bold)
            
            Text("Connect your Slack workspace to capture thoughts from your inbox channel")
                .foregroundColor(.secondary)
            
            Form {
                Section(header: Text("Slack Credentials")) {
                    SecureField("Bot Token (xoxb-...)", text: $botToken)
                        .onAppear {
                            botToken = settings.slackBotToken
                        }
                    
                    TextField("Channel ID (C...)", text: $channelID)
                        .onAppear {
                            channelID = settings.slackChannelID
                        }
                    
                    TextField("User ID (U...)", text: $userID)
                        .onAppear {
                            userID = settings.slackUserID
                        }
                }
                
                Section(header: Text("How to get these")) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("• Bot Token: Create a Slack app at api.slack.com/apps")
                        Text("• Channel ID: Right-click channel → View details → Copy ID")
                        Text("• User ID: Right-click your profile → Copy member ID")
                    }
                    .font(.caption)
                    .foregroundColor(.secondary)
                }
                
                if !testResult.isEmpty {
                    Text(testResult)
                        .foregroundColor(testResult.contains("✅") ? .green : .red)
                        .font(.caption)
                }
            }
            .formStyle(.grouped)
            
            HStack {
                Button("Skip") {
                    onSkip()
                }
                
                Spacer()
                
                Button("Test Connection") {
                    testConnection()
                }
                .disabled(isTesting || botToken.isEmpty)
                
                Button("Continue") {
                    saveAndContinue()
                }
                .buttonStyle(.borderedProminent)
                .disabled(botToken.isEmpty && channelID.isEmpty && userID.isEmpty)
            }
        }
        .padding(40)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    private func testConnection() {
        isTesting = true
        testResult = "Testing..."
        
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
    
    private func saveAndContinue() {
        settings.slackBotToken = botToken
        settings.slackChannelID = channelID
        settings.slackUserID = userID
        settings.saveCredentials()
        // Mark setup as completed if we have credentials
        if !botToken.isEmpty || !channelID.isEmpty || !userID.isEmpty {
            settings.setupCompleted = true
        }
        onContinue()
    }
}

struct SetupLLMStepView: View {
    @EnvironmentObject var settings: AppSettings
    let onContinue: () -> Void
    let onSkip: () -> Void
    
    @State private var providerType: LLMProviderType = .anthropic
    @State private var model: String = ""
    @State private var apiEndpoint: String = ""
    @State private var apiKey: String = ""
    @State private var isTesting = false
    @State private var testResult: String = ""
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Configure LLM")
                .font(.title)
                .fontWeight(.bold)
            
            Text("Choose your AI provider for classifying thoughts")
                .foregroundColor(.secondary)
            
            Form {
                Section(header: Text("Provider")) {
                    Picker("Provider", selection: $providerType) {
                        ForEach(LLMProviderType.allCases, id: \.self) { type in
                            Text(type.displayName).tag(type)
                        }
                    }
                    .onChange(of: providerType) {
                        apiEndpoint = providerType.defaultEndpoint
                        model = ""
                    }
                }
                
                if providerType.requiresAPIKey {
                    Section(header: Text("API Key")) {
                        SecureField("API Key", text: $apiKey)
                    }
                }
                
                if providerType == .ollama || providerType == .lmStudio {
                    Section(header: Text("Local Configuration")) {
                        TextField("API Endpoint", text: $apiEndpoint)
                        TextField("Model", text: $model)
                    }
                }
                
                Section(header: Text("Recommendations")) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("• Cloud: Anthropic Claude or OpenAI GPT-4")
                        Text("• Local: Ollama (free, private)")
                        Text("• For privacy: Use local models")
                    }
                    .font(.caption)
                    .foregroundColor(.secondary)
                }
                
                if !testResult.isEmpty {
                    Text(testResult)
                        .foregroundColor(testResult.contains("✅") ? .green : .red)
                        .font(.caption)
                }
            }
            .formStyle(.grouped)
            
            HStack {
                Button("Skip") {
                    onSkip()
                }
                
                Spacer()
                
                if providerType.requiresAPIKey || !model.isEmpty {
                    Button("Test Connection") {
                        testConnection()
                    }
                    .disabled(isTesting)
                }
                
                Button("Continue") {
                    saveAndContinue()
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(40)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .onAppear {
            providerType = settings.llmProviderType
            apiEndpoint = settings.llmAPIEndpoint.isEmpty ? providerType.defaultEndpoint : settings.llmAPIEndpoint
            apiKey = settings.llmAPIKey
            model = settings.llmModel
        }
    }
    
    private func testConnection() {
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
        
        let result = PythonBridge.shared.executeScript("process_inbox.py", arguments: ["--test-classify", "test"], environment: env, vaultPath: settings.vaultPath)
        
        DispatchQueue.main.async {
            isTesting = false
            switch result {
            case .success(let output):
                if output.contains("destination") || output.contains("✅") {
                    testResult = "✅ Connection successful!"
                } else {
                    testResult = "❌ Connection failed: \(output)"
                }
            case .failure(let error):
                testResult = "❌ Error: \(error.localizedDescription)"
            }
        }
    }
    
    private func saveAndContinue() {
        settings.llmProviderType = providerType
        settings.llmModel = model
        settings.llmAPIEndpoint = apiEndpoint
        settings.llmAPIKey = apiKey
        settings.saveCredentials()
        // Mark setup as completed if we have LLM configured
        if !apiKey.isEmpty || !model.isEmpty || providerType == .ollama || providerType == .lmStudio {
            settings.setupCompleted = true
        }
        onContinue()
    }
}

struct SetupObsidianStepView: View {
    @EnvironmentObject var settings: AppSettings
    let onContinue: () -> Void
    let onSkip: () -> Void
    
    @State private var vaultPath: String = ""
    @State private var isSelectingPath = false
    @State private var validationMessage: String = ""
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Configure Obsidian")
                .font(.title)
                .fontWeight(.bold)
            
            Text("Select your Obsidian vault folder where thoughts will be stored")
                .foregroundColor(.secondary)
            
            Form {
                Section(header: Text("Vault Path")) {
                    HStack {
                        TextField("Vault Path", text: $vaultPath)
                            .disabled(true)
                        
                        Button("Browse...") {
                            isSelectingPath = true
                        }
                    }
                    
                    if !validationMessage.isEmpty {
                        Text(validationMessage)
                            .foregroundColor(validationMessage.contains("✅") ? .green : .red)
                            .font(.caption)
                    }
                }
                
                Section(header: Text("Expected Structure")) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("people/")
                        Text("projects/")
                        Text("ideas/")
                        Text("admin/")
                        Text("daily/")
                        Text("_inbox_log/")
                    }
                    .font(.caption)
                    .foregroundColor(.secondary)
                }
            }
            .formStyle(.grouped)
            
            HStack {
                Button("Skip") {
                    onSkip()
                }
                
                Spacer()
                
                Button("Continue") {
                    saveAndContinue()
                }
                .buttonStyle(.borderedProminent)
                .disabled(vaultPath.isEmpty)
            }
        }
        .padding(40)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .onAppear {
            vaultPath = settings.vaultPath
            validateVaultPath()
        }
        .fileImporter(
            isPresented: $isSelectingPath,
            allowedContentTypes: [.folder],
            allowsMultipleSelection: false
        ) { result in
            switch result {
            case .success(let urls):
                if let url = urls.first {
                    vaultPath = url.path
                    validateVaultPath()
                }
            case .failure:
                break
            }
        }
    }
    
    private func validateVaultPath() {
        guard !vaultPath.isEmpty else {
            validationMessage = ""
            return
        }
        
        let fileManager = FileManager.default
        
        if !fileManager.fileExists(atPath: vaultPath) {
            validationMessage = "❌ Path does not exist"
            return
        }
        
        var isDirectory: ObjCBool = false
        if !fileManager.fileExists(atPath: vaultPath, isDirectory: &isDirectory) || !isDirectory.boolValue {
            validationMessage = "❌ Path is not a directory"
            return
        }
        
        let expectedFolders = ["people", "projects", "ideas", "admin", "daily", "_inbox_log"]
        let missingFolders = expectedFolders.filter { folder in
            let folderPath = (vaultPath as NSString).appendingPathComponent(folder)
            return !fileManager.fileExists(atPath: folderPath)
        }
        
        if missingFolders.isEmpty {
            validationMessage = "✅ Vault path is valid"
        } else {
            validationMessage = "⚠️ Missing folders: \(missingFolders.joined(separator: ", "))"
        }
    }
    
    private func saveAndContinue() {
        settings.vaultPath = vaultPath
        // Mark setup as completed if vault path is set
        if !vaultPath.isEmpty {
            settings.setupCompleted = true
        }
        onContinue()
    }
}

struct SetupCompleteView: View {
    let onFinish: () -> Void
    
    var body: some View {
        VStack(spacing: 30) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 80))
                .foregroundColor(.green)
            
            Text("Setup Complete!")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            Text("You're all set! Start capturing your thoughts.")
                .font(.title3)
                .foregroundColor(.secondary)
            
            VStack(alignment: .leading, spacing: 16) {
                Text("Next steps:")
                    .font(.headline)
                
                VStack(alignment: .leading, spacing: 8) {
                    Text("1. Go to Dashboard and click 'Start'")
                    Text("2. Post a message to your Slack channel")
                    Text("3. Watch it get processed automatically")
                }
                .font(.body)
                .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(NSColor.controlBackgroundColor))
            .cornerRadius(12)
            .padding(.horizontal, 40)
            
            Button("Get Started") {
                onFinish()
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
        }
        .padding(40)
    }
}

#Preview {
    WelcomeView(isPresented: .constant(true))
        .environmentObject(AppSettings())
}
