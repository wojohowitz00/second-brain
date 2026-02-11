//
//  StatusIndicator.swift
//  SecondBrain
//

import SwiftUI

struct StatusIndicator: View {
    let status: SystemStatus
    
    var body: some View {
        Circle()
            .fill(statusColor)
            .frame(width: 12, height: 12)
    }
    
    var statusColor: Color {
        switch status {
        case .healthy: return .green
        case .unhealthy: return .red
        case .unknown: return .orange
        }
    }
}

#Preview {
    HStack {
        StatusIndicator(status: .healthy)
        StatusIndicator(status: .unhealthy)
        StatusIndicator(status: .unknown)
    }
    .padding()
}
