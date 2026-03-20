//
//  MessagesView.swift
//  SecondBrain
//

import SwiftUI

struct MessagesView: View {
    @EnvironmentObject var settings: AppSettings
    @State private var messages: [Message] = []
    @State private var isLoading = false
    @State private var selectedMessage: Message?
    
    var body: some View {
        HSplitView {
            // Message List
            List(messages, selection: $selectedMessage) { message in
                MessageRow(message: message)
                    .tag(message)
            }
            .frame(minWidth: 300)
            
            // Message Detail
            if let message = selectedMessage {
                MessageDetailView(message: message)
            } else {
                Text("Select a message to view details")
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button(action: loadMessages) {
                    Label("Refresh", systemImage: "arrow.clockwise")
                }
                .disabled(isLoading)
            }
        }
        .onAppear {
            loadMessages()
        }
    }
    
    private func loadMessages() {
        isLoading = true
        
        // Call Python script to fetch messages
        let result = PythonBridge.shared.executeScriptJSON("process_inbox.py", arguments: ["--list-messages"], vaultPath: settings.vaultPath, as: [Message].self)
        
        DispatchQueue.main.async {
            isLoading = false
            switch result {
            case .success(let msgs):
                messages = msgs
            case .failure(let error):
                print("Error loading messages: \(error.localizedDescription)")
                messages = []
            }
        }
    }
}

struct MessageRow: View {
    let message: Message
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(message.text)
                .lineLimit(2)
                .font(.body)
            
            HStack {
                if let classification = message.classification {
                    Label(classification.destination, systemImage: "tag.fill")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Text(message.timestamp.formatted(date: .omitted, time: .shortened))
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 4)
    }
}

struct MessageDetailView: View {
    @EnvironmentObject var settings: AppSettings
    let message: Message
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Message Text
                VStack(alignment: .leading, spacing: 8) {
                    Text("Message")
                        .font(.headline)
                    Text(message.text)
                        .textSelection(.enabled)
                }
                .padding()
                .background(Color(NSColor.controlBackgroundColor))
                .cornerRadius(8)
                
                // Classification
                if let classification = message.classification {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Classification")
                            .font(.headline)
                        
                        HStack {
                            Label(classification.destination, systemImage: "tag.fill")
                            Spacer()
                            Text("Confidence: \(Int(classification.confidence * 100))%")
                        }
                        
                        Text("Filename: \(classification.filename)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color(NSColor.controlBackgroundColor))
                    .cornerRadius(8)
                } else if !message.processed {
                    Button("Classify Now") {
                        classifyMessage(message)
                    }
                    .buttonStyle(.borderedProminent)
                }
            }
            .padding()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    private func classifyMessage(_ message: Message) {
        // Trigger classification via Python script
        let result = PythonBridge.shared.executeScript("process_inbox.py", arguments: ["--classify", message.id], vaultPath: settings.vaultPath)
        
        switch result {
        case .success:
            print("Message classified successfully")
        case .failure(let error):
            print("Error classifying message: \(error.localizedDescription)")
        }
    }
}

#Preview {
    MessagesView()
}
