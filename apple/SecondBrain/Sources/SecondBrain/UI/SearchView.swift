import SwiftUI
import Combine

/// Live full-text search across notes using FTS5.
struct SearchView: View {
    let database: AppDatabase
    @State private var query: String = ""
    @State private var results: [Note] = []
    @State private var isSearching = false
    @State private var searchTask: Task<Void, Never>?
    
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Search field
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundStyle(.secondary)
                TextField("Search notes...", text: $query)
                    .textFieldStyle(.plain)
                    .font(.title3)
                
                if !query.isEmpty {
                    Button {
                        query = ""
                        results = []
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundStyle(.secondary)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(12)
            .background(.quaternary.opacity(0.5))
            .clipShape(RoundedRectangle(cornerRadius: 8))
            .padding(.horizontal, 24)
            .padding(.top, 16)
            .padding(.bottom, 12)
            .onChange(of: query) { _ in
                performDebouncedSearch()
            }
            
            Divider()
            
            // Results
            if query.isEmpty {
                emptyState
            } else if isSearching {
                ProgressView("Searching...")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if results.isEmpty {
                noResultsState
            } else {
                resultsList
            }
        }
    }
    
    // MARK: - Empty State
    
    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 48))
                .foregroundStyle(.secondary)
            Text("Search Your Notes")
                .font(.title3)
            Text("Type a query to search across all your notes\nusing full-text search.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    // MARK: - No Results
    
    private var noResultsState: some View {
        VStack(spacing: 12) {
            Image(systemName: "doc.text.magnifyingglass")
                .font(.system(size: 48))
                .foregroundStyle(.secondary)
            Text("No Results")
                .font(.title3)
            Text("No notes match \"\(query)\"")
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    // MARK: - Results List
    
    private var resultsList: some View {
        ScrollView {
            LazyVStack(spacing: 8) {
                HStack {
                    Text("\(results.count) result\(results.count == 1 ? "" : "s")")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                }
                
                ForEach(results, id: \.id) { note in
                    resultRow(for: note)
                }
            }
            .padding(.horizontal, 24)
            .padding(.vertical, 12)
        }
    }
    
    private func resultRow(for note: Note) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(note.classifiedTitle ?? note.classifiedFilename)
                    .font(.headline)
                    .lineLimit(1)
                
                Spacer()
                
                CategoryPill(category: note.correctedCategory ?? note.classifiedCategory)
            }
            
            Text(note.originalText)
                .font(.body)
                .foregroundStyle(.secondary)
                .lineLimit(2)
            
            Text(note.destinationPath)
                .font(.caption)
                .foregroundStyle(.tertiary)
        }
        .padding(10)
        .background(.quaternary.opacity(0.3))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
    
    // MARK: - Debounced Search
    
    private func performDebouncedSearch() {
        searchTask?.cancel()
        
        let currentQuery = query.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !currentQuery.isEmpty else {
            results = []
            isSearching = false
            return
        }
        
        isSearching = true
        searchTask = Task {
            // 300ms debounce
            try? await Task.sleep(nanoseconds: 300_000_000)
            
            guard !Task.isCancelled else { return }
            
            do {
                let searchResults = try database.searchNotes(query: currentQuery)
                await MainActor.run {
                    if !Task.isCancelled {
                        results = searchResults
                        isSearching = false
                    }
                }
            } catch {
                await MainActor.run {
                    results = []
                    isSearching = false
                }
            }
        }
    }
}
