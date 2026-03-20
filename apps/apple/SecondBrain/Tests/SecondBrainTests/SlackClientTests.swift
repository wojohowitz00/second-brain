import XCTest
@testable import SecondBrain

final class SlackClientTests: XCTestCase {
    
    func testFetchHistory_Success() async throws {
        // Given
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [MockURLProtocol.self]
        let session = URLSession(configuration: config)
        let client = SlackClient(session: session)
        
        let jsonResponse = """
        {
            "ok": true,
            "messages": [
                {
                    "text": "Hello world",
                    "user": "U12345",
                    "ts": "1678888888.000000"
                }
            ]
        }
        """
        
        MockURLProtocol.requestHandler = { request in
            XCTAssertEqual(request.url?.path, "/api/conversations.history")
            XCTAssertEqual(request.allHTTPHeaderFields?["Authorization"], "Bearer test-token")
            let response = HTTPURLResponse(url: request.url!, statusCode: 200, httpVersion: nil, headerFields: nil)!
            return (response, jsonResponse.data(using: .utf8)!)
        }
        
        // When
        let messages = try await client.fetchHistory(token: "test-token", channelID: "C12345")
        
        // Then
        XCTAssertEqual(messages.count, 1)
        XCTAssertEqual(messages.first?.text, "Hello world")
    }
}
