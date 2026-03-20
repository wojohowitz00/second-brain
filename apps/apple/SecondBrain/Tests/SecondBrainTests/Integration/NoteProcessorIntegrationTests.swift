import XCTest
@testable import SecondBrain

// Mock Clients
class MockSlackClient: SlackClientProtocol {
    var messagesToReturn: [SlackMessage] = []
    
    func fetchHistory(token: String, channelID: String, latest: String?) async throws -> [SlackMessage] {
        return messagesToReturn
    }
}

class MockOllamaClient: OllamaClientProtocol {
    var generateResult: String = ""
    var generateResults: [String] = [] // For multiple calls
    private var callIndex = 0
    
    func isReachable() async -> Bool { return true }
    
    func generate(model: String, prompt: String) async throws -> String {
        if !generateResults.isEmpty {
            let result = generateResults[callIndex % generateResults.count]
            callIndex += 1
            return result
        }
        return generateResult
    }
    
    func listModels() async throws -> [String] { return ["mock-model"] }
}

// MARK: - Integration Tests

final class NoteProcessorIntegrationTests: XCTestCase {
    var fileManager: FileManager!
    var tempVaultURL: URL!
    var processor: NoteProcessor!
    var mockSlack: MockSlackClient!
    var mockOllama: MockOllamaClient!
    
    override func setUp() {
        super.setUp()
        fileManager = FileManager.default
        tempVaultURL = fileManager.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try! fileManager.createDirectory(at: tempVaultURL, withIntermediateDirectories: true)
        
        mockSlack = MockSlackClient()
        mockOllama = MockOllamaClient()
        processor = NoteProcessor(slackClient: mockSlack, ollamaClient: mockOllama, fileManager: fileManager)
    }
    
    override func tearDown() {
        try? fileManager.removeItem(at: tempVaultURL)
        super.tearDown()
    }
    
    // MARK: - PARA Routing Tests
    
    func testProcessInbox_RoutesToProjectsFolder() async throws {
        // Given: A message classified as "Projects"
        let message = SlackMessage(text: "Launch MVP by March", user: "U1", ts: "1000.001", bot_id: nil)
        mockSlack.messagesToReturn = [message]
        mockOllama.generateResult = """
        { "category": "Projects", "name": "MVP Launch", "filename": "mvp_launch.md", "title": "MVP Launch Plan" }
        """
        
        // When
        let count = try await processor.processInbox(token: "t", channelID: "C1", vaultPath: tempVaultURL.path, model: "m")
        
        // Then
        XCTAssertEqual(count, 1)
        let fileURL = tempVaultURL.appendingPathComponent("Projects/mvp_launch.md")
        XCTAssertTrue(fileManager.fileExists(atPath: fileURL.path), "File should be in Projects/")
        let content = try String(contentsOf: fileURL)
        XCTAssertTrue(content.contains("# MVP Launch Plan"))
        XCTAssertTrue(content.contains("Launch MVP by March"))
    }
    
    func testProcessInbox_FallbackToInbox() async throws {
        // Given: Ollama returns garbage (unparseable)
        let message = SlackMessage(text: "Something random", user: "U1", ts: "2000.002", bot_id: nil)
        mockSlack.messagesToReturn = [message]
        mockOllama.generateResult = "I'm sorry, I can't classify this."
        
        // When
        let count = try await processor.processInbox(token: "t", channelID: "C1", vaultPath: tempVaultURL.path, model: "m")
        
        // Then
        XCTAssertEqual(count, 1)
        let fileURL = tempVaultURL.appendingPathComponent("Inbox/slack_2000.002.md")
        XCTAssertTrue(fileManager.fileExists(atPath: fileURL.path), "File should fall back to Inbox/")
    }
    
    func testProcessInbox_RoutesToMultipleFolders() async throws {
        // Given: Two messages, one Projects, one Resources
        let msg1 = SlackMessage(text: "Finish report", user: "U1", ts: "3000.001", bot_id: nil)
        let msg2 = SlackMessage(text: "Interesting article on AI", user: "U1", ts: "3000.002", bot_id: nil)
        mockSlack.messagesToReturn = [msg1, msg2]
        mockOllama.generateResults = [
            """
            { "category": "Projects", "name": "Report", "filename": "report.md", "title": "Finish Report" }
            """,
            """
            { "category": "Resources", "name": "AI", "filename": "ai_article.md", "title": "AI Article" }
            """
        ]
        
        // When
        let count = try await processor.processInbox(token: "t", channelID: "C1", vaultPath: tempVaultURL.path, model: "m")
        
        // Then
        XCTAssertEqual(count, 2)
        XCTAssertTrue(fileManager.fileExists(atPath: tempVaultURL.appendingPathComponent("Projects/report.md").path))
        XCTAssertTrue(fileManager.fileExists(atPath: tempVaultURL.appendingPathComponent("Resources/ai_article.md").path))
    }
}

// MARK: - ClassificationResult Unit Tests

final class ClassificationResultTests: XCTestCase {
    func testParse_ValidJSON() {
        let raw = """
        { "category": "Areas", "name": "Health", "filename": "health.md", "title": "Health Tracking" }
        """
        let result = ClassificationResult.parse(from: raw)
        XCTAssertNotNil(result)
        XCTAssertEqual(result?.category, "Areas")
        XCTAssertEqual(result?.folderName, "Areas")
        XCTAssertEqual(result?.filename, "health.md")
    }
    
    func testParse_MarkdownCodeFence() {
        let raw = """
        ```json
        { "category": "Projects", "name": "App", "filename": "app.md", "title": "App Dev" }
        ```
        """
        let result = ClassificationResult.parse(from: raw)
        XCTAssertNotNil(result)
        XCTAssertEqual(result?.folderName, "Projects")
    }
    
    func testParse_InvalidJSON_ReturnsNil() {
        let raw = "This is not JSON at all"
        let result = ClassificationResult.parse(from: raw)
        XCTAssertNil(result)
    }
    
    func testFolderName_UnknownCategory_FallsBackToInbox() {
        let result = ClassificationResult(category: "Unknown")
        XCTAssertEqual(result.folderName, "Inbox")
    }
}
