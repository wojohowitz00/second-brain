import SwiftUI

/// View for correcting misclassified notes.
struct CorrectionView: View {
    let database: AppDatabase
    @State private var uncorrectedNotes: [Note] = []
    @State private var selectedCategories: [Int64: String] = [:]
    @State private var errorMessage: String?
    
    private let correctionService = CorrectionService()
    private let categories = ["Projects", "Areas", "Resources", "Archives"]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Header
            HStack {
                Text("Corrections")
                    .font(.title2.bold())
                Spacer()
                Text("\(uncorrectedNotes.count) pending")
                    .foregroundStyle(.secondary)
            }
            .padding(.horizontal, 24)
            .padding(.top, 16)
            
            if let error = errorMessage {
                Text(error)
                    .foregroundStyle(.red)
                    .padding(.horizontal, 24)
            }
            
            if uncorrectedNotes.isEmpty {
                emptyState
            } else {
                notesList
            }
        }
        .onAppear { loadNotes() }
        .onReceive(NotificationCenter.default.publisher(for: .syncCompleted)) { _ in
            loadNotes()
        }
    }
    
    // MARK: - Empty State
    
    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "checkmark.seal.fill")
                .font(.system(size: 48))
                .foregroundStyle(.green)
            Text("All notes classified correctly!")
                .font(.title3)
            Text("Notes that need re-classification will appear here.")
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    // MARK: - Notes List
    
    private var notesList: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                ForEach(uncorrectedNotes, id: \.id) { note in
                    correctionRow(for: note)
                }
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 16)
        }
    }
    
    private func correctionRow(for note: Note) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            // Original text
            Text(note.originalText)
                .lineLimit(2)
                .font(.body)
            
            HStack(spacing: 12) {
                // Current classification
                HStack(spacing: 4) {
                    Text("Current:")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    CategoryPill(category: note.classifiedCategory)
                }
                
                Image(systemName: "arrow.right")
                    .foregroundStyle(.secondary)
                
                // New category picker
                Picker("", selection: categoryBinding(for: note)) {
                    Text("Select...").tag("")
                    ForEach(categories, id: \.self) { cat in
                        Text(cat).tag(cat)
                    }
                }
                .frame(width: 130)
                
                Spacer()
                
                // Apply button
                Button("Apply") {
                    applyCorrection(for: note)
                }
                .disabled(selectedCategory(for: note).isEmpty)
                .buttonStyle(.borderedProminent)
                .controlSize(.small)
            }
            
            // Destination path
            Text(note.destinationPath)
                .font(.caption)
                .foregroundStyle(.tertiary)
        }
        .padding(12)
        .background(.quaternary.opacity(0.3))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
    
    // MARK: - Helpers
    
    private func categoryBinding(for note: Note) -> Binding<String> {
        Binding(
            get: { selectedCategories[note.id ?? 0] ?? "" },
            set: { selectedCategories[note.id ?? 0] = $0 }
        )
    }
    
    private func selectedCategory(for note: Note) -> String {
        selectedCategories[note.id ?? 0] ?? ""
    }
    
    private func loadNotes() {
        do {
            uncorrectedNotes = try database.uncorrectedNotes()
            errorMessage = nil
        } catch {
            errorMessage = "Failed to load notes: \(error.localizedDescription)"
        }
    }
    
    private func applyCorrection(for note: Note) {
        let newCategory = selectedCategory(for: note)
        guard !newCategory.isEmpty else { return }
        
        let vaultPath = UserDefaults.standard.string(forKey: "vaultPath") ?? ""
        guard !vaultPath.isEmpty else {
            errorMessage = "Vault path not configured. Check Settings."
            return
        }
        
        var mutableNote = note
        do {
            try correctionService.applyCorrection(
                note: &mutableNote,
                newCategory: newCategory,
                vaultPath: vaultPath,
                database: database
            )
            // Remove from list with animation
            withAnimation {
                uncorrectedNotes.removeAll { $0.id == note.id }
                selectedCategories.removeValue(forKey: note.id ?? 0)
            }
        } catch {
            errorMessage = "Correction failed: \(error.localizedDescription)"
        }
    }
}
