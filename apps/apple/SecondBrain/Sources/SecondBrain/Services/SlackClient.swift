import Foundation

public struct SlackMessage: Decodable {
    public let text: String
    public let user: String
    public let ts: String
    public let bot_id: String?
}

public struct SlackHistoryResponse: Decodable {
    public let ok: Bool
    public let messages: [SlackMessage]
    public let error: String?
}

public protocol SlackClientProtocol {
    func fetchHistory(token: String, channelID: String, latest: String?) async throws -> [SlackMessage]
}

public class SlackClient: SlackClientProtocol {
    private let session: URLSession
    private let baseURL = URL(string: "https://slack.com/api")!
    
    public init(session: URLSession = .shared) {
        self.session = session
    }
    
    public func fetchHistory(token: String, channelID: String, latest: String? = nil) async throws -> [SlackMessage] {
        var components = URLComponents(url: baseURL.appendingPathComponent("conversations.history"), resolvingAgainstBaseURL: true)!
        
        var queryItems = [
            URLQueryItem(name: "channel", value: channelID),
            URLQueryItem(name: "limit", value: "20")
        ]
        
        if let latest = latest {
            queryItems.append(URLQueryItem(name: "latest", value: latest))
        }
        
        components.queryItems = queryItems
        
        var request = URLRequest(url: components.url!)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        let result = try JSONDecoder().decode(SlackHistoryResponse.self, from: data)
        
        guard result.ok else {
            // In a real app, define a proper error type
            throw URLError(.cannotParseResponse)
        }
        
        return result.messages
    }
}
