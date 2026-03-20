//
//  Message.swift
//  SecondBrain
//

import Foundation

struct Message: Identifiable, Codable, Hashable {
    let id: String // Slack timestamp
    let text: String
    let timestamp: Date
    let user: String?
    let processed: Bool
    let classification: Classification?
    
    enum CodingKeys: String, CodingKey {
        case id = "ts"
        case text
        case timestamp
        case user
        case processed
        case classification
    }
}

struct Classification: Codable, Hashable {
    let destination: String
    let confidence: Double
    let filename: String
    let extracted: [String: AnyCodable]
    let linkedEntities: [LinkedEntity]
    
    enum CodingKeys: String, CodingKey {
        case destination
        case confidence
        case filename
        case extracted
        case linkedEntities = "linked_entities"
    }
}

struct LinkedEntity: Codable, Hashable {
    let name: String
    let type: String
}

// Helper for encoding/decoding Any values in JSON
struct AnyCodable: Codable, Equatable, Hashable {
    let value: Any
    
    init(_ value: Any) {
        self.value = value
    }
    
    static func == (lhs: AnyCodable, rhs: AnyCodable) -> Bool {
        // Compare based on type and value
        switch (lhs.value, rhs.value) {
        case let (lhsBool as Bool, rhsBool as Bool):
            return lhsBool == rhsBool
        case let (lhsInt as Int, rhsInt as Int):
            return lhsInt == rhsInt
        case let (lhsDouble as Double, rhsDouble as Double):
            return lhsDouble == rhsDouble
        case let (lhsString as String, rhsString as String):
            return lhsString == rhsString
        case let (lhsArray as [Any], rhsArray as [Any]):
            guard lhsArray.count == rhsArray.count else { return false }
            return zip(lhsArray.map { AnyCodable($0) }, rhsArray.map { AnyCodable($0) }).allSatisfy { $0 == $1 }
        case let (lhsDict as [String: Any], rhsDict as [String: Any]):
            guard lhsDict.count == rhsDict.count else { return false }
            return lhsDict.allSatisfy { key, value in
                guard let rhsValue = rhsDict[key] else { return false }
                return AnyCodable(value) == AnyCodable(rhsValue)
            }
        default:
            return false
        }
    }
    
    func hash(into hasher: inout Hasher) {
        switch value {
        case let bool as Bool:
            hasher.combine(0)
            hasher.combine(bool)
        case let int as Int:
            hasher.combine(1)
            hasher.combine(int)
        case let double as Double:
            hasher.combine(2)
            hasher.combine(double)
        case let string as String:
            hasher.combine(3)
            hasher.combine(string)
        case let array as [Any]:
            hasher.combine(4)
            for item in array {
                AnyCodable(item).hash(into: &hasher)
            }
        case let dict as [String: Any]:
            hasher.combine(5)
            for (key, value) in dict.sorted(by: { $0.key < $1.key }) {
                hasher.combine(key)
                AnyCodable(value).hash(into: &hasher)
            }
        default:
            hasher.combine(6)
            hasher.combine(String(describing: value))
        }
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        if let bool = try? container.decode(Bool.self) {
            value = bool
        } else if let int = try? container.decode(Int.self) {
            value = int
        } else if let double = try? container.decode(Double.self) {
            value = double
        } else if let string = try? container.decode(String.self) {
            value = string
        } else if let array = try? container.decode([AnyCodable].self) {
            value = array.map { $0.value }
        } else if let dict = try? container.decode([String: AnyCodable].self) {
            value = dict.mapValues { $0.value }
        } else {
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "Unsupported type")
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        
        switch value {
        case let bool as Bool:
            try container.encode(bool)
        case let int as Int:
            try container.encode(int)
        case let double as Double:
            try container.encode(double)
        case let string as String:
            try container.encode(string)
        case let array as [Any]:
            try container.encode(array.map { AnyCodable($0) })
        case let dict as [String: Any]:
            try container.encode(dict.mapValues { AnyCodable($0) })
        default:
            throw EncodingError.invalidValue(value, EncodingError.Context(codingPath: container.codingPath, debugDescription: "Unsupported type"))
        }
    }
}
