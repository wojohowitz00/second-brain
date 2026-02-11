//
//  ContentView.swift
//  SecondBrain
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var settings: AppSettings
    @EnvironmentObject var backgroundService: BackgroundService
    @Binding var showWelcome: Bool
    @State private var selectedView: NavigationItem = .dashboard
    
    init(showWelcome: Binding<Bool> = .constant(false)) {
        _showWelcome = showWelcome
    }
    
    var body: some View {
        NavigationSplitView {
            SidebarView(selectedView: $selectedView)
        } detail: {
            DetailView(selectedView: selectedView)
        }
        .sheet(isPresented: $showWelcome) {
            WelcomeView(isPresented: $showWelcome)
                .environmentObject(settings)
        }
        .onAppear {
            if !settings.setupCompleted {
                showWelcome = true
            }
            // Reload credentials from Keychain
            settings.loadCredentials()
            // Update background service vault path and settings
            backgroundService.vaultPath = settings.vaultPath
            backgroundService.settings = settings
        }
        .onChange(of: settings.vaultPath) {
            backgroundService.vaultPath = settings.vaultPath
            backgroundService.settings = settings
        }
        .onChange(of: settings.slackBotToken) {
            backgroundService.settings = settings
        }
        .onChange(of: settings.llmAPIKey) {
            backgroundService.settings = settings
        }
        .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("ShowSetupWizard"))) { _ in
            showWelcome = true
        }
        .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("ShowHelp"))) { _ in
            selectedView = .help
        }
    }
}

enum NavigationItem: String, CaseIterable, Identifiable {
    case dashboard = "Dashboard"
    case messages = "Messages"
    case vault = "Vault"
    case logs = "Logs"
    case settings = "Settings"
    case help = "Help"
    
    var id: String { rawValue }
    
    var icon: String {
        switch self {
        case .dashboard: return "chart.bar.fill"
        case .messages: return "message.fill"
        case .vault: return "folder.fill"
        case .logs: return "doc.text.fill"
        case .settings: return "gearshape.fill"
        case .help: return "questionmark.circle.fill"
        }
    }
}

struct SidebarView: View {
    @Binding var selectedView: NavigationItem
    
    var body: some View {
        List(NavigationItem.allCases, selection: $selectedView) { item in
            Label(item.rawValue, systemImage: item.icon)
                .tag(item)
        }
        .navigationTitle("Second Brain")
    }
}

struct DetailView: View {
    let selectedView: NavigationItem
    
    var body: some View {
        Group {
            switch selectedView {
            case .dashboard:
                DashboardView()
            case .messages:
                MessagesView()
            case .vault:
                VaultBrowserView()
            case .logs:
                LogsView()
            case .settings:
                SettingsView()
            case .help:
                HelpView()
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

#Preview {
    ContentView(showWelcome: .constant(false))
        .environmentObject(AppSettings())
        .environmentObject(BackgroundService())
}
