//
//  LogsView.swift
//  SecondBrain
//

import SwiftUI
import AppKit
import UniformTypeIdentifiers

struct LogsView: View {
    @State private var logs: [LogEntry] = []
    @State private var selectedLogType: LogType = .all
    @State private var searchText: String = ""
    @State private var isAutoScroll = true
    
    var filteredLogs: [LogEntry] {
        var filtered = logs
        
        if selectedLogType != .all {
            filtered = filtered.filter { $0.type == selectedLogType }
        }
        
        if !searchText.isEmpty {
            filtered = filtered.filter { log in
                log.message.localizedCaseInsensitiveContains(searchText) ||
                log.timestamp.formatted().localizedCaseInsensitiveContains(searchText)
            }
        }
        
        return filtered
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Toolbar
            HStack {
                Picker("Log Type", selection: $selectedLogType) {
                    ForEach(LogType.allCases, id: \.self) { type in
                        Text(type.displayName).tag(type)
                    }
                }
                .frame(width: 150)
                
                TextField("Search", text: $searchText)
                    .frame(maxWidth: 200)
                
                Spacer()
                
                Toggle("Auto-scroll", isOn: $isAutoScroll)
                
                Button("Clear") {
                    logs = []
                }
                
                Button("Export") {
                    exportLogs()
                }
            }
            .padding()
            .background(Color(NSColor.controlBackgroundColor))
            
            // Log List
            ScrollViewReader { proxy in
                List(filteredLogs) { log in
                    LogEntryView(log: log)
                        .id(log.id)
                }
                .onChange(of: filteredLogs.count) {
                    if isAutoScroll, let lastLog = filteredLogs.last {
                        withAnimation {
                            proxy.scrollTo(lastLog.id, anchor: .bottom)
                        }
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .onAppear {
            startLogStreaming()
        }
    }
    
    private func startLogStreaming() {
        // In a real implementation, this would stream logs from Python scripts
        // For now, we'll simulate by reading log files periodically
        Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { _ in
            loadLogs()
        }
    }
    
    private func loadLogs() {
        // Read from log files
        let logPaths = [
            "/tmp/wry_sb.log",
            "/tmp/wry_sb-health.log",
            "/tmp/wry_sb-fix.log"
        ]
        
        var newLogs: [LogEntry] = []
        
        for (index, path) in logPaths.enumerated() {
            guard let content = try? String(contentsOfFile: path, encoding: .utf8) else { continue }
            
            let type: LogType = index == 0 ? .processing : (index == 1 ? .health : .fixes)
            
            let lines = content.components(separatedBy: "\n")
            for line in lines.suffix(50) {
                if !line.isEmpty {
                    newLogs.append(LogEntry(
                        type: type,
                        message: line,
                        timestamp: Date()
                    ))
                }
            }
        }
        
        logs = newLogs.sorted { $0.timestamp > $1.timestamp }
    }
    
    private func exportLogs() {
        let panel = NSSavePanel()
        panel.allowedContentTypes = [.text]
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        panel.nameFieldStringValue = "second-brain-logs-\(dateFormatter.string(from: Date())).txt"
        
        if panel.runModal() == .OK, let url = panel.url {
            let timeFormatter = DateFormatter()
            timeFormatter.dateStyle = .none
            timeFormatter.timeStyle = .medium
            let content = filteredLogs.map { log in
                "[\(timeFormatter.string(from: log.timestamp))] [\(log.type.displayName)] \(log.message)"
            }.joined(separator: "\n")
            
            try? content.write(to: url, atomically: true, encoding: .utf8)
        }
    }
}

#Preview {
    LogsView()
}
