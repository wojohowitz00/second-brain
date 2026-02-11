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
    
    func isReachable() async -> Bool { return true }
    
    func generate(model: String, prompt: String) async throws -> String {
        return generateResult
    }
    
    func listModels() async throws -> [String] { return ["mock-model"] }
}

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
    
    func testProcessInbox_IntegrationFlow() async throws {
        // Given
        let message = SlackMessage(text: "Project Idea: Neural Link", user: "U1", ts: "1234567890.123456", bot_id: nil)
        mockSlack.messagesToReturn = [message]
        mockOllama.generateResult = "{ \"category\": \"Projects\", \"name\": \"Neural Link\" }"
        
        // When
        let count = try await processor.processInbox(token: "test", channelID: "C1", vaultPath: tempVaultURL.path, model: "llama3")
        
        // Then
        XCTAssertEqual(count, 1)
        
        // Verify File Creation
        let inboxURL = tempVaultURL.appendingPathComponent("Inbox")
        let fileURL = inboxURL.appendingPathComponent("slack_1234567890.123456.md")
        
        XCTAssertTrue(fileManager.fileExists(atPath: fileURL.path))
        
        let content = try String(contentsOf: fileURL)
        XCTAssertTrue(content.contains("Project Idea: Neural Link"))
    }
}
