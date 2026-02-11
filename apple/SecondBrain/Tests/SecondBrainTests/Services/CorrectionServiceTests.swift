import XCTest
import GRDB
@testable import SecondBrain

final class CorrectionServiceTests: XCTestCase {
    var db: AppDatabase!
    var tempDir: URL!
    var service: CorrectionService!
    
    override func setUp() {
        super.setUp()
        db = try! AppDatabase.makeInMemory()
        tempDir = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try! FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        service = CorrectionService()
    }
    
    override func tearDown() {
        try? FileManager.default.removeItem(at: tempDir)
        super.tearDown()
    }
    
    // MARK: - Helpers
    
    private func createTestNote(category: String = "Projects", filename: String = "test_note.md") throws -> Note {
        var event = SyncEvent(messageCount: 1)
        try db.insertSyncEvent(&event)
        
        let folderName: String
        switch category.lowercased() {
        case "projects": folderName = "Projects"
        case "areas":    folderName = "Areas"
        case "resources": folderName = "Resources"
        default:         folderName = "Inbox"
        }
        
        // Create file on disk
        let folder = tempDir.appendingPathComponent(folderName)
        try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        let filePath = folder.appendingPathComponent(filename)
        try "# Test Note\n\nSome content".write(to: filePath, atomically: true, encoding: .utf8)
        
        var note = Note(
            syncEventId: event.id!,
            slackTs: "test.\(UUID().uuidString)",
            originalText: "Some content",
            classifiedCategory: category,
            classifiedFilename: filename,
            destinationPath: "\(folderName)/\(filename)"
        )
        try db.insertNote(&note)
        return note
    }
    
    // MARK: - Tests
    
    func testApplyCorrection_MovesFileAndUpdatesDB() throws {
        var note = try createTestNote(category: "Projects", filename: "to_move.md")
        
        // Verify file exists at old location
        let oldPath = tempDir.appendingPathComponent("Projects/to_move.md")
        XCTAssertTrue(FileManager.default.fileExists(atPath: oldPath.path))
        
        // Apply correction
        try service.applyCorrection(
            note: &note,
            newCategory: "Resources",
            vaultPath: tempDir.path,
            database: db
        )
        
        // File moved
        let newPath = tempDir.appendingPathComponent("Resources/to_move.md")
        XCTAssertFalse(FileManager.default.fileExists(atPath: oldPath.path))
        XCTAssertTrue(FileManager.default.fileExists(atPath: newPath.path))
        
        // DB updated
        XCTAssertEqual(note.correctedCategory, "Resources")
        XCTAssertNotNil(note.correctedAt)
        XCTAssertEqual(note.destinationPath, "Resources/to_move.md")
        
        // Verify in database
        let fetched = try db.dbWriter.read { db in
            try Note.fetchOne(db, key: note.id)
        }
        XCTAssertEqual(fetched?.correctedCategory, "Resources")
        XCTAssertEqual(fetched?.destinationPath, "Resources/to_move.md")
    }
    
    func testApplyCorrection_MissingFile_StillUpdatesDB() throws {
        var note = try createTestNote(category: "Projects", filename: "missing.md")
        
        // Delete the file first
        let oldPath = tempDir.appendingPathComponent("Projects/missing.md")
        try FileManager.default.removeItem(at: oldPath)
        XCTAssertFalse(FileManager.default.fileExists(atPath: oldPath.path))
        
        // Apply correction — should not throw
        try service.applyCorrection(
            note: &note,
            newCategory: "Areas",
            vaultPath: tempDir.path,
            database: db
        )
        
        // DB still updated
        XCTAssertEqual(note.correctedCategory, "Areas")
        XCTAssertEqual(note.destinationPath, "Areas/missing.md")
    }
    
    func testApplyCorrection_CreatesDestinationFolder() throws {
        var note = try createTestNote(category: "Projects", filename: "auto_folder.md")
        
        // Ensure destination folder doesn't exist
        let archivesPath = tempDir.appendingPathComponent("Archives")
        XCTAssertFalse(FileManager.default.fileExists(atPath: archivesPath.path))
        
        // Apply correction
        try service.applyCorrection(
            note: &note,
            newCategory: "Archives",
            vaultPath: tempDir.path,
            database: db
        )
        
        // Folder was created and file moved
        XCTAssertTrue(FileManager.default.fileExists(atPath: archivesPath.path))
        let newFilePath = archivesPath.appendingPathComponent("auto_folder.md")
        XCTAssertTrue(FileManager.default.fileExists(atPath: newFilePath.path))
    }
}
