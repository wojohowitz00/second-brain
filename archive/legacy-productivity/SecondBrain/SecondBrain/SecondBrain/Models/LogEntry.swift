//
//  LogEntry.swift
//  SecondBrain
//

import Foundation

enum LogType: String, CaseIterable {
    case all = "all"
    case processing = "processing"
    case health = "health"
    case fixes = "fixes"
    
    var displayName: String {
        switch self {
        case .all: return "All"
        case .processing: return "Processing"
        case .health: return "Health"
        case .fixes: return "Fixes"
        }
    }
}

struct LogEntry: Identifiable {
    let id = UUID()
    let type: LogType
    let message: String
    let timestamp: Date
}
