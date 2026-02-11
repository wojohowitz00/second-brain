//
//  SecondBrainApp.swift
//  SecondBrain
//

import SwiftUI

@main
struct SecondBrainApp: App {
    @StateObject private var settings = AppSettings()
    @StateObject private var backgroundService = BackgroundService()
    @State private var showWelcome = false
    
    var body: some Scene {
        WindowGroup {
            ContentView(showWelcome: $showWelcome)
                .environmentObject(settings)
                .environmentObject(backgroundService)
                .frame(minWidth: 1000, minHeight: 600)
                .onAppear {
                    backgroundService.vaultPath = settings.vaultPath
                    backgroundService.settings = settings
                }
                .onChange(of: settings.vaultPath) {
                    backgroundService.vaultPath = settings.vaultPath
                }
        }
        .commands {
            CommandGroup(replacing: .newItem) {}
            
            CommandGroup(after: .help) {
                Button("Show Setup Wizard") {
                    NotificationCenter.default.post(name: NSNotification.Name("ShowSetupWizard"), object: nil)
                }
                
                Button("Help & Instructions") {
                    NotificationCenter.default.post(name: NSNotification.Name("ShowHelp"), object: nil)
                }
            }
        }
    }
}
