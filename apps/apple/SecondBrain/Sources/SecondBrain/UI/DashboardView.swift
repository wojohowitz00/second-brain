import SwiftUI

/// Dashboard view showing sync stats, recent syncs, and recent notes.
struct DashboardView: View {
    let database: AppDatabase
    @StateObject private var viewModel: DashboardViewModel
    
    init(database: AppDatabase) {
        self.database = database
        _viewModel = StateObject(wrappedValue: DashboardViewModel(database: database))
    }
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // MARK: - Stats Cards
                statsRow
                
                Divider()
                
                // MARK: - Recent Syncs
                recentSyncsSection
                
                Divider()
                
                // MARK: - Recent Notes
                recentNotesSection
            }
            .padding(24)
        }
        .onAppear {
            viewModel.refresh()
        }
        .onReceive(NotificationCenter.default.publisher(for: .syncCompleted)) { _ in
            viewModel.refresh()
        }
    }
    
    // MARK: - Stats Row
    
    private var statsRow: some View {
        HStack(spacing: 16) {
            StatCard(
                title: "Total Notes",
                value: "\(viewModel.totalNotes)",
                icon: "doc.text.fill",
                color: .blue
            )
            StatCard(
                title: "Today",
                value: "\(viewModel.todayNotes)",
                icon: "calendar",
                color: .green
            )
            StatCard(
                title: "Top Category",
                value: viewModel.topCategory,
                icon: "folder.fill",
                color: .orange
            )
            StatCard(
                title: "Accuracy",
                value: String(format: "%.0f%%", viewModel.accuracy),
                icon: "checkmark.seal.fill",
                color: viewModel.accuracy >= 80 ? .green : .red
            )
        }
    }
    
    // MARK: - Recent Syncs
    
    private var recentSyncsSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Recent Syncs")
                .font(.headline)
            
            if viewModel.recentSyncs.isEmpty {
                Text("No syncs yet. Click \"Sync Now\" from the menu bar.")
                    .foregroundStyle(.secondary)
                    .padding(.vertical, 8)
            } else {
                ForEach(viewModel.recentSyncs, id: \.id) { event in
                    HStack {
                        Image(systemName: event.status == "success" ? "checkmark.circle.fill" : "xmark.circle.fill")
                            .foregroundStyle(event.status == "success" ? .green : .red)
                        
                        Text(formattedDate(event.timestamp))
                            .font(.system(.body, design: .monospaced))
                        
                        Spacer()
                        
                        Text("\(event.messageCount) note\(event.messageCount == 1 ? "" : "s")")
                            .foregroundStyle(.secondary)
                    }
                    .padding(.vertical, 4)
                }
            }
        }
    }
    
    // MARK: - Recent Notes
    
    private var recentNotesSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Recent Notes")
                .font(.headline)
            
            if viewModel.recentNotes.isEmpty {
                Text("No notes yet.")
                    .foregroundStyle(.secondary)
                    .padding(.vertical, 8)
            } else {
                ForEach(viewModel.recentNotes, id: \.id) { note in
                    HStack {
                        CategoryPill(category: note.correctedCategory ?? note.classifiedCategory)
                        
                        VStack(alignment: .leading) {
                            Text(note.classifiedTitle ?? note.classifiedFilename)
                                .font(.body)
                                .lineLimit(1)
                            Text(note.destinationPath)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        
                        Spacer()
                        
                        Text(formattedDate(note.createdAt))
                            .font(.caption)
                            .foregroundStyle(.tertiary)
                    }
                    .padding(.vertical, 4)
                }
            }
        }
    }
    
    // MARK: - Helpers
    
    private func formattedDate(_ isoString: String) -> String {
        let formatter = ISO8601DateFormatter()
        guard let date = formatter.date(from: isoString) else { return isoString }
        let display = DateFormatter()
        display.dateStyle = .short
        display.timeStyle = .short
        return display.string(from: date)
    }
}

// MARK: - Stat Card

struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .foregroundStyle(color)
                Spacer()
            }
            Text(value)
                .font(.title2.bold())
            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.quaternary.opacity(0.5))
        .clipShape(RoundedRectangle(cornerRadius: 10))
    }
}

// MARK: - Category Pill

struct CategoryPill: View {
    let category: String
    
    private var color: Color {
        switch category.lowercased() {
        case "projects": return .blue
        case "areas":    return .green
        case "resources": return .orange
        case "archives": return .gray
        default:         return .secondary
        }
    }
    
    var body: some View {
        Text(category)
            .font(.caption.bold())
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(color.opacity(0.2))
            .foregroundStyle(color)
            .clipShape(Capsule())
    }
}

// MARK: - Notification

extension Notification.Name {
    static let syncCompleted = Notification.Name("syncCompleted")
}
