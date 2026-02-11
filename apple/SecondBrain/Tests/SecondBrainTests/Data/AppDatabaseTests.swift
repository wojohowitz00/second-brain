import XCTest
import GRDB
@testable import SecondBrain

final class AppDatabaseTests: XCTestCase {
    var db: AppDatabase!
    
    override func setUp() {
        super.setUp()
        db = try! AppDatabase.makeInMemory()
    }
    
    // MARK: - Migration Tests
    
    func testMigration_CreatesTablesSuccessfully() throws {
        let tables = try db.dbWriter.read { db in
            try String.fetchAll(db, sql: "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        }
        XCTAssertTrue(tables.contains("sync_event"))
        XCTAssertTrue(tables.contains("note"))
        XCTAssertTrue(tables.contains("note_fts"))
    }
    
    // MARK: - SyncEvent Tests
    
    func testInsertSyncEvent() throws {
        var event = SyncEvent(messageCount: 5, status: "success")
        try db.insertSyncEvent(&event)
        
        XCTAssertNotNil(event.id)
        
        let fetched = try db.recentSyncEvents(limit: 1)
        XCTAssertEqual(fetched.count, 1)
        XCTAssertEqual(fetched.first?.messageCount, 5)
        XCTAssertEqual(fetched.first?.status, "success")
    }
    
    // MARK: - Note Tests
    
    func testInsertNote() throws {
        // First create a sync event
        var event = SyncEvent(messageCount: 1)
        try db.insertSyncEvent(&event)
        
        var note = Note(
            syncEventId: event.id!,
            slackTs: "1234567890.123456",
            originalText: "Launch the MVP by March",
            classifiedCategory: "Projects",
            classifiedName: "MVP Launch",
            classifiedFilename: "mvp_launch.md",
            classifiedTitle: "MVP Launch Plan",
            destinationPath: "Projects/mvp_launch.md"
        )
        try db.insertNote(&note)
        
        XCTAssertNotNil(note.id)
        
        let fetched = try db.notes(forSyncEvent: event.id!)
        XCTAssertEqual(fetched.count, 1)
        XCTAssertEqual(fetched.first?.classifiedCategory, "Projects")
        XCTAssertEqual(fetched.first?.slackTs, "1234567890.123456")
    }
    
    // MARK: - FTS5 Search Tests
    
    func testSearchNotes_FTS5() throws {
        var event = SyncEvent(messageCount: 2)
        try db.insertSyncEvent(&event)
        
        var note1 = Note(
            syncEventId: event.id!,
            slackTs: "1000.001",
            originalText: "Machine learning research paper on transformers",
            classifiedCategory: "Resources",
            classifiedFilename: "ml_transformers.md",
            classifiedTitle: "ML Transformers",
            destinationPath: "Resources/ml_transformers.md"
        )
        try db.insertNote(&note1)
        
        var note2 = Note(
            syncEventId: event.id!,
            slackTs: "1000.002",
            originalText: "Grocery list for the week",
            classifiedCategory: "Areas",
            classifiedFilename: "grocery_list.md",
            classifiedTitle: "Weekly Groceries",
            destinationPath: "Areas/grocery_list.md"
        )
        try db.insertNote(&note2)
        
        let results = try db.searchNotes(query: "machine learning")
        XCTAssertEqual(results.count, 1)
        XCTAssertEqual(results.first?.classifiedTitle, "ML Transformers")
    }
    
    func testSearchNotes_NoResults() throws {
        var event = SyncEvent(messageCount: 1)
        try db.insertSyncEvent(&event)
        
        var note = Note(
            syncEventId: event.id!,
            slackTs: "2000.001",
            originalText: "Something about cooking",
            classifiedCategory: "Areas",
            classifiedFilename: "cooking.md",
            destinationPath: "Areas/cooking.md"
        )
        try db.insertNote(&note)
        
        let results = try db.searchNotes(query: "quantum physics")
        XCTAssertEqual(results.count, 0)
    }
    
    // MARK: - Stats Tests
    
    func testNoteStats() throws {
        var event = SyncEvent(messageCount: 3)
        try db.insertSyncEvent(&event)
        
        var n1 = Note(syncEventId: event.id!, slackTs: "3000.001", originalText: "p1",
                      classifiedCategory: "Projects", classifiedFilename: "p1.md", destinationPath: "Projects/p1.md")
        var n2 = Note(syncEventId: event.id!, slackTs: "3000.002", originalText: "p2",
                      classifiedCategory: "Projects", classifiedFilename: "p2.md", destinationPath: "Projects/p2.md")
        var n3 = Note(syncEventId: event.id!, slackTs: "3000.003", originalText: "r1",
                      classifiedCategory: "Resources", classifiedFilename: "r1.md", destinationPath: "Resources/r1.md")
        
        try db.insertNote(&n1)
        try db.insertNote(&n2)
        try db.insertNote(&n3)
        
        let stats = try db.noteStats()
        XCTAssertEqual(stats["Projects"], 2)
        XCTAssertEqual(stats["Resources"], 1)
    }
    
    // MARK: - Uncorrected Notes
    
    func testUncorrectedNotes() throws {
        var event = SyncEvent(messageCount: 2)
        try db.insertSyncEvent(&event)
        
        var n1 = Note(syncEventId: event.id!, slackTs: "4000.001", originalText: "note1",
                      classifiedCategory: "Projects", classifiedFilename: "n1.md", destinationPath: "Projects/n1.md")
        var n2 = Note(syncEventId: event.id!, slackTs: "4000.002", originalText: "note2",
                      classifiedCategory: "Areas", classifiedFilename: "n2.md", destinationPath: "Areas/n2.md")
        
        try db.insertNote(&n1)
        try db.insertNote(&n2)
        
        // Correct one note
        n1.applyCorrection(newCategory: "Resources")
        try db.dbWriter.write { db in
            try n1.update(db)
        }
        
        let uncorrected = try db.uncorrectedNotes()
        XCTAssertEqual(uncorrected.count, 1)
        XCTAssertEqual(uncorrected.first?.slackTs, "4000.002")
    }
}
