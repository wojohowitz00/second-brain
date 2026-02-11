import Foundation

public protocol OllamaClientProtocol {
    func isReachable() async -> Bool
    func generate(model: String, prompt: String) async throws -> String
    func listModels() async throws -> [String]
}

public struct OllamaClient: OllamaClientProtocol {
    private let baseURL: URL
    private let session: URLSession

    public init(baseURL: URL = URL(string: "http://localhost:11434")!, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
    }

    public func isReachable() async -> Bool {
        let url = baseURL.appendingPathComponent("/")
        var request = URLRequest(url: url)
        request.httpMethod = "HEAD"
        request.timeoutInterval = 2.0

        do {
            let (_, response) = try await session.data(for: request)
            if let httpResponse = response as? HTTPURLResponse {
                return httpResponse.statusCode == 200
            }
            return false
        } catch {
            return false
        }
    }

    public func generate(model: String, prompt: String) async throws -> String {
        let url = baseURL.appendingPathComponent("/api/generate")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body: [String: Any] = [
            "model": model,
            "prompt": prompt,
            "stream": false
        ]

        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw urLError(.badServerResponse)
        }

        struct GenerateResponse: Decodable {
            let response: String
        }

        let result = try JSONDecoder().decode(GenerateResponse.self, from: data)
        return result.response
    }

    public func listModels() async throws -> [String] {
        let url = baseURL.appendingPathComponent("/api/tags")
        var request = URLRequest(url: url)
        request.httpMethod = "GET"

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw urLError(.badServerResponse)
        }

        struct ListResponse: Decodable {
            struct Model: Decodable {
                let name: String
            }
            let models: [Model]
        }

        let result = try JSONDecoder().decode(ListResponse.self, from: data)
        return result.models.map { $0.name }
    }
    
    private func urLError(_ code: URLError.Code) -> URLError {
        return URLError(code)
    }
}
