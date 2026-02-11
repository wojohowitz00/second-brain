import Foundation

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
            // Skip bots or empty messages if needed
            if message.text.isEmpty { continue }
            
            // 2. Classify
            let prompt = """
            You are a personal knowledge management assistant. Categorize the following text into one of the PARA method categories:
            - Projects: Active goals with a deadine.
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
            
            // In a real implementation, we would parse the JSON response.
            // For this phase, we'll just save to "Inbox" or a default location to verify flow.
            let _ = try? await ollamaClient.generate(model: model, prompt: prompt)
            
            // 3. Save to Vault (Inbox for now)
            let inboxURL = URL(fileURLWithPath: vaultPath).appendingPathComponent("Inbox")
            if !fileManager.fileExists(atPath: inboxURL.path) {
                try? fileManager.createDirectory(at: inboxURL, withIntermediateDirectories: true)
            }
            
            let filename = "slack_\(message.ts).md"
            let fileURL = inboxURL.appendingPathComponent(filename)
            
            if !fileManager.fileExists(atPath: fileURL.path) {
                let content = "# Note from Slack\n\n\(message.text)\n"
                try content.write(to: fileURL, atomically: true, encoding: String.Encoding.utf8)
                processedCount += 1
            }
        }
        
        return processedCount
    }
}
