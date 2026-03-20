//
//  SettingsView.swift
//  SecondBrain
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var settings: AppSettings
    @State private var showWelcome = false
    
    var body: some View {
        VStack(spacing: 0) {
            TabView {
                SlackSettingsView()
                    .tabItem {
                        Label("Slack", systemImage: "message.fill")
                    }
                
                LLMSettingsView()
                    .tabItem {
                        Label("LLM", systemImage: "brain.head.profile")
                    }
                
                ObsidianSettingsView()
                    .tabItem {
                        Label("Obsidian", systemImage: "folder.fill")
                    }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            
            Divider()
            
            HStack {
                Button("Run Setup Wizard") {
                    showWelcome = true
                }
                
                Spacer()
                
                Button("Help & Instructions") {
                    NotificationCenter.default.post(name: NSNotification.Name("ShowHelp"), object: nil)
                }
            }
            .padding()
        }
        .sheet(isPresented: $showWelcome) {
            WelcomeView(isPresented: $showWelcome)
                .environmentObject(settings)
        }
    }
}

#Preview {
    SettingsView()
        .environmentObject(AppSettings())
}
