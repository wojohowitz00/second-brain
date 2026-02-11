//
//  ObsidianSettingsView.swift
//  SecondBrain
//

import SwiftUI
import UniformTypeIdentifiers

struct ObsidianSettingsView: View {
    @EnvironmentObject var settings: AppSettings
    @State private var vaultPath: String = ""
    @State private var isSelectingPath = false
    @State private var validationMessage: String = ""
    
    var body: some View {
        Form {
            Section(header: Text("Obsidian Vault Path")) {
                HStack {
                    TextField("Vault Path", text: $vaultPath)
                        .disabled(true)
                    
                    Button("Browse...") {
                        selectVaultPath()
                    }
                }
                
                if !validationMessage.isEmpty {
                    Text(validationMessage)
                        .foregroundColor(validationMessage.contains("✅") ? .green : .red)
                        .font(.caption)
                }
            }
            
            Section(header: Text("Vault Structure")) {
                if FileManager.default.fileExists(atPath: vaultPath) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Expected folders:")
                            .font(.headline)
                        
                        ForEach(["people", "projects", "ideas", "admin", "daily", "_inbox_log"], id: \.self) { folder in
                            HStack {
                                let folderPath = (vaultPath as NSString).appendingPathComponent(folder)
                                Image(systemName: FileManager.default.fileExists(atPath: folderPath) ? "checkmark.circle.fill" : "xmark.circle.fill")
                                    .foregroundColor(FileManager.default.fileExists(atPath: folderPath) ? .green : .red)
                                Text(folder)
                            }
                        }
                    }
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
            case .failure(let error):
                validationMessage = "❌ Error selecting path: \(error.localizedDescription)"
            }
        }
    }
    
    private func selectVaultPath() {
        isSelectingPath = true
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
        
        // Check for expected folders
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
    
    private func saveSettings() {
        settings.vaultPath = vaultPath
        validateVaultPath()
    }
}

#Preview {
    ObsidianSettingsView()
        .environmentObject(AppSettings())
}
