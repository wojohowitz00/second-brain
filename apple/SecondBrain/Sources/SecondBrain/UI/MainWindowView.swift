import SwiftUI

/// Sidebar navigation items for the main window.
enum SidebarItem: String, CaseIterable, Identifiable {
    case dashboard = "Dashboard"
    case search = "Search"
    case settings = "Settings"
    
    var id: String { rawValue }
    
    var icon: String {
        switch self {
        case .dashboard: return "chart.bar.fill"
        case .search:    return "magnifyingglass"
        case .settings:  return "gear"
        }
    }
}

/// The main application window with sidebar navigation.
struct MainWindowView: View {
    let database: AppDatabase
    @State private var selectedItem: SidebarItem = .dashboard
    
    var body: some View {
        NavigationSplitView {
            List(SidebarItem.allCases, selection: $selectedItem) { item in
                Label(item.rawValue, systemImage: item.icon)
                    .tag(item)
            }
            .navigationSplitViewColumnWidth(min: 160, ideal: 180, max: 220)
            .listStyle(.sidebar)
        } detail: {
            switch selectedItem {
            case .dashboard:
                DashboardView(database: database)
            case .search:
                SearchPlaceholderView()
            case .settings:
                SettingsView()
            }
        }
        .frame(minWidth: 700, minHeight: 500)
        .navigationTitle("Second Brain")
    }
}

/// Placeholder for the Search view (Phase 13.4).
struct SearchPlaceholderView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 48))
                .foregroundStyle(.secondary)
            Text("Search")
                .font(.title2.bold())
            Text("Full-text search across your notes.\nComing in Phase 13.4.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
