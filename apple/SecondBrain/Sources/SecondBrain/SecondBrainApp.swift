import SwiftUI

@main
struct SecondBrainApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        Window("Second Brain", id: "main") {
            if let db = appDelegate.database {
                MainWindowView(database: db)
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
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Initialize database
        do {
            database = try AppDatabase.makeDefault()
        } catch {
            print("Failed to initialize database: \(error)")
        }
        
        // Initialize menu bar with database
        menuBarManager = MenuBarManager(database: database)
    }
}
