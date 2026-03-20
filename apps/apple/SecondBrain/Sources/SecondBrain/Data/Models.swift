import Foundation
import GRDB

/// A sync event records a single processing run.
public struct SyncEvent: Codable, FetchableRecord, MutablePersistableRecord {
    public var id: Int64?
    public var timestamp: String
    public var messageCount: Int
    public var status: String  // "success" or "error"
    
    public static let databaseTableName = "sync_event"
    
    public init(messageCount: Int, status: String = "success") {
        self.timestamp = ISO8601DateFormatter().string(from: Date())
        self.messageCount = messageCount
        self.status = status
    }
    
    // Auto-assign ID on insert
    public mutating func didInsert(_ inserted: InsertionSuccess) {
        id = inserted.rowID
    }
}

/// A note records a single classified message.
public struct Note: Codable, FetchableRecord, MutablePersistableRecord {
    public var id: Int64?
    public var syncEventId: Int64
    public var slackTs: String
    public var originalText: String
    public var classifiedCategory: String
    public var classifiedName: String?
    public var classifiedFilename: String
    public var classifiedTitle: String?
    public var destinationPath: String
    public var createdAt: String
    public var correctedCategory: String?
    public var correctedAt: String?
    
    public static let databaseTableName = "note"
    
    public init(
        syncEventId: Int64,
        slackTs: String,
        originalText: String,
        classifiedCategory: String,
        classifiedName: String? = nil,
        classifiedFilename: String,
        classifiedTitle: String? = nil,
        destinationPath: String
    ) {
        self.syncEventId = syncEventId
        self.slackTs = slackTs
        self.originalText = originalText
        self.classifiedCategory = classifiedCategory
        self.classifiedName = classifiedName
        self.classifiedFilename = classifiedFilename
        self.classifiedTitle = classifiedTitle
        self.destinationPath = destinationPath
        self.createdAt = ISO8601DateFormatter().string(from: Date())
    }
    
    // Auto-assign ID on insert
    public mutating func didInsert(_ inserted: InsertionSuccess) {
        id = inserted.rowID
    }
    
    /// Apply a correction to this note's category.
    public mutating func applyCorrection(newCategory: String) {
        correctedCategory = newCategory
        correctedAt = ISO8601DateFormatter().string(from: Date())
    }
}
