//
//  VaultBrowserView.swift
//  SecondBrain
//

import SwiftUI

struct VaultBrowserView: View {
    @EnvironmentObject var settings: AppSettings
    @State private var selectedFolder: VaultFolder = .people
    @State private var files: [VaultFile] = []
    @State private var selectedFile: VaultFile?
    @State private var isLoading = false
    
    var body: some View {
        HSplitView {
            // Folder List
            List(VaultFolder.allCases, selection: $selectedFolder) { folder in
                Label(folder.displayName, systemImage: folder.icon)
                    .tag(folder)
            }
            .frame(minWidth: 200)
            .onChange(of: selectedFolder) {
                loadFiles()
            }
            
            // File List
            List(files, selection: $selectedFile) { file in
                FileRow(file: file)
                    .tag(file)
            }
            .frame(minWidth: 250)
            
            // File Content
            if let file = selectedFile {
                FileViewerView(file: file)
            } else {
                Text("Select a file to view")
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .onAppear {
            loadFiles()
        }
    }
    
    private func loadFiles() {
        isLoading = true
        
        let folderPath = URL(fileURLWithPath: settings.vaultPath)
            .appendingPathComponent(selectedFolder.rawValue)
        
        guard let fileURLs = try? FileManager.default.contentsOfDirectory(
            at: folderPath,
            includingPropertiesForKeys: [.isRegularFileKey],
            options: [.skipsHiddenFiles]
        ) else {
            files = []
            isLoading = false
            return
        }
        
        files = fileURLs
            .filter { $0.pathExtension == "md" }
            .map { VaultFile(name: $0.lastPathComponent, path: $0.path, folder: selectedFolder) }
            .sorted { $0.name < $1.name }
        
        isLoading = false
    }
}

enum VaultFolder: String, CaseIterable, Identifiable {
    case people = "people"
    case projects = "projects"
    case ideas = "ideas"
    case admin = "admin"
    case daily = "daily"
    
    var id: String { rawValue }
    
    var displayName: String {
        rawValue.capitalized
    }
    
    var icon: String {
        switch self {
        case .people: return "person.fill"
        case .projects: return "folder.fill"
        case .ideas: return "lightbulb.fill"
        case .admin: return "checkmark.circle.fill"
        case .daily: return "calendar"
        }
    }
}

struct VaultFile: Identifiable, Hashable {
    let id = UUID()
    let name: String
    let path: String
    let folder: VaultFolder
}

struct FileRow: View {
    let file: VaultFile
    
    var body: some View {
        Text(file.name)
            .lineLimit(1)
    }
}

struct FileViewerView: View {
    let file: VaultFile
    @State private var content: String = ""
    @State private var isLoading = true
    
    var body: some View {
        ScrollView {
            if isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                Text(content)
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .onAppear {
            loadFileContent()
        }
    }
    
    private func loadFileContent() {
        isLoading = true
        
        if let data = try? Data(contentsOf: URL(fileURLWithPath: file.path)),
           let text = String(data: data, encoding: .utf8) {
            content = text
        } else {
            content = "Error loading file"
        }
        
        isLoading = false
    }
}

#Preview {
    VaultBrowserView()
        .environmentObject(AppSettings())
}
