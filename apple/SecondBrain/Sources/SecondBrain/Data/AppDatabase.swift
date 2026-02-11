import Foundation
import GRDB

/// Manages the SQLite database for the Second Brain app.
public class AppDatabase {
    /// The database connection. DatabasePool for production, DatabaseQueue for testing.
    public let dbWriter: any DatabaseWriter
    
    /// Creates an AppDatabase with the given DatabaseWriter.
    public init(_ dbWriter: any DatabaseWriter) throws {
        self.dbWriter = dbWriter
        try migrator.migrate(dbWriter)
    }
    
    /// Creates an AppDatabase at the default location.
    public static func makeDefault() throws -> AppDatabase {
        let appSupport = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        let dbDir = appSupport.appendingPathComponent("SecondBrain")
        try FileManager.default.createDirectory(at: dbDir, withIntermediateDirectories: true)
        let dbPath = dbDir.appendingPathComponent("secondbrain.sqlite").path
        let dbPool = try DatabasePool(path: dbPath)
        return try AppDatabase(dbPool)
    }
    
    /// Creates an in-memory AppDatabase for testing.
    public static func makeInMemory() throws -> AppDatabase {
        let dbQueue = try DatabaseQueue()
        return try AppDatabase(dbQueue)
    }
    
    // MARK: - Migrations
    
    private var migrator: DatabaseMigrator {
        var migrator = DatabaseMigrator()
        
        // v1: Core tables
        migrator.registerMigration("v1") { db in
            try db.create(table: "sync_event") { t in
                t.autoIncrementedPrimaryKey("id")
                t.column("timestamp", .text).notNull().defaults(sql: "(datetime('now'))")
                t.column("messageCount", .integer).notNull()
                t.column("status", .text).notNull().defaults(to: "success")
            }
            
            try db.create(table: "note") { t in
                t.autoIncrementedPrimaryKey("id")
                t.belongsTo("syncEvent", inTable: "sync_event").notNull()
                t.column("slackTs", .text).notNull().unique()
                t.column("originalText", .text).notNull()
                t.column("classifiedCategory", .text).notNull()
                t.column("classifiedName", .text)
                t.column("classifiedFilename", .text).notNull()
                t.column("classifiedTitle", .text)
                t.column("destinationPath", .text).notNull()
                t.column("createdAt", .text).notNull().defaults(sql: "(datetime('now'))")
                t.column("correctedCategory", .text)
                t.column("correctedAt", .text)
            }
        }
        
        // v2: FTS5 search index
        migrator.registerMigration("v2") { db in
            try db.create(virtualTable: "note_fts", using: FTS5()) { t in
                t.synchronize(withTable: "note")
                t.column("originalText")
                t.column("classifiedTitle")
                t.column("classifiedName")
            }
        }
        
        return migrator
    }
    
    // MARK: - Convenience Queries
    
    /// Insert a sync event and return it with its assigned ID.
    public func insertSyncEvent(_ event: inout SyncEvent) throws {
        try dbWriter.write { db in
            try event.insert(db)
        }
    }
    
    /// Insert a note record.
    public func insertNote(_ note: inout Note) throws {
        try dbWriter.write { db in
            try note.insert(db)
        }
    }
    
    /// Fetch recent sync events.
    public func recentSyncEvents(limit: Int = 20) throws -> [SyncEvent] {
        try dbWriter.read { db in
            try SyncEvent.order(Column("timestamp").desc).limit(limit).fetchAll(db)
        }
    }
    
    /// Fetch all notes for a given sync event.
    public func notes(forSyncEvent id: Int64) throws -> [Note] {
        try dbWriter.read { db in
            try Note.filter(Column("syncEventId") == id).fetchAll(db)
        }
    }
    
    /// Full-text search across notes.
    public func searchNotes(query: String, limit: Int = 50) throws -> [Note] {
        try dbWriter.read { db in
            let pattern = FTS5Pattern(matchingAnyTokenIn: query)
            guard let pattern = pattern else { return [] }
            let sql = """
                SELECT note.*
                FROM note
                JOIN note_fts ON note_fts.rowid = note.id
                WHERE note_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """
            return try Note.fetchAll(db, sql: sql, arguments: [pattern.rawPattern, limit])
        }
    }
    
    /// Get note count grouped by category.
    public func noteStats() throws -> [String: Int] {
        try dbWriter.read { db in
            let rows = try Row.fetchAll(db, sql: """
                SELECT classifiedCategory, COUNT(*) as count
                FROM note
                GROUP BY classifiedCategory
                """)
            var stats: [String: Int] = [:]
            for row in rows {
                stats[row["classifiedCategory"]] = row["count"]
            }
            return stats
        }
    }
    
    /// Fetch uncorrected notes (those that haven't been manually re-classified).
    public func uncorrectedNotes(limit: Int = 50) throws -> [Note] {
        try dbWriter.read { db in
            try Note.filter(Column("correctedCategory") == nil)
                .order(Column("createdAt").desc)
                .limit(limit)
                .fetchAll(db)
        }
    }
}
