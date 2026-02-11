import XCTest
@testable import SecondBrain

final class VaultScannerTests: XCTestCase {
    var fileManager: FileManager!
    var tempURL: URL!
    
    override func setUp() {
        super.setUp()
        fileManager = FileManager.default
        tempURL = fileManager.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try! fileManager.createDirectory(at: tempURL, withIntermediateDirectories: true)
    }
    
    override func tearDown() {
        try? fileManager.removeItem(at: tempURL)
        super.tearDown()
    }
    
    func testScan_FindsDomainsAndSubjects() throws {
        // Given: structure
        // Root/
        //   Personal/
        //     Projects/
        //       App Dev/
        //     Areas/
        //       Health/
        //   Work/ (No PARA, should be ignored or handled?)
        //     Docs/
        //   CCBH/
        //     Resources/
        //       Finance/
        
        let personal = tempURL.appendingPathComponent("Personal")
        let ccbh = tempURL.appendingPathComponent("CCBH")
        let work = tempURL.appendingPathComponent("Work") // Invalid domain
        
        try createDir(personal.appendingPathComponent("Projects").appendingPathComponent("App Dev"))
        try createDir(personal.appendingPathComponent("Areas").appendingPathComponent("Health"))
        try createDir(ccbh.appendingPathComponent("Resources").appendingPathComponent("Finance"))
        try createDir(work.appendingPathComponent("Docs"))
        
        let scanner = VaultScanner(fileManager: fileManager)
        
        // When
        let domains = try scanner.scan(rootURL: tempURL)
        
        // Then
        XCTAssertEqual(domains.count, 2)
        
        let personalDomain = domains.first { $0.name == "Personal" }
        XCTAssertNotNil(personalDomain)
        XCTAssertEqual(personalDomain?.projects, ["App Dev"])
        XCTAssertEqual(personalDomain?.areas, ["Health"])
        
        let ccbhDomain = domains.first { $0.name == "CCBH" }
        XCTAssertNotNil(ccbhDomain)
        XCTAssertEqual(ccbhDomain?.resources, ["Finance"])
        
        XCTAssertNil(domains.first { $0.name == "Work" })
    }
    
    private func createDir(_ url: URL) throws {
        try fileManager.createDirectory(at: url, withIntermediateDirectories: true)
    }
}
