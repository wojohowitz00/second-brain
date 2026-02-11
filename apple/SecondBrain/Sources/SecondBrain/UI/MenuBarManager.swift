import AppKit
import SwiftUI

class MenuBarManager: NSObject {
    private var statusItem: NSStatusItem
    private let ollamaClient = OllamaClient()
    
    override init() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        super.init()
        setupMenu()
        checkStatus()
    }
    
    private func setupMenu() {
        if let button = statusItem.button {
            button.image = NSImage(systemSymbolName: "brain.head.profile", accessibilityDescription: "Second Brain")
        }
        
        let menu = NSMenu()
        
        let statusMenuItem = NSMenuItem(title: "Status: Checking...", action: nil, keyEquivalent: "")
        statusMenuItem.tag = 1 // Tag to find it later
        menu.addItem(statusMenuItem)
        
        menu.addItem(NSMenuItem.separator())
        
        let syncItem = NSMenuItem(title: "Sync Now", action: #selector(syncNow), keyEquivalent: "s")
        syncItem.target = self
        menu.addItem(syncItem)
        
        menu.addItem(NSMenuItem.separator())
        
        let quitItem = NSMenuItem(title: "Quit", action: #selector(quit), keyEquivalent: "q")
        quitItem.target = self
        menu.addItem(quitItem)
        
        menu.addItem(NSMenuItem.separator())
        
        let settingsItem = NSMenuItem(title: "Settings...", action: #selector(openSettings), keyEquivalent: ",")
        settingsItem.target = self
        menu.addItem(settingsItem)
        
        statusItem.menu = menu
    }
    
    @objc func openSettings() {
        NSApp.sendAction(Selector(("showSettingsWindow:")), to: nil, from: nil)
    }

    @objc func syncNow() {
        print("Sync triggered")
        
        let token = UserDefaults.standard.string(forKey: "slackToken") ?? ""
        let channel = UserDefaults.standard.string(forKey: "slackChannelID") ?? ""
        let vaultPath = UserDefaults.standard.string(forKey: "vaultPath") ?? ""
        let model = UserDefaults.standard.string(forKey: "selectedModel") ?? "llama3"
        
        guard !token.isEmpty, !channel.isEmpty, !vaultPath.isEmpty else {
            print("Missing configuration")
            return
        }
        
        Task {
            let processor = NoteProcessor()
            do {
                let count = try await processor.processInbox(token: token, channelID: channel, vaultPath: vaultPath, model: model)
                print("Processed \(count) messages")
                await MainActor.run {
                    // Could update status item title briefly to show success
                }
            } catch {
                print("Error processing inbox: \(error)")
            }
        }
    }
    
    @objc func quit() {
        NSApplication.shared.terminate(nil)
    }
    
    private func checkStatus() {
        Task {
            let isConnected = await ollamaClient.isReachable()
            await MainActor.run {
                if let menu = statusItem.menu, let statusItem = menu.item(withTag: 1) {
                    statusItem.title = isConnected ? "Status: Connected" : "Status: Disconnected"
                }
            }
        }
    }
}
