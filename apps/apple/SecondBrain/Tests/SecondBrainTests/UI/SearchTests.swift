import XCTest
import GRDB
@testable import SecondBrain

final class SearchTests: XCTestCase {
    var db: AppDatabase!
    
    override func setUp() {
        super.setUp()
        db = try! AppDatabase.makeInMemory()
    }
    
    // MARK: - Helpers
    
    private func seedNotes() throws {
        var event = SyncEvent(messageCount: 3)
        try db.insertSyncEvent(&event)
        
        var n1 = Note(syncEventId: event.id!, slackTs: "s1",
                      originalText: "Machine learning research paper on transformers and attention",
                      classifiedCategory: "Resources",
                      classifiedFilename: "ml_transformers.md",
                      classifiedTitle: "ML Transformers Research",
                      destinationPath: "Resources/ml_transformers.md")
        
        var n2 = Note(syncEventId: event.id!, slackTs: "s2",
                      originalText: "Weekly grocery list and meal planning",
                      classifiedCategory: "Areas",
                      classifiedFilename: "grocery_list.md",
                      classifiedTitle: "Weekly Groceries",
                      destinationPath: "Areas/grocery_list.md")
        
        var n3 = Note(syncEventId: event.id!, slackTs: "s3",
                      originalText: "Q3 product launch deadline and marketing plan",
                      classifiedCategory: "Projects",
                      classifiedFilename: "q3_launch.md",
                      classifiedTitle: "Q3 Product Launch",
                      destinationPath: "Projects/q3_launch.md")
        
        try db.insertNote(&n1)
        try db.insertNote(&n2)
        try db.insertNote(&n3)
    }
    
    // MARK: - Tests
    
    func testSearch_ReturnsMatchingNotes() throws {
        try seedNotes()
        
        let results = try db.searchNotes(query: "machine learning")
        XCTAssertEqual(results.count, 1)
        XCTAssertEqual(results.first?.classifiedTitle, "ML Transformers Research")
    }
    
    func testSearch_EmptyQuery_ReturnsEmpty() throws {
        try seedNotes()
        
        let results = try db.searchNotes(query: "")
        XCTAssertEqual(results.count, 0)
    }
    
    func testSearch_NoMatch_ReturnsEmpty() throws {
        try seedNotes()
        
        let results = try db.searchNotes(query: "quantum physics")
        XCTAssertEqual(results.count, 0)
    }
    
    func testSearch_MatchesTitle() throws {
        try seedNotes()
        
        let results = try db.searchNotes(query: "groceries")
        XCTAssertEqual(results.count, 1)
        XCTAssertEqual(results.first?.classifiedTitle, "Weekly Groceries")
    }
    
    func testSearch_MultipleMatches() throws {
        try seedNotes()
        
        // "plan" appears in both grocery ("meal planning") and Q3 ("marketing plan")
        let results = try db.searchNotes(query: "plan")
        XCTAssertEqual(results.count, 2)
    }
}
