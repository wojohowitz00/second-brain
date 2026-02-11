//
//  LogEntryView.swift
//  SecondBrain
//

import SwiftUI

struct LogEntryView: View {
    let log: LogEntry
    
    var body: some View {
        HStack(alignment: .top, spacing: 8) {
            Text(log.timestamp.formatted(date: .omitted, time: .standard))
                .font(.caption)
                .foregroundColor(.secondary)
                .frame(width: 80, alignment: .leading)
            
            Text(log.type.displayName)
                .font(.caption)
                .padding(.horizontal, 6)
                .padding(.vertical, 2)
                .background(typeColor.opacity(0.2))
                .foregroundColor(typeColor)
                .cornerRadius(4)
            
            Text(log.message)
                .font(.system(.body, design: .monospaced))
                .textSelection(.enabled)
        }
        .padding(.vertical, 2)
    }
    
    var typeColor: Color {
        switch log.type {
        case .processing: return .blue
        case .health: return .green
        case .fixes: return .orange
        case .all: return .gray
        }
    }
}

#Preview {
    List {
        LogEntryView(log: LogEntry(type: .processing, message: "Processing inbox message", timestamp: Date()))
        LogEntryView(log: LogEntry(type: .health, message: "Health check passed", timestamp: Date()))
        LogEntryView(log: LogEntry(type: .fixes, message: "Fixed classification issue", timestamp: Date()))
    }
}
