import SwiftUI

@main
struct SecondBrainApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        Window("Second Brain", id: "main") {
            if let db = appDelegate.database {
                if appDelegate.setupComplete {
                    MainWindowView(database: db)
                } else {
                    WizardView {
                        appDelegate.setupComplete = true
                    }
                }
            } else {
                ProgressView("Loading...")
                    .frame(width: 300, height: 200)
            }
        }
        .defaultSize(width: 800, height: 600)
        
        Settings {
            SettingsView()
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate, ObservableObject {
    var menuBarManager: MenuBarManager?
    var database: AppDatabase?
    @Published var setupComplete: Bool = false
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Initialize database
        do {
            database = try AppDatabase.makeDefault()
        } catch {
            print("Failed to initialize database: \(error)")
        }
        
        // Check if setup has been completed (vault path exists)
        let vaultPath = UserDefaults.standard.string(forKey: "vaultPath") ?? ""
        setupComplete = !vaultPath.isEmpty
        
        // Initialize menu bar with database
        menuBarManager = MenuBarManager(database: database)
    }
}
