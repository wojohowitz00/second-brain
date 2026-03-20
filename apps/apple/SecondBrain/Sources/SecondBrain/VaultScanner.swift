import Foundation

public struct Domain: Identifiable, Equatable, Codable {
    public let id: String
    public let name: String
    public let path: URL
    public var projects: [String] = []
    public var areas: [String] = []
    public var resources: [String] = []
    public var archives: [String] = []
    
    public init(name: String, path: URL) {
        self.id = name
        self.name = name
        self.path = path
    }
}

public struct VaultScanner {
    private let fileManager: FileManager
    
    public init(fileManager: FileManager = .default) {
        self.fileManager = fileManager
    }
    
    public func scan(rootURL: URL) throws -> [Domain] {
        // Domains are top-level folders: Personal, CCBH, Just Value
        // Hardcoded for V1 parity, or dynamic? V1 was dynamic but looked for specific structure.
        // Let's scan top-level subdirectories.
        
        var domains: [Domain] = []
        
        let resourceKeys: [URLResourceKey] = [.isDirectoryKey]
        let options: FileManager.DirectoryEnumerationOptions = [.skipsHiddenFiles]
        
        let rootContents = try fileManager.contentsOfDirectory(at: rootURL, includingPropertiesForKeys: resourceKeys, options: options)
        
        for url in rootContents {
            let resourceValues = try url.resourceValues(forKeys: Set(resourceKeys))
            if resourceValues.isDirectory == true {
                // Check if this folder has PARA structure (heuristic for Domain)
                if isDomainFolder(url) {
                    var domain = Domain(name: url.lastPathComponent, path: url)
                    domain.projects = scanSubfolders(parent: url.appendingPathComponent("Projects"))
                    domain.areas = scanSubfolders(parent: url.appendingPathComponent("Areas"))
                    domain.resources = scanSubfolders(parent: url.appendingPathComponent("Resources"))
                    domain.archives = scanSubfolders(parent: url.appendingPathComponent("Archives"))
                    domains.append(domain)
                }
            }
        }
        
        return domains
    }
    
    private func isDomainFolder(_ url: URL) -> Bool {
        // A domain folder must contain at least one of PARA folders to be valid
        let paraFolders = ["Projects", "Areas", "Resources", "Archives"]
        for folder in paraFolders {
             let folderURL = url.appendingPathComponent(folder)
             var isDir: ObjCBool = false
             if fileManager.fileExists(atPath: folderURL.path, isDirectory: &isDir) && isDir.boolValue {
                 return true
             }
        }
        return false
    }
    
    private func scanSubfolders(parent: URL) -> [String] {
        guard let contents = try? fileManager.contentsOfDirectory(at: parent, includingPropertiesForKeys: [.isDirectoryKey], options: [.skipsHiddenFiles]) else {
            return []
        }
        
        var subjects: [String] = []
        for url in contents {
             if let resources = try? url.resourceValues(forKeys: [.isDirectoryKey]), resources.isDirectory == true {
                 subjects.append(url.lastPathComponent)
             }
        }
        return subjects.sorted()
    }
}
