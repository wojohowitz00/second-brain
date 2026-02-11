import Foundation

public struct ClassificationResult: Decodable {
    public let category: String
    public let name: String?
    public let filename: String?
    public let title: String?
    
    public init(category: String, name: String? = nil, filename: String? = nil, title: String? = nil) {
        self.category = category
        self.name = name
        self.filename = filename
        self.title = title
    }
    
    /// The PARA folder this classification maps to.
    public var folderName: String {
        switch category.lowercased() {
        case "projects": return "Projects"
        case "areas":    return "Areas"
        case "resources": return "Resources"
        case "archives": return "Archives"
        default:         return "Inbox"
        }
    }
    
    /// Extracts a ClassificationResult from a raw LLM response string.
    /// Handles cases where the model wraps JSON in markdown code fences.
    public static func parse(from raw: String) -> ClassificationResult? {
        // Strip markdown code fences if present
        var cleaned = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        if cleaned.hasPrefix("```") {
            // Remove opening fence (```json or ```)
            if let newlineIndex = cleaned.firstIndex(of: "\n") {
                cleaned = String(cleaned[cleaned.index(after: newlineIndex)...])
            }
            // Remove closing fence
            if cleaned.hasSuffix("```") {
                cleaned = String(cleaned.dropLast(3)).trimmingCharacters(in: .whitespacesAndNewlines)
            }
        }
        
        guard let data = cleaned.data(using: .utf8) else { return nil }
        return try? JSONDecoder().decode(ClassificationResult.self, from: data)
    }
}

public class NoteProcessor {
    private let slackClient: SlackClientProtocol
    private let ollamaClient: OllamaClientProtocol
    private let vaultScanner: VaultScanner
    private let fileManager: FileManager
    
    public init(slackClient: SlackClientProtocol = SlackClient(),
                ollamaClient: OllamaClientProtocol = OllamaClient(),
                vaultScanner: VaultScanner = VaultScanner(),
                fileManager: FileManager = .default) {
        self.slackClient = slackClient
        self.ollamaClient = ollamaClient
        self.vaultScanner = vaultScanner
        self.fileManager = fileManager
    }
    
    public func processInbox(token: String, channelID: String, vaultPath: String, model: String) async throws -> Int {
        // 1. Fetch recent messages
        let messages = try await slackClient.fetchHistory(token: token, channelID: channelID, latest: nil)
        
        var processedCount = 0
        
        for message in messages {
            if message.text.isEmpty { continue }
            
            // 2. Classify via Ollama
            let prompt = """
            You are a personal knowledge management assistant. Categorize the following text into one of the PARA method categories:
            - Projects: Active goals with a deadline.
            - Areas: Ongoing responsibilities without a deadline.
            - Resources: Topics of interest or reference material.
            - Archives: Inactive items.

            Text: "\(message.text)"

            Respond strictly with a JSON object. Do not explain.
            Format:
            {
                "category": "Projects" | "Areas" | "Resources" | "Archives",
                "name": "The specific Project/Area/Resource name (e.g. 'Health', 'Q3 Report')",
                "filename": "A safe filename ending in .md",
                "title": "A concise title"
            }
            """
            
            let rawResponse = try? await ollamaClient.generate(model: model, prompt: prompt)
            
            // 3. Parse classification (fallback to Inbox)
            let classification: ClassificationResult
            if let raw = rawResponse, let parsed = ClassificationResult.parse(from: raw) {
                classification = parsed
            } else {
                classification = ClassificationResult(category: "Inbox")
            }
            
            // 4. Route to correct PARA folder
            let folderURL = URL(fileURLWithPath: vaultPath).appendingPathComponent(classification.folderName)
            if !fileManager.fileExists(atPath: folderURL.path) {
                try? fileManager.createDirectory(at: folderURL, withIntermediateDirectories: true)
            }
            
            let filename = classification.filename ?? "slack_\(message.ts).md"
            let noteTitle = classification.title ?? "Note from Slack"
            let fileURL = folderURL.appendingPathComponent(filename)
            
            if !fileManager.fileExists(atPath: fileURL.path) {
                let content = "# \(noteTitle)\n\n\(message.text)\n"
                try content.write(to: fileURL, atomically: true, encoding: String.Encoding.utf8)
                processedCount += 1
            }
        }
        
        return processedCount
    }
}

