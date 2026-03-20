import Foundation

/// Service that handles note corrections: updates the database and moves the file on disk.
public class CorrectionService {
    private let fileManager: FileManager
    
    public init(fileManager: FileManager = .default) {
        self.fileManager = fileManager
    }
    
    /// Apply a correction to a note, moving the file and updating the DB.
    /// - Parameters:
    ///   - note: The note to correct (will be mutated in place).
    ///   - newCategory: The new PARA category (e.g. "Projects", "Areas", "Resources", "Archives").
    ///   - vaultPath: Root path of the Obsidian vault.
    ///   - database: The AppDatabase instance.
    /// - Returns: The updated Note after correction.
    @discardableResult
    public func applyCorrection(
        note: inout Note,
        newCategory: String,
        vaultPath: String,
        database: AppDatabase
    ) throws -> Note {
        // 1. Compute PARA folder name for the new category
        let newFolderName: String
        switch newCategory.lowercased() {
        case "projects": newFolderName = "Projects"
        case "areas":    newFolderName = "Areas"
        case "resources": newFolderName = "Resources"
        case "archives": newFolderName = "Archives"
        default:         newFolderName = "Inbox"
        }
        
        // 2. Compute file paths
        let oldFilePath = URL(fileURLWithPath: vaultPath).appendingPathComponent(note.destinationPath)
        let newFolder = URL(fileURLWithPath: vaultPath).appendingPathComponent(newFolderName)
        let newFilePath = newFolder.appendingPathComponent(note.classifiedFilename)
        let newDestinationPath = "\(newFolderName)/\(note.classifiedFilename)"
        
        // 3. Move file on disk (create destination folder if needed)
        if fileManager.fileExists(atPath: oldFilePath.path) {
            if !fileManager.fileExists(atPath: newFolder.path) {
                try fileManager.createDirectory(at: newFolder, withIntermediateDirectories: true)
            }
            try fileManager.moveItem(at: oldFilePath, to: newFilePath)
        }
        
        // 4. Update the note model
        note.applyCorrection(newCategory: newCategory)
        note.destinationPath = newDestinationPath
        
        // 5. Persist to database
        try database.dbWriter.write { db in
            try note.update(db)
        }
        
        return note
    }
}
