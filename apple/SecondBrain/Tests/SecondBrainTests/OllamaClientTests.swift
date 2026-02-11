import XCTest
@testable import SecondBrain

final class OllamaClientTests: XCTestCase {
    
    func testIsReachable_Success() async {
        // Given
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [MockURLProtocol.self]
        let session = URLSession(configuration: config)
        let client = OllamaClient(session: session)
        
        MockURLProtocol.requestHandler = { request in
            let response = HTTPURLResponse(url: request.url!, statusCode: 200, httpVersion: nil, headerFields: nil)!
            return (response, Data())
        }
        
        // When
        let isReachable = await client.isReachable()
        
        // Then
        XCTAssertTrue(isReachable)
    }
    
    func testIsReachable_Failure() async {
        // Given
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [MockURLProtocol.self]
        let session = URLSession(configuration: config)
        let client = OllamaClient(session: session)
        
        MockURLProtocol.requestHandler = { request in
            throw URLError(.cannotConnectToHost)
        }
        
        // When
        let isReachable = await client.isReachable()
        
        // Then
        XCTAssertFalse(isReachable)
    }
    
    func testGenerate_Success() async throws {
        // Given
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [MockURLProtocol.self]
        let session = URLSession(configuration: config)
        let client = OllamaClient(session: session)
        
        let jsonResponse = """
        {
            "model": "llama3",
            "created_at": "2023-08-04T19:22:45.499127Z",
            "response": "Hello, world!",
            "done": true
        }
        """
        
        MockURLProtocol.requestHandler = { request in
             let response = HTTPURLResponse(url: request.url!, statusCode: 200, httpVersion: nil, headerFields: nil)!
             return (response, jsonResponse.data(using: .utf8)!)
        }
        
        // When
        let response = try await client.generate(model: "llama3", prompt: "Hi")
        
        // Then
        XCTAssertEqual(response, "Hello, world!")
    }

    func testListModels_Success() async throws {
        // Given
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [MockURLProtocol.self]
        let session = URLSession(configuration: config)
        let client = OllamaClient(session: session)

        let jsonResponse = """
        {
            "models": [
                { "name": "llama3:latest" },
                { "name": "mistral:latest" }
            ]
        }
        """

        MockURLProtocol.requestHandler = { request in
            XCTAssertEqual(request.url?.path, "/api/tags")
            XCTAssertEqual(request.httpMethod, "GET")
            let response = HTTPURLResponse(url: request.url!, statusCode: 200, httpVersion: nil, headerFields: nil)!
            return (response, jsonResponse.data(using: .utf8)!)
        }

        // When
        let models = try await client.listModels()

        // Then
        XCTAssertEqual(models, ["llama3:latest", "mistral:latest"])
    }
}

// Mock Utility
class MockURLProtocol: URLProtocol {
    static var requestHandler: ((URLRequest) throws -> (HTTPURLResponse, Data))?
    
    override class func canInit(with request: URLRequest) -> Bool { return true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { return request }
    
    override func startLoading() {
        guard let handler = MockURLProtocol.requestHandler else {
            XCTFail("Received request with no handler set")
            return
        }
        
        do {
            let (response, data) = try handler(request)
            client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
            client?.urlProtocol(self, didLoad: data)
            client?.urlProtocolDidFinishLoading(self)
        } catch {
            client?.urlProtocol(self, didFailWithError: error)
        }
    }
    override func stopLoading() {}
}
