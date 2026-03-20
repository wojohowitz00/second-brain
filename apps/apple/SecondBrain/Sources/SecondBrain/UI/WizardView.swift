import SwiftUI

/// First-run setup wizard that guides new users through configuration.
struct WizardView: View {
    @StateObject private var viewModel = SettingsViewModel()
    @State private var currentStep = 0
    @State private var ollamaReachable = false
    @State private var isCheckingOllama = true
    var onComplete: () -> Void
    
    private let totalSteps = 5
    
    var body: some View {
        VStack(spacing: 0) {
            // Progress indicator
            progressBar
            
            // Step content
            TabView(selection: $currentStep) {
                ollamaStep.tag(0)
                modelStep.tag(1)
                vaultStep.tag(2)
                slackStep.tag(3)
                doneStep.tag(4)
            }
            .tabViewStyle(.automatic)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            
            // Navigation buttons
            navigationBar
        }
        .frame(width: 500, height: 420)
        .padding()
    }
    
    // MARK: - Progress Bar
    
    private var progressBar: some View {
        VStack(spacing: 8) {
            HStack {
                Text("Setup Wizard")
                    .font(.title2.bold())
                Spacer()
                Text("Step \(currentStep + 1) of \(totalSteps)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            
            ProgressView(value: Double(currentStep + 1), total: Double(totalSteps))
                .tint(.blue)
        }
        .padding(.bottom, 16)
    }
    
    // MARK: - Step 1: Ollama Check
    
    private var ollamaStep: some View {
        VStack(spacing: 16) {
            Image(systemName: "brain.head.profile")
                .font(.system(size: 48))
                .foregroundStyle(.blue)
            
            Text("Ollama Connection")
                .font(.title3.bold())
            
            Text("Second Brain uses Ollama for AI-powered note classification.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
            
            if isCheckingOllama {
                ProgressView("Checking connection...")
            } else {
                HStack {
                    Image(systemName: ollamaReachable ? "checkmark.circle.fill" : "xmark.circle.fill")
                        .foregroundStyle(ollamaReachable ? .green : .red)
                    Text(ollamaReachable ? "Ollama is running" : "Ollama not detected")
                }
                .font(.headline)
                
                if !ollamaReachable {
                    Text("Please install and start Ollama from ollama.ai")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    
                    Button("Retry") {
                        checkOllama()
                    }
                }
            }
        }
        .onAppear { checkOllama() }
    }
    
    // MARK: - Step 2: Model Selection
    
    private var modelStep: some View {
        VStack(spacing: 16) {
            Image(systemName: "cpu")
                .font(.system(size: 48))
                .foregroundStyle(.purple)
            
            Text("Select AI Model")
                .font(.title3.bold())
            
            Text("Choose which Ollama model to use for classification.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
            
            if viewModel.isLoadingModels {
                ProgressView("Loading models...")
            } else if viewModel.availableModels.isEmpty {
                Text("No models found. Install one via: ollama pull llama3")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            } else {
                Picker("Model", selection: $viewModel.selectedModel) {
                    ForEach(viewModel.availableModels, id: \.self) { model in
                        Text(model).tag(model)
                    }
                }
                .pickerStyle(.menu)
                .frame(width: 250)
            }
        }
        .task { await viewModel.fetchModels() }
    }
    
    // MARK: - Step 3: Vault Selection
    
    private var vaultStep: some View {
        VStack(spacing: 16) {
            Image(systemName: "folder.fill")
                .font(.system(size: 48))
                .foregroundStyle(.orange)
            
            Text("Obsidian Vault")
                .font(.title3.bold())
            
            Text("Select the root folder of your Obsidian vault.\nNotes will be organized into PARA folders here.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
            
            HStack {
                Text(viewModel.vaultPath.isEmpty ? "No vault selected" : viewModel.vaultPath)
                    .lineLimit(1)
                    .truncationMode(.middle)
                    .foregroundStyle(viewModel.vaultPath.isEmpty ? .secondary : .primary)
                    .frame(maxWidth: 300)
                
                Button("Browse...") {
                    viewModel.selectVault()
                }
            }
        }
    }
    
    // MARK: - Step 4: Slack Configuration
    
    private var slackStep: some View {
        VStack(spacing: 16) {
            Image(systemName: "message.fill")
                .font(.system(size: 48))
                .foregroundStyle(.green)
            
            Text("Slack Integration")
                .font(.title3.bold())
            
            Text("Enter your Slack credentials to sync messages.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
            
            VStack(alignment: .leading, spacing: 8) {
                Text("App-Level Token")
                    .font(.caption.bold())
                SecureField("xapp-...", text: $viewModel.slackToken)
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 350)
                
                Text("Channel ID")
                    .font(.caption.bold())
                TextField("C0123456789", text: $viewModel.slackChannelID)
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 350)
            }
        }
    }
    
    // MARK: - Step 5: Done
    
    private var doneStep: some View {
        VStack(spacing: 16) {
            Image(systemName: "checkmark.seal.fill")
                .font(.system(size: 48))
                .foregroundStyle(.green)
            
            Text("You're All Set!")
                .font(.title3.bold())
            
            Text("Second Brain is ready to organize your notes.")
                .foregroundStyle(.secondary)
            
            VStack(alignment: .leading, spacing: 6) {
                configRow("Ollama", value: ollamaReachable ? "Connected" : "Not connected")
                configRow("Model", value: viewModel.selectedModel.isEmpty ? "Not selected" : viewModel.selectedModel)
                configRow("Vault", value: viewModel.vaultPath.isEmpty ? "Not set" : viewModel.vaultPath)
                configRow("Slack", value: viewModel.slackToken.isEmpty ? "Not configured" : "Configured")
            }
            .padding()
            .background(.quaternary.opacity(0.5))
            .clipShape(RoundedRectangle(cornerRadius: 8))
            
            Button("Get Started") {
                onComplete()
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
        }
    }
    
    private func configRow(_ label: String, value: String) -> some View {
        HStack {
            Text(label)
                .font(.caption.bold())
                .frame(width: 60, alignment: .leading)
            Text(value)
                .font(.caption)
                .foregroundStyle(.secondary)
                .lineLimit(1)
                .truncationMode(.middle)
        }
    }
    
    // MARK: - Navigation Bar
    
    private var navigationBar: some View {
        HStack {
            if currentStep > 0 && currentStep < totalSteps - 1 {
                Button("Back") {
                    withAnimation { currentStep -= 1 }
                }
            }
            
            Spacer()
            
            if currentStep < totalSteps - 1 {
                Button("Next") {
                    withAnimation { currentStep += 1 }
                }
                .buttonStyle(.borderedProminent)
                .disabled(!canAdvance)
            }
        }
        .padding(.top, 16)
    }
    
    private var canAdvance: Bool {
        switch currentStep {
        case 2: return !viewModel.vaultPath.isEmpty
        default: return true
        }
    }
    
    // MARK: - Helpers
    
    private func checkOllama() {
        isCheckingOllama = true
        Task {
            let client = OllamaClient()
            let reachable = await client.isReachable()
            await MainActor.run {
                ollamaReachable = reachable
                isCheckingOllama = false
            }
        }
    }
}
