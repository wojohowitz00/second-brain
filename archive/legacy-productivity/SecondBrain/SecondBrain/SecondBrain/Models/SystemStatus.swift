//
//  SystemStatus.swift
//  SecondBrain
//

import Foundation

enum SystemStatus {
    case healthy
    case unhealthy
    case unknown
    
    var displayName: String {
        switch self {
        case .healthy: return "Healthy"
        case .unhealthy: return "Unhealthy"
        case .unknown: return "Unknown"
        }
    }
}
