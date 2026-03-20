import SwiftUI

struct SettingsView: View {
    @StateObject private var viewModel = SettingsViewModel()
    
    var body: some View {
        Form {
            Section(header: Text("Obsidian Vault")) {
                HStack {
                    TextField("Vault Path", text: $viewModel.vaultPath)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .disabled(true) // Read-only, use browse button
                    
                    Button("Browse...") {
                        viewModel.selectVault()
                    }
                }
                Text("Select the root folder of your Obsidian vault.")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Section(header: Text("Ollama Model")) {
                if viewModel.isLoadingModels {
                    ProgressView("Loading models...")
                        .controlSize(.small)
                } else if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                    Button("Retry") {
                        Task { await viewModel.fetchModels() }
                    }
                } else {
                    Picker("Model", selection: $viewModel.selectedModel) {
                        if viewModel.availableModels.isEmpty {
                            Text("No models found").tag("")
                        } else {
                            ForEach(viewModel.availableModels, id: \.self) { model in
                                Text(model).tag(model)
                            }
                        }
                    }
                }
            }
            
            Section(header: Text("Slack Configuration")) {
                SecureField("App-Level Token (xapp-...)", text: $viewModel.slackToken)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                
                TextField("Channel ID", text: $viewModel.slackChannelID)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
            }
            
            Section {
                Toggle("Start at Login", isOn: $viewModel.isStartAtLoginEnabled)
            }
        }
        .padding()
        .frame(width: 450, height: 400)
        .task {
            await viewModel.fetchModels()
            viewModel.checkLaunchAgentStatus()
        }
    }
}
