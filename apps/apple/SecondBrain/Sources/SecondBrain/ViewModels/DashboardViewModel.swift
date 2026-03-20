import Foundation
import GRDB

/// ViewModel for the Dashboard, loading data from AppDatabase.
@MainActor
class DashboardViewModel: ObservableObject {
    private let database: AppDatabase
    
    @Published var totalNotes: Int = 0
    @Published var todayNotes: Int = 0
    @Published var topCategory: String = "—"
    @Published var accuracy: Double = 100.0
    @Published var recentSyncs: [SyncEvent] = []
    @Published var recentNotes: [Note] = []
    
    init(database: AppDatabase) {
        self.database = database
    }
    
    func refresh() {
        do {
            // Recent syncs
            recentSyncs = try database.recentSyncEvents(limit: 10)
            
            // Recent notes
            recentNotes = try database.dbWriter.read { db in
                try Note.order(Column("createdAt").desc).limit(20).fetchAll(db)
            }
            
            // Stats
            let stats = try database.noteStats()
            totalNotes = stats.values.reduce(0, +)
            topCategory = stats.max(by: { $0.value < $1.value })?.key ?? "—"
            
            // Today's notes
            let todayString = ISO8601DateFormatter().string(from: Calendar.current.startOfDay(for: Date()))
            todayNotes = try database.dbWriter.read { db in
                try Note.filter(Column("createdAt") >= todayString).fetchCount(db)
            }
            
            // Accuracy: % of notes that have NOT been corrected
            let totalCount = totalNotes
            let correctedCount = try database.dbWriter.read { db in
                try Note.filter(Column("correctedCategory") != nil).fetchCount(db)
            }
            accuracy = totalCount > 0 ? Double(totalCount - correctedCount) / Double(totalCount) * 100.0 : 100.0
            
        } catch {
            print("Dashboard refresh error: \(error)")
        }
    }
}
